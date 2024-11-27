from collections.abc import Generator

from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


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
