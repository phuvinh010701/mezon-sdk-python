# Mezon SDK Python

[![PyPI version](https://badge.fury.io/py/mezon-sdk.svg)](https://badge.fury.io/py/mezon-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/mezon-sdk.svg)](https://pypi.org/project/mezon-sdk/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python SDK for building bots and applications on the Mezon platform. Async-first, type-safe, and production-ready.

## Installation

```bash
pip install mezon-sdk
```

## Quick Start

```python
import asyncio
from mezon import MezonClient
from mezon.models import ChannelMessageContent
from mezon.protobuf.api import api_pb2

client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
)

async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return
    channel = await client.channels.fetch(message.channel_id)
    await channel.send(content=ChannelMessageContent(t="Hello!"))

client.on_channel_message(handle_message)

async def main():
    await client.login()
    await asyncio.Event().wait()

asyncio.run(main())
```

## Documentation

**Full documentation:** [https://docs.laptrinhai.id.vn/](https://docs.laptrinhai.id.vn)

- [Installation Guide](https://docs.laptrinhai.id.vn/getting-started/installation/)
- [Quick Start](https://docs.laptrinhai.id.vn/getting-started/quickstart/)
- [API Reference](https://docs.laptrinhai.id.vn/api-reference/client/)
- [Examples](https://docs.laptrinhai.id.vn/examples/basic-bot/)

## Features

- Async/await native with `asyncio`
- Real-time WebSocket with auto-reconnection
- Type-safe with Pydantic models
- Event-driven architecture
- Interactive messages (buttons, forms)
- Token sending support
- Message caching with SQLite

## Testing

Pytest is the primary path for focused unit and regression coverage.

For regression coverage around socket/protobuf/login behavior, run:

```bash
uv run pytest tests/unit/test_socket_regressions.py
```

You can also run the broader pytest suite with:

```bash
uv run pytest tests/
```

For broader integration coverage against a real Mezon environment, set the required `MEZON_*` environment variables and run:

```bash
uv run python -m tests.test_runner
```

The integration runner includes the reconnect/login suite in `tests/test_reconnect.py`.

## Links

- [PyPI Package](https://pypi.org/project/mezon-sdk/)
- [GitHub Repository](https://github.com/phuvinh010701/mezon-sdk-python)
- [Issue Tracker](https://github.com/phuvinh010701/mezon-sdk-python/issues)
- [Changelog](https://phuvinh010701.github.io/mezon-sdk-python/changelog/)

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
