
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_member
from app.schemas.fine import (
    FinePaymentCreate,
    FinePaymentResponse,
    MemberFineResponse,
)
from app.services.fine_service import (
    FineConflictError,
    FineNotFoundError,
    get_member_fines,
    make_fine_payment,
)

router = APIRouter(tags=["Fines"])


@router.get(
    "/members/me/fines",
    response_model=list[MemberFineResponse],
)
def list_my_fines(
    member: dict = Depends(get_current_member),
):
    return get_member_fines(member["member_id"])


@router.post(
    "/fines/{fine_id}/payments",
    response_model=FinePaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def pay_fine(
    fine_id: int,
    payment_data: FinePaymentCreate,
    member: dict = Depends(get_current_member),
):
    try:
        return make_fine_payment(
            fine_id=fine_id,
            member_id=member["member_id"],
            amount=payment_data.amount,
        )
    except FineNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "FINE_NOT_FOUND",
                "message": str(exc),
            },
        ) from exc
    except FineConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "PAYMENT_CONFLICT",
                "message": str(exc),
            },
        ) from exc
