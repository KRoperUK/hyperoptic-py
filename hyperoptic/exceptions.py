"""Custom exceptions for the Hyperoptic client."""


class HyperopticError(Exception):
    """Base exception for Hyperoptic client errors."""


class AuthenticationError(HyperopticError):
    """Raised when authentication fails."""


class APIError(HyperopticError):
    """Raised when an API request fails."""

    def __init__(self, status_code: int, message: str, url: str = "") -> None:
        self.status_code = status_code
        self.url = url
        super().__init__(f"HTTP {status_code}: {message} ({url})")
