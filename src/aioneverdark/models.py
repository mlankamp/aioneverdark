from __future__ import annotations

from enum import IntEnum

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FireplaceMode(IntEnum):
    Off = 1
    WarmingUp = 2
    Running = 3
    CoolingDown = 4


class FireplaceStats(BaseModel):
    """Response model for /stats."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    room_name: str
    protected: bool
    id: str
    name: str
    temp_progress: int
    current_temperature: int
    target_temperature: int
    fuel: int
    timer: int
    expected_time: int
    error_code: int
    mode: FireplaceMode


class FireplaceInfo(BaseModel):
    """Response model for /getinfo."""

    fw_ver: str
    hw_ver: str
    model: str
    dev_id: str
    home_wifi: str
    loc_ip: str
    dev_mac: str
