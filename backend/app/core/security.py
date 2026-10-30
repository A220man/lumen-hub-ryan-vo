"""Security utilities for JWT token handling."""

import time
from typing import Any, Dict, Optional

import httpx
from jose import jwt
from jose.exceptions import JWTError
from pydantic import BaseModel

from app.core.config import get_settings


class JWKS(BaseModel):
    """JSON Web Key Set."""
    keys: list[Dict[str, Any]]


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    preferred_username: Optional[str] = None
    realm_access: Optional[Dict[str, list[str]]] = None
    resource_access: Optional[Dict[str, Dict[str, list[str]]]] = None
    exp: int
    iat: int
    aud: Optional[list[str] | str] = None
    iss: str


class AuthError(Exception):
    """Authentication error."""
    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class JWKSClient:
    """Client for fetching and caching JWKS from Keycloak."""

    def __init__(self) -> None:
        self._jwks: Optional[JWKS] = None
        self._fetched_at: float = 0
        self._cache_ttl: int = 3600  # 1 hour

    async def get_jwks(self) -> JWKS:
        """Get JWKS, fetching from Keycloak if needed."""
        settings = get_settings()
        now = time.time()

        if self._jwks and (now - self._fetched_at) < self._cache_ttl:
            return self._jwks

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(settings.effective_oidc_jwks_url)
            response.raise_for_status()
            self._jwks = JWKS(**response.json())
            self._fetched_at = now
            return self._jwks

    def get_signing_key(self, kid: str) -> Optional[str]:
        """Get the public key for a given key ID."""
        if not self._jwks:
            return None

        for key in self._jwks.keys:
            if key.get("kid") == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        return None


_jwks_client = JWKSClient()


async def validate_token(token: str) -> TokenPayload:
    """Validate a JWT token and return the payload."""
    settings = get_settings()

    try:
        # Get unverified header to find the key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise AuthError("Token missing key ID")

        # Get JWKS and find the signing key
        jwks = await _jwks_client.get_jwks()
        signing_key = _jwks_client.get_signing_key(kid)
        if not signing_key:
            raise AuthError("Unable to find signing key")

        # Verify and decode the token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[settings.algorithm],
            audience=settings.oidc_audience,
            issuer=settings.effective_oidc_issuer_url,
            options={"verify_exp": True},
        )

        return TokenPayload(**payload)

    except JWTError as e:
        raise AuthError(f"Invalid token: {str(e)}")
    except httpx.HTTPError as e:
        raise AuthError(f"Failed to fetch JWKS: {str(e)}", status_code=503)


def extract_roles(payload: TokenPayload) -> list[str]:
    """Extract roles from token payload."""
    roles = set()

    # Realm roles
    if payload.realm_access and "roles" in payload.realm_access:
        roles.update(payload.realm_access["roles"])

    # Client roles
    if payload.resource_access:
        for client_roles in payload.resource_access.values():
            if "roles" in client_roles:
                roles.update(client_roles["roles"])

    return list(roles)


def get_user_info(payload: TokenPayload) -> dict:
    """Extract user info from token payload."""
    return {
        "id": payload.sub,
        "email": payload.email or payload.preferred_username,
        "name": payload.name,
        "roles": extract_roles(payload),
    }
