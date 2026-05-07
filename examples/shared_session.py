"""Share an aiohttp ClientSession across multiple Neverdark clients.

Useful in applications (e.g. Home Assistant) that manage a single
ClientSession for all outgoing HTTP requests.
"""

from __future__ import annotations

import asyncio

import aiohttp

from aioneverdark import NeverdarkClient


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        # Both clients reuse the same session; it is not closed when they exit.
        async with NeverdarkClient(host="192.168.1.x", session=session) as client:
            info = await client.get_info()
            print(f"Device: {info.model}")

        async with NeverdarkClient(host="192.168.1.y", session=session) as client2:
            stats = await client2.get_stats()
            print(f"Fuel:   {stats.fuel}%")


asyncio.run(main())
