from app.services.book_service import get_all_books, get_book_by_id


def main():
  books = get_all_books()

  print(f"Total book titles: {len(books)}")

  for book in books:
    print(
      f"{book['title']} | "
      f"Total copies: {book['total_copies']} | "
      f"Available: {book['available_copies']}"
    )

  if books:
    book_id = books[0]["book_id"]
    print("\nBook details:")
    print(get_book_by_id(book_id))


if __name__ == "__main__":
  main()