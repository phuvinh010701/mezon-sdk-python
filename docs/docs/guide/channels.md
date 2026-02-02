# Channels

Working with channels in the Mezon SDK.

## Fetching Channels

### From Client

```python
# Fetch a channel by ID
channel = await client.channels.fetch("channel_id")

print(f"Channel: {channel.name}")
print(f"Type: {channel.channel_type}")
```

### From Clan

```python
# Get a clan
clan = await client.clans.get("clan_id")

# Load all channels in the clan
await clan.load_channels()

# Get a specific channel
channel = await clan.channels.get("channel_id")
```

## Channel Properties

```python
channel.id           # Channel ID
channel.name         # Channel name
channel.channel_type # Type of channel
channel.is_private   # Whether the channel is private
channel.messages     # Message cache manager
```

## Sending Messages

See the [Messaging Guide](messaging.md) for details.

```python
from mezon.models import ChannelMessageContent

# Send a message
await channel.send(content=ChannelMessageContent(t="Hello!"))

# Send ephemeral message
await channel.send_ephemeral(
    receiver_id="user_id",
    content=ChannelMessageContent(text="Private message")
)
```

## Accessing Messages

```python
# Get a message by ID
message = channel.messages.get("message_id")

# Reply to it
await message.reply(content=ChannelMessageContent(t="Reply!"))

# Update it
await message.update(content=ChannelMessageContent(t="Updated!"))
```

## Channel Types

The SDK supports various channel types:

```python
from mezon.constants import ChannelType

ChannelType.TEXT           # Text channel
ChannelType.VOICE          # Voice channel
ChannelType.DM             # Direct message
ChannelType.GROUP_DM       # Group direct message
ChannelType.CATEGORY       # Category (container for channels)
ChannelType.ANNOUNCEMENT   # Announcement channel
ChannelType.FORUM          # Forum channel
```

## DM Channels

### Send DM to User

```python
# Get user
user = await client.users.get("user_id")

# Send DM
await user.send_dm_message(
    content=ChannelMessageContent(t="Hello via DM!")
)
```

### Using Channel Manager

```python
# Get DM channel
dm_channel = await client.channel_manager.get_dm_channel("user_id")

# Send message
await dm_channel.send(content=ChannelMessageContent(t="Hello!"))
```

## Channel Events

Listen for channel-related events:

```python
from mezon.protobuf.rtapi import realtime_pb2

async def on_channel_created(event: realtime_pb2.ChannelCreatedEvent):
    print(f"New channel: {event.channel_id}")
    # Fetch the new channel
    channel = await client.channels.fetch(event.channel_id)

async def on_channel_updated(event: realtime_pb2.ChannelUpdatedEvent):
    print(f"Channel updated: {event.channel_id}")

async def on_channel_deleted(event: realtime_pb2.ChannelDeletedEvent):
    print(f"Channel deleted: {event.channel_id}")

client.on_channel_created(on_channel_created)
client.on_channel_updated(on_channel_updated)
client.on_channel_deleted(on_channel_deleted)
```

## User Presence in Channels

```python
async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(f"User {event.user_id} joined {event.channel_id}")

async def on_user_left(event: realtime_pb2.UserChannelRemoved):
    print(f"User {event.user_id} left {event.channel_id}")

client.on_user_channel_added(on_user_joined)
client.on_user_channel_removed(on_user_left)
```
