"""Read current stats from a Neverdark fireplace."""

from __future__ import annotations

import asyncio

from aioneverdark import NeverdarkClient
from aioneverdark.models import FireplaceMode


async def main() -> None:
    async with NeverdarkClient(host="192.168.1.x") as client:
        stats = await client.get_stats()

    print(f"Mode:                {stats.mode.name}")
    print(f"Current temperature: {stats.current_temperature}°C")
    print(f"Target temperature:  {stats.target_temperature}°C")
    print(f"Fuel:                {stats.fuel}%")
    print(f"Flame progress:      {stats.temp_progress}%")
    print(f"Expected time:       {stats.expected_time} min")
    print(f"Error code:          {stats.error_code}")

    if stats.mode is FireplaceMode.CoolingDown:
        print("Fireplace is cooling down.")
    elif stats.mode is FireplaceMode.Off:
        print("Fireplace is off.")


asyncio.run(main())
