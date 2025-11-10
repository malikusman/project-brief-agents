"""Helpers for loading prompt templates from disk."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def load_prompt(path: Path) -> str:
    """Read a prompt file and return its content."""

    if not path.is_absolute():
        resolved = BASE_DIR / path
    else:
        resolved = path
    return resolved.read_text(encoding="utf-8").strip()


