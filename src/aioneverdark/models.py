from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FireplaceInfo:
    """Response model for /getinfo."""

    fw_ver: str
    hw_ver: str
    model: str
    dev_id: str
    home_wifi: str
    loc_ip: str
    dev_mac: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FireplaceInfo:
        return cls(
            fw_ver=data["fw_ver"],
            hw_ver=data["hw_ver"],
            model=data["model"],
            dev_id=data["dev_id"],
            home_wifi=data["home_wifi"],
            loc_ip=data["loc_ip"],
            dev_mac=data["dev_mac"],
        )
