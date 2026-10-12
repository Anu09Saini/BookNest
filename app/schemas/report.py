from datetime import date
from pydantic import BaseModel


class OverdueLoanResponse(BaseModel):
  loan_id: int
  member_id: int
  member_name: str
  member_email: str
  book_title: str
  copy_id: int
  branch_name: str
  due_date: date
  overdue_days: int


class MostBorrowedBookResponse(BaseModel):
  book_id: int
  title: str
  borrow_count: int
