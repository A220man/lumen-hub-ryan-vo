"""Backend conftest for pytest."""

import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set required test environment variables BEFORE importing app
os.environ.setdefault("SECRET_KEY", "test-secret-key-min-32-characters-long")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("KEYCLOAK_URL", "http://localhost:8080")
os.environ.setdefault("KEYCLOAK_REALM", "lumen-hub")
os.environ.setdefault("KEYCLOAK_CLIENT_ID", "lumen-hub-backend")
os.environ.setdefault("OIDC_AUDIENCE", "lumen-hub-api")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/lumen_hub_test")

from app.main import app


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """Async test client fixture."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client