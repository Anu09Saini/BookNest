
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
