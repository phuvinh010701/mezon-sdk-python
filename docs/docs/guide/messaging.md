# Sending Messages

SDK hỗ trợ gửi tin nhắn thường, reply, reaction, update, ephemeral message, và message kèm attachments/mentions.

## Send a basic message

```python
from mezon.models import ChannelMessageContent

channel = await client.channels.fetch(123456789)
ack = await channel.send(
    content=ChannelMessageContent(t="Hello, world!")
)

print(ack.message_id)
```

## `TextChannel.send(...)`

```python
ack = await channel.send(
    content=ChannelMessageContent(t="Hello @user"),
    mentions=[...],
    attachments=[...],
    mention_everyone=False,
    anonymous_message=False,
    topic_id=None,
    code=None,
)
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `content` | `ChannelMessageContent` | Message body |
| `mentions` | `list[ApiMessageMention] | None` | Mention payloads |
| `attachments` | `list[ApiMessageAttachment] | None` | Attachment metadata |
| `mention_everyone` | `bool | None` | Mention everyone in the channel |
| `anonymous_message` | `bool | None` | Send as anonymous message |
| `topic_id` | `int | None` | Thread/topic target |
| `code` | `int | None` | Override message type |

## Mentions

```python
from mezon.models import ApiMessageMention, ChannelMessageContent

await channel.send(
    content=ChannelMessageContent(t="Hello @alice"),
    mentions=[ApiMessageMention(user_id=123456789)]
)
```

`ApiMessageMention` also supports role mentions and positional metadata (`s`, `e`) when you need precise formatting.

## Attachments

```python
from mezon.models import ApiMessageAttachment, ChannelMessageContent

await channel.send(
    content=ChannelMessageContent(t="See attachment"),
    attachments=[
        ApiMessageAttachment(
            url="https://example.com/image.png",
            filename="image.png",
            filetype="image/png",
            size=1024,
        )
    ],
)
```

## Reply to a message

To reply, fetch the cached `Message` object and call `reply(...)`:

```python
message = await channel.messages.fetch(987654321)

await message.reply(
    content=ChannelMessageContent(t="Thanks for the context")
)
```

`Message.reply(...)` builds the reference payload for you.

## Update a message

```python
message = await channel.messages.fetch(987654321)

await message.update(
    content=ChannelMessageContent(t="Updated text")
)
```

## React to a message

```python
message = await channel.messages.fetch(987654321)

await message.react(
    emoji_id=1,
    emoji="thumbsup",
    count=1,
)
```

Set `action_delete=True` to remove a reaction.

## Ephemeral messages

Ephemeral messages are visible only to selected recipients.

```python
await channel.send_ephemeral(
    receiver_ids=[message.sender_id],
    content=ChannelMessageContent(text="Only you can see this"),
)
```

### `TextChannel.send_ephemeral(...)`

| Parameter | Type | Description |
|---|---|---|
| `receiver_ids` | `list[int]` | One or more recipients |
| `content` | `Any` | Message body, typically `ChannelMessageContent` |
| `reference_message_id` | `int | None` | Build an ephemeral reply to an existing message |
| `mentions` | `list[ApiMessageMention] | None` | Mention payloads |
| `attachments` | `list[ApiMessageAttachment] | None` | Attachments |
| `mention_everyone` | `bool | None` | Mention everyone |
| `anonymous_message` | `bool | None` | Anonymous flag |
| `topic_id` | `int | None` | Thread/topic target |
| `code` | `int` | Defaults to `TypeMessage.EPHEMERAL` |

## Legacy `client.send_message(...)`

The client still exposes a lower-level legacy method for direct socket writes:

```python
await client.send_message(
    clan_id=987654321,
    channel_id=123456789,
    mode=1,
    is_public=True,
    msg="Hello from legacy API",
)
```

Prefer `TextChannel.send(...)` unless you explicitly need the lower-level shape.

## Common handler pattern

```python
import json
from mezon.models import ChannelMessageContent
from mezon.protobuf.api import api_pb2

async def handle_message(event: api_pb2.ChannelMessage):
    if event.sender_id == client.client_id:
        return

    data = json.loads(event.content)
    if data.get("t") == "!ping":
        channel = await client.channels.fetch(event.channel_id)
        await channel.send(content=ChannelMessageContent(t="Pong!"))

client.on_channel_message(handle_message)
```
