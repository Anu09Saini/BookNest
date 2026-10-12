
from getpass import getpass

from app.core.security import hash_password
from app.database import execute_query, fetch_one


email = input("Enter the member's email: ").strip().lower()
password = getpass("Enter the new password: ")
confirm_password = getpass("Confirm the new password: ")

if password != confirm_password:
    print("Error: Passwords do not match.")
    raise SystemExit(1)

if len(password) < 8 or len(password) > 128:
    print("Error: Password must be between 8 and 128 characters.")
    raise SystemExit(1)

member = fetch_one(
    """
    SELECT member_id, name, email
    FROM members
    WHERE email = %s
    """,
    (email,),
)

if member is None:
    print("Error: No member found with that email.")
    raise SystemExit(1)

password_hash = hash_password(password)

execute_query(
    """
    UPDATE members
    SET password_hash = %s
    WHERE member_id = %s
    """,
    (password_hash, member["member_id"]),
)

print(f"Password reset successfully for {member['email']}.")
