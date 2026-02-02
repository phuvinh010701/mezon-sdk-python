# Event Handling

The SDK provides an event-driven architecture for handling real-time events from Mezon.

## Registering Event Handlers

### Convenient Methods

The client provides convenient methods for common events:

```python
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2

# Message events
async def on_message(message: api_pb2.ChannelMessage):
    print(f"Message: {message.content}")

client.on_channel_message(on_message)

# Channel events
async def on_channel_created(event: realtime_pb2.ChannelCreatedEvent):
    print(f"Channel created: {event.channel_id}")

async def on_channel_updated(event: realtime_pb2.ChannelUpdatedEvent):
    print(f"Channel updated: {event.channel_id}")

async def on_channel_deleted(event: realtime_pb2.ChannelDeletedEvent):
    print(f"Channel deleted: {event.channel_id}")

client.on_channel_created(on_channel_created)
client.on_channel_updated(on_channel_updated)
client.on_channel_deleted(on_channel_deleted)

# User events
async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(f"User {event.user_id} joined channel")

async def on_user_left(event: realtime_pb2.UserChannelRemoved):
    print(f"User {event.user_id} left channel")

client.on_user_channel_added(on_user_joined)
client.on_user_channel_removed(on_user_left)

# Clan events
async def on_clan_user_added(event: realtime_pb2.AddClanUserEvent):
    print(f"User joined clan: {event.clan_id}")

client.on_add_clan_user(on_clan_user_added)

# Button clicks
async def on_button_click(event):
    print(f"Button clicked: {event}")

client.on_message_button_clicked(on_button_click)

# Notifications
async def on_notification(event):
    print(f"Notification: {event}")

client.on_notification(on_notification)
```

### Generic Event Handler

For any event, use the `on()` method:

```python
from mezon import Events

async def handler(data):
    print(f"Event received: {data}")

client.on(Events.VOICE_STARTED_EVENT, handler)
client.on(Events.GIVE_COFFEE, handler)
```

## Available Events

### Message Events

| Event | Description |
|-------|-------------|
| `Events.CHANNEL_MESSAGE` | New message in channel |
| `Events.MESSAGE_REACTION` | Reaction added/removed |
| `Events.MESSAGE_TYPING_EVENT` | User is typing |
| `Events.MESSAGE_BUTTON_CLICKED` | Button clicked |

### Channel Events

| Event | Description |
|-------|-------------|
| `Events.CHANNEL_CREATED` | Channel created |
| `Events.CHANNEL_UPDATED` | Channel updated |
| `Events.CHANNEL_DELETED` | Channel deleted |
| `Events.CHANNEL_PRESENCE_EVENT` | User presence in channel |

### User Events

| Event | Description |
|-------|-------------|
| `Events.USER_CHANNEL_ADDED` | User added to channel |
| `Events.USER_CHANNEL_REMOVED` | User removed from channel |
| `Events.USER_CLAN_REMOVED` | User removed from clan |
| `Events.ADD_CLAN_USER` | User joined clan |

### Voice Events

| Event | Description |
|-------|-------------|
| `Events.VOICE_STARTED_EVENT` | Voice session started |
| `Events.VOICE_ENDED_EVENT` | Voice session ended |
| `Events.VOICE_JOINED_EVENT` | User joined voice |
| `Events.VOICE_LEAVED_EVENT` | User left voice |

### Other Events

| Event | Description |
|-------|-------------|
| `Events.CLAN_UPDATED_EVENT` | Clan settings updated |
| `Events.CLAN_EVENT_CREATED` | Clan event created |
| `Events.GIVE_COFFEE` | Coffee given |
| `Events.TOKEN_SEND` | Token sent |
| `Events.NOTIFICATION` | Notification received |

## Sync vs Async Handlers

Both sync and async handlers are supported:

```python
# Async handler (recommended)
async def async_handler(data):
    await some_async_operation()
    print(f"Received: {data}")

# Sync handler
def sync_handler(data):
    print(f"Received: {data}")

client.on(Events.GIVE_COFFEE, async_handler)
client.on(Events.GIVE_COFFEE, sync_handler)
```

## Handler Execution

Handlers are executed in a fire-and-forget manner. Exceptions in handlers are logged but don't affect other handlers:

```python
async def handler(data):
    raise Exception("This won't crash the bot")

client.on_channel_message(handler)  # Error is logged, bot continues
```

## Multiple Handlers

You can register multiple handlers for the same event:

```python
async def log_message(message):
    print(f"Log: {message.content}")

async def process_message(message):
    # Process the message
    pass

client.on_channel_message(log_message)
client.on_channel_message(process_message)
```

Both handlers will be called for each message.
