import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

# Load database configuration from the .env file.
load_dotenv()


def get_connection():
  """
  Create and return a PostgreSQL connection.

  The caller is responsible for closing the connection,
  preferably by using it in a 'with' statement.
  """
  return psycopg.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    dbname=os.getenv("DB_NAME", "library_db"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    connect_timeout=5,
    row_factory=dict_row,
  )


def fetch_all(query, params=None):
  """Execute a SELECT query and return all matching rows."""
  with get_connection() as conn:
    with conn.cursor() as cursor:
      cursor.execute(query, params)
      return cursor.fetchall()


def fetch_one(query, params=None):
  """Execute a query and return one row, or None."""
  with get_connection() as conn:
    with conn.cursor() as cursor:
      cursor.execute(query, params)
      return cursor.fetchone()


def execute_query(query, params=None):
  """
  Execute an INSERT, UPDATE, or DELETE query.

  The transaction commits on success and rolls back
  automatically if an exception occurs.
  """
  with get_connection() as conn:
    with conn.cursor() as cursor:
      cursor.execute(query, params)
      return cursor.rowcount
