import enum

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):
    """Base class for all models, using MappedAsDataclass and DeclarativeBase in SQLAlchemy 2.0."""


class BookStatus(enum.Enum):
    """Enumeration for the status of a book in a user's list."""

    RECOMMENDED = "recommended"
    READING = "reading"
    COMPLETED = "completed"


class UserBook(Base):
    """Represents the association between users and books."""

    __tablename__ = "user_book"

    book: Mapped["Book"] = relationship("Book", back_populates="user", init=False)
    user: Mapped["User"] = relationship("User", back_populates="book", init=False)

    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    status: Mapped[BookStatus] = mapped_column(default=BookStatus.RECOMMENDED)


class AuthorBook(Base):
    """Represents the association between authors and books."""

    __tablename__ = "author_book"

    author: Mapped["Author"] = relationship("Author", back_populates="book", init=False)
    book: Mapped["Book"] = relationship("Book", back_populates="author", init=False)

    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"), primary_key=True)


class User(Base):
    """Represents a user in the system."""

    __tablename__ = "user"

    book: Mapped[list["UserBook"]] = relationship("UserBook", back_populates="user", init=False)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column()


class Book(Base):
    """Represents a book in the system."""

    __tablename__ = "book"

    user: Mapped[list["UserBook"]] = relationship("UserBook", back_populates="book", init=False)

    author: Mapped[list["AuthorBook"]] = relationship("AuthorBook", back_populates="book", init=False)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    title: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (Index("idx_book_title", "title"),)


class Author(Base):
    """Represents an author of books."""

    __tablename__ = "author"

    book: Mapped[list["AuthorBook"]] = relationship("AuthorBook", back_populates="author", init=False)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (Index("idx_author_name", "name"),)
