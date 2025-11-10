"""Configuration utilities for the agents service."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Shared configuration values for LangGraph orchestration."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="development", alias="ENVIRONMENT")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    mongo_uri: str = Field(
        default="mongodb://localhost:27017/project_brief", alias="MONGODB_URI"
    )
    mongo_database: str = Field(default="project_brief", alias="MONGODB_DATABASE")
    mongo_collection: str = Field(default="agent_state", alias="MONGODB_COLLECTION")

    uploads_dir: Path = Field(
        default=Path("/var/project-brief/uploads"), alias="UPLOADS_DIR"
    )

    intake_system_prompt_path: Path = Field(
        default=Path("intake_system.md"),
        alias="INTAKE_SYSTEM_PROMPT_PATH",
    )
    brief_system_prompt_path: Path = Field(
        default=Path("brief_system.md"),
        alias="BRIEF_SYSTEM_PROMPT_PATH",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


