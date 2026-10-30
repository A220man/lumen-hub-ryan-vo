"""Backend authentication tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.mark.asyncio
async def test_auth_config_endpoint() -> None:
    """Test auth config endpoint returns Keycloak configuration."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/config")
    assert response.status_code == 200
    data = response.json()
    assert "keycloak_url" in data
    assert "realm" in data
    assert "client_id" in data
    assert "redirect_uri" in data


@pytest.mark.asyncio
async def test_me_endpoint_requires_auth() -> None:
    """Test /me endpoint requires authentication."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_redirect() -> None:
    """Test login redirect endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False) as client:
        response = await client.get("/api/v1/auth/login")
    assert response.status_code == 307
    assert "location" in response.headers
    assert "protocol/openid-connect/auth" in response.headers["location"]


@pytest.mark.asyncio
async def test_token_exchange_invalid_code() -> None:
    """Test token exchange with invalid code."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.json = AsyncMock(return_value={"error": "invalid_grant"})
        mock_post.return_value = mock_response

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/token", params={"code": "invalid"})
    assert response.status_code == 400
