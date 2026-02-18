"""Keycloak OIDC authentication for the Hyperoptic customer portal.

Supports two strategies:
1. Direct ``grant_type=password`` (Resource Owner Password Credentials) — the
   simplest approach, used when the Keycloak realm allows it.
2. Simulated browser PKCE Authorization-Code flow — scrapes the Keycloak login
   form, POSTs credentials, follows the redirect to obtain an auth code, then
   exchanges it for tokens.  Used as an automatic fallback.
"""

from __future__ import annotations

import hashlib
import logging
import re
import secrets
import time
from base64 import urlsafe_b64encode
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from hyperoptic.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

AUTH_BASE = "https://auth.hyperoptic.com/realms/hyperoptic/protocol/openid-connect"
TOKEN_URL = f"{AUTH_BASE}/token"
AUTH_URL = f"{AUTH_BASE}/auth"
CLIENT_ID = "customer-portal"
DEFAULT_REDIRECT_URI = "https://account.hyperoptic.com/my-plan"
DEFAULT_SCOPES = "openid email customer_id atlas-chat-audience profile"


def _generate_code_verifier(length: int = 96) -> str:
    """Generate a PKCE code verifier (RFC 7636)."""
    return secrets.token_urlsafe(length)[:128]


def _generate_code_challenge(verifier: str) -> str:
    """Derive S256 code challenge from a verifier."""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


@dataclass
class TokenSet:
    """Holds the current OIDC token set and expiry metadata."""

    access_token: str
    refresh_token: str
    id_token: str = ""
    token_type: str = "Bearer"
    expires_in: int = 300
    refresh_expires_in: int = 1800
    scope: str = ""
    # Absolute timestamp when the access token expires.
    _expires_at: float = field(default=0.0, repr=False)
    # Absolute timestamp when the refresh token expires.
    _refresh_expires_at: float = field(default=0.0, repr=False)

    def __post_init__(self) -> None:
        now = time.time()
        if self._expires_at == 0.0:
            self._expires_at = now + self.expires_in
        if self._refresh_expires_at == 0.0:
            self._refresh_expires_at = now + self.refresh_expires_in

    @property
    def access_expired(self) -> bool:
        return time.time() >= (self._expires_at - 30)  # 30s grace

    @property
    def refresh_expired(self) -> bool:
        return time.time() >= (self._refresh_expires_at - 30)


