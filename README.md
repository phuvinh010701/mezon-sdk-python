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

**Full documentation:** [https://phuvinh010701.github.io/mezon-sdk-python/](https://phuvinh010701.github.io/mezon-sdk-python/)

- [Installation Guide](https://phuvinh010701.github.io/mezon-sdk-python/getting-started/installation/)
- [Quick Start](https://phuvinh010701.github.io/mezon-sdk-python/getting-started/quickstart/)
- [API Reference](https://phuvinh010701.github.io/mezon-sdk-python/api-reference/client/)
- [Examples](https://phuvinh010701.github.io/mezon-sdk-python/examples/basic-bot/)

## Features

- Async/await native with `asyncio`
- Real-time WebSocket with auto-reconnection
- Type-safe with Pydantic models
- Event-driven architecture
- Interactive messages (buttons, forms)
- Token sending support
- Message caching with SQLite

## Links

- [PyPI Package](https://pypi.org/project/mezon-sdk/)
- [GitHub Repository](https://github.com/phuvinh010701/mezon-sdk-python)
- [Issue Tracker](https://github.com/phuvinh010701/mezon-sdk-python/issues)
- [Changelog](https://phuvinh010701.github.io/mezon-sdk-python/changelog/)

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
