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
    title: str
    authors: list[Author]
    status: BookStatus
