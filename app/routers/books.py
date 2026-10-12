from fastapi import APIRouter, HTTPException, status
from psycopg.errors import UniqueViolation

from app.schemas.book import BookDetail, BookListItem, BookCreate
from app.services.book_service import (create_book, get_all_books, get_book_by_id,)

router = APIRouter(
  prefix="/books",
  tags=["Books"],
)


@router.get("/", response_model=list[BookListItem])
def list_books():
  """Return all books with physical copy counts."""
  return get_all_books()


@router.get("/{book_id}", response_model=BookDetail)
def retrieve_book(book_id: int):
  """Return a single book by its ID."""
  book = get_book_by_id(book_id)

  if book is None:
    raise HTTPException(
      status_code=404,
      detail={
          "error": "BOOK_NOT_FOUND",
          "message": f"Book with ID {book_id} was not found.",
      },
    )

  return book



@router.post("/", response_model=BookDetail, status_code=status.HTTP_201_CREATED)
def add_book(book_data: BookCreate):
  try:
    book = create_book(
      title=book_data.title,
      isbn=book_data.isbn,
      publication_year=book_data.publication_year,
    )
    return book

  except UniqueViolation as exc:
    raise HTTPException(
      status_code=409,
      detail={
        "error": "DUPLICATE_ISBN",
        "message": "A book with this ISBN already exists.",
      },
    ) from exc

