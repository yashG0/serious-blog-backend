from datetime import datetime
from pydantic import BaseModel, Field, UUID4


class PostCreateSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=3)
    category_id: UUID4 = Field(...)


class PostOutSchema(BaseModel):
    id: UUID4 = Field(...)
    title: str = Field(...)
    content: str = Field(...)
    image: str | None = Field(default=None)
    created_at: datetime
    updated_at: datetime


class PostUpdateSchema(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    content: str | None = Field(default=None, min_length=3)
    image: str | None = Field(default=None)
    category_id: UUID4 | None = Field(default=None)
