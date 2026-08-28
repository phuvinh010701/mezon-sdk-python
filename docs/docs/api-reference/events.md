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
| `Events.MESSAGE_REACTION` | Reaction added/removed | `on_message_reaction()` |
| `Events.MESSAGE_BUTTON_CLICKED` | Button clicked | `on_message_button_clicked()` |

### Channel Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.CHANNEL_CREATED` | Channel created | `on_channel_created()` |
| `Events.CHANNEL_UPDATED` | Channel updated | `on_channel_updated()` |
| `Events.CHANNEL_DELETED` | Channel deleted | `on_channel_deleted()` |

### User Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.USER_CHANNEL_ADDED` | User joined channel | `on_user_channel_added()` |
| `Events.USER_CHANNEL_REMOVED` | User left channel | `on_channel_user_removed()` |
| `Events.USER_CLAN_REMOVED` | User left clan | `on_user_clan_removed()` |
| `Events.ADD_CLAN_USER` | User joined clan | `on_add_clan_user()` |

### Voice Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.VOICE_STARTED_EVENT` | Voice session started | `on_voice_started_event()` |
| `Events.VOICE_ENDED_EVENT` | Voice session ended | `on_voice_ended_event()` |
| `Events.VOICE_JOINED_EVENT` | User joined voice | `on_voice_joined_event()` |
| `Events.VOICE_LEAVED_EVENT` | User left voice | `on_voice_leaved_event()` |

### Clan Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.CLAN_EVENT_CREATED` | Clan event created | `on_clan_event_created()` |

### AI Agent Events

See [AI Agent (SSE)](../guide/ai-agent.md) for setup details.

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.AI_AGENT_ENABLE` | AI agent enabled for the bot | `on_ai_agent_enabled_event()` |
| `Events.AI_AGENT_SESSION_STARTED` | AI agent session started | `on_ai_agent_session_started()` |
| `Events.AI_AGENT_SESSION_ENDED` | AI agent session ended | `on_ai_agent_session_ended()` |
| `Events.AI_AGENT_SESSION_SUMMARY_DONE` | AI agent session summary ready | `on_ai_agent_session_summary_done()` |

### Other Events

| Event | Description | Convenient Method |
|-------|-------------|-------------------|
| `Events.GIVE_COFFEE` | Coffee given | `on_give_coffee()` |
| `Events.TOKEN_SEND` | Token sent | `on_token_send()` |
| `Events.NOTIFICATIONS` | Notification received | `on_notification()` |
| `Events.QUICK_MENU` | Quick menu action triggered | `on_quick_menu_event()` |
| `Events.ROLE_EVENT` | Clan role created | `on_role_event()` |
| `Events.ROLE_ASSIGN` | Role assigned to a user | `on_role_assign()` |
| `Events.DROPDOWN_BOX_SELECTED` | Dropdown option selected | `on_dropdown_box_selected()` |
| `Events.WEBRTC_SIGNALING_FWD` | WebRTC signaling forwarded | `on_webrtc_signaling_fwd()` |
| `Events.STREAMING_JOINED_EVENT` | User joined a stream room | `on_streaming_joined_event()` |
| `Events.STREAMING_LEAVED_EVENT` | User left a stream room | `on_streaming_leaved_event()` |

## Event Handlers

### Convenient Methods

```python
from mezon.models import ChannelMessage
from mezon.protobuf.rtapi import realtime_pb2


# Message
async def on_message(msg: ChannelMessage):
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
