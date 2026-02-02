# Basic Bot Example

A standalone bot that responds to commands.

## Full Example

```python
import asyncio
import json
import logging
import signal
from mezon import MezonClient, ButtonBuilder, ButtonMessageStyle
from mezon.models import ChannelMessageContent, ApiSentTokenRequest
from mezon.protobuf.api import api_pb2

# Initialize client
client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    enable_logging=True,
    log_level=logging.INFO,
)

# Command handlers
async def handle_message(message: api_pb2.ChannelMessage):
    # Ignore bot's own messages
    if message.sender_id == client.client_id:
        return

    # Parse content
    content = json.loads(message.content)
    text = content.get("t", "").strip()

    # Get channel for responses
    channel = await client.channels.fetch(message.channel_id)
    msg = channel.messages.get(message.message_id)

    # Command: !help
    if text == "!help":
        help_text = """**Available Commands:**
- `!help` - Show this message
- `!ping` - Check bot latency
- `!hello` - Get a greeting
- `!tip @user` - Send tokens to a user
- `!poll` - Create a simple poll"""

        await msg.reply(content=ChannelMessageContent(t=help_text))

    # Command: !ping
    elif text == "!ping":
        await msg.reply(content=ChannelMessageContent(t="Pong!"))

    # Command: !hello
    elif text == "!hello":
        await channel.send_ephemeral(
            receiver_id=message.sender_id,
            content=ChannelMessageContent(text="Hello! This is a private message.")
        )
        await msg.reply(content=ChannelMessageContent(t=f"Hello <@{message.sender_id}>!"))

    # Command: !tip
    elif text.startswith("!tip"):
        # Extract mentioned user
        mentions = content.get("mentions", [])
        if not mentions:
            await msg.reply(content=ChannelMessageContent(t="Usage: !tip @user"))
            return

        receiver_id = mentions[0].get("user_id")
        result = await client.send_token(
            ApiSentTokenRequest(
                receiver_id=receiver_id,
                amount=1,
                note="Tip from bot!",
            )
        )

        if result.ok:
            await msg.reply(content=ChannelMessageContent(t="Token sent!"))
        else:
            await msg.reply(content=ChannelMessageContent(t=f"Failed: {result.error}"))

    # Command: !poll
    elif text == "!poll":
        buttons = ButtonBuilder()
        buttons.add_button("vote_yes", "Yes", ButtonMessageStyle.SUCCESS)
        buttons.add_button("vote_no", "No", ButtonMessageStyle.DANGER)
        buttons.add_button("vote_maybe", "Maybe", ButtonMessageStyle.SECONDARY)

        await channel.send(
            content=ChannelMessageContent(
                t="**Quick Poll:** Do you like this bot?",
                components=[{"components": buttons.build()}]
            )
        )

# Handle button clicks
async def handle_button(event):
    button_id = event.button_id
    user_id = event.user_id
    channel = await client.channels.fetch(event.channel_id)

    if button_id.startswith("vote_"):
        vote = button_id.replace("vote_", "")
        await channel.send_ephemeral(
            receiver_id=user_id,
            content=ChannelMessageContent(text=f"You voted: {vote}")
        )

# Register handlers
client.on_channel_message(handle_message)
client.on_message_button_clicked(handle_button)

# Graceful shutdown
async def shutdown():
    print("Shutting down...")
    if client.socket_manager:
        await client.socket_manager.disconnect()

async def main():
    await client.login()
    print(f"Bot is running as {client.client_id}")

    # Handle signals
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

## Running the Bot

1. Replace `YOUR_BOT_ID` and `YOUR_API_KEY` with your credentials
2. Run: `python bot.py`
3. Test commands in a Mezon channel

## Using Environment Variables

```python
import os

client = MezonClient(
    client_id=os.environ["MEZON_BOT_ID"],
    api_key=os.environ["MEZON_API_KEY"],
)
```

Run with:

```bash
MEZON_BOT_ID=your_id MEZON_API_KEY=your_key python bot.py
```
