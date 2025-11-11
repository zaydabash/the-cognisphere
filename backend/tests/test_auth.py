"""
Tests for authentication and authorization.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, status

from auth import verify_api_key, get_auth_status


class TestAuthentication:
    """Test authentication functionality."""
    
    def test_auth_status_disabled(self):
        """Test auth status when authentication is disabled."""
        with patch.dict(os.environ, {"REQUIRE_AUTH": "false", "API_KEY": ""}):
            status = get_auth_status()
            assert status["authentication_required"] is False
            assert status["status"] == "disabled"
    
    def test_auth_status_enabled(self):
        """Test auth status when authentication is enabled."""
        with patch.dict(os.environ, {"REQUIRE_AUTH": "true", "API_KEY": "test-key"}):
            status = get_auth_status()
            assert status["authentication_required"] is True
            assert status["api_key_configured"] is True
            assert status["status"] == "enabled"
    
    @pytest.mark.asyncio
    async def test_verify_api_key_no_auth_required(self):
        """Test API key verification when auth is not required."""
        with patch.dict(os.environ, {"REQUIRE_AUTH": "false"}):
            result = await verify_api_key(None)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_api_key_no_key_configured(self):
        """Test API key verification when no key is configured."""
        with patch.dict(os.environ, {"REQUIRE_AUTH": "true", "API_KEY": ""}):
            result = await verify_api_key(None)
            assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_api_key_missing_credentials(self):
        """Test API key verification with missing credentials."""
        with patch.dict(os.environ, {"REQUIRE_AUTH": "true", "API_KEY": "test-key"}):
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key(None)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Missing authentication credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_verify_api_key_invalid_key(self):
        """Test API key verification with invalid key."""
        with patch.dict(os.environ, {"REQUIRE_AUTH": "true", "API_KEY": "test-key"}):
            credentials = MagicMock()
            credentials.credentials = "wrong-key"
            
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key(credentials)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid API key" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_verify_api_key_valid_key(self):
        """Test API key verification with valid key."""
        with patch.dict(os.environ, {"REQUIRE_AUTH": "true", "API_KEY": "test-key"}):
            credentials = MagicMock()
            credentials.credentials = "test-key"
            
            result = await verify_api_key(credentials)
            assert result is True

