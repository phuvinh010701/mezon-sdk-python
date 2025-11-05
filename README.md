# Mezon SDK Python

[![PyPI version](https://badge.fury.io/py/mezon-sdk.svg)](https://badge.fury.io/py/mezon-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/mezon-sdk.svg)](https://pypi.org/project/mezon-sdk/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Python implementation of the Mezon SDK with 1:1 logic mapping to the TypeScript SDK. Build powerful bots and applications for the Mezon platform with a clean, async-first API.

## Features

- =� **Async/Await Native** - Built from the ground up with `asyncio` for high-performance concurrent operations
- = **Real-time WebSocket** - Full support for real-time messaging and events via WebSocket with automatic reconnection
- =� **Type-Safe** - Comprehensive type hints and Pydantic models for better IDE support and fewer runtime errors
- <� **Event-Driven** - Elegant event handler system for building reactive applications
- = **Protocol Buffers** - Efficient binary serialization for optimal performance
- =� **Production Ready** - Proper error handling, logging, and graceful shutdown mechanisms
- >� **Framework Integration** - Works seamlessly with FastAPI, Flask, Django, and other Python frameworks

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

## Dependencies

The SDK has minimal dependencies for a lightweight installation:

- **pydantic** (>=2.12.3) - Data validation and settings management
- **aiohttp** (>=3.9.0) - Async HTTP client/server
- **websockets** (>=12.0) - WebSocket protocol implementation
- **protobuf** (>=4.25.0) - Protocol Buffers for efficient serialization
- **pyjwt** (>=2.8.0) - JSON Web Token implementation
- **aiosqlite** (>=0.20.0) - Async SQLite database interface for message caching

All dependencies are automatically installed when you install the SDK.

## Quick Start

### Basic Bot Example

```python
import asyncio
import json
import logging
from mezon import MezonClient
from mezon.protobuf.api import api_pb2

# Initialize the client with logging
client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    enable_logging=True,
    log_level=logging.INFO,
)

# Handle incoming messages
async def handle_message(message: api_pb2.ChannelMessage):
    # Ignore messages from the bot itself
    if message.sender_id == client.client_id:
        return

    # Parse message content
    message_content = json.loads(message.content)
    content = message_content.get("t")

    # Respond to !hello command
    if content.startswith("!hello"):
        channel = await client.channels.fetch(message.channel_id)
        await channel.send(content="Hello! I'm a Mezon bot 👋")

# Register event handler using the convenient method
client.on_channel_message(handle_message)

# Run the bot
async def main():
    await client.login()
    print("Bot is running...")
    # Keep the bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

### FastAPI Integration

```python
from contextlib import asynccontextmanager
import logging
import json
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mezon import MezonClient
from mezon.models import ApiSentTokenRequest
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2

# Initialize client with logging
client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    enable_logging=True,
    log_level=logging.INFO,
)

# Handle incoming messages
async def handle_channel_message(message: api_pb2.ChannelMessage):
    # Ignore bot's own messages
    if message.sender_id == client.client_id:
        return

    message_content = json.loads(message.content)
    content = message_content.get("t")

    if content.startswith("!ping"):
        channel = await client.channels.fetch(message.channel_id)
        await channel.send(content="Pong! 🏓")

    elif content.startswith("!tip"):
        # Send tokens to user
        await client.send_token(
            ApiSentTokenRequest(
                receiver_id=message.sender_id,
                amount=10,
                note="Thanks for using the bot!",
            )
        )

# Handle channel events
async def handle_channel_created(message: realtime_pb2.ChannelCreatedEvent):
    print(f"New channel created: {message.channel_id}")

async def handle_channel_updated(message: realtime_pb2.ChannelUpdatedEvent):
    print(f"Channel updated: {message.channel_id}")

async def handle_user_joined(message: realtime_pb2.UserChannelAdded):
    print(f"User {message.user_id} joined channel {message.channel_id}")

# Register event handlers using convenient methods
client.on_channel_message(handle_channel_message)
client.on_channel_created(handle_channel_created)
client.on_channel_updated(handle_channel_updated)
client.on_user_channel_added(handle_user_joined)

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

@app.get("/clan/{clan_id}/voice-users")
async def get_voice_users(clan_id: str):
    """Get users in voice channels for a specific clan"""
    clan = await client.clans.get(clan_id)
    voice_users = await clan.list_channel_voice_users()
    return JSONResponse(content=voice_users)

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
# Method 1: Using channel objects (recommended)
channel = await client.channels.fetch("channel_id")
await channel.send(content="Your message here")

# Send with mentions and attachments
from mezon.models import ApiMessageMention, ApiMessageAttachment

await channel.send(
    content="Hello @user!",
    mentions=[ApiMessageMention(user_id="user_id")],
    attachments=[ApiMessageAttachment(url="https://example.com/image.png")]
)

# Reply to a message
message = await channel.messages.get("message_id")
await message.reply(content="This is a reply")

# Send ephemeral message (only visible to specific user)
await channel.send_ephemeral(
    receiver_id="user_id",
    content="This message is only visible to you"
)

# Method 2: Using client.send_message (legacy)
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

# Send tokens to users
from mezon.models import ApiSentTokenRequest

await client.send_token(
    ApiSentTokenRequest(
        receiver_id="user_id",
        amount=100,
        note="Thanks for your help!",
    )
)
```

### Event Handlers

The SDK provides convenient methods for common events:

```python
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2

# Message events - using convenient methods (recommended)
async def on_message(message: api_pb2.ChannelMessage):
    print(f"Message from {message.sender_id}: {message.content}")

client.on_channel_message(on_message)

# Channel events
async def on_channel_created(event: realtime_pb2.ChannelCreatedEvent):
    print(f"New channel: {event.channel_id}")

async def on_channel_updated(event: realtime_pb2.ChannelUpdatedEvent):
    print(f"Channel updated: {event.channel_id}")

async def on_channel_deleted(event: realtime_pb2.ChannelDeletedEvent):
    print(f"Channel deleted: {event.channel_id}")

client.on_channel_created(on_channel_created)
client.on_channel_updated(on_channel_updated)
client.on_channel_deleted(on_channel_deleted)

# User events
async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(f"User {event.user_id} joined channel {event.channel_id}")

async def on_user_left(event: realtime_pb2.UserChannelRemoved):
    print(f"User {event.user_id} left channel {event.channel_id}")

client.on_user_channel_added(on_user_joined)
client.on_user_channel_removed(on_user_left)

# Clan events
async def on_user_clan_added(event: realtime_pb2.AddClanUserEvent):
    print(f"User joined clan: {event.clan_id}")

client.on_add_clan_user(on_user_clan_added)

# Generic event handler (for any event)
from mezon import Events

async def generic_handler(data):
    await some_async_operation()

client.on(Events.VOICE_STARTED_EVENT, generic_handler)

# Sync handlers are also supported
def sync_handler(data):
    print(f"Received: {data}")

client.on(Events.GIVE_COFFEE, sync_handler)
```

## API Reference

### MezonClient

```python
client = MezonClient(
    client_id: str,              # Your bot ID
    api_key: str,             # Your API key
    host: str = "gw.mezon.ai",  # API host (optional)
    port: str = "443",        # API port (optional)
    use_ssl: bool = True,     # Use SSL connection (optional)
    timeout: int = 7000,      # Request timeout in ms (optional)
)
```

#### Methods

**Authentication & Connection:**
- `async login()` - Authenticate and connect to Mezon
- `async close_socket()` - Close WebSocket connection

**Messaging:**
- `async send_message(...)` - Send a message to a channel (legacy)
- `async send_token(request: ApiSentTokenRequest)` - Send tokens to a user

**Friends:**
- `async get_list_friends(limit, state, cursor)` - Get list of friends
- `async accept_friend(user_id: str)` - Accept a friend request
- `async add_friend(username: str, user_id: str)` - Add a friend

**Event Handlers (Convenient Methods):**
- `on_channel_message(handler)` - Handle channel messages
- `on_channel_created(handler)` - Handle channel creation
- `on_channel_updated(handler)` - Handle channel updates
- `on_channel_deleted(handler)` - Handle channel deletion
- `on_user_channel_added(handler)` - Handle user joining channel
- `on_user_channel_removed(handler)` - Handle user leaving channel
- `on_add_clan_user(handler)` - Handle user joining clan
- `on_clan_event_created(handler)` - Handle clan event creation
- `on_message_button_clicked(handler)` - Handle message button clicks
- `on_notification(handler)` - Handle notifications
- `on(event_name, handler)` - Register generic event handler

**Managers:**
- `client.channels` - Channel manager for accessing channels
- `client.clans` - Clan manager for accessing clans

### Clan

Access clan objects through the client:

```python
clan = await client.clans.get("clan_id")
```

**Clan Methods:**
- `async load_channels()` - Load all channels in the clan
- `async list_channel_voice_users(channel_id, channel_type, limit, state, cursor)` - List users in voice channels
- `async update_role(role_id: str, request: dict)` - Update a role
- `async list_roles(limit, state, cursor)` - List all roles in the clan

**Clan Properties:**
- `clan.id` - Clan ID
- `clan.name` - Clan name
- `clan.channels` - Channel manager for clan channels
- `clan.users` - User manager for clan users

**Example:**

```python
# Get clan and list voice users
clan = await client.clans.get("clan_id")
voice_users = await clan.list_channel_voice_users()
print(f"Users in voice: {voice_users}")

# List roles
roles = await clan.list_roles()
print(f"Clan roles: {roles}")

# Update a role
await clan.update_role(
    role_id="role_id",
    request={"title": "New Role Name", "permissions": ["SEND_MESSAGE"]}
)
```

### Channel

Access channels through the client or clan:

```python
# From client
channel = await client.channels.fetch("channel_id")

# From clan
clan = await client.clans.get("clan_id")
await clan.load_channels()
channel = await clan.channels.get("channel_id")
```

**Channel Methods:**
- `async send(content, mentions, attachments)` - Send a message
- `async send_ephemeral(receiver_id, content)` - Send ephemeral message
- `channel.messages.get(message_id)` - Get a message object

**Message Methods:**
- `async reply(content, mentions, attachments)` - Reply to a message

### Models

```python
from mezon.models import (
    ApiMessageMention,      # Message mention
    ApiMessageAttachment,   # Message attachment
    ApiMessageRef,          # Message reference (reply)
    ApiSentTokenRequest,    # Token sending request
    ChannelMessageAck,      # Message acknowledgment
    ApiChannelDescription,  # Channel information
    ApiClanDesc,           # Clan information
)
```

## Message Caching

The SDK includes built-in message caching using async SQLite (`aiosqlite`) for better performance and offline message access.

### How It Works

Messages are automatically cached to a local SQLite database when received. This provides:

- **Faster Message Retrieval**: Cached messages load instantly without API calls
- **Offline Access**: Access previously received messages even when offline
- **Non-blocking Operations**: All database operations are async and don't block the event loop
- **Automatic Management**: Cache is handled automatically by the SDK

### Database Location

By default, messages are cached in:
```
./mezon-cache/mezon-messages-cache.db
```

### Custom Cache Location

```python
from mezon.messages.db import MessageDB

# Initialize with custom path
message_db = MessageDB(db_path="./custom-path/messages.db")

client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    # Pass custom message_db to client if needed
)
```

### Working with Cached Messages

```python
from mezon.messages.db import MessageDB

