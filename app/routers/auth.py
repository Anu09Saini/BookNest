
from fastapi import APIRouter, HTTPException, status

from app.core.security import (
	create_access_token,
	verify_password,
	JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.schemas.member import MemberLogin, TokenResponse
from app.services.member_service import get_member_by_email

router = APIRouter(
	prefix="/auth",
	tags=["Authentication"],
)


@router.post("/member/login", response_model=TokenResponse)
def member_login(login_data: MemberLogin):
	member = get_member_by_email(login_data.email)

	# Use the same error for unknown emails and wrong passwords.
	if (
		member is None
		or not verify_password(
				login_data.password,
				member["password_hash"],
		)
	):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail={
					"error": "INVALID_CREDENTIALS",
					"message": "Email or password is incorrect.",
			},
			headers={"WWW-Authenticate": "Bearer"},
		)

	if member["status"] != "active":
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail={
					"error": "MEMBER_INACTIVE",
					"message": "This membership is not active.",
			},
		)

	token = create_access_token(member["member_id"])

	return {
		"access_token": token,
		"token_type": "bearer",
		"expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
	}
