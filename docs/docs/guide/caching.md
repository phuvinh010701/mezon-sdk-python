# Message Caching

The SDK includes built-in message caching using async SQLite for better performance.

## How It Works

Messages are automatically cached to a local SQLite database when received:

- **Faster Retrieval** - Cached messages load instantly
- **Offline Access** - Access previously received messages offline
- **Non-blocking** - All operations are async
- **Automatic** - Handled by the SDK automatically

## Database Location

Default location:

```
./mezon-cache/mezon-messages-cache.db
```

## Custom Location

```python
from mezon.messages.db import MessageDB

# Custom path
message_db = MessageDB(db_path="./custom-path/messages.db")
```

## Working with Cached Messages

```python
from mezon.messages.db import MessageDB

async def work_with_cache():
    async with MessageDB() as db:
        # Get messages by channel
        messages = await db.get_messages_by_channel(
            channel_id="channel_123",
            limit=50,
            offset=0
        )

        # Get specific message
        message = await db.get_message_by_id(
            message_id="msg_456",
            channel_id="channel_123"
        )

        # Count messages
        count = await db.get_message_count(channel_id="channel_123")
        total = await db.get_message_count()  # All messages

        # Clear channel messages
        deleted = await db.clear_channel_messages("channel_123")

        # Delete specific message
        success = await db.delete_message("msg_456", "channel_123")
```

## MessageDB Methods

| Method | Description |
|--------|-------------|
| `get_messages_by_channel(channel_id, limit, offset)` | Get messages from a channel |
| `get_message_by_id(message_id, channel_id)` | Get a specific message |
| `get_message_count(channel_id=None)` | Count messages |
| `clear_channel_messages(channel_id)` | Delete all messages in a channel |
| `delete_message(message_id, channel_id)` | Delete a specific message |

## Performance Benefits

Using `aiosqlite` provides:

- **Non-blocking I/O** - Database operations don't block the event loop
- **Concurrent Operations** - Multiple database operations can run concurrently
- **Lazy Connection** - Connection established only when needed
- **Auto-cleanup** - Context manager handles cleanup

## Example: Search Cached Messages

```python
from mezon.messages.db import MessageDB

async def search_messages(channel_id: str, keyword: str):
    async with MessageDB() as db:
        messages = await db.get_messages_by_channel(
            channel_id=channel_id,
            limit=1000
        )

        matching = [
            msg for msg in messages
            if keyword.lower() in msg.content.lower()
        ]

        return matching
```

## Cache with Message Handling

```python
from mezon.messages.db import MessageDB
from mezon.protobuf.api import api_pb2

async def handle_message(message: api_pb2.ChannelMessage):
    # Message is automatically cached by the SDK

    # Later, retrieve from cache
    async with MessageDB() as db:
        cached = await db.get_message_by_id(
            message_id=message.message_id,
            channel_id=message.channel_id
        )
        if cached:
            print(f"Found in cache: {cached.content}")

client.on_channel_message(handle_message)
```
