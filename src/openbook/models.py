import enum

from sqlalchemy import Enum, ForeignKey, Index, Integer, String
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

    # Relationships to Book and User with type hints
    book: Mapped["Book"] = relationship("Book", back_populates="user_book_entries")
    user: Mapped["User"] = relationship("User", back_populates="user_book_entries")

    # Association Table Columns with type hints
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    status: Mapped[BookStatus] = mapped_column(Enum(BookStatus), default=BookStatus.RECOMMENDED)


class AuthorBook(Base):
    """Represents the association between authors and books."""

    __tablename__ = "author_book"

    # Relationships to Author and Book with type hints
    author: Mapped["Author"] = relationship("Author", back_populates="books")
    book: Mapped["Book"] = relationship("Book", back_populates="authors")

    # Association Table Columns with type hints
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("authors.id"), primary_key=True)


class User(Base):
    """Represents a user in the system."""

    __tablename__ = "user"

    # Many-to-many relationship with Book through UserBook with type hints
    books: Mapped[list["UserBook"]] = relationship("UserBook", back_populates="user")

    # Table Columns with type hints
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String)


class Book(Base):
    """Represents a book in the system."""

    __tablename__ = "book"

    # Many-to-many relationship with User through UserBook with type hints
    users: Mapped[list["UserBook"]] = relationship("UserBook", back_populates="book")

    # Many-to-many relationship with Author through AuthorBook with type hints
    authors: Mapped[list["AuthorBook"]] = relationship("AuthorBook", back_populates="book")

    # Table Columns with type hints
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (Index("idx_book_title", "title"),)


class Author(Base):
    """Represents an author of books."""

    __tablename__ = "author"

    # Many-to-many relationship with Book through AuthorBook association with type hints
    books: Mapped[list["AuthorBook"]] = relationship("AuthorBook", back_populates="author")

    # Table Columns with type hints
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (Index("idx_author_name", "name"),)
