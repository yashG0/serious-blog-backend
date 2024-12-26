from datetime import datetime

from pydantic import BaseModel, Field, UUID4


class CommentCreateSchema(BaseModel):
    content: str = Field(...)


class CommentOutSchema(BaseModel):
    id: UUID4 = Field(...)
    content: str = Field(...)
    post_id: UUID4 = Field(...)
    user_id: UUID4 = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
