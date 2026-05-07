from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Any

from aiohttp.client import ClientError, ClientSession
from yarl import URL

from .const import (
    ENDPOINT_INFO,
    ENDPOINT_SET_LEVEL,
    ENDPOINT_STATS,
    ENDPOINT_TURN_OFF,
    ENDPOINT_TURN_ON,
    PORT,
    SCHEME,
)
from .exceptions import NeverdarkApiError, NeverdarkCommandError
from .models import FireplaceInfo, FireplaceStats


class NeverdarkClient:
    """Async client for the Neverdark Fireplace API.

    Usage::

        async with NeverdarkClient(host="192.168.1.x") as client:
            info = await client.get_info()

    An existing ``aiohttp.ClientSession`` can be supplied; in that case the
    caller is responsible for closing it::

        async with aiohttp.ClientSession() as session:
            async with NeverdarkClient(host="192.168.1.x", session=session) as client:
                info = await client.get_info()
    """

    def __init__(self, host: str, session: ClientSession | None = None) -> None:
        self.request_timeout: int = 10
        self.host = host
        self.session: ClientSession | None = session
        self._close_session: bool = False

    async def __aenter__(self)-> NeverdarkClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

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

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        url = URL.build(
            scheme=SCHEME,
            host=self.host,
            port=PORT,
            path=path
        )

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(method, url, **kwargs)
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occured while connecting to Neverdark device"
            raise NeverdarkApiError(msg) from exception
        except (
            ClientError
        ) as exception:
            msg = "Error occured while communicating with Neverdark devices"
            raise NeverdarkApiError(msg) from exception

        return await response.json()

