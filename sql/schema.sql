
-- ============================================
-- BookNest: Library Management Database
-- Database: PostgreSQL
-- ============================================

-- 1. Library branches
CREATE TABLE IF NOT EXISTS branches (
    branch_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    address TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Books: one record per book title/edition
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(255) NOT NULL,
    publication_year INTEGER
        CHECK (publication_year BETWEEN 1 AND 9999),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. Authors
CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(150) NOT NULL
);

-- 4. Many-to-many relationship between books and authors
CREATE TABLE IF NOT EXISTS book_authors (
    book_id INTEGER NOT NULL
        REFERENCES books(book_id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL
        REFERENCES authors(author_id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, author_id)
);

-- 5. Physical copies of books at individual branches
CREATE TABLE IF NOT EXISTS book_copies (
    copy_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    book_id INTEGER NOT NULL
        REFERENCES books(book_id),
    branch_id INTEGER NOT NULL
        REFERENCES branches(branch_id),
    status VARCHAR(20) NOT NULL DEFAULT 'available'
        CHECK (status IN (
            'available', 'loaned', 'lost', 'maintenance'
        )),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. Library members
CREATE TABLE IF NOT EXISTS members (
    member_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'suspended', 'inactive')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. Library staff
CREATE TABLE IF NOT EXISTS staff (
    staff_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    branch_id INTEGER NOT NULL REFERENCES branches(branch_id),
    name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'librarian'
        CHECK (role IN ('librarian', 'admin')),
    status VARCHAR(20) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive'))
);

-- 8. Loans and returns
CREATE TABLE IF NOT EXISTS loans (
    loan_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    copy_id INTEGER NOT NULL REFERENCES book_copies(copy_id),
    member_id INTEGER NOT NULL REFERENCES members(member_id),
    checkout_staff_id INTEGER NOT NULL REFERENCES staff(staff_id),
    return_staff_id INTEGER REFERENCES staff(staff_id),
    checkout_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (due_date >= checkout_date),
    CHECK (return_date IS NULL OR return_date >= checkout_date),
    CHECK (return_date IS NULL OR return_staff_id IS NOT NULL)
);

-- A physical copy can have only one active loan.
CREATE UNIQUE INDEX IF NOT EXISTS
    uq_loans_one_active_loan_per_copy
ON loans(copy_id)
WHERE return_date IS NULL;

-- 9. Fines: one fine record per loan
CREATE TABLE IF NOT EXISTS fines (
    fine_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    loan_id INTEGER NOT NULL UNIQUE REFERENCES loans(loan_id),
    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'unpaid'
        CHECK (status IN ('unpaid', 'partial', 'paid')),
    assessed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 10. Fine payment history
CREATE TABLE IF NOT EXISTS fine_payments (
    payment_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fine_id INTEGER NOT NULL REFERENCES fines(fine_id),
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    paid_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 11. Partner catalogue service credentials
CREATE TABLE IF NOT EXISTS partner_clients (
    partner_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    secret_hash TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Indexes for common queries
-- ============================================

CREATE INDEX IF NOT EXISTS idx_copies_book_branch
    ON book_copies(book_id, branch_id);

CREATE INDEX IF NOT EXISTS idx_loans_member
    ON loans(member_id);

CREATE INDEX IF NOT EXISTS idx_loans_due_date
    ON loans(due_date);

CREATE INDEX IF NOT EXISTS idx_loans_active_member
    ON loans(member_id)
    WHERE return_date IS NULL;

CREATE INDEX IF NOT EXISTS idx_fines_status
    ON fines(status);

CREATE INDEX IF NOT EXISTS idx_fine_payments_fine
    ON fine_payments(fine_id);
