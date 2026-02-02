# TextChannel

Represents a text channel on Mezon.

## Accessing Channels

```python
# From client
channel = await client.channels.fetch("channel_id")

# From clan
clan = await client.clans.get("clan_id")
await clan.load_channels()
channel = await clan.channels.get("channel_id")
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Channel ID |
| `name` | `str` | Channel name |
| `channel_type` | `int` | Type of channel |
| `is_private` | `bool` | Whether channel is private |
| `messages` | `MessageManager` | Message cache manager |

## Methods

### `send(...) -> ChannelMessageAck`

Send a message to the channel.

```python
from mezon.models import ChannelMessageContent, ApiMessageMention, ApiMessageAttachment

result = await channel.send(
    content=ChannelMessageContent(t="Hello!"),
    mentions=None,      # Optional[List[ApiMessageMention]]
    attachments=None,   # Optional[List[ApiMessageAttachment]]
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `content` | `ChannelMessageContent` | Message content |
| `mentions` | `List[ApiMessageMention]` | User mentions |
| `attachments` | `List[ApiMessageAttachment]` | Attachments |

**Returns:** `ChannelMessageAck` with `message_id`

### `send_ephemeral(...) -> None`

Send an ephemeral message (only visible to one user).

```python
await channel.send_ephemeral(
    receiver_id="user_id",
    content=ChannelMessageContent(text="Only you see this!")
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `receiver_id` | `str` | User who will see the message |
| `content` | `ChannelMessageContent` | Message content |

### `messages.get(message_id: str) -> Message`

Get a message object by ID.

```python
message = channel.messages.get("message_id")

# Then use message methods
await message.reply(content=ChannelMessageContent(t="Reply!"))
await message.update(content=ChannelMessageContent(t="Updated!"))
```

## Example

```python
from mezon.models import ChannelMessageContent, ApiMessageMention

# Fetch channel
channel = await client.channels.fetch("channel_id")

# Send message
sent = await channel.send(
    content=ChannelMessageContent(t="Hello @user!"),
    mentions=[ApiMessageMention(user_id="user_id")]
)

print(f"Sent message: {sent.message_id}")

# Send ephemeral
await channel.send_ephemeral(
    receiver_id="user_id",
    content=ChannelMessageContent(text="Private message!")
)

# Get and reply to a message
message = channel.messages.get(sent.message_id)
await message.reply(content=ChannelMessageContent(t="Self-reply!"))
```

## Channel Types

```python
from mezon.constants import ChannelType

ChannelType.TEXT           # Text channel
ChannelType.VOICE          # Voice channel
ChannelType.DM             # Direct message
ChannelType.GROUP_DM       # Group DM
ChannelType.CATEGORY       # Category
ChannelType.ANNOUNCEMENT   # Announcement
ChannelType.FORUM          # Forum
```
