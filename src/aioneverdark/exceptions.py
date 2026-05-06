from __future__ import annotations


class NeverdarkError(Exception):
    """Base exception for all aioneverdark errors."""


class NeverdarkApiError(NeverdarkError):
    """Raised when the Neverdark API returns a non-2xx response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"API error {status_code}: {message}")
