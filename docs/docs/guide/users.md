# Users

Working with users in the Mezon SDK.

## Accessing Users

```python
# Get a user from cache
user = await client.users.get("user_id")

print(f"User ID: {user.id}")
```

## Sending Direct Messages

Send a DM to a user:

```python
from mezon.models import ChannelMessageContent

user = await client.users.get("user_id")
await user.send_dm_message(
    content=ChannelMessageContent(t="Hello via DM!")
)
```

## Friends

### List Friends

```python
friends = await client.get_list_friends(
    limit=100,
    state=None,   # Optional filter
    cursor=None   # For pagination
)

for friend in friends:
    print(f"Friend: {friend}")
```

### Add Friend

```python
await client.add_friend(
    username="friend_username",
    user_id="friend_user_id"
)
```

### Accept Friend Request

```python
await client.accept_friend(user_id="user_id")
```

## User Events

### User Joined Channel

```python
from mezon.protobuf.rtapi import realtime_pb2

async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(f"User {event.user_id} joined channel {event.channel_id}")

client.on_user_channel_added(on_user_joined)
```

### User Left Channel

```python
async def on_user_left(event: realtime_pb2.UserChannelRemoved):
    print(f"User {event.user_id} left channel {event.channel_id}")

client.on_user_channel_removed(on_user_left)
```

### User Joined Clan

```python
async def on_user_joined_clan(event: realtime_pb2.AddClanUserEvent):
    print(f"User joined clan: {event.clan_id}")

client.on_add_clan_user(on_user_joined_clan)
```

### User Left Clan

```python
from mezon import Events

async def on_user_left_clan(event):
    print(f"User left clan")

client.on(Events.USER_CLAN_REMOVED, on_user_left_clan)
```

## Message Author

When handling messages, access the sender:

```python
async def handle_message(message: api_pb2.ChannelMessage):
    sender_id = message.sender_id

    # Check if it's the bot
    if sender_id == client.client_id:
        return

    # Get user object
    user = await client.users.get(sender_id)

    # Reply or DM
    channel = await client.channels.fetch(message.channel_id)
    await channel.send(
        content=ChannelMessageContent(t=f"Hello <@{sender_id}>!")
    )

client.on_channel_message(handle_message)
```
