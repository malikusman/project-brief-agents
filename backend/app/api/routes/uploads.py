"""File upload endpoints."""

from fastapi import APIRouter, Depends, UploadFile

from app.dependencies.mongo import get_database
from app.models import DocumentCreateResponse, DocumentModel
from app.services.documents import save_and_parse_upload

router = APIRouter()


@router.post("/uploads", response_model=DocumentCreateResponse)
async def upload_document(
    file: UploadFile,
    database=Depends(get_database),
) -> DocumentCreateResponse:
    document = await save_and_parse_upload(file)
    record = document.model_dump()
    await database["documents"].insert_one(record)
    return DocumentCreateResponse(document=document)
