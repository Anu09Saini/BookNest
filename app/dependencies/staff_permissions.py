from fastapi import Depends, HTTPException, status

from app.dependencies.staff_auth import get_current_staff


def require_librarian(staff: dict = Depends(get_current_staff),):
  if staff["role"] not in ("librarian", "admin"):
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail={
          "error": "INSUFFICIENT_PERMISSIONS",
          "message": "Librarian or admin access is required.",
      },
    )

  return staff