async def get_cached_messages():
    async with MessageDB() as db:
        # Get messages from a specific channel
        messages = await db.get_messages_by_channel(
            channel_id="channel_123",
            limit=50,
            offset=0
        )

        # Get a specific message
        message = await db.get_message_by_id(
            message_id="msg_456",
            channel_id="channel_123"
        )

        # Get message count
        count = await db.get_message_count(channel_id="channel_123")
        total_count = await db.get_message_count()  # All messages

        # Clear channel messages
        deleted = await db.clear_channel_messages("channel_123")

        # Delete specific message
        success = await db.delete_message("msg_456", "channel_123")
```

### Performance Benefits

The async SQLite implementation using `aiosqlite` provides:

- **Non-blocking I/O**: Database operations don't block the event loop
- **Concurrent Operations**: Multiple database operations can run concurrently
- **Better Scalability**: Handles high message volumes without performance degradation
- **Lazy Connection**: Database connection is only established when needed

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
    client = MezonClient(client_id="...", api_key="...")
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
    client_id="...",
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

- =� [PyPI Package](https://pypi.org/project/mezon-sdk/)
- = [GitHub Repository](https://github.com/phuvinh010701/mezon-sdk-python)
- = [Issue Tracker](https://github.com/phuvinh010701/mezon-sdk-python/issues)
- =� [Changelog](CHANGELOG.md)

## Support

If you encounter any issues or have questions:

1. Check the [Issue Tracker](https://github.com/phuvinh010701/mezon-sdk-python/issues)
2. Create a new issue with detailed information
3. Join our community discussions

## Acknowledgments

- Based on the [Mezon TypeScript SDK](https://github.com/mezon/mezon-ts)
- Built with d by the community

---

**Made with Python =
 | Powered by Mezon =�**
