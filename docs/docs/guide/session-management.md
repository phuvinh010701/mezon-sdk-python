# Session Management

Session handling in the SDK is centered around `MezonClient.get_session()`, `SessionManager`, and the active `Session` attached after `login()`.

## Authentication flow

When you call:

```python
await client.login()
```

The SDK:

1. Calls `client.get_session()`.
2. Uses `SessionManager.authenticate(...)` to call the Mezon auth API.
3. Receives a session payload containing token, refresh token, API URL, and WebSocket URL.
4. Rebuilds `MezonApi` and `SocketManager` using those returned URLs.

## Getting a fresh session manually

```python
session = await client.get_session()
print(session.token)
print(session.api_url)
print(session.ws_url)
```

This is useful if you need to inspect the session lifecycle without fully connecting the bot.

## Accessing the active session after login

```python
await client.login()
session = client.session_manager.get_session()
```

The active session is stored on `client.session_manager` after manager initialization completes.

## What is in the session

The Pydantic `ApiSession` model includes fields such as:

- `token`
- `refresh_token`
- `user_id`
- `api_url`
- `id_token`
- `ws_url`

## Reconnect behavior

With `enable_auto_reconnect=True` (the default), the client can request a new session and rebuild transport state after a disconnect.

## Practical guidance

- Treat the session as runtime state owned by the client.
- Prefer `client.login()` over manually wiring `SessionManager` unless you are extending the SDK internals.
- Use `client.close_socket()` during shutdown so the active realtime session closes cleanly.
