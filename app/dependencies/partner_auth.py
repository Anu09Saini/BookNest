from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.security import verify_password
from app.database import fetch_one


# identifies the partner.
api_key_header = APIKeyHeader(
  name="X-API-Key",
  auto_error=False,
)

#the secret used for verification of partner
api_secret_header = APIKeyHeader(
  name="X-API-Secret",
  auto_error=False,
)


def get_current_partner(
  api_key: str | None = Depends(api_key_header),
  api_secret: str | None = Depends(api_secret_header),
):
  credentials_error = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail={
          "error": "INVALID_PARTNER_CREDENTIALS",
          "message": "Invalid or inactive partner credentials.",
      },
      headers={"WWW-Authenticate": "APIKey"},
  )

  if not api_key or not api_secret:
    raise credentials_error

  # retrieves the partner using a parameterized query.
  partner = fetch_one(
    """
    SELECT partner_id, name, secret_hash, is_active
    FROM partner_clients
    WHERE api_key = %s
    """,
    (api_key,),
  )

  if partner is None or not partner["is_active"]:
    raise credentials_error

  # checks the submitted secret against the stored Argon2 hash.
  if not verify_password(api_secret, partner["secret_hash"]):
    raise credentials_error

  return {
    "partner_id": partner["partner_id"],
    "name": partner["name"],
  }
