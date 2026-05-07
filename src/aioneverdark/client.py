from __future__ import annotations

from types import TracebackType
from typing import Any

import aiohttp

from .const import (
    ENDPOINT_INFO,
    ENDPOINT_SET_LEVEL,
    ENDPOINT_STATS,
    ENDPOINT_TURN_OFF,
    ENDPOINT_TURN_ON,
)
from .exceptions import NeverdarkApiError, NeverdarkCommandError
from .models import FireplaceInfo, FireplaceStats


class NeverdarkClient:
    """Async client for the Neverdark Fireplace API.

    Usage::

        async with NeverdarkClient(host="192.168.1.x") as client:
            info = await client.get_info()
    """

    def __init__(self, host: str) -> None:
        self._base_url = f"http://{host}"
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> NeverdarkClient:
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_info(self) -> FireplaceInfo:
        """Return device information (firmware version, model, MAC address, etc.)."""
        data = await self._request("GET", ENDPOINT_INFO)
        return FireplaceInfo.model_validate(data)

    async def get_stats(self) -> FireplaceStats:
        """Return current fireplace stats (temperature, fuel, mode, etc.)."""
        data = await self._request("GET", ENDPOINT_STATS)
        return FireplaceStats.model_validate(data)

    async def turn_on(self) -> None:
        """Turn the fireplace on."""
        data = await self._request("POST", ENDPOINT_TURN_ON)
        if not data.get("success"):
            raise NeverdarkCommandError("turn_on command failed: device returned success=false")

    async def turn_off(self) -> None:
        """Turn the fireplace off."""
        data = await self._request("POST", ENDPOINT_TURN_OFF)
        if not data.get("success"):
            raise NeverdarkCommandError("turn_off command failed: device returned success=false")

    async def set_level(self, flame_level: int) -> int:
        """Set the flame level (0-100). Returns the confirmed level from the device."""
        if not 0 <= flame_level <= 100:
            raise ValueError(f"flame_level must be between 0 and 100, got {flame_level}")
        data = await self._request("POST", ENDPOINT_SET_LEVEL, json={"flameLevel": flame_level})
        if not data.get("success"):
            raise NeverdarkCommandError("set_level command failed: device returned success=false")
        return int(data["newLevel"])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Execute an HTTP request and return the parsed JSON body."""
        session = self._get_session()
        url = f"{self._base_url}{path}"

        async with session.request(method, url, **kwargs) as resp:
            if not resp.ok:
                raise NeverdarkApiError(resp.status, await resp.text())
            return await resp.json()

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            raise RuntimeError(
                "Client is not open. Use 'async with NeverdarkClient(...) as client'."
            )
        return self._session
