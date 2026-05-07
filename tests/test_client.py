from __future__ import annotations

import aiohttp
import pytest
from aioresponses import aioresponses
from yarl import URL

from aioneverdark import FireplaceInfo, FireplaceMode, FireplaceStats, NeverdarkClient
from aioneverdark.const import (
    ENDPOINT_INFO,
    ENDPOINT_SET_LEVEL,
    ENDPOINT_STATS,
    ENDPOINT_TURN_OFF,
    ENDPOINT_TURN_ON,
    PORT,
    SCHEME,
)
from aioneverdark.exceptions import NeverdarkApiError, NeverdarkCommandError

HOST = "192.168.1.100"


def _url(path: str) -> URL:
    return URL.build(scheme=SCHEME, host=HOST, port=PORT, path=path)


INFO_RESPONSE = {
    "fw_ver": "2.0.10",
    "hw_ver": "2.0.0",
    "model": "CHALET-II (IN) 700",
    "dev_id": "8266",
    "home_wifi": "fireplace",
    "loc_ip": HOST,
    "dev_mac": "F8:B3:B7:C0:54:20",
}

STATS_RESPONSE = {
    "roomName": "",
    "protected": False,
    "id": "CHALET-II (IN) 700  (s/n 8266)",
    "name": "firetec_CHALET-II (IN) 700  (s/n 8266)",
    "tempProgress": 99,
    "currentTemperature": 21,
    "targetTemperature": 22,
    "fuel": 63,
    "timer": 0,
    "expectedTime": 120,
    "errorCode": 0,
    "mode": 3,
}


# ---------------------------------------------------------------------------
# get_info
# ---------------------------------------------------------------------------


async def test_get_info_returns_model(mocked_api: aioresponses) -> None:
    mocked_api.get(_url(ENDPOINT_INFO), payload=INFO_RESPONSE)

    async with NeverdarkClient(host=HOST) as client:
        info = await client.get_info()

    assert isinstance(info, FireplaceInfo)
    assert info.fw_ver == "2.0.10"
    assert info.model == "CHALET-II (IN) 700"
    assert info.dev_mac == "F8:B3:B7:C0:54:20"


async def test_get_info_raises_on_error_response(mocked_api: aioresponses) -> None:
    mocked_api.get(_url(ENDPOINT_INFO), status=500, body="Internal Server Error")

    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(NeverdarkApiError):
            await client.get_info()


# ---------------------------------------------------------------------------
# get_stats
# ---------------------------------------------------------------------------


async def test_get_stats_returns_model(mocked_api: aioresponses) -> None:
    mocked_api.get(_url(ENDPOINT_STATS), payload=STATS_RESPONSE)

    async with NeverdarkClient(host=HOST) as client:
        stats = await client.get_stats()

    assert isinstance(stats, FireplaceStats)
    assert stats.fuel == 63
    assert stats.current_temperature == 21
    assert stats.target_temperature == 22
    assert stats.mode is FireplaceMode.Running


async def test_get_stats_mode_enum_values(mocked_api: aioresponses) -> None:
    for raw, expected in [
        (1, FireplaceMode.Off),
        (2, FireplaceMode.WarmingUp),
        (3, FireplaceMode.Running),
        (4, FireplaceMode.CoolingDown),
    ]:
        mocked_api.get(_url(ENDPOINT_STATS), payload={**STATS_RESPONSE, "mode": raw})
        async with NeverdarkClient(host=HOST) as client:
            stats = await client.get_stats()
        assert stats.mode is expected


# ---------------------------------------------------------------------------
# turn_on
# ---------------------------------------------------------------------------


async def test_turn_on_success(mocked_api: aioresponses) -> None:
    mocked_api.post(_url(ENDPOINT_TURN_ON), payload={"success": True})

    async with NeverdarkClient(host=HOST) as client:
        await client.turn_on()  # should not raise


async def test_turn_on_raises_on_failure(mocked_api: aioresponses) -> None:
    mocked_api.post(_url(ENDPOINT_TURN_ON), payload={"success": False})

    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(NeverdarkCommandError):
            await client.turn_on()


async def test_turn_on_raises_on_http_error(mocked_api: aioresponses) -> None:
    mocked_api.post(_url(ENDPOINT_TURN_ON), status=503, body="Service Unavailable")

    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(NeverdarkApiError):
            await client.turn_on()


# ---------------------------------------------------------------------------
# turn_off
# ---------------------------------------------------------------------------


async def test_turn_off_success(mocked_api: aioresponses) -> None:
    mocked_api.post(_url(ENDPOINT_TURN_OFF), payload={"success": True})

    async with NeverdarkClient(host=HOST) as client:
        await client.turn_off()  # should not raise


async def test_turn_off_raises_on_failure(mocked_api: aioresponses) -> None:
    mocked_api.post(_url(ENDPOINT_TURN_OFF), payload={"success": False})

    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(NeverdarkCommandError):
            await client.turn_off()


# ---------------------------------------------------------------------------
# set_level
# ---------------------------------------------------------------------------


async def test_set_level_returns_confirmed_level(mocked_api: aioresponses) -> None:
    mocked_api.post(_url(ENDPOINT_SET_LEVEL), payload={"success": True, "newLevel": 75})

    async with NeverdarkClient(host=HOST) as client:
        confirmed = await client.set_level(75)

    assert confirmed == 75


async def test_set_level_boundary_values(mocked_api: aioresponses) -> None:
    for level in (0, 100):
        mocked_api.post(_url(ENDPOINT_SET_LEVEL), payload={"success": True, "newLevel": level})
        async with NeverdarkClient(host=HOST) as client:
            assert await client.set_level(level) == level


async def test_set_level_raises_on_out_of_range() -> None:
    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(ValueError):
            await client.set_level(101)
        with pytest.raises(ValueError):
            await client.set_level(-1)


async def test_set_level_raises_on_failure(mocked_api: aioresponses) -> None:
    mocked_api.post(_url(ENDPOINT_SET_LEVEL), payload={"success": False, "newLevel": 0})

    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(NeverdarkCommandError):
            await client.set_level(50)


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------


async def test_session_created_lazily(mocked_api: aioresponses) -> None:
    mocked_api.get(_url(ENDPOINT_INFO), payload=INFO_RESPONSE)

    client = NeverdarkClient(host=HOST)
    assert client.session is None

    async with client:
        await client.get_info()
        assert client.session is not None


async def test_owned_session_closed_after_exit(mocked_api: aioresponses) -> None:
    mocked_api.get(_url(ENDPOINT_INFO), payload=INFO_RESPONSE)

    async with NeverdarkClient(host=HOST) as client:
        await client.get_info()
        session = client.session

    assert session is not None
    assert session.closed


async def test_external_session_not_closed_on_exit(mocked_api: aioresponses) -> None:
    mocked_api.get(_url(ENDPOINT_INFO), payload=INFO_RESPONSE)

    session = aiohttp.ClientSession()
    try:
        async with NeverdarkClient(host=HOST, session=session) as client:
            await client.get_info()
        assert not session.closed
    finally:
        await session.close()


async def test_close_is_idempotent(mocked_api: aioresponses) -> None:
    mocked_api.get(_url(ENDPOINT_INFO), payload=INFO_RESPONSE)

    async with NeverdarkClient(host=HOST) as client:
        await client.get_info()

    await client.close()  # second close should not raise
