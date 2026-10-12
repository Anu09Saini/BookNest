import secrets

from app.core.security import hash_password
from app.database import get_connection


def main():
  name = input("Enter partner name: ").strip()

  if not name:
    print("Partner name cannot be empty.")
    return

  api_key = "bn_live_" + secrets.token_urlsafe(24)
  api_secret = secrets.token_urlsafe(48)
  secret_hash = hash_password(api_secret)

  try:
    with get_connection() as conn:
      with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO partner_clients
                (name, api_key, secret_hash, is_active)
            VALUES (%s, %s, %s, TRUE)
            RETURNING partner_id, name, api_key
            """,
            (name, api_key, secret_hash),
        )
        partner = cursor.fetchone()

  except Exception as exc:
    # Do not print secrets or database details.
    print("Could not create partner. Check the name and database.")
    print(f"Error type: {type(exc).__name__}")
    return

  print("\nPartner created successfully.")
  print(f"Partner ID: {partner['partner_id']}")
  print(f"Partner name: {partner['name']}")
  print(f"API key: {api_key}")
  print(f"API secret: {api_secret}")
  print("\nSave both credentials securely now.")
  print("The API secret will not be stored in plaintext.")


if __name__ == "__main__":
    main()

