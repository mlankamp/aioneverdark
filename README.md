# aioneverdark

Asynchronous Python client for controlling [Neverdark](https://neverdark.one) smart fireplaces via their REST API.

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
        info = await client.get_info()
        print(f"Model: {info.model}, firmware: {info.fw_ver}, MAC: {info.dev_mac}")

asyncio.run(main())
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy src/aioneverdark
```
