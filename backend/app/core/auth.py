"""Authentication dependencies for FastAPI."""

from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import AuthError, TokenPayload, get_user_info, validate_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> dict:
    """Get current authenticated user from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = await validate_token(credentials.credentials)
        return get_user_info(payload)
    except AuthError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)]
) -> Optional[dict]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None

    try:
        payload = await validate_token(credentials.credentials)
        return get_user_info(payload)
    except AuthError:
        return None


def require_roles(*required_roles: str):
    """Dependency factory for role-based access control."""
    async def role_checker(
        user: Annotated[dict, Depends(get_current_user)]
    ) -> dict:
        user_roles = set(user.get("roles", []))
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(required_roles)}",
            )
        return user
    return role_checker
