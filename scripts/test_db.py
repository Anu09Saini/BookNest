
from app.database import fetch_one, fetch_all


def main():
	# Verify the connection and database identity.
	result = fetch_one(
		"""
		SELECT
				current_database() AS database_name,
				current_user AS database_user
		"""
	)

	print("Database connection successful!")
	print(result)

	# Verify that Python can read the books table.
	books = fetch_all(
		"""
		SELECT book_id, title, isbn
		FROM books
		ORDER BY title
		LIMIT %s
		""",
		(5,),
	)

	print("\nBooks retrieved from PostgreSQL:")

	for book in books:
		print(book)


if __name__ == "__main__":
    main()
