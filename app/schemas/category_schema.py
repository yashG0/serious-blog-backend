from datetime import datetime

from pydantic import BaseModel, Field, UUID4


class CategoryCreateSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)
    description: str = Field(..., min_length=12, max_length=550)


class CategoryOutSchema(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(...)
    description: str = Field(...)

    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    class Config:
        from_attributes = True
