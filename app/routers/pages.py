from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from pathlib import Path
import re
import psycopg

from decimal import Decimal, InvalidOperation
from fastapi.responses import RedirectResponse

from datetime import date, timedelta
from app.core.security import verify_password, hash_password
from app.database import fetch_all

from app.services.book_service import get_all_books
from app.services.member_service import (
    create_member,
    get_member_by_email,
    get_member_by_id,
)
from app.services.loan_service import (
    get_member_loans,
    checkout_book,
    return_book,
    LoanNotFoundError,
    LoanConflictError,
    LoanValidationError,
)
from app.services.staff_service import (
    get_staff_by_email,
    get_staff_by_id,
)
from app.services.fine_service import (
    FineConflictError,
    FineNotFoundError,
    get_member_fines,
    make_fine_payment,
)
from app.services.report_service import (
    get_overdue_loans,
    get_most_borrowed_books,
)


router = APIRouter(tags=["Web UI"])

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
  directory=str(BASE_DIR / "templates")
)


@router.get("/catalogue", name="catalogue_page")
def catalogue_page(request: Request):
  books = get_all_books()

  return templates.TemplateResponse(
    request=request,
    name="catalogue.html",
    context={"books": books},
  )



# MEMBERS ROUTES

# new member registration
@router.get("/members/register", name="member_register_page")
def member_register_page(request: Request):
  return templates.TemplateResponse(
    request=request,
    name="member_register.html",
    context={
      "error": None,
      "name": "",
      "email": "",
    },
  )


@router.post("/members/register", name="member_register_submit")
def member_register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
  name = name.strip()
  email = email.strip().lower()

  error = None

  if not name:
      error = "Please enter your name."
  elif len(name) > 150:
      error = "Name cannot exceed 150 characters."
  elif len(email) > 254 or not re.fullmatch(
      r"[^@\s]+@[^@\s]+\.[^@\s]+", email
  ):
      error = "Please enter a valid email address."
  elif len(password) < 8 or len(password) > 128:
      error = "Password must contain between 8 and 128 characters."

  if error:
      return templates.TemplateResponse(
          request=request,
          name="member_register.html",
          context={
              "error": error,
              "name": name,
              "email": email,
          },
          status_code=422,
      )

  password_hash = hash_password(password)

  try:
      create_member(
          name=name,
          email=email,
          password_hash=password_hash,
      )
  except psycopg.errors.UniqueViolation:
      return templates.TemplateResponse(
          request=request,
          name="member_register.html",
          context={
              "error": "An account with this email already exists.",
              "name": name,
              "email": email,
          },
          status_code=409,
      )

  return RedirectResponse(
      url="/members/login?registered=1",
      status_code=303,
  )

# member login page
@router.get("/members/login", name="member_login_page")
def member_login_page(request: Request):
  if request.session.get("member_id"):
    return RedirectResponse(
      "/members/dashboard",
      status_code=303,
    )

  return templates.TemplateResponse(
    request=request,
    name="member_login.html",
    context={"error": None},
  )




@router.post("/members/login", name="member_login_submit")
def member_login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
  member = get_member_by_email(email.strip().lower())

  if (
    member is None
    or member["status"] != "active"
    or not verify_password(password, member["password_hash"])
  ):
    return templates.TemplateResponse(
        request=request,
        name="member_login.html",
        context={"error": "Invalid email or password."},
        status_code=401,
    )

  # Preserve an existing staff session if one exists.
  request.session.pop("member_id", None)
  request.session["member_id"] = member["member_id"]

  return RedirectResponse(
    "/members/dashboard",
    status_code=303,
  )


@router.get("/members/dashboard", name="member_dashboard")
def member_dashboard(request: Request):
  member_id = request.session.get("member_id")

  if not member_id:
    return RedirectResponse(
      "/members/login",
      status_code=303,
    )

  member = get_member_by_id(member_id)

  if member is None or member["status"] != "active":
    request.session.pop("member_id", None)
    return RedirectResponse(
      "/members/login",
      status_code=303,
    )

  return templates.TemplateResponse(
    request=request,
    name="member_dashboard.html",
    context={
      "member": member,
      "loans": get_member_loans(member_id),
      "fines": get_member_fines(member_id),
      "message": request.query_params.get("message"),
    },
  )


@router.post("/members/logout", name="member_logout")
def member_logout(request: Request):
  request.session.pop("member_id", None)

  return RedirectResponse(
    "/members/login",
    status_code=303,
  )


@router.post("/members/me/fines/{fine_id}/payments", name="member_pay_fine",)
def member_pay_fine(request: Request, fine_id: int, amount: Decimal = Form(...),):
  member_id = request.session.get("member_id")

  if not member_id:
    return RedirectResponse(
      "/members/login",
      status_code=303,
    )

  if not amount.is_finite() or amount <= 0:
    return RedirectResponse(
      "/members/dashboard?message=Enter+a+valid+payment+amount",
      status_code=303,
    )

  try:
    make_fine_payment(
      fine_id=fine_id,
      member_id=member_id,
      amount=amount,
    )
  except FineNotFoundError:
    return RedirectResponse(
      "/members/dashboard?message=Fine+not+found",
      status_code=303,
    )
  except FineConflictError:
    return RedirectResponse(
      "/members/dashboard?message=Payment+exceeds+the+balance+or+fine+is+paid",
      status_code=303,
    )
  except InvalidOperation:
    return RedirectResponse(
      "/members/dashboard?message=Invalid+payment+amount",
      status_code=303,
    )

  return RedirectResponse(
    "/members/dashboard?message=Payment+successful",
    status_code=303,
    )


