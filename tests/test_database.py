import pytest
from fastapi.testclient import TestClient
from openbook.auth import verify_user
from openbook.database import get_db
from openbook.models.orm import Author, AuthorBook, Base, Book, BookStatus, User, UserBook
from openbook.server import app  # Assuming this is where the FastAPI app is created
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite database URL for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the database dependency for FastAPI
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_user_override() -> User:
    return User(id="", email="testuser@example.com", name="Test User")


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_user] = verify_user_override


client = TestClient(app)


# Pytest fixture to handle setup and teardown
@pytest.fixture(scope="function")
def setup_database():
    # Create tables before running tests
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after running tests
    Base.metadata.drop_all(bind=engine)


def test_get_books(setup_database):
    """
    Test the GET /books route to ensure it retrieves all books for a given user.
    """
    # Create a test user in the database
    db = TestingSessionLocal()
    user = User(id="", email="testuser@example.com", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create an author in the database
    author = Author(name="Test Author")
    db.add(author)
    db.commit()
    db.refresh(author)

    # Create several test book entries in the database
    books = [
        Book(title="Test Book 1", isbn="1234567890"),
        Book(title="Test Book 2", isbn="0987654321"),
        Book(title="Test Book 3", isbn="1122334455"),
    ]

    # Add the books to the database
    db.add_all(books)
    db.commit()

    # Associate each book with the user (without worrying about the status)
    user_books = [UserBook(user_id=user.id, book_id=book.id) for book in books]

    # Add the associations to the database
    db.add_all(user_books)
    db.commit()

    # Now create the AuthorBook entries to link books with authors
    author_books = [AuthorBook(book_id=book.id, author_id=author.id) for book in books]

    # Add the AuthorBook associations to the database
    db.add_all(author_books)
    db.commit()

    # Make the GET request to retrieve all books for the user
    response = client.get(f"/books?user_id={user.id}&skip=0&limit=100")

    # Assert the response
    assert response.status_code == 200
    assert len(response.json()) == 3  # We added 3 books for the user

    # The expected response should include books with authors and their status
    expected_books = [
        {
            "id": book.id,
            "isbn": book.isbn,
            "title": book.title,
            "authors": [
                {"id": author.author_id, "name": author.author.name, "books": []}
                for author in author_books
                if author.book_id == book.id
            ],
            "status": user_books[i].status.name.lower(),  # Assuming status from user_book table
        }
        for i, book in enumerate(books)
    ]

    assert response.json() == expected_books


def test_get_completed_books(setup_database):
    """
    Test the GET /books/completed route to ensure it retrieves all books for a given user.
    """
    # Create a test user in the database
    db = TestingSessionLocal()
    user = User(id="", email="testuser@example.com", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create an author in the database
    author = Author(name="Test Author")
    db.add(author)
    db.commit()
    db.refresh(author)

    # Create several test book entries in the database
    books = [
        Book(title="Test Book 1", isbn="1234567890"),
        Book(title="Test Book 2", isbn="0987654321"),
        Book(title="Test Book 3", isbn="1122334455"),
    ]

    # Add the books to the database
    db.add_all(books)
    db.commit()

    # Associate each book with the user (without worrying about the status)
    user_books = [
        UserBook(
            user_id=user.id,
            book_id=book.id,
            status=BookStatus("completed") if i == 0 or i == 2 else BookStatus("recommended"),
        )
        for i, book in enumerate(books)
    ]

    # Add the associations to the database
    db.add_all(user_books)
    db.commit()

    # Now create the AuthorBook entries to link books with authors
    author_books = [AuthorBook(book_id=book.id, author_id=author.id) for book in books]

    # Add the AuthorBook associations to the database
    db.add_all(author_books)
    db.commit()

    # Make the GET request to retrieve completed books for the user
    response = client.get(f"/books/completed?user_id={user.id}")

    assert response.status_code == 200
    assert len(response.json()) == 2

    expected_books = [
        {
            "id": book.id,
            "isbn": book.isbn,
            "title": book.title,
            "authors": [
                {"id": author.author_id, "name": author.author.name, "books": []}
                for author in author_books
                if author.book_id == book.id
            ],
            "status": user_books[i].status.name.lower(),
        }
        for i, book in enumerate(books)
        if i != 1
    ]

    assert response.json() == expected_books


def test_add_completed_book(setup_database):
    db = TestingSessionLocal()
    user = User(id="", email="testuser@example.com", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)

    book = Book(title="Test Book 1", isbn="1234567890")
    db.add(book)
    db.commit()
    db.refresh(book)

    response = client.post("/books/completed", json={"id": book.id, "user_id": user.id})
    assert response.status_code == 200

    user_book = db.query(UserBook).filter_by(user_id=user.id, book_id=book.id).first()
    assert user_book is not None
    assert user_book.status == BookStatus.COMPLETED

    response = client.post("/books/completed", json={"id": book.id, "user_id": user.id})
    assert response.status_code == 200

    user_book = db.query(UserBook).filter_by(user_id=user.id, book_id=book.id).first()
    assert user_book is not None
    assert user_book.status == BookStatus.COMPLETED


def test_get_recommended_books(setup_database):
    """
    Test the GET /books/recommended route to ensure it retrieves all books for a given user.
    """
    # Create a test user in the database
    db = TestingSessionLocal()
    user = User(id="", email="testuser@example.com", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create an author in the database
    author = Author(name="Test Author")
    db.add(author)
    db.commit()
    db.refresh(author)

    # Create several test book entries in the database
    books = [
        Book(title="Test Book 1", isbn="1234567890"),
        Book(title="Test Book 2", isbn="0987654321"),
        Book(title="Test Book 3", isbn="1122334455"),
    ]

    # Add the books to the database
    db.add_all(books)
    db.commit()

    # Associate each book with the user (without worrying about the status)
    user_books = [
        UserBook(
            user_id=user.id,
            book_id=book.id,
            status=BookStatus("recommended") if i == 0 or i == 2 else BookStatus("completed"),
        )
        for i, book in enumerate(books)
    ]

    # Add the associations to the database
    db.add_all(user_books)
    db.commit()

    # Now create the AuthorBook entries to link books with authors
    author_books = [AuthorBook(book_id=book.id, author_id=author.id) for book in books]

    # Add the AuthorBook associations to the database
    db.add_all(author_books)
    db.commit()

    # Make the GET request to retrieve completed books for the user
    response = client.get(f"/books/recommended?user_id={user.id}")

    assert response.status_code == 200
    assert len(response.json()) == 2

    expected_books = [
        {
            "id": book.id,
            "isbn": book.isbn,
            "title": book.title,
            "authors": [
                {"id": author.author_id, "name": author.author.name, "books": []}
                for author in author_books
                if author.book_id == book.id
            ],
            "status": user_books[i].status.name.lower(),
        }
        for i, book in enumerate(books)
        if i != 1
    ]

    assert response.json() == expected_books


def test_get_reading_books(setup_database):
    """
    Test the GET /books/recommended route to ensure it retrieves all books for a given user.
    """
    # Create a test user in the database
    db = TestingSessionLocal()
    user = User(id="", email="testuser@example.com", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create an author in the database
    author = Author(name="Test Author")
    db.add(author)
    db.commit()
    db.refresh(author)

    # Create several test book entries in the database
    books = [
        Book(title="Test Book 1", isbn="1234567890"),
        Book(title="Test Book 2", isbn="0987654321"),
        Book(title="Test Book 3", isbn="1122334455"),
    ]

    # Add the books to the database
    db.add_all(books)
    db.commit()

    # Associate each book with the user (without worrying about the status)
    user_books = [
        UserBook(
            user_id=user.id,
            book_id=book.id,
            status=BookStatus("reading") if i == 0 or i == 2 else BookStatus("recommended"),
        )
        for i, book in enumerate(books)
    ]

    # Add the associations to the database
    db.add_all(user_books)
    db.commit()

    # Now create the AuthorBook entries to link books with authors
    author_books = [AuthorBook(book_id=book.id, author_id=author.id) for book in books]

    # Add the AuthorBook associations to the database
    db.add_all(author_books)
    db.commit()

    # Make the GET request to retrieve completed books for the user
    response = client.get(f"/books/reading?user_id={user.id}")

    assert response.status_code == 200
    assert len(response.json()) == 2

    expected_books = [
        {
            "id": book.id,
            "isbn": book.isbn,
            "title": book.title,
            "authors": [
                {"id": author.author_id, "name": author.author.name, "books": []}
                for author in author_books
                if author.book_id == book.id
            ],
            "status": user_books[i].status.name.lower(),
        }
        for i, book in enumerate(books)
        if i != 1
    ]

    assert response.json() == expected_books


def test_add_reading_book(setup_database):
    db = TestingSessionLocal()
    user = User(id="", email="testuser@example.com", name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)

    book = Book(title="Test Book 1", isbn="1234567890")
    db.add(book)
    db.commit()
    db.refresh(book)

    response = client.post("/books/reading", json={"id": book.id, "user_id": user.id})
    assert response.status_code == 200

    user_book = db.query(UserBook).filter_by(user_id=user.id, book_id=book.id).first()
    assert user_book is not None
    assert user_book.status == BookStatus.READING

    response = client.post("/books/reading", json={"id": book.id, "user_id": user.id})
    assert response.status_code == 200

    user_book = db.query(UserBook).filter_by(user_id=user.id, book_id=book.id).first()
    assert user_book is not None
    assert user_book.status == BookStatus.READING
