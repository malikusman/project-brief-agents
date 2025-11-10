"""Checkpointing utilities for LangGraph workflows."""

from contextlib import AbstractContextManager
from typing import Optional

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mongodb import MongoDBSaver

from pymongo.errors import PyMongoError

from project_agents.config.settings import get_settings

CheckpointType = Optional[MongoDBSaver | InMemorySaver]

_saver: CheckpointType = None


def get_checkpointer() -> MongoDBSaver | InMemorySaver:
    """Return singleton MongoDBSaver instance."""
    global _saver  # noqa: PLW0603 - module-level cache

    if _saver is None:
        settings = get_settings()
        try:
            _mongo_saver = MongoDBSaver.from_conn_string(
                connection_string=settings.mongo_uri,
                database_name=settings.mongo_database,
                collection_name=settings.mongo_collection,
            )
            _mongo_saver.setup()
            _saver = _mongo_saver
        except (PyMongoError, Exception):  # noqa: BLE001 - fallback to in-memory
            _saver = InMemorySaver()
    return _saver


def close_checkpointer() -> None:
    """Close the underlying MongoDB saver."""
    global _saver  # noqa: PLW0603

    if _saver is not None:
        close = getattr(_saver, "close", None)
        if callable(close):
            close()
        _saver = None


class ManagedCheckpointer(AbstractContextManager[MongoDBSaver | InMemorySaver]):
    """Context manager wrapper to ensure closings in scripts/tests."""

    def __enter__(self) -> MongoDBSaver | InMemorySaver:
        return get_checkpointer()

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        close_checkpointer()


