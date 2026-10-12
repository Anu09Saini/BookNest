from getpass import getpass

from app.core.security import hash_password
from app.database import execute_query, fetch_one


def main():
  email = input("Staff email: ").strip().lower()
  password = getpass("New password (minimum 8 characters): ")
  confirm = getpass("Confirm password: ")

  if len(password) < 8 or len(password) > 128:
    print("Password must be between 8 and 128 characters.")
    return

  if password != confirm:
    print("Passwords do not match.")
    return

  staff = fetch_one(
    """
    SELECT staff_id
    FROM staff
    WHERE email = %s
    """,
    (email,),
  )

  if staff is None:
    print("Staff account not found.")
    return

  password_hash = hash_password(password)

  execute_query(
    """
    UPDATE staff
    SET password_hash = %s
    WHERE staff_id = %s
    """,
    (password_hash, staff["staff_id"]),
  )

  print("Staff password updated successfully.")


if __name__ == "__main__":
    main()