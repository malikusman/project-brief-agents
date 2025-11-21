"""Checkpointing utilities for LangGraph workflows."""

import logging
from contextlib import AbstractContextManager
from typing import Optional

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mongodb import MongoDBSaver

from pymongo.errors import PyMongoError

from project_agents.config.settings import get_settings

logger = logging.getLogger(__name__)

CheckpointType = Optional[MongoDBSaver | InMemorySaver]

_saver: CheckpointType = None
_mongo_context = None  # Track the context manager for proper cleanup


def get_checkpointer() -> MongoDBSaver | InMemorySaver:
    """Return singleton MongoDBSaver instance."""
    global _saver, _mongo_context  # noqa: PLW0603 - module-level cache

    if _saver is None:
        settings = get_settings()
        logger.info(
            f"Initializing checkpointer with MongoDB URI: {settings.mongo_uri} "
            f"(database: {settings.mongo_database}, collection: {settings.mongo_collection})"
        )
        try:
            # from_conn_string returns a context manager, we need to enter it to get the saver
            _mongo_context = MongoDBSaver.from_conn_string(
                conn_string=settings.mongo_uri,
                db_name=settings.mongo_database,
                checkpoint_collection_name=settings.mongo_collection,
            )
            logger.info("MongoDBSaver context manager created, entering context...")
            _mongo_saver = _mongo_context.__enter__()
            logger.info("MongoDBSaver initialized successfully")
            _saver = _mongo_saver
            logger.info("Using MongoDBSaver for checkpoint persistence")
        except PyMongoError as e:
            logger.warning(
                f"Failed to create MongoDBSaver due to MongoDB error: {e}. "
                "Falling back to InMemorySaver (checkpoints will not persist)."
            )
            _saver = InMemorySaver()
            logger.warning("Using InMemorySaver - checkpoints will be lost on restart")
        except Exception as e:  # noqa: BLE001 - fallback to in-memory
            logger.warning(
                f"Failed to create MongoDBSaver due to unexpected error: {e}. "
                "Falling back to InMemorySaver (checkpoints will not persist)."
            )
            _saver = InMemorySaver()
            logger.warning("Using InMemorySaver - checkpoints will be lost on restart")
    else:
        checkpointer_type = "MongoDBSaver" if isinstance(_saver, MongoDBSaver) else "InMemorySaver"
        logger.debug(f"Returning existing checkpointer: {checkpointer_type}")
    return _saver


def close_checkpointer() -> None:
    """Close the underlying MongoDB saver."""
    global _saver, _mongo_context  # noqa: PLW0603

    if _saver is not None:
        if isinstance(_saver, MongoDBSaver) and _mongo_context is not None:
            # Properly exit the context manager
            try:
                _mongo_context.__exit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing MongoDB context: {e}")
        else:
            # For InMemorySaver, just call close if it exists
            close = getattr(_saver, "close", None)
            if callable(close):
                close()
        _saver = None
        _mongo_context = None


class ManagedCheckpointer(AbstractContextManager[MongoDBSaver | InMemorySaver]):
    """Context manager wrapper to ensure closings in scripts/tests."""

    def __enter__(self) -> MongoDBSaver | InMemorySaver:
        return get_checkpointer()

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        close_checkpointer()


