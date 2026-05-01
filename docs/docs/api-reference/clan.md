# Clan

`Clan` represents a Mezon community/server and provides access to channels, voice presence, and role operations.

## Getting a clan

```python
clan = await client.clans.fetch(987654321)
print(clan.id, clan.name)
```

## Properties

| Property | Type | Description |
|---|---|---|
| `id` | `int` | Clan ID |
| `name` | `str` | Clan name |
| `welcome_channel_id` | `int` | Configured welcome channel |
| `channels` | `CacheManager[int, TextChannel]` | Clan-scoped channel cache |
| `client` | `MezonClient` | Owning client |
| `api_client` | `MezonApi` | Authenticated API client |
| `session_token` | `str` | Session token used for API calls |

## `load_channels() -> None`

```python
await clan.load_channels()
channel = await clan.channels.fetch(123456789)
```

Loads clan text channels via the API and populates both clan-local and global channel caches.

## `list_channel_voice_users(...) -> ApiVoiceChannelUserList`

```python
voice_users = await clan.list_channel_voice_users()
voice_users = await clan.list_channel_voice_users(
    channel_id=123456789,
    limit=100,
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `channel_id` | `int` | `0` | Optional specific channel |
| `channel_type` | `int | None` | voice default | Override the voice channel type filter |
| `limit` | `int` | `500` | Max results, must satisfy `0 < limit <= 500` |
| `state` | `int | None` | `None` | API state filter |
| `cursor` | `str | None` | `None` | Pagination cursor |

## `list_roles(...) -> ApiRoleListEventResponse`

```python
roles_response = await clan.list_roles(limit=100)
print(roles_response.roles)
```

## `update_role(role_id: int, request: dict) -> bool`

```python
await clan.update_role(
    role_id=123,
    request={"title": "Moderator"},
)
```

## Notes

- `Clan` does not eagerly load every channel on creation; call `load_channels()` when you want clan-scoped channel access.
- For simple channel access, `client.channels.fetch(...)` is often enough.
