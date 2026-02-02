# MezonClient

The main entry point for interacting with the Mezon platform.

## Constructor

```python
from mezon import MezonClient

client = MezonClient(
    client_id: str,
    api_key: str,
    host: str = "gw.mezon.ai",
    port: str = "443",
    use_ssl: bool = True,
    timeout: int = 7000,
    enable_logging: bool = False,
    log_level: int = logging.INFO,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client_id` | `str` | Required | Your bot's client ID |
| `api_key` | `str` | Required | Your API key |
| `host` | `str` | `"gw.mezon.ai"` | API host |
| `port` | `str` | `"443"` | API port |
| `use_ssl` | `bool` | `True` | Use SSL connection |
| `timeout` | `int` | `7000` | Request timeout in ms |
| `enable_logging` | `bool` | `False` | Enable SDK logging |
| `log_level` | `int` | `logging.INFO` | Python logging level |

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `client_id` | `str` | The bot's client ID |
| `channels` | `CacheManager[int, TextChannel]` | Channel manager |
| `clans` | `CacheManager[int, Clan]` | Clan manager |
| `users` | `CacheManager[int, User]` | User manager |
| `session_manager` | `SessionManager` | Session management |
| `socket_manager` | `SocketManager` | WebSocket management |
| `channel_manager` | `ChannelManager` | Channel management |
| `event_manager` | `EventManager` | Event management |
| `api_client` | `MezonApi` | HTTP API client |

## Methods

### Authentication

#### `login(enable_auto_reconnect: bool = True) -> None`

Authenticate and connect to Mezon.

```python
await client.login()
await client.login(enable_auto_reconnect=False)
```

#### `close_socket() -> None`

Close the WebSocket connection.

```python
await client.close_socket()
```

### Messaging

#### `send_message(...) -> ChannelMessageAck`

Send a message to a channel (legacy method).

```python
from mezon.models import ApiMessageMention, ApiMessageAttachment, ApiMessageRef

result = await client.send_message(
    clan_id="clan_id",
    channel_id="channel_id",
    mode=1,
    is_public=True,
    msg="Hello!",
    mentions=None,      # Optional[List[ApiMessageMention]]
    attachments=None,   # Optional[List[ApiMessageAttachment]]
    ref=None,           # Optional[List[ApiMessageRef]]
)
```

#### `send_token(request: ApiSentTokenRequest) -> AddTxResponse`

Send tokens to a user.

```python
from mezon.models import ApiSentTokenRequest

result = await client.send_token(
    ApiSentTokenRequest(
        receiver_id="user_id",
        amount=10,
        note="Thanks!",
    )
)
```

### Friends

#### `get_list_friends(limit: int, state: int = None, cursor: str = None) -> List`

Get list of friends.

```python
friends = await client.get_list_friends(limit=100)
```

#### `accept_friend(user_id: str) -> None`

Accept a friend request.

```python
await client.accept_friend(user_id="user_id")
```

#### `add_friend(username: str, user_id: str) -> None`

Add a friend.

```python
await client.add_friend(username="username", user_id="user_id")
```

### Event Handlers

#### `on(event_name: str, handler: Callable) -> None`

Register a generic event handler.

```python
from mezon import Events

async def handler(data):
    print(data)

client.on(Events.VOICE_STARTED_EVENT, handler)
```

#### `on_channel_message(handler: Callable) -> None`

Handle channel messages.

```python
async def handler(message: api_pb2.ChannelMessage):
    print(message.content)

client.on_channel_message(handler)
```

#### `on_channel_created(handler: Callable) -> None`

Handle channel creation.

```python
async def handler(event: realtime_pb2.ChannelCreatedEvent):
    print(event.channel_id)

client.on_channel_created(handler)
```

#### `on_channel_updated(handler: Callable) -> None`

Handle channel updates.

#### `on_channel_deleted(handler: Callable) -> None`

Handle channel deletion.

#### `on_user_channel_added(handler: Callable) -> None`

Handle user joining channel.

#### `on_user_channel_removed(handler: Callable) -> None`

Handle user leaving channel.

#### `on_add_clan_user(handler: Callable) -> None`

Handle user joining clan.

#### `on_clan_event_created(handler: Callable) -> None`

Handle clan event creation.

#### `on_message_button_clicked(handler: Callable) -> None`

Handle message button clicks.

#### `on_notification(handler: Callable) -> None`

Handle notifications.
