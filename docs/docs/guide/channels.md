# Channels

`TextChannel` là abstraction chính để gửi message, reply, reaction, và ephemeral message trong SDK.

## Fetching channels

### From the global client cache

```python
channel = await client.channels.fetch(123456789)
print(channel.name)
```

### From a clan

```python
clan = await client.clans.fetch(987654321)
await clan.load_channels()
channel = await clan.channels.fetch(123456789)
```

Use `fetch(...)` if the object may need to be loaded. Use `get(...)` only when you are certain the item is already cached.

## Common properties

| Property | Type | Description |
|---|---|---|
| `channel.id` | `int | None` | Channel ID |
| `channel.name` | `str | None` | Channel label |
| `channel.channel_type` | `int | None` | Raw Mezon channel type |
| `channel.is_private` | `bool` | Public/private state |
| `channel.category_id` | `int` | Parent category ID |
| `channel.parent_id` | `int` | Parent channel/thread grouping |
| `channel.messages` | `CacheManager[int, Message]` | Message cache/fetch entrypoint |

## Sending messages

```python
from mezon.models import ChannelMessageContent

await channel.send(content=ChannelMessageContent(t="Hello"))
```

For the full parameter list, see [Sending Messages](messaging.md).

## Sending ephemeral messages

```python
await channel.send_ephemeral(
    receiver_ids=[123456789],
    content=ChannelMessageContent(text="Private response"),
)
```

`send_ephemeral(...)` accepts a list of recipients, not a single `receiver_id` argument.

## Working with cached messages

```python
message = await channel.messages.fetch(987654321)
await message.reply(content=ChannelMessageContent(t="Reply"))
await message.update(content=ChannelMessageContent(t="Edited"))
await message.react(emoji_id=1, emoji="thumbsup", count=1)
```

`channel.messages.fetch(...)` loads through the message cache/database layer. `get(...)` only works if the message is already cached in memory.

## DM flows

The `User` structure is the easiest way to open and send DMs:

```python
user = await client.users.fetch(123456789)
await user.send_dm_message(content=ChannelMessageContent(t="Hello via DM"))
```

If the user does not yet have a DM channel, the SDK creates one automatically before sending.

## Channel events

```python
from mezon.protobuf.rtapi import realtime_pb2

async def on_channel_created(event: realtime_pb2.ChannelCreatedEvent):
    print(event.channel_id)

async def on_channel_updated(event: realtime_pb2.ChannelUpdatedEvent):
    print(event.channel_id)

async def on_channel_deleted(event: realtime_pb2.ChannelDeletedEvent):
    print(event.channel_id)

client.on_channel_created(on_channel_created)
client.on_channel_updated(on_channel_updated)
client.on_channel_deleted(on_channel_deleted)
```

## Presence-related user events

```python
async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(event.user_id, event.channel_id)

async def on_user_left(event: realtime_pb2.UserChannelRemoved):
    print(event.user_id, event.channel_id)

client.on_user_channel_added(on_user_joined)
client.on_channel_user_removed(on_user_left)
```
