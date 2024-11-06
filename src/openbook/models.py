import enum

from sqlalchemy import Column, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class BookStatus(enum.Enum):
    """Enumeration for the status of a book in a user's list."""

    RECOMMENDED = "recommended"
    READING = "reading"
    COMPLETED = "completed"


class UserBookList(Base):
    """Represents the association between userslist and books."""

    __tablename__ = "user_book_lists"

    # Association Table Columns
    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    user_list_id = Column(Integer, ForeignKey("user_lists.id"), primary_key=True)
    status = Column(Enum(BookStatus), default=BookStatus.RECOMMENDED)

    # Relationships to Book and User_List
    book = relationship("Book", back_populates="user_book_list_entries")
    user_list = relationship("UserList", back_populates="user_book_list_entries")

    __table_args__ = (Index("idx_user_book", "user_list_id", "book_id"),)


class AuthorBook(Base):
    """Represents the association between authors and books."""

    __tablename__ = "author_book"

    # Table Columns
    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    author_id = Column(Integer, ForeignKey("authors.id"), primary_key=True)

    # Relationships to Author and Book
    author = relationship("Author", back_populates="books")
    book = relationship("Book", back_populates="authors")


class User(Base):
    """Represents a user in the system."""

    __tablename__ = "users"

    # Table Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    password = Column(String)

    # One-to-one relationship with User_List
    user_list = relationship("UserList", back_populates="user", uselist=False)

    __table_args__ = (Index("idx_user_email", "email"),)


class Book(Base):
    """Represents a book in the system."""

    __tablename__ = "books"

    # Table Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)

    # Many-to-many relationship with User_List through User_Book_List
    user_book_list_entries = relationship("UserBookList", back_populates="book")

    # Many-to-many relationship with Author through Author_Book
    authors = relationship("AuthorBook", back_populates="book")

    __table_args__ = (Index("idx_book_title", "title"),)


class Author(Base):
    """Represents an author of books."""

    __tablename__ = "authors"

    # Table Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # Many-to-many relationship with Book through Author_Book association
    books = relationship("AuthorBook", back_populates="author")

    __table_args__ = (Index("idx_author_name", "name"),)


class UserList(Base):
    """Represents a user's reading list."""

    __tablename__ = "user_lists"

    # Table Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationship with User
    user = relationship("User", back_populates="user_list")

    # Many-to-many relationship with Book through User_Book_List
    user_book_list_entries = relationship("UserBookList", back_populates="user_list")

    __table_args__ = (Index("idx_user_list_user_id", "user_id"),)
