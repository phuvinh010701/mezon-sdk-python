# Message

`Message` wraps a cached channel message and exposes reply, edit, react, and delete operations.

## Getting a message

```python
channel = await client.channels.fetch(123456789)
message = await channel.messages.fetch(987654321)
```

## Properties

| Property | Type | Description |
|---|---|---|
| `id` | `int` | Message ID |
| `sender_id` | `int` | Author ID |
| `content` | `ChannelMessageContent` | Parsed message content |
| `mentions` | `list[ApiMessageMention] | None` | Mention payloads |
| `attachments` | `list[ApiMessageAttachment] | None` | Attachments |
| `reactions` | `list[ApiMessageReaction] | None` | Current reactions |
| `references` | `list[ApiMessageRef] | None` | Reply/reference metadata |
| `topic_id` | `int | None` | Topic/thread ID |
| `channel` | `TextChannel` | Parent channel |

## `reply(...) -> ChannelMessageAck`

```python
from mezon.models import ChannelMessageContent

ack = await message.reply(
    content=ChannelMessageContent(t="Thanks for the update"),
    mentions=None,
    attachments=None,
    mention_everyone=None,
    anonymous_message=None,
    topic_id=None,
    code=None,
)
```

The SDK constructs the `ApiMessageRef` payload automatically from the current message.

## `update(...) -> ChannelMessageAck`

```python
await message.update(
    content=ChannelMessageContent(t="Edited content")
)
```

## `react(...)`

```python
await message.react(
    emoji_id=1,
    emoji="thumbsup",
    count=1,
)
```

Optional arguments:

- `id`: reaction payload ID, defaults to `0`
- `action_delete`: set to `True` to remove the reaction

## `delete(...)`

```python
await message.delete()
```

Deletes the message from the underlying channel.

## Notes

- `channel.messages.fetch(...)` is safer than `get(...)` unless you know the message is already cached in memory.
- Reply/update/delete all use the parent channel metadata (`clan_id`, `channel_id`, `topic_id`, visibility) automatically.
