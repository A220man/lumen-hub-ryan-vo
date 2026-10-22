"""Health check API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

router = APIRouter()


@router.get("/health", summary="Health check endpoint")
async def health_check() -> dict:
    """Basic health check - returns service status."""
    settings = get_settings()
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/health/ready", summary="Readiness check")
async def readiness_check() -> dict:
    """Readiness check - verifies dependencies are available."""
    # TODO: Add database connectivity check
    # TODO: Add Keycloak connectivity check
    return {
        "status": "ready",
        "checks": {
            "database": "pending",
            "keycloak": "pending",
        },
    }


@router.get("/health/live", summary="Liveness check")
async def liveness_check() -> dict:
    """Liveness check - returns basic service aliveness."""
    return {"status": "alive"}