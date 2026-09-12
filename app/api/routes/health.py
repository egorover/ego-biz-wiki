"""Health-check endpoint."""

from fastapi import APIRouter

from app.api.schemas.health import HealthResponse
from app.infrastructure.config.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return basic application health information."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )
