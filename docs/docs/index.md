# Mezon SDK Python

A Python implementation of the Mezon SDK for building bots and applications on the Mezon platform.

[![PyPI version](https://badge.fury.io/py/mezon-sdk.svg)](https://badge.fury.io/py/mezon-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/mezon-sdk.svg)](https://pypi.org/project/mezon-sdk/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Features

- **Async/Await Native** - Built with `asyncio` for high-performance concurrent operations
- **Real-time WebSocket** - Full support for real-time messaging with automatic reconnection
- **Type-Safe** - Comprehensive type hints and Pydantic models
- **Event-Driven** - Elegant event handler system for reactive applications
- **Protocol Buffers** - Efficient binary serialization
- **Production Ready** - Proper error handling, logging, and graceful shutdown

## Quick Install

```bash
pip install mezon-sdk
```

## Quick Example

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

## Next Steps

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Installation**

    ---

    Install the SDK using pip, poetry, or uv

    [:octicons-arrow-right-24: Installation Guide](getting-started/installation.md)

-   :material-rocket-launch:{ .lg .middle } **Quick Start**

    ---

    Build your first Mezon bot in minutes

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :material-book-open-variant:{ .lg .middle } **Guide**

    ---

    Learn about events, messaging, and more

    [:octicons-arrow-right-24: Read the Guide](guide/client.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete API documentation

    [:octicons-arrow-right-24: API Reference](api-reference/client.md)

</div>

## Links

- [PyPI Package](https://pypi.org/project/mezon-sdk/)
- [GitHub Repository](https://github.com/phuvinh010701/mezon-sdk-python)
- [Issue Tracker](https://github.com/phuvinh010701/mezon-sdk-python/issues)
