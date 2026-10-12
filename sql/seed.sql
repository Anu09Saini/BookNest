
-- ============================================
-- BookNest: Sample Data
-- WARNING: This reset is intended ONLY for
-- the development database.
-- ============================================

BEGIN;

-- Clear sample data and restart IDs.
-- Do not run against a database containing
-- data you need to preserve.
TRUNCATE TABLE
    fine_payments,
    fines,
    loans,
    book_copies,
    book_authors,
    authors,
    books,
    members,
    staff,
    partner_clients,
    branches
RESTART IDENTITY CASCADE;

-- 1. Branches
INSERT INTO branches (name, address) VALUES
    ('Central Library', 'Sector 17, Chandigarh'),
    ('North Branch', 'Sector 15, Chandigarh'),
    ('South Branch', 'Sector 34, Chandigarh');

-- 2. Books
INSERT INTO books (isbn, title, publication_year) VALUES
    ('9780735211292', 'Atomic Habits', 2018),
    ('9780062315007', 'The Alchemist', 1988),
    ('9780132350884', 'Clean Code', 2008),
    ('9780134685991', 'Effective Java', 2017),
    ('9781501124020', 'Educated', 2018),
    ('9780141439518', 'Pride and Prejudice', 1813);

-- 3. Authors
INSERT INTO authors (name) VALUES
    ('James Clear'),
    ('Paulo Coelho'),
    ('Robert C. Martin'),
    ('Joshua Bloch'),
    ('Tara Westover'),
    ('Jane Austen');

-- 4. Connect books and authors
INSERT INTO book_authors (book_id, author_id)
SELECT b.book_id, a.author_id
FROM (VALUES
    ('9780735211292', 'James Clear'),
    ('9780062315007', 'Paulo Coelho'),
    ('9780132350884', 'Robert C. Martin'),
    ('9780134685991', 'Joshua Bloch'),
    ('9781501124020', 'Tara Westover'),
    ('9780141439518', 'Jane Austen')
) AS x(isbn, author_name)
JOIN books b ON b.isbn = x.isbn
JOIN authors a ON a.name = x.author_name;

-- 5. Physical copies across branches
INSERT INTO book_copies (book_id, branch_id, status)
SELECT b.book_id, br.branch_id, x.status
FROM (VALUES
    ('9780735211292', 'Central Library', 'loaned'),
    ('9780735211292', 'Central Library', 'available'),
    ('9780735211292', 'North Branch', 'loaned'),
    ('9780062315007', 'Central Library', 'available'),
    ('9780062315007', 'South Branch', 'loaned'),
    ('9780132350884', 'Central Library', 'available'),
    ('9780132350884', 'North Branch', 'available'),
    ('9780134685991', 'South Branch', 'available'),
    ('9781501124020', 'North Branch', 'available'),
    ('9780141439518', 'South Branch', 'available')
) AS x(isbn, branch_name, status)
JOIN books b ON b.isbn = x.isbn
JOIN branches br ON br.name = x.branch_name;

-- 6. Members
-- Password values are placeholders, not usable
-- authentication hashes. We will replace them
-- with real hashes when implementing authentication.
INSERT INTO members (name, email, password_hash, status) VALUES
    ('Ananya Sharma', 'ananya@example.com',
     'REPLACE_WITH_PASSWORD_HASH', 'active'),
    ('Rohan Mehta', 'rohan@example.com',
     'REPLACE_WITH_PASSWORD_HASH', 'active'),
    ('Priya Verma', 'priya@example.com',
     'REPLACE_WITH_PASSWORD_HASH', 'active'),
    ('Kabir Singh', 'kabir@example.com',
     'REPLACE_WITH_PASSWORD_HASH', 'active');

-- 7. Staff
INSERT INTO staff
    (branch_id, name, email, password_hash, role, status)
SELECT br.branch_id, x.name, x.email,
       'REPLACE_WITH_PASSWORD_HASH', x.role, 'active'
FROM (VALUES
    ('Central Library', 'Neha Kapoor',
     'neha.staff@example.com', 'admin'),
    ('North Branch', 'Aman Gill',
     'aman.staff@example.com', 'librarian'),
    ('South Branch', 'Simran Kaur',
     'simran.staff@example.com', 'librarian')
) AS x(branch_name, name, email, role)
JOIN branches br ON br.name = x.branch_name;

-- 8. Loans
-- Loan A: active, due in the future
-- Loan B: active, overdue
-- Loan C: returned late
-- Loan D: returned on time
-- Loan E: active, due in the future

INSERT INTO loans (
    copy_id, member_id, checkout_staff_id,
    return_staff_id, checkout_date, due_date, return_date
)
SELECT cp.copy_id, m.member_id, s.staff_id,
       NULL, CURRENT_DATE - 5, CURRENT_DATE + 9, NULL
