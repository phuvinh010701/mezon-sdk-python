# TextChannel

`TextChannel` đại diện cho một channel có thể gửi message trong clan hoặc DM flow.

## Getting a channel

```python
channel = await client.channels.fetch(123456789)

clan = await client.clans.fetch(987654321)
await clan.load_channels()
channel = await clan.channels.fetch(123456789)
```

## Properties

| Property | Type | Description |
|---|---|---|
| `id` | `int | None` | Channel ID |
| `name` | `str | None` | Channel label |
| `channel_type` | `int | None` | Raw channel type |
| `is_private` | `bool` | Public/private state |
| `category_id` | `int` | Category ID if present |
| `category_name` | `str` | Category name if present |
| `parent_id` | `int` | Parent channel/thread grouping |
| `meeting_code` | `str` | Meeting code for voice-like flows |
| `messages` | `CacheManager[int, Message]` | Message fetch/cache helper |
| `clan` | `Clan` | Owning clan |

## `send(...) -> ChannelMessageAck`

```python
from mezon.models import ChannelMessageContent

ack = await channel.send(
    content=ChannelMessageContent(t="Hello"),
    mentions=None,
    attachments=None,
    mention_everyone=None,
    anonymous_message=None,
    topic_id=None,
    code=None,
)
```

Returns a `ChannelMessageAck` that includes the new `message_id`.

## `send_ephemeral(...)`

```python
await channel.send_ephemeral(
    receiver_ids=[123456789],
    content=ChannelMessageContent(text="Private response"),
)
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `receiver_ids` | `list[int]` | Recipients who can see the message |
| `content` | `Any` | Usually `ChannelMessageContent` |
| `reference_message_id` | `int | None` | Reference an existing message |
| `mentions` | `list[ApiMessageMention] | None` | Mentions |
| `attachments` | `list[ApiMessageAttachment] | None` | Attachments |
| `mention_everyone` | `bool | None` | Mention everyone |
| `anonymous_message` | `bool | None` | Anonymous flag |
| `topic_id` | `int | None` | Topic/thread target |
| `code` | `int` | Defaults to `TypeMessage.EPHEMERAL` |

## Working with messages

```python
message = await channel.messages.fetch(987654321)
await message.reply(content=ChannelMessageContent(t="Reply"))
await message.update(content=ChannelMessageContent(t="Edited"))
await message.react(emoji_id=1, emoji="thumbsup", count=1)
```

## Notes

- `channel.messages.fetch(...)` loads through the cache/database fetcher.
- `channel.messages.get(...)` only returns an in-memory cached value.
- Message and channel IDs in this SDK are integers, even if your app stores them as strings externally.
