"""Application API routing."""

from fastapi import APIRouter

from app.api.routes import briefs, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(briefs.router, tags=["briefs"])


