from pydantic import BaseModel, Field, field_validator


class BookCreate(BaseModel):
	title: str = Field(min_length=1, max_length=255)
	isbn: str | None = Field(default=None, max_length=20)
	publication_year: int | None = Field(default=None, ge=1, le=9999)

	@field_validator("title")
	@classmethod
	def validate_title(cls, value: str) -> str:
		value = value.strip()

		if not value:
			raise ValueError("Title cannot be empty.")

		return value

	@field_validator("isbn")
	@classmethod
	def normalize_isbn(cls, value: str | None) -> str | None:
		if value is None:
			return None

		value = value.strip()
		return value or None


class BookListItem(BaseModel):
	book_id: int
	title: str
	isbn: str | None
	publication_year: int | None
	total_copies: int
	available_copies: int


class BookDetail(BaseModel):
	book_id: int
	title: str
	isbn: str | None
	publication_year: int | None
