from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from openbook.database import get_db
from openbook.models import orm
from openbook.models.orm import Book, BookStatus, UserBook
from openbook.models.schemas import Book as BookSchema

router = APIRouter(tags=["books"])


@router.get("/books")
async def get_books(user_id: int, db: Annotated[Session, Depends(get_db)]) -> list[BookSchema]:
    """Retrieve the user's book list."""
    user_books = db.query(UserBook).filter(UserBook.user_id == user_id).join(Book, Book.id == UserBook.book_id).all()
    return [BookSchema.model_validate(user_book.book) for user_book in user_books]


@router.get("/books/completed")
async def get_completed_books(user_id: int, db: Annotated[Session, Depends(get_db)]) -> list[BookSchema]:
    """Retrieve the user's completed list."""
    user_completed_books = (
        db.query(Book)
        .join(UserBook, UserBook.book_id == Book.id)
        .filter(UserBook.user_id == user_id, UserBook.status == BookStatus.COMPLETED)
        .all()
    )
    return [BookSchema.model_validate(user_completed_books) for user_book in user_completed_books]


@router.post("/books/completed")
async def add_completed_book(id: int, user_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    """Add a book to the user's list of completed books."""
    stmt = (
        insert(UserBook)
        .values(user_id=user_id, book_id=id, status=BookStatus.COMPLETED)
        .on_conflict_do_update(
            index_elements=[UserBook.user_id, UserBook.book_id], set_={"status": BookStatus.COMPLETED}
        )
    )
    db.execute(stmt)
    db.commit()


@router.get("/books/recommended")
async def get_recommended_books(user_id: int, db: Annotated[Session, Depends(get_db)]) -> list[BookSchema]:
    """Get a list of recommended books for the user."""
    user_recommended_books = (
        db.query(Book)
        .join(UserBook, UserBook.book_id == Book.id)
        .filter(UserBook.user_id == user_id, UserBook.status == BookStatus.COMPLETED)
        .all()
    )
    return [BookSchema.model_validate(user_recommended_books) for user_book in user_recommended_books]


router.post("/books/recommended")


async def add_recommended_book(id: int, user_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    """Add a book to the user's list of recommended books."""
    stmt = (
        insert(UserBook)
        .values(user_id=user_id, book_id=id, status=BookStatus.RECOMMENDED)
        .on_conflict_do_update(
            index_elements=[UserBook.user_id, UserBook.book_id], set_={"status": BookStatus.RECOMMENDED}
        )
    )
    db.execute(stmt)
    db.commit()


@router.get("/books/reading")
async def get_reading_books(user_id: int, db: Annotated[Session, Depends(get_db)]) -> list[BookSchema]:
    """Retrieve the user's reading list."""
    user_reading_books = (
        db.query(Book)
        .join(UserBook, UserBook.book_id == Book.id)
        .filter(UserBook.user_id == user_id, UserBook.status == BookStatus.READING)
        .all()
    )
    return [BookSchema.model_validate(user_reading_books) for user_book in user_reading_books]


@router.post("/books/reading")
async def add_reading_book(id: int, user_id: int, db: Annotated[Session, Depends(get_db)]) -> None:
    """Add a book to the user's list of reading books."""
    stmt = (
        insert(UserBook)
        .values(user_id=user_id, book_id=id, status=BookStatus.READING)
        .on_conflict_do_update(index_elements=[UserBook.user_id, UserBook.book_id], set_={"status": BookStatus.READING})
    )
    db.execute(stmt)
    db.commit()


@router.get("/books/search")
async def search_books(
    session: Annotated[Session, Depends(get_db)],
    author: str | None = None,
    title: str | None = None,
    skip: int = 0,
    limit: int = 10,
) -> list[BookSchema]:
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
select fts_book.id, isbn, title, status from fts_book
left join user_book on user_book.book_id = fts_book.id
left join user on user_book.user_id = user.id
where fts_book = :title limit :limit offset :skip
""")
        params = dict(title=title, limit=limit, skip=skip)
    elif author:
        stmt = text("""\
select book.id, isbn, title, status from fts_author
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
        BookSchema(id=r[0], isbn=r[1], title=r[2], authors=[], status=orm.BookStatus.UNREAD if r[3] is None else r[3])
        for r in results
    ]
