from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_docs_are_available():
  response = client.get("/docs")
  assert response.status_code == 200


def test_catalogue_page_loads():
  response = client.get("/catalogue")
  assert response.status_code == 200
  assert "BookNest" in response.text


def test_books_endpoint_returns_json():
  response = client.get("/books/")

  assert response.status_code == 200
  assert isinstance(response.json(), list)


def test_member_dashboard_requires_login():
  response = client.get("/members/dashboard", follow_redirects=False)

  assert response.status_code == 303
  assert response.headers["location"] == "/members/login"


def test_staff_dashboard_requires_login():
  response = client.get("/staff/dashboard", follow_redirects=False)

  assert response.status_code == 303
  assert response.headers["location"] == "/staff/login"


def test_partner_catalogue_rejects_missing_credentials():
  response = client.get("/partner/catalogue/books")

  assert response.status_code == 401


def test_reports_reject_missing_staff_session():
  response = client.get(
      "/reports/overdue-loans",
      follow_redirects=False,
  )
  assert response.status_code == 401
