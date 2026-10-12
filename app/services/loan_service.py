
from datetime import date

from app.database import get_connection


class LoanNotFoundError(Exception):
  pass


class LoanConflictError(Exception):
  pass


class LoanValidationError(Exception):
  pass


def checkout_book(member_id, copy_id, staff_id, due_date):
	with get_connection() as conn:
		with conn.cursor() as cursor:
			# Lock the member row. This serializes concurrent
			# checkout attempts for the same member.
			cursor.execute(
				"""
				SELECT member_id, status
				FROM members
				WHERE member_id = %s
				FOR UPDATE
				""",
				(member_id,),
			)
			member = cursor.fetchone()

			if member is None:
				raise LoanNotFoundError("Member not found.")

			if member["status"] != "active":
				raise LoanConflictError(
						"This member cannot borrow books."
				)

			# Lock the physical copy to prevent concurrent checkout.
			cursor.execute(
				"""
				SELECT copy_id, status
				FROM book_copies
				WHERE copy_id = %s
				FOR UPDATE
				""",
				(copy_id,),
			)
			copy = cursor.fetchone()

			if copy is None:
				raise LoanNotFoundError("Book copy not found.")

			if copy["status"] != "available":
				raise LoanConflictError(
						"This book copy is not available."
				)

			# Enforce the maximum of three active loans.
			cursor.execute(
				"""
				SELECT COUNT(*) AS active_loans
				FROM loans
				WHERE member_id = %s
					AND return_date IS NULL
				""",
				(member_id,),
			)
			active_loans = cursor.fetchone()["active_loans"]

			if active_loans >= 3:
				raise LoanConflictError(
						"A member cannot have more than three active loans."
				)

			if due_date < date.today():
				raise LoanValidationError(
						"The due date cannot be in the past."
				)

			# Insert the loan.
			cursor.execute(
				"""
				INSERT INTO loans (
						copy_id,
						member_id,
						checkout_staff_id,
						checkout_date,
						due_date
				)
				VALUES (%s, %s, %s, CURRENT_DATE, %s)
				RETURNING
						loan_id, member_id, copy_id,
						checkout_staff_id, checkout_date,
						due_date, return_date
				""",
				(copy_id, member_id, staff_id, due_date),
			)
			loan = cursor.fetchone()

			# Update copy status within the same transaction.
			cursor.execute(
				"""
				UPDATE book_copies
				SET status = 'loaned'
				WHERE copy_id = %s
				""",
				(copy_id,),
			)

			return loan


def return_book(loan_id, staff_id):
	with get_connection() as conn:
		with conn.cursor() as cursor:
			cursor.execute(
				"""
				SELECT loan_id, copy_id, due_date, return_date
				FROM loans
				WHERE loan_id = %s
				FOR UPDATE
				""",
				(loan_id,),
			)
			loan = cursor.fetchone()

			if loan is None:
				raise LoanNotFoundError("Loan not found.")

			if loan["return_date"] is not None:
				raise LoanConflictError(
						"This loan has already been returned."
				)

			return_date = date.today()
			overdue_days = max(
				(return_date - loan["due_date"]).days,
				0,
			)
			fine_amount = overdue_days * 10

			cursor.execute(
				"""
				UPDATE loans
				SET return_date = %s,
						return_staff_id = %s
				WHERE loan_id = %s
				""",
				(return_date, staff_id, loan_id),
			)

			cursor.execute(
				"""
				UPDATE book_copies
				SET status = 'available'
				WHERE copy_id = %s
				""",
				(loan["copy_id"],),
			)

			fine = None

			if fine_amount > 0:
				cursor.execute(
					"""
					INSERT INTO fines (loan_id, amount, status)
					VALUES (%s, %s, 'unpaid')
					RETURNING fine_id, loan_id, amount, status
					""",
					(loan_id, fine_amount),
				)
				fine = cursor.fetchone()

			return {
				"loan_id": loan_id,
				"return_date": return_date,
				"overdue_days": overdue_days,
				"fine": fine,
			}


def get_member_loans(member_id):
	with get_connection() as conn:
		with conn.cursor() as cursor:
			cursor.execute(
					"""
					SELECT
							l.loan_id,
							b.title AS book_title,
							br.name AS branch_name,
							l.checkout_date,
							l.due_date,
							l.return_date,
							CASE
									WHEN l.return_date IS NOT NULL THEN 'returned'
									WHEN l.due_date < CURRENT_DATE THEN 'overdue'
									ELSE 'active'
							END AS status
					FROM loans AS l
					JOIN book_copies AS cp
							ON cp.copy_id = l.copy_id
					JOIN books AS b
							ON b.book_id = cp.book_id
					JOIN branches AS br
							ON br.branch_id = cp.branch_id
					WHERE l.member_id = %s
					ORDER BY l.checkout_date DESC, l.loan_id DESC
					""",
					(member_id,),
			)
			return cursor.fetchall()
