from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, UUID4


class UserCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=64)


class UserOutSchema(BaseModel):
    id: UUID4 = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    is_active: bool = Field(...)
    is_admin: bool = Field(...)

    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


class PasswordChangeSchema(BaseModel):
    old_password: str = Field(...)
    new_password: str = Field(...)
    confirmed_password: str = Field(...)
