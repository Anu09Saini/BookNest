
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)
from app.services.member_service import get_member_by_id

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_member(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "AUTHENTICATION_REQUIRED",
                "message": "A valid Bearer token is required.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        if payload.get("type") != "member":
            raise ValueError("Invalid token type")

        member_id = int(payload["sub"])

    except (
        jwt.InvalidTokenError,
        ValueError,
        KeyError,
        TypeError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_TOKEN",
                "message": "The access token is invalid or expired.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    member = get_member_by_id(member_id)

    if member is None or member["status"] != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_MEMBER",
                "message": "The member account is unavailable.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return member
