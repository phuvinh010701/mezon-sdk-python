# Message

Represents a message on Mezon.

## Accessing Messages

```python
# From channel
channel = await client.channels.fetch("channel_id")
message = channel.messages.get("message_id")
```

## Methods

### `reply(...) -> ChannelMessageAck`

Reply to the message.

```python
from mezon.models import ChannelMessageContent, ApiMessageMention, ApiMessageAttachment

result = await message.reply(
    content=ChannelMessageContent(t="This is a reply!"),
    mentions=None,      # Optional[List[ApiMessageMention]]
    attachments=None,   # Optional[List[ApiMessageAttachment]]
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `content` | `ChannelMessageContent` | Reply content |
| `mentions` | `List[ApiMessageMention]` | User mentions |
| `attachments` | `List[ApiMessageAttachment]` | Attachments |

**Returns:** `ChannelMessageAck`

### `update(content: ChannelMessageContent) -> None`

Update/edit the message content.

```python
await message.update(
    content=ChannelMessageContent(t="Updated content (edited)")
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `content` | `ChannelMessageContent` | New content |

### `react(...) -> None`

Add a reaction to the message.

```python
await message.react(
    emoji_id="emoji_id",
    emoji="emoji_name",
    count=1
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `emoji_id` | `str` | Emoji ID |
| `emoji` | `str` | Emoji name/text |
| `count` | `int` | Reaction count |

## Example

```python
from mezon.models import ChannelMessageContent

# Get channel and send a message
channel = await client.channels.fetch("channel_id")
sent = await channel.send(content=ChannelMessageContent(t="Original"))

# Get the message object
message = channel.messages.get(sent.message_id)

# Reply to it
await message.reply(content=ChannelMessageContent(t="Reply!"))

# Update it
await message.update(content=ChannelMessageContent(t="Updated (edited)"))

# React to it
await message.react(emoji_id="emoji_123", emoji="thumbsup", count=1)
```

## In Message Handlers

```python
import json
from mezon.protobuf.api import api_pb2

async def handle_message(message_event: api_pb2.ChannelMessage):
    if message_event.sender_id == client.client_id:
        return

    content = json.loads(message_event.content)
    text = content.get("t", "")

    if text == "!ping":
        channel = await client.channels.fetch(message_event.channel_id)
        message = channel.messages.get(message_event.message_id)
        await message.reply(content=ChannelMessageContent(t="Pong!"))

client.on_channel_message(handle_message)
```
