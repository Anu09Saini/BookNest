# BookNest — Library Management System

BookNest is a library management system built with **FastAPI, PostgreSQL, psycopg 3, and Jinja2**. It models a library operating across three branches and supports catalogue management, member accounts, book circulation, fine payments, staff reporting, and secure partner catalogue access.

The project combines a REST API with a browser-based interface. It also includes a normalized relational database, SQL reports, authentication and authorization, a Postman collection, and a curl helper script.

## Table of Contents

1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Design Decisions and Rationale](#design-decisions-and-rationale)
5. [Installation and Setup](#installation-and-setup)
6. [Browser UI](#browser-ui)
7. [API Reference](#api-reference)
8. [Authentication and Authorization](#authentication-and-authorization)
9. [Partner Catalogue Integration](#partner-catalogue-integration)
10. [Postman Collection](#postman-collection)
11. [curl Helper](#curl-helper)
12. [SQL Reports](#sql-reports)
13. [Loom Demonstration](#loom-demonstration)

## Features

### Database and SQL
- Normalized PostgreSQL database schema.
- Primary keys, foreign keys, unique constraints, check constraints, and indexes.
- Parameterized SQL queries using psycopg 3.
- Separate tables for books, authors, physical copies, branches, members, staff, loans, fines, and fine payments.
- A many-to-many relationship between books and authors.
- SQL reporting queries using joins, filtering, grouping, aggregate functions, and `HAVING`.

### Book Catalogue
- Public catalogue browsing.
- API endpoints for listing books and retrieving book details.
- Staff-only Add New Book page.
- Required-field validation for book title, ISBN, and publication year.
- Duplicate ISBN prevention through a database unique constraint.
- Separate tracking of book titles and physical copies.

### Members and Authentication
- Member registration and login.
- JWT-based authentication for protected member API endpoints.
- Member profile, loan, and fine views.
- Member ownership checks for protected operations.
- Password hashing using Argon2 through `pwdlib`.

### Library Circulation
- Staff checkout and return operations.
- Maximum of three active loans per member.
- Due-date tracking and overdue loan identification.
- Fine calculation for overdue returns.
- Fine payment tracking, including partial payments and outstanding balances.

### Staff Dashboard and Reports
- Staff session authentication.
- Role-based access for active librarians and administrators.
- Dashboard for checkout and active-loan management.
- Separate Add New Book page.
- Dedicated Reports page containing:
  - Overdue loans.
  - Most-borrowed books.
  - Outstanding fines.
  - Physical copy counts and availability by branch.
- Navigation between the staff dashboard, book creation page, and reports page.

### Partner Catalogue API
- API-key and API-secret authentication.
- Partner secret verification against a stored hash.
- Rejection of invalid and inactive partner credentials.
- JSON catalogue access for authorized external applications.
- Swagger/OpenAPI support for testing the partner API.

### Developer Tools
- Swagger/OpenAPI documentation.
- Postman collection.
- curl helper script.
- SQL schema, seed data, and reporting queries.
- Automated API smoke tests.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Application programming language |
| FastAPI | REST API and request handling |
| PostgreSQL | Relational database |
| psycopg 3 | PostgreSQL connectivity and SQL execution |
| Pydantic | Request and response data validation |
| Jinja2 | Server-rendered browser UI |
| Starlette SessionMiddleware | Browser session management |
| JWT | Member API authentication |
| `pwdlib` with Argon2 | Password and partner-secret hashing |
| Postman | API testing |
| curl | Command-line API testing |

## Project Structure

```text
BookNest/
├── app/
│   ├── core/
│   │   └── security.py
│   ├── dependencies/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── static/
│   │   └── css/
│   ├── templates/
│   ├── database.py
│   └── main.py
├── sql/
│   ├── schema.sql
│   ├── seed.sql
│   └── reports.sql
├── tests/
├── postman/
│   └── BookNest.postman_collection.json
├── scripts/
│   ├── booknest_curl.sh
│   └── create_partner.py
├── .env.example
├── .gitignore
└── requirements.txt
```

The `app` directory contains the application, with routers handling requests, services implementing business and database operations, schemas defining data structures, and templates providing the browser UI.

The `sql` directory contains database creation, development seed data, and reporting queries. The `postman` and `scripts` provide API testing resources.

## Design Decisions and Rationale

The main design priorities are data integrity, security, maintainability, and a clear separation of responsibilities.

### 1. Relational Database and Normalization

**Decision:** Use PostgreSQL with a normalized relational schema.

**Rationale:** Library operations involve related entities, including books, physical copies, branches, members, loans, and payments. A relational database supports foreign-key relationships, uniqueness rules, constraints, and transactional operations.

Books and physical copies are modeled separately because one title may have multiple copies distributed across different branches. Authors are stored separately from books, with a junction table named `book_authors` to represent the many-to-many relationship.

This structure reduces unnecessary duplication and makes it easier to track individual copies, borrowing activity, and branch inventory.

### 2. Parameterized SQL and Database Services

**Decision:** Use psycopg 3 with parameterized SQL and reusable database service functions.

**Rationale:** Parameterized queries reduce SQL injection risk by keeping user-supplied values separate from SQL statements. Service functions centralize database operations and make them easier to reuse and maintain.

Database queries use placeholders such as `%s` rather than concatenating user input into SQL strings.

### 3. Separate API and Browser UI

**Decision:** Use FastAPI for REST endpoints and Jinja2 for server-rendered HTML pages.

**Rationale:** The API supports external clients and programmatic integration, while the browser interface makes common library operations accessible to members and staff.

Separating the two interfaces keeps API clients independent of the browser UI and provides a straightforward way to demonstrate the application without requiring a separate frontend framework.

### 4. Different Authentication Mechanisms

**Decision:** Use JWTs for member API requests, signed sessions for browser-based staff workflows, and API keys plus API secrets for partner integrations.

**Rationale:** These clients have different authentication needs.

- Member JWTs support authenticated API requests.
- Staff sessions support browser navigation and form submissions.
- Partner credentials allow external applications to access the catalogue without receiving staff or member credentials.

Authentication establishes the identity of a requester, while authorization determines which operations that requester may perform.

### 5. Role-Based Access and Member Data Isolation

**Decision:** Restrict staff operations to authorized staff roles and enforce ownership checks for member-specific resources.

**Rationale:** Library operations such as circulation and reporting should not be available to ordinary members or external partners. Members should only be able to access their own loans and fines.

Active librarians and administrators can access staff operations, while protected member endpoints verify the authenticated member's identity and ownership of the requested resource.

### 6. Book Circulation and Physical Copies

**Decision:** Represent a loan as the borrowing of a physical copy rather than only a book title.

**Rationale:** Multiple copies of the same title can exist at different branches. Tracking copies individually makes it possible to identify which copy is available, loaned, lost, or under maintenance.

The system enforces a three-active-loan limit per member. Database constraints and transaction handling help prevent conflicting operations, such as issuing the same copy to multiple active loans.

### 7. Fine and Payment Modeling

**Decision:** Store fines separately from fine payment records.

**Rationale:** A fine and its payments represent different business events. Keeping payment history separate supports partial payments and allows the system to calculate the remaining balance.

The application tracks unpaid, partially paid, and paid fines. This makes outstanding balances available for reporting and member account views.

### 8. Separate Staff Dashboard and Reports

**Decision:** Keep routine circulation operations on the staff dashboard and place detailed reports on a separate page.

**Rationale:** Checkout and return operations are frequent tasks, while reports are used for monitoring and decision-making. Separating these screens keeps the main dashboard focused and gives reports room for detailed tables.

The Reports page provides four views:

- **Overdue loans:** identifies books that have passed their due dates and remain unreturned.
- **Most-borrowed books:** shows borrowing frequency by title.
- **Outstanding fines:** identifies unpaid balances, including partially paid fines.
- **Copies per branch:** summarizes inventory and copy status across branches.

These reports support operational follow-up and library resource planning.

### 9. Separate Partner Catalogue API

**Decision:** Expose the partner catalogue through a dedicated authenticated API endpoint.

**Rationale:** External applications may need catalogue data, but they should not receive unrestricted access to member records or staff operations.

The partner API uses an API key to identify the partner and a separate API secret to verify credentials. The secret is stored as a hash, and inactive partners are rejected.

### 10. Validation and Error Handling

**Decision:** Validate inputs at request-handling boundaries and use database constraints for data-integrity rules.

**Rationale:** Browser-side validation improves usability, while server-side validation prevents invalid submissions from being accepted when browser checks are bypassed.

Database constraints provide additional protection for rules such as unique ISBNs and valid relationships. The application returns structured JSON errors for API requests and understandable messages for browser forms.

### 11. Configuration and Development Tooling

**Decision:** Store local configuration in environment variables and provide `.env.example`, API documentation, Postman requests, curl scripts, and tests.

**Rationale:** Environment-based configuration separates credentials from source code. An example environment file makes setup easier without publishing actual secrets.

Swagger, Postman, and curl provide complementary ways to inspect, exercise, and verify the application.

## Installation and Setup

### Prerequisites

Install the following before running BookNest:

- Python 3.11
- PostgreSQL
- pip
- Git
- A terminal and virtual environment

### 1. Clone the repository

```bash
git clone https://github.com/Anu09Saini/BookNest.git
cd BookNest
```

### 2. Create and activate a virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create the `library_db` database and an application user with the required permissions.

For example, an administrator can create the database and user using PostgreSQL's `psql` shell:

```sql
CREATE DATABASE library_db;
CREATE USER library_user WITH PASSWORD 'choose_a_local_password';
GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;
```

Apply the schema:

```bash
psql -d library_db -f sql/schema.sql
```

Load development seed data:

```bash
psql -d library_db -f sql/seed.sql
```


If your local PostgreSQL setup requires an explicit host or username, use the appropriate `psql` options, such as `-h localhost -U library_user`.

**Important:** Review `sql/seed.sql` before running it. Development seed scripts may reset existing data and should not be run against a database containing information you need to preserve.

### 5. Configure environment variables

Create your local environment file:

```bash
cp .env.example .env
```
Update `.env` with your actual local values.

Example configuration:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=library_db
DB_USER=library_user
DB_PASSWORD=your_database_password

JWT_SECRET_KEY=your_secure_jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

SESSION_SECRET_KEY=your_secure_session_secret
```

The database username and password must match your PostgreSQL configuration. Generate strong, separate secrets for JWT signing and session signing.


### 6. Run the application

```bash
uvicorn app.main:app --reload
```

The application will be available at:

`http://127.0.0.1:8000`


The `--reload` option is intended for development, not production deployment.

## Browser UI

| Page | URL | Access |
|---|---|---|
| Public catalogue | `/catalogue` | Public |
| Member registration | `/members/register` | Public |
| Member login | `/members/login` | Public |
| Member dashboard | `/members/dashboard` | Authenticated member |
| Staff login | `/staff/login` | Public |
| Staff dashboard | `/staff/dashboard` | Authorized staff |
| Add New Book | `/staff/books/new` | Librarian/admin |
| Library Reports | `/staff/reports` | Librarian/admin |
| Swagger documentation | `/docs` | API documentation |

The staff dashboard focuses on checkout, returns, and active loans. Book creation and detailed reports are accessed through separate pages.

Creating a book title does not automatically create physical copies. Physical copies are tracked separately and associated with library branches.

## API Reference

The following table summarizes the main API endpoints.


| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| GET | `/books/` | Public | List books |
| GET | `/books/{book_id}` | Public | Retrieve book details |
| POST | `/books/` | As configured by the API router | Create a book |
| POST | `/members/` | Public | Register a member |
| POST | `/auth/member/login` | Public | Obtain a member JWT |
| GET | `/members/me` | Member JWT | Retrieve current member profile |
| POST | `/auth/staff/login` | Public | Start a staff session |
| POST | `/auth/staff/logout` | Staff session | End a staff session |
| GET | `/staff/me` | Staff session | Retrieve current staff profile |
| POST | `/loans` | Staff session | Check out a physical copy |
| POST | `/loans/{loan_id}/return` | Staff session | Return a loan |
| GET | `/members/me/loans` | Member JWT | Retrieve own loans |
| GET | `/members/me/fines` | Member JWT | Retrieve own fines |
| POST | `/fines/{fine_id}/payments` | Member JWT | Pay an eligible fine |
| GET | `/reports/overdue-loans` | Librarian/admin | Retrieve overdue loans |
| GET | `/reports/most-borrowed-books` | Librarian/admin | Retrieve borrowing statistics |
| GET | `/partner/catalogue/books` | Partner API key and secret | Retrieve partner catalogue |

The browser UI also provides the outstanding-fines and copies-per-branch reports. These are currently presented through the staff Reports page; they do not have separate REST endpoints.

## Authentication and Authorization

### Member API Authentication

Members log in through:

```text
POST /auth/member/login
```

The API returns an access token. Protected member endpoints require the token in the `Authorization` header:

```http
Authorization: Bearer (Enter_Access_token)
```

Example:

```bash
curl http://127.0.0.1:8000/members/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Replace the placeholder with the token returned by the login endpoint.


### Staff Session Authentication

Staff authenticate through:

```text
POST /auth/staff/login
```

The browser UI uses a signed session cookie to maintain the staff session. Protected staff pages and circulation operations require an active, authorized staff session.

Postman can retain cookies after login, and the curl helper uses a local cookie jar for staff workflows.

### Authorization Rules

- Active librarians can access authorized staff operations and reports.
- Members can access their own protected resources.
- Member ownership checks prevent access to another member's loans and fines.
- Partner credentials grant access to the partner catalogue, not to staff or member operations.

## Partner Catalogue Integration

BookNest exposes a dedicated endpoint for authorized external applications:

```text
GET /partner/catalogue/books
```

The endpoint returns catalogue data in JSON format and requires two HTTP headers:

```http
X-API-Key: YOUR_PARTNER_API_KEY
X-API-Secret: YOUR_PARTNER_API_SECRET
```

### 1. Create partner credentials

Run the partner creation script:

```bash
python -m scripts.create_partner
```

Follow the script's prompts and securely save the generated credentials.

The application stores the secret as a hash and verifies the supplied secret when requests are made.

### 2. Test with curl

Set your credentials in your local terminal:

```bash
export BOOKNEST_PARTNER_API_KEY="YOUR_PARTNER_API_KEY"
export BOOKNEST_PARTNER_API_SECRET="YOUR_PARTNER_API_SECRET"
```

Use the helper script:

```bash
scripts/booknest_curl.sh partner-books
```

Alternatively, call the endpoint directly:

```bash
curl -X GET \
  "http://127.0.0.1:8000/partner/catalogue/books" \
  -H "X-API-Key: $BOOKNEST_PARTNER_API_KEY" \
  -H "X-API-Secret: $BOOKNEST_PARTNER_API_SECRET"
```

### 3. Test with Swagger

1. Start the application and open `http://127.0.0.1:8000/docs`.
2. Locate `GET /partner/catalogue/books`.
3. Click **Authorize**.
4. Enter the partner API key and secret in the corresponding security fields.
5. Click **Authorize** and close the dialog.
6. Execute the catalogue request.

### 4. Expected behavior

- Valid credentials belonging to an active partner should return the catalogue.
- Missing or incorrect credentials should be rejected.
- Credentials belonging to an inactive partner should be rejected.

## Postman Collection

The Postman collection is located at:

```text
postman/BookNest.postman_collection.json
```

Import it into Postman using **Import**.

Configure the collection variables for the base URL, member token, and required credentials according to the requests in the collection.

Recommended testing workflow:

1. Log in as staff before testing checkout, return, and staff report endpoints.
2. Log in as a member and use the returned access token for protected member requests.
3. Use valid IDs from the development database.
4. Pay only fines belonging to the authenticated member and do not exceed the outstanding balance.
5. Use unique ISBNs and email addresses for create/register requests.
6. Test partner access with valid credentials and verify that invalid credentials are rejected.


## curl Helper

The helper script is located at:

```text
scripts/booknest_curl.sh
```

Make it executable:

```bash
chmod +x scripts/booknest_curl.sh
```

List the supported commands:

```bash
scripts/booknest_curl.sh help
```

Examples:

```bash
scripts/booknest_curl.sh books
scripts/booknest_curl.sh book 1
scripts/booknest_curl.sh staff-login YOUR_STAFF_EMAIL YOUR_STAFF_PASSWORD
scripts/booknest_curl.sh staff-me
scripts/booknest_curl.sh overdue
scripts/booknest_curl.sh popular 5
```

### Member workflow

Log in with a development member account:

```bash
scripts/booknest_curl.sh member-login YOUR_MEMBER_EMAIL YOUR_MEMBER_PASSWORD
```

Use the access token according to the helper's instructions, then run:

```bash
scripts/booknest_curl.sh member-loans
scripts/booknest_curl.sh member-fines
```

### Partner workflow

```bash

export BOOKNEST_PARTNER_API_KEY="YOUR_PARTNER_API_KEY"
export BOOKNEST_PARTNER_API_SECRET="YOUR_PARTNER_API_SECRET"
scripts/booknest_curl.sh partner-books
```

Refer to the helper's usage output for the supported commands and arguments.

## SQL Reports

The SQL reporting queries are located in:

```text
sql/reports.sql
```

The reports cover:

- Overdue loans.
- Most-borrowed books.
- Outstanding fines.
- Physical copy counts by branch.

They demonstrate joins, filtering, grouping, aggregate functions, and `HAVING`.

The browser-based Reports page presents four reports for library staff. The SQL reporting file provides queries for database-level reporting and demonstrates relational query techniques.


## Loom Demonstration

Video:   https://www.loom.com/share/8577fd169d974f96b21f3f1e71965151


