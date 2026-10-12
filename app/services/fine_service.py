
from decimal import Decimal

from app.database import get_connection


class FineNotFoundError(Exception):
    pass


class FineConflictError(Exception):
    pass


def get_member_fines(member_id: int):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    f.fine_id,
                    f.loan_id,
                    b.title AS book_title,
                    f.amount AS fine_amount,
                    COALESCE(SUM(fp.amount), 0)::numeric
                        AS paid_amount,
                    (
                        f.amount - COALESCE(SUM(fp.amount), 0)
                    )::numeric AS outstanding_amount,
                    f.status,
                    f.assessed_at
                FROM fines f
                JOIN loans l ON l.loan_id = f.loan_id
                JOIN book_copies cp ON cp.copy_id = l.copy_id
                JOIN books b ON b.book_id = cp.book_id
                LEFT JOIN fine_payments fp
                    ON fp.fine_id = f.fine_id
                WHERE l.member_id = %s
                GROUP BY
                    f.fine_id,
                    f.loan_id,
                    b.title,
                    f.amount,
                    f.status,
                    f.assessed_at
                ORDER BY f.assessed_at DESC, f.fine_id DESC
                """,
                (member_id,),
            )
            return cursor.fetchall()


def make_fine_payment(
    fine_id: int,
    member_id: int,
    amount: Decimal,
):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Lock the fine to prevent concurrent overpayments.
            cursor.execute(
                """
                SELECT f.fine_id, f.amount, f.status
                FROM fines f
                JOIN loans l ON l.loan_id = f.loan_id
                WHERE f.fine_id = %s
                  AND l.member_id = %s
                FOR UPDATE OF f
                """,
                (fine_id, member_id),
            )
            fine = cursor.fetchone()

            if fine is None:
                # Do not reveal whether another member owns the fine.
                raise FineNotFoundError(
                    "Fine not found."
                )

            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0)::numeric
                    AS paid_amount
                FROM fine_payments
                WHERE fine_id = %s
                """,
                (fine_id,),
            )
            paid_amount = cursor.fetchone()["paid_amount"]

            outstanding = fine["amount"] - paid_amount

            if outstanding <= Decimal("0"):
                raise FineConflictError(
                    "This fine has already been paid."
                )

            if amount > outstanding:
                raise FineConflictError(
                    "Payment exceeds the outstanding balance."
                )

            cursor.execute(
                """
                INSERT INTO fine_payments (fine_id, amount)
                VALUES (%s, %s)
                RETURNING payment_id, fine_id, amount, paid_at
                """,
                (fine_id, amount),
            )
            payment = cursor.fetchone()

            new_outstanding = outstanding - amount

            if new_outstanding == Decimal("0"):
                new_status = "paid"
            elif paid_amount + amount > Decimal("0"):
                new_status = "partial"
            else:
                new_status = "unpaid"

            cursor.execute(
                """
                UPDATE fines
                SET status = %s
                WHERE fine_id = %s
                """,
                (new_status, fine_id),
            )

            return {
                **payment,
                "fine_status": new_status,
                "outstanding_amount": new_outstanding,
            }
