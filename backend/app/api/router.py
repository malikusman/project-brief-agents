"""Application API routing."""

from fastapi import APIRouter

from app.api.routes import briefs, health, uploads

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(briefs.router, tags=["briefs"])
api_router.include_router(uploads.router, tags=["uploads"])


