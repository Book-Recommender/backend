from fastapi import APIRouter

from openbook.models.schemas import Book

router = APIRouter(tags=["books"])


@router.get("/books")
async def get_books() -> list[Book]:
    """Retrieve the user's book list."""
    return []


@router.post("/books")
async def add_book(id: int) -> None:
    """Add a book to the user's list of completed books."""


@router.get("/books/recommended")
async def get_recommended_books() -> list[Book]:
    """Get a list of recommended books for the user."""
    return []
