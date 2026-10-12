
from app.database import fetch_all


def get_overdue_loans():
  query = """
      SELECT
          l.loan_id,
          l.member_id,
          m.name AS member_name,
          m.email AS member_email,
          b.title AS book_title,
          cp.copy_id,
          br.name AS branch_name,
          l.due_date,
          (CURRENT_DATE - l.due_date) AS overdue_days
      FROM loans l
      JOIN members m ON m.member_id = l.member_id
      JOIN book_copies cp ON cp.copy_id = l.copy_id
      JOIN books b ON b.book_id = cp.book_id
      JOIN branches br ON br.branch_id = cp.branch_id
      WHERE l.return_date IS NULL
        AND l.due_date < CURRENT_DATE
      ORDER BY l.due_date ASC, l.loan_id ASC
  """
  return fetch_all(query)


def get_most_borrowed_books(limit: int = 5):
  query = """
      SELECT
          b.book_id,
          b.title,
          COUNT(l.loan_id)::integer AS borrow_count
      FROM books b
      LEFT JOIN book_copies cp ON cp.book_id = b.book_id
      LEFT JOIN loans l ON l.copy_id = cp.copy_id
      GROUP BY b.book_id, b.title
      ORDER BY borrow_count DESC, b.title ASC
      LIMIT %s
  """
  return fetch_all(query, (limit,))



def get_outstanding_fines():
	query = """
			SELECT
					f.fine_id,
					l.loan_id,
					m.name AS member_name,
					b.title AS book_title,
					f.amount AS original_amount,
					COALESCE(SUM(fp.amount), 0) AS amount_paid,
					f.amount - COALESCE(SUM(fp.amount), 0) AS balance,
					f.status
			FROM fines f
			JOIN loans l ON l.loan_id = f.loan_id
			JOIN members m ON m.member_id = l.member_id
			JOIN book_copies cp ON cp.copy_id = l.copy_id
			JOIN books b ON b.book_id = cp.book_id
			LEFT JOIN fine_payments fp ON fp.fine_id = f.fine_id
			WHERE f.status IN ('unpaid', 'partial')
			GROUP BY
					f.fine_id, l.loan_id, m.name, b.title,
					f.amount, f.status
			HAVING f.amount - COALESCE(SUM(fp.amount), 0) > 0
			ORDER BY balance DESC, f.fine_id
	"""
	return fetch_all(query)


def get_copies_per_branch():
	query = """
			SELECT
					br.branch_id,
					br.name AS branch_name,
					COUNT(cp.copy_id)::integer AS total_copies,
					COUNT(cp.copy_id) FILTER (
							WHERE cp.status = 'available'
					)::integer AS available_copies,
					COUNT(cp.copy_id) FILTER (
							WHERE cp.status = 'loaned'
					)::integer AS loaned_copies,
					COUNT(cp.copy_id) FILTER (
							WHERE cp.status = 'lost'
					)::integer AS lost_copies,
					COUNT(cp.copy_id) FILTER (
							WHERE cp.status = 'maintenance'
					)::integer AS maintenance_copies
			FROM branches br
			LEFT JOIN book_copies cp ON cp.branch_id = br.branch_id
			GROUP BY br.branch_id, br.name
			ORDER BY br.name
	"""
	return fetch_all(query)

