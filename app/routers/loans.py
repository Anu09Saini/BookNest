
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_member
from app.dependencies.staff_auth import get_current_staff
from app.schemas.loan import (LoanCreate, LoanResponse, MemberLoanResponse,)
from app.services.loan_service import (
    LoanConflictError,
    LoanNotFoundError,
    LoanValidationError,
    checkout_book,
    get_member_loans,
    return_book,
)

router = APIRouter(tags=["Loans"])


@router.post(
	"/loans",
	response_model=LoanResponse,
	status_code=status.HTTP_201_CREATED,
)


def create_loan(loan_data: LoanCreate, current_staff=Depends(get_current_staff),):
	try:
		return checkout_book(
			member_id=loan_data.member_id,
			copy_id=loan_data.copy_id,
			staff_id=current_staff["staff_id"],
			due_date=loan_data.due_date,
		)
	except LoanNotFoundError as exc:
		raise HTTPException(
			status_code=404,
			detail={
				"error": "RESOURCE_NOT_FOUND",
				"message": str(exc),
			},
		) from exc
	except LoanConflictError as exc:
		raise HTTPException(
			status_code=409,
			detail={
				"error": "LOAN_CONFLICT",
				"message": str(exc),
			},
		) from exc
	except LoanValidationError as exc:
		raise HTTPException(
			status_code=422,
			detail={
				"error": "INVALID_LOAN",
				"message": str(exc),
			},
		) from exc


@router.post("/loans/{loan_id}/return")
def return_loan(loan_id: int, current_staff=Depends(get_current_staff),):
	try:
		return return_book(
			loan_id=loan_id,
			staff_id=current_staff["staff_id"],
		)
	except LoanNotFoundError as exc:
		raise HTTPException(
			status_code=404,
			detail={
					"error": "LOAN_NOT_FOUND",
					"message": str(exc),
			},
		) from exc
	except LoanConflictError as exc:
		raise HTTPException(
			status_code=409,
			detail={
					"error": "LOAN_ALREADY_RETURNED",
					"message": str(exc),
			},
		) from exc


@router.get("/members/me/loans", response_model=list[MemberLoanResponse],)
def list_my_loans( current_member=Depends(get_current_member),):
  return get_member_loans(current_member["member_id"])
