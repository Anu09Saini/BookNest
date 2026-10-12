
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()

password_hasher = PasswordHash.recommended()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
  os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not JWT_SECRET_KEY:
  raise RuntimeError("JWT_SECRET_KEY must be configured in .env")


def hash_password(password: str) -> str:
	"""Return a secure password hash."""
	return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
	"""Verify a password against its stored hash."""
	return password_hasher.verify(password, password_hash)


def create_access_token(member_id: int) -> str:
	"""Create a signed JWT for a member."""
	now = datetime.now(timezone.utc)

	payload = {
		"sub": str(member_id),
		"type": "member",
		"iat": now,
		"exp": now + timedelta(
				minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
		),
	}

	return jwt.encode(
		payload,
		JWT_SECRET_KEY,
		algorithm=JWT_ALGORITHM,
	)
