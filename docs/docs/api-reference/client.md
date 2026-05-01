# MezonClient

`MezonClient` is the main SDK entry point for authentication, real-time connectivity, token sending, and event registration.

## Constructor

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
    log_level=logging.INFO,
    enable_logging=False,
)
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `client_id` | `str | int` | required | Bot ID |
| `api_key` | `str` | required | API key |
| `host` | `str` | `"gw.mezon.ai"` | Login/API host |
| `port` | `str` | `"443"` | Login/API port |
| `use_ssl` | `bool` | `True` | TLS for HTTP/WebSocket URLs |
| `timeout` | `int` | `7000` | Timeout in milliseconds |
| `mmn_api_url` | `str` | Mezon default | MMN API endpoint |
| `zk_api_url` | `str` | Mezon default | ZK API endpoint |
| `log_level` | `int` | `logging.INFO` | Logging level |
| `enable_logging` | `bool` | `False` | Enable SDK logging |

## Main properties

| Property | Type | Description |
|---|---|---|
| `client_id` | `int` | Authenticated bot ID |
| `clans` | `CacheManager[int, Clan]` | Clan fetch/cache layer |
| `channels` | `CacheManager[int, TextChannel]` | Channel fetch/cache layer |
| `users` | `CacheManager[int, User]` | User fetch/cache layer |
| `event_manager` | `EventManager` | Event registration/dispatch |
| `message_db` | `MessageDB` | SQLite-backed message cache |
| `session_manager` | `SessionManager` | Active session holder |
| `socket_manager` | `SocketManager` | WebSocket write and connect operations |
| `channel_manager` | `ChannelManager` | Channel-related API helpers |
| `api_client` | `MezonApi` | Authenticated HTTP API client |

## Authentication lifecycle

### `login(enable_auto_reconnect: bool = True) -> None`

```python
await client.login()
await client.login(enable_auto_reconnect=False)
```

Authenticates, initializes managers from the returned session URLs, connects the socket, and prepares MMN/ZK support.

### `get_session() -> Session`

```python
session = await client.get_session()
print(session.token)
```

Fetches a fresh session without fully logging the client in.

### `close_socket() -> None`

```python
await client.close_socket()
```

Closes the active WebSocket connection.

## Messaging methods

### `send_message(...)`

Legacy direct send helper:

```python
await client.send_message(
    clan_id=987654321,
    channel_id=123456789,
    mode=1,
    is_public=True,
    msg="Hello from legacy API",
)
```

Prefer `TextChannel.send(...)` for most applications.

### `send_token(token_event: ApiSentTokenRequest) -> AddTxResponse`

```python
from mezon.models import ApiSentTokenRequest

result = await client.send_token(
    ApiSentTokenRequest(
        receiver_id=123456789,
        amount=10,
        note="Thanks!",
    )
)
```

## Friend-related helpers

### `get_list_friends(limit: int, state: int = None, cursor: str = None)`

```python
friends = await client.get_list_friends(limit=100)
```

### `accept_friend(user_id: str) -> None`

```python
await client.accept_friend(user_id="123456789")
```

### `add_friend(username: str, user_id: str) -> None`

```python
await client.add_friend(username="alice", user_id="123456789")
```

## Event helper methods

The client exposes convenience registration methods on top of `EventManager`, including:

- `on_channel_message(...)`
- `on_channel_created(...)`
- `on_channel_updated(...)`
- `on_channel_deleted(...)`
- `on_token_send(...)`
- `on_message_reaction(...)`
- `on_channel_user_removed(...)`
- `on_user_channel_added(...)`
- `on_user_clan_removed(...)`
- `on_give_coffee(...)`
- `on_role_event(...)`
- `on_clan_event_created(...)`
- `on_message_button_clicked(...)`
- `on_streaming_joined_event(...)`
- `on_streaming_leaved_event(...)`
- `on_dropdown_box_selected(...)`
- `on_webrtc_signaling_fwd(...)`
- `on_voice_started_event(...)`
- `on_voice_ended_event(...)`
- `on_voice_joined_event(...)`
- `on_voice_leaved_event(...)`
- `on_quick_menu_event(...)`
- `on_ai_agent_enabled_event(...)`
- `on_ai_agent_session_started(...)`
- `on_ai_agent_session_ended(...)`
- `on_ai_agent_session_summary_done(...)`
- `on_role_assign(...)`
- `on_notification(...)`
- `on_add_clan_user(...)`

For usage examples, see [Event Handling](../guide/events.md).
