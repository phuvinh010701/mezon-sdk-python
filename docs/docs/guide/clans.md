# Clans

Working with clans (servers/communities) in the Mezon SDK.

## Accessing Clans

```python
# Get a clan by ID
clan = await client.clans.get("clan_id")

print(f"Clan: {clan.name}")
print(f"ID: {clan.id}")
```

## Clan Properties

```python
clan.id        # Clan ID
clan.name      # Clan name
clan.channels  # Channel manager for the clan
clan.users     # User manager for the clan
```

## Loading Channels

Load all channels in a clan:

```python
# Load channels
await clan.load_channels()

# Access a channel
channel = await clan.channels.get("channel_id")
```

## Voice Users

List users in voice channels:

```python
# List all voice users in the clan
voice_users = await clan.list_channel_voice_users()

# With specific channel
voice_users = await clan.list_channel_voice_users(
    channel_id="channel_id",
    limit=100
)

for user in voice_users:
    print(f"User in voice: {user}")
```

## Roles

### List Roles

```python
roles = await clan.list_roles()

for role in roles:
    print(f"Role: {role.title}")
```

### Update Role

```python
await clan.update_role(
    role_id="role_id",
    request={
        "title": "New Role Name",
        "permissions": ["SEND_MESSAGE", "READ_MESSAGES"]
    }
)
```

## Clan Events

Listen for clan-related events:

```python
from mezon.protobuf.rtapi import realtime_pb2

# User joined clan
async def on_user_joined_clan(event: realtime_pb2.AddClanUserEvent):
    print(f"User joined clan: {event.clan_id}")
    # Welcome the user
    channel = await client.channels.fetch("welcome_channel_id")
    await channel.send(
        content=ChannelMessageContent(t=f"Welcome <@{event.user_id}>!")
    )

client.on_add_clan_user(on_user_joined_clan)

# Clan updated
async def on_clan_updated(event):
    print(f"Clan settings changed")

client.on(Events.CLAN_UPDATED_EVENT, on_clan_updated)

# Clan event created
async def on_clan_event(event):
    print(f"New clan event created")

client.on_clan_event_created(on_clan_event)
```

## User Clan Removal

```python
async def on_user_left_clan(event: realtime_pb2.UserClanRemovedEvent):
    print(f"User {event.user_id} left clan {event.clan_id}")

client.on(Events.USER_CLAN_REMOVED, on_user_left_clan)
```
