from __future__ import annotations

import pytest
from aioresponses import aioresponses

from aioneverdark import NeverdarkClient, FireplaceInfo
from aioneverdark.const import ENDPOINT_INFO
from aioneverdark.exceptions import NeverdarkApiError

HOST = "192.168.1.100"
BASE_URL = f"http://{HOST}"
INFO_URL = f"{BASE_URL}{ENDPOINT_INFO}"

INFO_RESPONSE = {
    "fw_ver": "2.0.10",
    "hw_ver": "2.0.0",
    "model": "CHALET-II (IN) 700",
    "dev_id": "8266",
    "home_wifi": "fireplace",
    "loc_ip": "192.168.1.100",
    "dev_mac": "F8:B3:B7:C0:54:20",
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
