from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship

from ..db.config import base


class User(base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # relationship ->
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")


class Post(base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    image = Column(String, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'))

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # relationship ->
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    category = relationship("Category", back_populates="posts")


class Category(base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # relationship ->
    posts = relationship("Post", back_populates="category")


class Comment(base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    content = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id'))

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # relationship ->
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