# STAFF DASHBOARD ROUTES

def get_dashboard_staff(request: Request):
  staff_id = request.session.get("staff_id")

  if not staff_id:
    return None

  staff = get_staff_by_id(staff_id)

  if (
    staff is None
    or staff["status"] != "active"
    or staff["role"] not in ("librarian", "admin")
  ):
    request.session.pop("staff_id", None)
    return None

  return staff


@router.get("/staff/login", name="staff_login_page")
def staff_login_page(request: Request):
  if get_dashboard_staff(request):
    return RedirectResponse("/staff/dashboard", status_code=303)

  return templates.TemplateResponse(
    request=request,
    name="staff_login.html",
    context={"error": None},
  )


@router.post("/staff/login", name="staff_login_submit")
def staff_login_submit(
  request: Request,
  email: str = Form(...),
  password: str = Form(...),
):
  staff = get_staff_by_email(email.strip().lower())

  if (
    staff is None
    or staff["status"] != "active"
    or staff["role"] not in ("librarian", "admin")
    or not verify_password(password, staff["password_hash"])
  ):
    return templates.TemplateResponse(
      request=request,
      name="staff_login.html",
      context={"error": "Invalid email or password, or insufficient access."},
      status_code=401,
    )

  request.session.pop("staff_id", None)
  request.session["staff_id"] = staff["staff_id"]

  return RedirectResponse("/staff/dashboard", status_code=303)


@router.post("/staff/logout", name="staff_logout")
def staff_logout(request: Request):
  request.session.pop("staff_id", None)
  return RedirectResponse("/staff/login", status_code=303)


@router.get("/staff/dashboard", name="staff_dashboard")
def staff_dashboard(request: Request):
  staff = get_dashboard_staff(request)

  if not staff:
    return RedirectResponse("/staff/login", status_code=303)

  available_copies = fetch_all(
    """
    SELECT cp.copy_id, b.title, br.name AS branch_name
    FROM book_copies cp
    JOIN books b ON b.book_id = cp.book_id
    JOIN branches br ON br.branch_id = cp.branch_id
    WHERE cp.status = %s
    ORDER BY b.title, br.name, cp.copy_id
    """,
    ("available",),
  )

  members = fetch_all(
    """
    SELECT member_id, name, email
    FROM members
    WHERE status = %s
    ORDER BY name
    """,
    ("active",),
  )

  active_loans = fetch_all(
    """
    SELECT
        l.loan_id,
        m.name AS member_name,
        b.title AS book_title,
        br.name AS branch_name,
        l.due_date
    FROM loans l
    JOIN members m ON m.member_id = l.member_id
    JOIN book_copies cp ON cp.copy_id = l.copy_id
    JOIN books b ON b.book_id = cp.book_id
    JOIN branches br ON br.branch_id = cp.branch_id
    WHERE l.return_date IS NULL
    ORDER BY l.due_date, l.loan_id
    """
  )

  today = date.today()

  return templates.TemplateResponse(
    request=request,
    name="staff_dashboard.html",
    context={
        "staff": staff,
        "available_copies": available_copies,
        "members": members,
        "active_loans": active_loans,
        "overdue_loans": get_overdue_loans(),
        "popular_books": get_most_borrowed_books(5),
        "today": today.isoformat(),
        "default_due_date": (today + timedelta(days=14)).isoformat(),
        "message": request.query_params.get("message"),
    },
  )


@router.post("/staff/loans/checkout", name="staff_checkout_book")
def staff_checkout_book(
  request: Request,
  member_id: int = Form(...),
  copy_id: int = Form(...),
  due_date: date = Form(...),
):
  staff = get_dashboard_staff(request)

  if not staff:
    return RedirectResponse("/staff/login", status_code=303)

  try:
    checkout_book(
      member_id=member_id,
      copy_id=copy_id,
      staff_id=staff["staff_id"],
      due_date=due_date,
    )
    message = "Book checked out successfully."
  except LoanNotFoundError:
    message = "Member or book copy was not found."
  except LoanConflictError as exc:
    message = str(exc)
  except LoanValidationError as exc:
    message = str(exc)

  from urllib.parse import quote
  return RedirectResponse(
    f"/staff/dashboard?message={quote(message)}",
    status_code=303,
  )


@router.post("/staff/loans/{loan_id}/return", name="staff_return_book",)
def staff_return_book(request: Request, loan_id: int):
  staff = get_dashboard_staff(request)

  if not staff:
    return RedirectResponse("/staff/login", status_code=303)

  try:
      result = return_book(
        loan_id=loan_id,
        staff_id=staff["staff_id"],
      )
      if result["fine"]:
        message = (
          f"Book returned. Fine assessed: "
          f"{result['fine']['amount']}."
        )
      else:
        message = "Book returned successfully. No fine assessed."
  except LoanNotFoundError:
    message = "Loan not found."
  except LoanConflictError as exc:
    message = str(exc)

  from urllib.parse import quote
  return RedirectResponse(
    f"/staff/dashboard?message={quote(message)}",
    status_code=303,
  )


