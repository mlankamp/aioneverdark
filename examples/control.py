"""Turn the fireplace on and set a flame level."""

from __future__ import annotations

import asyncio

from aioneverdark import NeverdarkClient
from aioneverdark.exceptions import NeverdarkCommandError


async def main() -> None:
    async with NeverdarkClient(host="192.168.1.x") as client:
        try:
            await client.turn_on()
            print("Fireplace turned on.")

            confirmed_level = await client.set_level(75)
            print(f"Flame level set to {confirmed_level}%.")
        except NeverdarkCommandError as err:
            print(f"Command failed: {err}")


asyncio.run(main())
