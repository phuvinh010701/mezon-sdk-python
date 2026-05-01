# Quick Start

Build your first Mezon bot in minutes.

## Prerequisites

- Mezon bot ID and API key
- Python 3.10+
- `mezon-sdk` installed

## Basic bot

Create `bot.py`:

```python
import asyncio
import json
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

    payload = json.loads(message.content)
    text = payload.get("t", "")

    if text.startswith("!hello"):
        channel = await client.channels.fetch(message.channel_id)
        await channel.send(
            content=ChannelMessageContent(t="Hello! I'm a Mezon bot")
        )

client.on_channel_message(handle_message)

async def main():
    await client.login()
    print("Bot is running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python bot.py
```

## What is happening

1. `MezonClient` stores credentials and prepares event/caching infrastructure.
2. `client.login()` authenticates, initializes managers, and opens the real-time socket.
3. `client.on_channel_message(...)` registers a handler for incoming channel messages.
4. `client.channels.fetch(...)` resolves a `TextChannel` object.
5. `channel.send(...)` writes a chat message through the socket manager.

## Replying to a message

```python
async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

    channel = await client.channels.fetch(message.channel_id)
    msg = await channel.messages.fetch(message.message_id)
    await msg.reply(content=ChannelMessageContent(t="Got your message"))
```

## Sending an ephemeral response

```python
await channel.send_ephemeral(
    receiver_ids=[message.sender_id],
    content=ChannelMessageContent(text="Only you can see this"),
)
```

## Handling more events

```python
from mezon.protobuf.rtapi import realtime_pb2

async def on_channel_created(event: realtime_pb2.ChannelCreatedEvent):
    print(f"New channel: {event.channel_id}")

async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(f"User {event.user_id} joined {event.channel_id}")

client.on_channel_created(on_channel_created)
client.on_user_channel_added(on_user_joined)
```

## Use environment variables in production

```python
import os

client = MezonClient(
    client_id=os.environ["MEZON_BOT_ID"],
    api_key=os.environ["MEZON_API_KEY"],
)
```

## Next steps

- [Client Configuration](../guide/client.md)
- [Event Handling](../guide/events.md)
- [Sending Messages](../guide/messaging.md)
- [Interactive Messages](../guide/interactive.md)
- [FastAPI Integration](../examples/fastapi.md)