class HyperopticAuth:
    """Manages authentication against the Hyperoptic Keycloak realm.

    Parameters
    ----------
    email : str
        Hyperoptic account email address.
    password : str
        Hyperoptic account password.
    """

    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password
        self._tokens: TokenSet | None = None
        self._http = httpx.Client(
            follow_redirects=False,
            timeout=30.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
                ),
                "Accept": "*/*",
                "Origin": "https://account.hyperoptic.com",
                "Referer": "https://account.hyperoptic.com/",
            },
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def access_token(self) -> str:
        """Return a valid access token, refreshing/re-authenticating as needed."""
        if self._tokens is None:
            self.login()
        assert self._tokens is not None

        if self._tokens.access_expired:
            if self._tokens.refresh_expired:
                logger.info("Refresh token expired — performing full re-login")
                self.login()
            else:
                self._refresh()

        return self._tokens.access_token

    @property
    def authorization_header(self) -> dict[str, str]:
        """Return an ``Authorization`` header dict ready for use."""
        return {"Authorization": f"Bearer {self.access_token}"}

    def login(self) -> None:
        """Authenticate and obtain a fresh token set.

        Tries ``grant_type=password`` first.  If the Keycloak realm rejects it
        (HTTP 400 with ``unauthorized_client`` or ``invalid_grant``), falls
        back to the full PKCE browser-simulation flow.
        """
        try:
            self._login_password_grant()
            logger.info("Authenticated via password grant")
        except AuthenticationError:
            logger.info("Password grant refused — falling back to PKCE flow")
            self._login_pkce_flow()
            logger.info("Authenticated via PKCE flow")

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> HyperopticAuth:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Strategy 1: Resource Owner Password Credentials
    # ------------------------------------------------------------------

    def _login_password_grant(self) -> None:
        resp = self._http.post(
            TOKEN_URL,
            data={
                "grant_type": "password",
                "client_id": CLIENT_ID,
                "username": self.email,
                "password": self.password,
                "scope": DEFAULT_SCOPES,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if resp.status_code != 200:
            raise AuthenticationError(
                f"Password grant failed ({resp.status_code}): {resp.text}"
            )

        self._store_tokens(resp.json())

    # ------------------------------------------------------------------
    # Strategy 2: Simulated PKCE Authorization-Code flow
    # ------------------------------------------------------------------

    def _login_pkce_flow(self) -> None:
        code_verifier = _generate_code_verifier()
        code_challenge = _generate_code_challenge(code_verifier)

        # 1. GET the Keycloak login page to obtain the session + form action.
        params = {
            "client_id": CLIENT_ID,
            "redirect_uri": DEFAULT_REDIRECT_URI,
            "response_type": "code",
            "scope": DEFAULT_SCOPES,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        login_page_resp = self._http.get(AUTH_URL, params=params, follow_redirects=True)

        if login_page_resp.status_code != 200:
            raise AuthenticationError(
                f"Failed to load Keycloak login page ({login_page_resp.status_code})"
            )

        # Extract the form action URL from the HTML.
        form_action = self._extract_form_action(login_page_resp.text)
        if not form_action:
            raise AuthenticationError(
                "Could not find login form action URL in Keycloak page"
            )

        # Carry over cookies set by Keycloak.
        cookies: dict[str, str] = dict(login_page_resp.cookies)

        # 2. POST credentials to the form action.
        login_resp = self._http.post(
            form_action,
            data={"username": self.email, "password": self.password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            cookies=cookies,
            follow_redirects=False,
        )

        # Keycloak responds with a 302 redirect containing the code.
        if login_resp.status_code not in (302, 303):
            raise AuthenticationError(
                f"Expected redirect after login, got {login_resp.status_code}. "
                "Check email/password."
            )

        redirect_url = login_resp.headers.get("location", "")
        code = self._extract_code_from_redirect(redirect_url)
        if not code:
            # Sometimes there's a chain of redirects — follow them.
            code = self._follow_redirects_for_code(login_resp, cookies)

        if not code:
            raise AuthenticationError(
                f"Could not extract authorization code from redirect: {redirect_url}"
            )

        # 3. Exchange the authorization code for tokens.
        token_resp = self._http.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "code": code,
                "redirect_uri": DEFAULT_REDIRECT_URI,
                "code_verifier": code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_resp.status_code != 200:
            raise AuthenticationError(
                f"Token exchange failed ({token_resp.status_code}): {token_resp.text}"
            )

        self._store_tokens(token_resp.json())

    # ------------------------------------------------------------------
    # Token refresh
    # ------------------------------------------------------------------

    def _refresh(self) -> None:
        """Use the refresh token to get a new access token."""
        assert self._tokens is not None
        resp = self._http.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": CLIENT_ID,
                "refresh_token": self._tokens.refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if resp.status_code != 200:
            logger.warning("Token refresh failed — performing full re-login")
            self.login()
            return

        self._store_tokens(resp.json())
        logger.debug("Access token refreshed")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _store_tokens(self, data: dict) -> None:
        self._tokens = TokenSet(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            id_token=data.get("id_token", ""),
            token_type=data.get("token_type", "Bearer"),
            expires_in=data.get("expires_in", 300),
            refresh_expires_in=data.get("refresh_expires_in", 1800),
            scope=data.get("scope", ""),
        )

    @staticmethod
    def _extract_form_action(html: str) -> str | None:
        """Pull the ``action`` attribute from the Keycloak login ``<form>``."""
        # Match action="..." on the form that has id="kc-form-login" or just
        # the first form with a POST action to the Keycloak auth endpoint.
        match = re.search(
            r'<form[^>]*\baction=["\']([^"\']+)["\'][^>]*\bmethod=["\']post["\']',
            html,
            re.IGNORECASE,
        )
        if not match:
            # Try reversed order (method before action).
            match = re.search(
                r'<form[^>]*\bmethod=["\']post["\'][^>]*\baction=["\']([^"\']+)["\']',
                html,
                re.IGNORECASE,
            )
        if match:
            import html as html_module

            return html_module.unescape(match.group(1))
        return None

    @staticmethod
    def _extract_code_from_redirect(url: str) -> str | None:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        codes = qs.get("code")
        return codes[0] if codes else None

    def _follow_redirects_for_code(
        self, resp: httpx.Response, cookies: httpx.Cookies | dict
    ) -> str | None:
        """Follow redirect chain (max 5) looking for the auth code."""
        for _ in range(5):
            location = resp.headers.get("location", "")
            code = self._extract_code_from_redirect(location)
            if code:
                return code
            if not location:
                return None
            resp = self._http.get(location, cookies=cookies, follow_redirects=False)
            if resp.status_code not in (301, 302, 303, 307, 308):
                return None
        return None
