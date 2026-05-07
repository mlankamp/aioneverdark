"""Get device info from a Neverdark fireplace."""

from __future__ import annotations

import asyncio

from aioneverdark import NeverdarkClient


async def main() -> None:
    async with NeverdarkClient(host="192.168.1.x") as client:
        info = await client.get_info()

    print(f"Model:    {info.model}")
    print(f"Firmware: {info.fw_ver}")
    print(f"Hardware: {info.hw_ver}")
    print(f"MAC:      {info.dev_mac}")
    print(f"Local IP: {info.loc_ip}")
    print(f"Wi-Fi:    {info.home_wifi}")


asyncio.run(main())
