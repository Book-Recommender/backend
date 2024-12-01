from __future__ import annotations

from pydantic import BaseModel

from .orm import BookStatus


class Author(BaseModel):
    """Author."""

    id: int
    name: str
    books: list[Book]


class Book(BaseModel):
    """Book."""

    id: int
    isbn: str
    title: str
    authors: list[Author]
    status: BookStatus


class BookRequest(BaseModel):
    """BookRequest."""

    id: int
    user_id: int
