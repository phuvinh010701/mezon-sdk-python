# Events

Event types available in the SDK.

## Using Events

```python
from mezon import Events

# Register handler
client.on(Events.CHANNEL_MESSAGE, handler)
```

## Event Reference

### Message Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.CHANNEL_MESSAGE` | New message in channel | `on_channel_message()` |
| `Events.MESSAGE_REACTION` | Reaction added/removed | - |
| `Events.MESSAGE_TYPING_EVENT` | User is typing | - |
| `Events.MESSAGE_BUTTON_CLICKED` | Button clicked | `on_message_button_clicked()` |

### Channel Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.CHANNEL_CREATED` | Channel created | `on_channel_created()` |
| `Events.CHANNEL_UPDATED` | Channel updated | `on_channel_updated()` |
| `Events.CHANNEL_DELETED` | Channel deleted | `on_channel_deleted()` |
| `Events.CHANNEL_PRESENCE_EVENT` | User presence in channel | - |

### User Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.USER_CHANNEL_ADDED` | User joined channel | `on_user_channel_added()` |
| `Events.USER_CHANNEL_REMOVED` | User left channel | `on_user_channel_removed()` |
| `Events.USER_CLAN_REMOVED` | User left clan | - |
| `Events.ADD_CLAN_USER` | User joined clan | `on_add_clan_user()` |

### Voice Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.VOICE_STARTED_EVENT` | Voice session started | - |
| `Events.VOICE_ENDED_EVENT` | Voice session ended | - |
| `Events.VOICE_JOINED_EVENT` | User joined voice | - |
| `Events.VOICE_LEAVED_EVENT` | User left voice | - |

### Clan Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.CLAN_UPDATED_EVENT` | Clan settings updated | - |
| `Events.CLAN_EVENT_CREATED` | Clan event created | `on_clan_event_created()` |

### Other Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.GIVE_COFFEE` | Coffee given | - |
| `Events.TOKEN_SEND` | Token sent | - |
| `Events.NOTIFICATION` | Notification received | `on_notification()` |

## Event Handlers

### Convenient Methods

```python
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2

# Message
async def on_message(msg: api_pb2.ChannelMessage):
    print(msg.content)

client.on_channel_message(on_message)

# Channel created
async def on_created(event: realtime_pb2.ChannelCreatedEvent):
    print(event.channel_id)

client.on_channel_created(on_created)

# User joined channel
async def on_joined(event: realtime_pb2.UserChannelAdded):
    print(f"{event.user_id} joined {event.channel_id}")

client.on_user_channel_added(on_joined)
```

### Generic Handler

```python
from mezon import Events

async def handler(data):
    print(f"Event: {data}")

client.on(Events.VOICE_STARTED_EVENT, handler)
client.on(Events.GIVE_COFFEE, handler)
```

## Handler Types

Both sync and async handlers are supported:

```python
# Async (recommended)
async def async_handler(data):
    await some_operation()

# Sync
def sync_handler(data):
    print(data)

client.on(Events.GIVE_COFFEE, async_handler)
client.on(Events.GIVE_COFFEE, sync_handler)
```

## Multiple Handlers

Register multiple handlers for the same event:

```python
async def log_message(msg):
    print(f"Log: {msg}")

async def process_message(msg):
    # Process...
    pass

client.on_channel_message(log_message)
client.on_channel_message(process_message)
```

Both handlers run for each message.
