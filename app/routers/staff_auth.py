from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.security import verify_password
from app.dependencies.staff_auth import get_current_staff
from app.schemas.staff import StaffLogin, StaffResponse
from app.services.staff_service import get_staff_by_email

router = APIRouter(tags=["Staff Authentication"])


@router.post("/auth/staff/login")
def staff_login(
  login_data: StaffLogin,
  request: Request,
):
  staff = get_staff_by_email(login_data.email)

  if (
    staff is None
    or not verify_password(
      login_data.password,
      staff["password_hash"],
    )
  ):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
          "error": "INVALID_CREDENTIALS",
          "message": "Email or password is incorrect.",
        },
      )

  if staff["status"] != "active":
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
          "error": "STAFF_INACTIVE",
          "message": "This staff account is inactive.",
        },
      )

  # Prevent reuse of any existing session contents.
  request.session.clear()
  request.session["staff_id"] = staff["staff_id"]

  return {"message": "Staff login successful."}


@router.post("/auth/staff/logout")
def staff_logout(request: Request):
  request.session.clear()
  return {"message": "Staff logout successful."}


@router.get("/staff/me", response_model=StaffResponse)
def staff_profile(
  current_staff=Depends(get_current_staff),
):
  return current_staff