FROM book_copies cp
JOIN books b ON b.book_id = cp.book_id
JOIN branches br ON br.branch_id = cp.branch_id
JOIN members m ON m.email = 'ananya@example.com'
JOIN staff s ON s.email = 'neha.staff@example.com'
WHERE b.isbn = '9780735211292'
  AND br.name = 'Central Library'
  AND cp.status = 'loaned';

INSERT INTO loans (
    copy_id, member_id, checkout_staff_id,
    return_staff_id, checkout_date, due_date, return_date
)
SELECT cp.copy_id, m.member_id, s.staff_id,
       NULL, CURRENT_DATE - 20, CURRENT_DATE - 6, NULL
FROM book_copies cp
JOIN books b ON b.book_id = cp.book_id
JOIN branches br ON br.branch_id = cp.branch_id
JOIN members m ON m.email = 'rohan@example.com'
JOIN staff s ON s.email = 'aman.staff@example.com'
WHERE b.isbn = '9780735211292'
  AND br.name = 'North Branch'
  AND cp.status = 'loaned';

INSERT INTO loans (
    copy_id, member_id, checkout_staff_id,
    return_staff_id, checkout_date, due_date, return_date
)
SELECT cp.copy_id, m.member_id, checkout_staff.staff_id,
       return_staff.staff_id, CURRENT_DATE - 30,
       CURRENT_DATE - 20, CURRENT_DATE - 17
FROM book_copies cp
JOIN books b ON b.book_id = cp.book_id
JOIN branches br ON br.branch_id = cp.branch_id
JOIN members m ON m.email = 'priya@example.com'
JOIN staff checkout_staff
    ON checkout_staff.email = 'neha.staff@example.com'
JOIN staff return_staff
    ON return_staff.email = 'neha.staff@example.com'
WHERE b.isbn = '9780062315007'
  AND br.name = 'South Branch'
  AND cp.status = 'loaned';

-- The previous loan uses the same book title at
-- South Branch, which is also currently marked loaned.
-- Its return date is historical; copy status will be
-- reconciled in a later verification step.

INSERT INTO loans (
    copy_id, member_id, checkout_staff_id,
    return_staff_id, checkout_date, due_date, return_date
)
SELECT cp.copy_id, m.member_id, s.staff_id,
       s.staff_id, CURRENT_DATE - 15,
       CURRENT_DATE - 5, CURRENT_DATE - 5
FROM book_copies cp
JOIN books b ON b.book_id = cp.book_id
JOIN branches br ON br.branch_id = cp.branch_id
JOIN members m ON m.email = 'kabir@example.com'
JOIN staff s ON s.email = 'simran.staff@example.com'
WHERE b.isbn = '9780062315007'
  AND br.name = 'South Branch'
  AND cp.status = 'loaned';

INSERT INTO loans (
    copy_id, member_id, checkout_staff_id,
    return_staff_id, checkout_date, due_date, return_date
)
SELECT cp.copy_id, m.member_id, s.staff_id,
       NULL, CURRENT_DATE - 2, CURRENT_DATE + 12, NULL
FROM book_copies cp
JOIN books b ON b.book_id = cp.book_id
JOIN branches br ON br.branch_id = cp.branch_id
JOIN members m ON m.email = 'ananya@example.com'
JOIN staff s ON s.email = 'neha.staff@example.com'
WHERE b.isbn = '9780062315007'
  AND br.name = 'South Branch'
  AND cp.status = 'loaned';

-- 9. Fines
-- Three days late * 10 = 30
INSERT INTO fines (loan_id, amount, status)
SELECT l.loan_id, 30.00, 'unpaid'
FROM loans l
JOIN members m ON m.member_id = l.member_id
JOIN book_copies cp ON cp.copy_id = l.copy_id
JOIN books b ON b.book_id = cp.book_id
WHERE m.email = 'priya@example.com'
  AND b.isbn = '9780062315007'
  AND l.return_date IS NOT NULL;

-- 10. Example payment history
-- Payment of 10 against a fine of 30.
UPDATE fines
SET status = 'partial'
WHERE loan_id IN (
    SELECT l.loan_id
    FROM loans l
    JOIN members m ON m.member_id = l.member_id
    JOIN book_copies cp ON cp.copy_id = l.copy_id
    JOIN books b ON b.book_id = cp.book_id
    WHERE m.email = 'priya@example.com'
      AND b.isbn = '9780062315007'
      AND l.return_date IS NOT NULL
);

INSERT INTO fine_payments (fine_id, amount)
SELECT f.fine_id, 10.00
FROM fines f
JOIN loans l ON l.loan_id = f.loan_id
JOIN members m ON m.member_id = l.member_id
WHERE m.email = 'priya@example.com';

COMMIT;
