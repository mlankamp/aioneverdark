# aioneverdark – Copilot Instructions

## Project overview

`aioneverdark` is an async Python library for controlling Neverdark smart fireplaces over the local network via their REST API. It is built on top of `aiohttp` and uses `asyncio` throughout. The API was reverse-engineered from the Neverdark mobile app/smart home module.

## Build, test, and lint commands

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_client.py

# Run a single test by name
pytest tests/test_client.py::TestFireplaceClient::test_get_status

# Lint and format
ruff check .
ruff format .

# Type checking
mypy src/aioneverdark
```

## Project layout

```
src/
  aioneverdark/
    __init__.py       # Public API surface (re-exports)
    client.py         # NeverdarkClient – main entry point
    models.py         # Pydantic models for API request/response objects
    exceptions.py     # Library-specific exception hierarchy
    const.py          # Endpoint paths and constants
tests/
  conftest.py         # Shared fixtures (mock client session)
  test_client.py
pyproject.toml
```

## Architecture

- **`NeverdarkClient`** is the single public class consumers instantiate. It owns the `aiohttp.ClientSession` lifecycle (created on `__aenter__`, closed on `__aexit__`). Use it as an async context manager.
- **No authentication** — the device is accessed directly by host IP on the local network; no tokens or credentials are required.
- **Models** are plain `@dataclass` classes in `models.py`. JSON responses are parsed via a `from_dict(data)` classmethod on each model.
- **Exceptions** derive from `NeverdarkError` (base). HTTP errors are wrapped into `NeverdarkApiError` with `status_code` and `message` fields.

## Key conventions

### Async context manager pattern
`AioneverdarkClient` must be used as an async context manager (it manages the `aiohttp.ClientSession`). Only the device IP/host is required:
```python
async with AioneverdarkClient(host="192.168.1.x") as client:
    status = await client.get_status()
```

### Single `ClientSession` per client instance
Never create a new `aiohttp.ClientSession` per request. The session is created once in `__aenter__` and reused for all requests in that instance.

### All public methods are `async def`
No sync wrappers. Consumers are expected to use `asyncio`.

### Request helper
Internal HTTP calls go through a private `_request(method, path, **kwargs)` coroutine on the client that handles auth headers, base URL composition, error mapping, and retries. Do not call `self._session` directly from feature methods.

### Error handling
Raise `NeverdarkApiError` for non-2xx responses. Never swallow exceptions silently.

### Testing with `aioresponses`
Mock HTTP calls using the `aioresponses` library (not `unittest.mock` patching of `aiohttp`). Shared fixtures live in `tests/conftest.py`:
```python
@pytest.fixture
def mocked_api():
    with aioresponses() as m:
        yield m
```
Tests are async functions — no `@pytest.mark.asyncio` decorator needed because `asyncio_mode = "auto"` is set in `pyproject.toml`.

### `pyproject.toml` is the single source of truth
Dependencies, optional `[dev]` extras, `ruff` config, `mypy` config, and `pytest` config all live in `pyproject.toml`. Do not create separate config files (`setup.cfg`, `.flake8`, `mypy.ini`, etc.).

### Type hints
All public functions and methods must be fully annotated. Run `mypy` to verify. Use `from __future__ import annotations` at the top of every module.
