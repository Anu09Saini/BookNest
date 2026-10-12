
from fastapi import APIRouter, HTTPException, status, Depends
from psycopg.errors import UniqueViolation

from app.schemas.member import MemberCreate, MemberResponse
from app.services.member_service import create_member
from app.core.security import hash_password
from app.dependencies.auth import get_current_member

router = APIRouter(
	prefix="/members",
	tags=["Members"],
)


@router.post(
	"/",
	response_model=MemberResponse,
	status_code=status.HTTP_201_CREATED,
)
def register_member(member_data: MemberCreate):
	password_hash = hash_password(member_data.password)

	try:
		member = create_member(
			name=member_data.name,
			email=member_data.email,
			password_hash=password_hash,
		)
		return member

	except UniqueViolation as exc:
		raise HTTPException(
			status_code=409,
			detail={
					"error": "EMAIL_ALREADY_REGISTERED",
					"message": "A member with this email already exists.",
			},
		) from exc


@router.get("/me", response_model=MemberResponse)
def get_my_profile(
  current_member=Depends(get_current_member),
):
  return current_member
