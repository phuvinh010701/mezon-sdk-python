# Basic Bot Example

A simple bot that responds to commands and demonstrates replies, ephemeral messages, token sending, and button interactions.

## Full example

```python
import asyncio
import json
import logging
from mezon import ButtonBuilder, ButtonMessageStyle, MezonClient
from mezon.models import ApiSentTokenRequest, ChannelMessageContent
from mezon.protobuf.api import api_pb2

client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    enable_logging=True,
    log_level=logging.INFO,
)

async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

    payload = json.loads(message.content)
    text = payload.get("t", "").strip()

    channel = await client.channels.fetch(message.channel_id)
    msg = await channel.messages.fetch(message.message_id)

    if text == "!help":
        await msg.reply(
            content=ChannelMessageContent(
                t="Available commands: !help, !ping, !hello, !tip, !poll"
            )
        )

    elif text == "!ping":
        await msg.reply(content=ChannelMessageContent(t="Pong!"))

    elif text == "!hello":
        await channel.send_ephemeral(
            receiver_ids=[message.sender_id],
            content=ChannelMessageContent(text="Hello! This is a private message."),
        )
        await msg.reply(content=ChannelMessageContent(t="Hello!"))

    elif text.startswith("!tip"):
        mentions = payload.get("mentions", [])
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

    elif text == "!poll":
        buttons = ButtonBuilder()
        buttons.add_button("vote_yes", "Yes", ButtonMessageStyle.SUCCESS)
        buttons.add_button("vote_no", "No", ButtonMessageStyle.DANGER)
        buttons.add_button("vote_maybe", "Maybe", ButtonMessageStyle.SECONDARY)

        await channel.send(
            content=ChannelMessageContent(
                t="Do you like this bot?",
                components=[{"components": buttons.build()}],
            )
        )

async def handle_button(event):
    if event.button_id.startswith("vote_"):
        channel = await client.channels.fetch(event.channel_id)
        vote = event.button_id.replace("vote_", "")
        await channel.send_ephemeral(
            receiver_ids=[event.user_id],
            content=ChannelMessageContent(text=f"You voted: {vote}"),
        )

client.on_channel_message(handle_message)
client.on_message_button_clicked(handle_button)

async def main():
    await client.login()
    print(f"Bot is running as {client.client_id}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

## Highlights

- `channel.messages.fetch(...)` loads a `Message` helper before replying.
- `send_ephemeral(...)` expects `receiver_ids=[...]`.
- `send_token(...)` requires a successful `client.login()` first.
