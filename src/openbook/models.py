from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Reading_list_book(Base):
    __titlename__ = 'reading_list_book'
    book_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    reading_list_id = Column(Integer, ForeignKey('reading_lists'), primary_key=True)

    status = Column(String, default='reading')

    books = relationship("Book", back_populates="reading_list_book")
    reading_lists = relationship("Reading_List", back_populates="reading_list_book")
    
class Recommended_list_book(Base):
    __titlename__ = 'recommended_list_book'
    book_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    recommended_list_id = Column(Integer, ForeignKey('recommended_lists'), primary_key=True)

    books = relationship("Book", back_populates="recommended_list_book")
    recommended_lists = relationship("Recommended_list", back_populates="recommended_list_book")  

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    password = Column(String)

    completed_list = relationship("Completed_list", back_populates= "users", uselist=False)

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)

    reading_list_book = relationship("Reading_list_book", back_populates="books")

class Reading_list(Base):
    __tablename__ = 'reading_lists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    
    user = relationship("User", back_populates="reading_lists")

    reading_list_book = relationship("Reading_list_book", back_populates="reading_lists")

class Recommended_list(Base):
    __tablename__ = 'recommended_lists'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

    user = relationship("User", back_populates="recommended_lists")