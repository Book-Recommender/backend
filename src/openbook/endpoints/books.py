from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from openbook.database import get_db
from openbook.models import orm
from openbook.models.orm import AuthorBook, Book, BookStatus, UserBook
from openbook.models.schemas import Author as AuthorSchema, Book as BookSchema, BookRequest

router = APIRouter(tags=["books"])


@router.get("/books")
async def get_books(user_id: int, db: Annotated[Session, Depends(get_db)]) -> list[BookSchema]:
    """Retrieve the user's book list."""
    user_books = (
        db.query(Book)
        .join(UserBook, Book.id == UserBook.book_id)
        .join(AuthorBook, AuthorBook.book_id == Book.id)
        .filter(UserBook.user_id == user_id)
        .all()
    )
    return [
        BookSchema(
            id=book.id,
            isbn=book.isbn,
            title=book.title,
            authors=[AuthorSchema(id=author.author_id, name=author.author.name, books=[]) for author in book.author],
            status=book.user[0].status,
        )
        for book in user_books
    ]


@router.get("/books/completed")
async def get_completed_books(user_id: int, db: Annotated[Session, Depends(get_db)]) -> list[BookSchema]:
    """Retrieve the user's completed book list."""
    user_books = (
        db.query(Book)
        .join(UserBook, Book.id == UserBook.book_id)
        .join(AuthorBook, AuthorBook.book_id == Book.id)
        .filter(UserBook.user_id == user_id, UserBook.status == BookStatus.COMPLETED)
    )

    return [
        BookSchema(
            id=book.id,
            isbn=book.isbn,
            title=book.title,
            authors=[AuthorSchema(id=author.author_id, name=author.author.name, books=[]) for author in book.author],
            status=book.user[0].status,
        )
        for book in user_books
    ]


@router.post("/books/completed")
async def add_completed_book(book_request: BookRequest, db: Annotated[Session, Depends(get_db)]) -> None:
    """Add a book to the user's list of completed books."""
    stmt = (
        insert(UserBook)
        .values(user_id=book_request.user_id, book_id=book_request.id, status=BookStatus.COMPLETED)
        .on_conflict_do_update(
            index_elements=[UserBook.user_id, UserBook.book_id], set_={"status": BookStatus.COMPLETED}
        )
    )
    db.execute(stmt)
    db.commit()


@router.get("/books/recommended")
async def get_recommended_book(user_id: int, db: Annotated[Session, Depends(get_db)]) -> list[BookSchema]:
    """Retrieve the user's completed book list."""
    user_books = (
        db.query(Book)
        .join(UserBook, Book.id == UserBook.book_id)
        .join(AuthorBook, AuthorBook.book_id == Book.id)
        .filter(UserBook.user_id == user_id, UserBook.status == BookStatus.RECOMMENDED)
    )

    return [
        BookSchema(
            id=book.id,
            isbn=book.isbn,
            title=book.title,
            authors=[AuthorSchema(id=author.author_id, name=author.author.name, books=[]) for author in book.author],
            status=book.user[0].status,
        )
        for book in user_books
    ]


@router.post("/books/recommended")
async def add_recommended_book(book_request: BookRequest, db: Annotated[Session, Depends(get_db)]) -> None:
    """Add a book to the user's list of completed books."""
    stmt = (
        insert(UserBook)
        .values(user_id=book_request.user_id, book_id=book_request.id, status=BookStatus.RECOMMENDED)
        .on_conflict_do_update(
            index_elements=[UserBook.user_id, UserBook.book_id], set_={"status": BookStatus.RECOMMENDED}
        )
    )
    db.execute(stmt)
    db.commit()


@router.get("/books/reading")
async def get_reading_book(user_id: int, db: Annotated[Session, Depends(get_db)]) -> list[BookSchema]:
    """Retrieve the user's reading book list."""
    user_books = (
        db.query(Book)
        .join(UserBook, Book.id == UserBook.book_id)
        .join(AuthorBook, AuthorBook.book_id == Book.id)
        .filter(UserBook.user_id == user_id, UserBook.status == BookStatus.READING)
    )

    return [
        BookSchema(
            id=book.id,
            isbn=book.isbn,
            title=book.title,
            authors=[AuthorSchema(id=author.author_id, name=author.author.name, books=[]) for author in book.author],
            status=book.user[0].status,
        )
        for book in user_books
    ]


@router.post("/books/reading")
async def add_reading_book(book_request: BookRequest, db: Annotated[Session, Depends(get_db)]) -> None:
    """Add a book to the user's list of reading books."""
    stmt = (
        insert(UserBook)
        .values(user_id=book_request.user_id, book_id=book_request.id, status=BookStatus.READING)
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
        BookSchema(
            id=r[0],
            isbn=r[1],
            title=r[2],
            authors=[AuthorSchema(id=r[4], name=r[5], books=[])],
            status=orm.BookStatus.UNREAD if r[3] is None else r[3],
        )
        for r in results
    ]
