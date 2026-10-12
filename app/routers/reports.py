from fastapi import APIRouter, Depends, Query

from app.dependencies.staff_permissions import require_librarian
from app.schemas.report import (
    MostBorrowedBookResponse,
    OverdueLoanResponse,
)
from app.services.report_service import (
  get_most_borrowed_books,
  get_overdue_loans,
)

router = APIRouter(
  prefix="/reports",
  tags=["Reports"],
  dependencies=[Depends(require_librarian)],
)


@router.get("/overdue-loans", response_model=list[OverdueLoanResponse],)
def overdue_loans_report():
  return get_overdue_loans()


@router.get("/most-borrowed-books", response_model=list[MostBorrowedBookResponse],)
def most_borrowed_books_report(limit: int = Query(default=5, ge=1, le=100),):
  return get_most_borrowed_books(limit)
