
from app.database import fetch_one


def create_member(name, email, password_hash):
	query = """
		INSERT INTO members (name, email, password_hash)
		VALUES (%s, %s, %s)
		RETURNING member_id, name, email, status
"""

	return fetch_one(
		query,
		(name, email, password_hash),
	)


def get_member_by_email(email):
	query = """
		SELECT member_id, name, email, password_hash, status
		FROM members
		WHERE email = %s
	"""

	return fetch_one(query, (email,))


def get_member_by_id(member_id):
	query = """
		SELECT member_id, name, email, status
		FROM members
		WHERE member_id = %s
	"""

	return fetch_one(query, (member_id,))
