from __future__ import annotations

import pytest
from aioresponses import aioresponses

from aioneverdark import FireplaceInfo, FireplaceMode, FireplaceStats, NeverdarkClient
from aioneverdark.const import (
    ENDPOINT_INFO,
    ENDPOINT_SET_LEVEL,
    ENDPOINT_STATS,
    ENDPOINT_TURN_OFF,
    ENDPOINT_TURN_ON,
)
from aioneverdark.exceptions import NeverdarkApiError, NeverdarkCommandError

HOST = "192.168.1.100"
BASE_URL = f"http://{HOST}"
INFO_URL = f"{BASE_URL}{ENDPOINT_INFO}"
STATS_URL = f"{BASE_URL}{ENDPOINT_STATS}"
TURN_ON_URL = f"{BASE_URL}{ENDPOINT_TURN_ON}"
TURN_OFF_URL = f"{BASE_URL}{ENDPOINT_TURN_OFF}"
SET_LEVEL_URL = f"{BASE_URL}{ENDPOINT_SET_LEVEL}"

INFO_RESPONSE = {
    "fw_ver": "2.0.10",
    "hw_ver": "2.0.0",
    "model": "CHALET-II (IN) 700",
    "dev_id": "8266",
    "home_wifi": "fireplace",
    "loc_ip": "192.168.1.100",
    "dev_mac": "F8:B3:B7:C0:54:20",
}

STATS_RESPONSE = {
    "roomName": "",
    "protected": False,
    "id": "CHALET-II (IN) 700  (s/n 8266)",
    "name": "firetec_CHALET-II (IN) 700  (s/n 8266)",
    "tempProgress": 99,
    "currentTemperature": 1,
    "targetTemperature": 1,
    "fuel": 63,
    "timer": 0,
    "expectedTime": 120,
    "errorCode": 0,
    "mode": FireplaceMode.Off,
}


@pytest.fixture
def mocked_api() -> aioresponses:
    with aioresponses() as m:
        yield m


async def test_get_info_returns_model(mocked_api: aioresponses) -> None:
    mocked_api.get(INFO_URL, payload=INFO_RESPONSE)

    async with NeverdarkClient(host=HOST) as client:
        info = await client.get_info()

    assert isinstance(info, FireplaceInfo)
    assert info.fw_ver == "2.0.10"
    assert info.model == "CHALET-II (IN) 700"
    assert info.dev_mac == "F8:B3:B7:C0:54:20"


async def test_get_stats_returns_model(mocked_api: aioresponses) -> None:
    mocked_api.get(STATS_URL, payload=STATS_RESPONSE)

    async with NeverdarkClient(host=HOST) as client:
        stats = await client.get_stats()

    assert isinstance(stats, FireplaceStats)
    assert stats.fuel == 63
    assert stats.mode == FireplaceMode.Off
    assert stats.current_temperature == 1


async def test_turn_on(mocked_api: aioresponses) -> None:
    mocked_api.post(TURN_ON_URL, payload={"success": True})

    async with NeverdarkClient(host=HOST) as client:
        await client.turn_on()  # should not raise


async def test_turn_on_raises_on_failure(mocked_api: aioresponses) -> None:
    mocked_api.post(TURN_ON_URL, payload={"success": False})

    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(NeverdarkCommandError):
            await client.turn_on()


async def test_turn_off(mocked_api: aioresponses) -> None:
    mocked_api.post(TURN_OFF_URL, payload={"success": True})

    async with NeverdarkClient(host=HOST) as client:
        await client.turn_off()  # should not raise


async def test_turn_off_raises_on_failure(mocked_api: aioresponses) -> None:
    mocked_api.post(TURN_OFF_URL, payload={"success": False})

    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(NeverdarkCommandError):
            await client.turn_off()


async def test_set_level(mocked_api: aioresponses) -> None:
    mocked_api.post(SET_LEVEL_URL, payload={"success": True, "newLevel": 75})

    async with NeverdarkClient(host=HOST) as client:
        confirmed = await client.set_level(75)

    assert confirmed == 75


async def test_set_level_raises_on_failure(mocked_api: aioresponses) -> None:
    mocked_api.post(SET_LEVEL_URL, payload={"success": False, "newLevel": 0})

    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(NeverdarkCommandError):
            await client.set_level(75)


async def test_set_level_raises_on_invalid_range() -> None:
    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(ValueError):
            await client.set_level(101)


async def test_raises_api_error_on_500(mocked_api: aioresponses) -> None:
    mocked_api.get(INFO_URL, status=500, body="Internal Server Error")

    async with NeverdarkClient(host=HOST) as client:
        with pytest.raises(NeverdarkApiError) as exc_info:
            await client.get_info()

    assert exc_info.value.status_code == 500


async def test_raises_runtime_error_without_context_manager() -> None:
    client = NeverdarkClient(host=HOST)
    with pytest.raises(RuntimeError, match="async with"):
        await client.get_info()
