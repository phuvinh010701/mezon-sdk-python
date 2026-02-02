# Quick Start

Build your first Mezon bot in minutes.

## Prerequisites

- Mezon Bot ID and API Key (obtain from Mezon platform)
- Python 3.10+
- `mezon-sdk` installed

## Basic Bot

Create a file `bot.py`:

```python
import asyncio
import json
from mezon import MezonClient
from mezon.models import ChannelMessageContent
from mezon.protobuf.api import api_pb2

# Initialize the client
client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
)

# Handle incoming messages
async def handle_message(message: api_pb2.ChannelMessage):
    # Ignore messages from the bot itself
    if message.sender_id == client.client_id:
        return

    # Parse message content
    message_content = json.loads(message.content)
    text = message_content.get("t", "")

    # Respond to !hello command
    if text.startswith("!hello"):
        channel = await client.channels.fetch(message.channel_id)
        await channel.send(
            content=ChannelMessageContent(t="Hello! I'm a Mezon bot")
        )

# Register the event handler
client.on_channel_message(handle_message)

# Run the bot
async def main():
    await client.login()
    print("Bot is running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

Run your bot:

```bash
python bot.py
```

## What's Happening?

1. **`MezonClient`** - The main entry point that handles authentication and connections
2. **`client.login()`** - Authenticates with the Mezon API and establishes a WebSocket connection
3. **`client.on_channel_message()`** - Registers a handler for incoming messages
4. **`client.channels.fetch()`** - Gets a channel object to send messages
5. **`channel.send()`** - Sends a message to the channel

## Adding More Features

### Reply to Messages

```python
async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

    channel = await client.channels.fetch(message.channel_id)
    msg = channel.messages.get(message.message_id)
    await msg.reply(content=ChannelMessageContent(t="Got your message!"))
```

### Send Ephemeral Messages

Ephemeral messages are only visible to a specific user:

```python
await channel.send_ephemeral(
    receiver_id=message.sender_id,
    content=ChannelMessageContent(text="Only you can see this!")
)
```

### Handle Multiple Events

```python
from mezon.protobuf.rtapi import realtime_pb2

async def on_channel_created(event: realtime_pb2.ChannelCreatedEvent):
    print(f"New channel: {event.channel_id}")

async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(f"User {event.user_id} joined {event.channel_id}")

client.on_channel_created(on_channel_created)
client.on_user_channel_added(on_user_joined)
```

## Environment Variables

For production, use environment variables:

```python
import os

client = MezonClient(
    client_id=os.environ["MEZON_BOT_ID"],
    api_key=os.environ["MEZON_API_KEY"],
)
```

## Next Steps

- [Event Handling](../guide/events.md) - Learn about all available events
- [Sending Messages](../guide/messaging.md) - Advanced messaging features
- [Interactive Messages](../guide/interactive.md) - Buttons and forms
- [FastAPI Integration](../examples/fastapi.md) - Build a web API with your bot
