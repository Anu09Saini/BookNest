import os
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from app.errors import (
    http_exception_handler,
    validation_exception_handler,
)

from app.routers import auth, books, fines, loans, members, partner, reports, staff_auth, pages

load_dotenv()

app = FastAPI(
    title="BookNest Library API",
    description="REST API for managing library books, members, loans, and fines.",
    version="1.0.0",
)



BASE_DIR = Path(__file__).resolve().parent

app.mount(
  "/static",
  StaticFiles(directory=str(BASE_DIR / "static")),
  name="static",
)

templates = Jinja2Templates(
  directory=str(BASE_DIR / "templates")
)


session_secret = os.getenv("SESSION_SECRET_KEY")
if not session_secret:
  raise RuntimeError("SESSION_SECRET_KEY must be configured in .env")


app.add_middleware(
  SessionMiddleware,
  secret_key=session_secret,
  session_cookie="booknest_staff_session",
  max_age=1800,
  same_site="lax",
  https_only=False,  # Local development only; use True in production.
)


app.add_exception_handler(
  HTTPException,
  http_exception_handler,
)

app.add_exception_handler(
  RequestValidationError,
  validation_exception_handler,
)

app.include_router(books.router)
app.include_router(members.router)
app.include_router(auth.router)
app.include_router(staff_auth.router)
app.include_router(loans.router)
app.include_router(fines.router)
app.include_router(reports.router)
app.include_router(partner.router)
app.include_router(pages.router)


@app.get("/")
def home():
  return {
    "message": "Welcome to BookNest Library API",
    "status": "running",
  }


@app.get("/health")
def health_check():
  return {"status": "healthy"}
