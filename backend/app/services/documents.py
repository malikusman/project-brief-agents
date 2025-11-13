"""Document storage and parsing utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from app.core.config import get_settings
from app.models import DocumentModel


async def save_and_parse_upload(upload: UploadFile) -> DocumentModel:
    settings = get_settings()
    uploads_dir = Path(settings.uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid4())
    sanitized_name = upload.filename or f"document-{file_id}"
    target_path = uploads_dir / f"{file_id}-{sanitized_name}"

    content = await upload.read()
    target_path.write_bytes(content)

    text = _extract_text(target_path)

    return DocumentModel(
        id=file_id,
        name=sanitized_name,
        text=text,
    )


def _extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    try:
        if suffix in {'.txt', '.md'}:
            loader = TextLoader(str(path), autodetect_encoding=True)
            return _join_documents(loader.load())
        if suffix in {'.pdf'}:
            loader = PyPDFLoader(str(path))
            return _join_documents(loader.load())
        return path.read_text(encoding='utf-8', errors='ignore')
    except Exception:  # noqa: BLE001
        return path.read_text(encoding='utf-8', errors='ignore')


def _join_documents(documents: Iterable) -> str:
    parts = []
    for doc in documents:
        content = getattr(doc, 'page_content', '')
        if content:
            parts.append(content.strip())
    return "\n\n".join(parts)
