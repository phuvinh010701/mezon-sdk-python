# User

`User` represents a Mezon user and provides helpers for DM messaging and DM channel creation.

## Getting a user

```python
user = await client.users.fetch(123456789)
print(user.id, user.username)
```

## Properties

| Property | Type | Description |
|---|---|---|
| `id` | `int` | User ID |
| `username` | `str | None` | Username |
| `display_name` | `str | None` | Display name |
| `avatar` | `str | None` | Avatar URL |
| `clan_nick` | `str | None` | Clan nickname |
| `clan_avatar` | `str | None` | Clan avatar URL |
| `dm_channel_id` | `int | None` | Existing DM channel ID |

## `create_dm_channel() -> ApiChannelDescription`

```python
channel_desc = await user.create_dm_channel()
print(channel_desc.channel_id)
```

Creates a DM channel if one does not already exist.

## `send_dm_message(...) -> ChannelMessageAck`

```python
from mezon.models import ChannelMessageContent

ack = await user.send_dm_message(
    content=ChannelMessageContent(t="Hello via DM"),
)
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `content` | `ChannelMessageContent` | Message payload |
| `code` | `int` | Message type, defaults to chat |
| `attachments` | `list[ApiMessageAttachment] | None` | Optional attachments |

If `dm_channel_id` is missing, the SDK creates the DM channel before sending.
