
from datetime import date

from pydantic import BaseModel, Field


class LoanCreate(BaseModel):
	member_id: int = Field(gt=0)
	copy_id: int = Field(gt=0)
	due_date: date


class LoanResponse(BaseModel):
	loan_id: int
	member_id: int
	copy_id: int
	checkout_staff_id: int
	checkout_date: date
	due_date: date
	return_date: date | None


class MemberLoanResponse(BaseModel):
	loan_id: int
	book_title: str
	branch_name: str
	checkout_date: date
	due_date: date
	return_date: date | None
	status: str
