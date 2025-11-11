"""Application configuration and settings management."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base configuration pulled from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Project Brief Backend"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    mongo_uri: str = Field(
        default="mongodb://localhost:27017/project_brief", alias="MONGODB_URI"
    )
    mongo_database: str = Field(default="project_brief", alias="MONGODB_DATABASE")

    uploads_dir: Path = Field(
        default=Path("/var/project-brief/uploads"), alias="UPLOADS_DIR"
    )
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["*"], alias="BACKEND_CORS_ALLOWED_ORIGINS"
    )

    agents_base_url: str = Field(
        default="http://agents:8080", alias="AGENTS_BASE_URL"
    )
    agents_timeout_seconds: int = Field(
        default=60, alias="AGENTS_TIMEOUT_SECONDS"
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


