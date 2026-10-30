"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    """User info response model."""
    id: str
    email: str
    name: str | None = None
    roles: list[str]


@router.get("/login")
async def login_redirect() -> RedirectResponse:
    """Redirect to Keycloak login page."""
    settings = get_settings()
    login_url = (
        f"{settings.effective_oidc_issuer_url}/protocol/openid-connect/auth"
        f"?client_id={settings.keycloak_client_id}"
        f"&redirect_uri={settings.cors_origins[0]}/callback"
        f"&response_type=code"
        f"&scope=openid profile email"
    )
    return RedirectResponse(url=login_url)


@router.post("/token", response_model=TokenResponse)
async def exchange_code_for_token(code: str) -> TokenResponse:
    """Exchange authorization code for access token."""
    settings = get_settings()

    import httpx

    token_url = f"{settings.effective_oidc_issuer_url}/protocol/openid-connect/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{settings.cors_origins[0]}/callback",
        "client_id": settings.keycloak_client_id,
    }

    if settings.keycloak_client_secret:
        data["client_secret"] = settings.keycloak_client_secret

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token",
            )
        token_data = response.json()

    return TokenResponse(
        access_token=token_data["access_token"],
        token_type=token_data.get("token_type", "bearer"),
        expires_in=token_data.get("expires_in", 300),
    )


@router.post("/logout")
async def logout() -> dict:
    """Logout endpoint - client should clear token."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserInfo)
async def get_me(user: dict = Depends(get_current_user)) -> UserInfo:
    """Get current user info."""
    return UserInfo(**user)


@router.get("/config")
async def get_auth_config() -> dict:
    """Get Keycloak configuration for frontend."""
    settings = get_settings()
    return {
        "keycloak_url": settings.keycloak_url,
        "realm": settings.keycloak_realm,
        "client_id": settings.keycloak_client_id,
        "redirect_uri": f"{settings.cors_origins[0]}/callback",
    }
