# Clans

`Clan` represents a Mezon community/server and exposes channel loading, voice presence, and role helpers.

## Fetch a clan

```python
clan = await client.clans.fetch(987654321)
print(clan.id, clan.name)
```

## Load clan channels

```python
await clan.load_channels()
channel = await clan.channels.fetch(123456789)
```

`load_channels()` populates the clan-local channel cache from the API.

## Voice users

```python
voice_users = await clan.list_channel_voice_users()
voice_users = await clan.list_channel_voice_users(
    channel_id=123456789,
    limit=100,
)
```

`limit` must satisfy `0 < limit <= 500`.

## Roles

```python
roles_response = await clan.list_roles(limit=100)
print(roles_response.roles)

await clan.update_role(
    role_id=123,
    request={"title": "Moderator"},
)
```

## Clan-related events

```python
from mezon import Events
from mezon.models import ChannelMessageContent
from mezon.protobuf.rtapi import realtime_pb2

async def on_user_joined_clan(event: realtime_pb2.AddClanUserEvent):
    print(event.clan_id, event.user_id)

async def on_clan_updated(event):
    print("Clan updated")

async def on_clan_event(event):
    print("Clan event created")

client.on_add_clan_user(on_user_joined_clan)
client.on(Events.CLAN_UPDATED_EVENT, on_clan_updated)
client.on_clan_event_created(on_clan_event)
```
