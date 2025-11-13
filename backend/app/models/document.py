"""Document metadata models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentModel(BaseModel):
    id: str = Field(..., description="Document identifier")
    name: str = Field(..., min_length=1)
    url: Optional[str] = None
    notes: Optional[str] = None
    text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentCreateResponse(BaseModel):
    document: DocumentModel

