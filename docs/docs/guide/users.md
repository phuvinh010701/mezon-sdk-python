# Users

`User` đại diện cho người dùng Mezon và chủ yếu hữu ích cho DM flows hoặc khi bạn cần thông tin sender đã được cache.

## Fetching a user

```python
user = await client.users.fetch(123456789)
print(user.id, user.username, user.display_name)
```

Use `fetch(...)` when the user may need to be resolved by the SDK. `get(...)` only works for already-cached users.

## Send a DM

```python
from mezon.models import ChannelMessageContent

user = await client.users.fetch(123456789)
await user.send_dm_message(
    content=ChannelMessageContent(t="Hello via DM")
)
```

If the user does not already have a DM channel, the SDK creates one first.

## Friend helpers on the client

```python
friends = await client.get_list_friends(limit=100)
await client.add_friend(username="alice", user_id="123456789")
await client.accept_friend(user_id="123456789")
```

## User-related events

```python
from mezon.protobuf.rtapi import realtime_pb2

async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(event.user_id, event.channel_id)

async def on_user_left(event: realtime_pb2.UserChannelRemoved):
    print(event.user_id, event.channel_id)

async def on_user_joined_clan(event: realtime_pb2.AddClanUserEvent):
    print(event.user_id, event.clan_id)

client.on_user_channel_added(on_user_joined)
client.on_channel_user_removed(on_user_left)
client.on_add_clan_user(on_user_joined_clan)
```

## Working with message senders

```python
from mezon.models import ChannelMessageContent
from mezon.protobuf.api import api_pb2

async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

    user = await client.users.fetch(message.sender_id)
    channel = await client.channels.fetch(message.channel_id)
    await channel.send(
        content=ChannelMessageContent(t=f"Hello {user.display_name or user.username}!")
    )

client.on_channel_message(handle_message)
```
