from collections.abc import Generator

from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry


class Settings(BaseSettings):
    """Settings function."""

    DATABASE_URL: str = "sqlite:///mydb.db"

    class Config:
        """Environment config."""

        env_file = ".env"


settings = Settings()

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency Function."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection: DBAPIConnection, _connection_record: ConnectionPoolEntry) -> None:
    """Event to turn on WAL mode for every connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.close()
