"""Tests for Hyperoptic authentication."""

from unittest.mock import Mock, patch

import pytest

from hyperoptic.auth import (
    HyperopticAuth,
    TokenSet,
    _generate_code_challenge,
    _generate_code_verifier,
)
from hyperoptic.exceptions import AuthenticationError


class TestCodeGeneration:
    """Test PKCE code verifier and challenge generation."""

    def test_generate_code_verifier(self):
        verifier = _generate_code_verifier()
        assert isinstance(verifier, str)
        assert len(verifier) > 0
        assert len(verifier) <= 128

    def test_generate_code_verifier_changes(self):
        """Verify that each call generates a different verifier."""
        v1 = _generate_code_verifier()
        v2 = _generate_code_verifier()
        assert v1 != v2

    def test_generate_code_challenge(self):
        """Test S256 code challenge derivation."""
        verifier = _generate_code_verifier()
        challenge = _generate_code_challenge(verifier)
        assert isinstance(challenge, str)
        assert len(challenge) > 0
        # S256 should remove padding
        assert not challenge.endswith("=")

    def test_code_challenge_deterministic(self):
        """Same verifier should produce same challenge."""
        verifier = "test_verifier_123456789"
        c1 = _generate_code_challenge(verifier)
        c2 = _generate_code_challenge(verifier)
        assert c1 == c2


class TestTokenSet:
    """Test the TokenSet data class."""

    def test_token_set_creation(self, keycloak_token_response):
        """Test basic TokenSet instantiation."""
        ts = TokenSet(
            access_token="at",
            refresh_token="rt",
            expires_in=300,
            refresh_expires_in=1800,
        )
        assert ts.access_token == "at"
        assert ts.refresh_token == "rt"
        assert ts.token_type == "Bearer"

    def test_token_set_expiry_calculation(self, token_set):
        """Test that expiry timestamps are calculated on creation."""
        assert token_set._expires_at > 0
        assert token_set._refresh_expires_at > 0
        assert (
            token_set._refresh_expires_at > token_set._expires_at
        )  # refresh should be longer

    def test_access_expired_property(self, token_set):
        """Test access_expired property."""
        assert not token_set.access_expired  # Fresh token

    def test_refresh_expired_property(self, token_set):
        """Test refresh_expired property."""
        assert not token_set.refresh_expired  # Fresh token

    def test_token_properties_with_explicit_timestamp(self):
        """Test TokenSet with explicit expiry timestamps."""
        import time

        now = time.time()
        ts = TokenSet(
            access_token="at",
            refresh_token="rt",
            _expires_at=now + 300,  # Expires in 300 seconds (well beyond 30s grace)
            _refresh_expires_at=now + 1800,
        )
        assert not ts.access_expired


class TestHyperopticAuthPasswordGrant:
    """Test password grant authentication."""

    @patch("httpx.Client")
    def test_login_password_grant_success(
        self, mock_client_class, keycloak_token_response
    ):
        """Test successful password grant login."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = keycloak_token_response
        mock_client.post.return_value = mock_response

        auth = HyperopticAuth(email="test@example.com", password="secret")
        auth.login()

        assert auth._tokens is not None
        assert auth._tokens.access_token == keycloak_token_response["access_token"]
        assert auth._tokens.refresh_token == keycloak_token_response["refresh_token"]

        # Verify the correct endpoint was called
        mock_client.post.assert_called()
        call_args = mock_client.post.call_args
        assert "token" in call_args[0][0]

    @patch("httpx.Client")
    def test_login_password_grant_failure(self, mock_client_class):
        """Test password grant failure."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = '{"error": "invalid_grant"}'
        mock_client.post.side_effect = [
            mock_response,  # Password grant fails
            mock_response,  # PKCE fallback also fails because we're not mocking HTML
        ]

        auth = HyperopticAuth(email="test@example.com", password="wrong")

        # Should raise AuthenticationError on fallback (no HTML form available)
        with pytest.raises(AuthenticationError):
            auth.login()

    @patch("httpx.Client")
    def test_access_token_property(self, mock_client_class, keycloak_token_response):
        """Test access_token property triggers login if needed."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = keycloak_token_response
        mock_client.post.return_value = mock_response

        auth = HyperopticAuth(email="test@example.com", password="secret")
        token = auth.access_token

        assert token == keycloak_token_response["access_token"]
        assert mock_client.post.called

    @patch("httpx.Client")
    def test_authorization_header(self, mock_client_class, keycloak_token_response):
        """Test authorization_header property."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = keycloak_token_response
        mock_client.post.return_value = mock_response

        auth = HyperopticAuth(email="test@example.com", password="secret")
        header = auth.authorization_header

        assert "Authorization" in header
        assert header["Authorization"].startswith("Bearer ")
        assert keycloak_token_response["access_token"] in header["Authorization"]

    @patch("httpx.Client")
    def test_context_manager(self, mock_client_class, keycloak_token_response):
        """Test using HyperopticAuth as a context manager."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = keycloak_token_response
        mock_client.post.return_value = mock_response

        with HyperopticAuth(email="test@example.com", password="secret") as auth:
            assert auth._tokens is None  # Not logged in yet
            token = auth.access_token  # Trigger login
            assert auth._tokens is not None

        # Should close when exiting context
        mock_client.close.assert_called()


class TestHyperopticAuthRefresh:
    """Test token refresh functionality."""

    @patch("httpx.Client")
    def test_refresh_token(self, mock_client_class, keycloak_token_response):
        """Test token refresh using refresh_token grant."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock initial login
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = keycloak_token_response
        mock_client.post.return_value = mock_response

        auth = HyperopticAuth(email="test@example.com", password="secret")
        auth.login()

        # Mock refresh response (new tokens)
        new_token_response = keycloak_token_response.copy()
        new_token_response["access_token"] = "new_access_token"
        mock_response.json.return_value = new_token_response
        mock_client.post.return_value = mock_response

        # Force refresh
        auth._refresh()

        assert auth._tokens.access_token == "new_access_token"
        assert mock_client.post.call_count >= 2  # Login + refresh

    @patch("httpx.Client")
    def test_auto_refresh_on_expired_access_token(
        self, mock_client_class, keycloak_token_response
    ):
        """Test that access_token property auto-refreshes when token expires."""
        import time

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # First call: initial login
        login_response = keycloak_token_response.copy()
        login_response["expires_in"] = 300  # Standard 5 min expiry

        # Second call: refresh
        refresh_response = keycloak_token_response.copy()
        refresh_response["access_token"] = "refreshed_token"

        mock_client.post.side_effect = [
            Mock(status_code=200, json=lambda: login_response),
            Mock(status_code=200, json=lambda: refresh_response),
        ]

        auth = HyperopticAuth(email="test@example.com", password="secret")

        # Get initial token
        token1 = auth.access_token
        assert token1 == login_response["access_token"]

        # Manually set expiry to the past to simulate expired token
        auth._tokens._expires_at = time.time() - 10  # Expired 10 seconds ago

        # Next access should trigger refresh
        token2 = auth.access_token
        assert token2 == "refreshed_token"
