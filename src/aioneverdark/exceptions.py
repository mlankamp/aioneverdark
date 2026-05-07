from __future__ import annotations


class NeverdarkError(Exception):
    """Base exception for all aioneverdark errors."""


class NeverdarkApiError(NeverdarkError):
    """Raised when the Neverdark API returns a non-2xx response."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(f"API error: {message}")


class NeverdarkCommandError(NeverdarkError):
    """Raised when the device returns {\"success\": false} for a command."""
