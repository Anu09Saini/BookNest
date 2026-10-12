
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class FinePaymentCreate(BaseModel):
  amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class MemberFineResponse(BaseModel):
  fine_id: int
  loan_id: int
  book_title: str
  fine_amount: Decimal
  paid_amount: Decimal
  outstanding_amount: Decimal
  status: str
  assessed_at: datetime


class FinePaymentResponse(BaseModel):
  payment_id: int
  fine_id: int
  amount: Decimal
  paid_at: datetime
  fine_status: str
  outstanding_amount: Decimal
