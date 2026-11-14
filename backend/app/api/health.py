"""Health check API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

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


@router.get("/health/schema", summary="Schema health check")
async def schema_health_check() -> dict:
    """Schema health check - verifies PostgREST schema security.

    Detects if pg_pgrst.no_exposed_schemas function is available,
    which prevents access to exposed database schemas.
    """
    settings = get_settings()

    # Check if pg_pgrst.no_exposed_schemas function exists
    # This function is part of the PostgREST extension for schema security
    try:
        async with AsyncSession(settings.database_url) as session:
            result = await session.execute(
                text(
                    "SELECT 1 FROM pg_proc WHERE proname = 'no_exposed_schemas' AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'pg_pgrst')"
                )
            )
            function_exists = result.scalar() is not None
    except Exception:
        function_exists = False

    if function_exists:
        return {
            "status": "healthy",
            "schema_security": {
                "pg_pgrst_no_exposed_schemas": True,
                "detail": "pg_pgrst.no_exposed_schemas function is available",
            },
        }
    else:
        return {
            "status": "degraded",
            "schema_security": {
                "pg_pgrst_no_exposed_schemas": False,
                "detail": "pg_pgrst.no_exposed_schemas function is missing - schemas may be exposed",
            },
        }
