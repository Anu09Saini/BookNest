from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class MemberCreate(BaseModel):
	name: str = Field(min_length=1, max_length=150)
	email: EmailStr
	password: str = Field(min_length=8, max_length=128)

	@field_validator("name")
	@classmethod
	def validate_name(cls, value: str) -> str:
		value = value.strip()

		if not value:
				raise ValueError("Name cannot be empty.")

		return value

	@field_validator("email")
	@classmethod
	def normalize_email(cls, value: str) -> str:
		return value.strip().lower()


class MemberLogin(BaseModel):
	email: EmailStr
	password: str = Field(min_length=1, max_length=128)

	@field_validator("email")
	@classmethod
	def normalize_email(cls, value: str) -> str:
		return value.strip().lower()


class MemberResponse(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	member_id: int
	name: str
	email: EmailStr
	status: str


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"
	expires_in: int
