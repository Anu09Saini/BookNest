from app.database import fetch_one


def get_staff_by_email(email):
  query = """
      SELECT
          staff_id,
          name,
          email,
          branch_id,
          password_hash,
          role,
          status
      FROM staff
      WHERE email = %s
  """
  return fetch_one(query, (email,))


def get_staff_by_id(staff_id):
  query = """
      SELECT
          staff_id,
          name,
          email,
          branch_id,
          role,
          status
      FROM staff
      WHERE staff_id = %s
  """
  return fetch_one(query, (staff_id,))