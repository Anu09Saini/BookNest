-- Find all overdue loans

SELECT
    l.loan_id,
    m.name AS member_name,
    m.email,
    b.title AS book_title,
    br.name AS branch_name,
    l.checkout_date,
    l.due_date,
    CURRENT_DATE - l.due_date AS days_overdue
FROM loans AS l
JOIN members AS m
    ON m.member_id = l.member_id
JOIN book_copies AS cp
    ON cp.copy_id = l.copy_id
JOIN books AS b
    ON b.book_id = cp.book_id
JOIN branches AS br
    ON br.branch_id = cp.branch_id
WHERE l.return_date IS NULL
  AND l.due_date < CURRENT_DATE
ORDER BY l.due_date ASC;



-- Find the most borrowed books

SELECT
    b.book_id,
    b.title,
    COUNT(l.loan_id) AS total_borrowings
FROM books AS b
JOIN book_copies AS cp
    ON cp.book_id = b.book_id
JOIN loans AS l
    ON l.copy_id = cp.copy_id
GROUP BY b.book_id, b.title
ORDER BY total_borrowings DESC, b.title ASC
LIMIT 5;


-- Calculate outstanding fines per member

SELECT
    m.member_id,
    m.name AS member_name,
    f.fine_id,
    f.amount AS original_fine,
    COALESCE(SUM(fp.amount), 0) AS amount_paid,
    f.amount - COALESCE(SUM(fp.amount), 0) AS outstanding_amount
FROM members AS m
JOIN loans AS l
    ON l.member_id = m.member_id
JOIN fines AS f
    ON f.loan_id = l.loan_id
LEFT JOIN fine_payments AS fp
    ON fp.fine_id = f.fine_id
GROUP BY
    m.member_id,
    m.name,
    f.fine_id,
    f.amount
HAVING f.amount - COALESCE(SUM(fp.amount), 0) > 0
ORDER BY outstanding_amount DESC;


-- Summarize available and borrowed copies by branch

SELECT
    br.name AS branch_name,
    COUNT(cp.copy_id) AS total_copies,
    COUNT(cp.copy_id) FILTER (
        WHERE cp.status = 'available'
    ) AS available_copies,
    COUNT(cp.copy_id) FILTER (
        WHERE cp.status = 'loaned'
    ) AS loaned_copies
FROM branches AS br
LEFT JOIN book_copies AS cp
    ON cp.branch_id = br.branch_id
GROUP BY br.branch_id, br.name
ORDER BY br.name;
