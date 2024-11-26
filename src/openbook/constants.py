from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings function."""

    database_url: str = "sqlite:///bookclub.db"

    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_discovery_url: str = ""

    class Config:
        """Environment config."""

        env_file = ".env"


settings = Settings()
