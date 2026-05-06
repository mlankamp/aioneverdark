# aioneverdark

Async Python library for controlling [Neverdark](https://neverdark.one) smart fireplaces via their REST API.

## Installation

```bash
pip install aioneverdark
```

## Usage

```python
import asyncio
from aioneverdark import NeverdarkClient

async def main() -> None:
    async with NeverdarkClient(host="192.168.1.x") as client:
        status = await client.get_status()
        print(f"Fireplace is {'on' if status.is_on else 'off'}, flame level: {status.flame_level}")

asyncio.run(main())
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy src/aioneverdark
```
