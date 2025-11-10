"""Health and readiness endpoints."""

from fastapi import APIRouter, status

from app.core.config import get_settings

router = APIRouter()


@router.get(
    "/live",
    summary="Liveness probe",
    status_code=status.HTTP_200_OK,
)
async def live() -> dict[str, str]:
    """Return basic application metadata."""

    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@router.get(
    "/ready",
    summary="Readiness probe",
    status_code=status.HTTP_200_OK,
)
async def ready() -> dict[str, str]:
    """Readiness check placeholder."""

    return {"status": "ready"}


