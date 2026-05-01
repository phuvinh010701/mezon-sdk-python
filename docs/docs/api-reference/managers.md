# Managers

Các manager trong SDK chịu trách nhiệm cho authentication state, WebSocket transport, channel operations, và event dispatch.

## SessionManager

Source: `mezon/managers/session.py`

### Responsibility

- Authenticate with `MezonApi`
- Hold the active `Session`

### Main methods

```python
session = client.session_manager.get_session()
```

```python
session = await client.session_manager.authenticate(client_id, api_key)
```

`authenticate(...)` calls the Mezon auth API and returns a `Session` object.

## SocketManager

Source: `mezon/managers/socket.py`

### Responsibility

- Own the low-level socket adapter
- Connect/reconnect using authenticated sessions
- Join clans and DM channels after login
- Write chat, ephemeral, update, delete, and reaction payloads

### Main methods

```python
await client.socket_manager.connect(session)
await client.socket_manager.connect_socket(session.token)
```

```python
await client.socket_manager.write_chat_message(...)
await client.socket_manager.write_ephemeral_message(...)
await client.socket_manager.update_chat_message(...)
await client.socket_manager.write_message_reaction(...)
```

## ChannelManager

Source: `mezon/managers/channel.py`

### Responsibility

- Channel-related API helpers
- DM channel creation and initialization

You usually interact with it indirectly through `client.channels`, `client.users`, or `User.send_dm_message(...)`.

## EventManager

Source: `mezon/managers/event.py`

### Responsibility

- Register handlers with `on(...)`
- Dispatch incoming realtime events to user and default handlers

In day-to-day usage you normally call convenience methods on `MezonClient`, for example:

```python
client.on_channel_message(handler)
client.on_message_button_clicked(handler)
client.on_notification(handler)
```

## CacheManager

Source: `mezon/managers/cache.py`

### Responsibility

- In-memory cache with optional async fetcher
- Used by `client.clans`, `client.channels`, `client.users`, and `channel.messages`

### Usage pattern

```python
channel = await client.channels.fetch(123456789)
message = await channel.messages.fetch(987654321)
```

Use `fetch(...)` when loading may be required. Use `get(...)` only when you expect the object to already be present in memory.
