"""
Authentication and authorization utilities for The Cognisphere API.

Provides API key-based authentication for protecting endpoints.
"""

import os
from typing import Optional
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security scheme
security = HTTPBearer(auto_error=False)

# Get API key from environment
API_KEY = os.getenv("API_KEY", None)
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "false").lower() == "true"


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
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
    # If authentication is not required, allow access
    if not REQUIRE_AUTH:
        return True
    
    # If no API key is configured, allow access (development mode)
    if not API_KEY:
        return True
    
    # If no credentials provided, deny access
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify API key
    if credentials.credentials != API_KEY:
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
    return {
        "authentication_required": REQUIRE_AUTH,
        "api_key_configured": API_KEY is not None,
        "status": "enabled" if REQUIRE_AUTH and API_KEY else "disabled"
    }

