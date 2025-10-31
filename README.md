# Mezon SDK Python

[![PyPI version](https://badge.fury.io/py/mezon-sdk.svg)](https://badge.fury.io/py/mezon-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/mezon-sdk.svg)](https://pypi.org/project/mezon-sdk/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python implementation of the Mezon SDK with 1:1 logic mapping to the TypeScript SDK. Build powerful bots and applications for the Mezon platform with a clean, async-first API.

## Features

- =€ **Async/Await Native** - Built from the ground up with `asyncio` for high-performance concurrent operations
- = **Real-time WebSocket** - Full support for real-time messaging and events via WebSocket with automatic reconnection
- =æ **Type-Safe** - Comprehensive type hints and Pydantic models for better IDE support and fewer runtime errors
- <¯ **Event-Driven** - Elegant event handler system for building reactive applications
- = **Protocol Buffers** - Efficient binary serialization for optimal performance
- =á **Production Ready** - Proper error handling, logging, and graceful shutdown mechanisms
- >é **Framework Integration** - Works seamlessly with FastAPI, Flask, Django, and other Python frameworks

## Installation

### Using pip

```bash
pip install mezon-sdk
```

### Using Poetry

```bash
poetry add mezon-sdk
```

### Using uv (Recommended for fast installs)

```bash
uv pip install mezon-sdk
```

## Quick Start

### Basic Bot Example

```python
from mezon import MezonClient, Events
from mezon.protobuf.rtapi import realtime_pb2
import json
import asyncio

# Initialize the client
client = MezonClient(
    bot_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY"
)

# Handle incoming messages
async def handle_message(message: realtime_pb2.ChannelMessageSend):
    content = json.loads(message.content).get("t")

    if content.startswith("!hello"):
        await client.send_message(
            clan_id=message.clan_id,
            channel_id=message.channel_id,
            mode=message.mode,
            is_public=message.is_public,
            msg="Hello! I'm a Mezon bot =K"
        )

# Register event handlers
client.on(Events.CHANNEL_MESSAGE, handle_message)

# Run the bot
async def main():
    await client.login()
    # Keep the bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

### FastAPI Integration

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mezon import MezonClient, Events
from mezon.protobuf.rtapi import realtime_pb2
import json

client = MezonClient(bot_id="YOUR_BOT_ID", api_key="YOUR_API_KEY")

async def handle_channel_message(message: realtime_pb2.ChannelMessageSend):
    message_content = json.loads(message.content)
    content = message_content.get("t")

    if content.startswith("!ping"):
        await client.send_message(
            clan_id=message.clan_id,
            channel_id=message.channel_id,
            mode=message.mode,
            is_public=message.is_public,
            msg="Pong! <Ó"
        )

client.on(Events.CHANNEL_MESSAGE, handle_channel_message)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Mezon
    print("Connecting to Mezon...")
    await client.login()
    print("Connected successfully!")

    yield

    # Shutdown: Cleanup connections
    print("Shutting down - closing connections...")
    if hasattr(client, 'socket_manager') and client.socket_manager:
        await client.socket_manager.disconnect()
    print("Disconnected successfully!")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return JSONResponse(content={"status": "healthy"})

# Run with: uvicorn main:app --reload
```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip/poetry

### Setting up with Conda + uv (Recommended)

```bash
# Create and activate conda environment
conda create -n mezon-sdk python=3.10
conda activate mezon-sdk

# Install uv (fast package installer)
pip install uv

# Clone the repository
git clone https://github.com/phuvinh010701/mezon-sdk-python.git
cd mezon-sdk-python

# Install dependencies with uv
uv pip install -e ".[dev]"
```

### Setting up with Poetry

```bash
# Install poetry if you haven't
pip install poetry

# Clone the repository
git clone https://github.com/phuvinh010701/mezon-sdk-python.git
cd mezon-sdk-python

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Setting up with venv + pip

```bash
# Clone the repository
git clone https://github.com/phuvinh010701/mezon-sdk-python.git
cd mezon-sdk-python

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Core Concepts

### Events

The SDK provides a comprehensive event system. Available events:

```python
from mezon import Events

# Message Events
Events.CHANNEL_MESSAGE          # New message in channel
Events.MESSAGE_REACTION_EVENT   # Reaction added/removed
Events.MESSAGE_TYPING_EVENT     # User is typing

# Channel Events
Events.CHANNEL_CREATED_EVENT    # New channel created
Events.CHANNEL_UPDATED_EVENT    # Channel updated
Events.CHANNEL_DELETED_EVENT    # Channel deleted
Events.CHANNEL_PRESENCE_EVENT   # User presence in channel

# User Events
Events.USER_CHANNEL_ADDED_EVENT    # User added to channel
Events.USER_CHANNEL_REMOVED_EVENT  # User removed from channel
Events.USER_CLAN_REMOVED_EVENT     # User removed from clan

# Clan Events
Events.CLAN_UPDATED_EVENT          # Clan settings updated
Events.CLAN_EVENT_CREATED          # New clan event

# Voice Events
Events.VOICE_STARTED_EVENT      # Voice session started
Events.VOICE_ENDED_EVENT        # Voice session ended
Events.VOICE_JOINED_EVENT       # User joined voice
Events.VOICE_LEAVED_EVENT       # User left voice

# And many more...
```

### Sending Messages

```python
await client.send_message(
    clan_id="clan_id",
    channel_id="channel_id",
    mode=1,  # Channel mode
    is_public=True,
    msg="Your message here",
    mentions=None,  # Optional: List[ApiMessageMention]
    attachments=None,  # Optional: List[ApiMessageAttachment]
    ref=None,  # Optional: List[ApiMessageRef] for replies
)
```

### Event Handlers

```python
# Async handler (recommended)
async def async_handler(data):
    await some_async_operation()

client.on(Events.CHANNEL_MESSAGE, async_handler)

# Sync handler (also supported)
def sync_handler(data):
    print(f"Received: {data}")

client.on(Events.GIVE_COFFEE, sync_handler)
```

## API Reference

### MezonClient

```python
client = MezonClient(
    bot_id: str,              # Your bot ID
    api_key: str,             # Your API key
    host: str = "gw.mezon.ai",  # API host (optional)
    port: str = "443",        # API port (optional)
    use_ssl: bool = True,     # Use SSL connection (optional)
    timeout: int = 7000,      # Request timeout in ms (optional)
)
```

#### Methods

- `async login()` - Authenticate and connect to Mezon
- `async send_message(...)` - Send a message to a channel
- `on(event_name, handler)` - Register an event handler

### Models

```python
from mezon.models import (
    ApiMessageMention,      # Message mention
    ApiMessageAttachment,   # Message attachment
    ApiMessageRef,          # Message reference (reply)
    ChannelMessageAck,      # Message acknowledgment
    ApiChannelDescription,  # Channel information
    ApiClanDesc,           # Clan information
)
```

## Advanced Usage

### Custom Heartbeat Timeout Callback

```python
from mezon.socket import Socket

socket = Socket(host="gw.mezon.ai", port="443", use_ssl=True)

async def on_heartbeat_timeout():
    print("Connection lost - attempting reconnection...")
    # Your reconnection logic here

socket.onheartbeattimeout = on_heartbeat_timeout
```

### Graceful Shutdown

```python
import signal
import asyncio

async def shutdown(client):
    """Gracefully shutdown the client"""
    print("Shutting down...")
    if hasattr(client, 'socket_manager') and client.socket_manager:
        await client.socket_manager.disconnect()
    print("Shutdown complete")

async def main():
    client = MezonClient(bot_id="...", api_key="...")
    await client.login()

    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(shutdown(client))
        )

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=mezon --cov-report=html
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Workflow

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`ruff check .`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

## Troubleshooting

### Connection Issues

If you experience connection timeouts:

```python
# Increase timeout
client = MezonClient(
    bot_id="...",
    api_key="...",
    timeout=15000  # 15 seconds
)
```

### Process Won't Exit (Ctrl+C)

Make sure to properly close connections:

```python
# In your shutdown handler
if hasattr(client, 'socket_manager') and client.socket_manager:
    await client.socket_manager.disconnect()
```

### Import Errors

If you get import errors, ensure all dependencies are installed:

```bash
uv pip install --upgrade mezon-sdk
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Links

- =æ [PyPI Package](https://pypi.org/project/mezon-sdk/)
- = [GitHub Repository](https://github.com/phuvinh010701/mezon-sdk-python)
- = [Issue Tracker](https://github.com/phuvinh010701/mezon-sdk-python/issues)
- =Ö [Changelog](CHANGELOG.md)

## Support

If you encounter any issues or have questions:

1. Check the [Issue Tracker](https://github.com/phuvinh010701/mezon-sdk-python/issues)
2. Create a new issue with detailed information
3. Join our community discussions

## Acknowledgments

- Based on the [Mezon TypeScript SDK](https://github.com/mezon/mezon-ts)
- Built with d by the community

---

**Made with Python = | Powered by Mezon =€**
