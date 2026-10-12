
from fastapi import HTTPException, Request, status

from app.services.staff_service import get_staff_by_id


def get_current_staff(request: Request):
  staff_id = request.session.get("staff_id")

  if staff_id is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail={
        "error": "STAFF_LOGIN_REQUIRED",
        "message": "Please log in as a staff member.",
      },
    )

  staff = get_staff_by_id(staff_id)

  if staff is None or staff["status"] != "active":
    request.session.clear()

    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail={
        "error": "INVALID_STAFF_SESSION",
        "message": "The staff session is no longer valid.",
      },
    )

  return staff
