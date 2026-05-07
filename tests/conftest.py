from __future__ import annotations

import pytest
from aioresponses import aioresponses


@pytest.fixture
def mocked_api() -> aioresponses:
    with aioresponses() as m:
        yield m
