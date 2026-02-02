# Clan

Represents a clan (server/community) on Mezon.

## Accessing Clans

```python
clan = await client.clans.get("clan_id")
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Clan ID |
| `name` | `str` | Clan name |
| `channels` | `CacheManager` | Channel manager for the clan |
| `users` | `CacheManager` | User manager for the clan |

## Methods

### `load_channels() -> None`

Load all channels in the clan.

```python
await clan.load_channels()
```

### `list_channel_voice_users(...) -> ApiVoiceChannelUserList`

List users in voice channels.

```python
voice_users = await clan.list_channel_voice_users(
    channel_id=None,      # Optional: specific channel
    channel_type=None,    # Optional: channel type filter
    limit=100,            # Optional: max results
    state=None,           # Optional: state filter
    cursor=None,          # Optional: pagination cursor
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channel_id` | `str` | `None` | Specific channel to query |
| `channel_type` | `int` | `None` | Channel type filter |
| `limit` | `int` | `100` | Maximum results |
| `state` | `int` | `None` | State filter |
| `cursor` | `str` | `None` | Pagination cursor |

**Returns:** `ApiVoiceChannelUserList`

### `list_roles(...) -> List`

List all roles in the clan.

```python
roles = await clan.list_roles(
    limit=100,
    state=None,
    cursor=None,
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `100` | Maximum results |
| `state` | `int` | `None` | State filter |
| `cursor` | `str` | `None` | Pagination cursor |

### `update_role(role_id: str, request: dict) -> None`

Update a role.

```python
await clan.update_role(
    role_id="role_id",
    request={
        "title": "New Role Name",
        "permissions": ["SEND_MESSAGE", "READ_MESSAGES"],
    }
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `role_id` | `str` | Role ID to update |
| `request` | `dict` | Update data |

## Example

```python
# Get clan
clan = await client.clans.get("clan_id")

# Load channels
await clan.load_channels()

# Access a channel
channel = await clan.channels.get("channel_id")

# List voice users
voice_users = await clan.list_channel_voice_users()
for user in voice_users:
    print(f"In voice: {user}")

# List and update roles
roles = await clan.list_roles()
for role in roles:
    print(f"Role: {role.title}")

await clan.update_role(
    role_id=roles[0].id,
    request={"title": "Updated Role"}
)
```
