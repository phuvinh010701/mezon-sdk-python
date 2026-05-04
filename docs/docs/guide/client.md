# Client Configuration

`MezonClient` là entry point chính để xác thực, khởi tạo managers, kết nối WebSocket, và đăng ký event handlers.

## Initialization

```python
import logging
from mezon import MezonClient

client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    host="gw.mezon.ai",
    port="443",
    use_ssl=True,
    timeout=7000,
    mmn_api_url="https://dong.mezon.ai/mmn-api/",
    zk_api_url="https://dong.mezon.ai/zk-api/",
    enable_logging=True,
    log_level=logging.INFO,
)
```

## Constructor parameters

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `client_id` | `str | int` | required | Bot/client ID |
| `api_key` | `str` | required | API key used for authentication |
| `host` | `str` | `"gw.mezon.ai"` | Login/API host |
| `port` | `str` | `"443"` | Login/API port |
| `use_ssl` | `bool` | `True` | Use TLS for HTTP and WebSocket URLs |
| `timeout` | `int` | `7000` | Request timeout in milliseconds |
| `mmn_api_url` | `str` | Mezon MMN default | Token transfer backend |
| `zk_api_url` | `str` | Mezon ZK default | ZK proof backend |
| `enable_logging` | `bool` | `False` | Enable SDK logging |
| `log_level` | `int` | `logging.INFO` | Python logging level |

## What `login()` does

```python
await client.login()
await client.login(enable_auto_reconnect=False)
```

`login()` performs these steps:

1. Authenticates through `SessionManager` and retrieves a session token.
2. Rebuilds API and socket managers from the session URLs returned by the server.
3. Connects the transport socket and joins clan chats / DM channels.
4. Initializes MMN and ZK clients for token sending.
5. Optionally enables automatic reconnect handlers.

## Common properties after login

| Property | Type | Description |
|---|---|---|
| `client.client_id` | `int` | Authenticated bot ID |
| `client.clans` | `CacheManager[int, Clan]` | Clan cache/fetch entrypoint |
| `client.channels` | `CacheManager[int, TextChannel]` | Channel cache/fetch entrypoint |
| `client.users` | `CacheManager[int, User]` | User cache/fetch entrypoint |
| `client.session_manager` | `SessionManager` | Holds the active `Session` |
| `client.socket_manager` | `SocketManager` | WebSocket/write operations |
| `client.channel_manager` | `ChannelManager` | DM/channel API helpers |
| `client.event_manager` | `EventManager` | Event registration and dispatch |
| `client.api_client` | `MezonApi` | Authenticated HTTP client |

## Accessing channels and clans

```python
channel = await client.channels.fetch(123456789)
clan = await client.clans.fetch(987654321)

await clan.load_channels()
channel = await clan.channels.fetch(123456789)
```

Use `fetch(...)` when the object may need to be loaded. Use `get(...)` only when you know it is already cached.

## Event registration

```python
from mezon.protobuf.api import api_pb2

async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

client.on_channel_message(handle_message)
```

For a complete list of helpers such as `on_channel_updated`, `on_token_send`, `on_quick_menu_event`, and `on_notification`, see [Event Handling](events.md).

## Reconnect behavior

By default, `login()` enables automatic reconnect:

```python
await client.login(enable_auto_reconnect=True)
```

When reconnecting, the client rebuilds its managers from a fresh session and reconnects the socket. Handlers registered on `client.event_manager` stay attached to the client instance.

## Shutdown

Close the socket when your process exits:

```python
import asyncio

async def main():
    await client.login()
    try:
        await asyncio.Event().wait()
    finally:
        await client.close_socket()
```

`close_socket()` shuts down the active WebSocket connection. If you build your own app lifecycle, prefer calling this method instead of reaching into lower-level socket objects.
