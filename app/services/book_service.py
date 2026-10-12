from app.database import fetch_all, fetch_one


def get_all_books():
	query = """
		SELECT
				b.book_id,
				b.title,
				b.isbn,
				b.publication_year,
				COUNT(cp.copy_id) AS total_copies,
				COUNT(cp.copy_id) FILTER (
						WHERE cp.status = 'available'
				) AS available_copies
		FROM books AS b
		LEFT JOIN book_copies AS cp
				ON cp.book_id = b.book_id
		GROUP BY
				b.book_id,
				b.title,
				b.isbn,
				b.publication_year
		ORDER BY b.title
	"""

	return fetch_all(query)


def get_book_by_id(book_id):
	query = """
		SELECT
				b.book_id,
				b.title,
				b.isbn,
				b.publication_year
		FROM books AS b
		WHERE b.book_id = %s
	"""

	return fetch_one(query, (book_id,))



def create_book(title, isbn=None, publication_year=None):
	query = """
		INSERT INTO books (title, isbn, publication_year)
		VALUES (%s, %s, %s)
		RETURNING book_id, title, isbn, publication_year
	"""

	return fetch_one(
		query, (title, isbn, publication_year),
	)
