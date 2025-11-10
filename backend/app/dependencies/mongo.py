"""MongoDB connection helpers."""

from collections.abc import AsyncIterator
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

_client: Optional[AsyncIOMotorClient] = None


def get_mongo_client() -> AsyncIOMotorClient:
    """Return a singleton Motor client."""
    global _client  # noqa: PLW0603 - module-level singleton

    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongo_uri)
    return _client


async def get_database() -> AsyncIterator[AsyncIOMotorDatabase]:
    """FastAPI dependency that yields the target database."""

    client = get_mongo_client()
    settings = get_settings()
    yield client[settings.mongo_database]


async def close_client() -> None:
    """Close the underlying Mongo client."""
    global _client  # noqa: PLW0603

    if _client is not None:
        _client.close()
        _client = None


