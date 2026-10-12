from pydantic import BaseModel, EmailStr, Field, field_validator


class StaffLogin(BaseModel):
  email: EmailStr
  password: str = Field(min_length=1, max_length=128)

  @field_validator("email")
  @classmethod
  def normalize_email(cls, value: str) -> str:
    return value.strip().lower()


class StaffResponse(BaseModel):
  staff_id: int
  name: str
  email: EmailStr
  branch_id: int
  role: str
  status: str