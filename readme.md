# BookNest — Library Management System

BookNest is a library management backend with a basic browser UI, built using FastAPI, PostgreSQL, psycopg, and Jinja2. It models a library with three branches and supports catalogue browsing, member accounts, book circulation, fines, staff reports, and partner catalogue access.


## Features

- Relational PostgreSQL schema with primary/foreign keys, constraints, and indexes.
- Parameterized SQL queries using psycopg.
- Book catalogue and book detail endpoints.
- Member registration and JWT-based API authentication.
- Staff session authentication for circulation and reports.
- Book checkout and returns, including a three-active-loan limit.
- Overdue fine calculation and fine payment tracking.
- Member-specific loan and fine views.
- Reports for overdue loans and most-borrowed books.
- Partner catalogue authentication using an API key and hashed API secret.
- Jinja2 UI for public catalogue, member area, and librarian dashboard.
- Postman collection, curl helper, SQL reports, and smoke tests.

## Stack

Python 3.11, FastAPI, PostgreSQL, psycopg 3, Pydantic, Jinja2, Starlette SessionMiddleware, JWT, and Argon2 password hashing via `pwdlib`.

## Project structure

```text
BookNest/
├── app/
│   ├── core/
│   ├── dependencies/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── static/css/
│   ├── templates/
│   ├── database.py
│   └── main.py
├── sql/
│   ├── schema.sql
│   ├── seed.sql
│   └── reports.sql
├── tests/
├── postman/BookNest.postman_collection.json
├── scripts/
│   ├── booknest_curl.sh
│   └── create_partner.py
├── .env.example
├── .gitignore
└── requirements.txt
```

## Setup

Prerequisites: Python 3.11, PostgreSQL, pip, and a virtual environment.

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create the `library_db` database and `lib_user` application user if not already configured. Apply the schema and seed data using your local PostgreSQL setup:

```bash
psql -d library_db -f sql/schema.sql
psql -d library_db -f sql/seed.sql
```

**Warning:** inspect `sql/seed.sql` first. It may truncate tables and reset IDs. Never run it against data you need to preserve.

Create `.env` from `.env.example` and fill in your local values. Typical variables:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=library_db
DB_USER=lib_user
DB_PASSWORD=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
SESSION_SECRET_KEY=
```

Run the application:

```bash
uvicorn app.main:app --reload
```

## Browser pages and API docs

- Public catalogue: http://127.0.0.1:8000/catalogue
- Member login: http://127.0.0.1:8000/members/login
- Member dashboard: http://127.0.0.1:8000/members/dashboard
- Staff login: http://127.0.0.1:8000/staff/login
- Staff dashboard: http://127.0.0.1:8000/staff/dashboard
- Swagger/OpenAPI: http://127.0.0.1:8000/docs

## API reference

| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| GET | `/books/` | Public | List books |
| GET | `/books/{book_id}` | Public | Get book details |
| POST | `/books/` | Follow router policy | Create a book |
| POST | `/members/` | Public | Register a member |
| POST | `/auth/member/login` | Public | Get member JWT |
| GET | `/members/me` | Member JWT | Current member profile |
| POST | `/auth/staff/login` | Public | Start staff session |
| POST | `/auth/staff/logout` | Staff session | End staff session |
| GET | `/staff/me` | Staff session | Current staff profile |
| POST | `/loans` | Staff session | Check out a copy |
| POST | `/loans/{loan_id}/return` | Staff session | Return a loan |
| GET | `/members/me/loans` | Member JWT | Current member's loans |
| GET | `/members/me/fines` | Member JWT | Current member's fines |
| POST | `/fines/{fine_id}/payments` | Member JWT | Pay own fine |
| GET | `/reports/overdue-loans` | Librarian/admin session | Overdue report |
| GET | `/reports/most-borrowed-books` | Librarian/admin session | Popularity report |
| GET | `/partner/catalogue/books` | Partner key + secret | Partner catalogue |

Use `/docs` for the exact schemas and status codes in the running version.

## Authentication

### Member API
Member login returns a JWT. Send it on protected API requests:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Staff API
Staff login uses a signed session cookie. Postman retains the cookie after login; the curl helper stores it in a local cookie jar.

### Partner API
Partner requests use `X-API-Key` and `X-API-Secret`. Create credentials locally:

```bash
python -m scripts.create_partner
```

Save the secret securely when displayed. Only its hash is stored in the database.

## Postman collection

Import `postman/BookNest.postman_collection.json` through Postman's **Import** action. Set collection variables for base URL, member/staff credentials, and partner credentials.

Recommended workflow:
1. Log in as staff before checkout, return, and report requests.
2. Log in as a member and copy `access_token` to `member_token`.
3. Use valid IDs from development database.
4. Pay only a fine owned by the authenticated member; do not exceed its outstanding balance.
5. Use unique ISBNs and emails for create/register requests.

The collection contains write requests. Use a development database and avoid repeated destructive or duplicate submissions.

## curl helper

```bash
chmod +x scripts/booknest_curl.sh
scripts/booknest_curl.sh books
scripts/booknest_curl.sh book 1
scripts/booknest_curl.sh staff-login neha.staff@example.com 'nehastaff'
scripts/booknest_curl.sh staff-me
scripts/booknest_curl.sh overdue
scripts/booknest_curl.sh popular 5
```

Member workflow:

```bash
scripts/booknest_curl.sh member-login testmember@example.com 'Testmember1'
export BOOKNEST_MEMBER_TOKEN=''
scripts/booknest_curl.sh member-loans
scripts/booknest_curl.sh member-fines
```

Partner workflow:

```bash
export BOOKNEST_PARTNER_API_KEY='bn_live_LPk02ehW5_V-tybm7CJDKNBP8YYJQTQK'
export BOOKNEST_PARTNER_API_SECRET='OtJlp7w2OGDl8yQ8FoZ7SuOMd9yLSuDyPGFJkr6iVGPe3reWIeBFXppFcuh-DJCn'
scripts/booknest_curl.sh partner-books
```

List commands with `scripts/booknest_curl.sh help`. 

## SQL reports

`sql/reports.sql` includes queries for overdue loans, most-borrowed books, outstanding fines, and copy counts by branch. They demonstrate joins, filtering, grouping, aggregates, and `HAVING`.




## Loom Video Link:   
  Video:   https://www.loom.com/share/8577fd169d974f96b21f3f1e71965151