"""
Authentication and authorization utilities for The Cognisphere API.

Provides API key-based authentication for protecting endpoints.
"""

import os
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Security scheme
security = HTTPBearer(auto_error=False)


def _get_api_key() -> Optional[str]:
    """Read the configured API key from the environment (empty == unset)."""
    return os.getenv("API_KEY") or None


def _auth_required() -> bool:
    """Read whether authentication is required from the environment."""
    return os.getenv("REQUIRE_AUTH", "false").lower() == "true"


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> bool:
    """
    Verify API key from request.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        True if authentication is successful

    Raises:
        HTTPException: If authentication fails
    """
    api_key = _get_api_key()
    require_auth = _auth_required()

    # If authentication is not required, allow access
    if not require_auth:
        return True

    # If no API key is configured, allow access (development mode)
    if not api_key:
        return True

    # If no credentials provided, deny access
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify API key
    if credentials.credentials != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


def get_auth_status() -> dict:
    """
    Get authentication status information.

    Returns:
        Dictionary with authentication configuration status
    """
    api_key = _get_api_key()
    require_auth = _auth_required()
    return {
        "authentication_required": require_auth,
        "api_key_configured": api_key is not None,
        "status": "enabled" if require_auth and api_key else "disabled",
    }
