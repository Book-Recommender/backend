from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from openbook.database import get_db
from openbook.models import orm
from openbook.models.schemas import Author, Book

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


@router.get("/books/search")
async def search_books(
    session: Annotated[Session, Depends(get_db)],
    author: str | None = None,
    title: str | None = None,
    skip: int = 0,
    limit: int = 10,
) -> list[Book]:
    """
    Search the database for books by title or author.

    Only one of title, author may be provided.

    Args:
        author: Search by book author.
        title: Search by book title.
        skip: Number of books to skip in the results.
        limit: Number of books to return. Max is 100.

    Returns:
        A list of books that match the query, sorted in descending order by
        relevance.

    Raises:
        If author and title are given, or neither author nor title are given.
    """
    limit = min(limit, 100)

    if author and title:
        raise HTTPException(status_code=400)

    if title:
        stmt = text("""\
select fts_book.id, isbn, title, status, author.id, author.name from fts_book
left join user_book on user_book.book_id = fts_book.id
left join user on user_book.user_id = user.id
join author_book on author_book.book_id = fts_book.id
join author on author_book.author_id = author.id
where fts_book = :title limit :limit offset :skip
""")
        params = dict(title=title, limit=limit, skip=skip)
    elif author:
        stmt = text("""\
select book.id, isbn, title, status, fts_author.id, fts_author.name from fts_author
join author_book on author_book.author_id = fts_author.id
join book on book.id = author_book.book_id
left join user_book on user_book.book_id = book.id
where fts_author = :author limit :limit offset :skip
""")
        params = dict(author=author, limit=limit, skip=skip)
    else:
        raise HTTPException(status_code=400)

    results = session.execute(stmt, params=params)
    return [
        Book(
            id=r[0],
            isbn=r[1],
            title=r[2],
            authors=[Author(id=r[4], name=r[5], books=[])],
            status=orm.BookStatus.UNREAD if r[3] is None else r[3],
        )
        for r in results
    ]
