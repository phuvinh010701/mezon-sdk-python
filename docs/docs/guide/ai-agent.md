# AI Agent (SSE)

The SDK can stream AI agent room/session lifecycle events over Server-Sent Events (SSE), in addition to the WebSocket `AI_AGENT_ENABLE` event that arrives over the regular socket connection.

## Configuring the SSE endpoint

Pass `agent_event_url` when constructing the client:

```python
from mezon import MezonClient

client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    agent_event_url="https://agent.mezon.ai",
)
```

If `agent_event_url` is not set, `connect_ai_agent_sse()` raises `ValueError` when called.

## Connecting and disconnecting

```python
await client.login()
await client.connect_ai_agent_sse()  # defaults to path "api/sse/metadata"

# later
await client.disconnect_ai_agent_sse()
```

`connect_ai_agent_sse(path="api/sse/metadata")` opens a background SSE stream authenticated with `client.client_id` and `client.api_key`. Calling it again while already connected is a no-op. `disconnect_ai_agent_sse()` cancels the stream and closes the underlying HTTP session/response.

## Handling events

```python
from mezon.models import (
    AIAgentSessionEndedEvent,
    AIAgentSessionStartedEvent,
    AIAgentSessionSummaryDoneEvent,
)


async def on_enabled(event):
    print("AI agent enabled:", event)


async def on_started(event: AIAgentSessionStartedEvent):
    print("Session started:", event)


async def on_ended(event: AIAgentSessionEndedEvent):
    print("Session ended:", event)


async def on_summary(event: AIAgentSessionSummaryDoneEvent):
    print("Summary ready:", event)


client.on_ai_agent_enabled_event(on_enabled)  # Events.AI_AGENT_ENABLE (WebSocket)
client.on_ai_agent_session_started(on_started)  # Events.AI_AGENT_SESSION_STARTED (SSE)
client.on_ai_agent_session_ended(on_ended)  # Events.AI_AGENT_SESSION_ENDED (SSE)
client.on_ai_agent_session_summary_done(
    on_summary
)  # Events.AI_AGENT_SESSION_SUMMARY_DONE (SSE)
```

`on_ai_agent_enabled_event` fires for `realtime_pb2.AIAgentEnabledEvent` messages received over the normal WebSocket connection — it does not require `connect_ai_agent_sse()`. The other three handlers are driven by the SSE stream and only fire after a successful `connect_ai_agent_sse()` call.

## SSE connection lifecycle events

The stream itself also emits generic connection-lifecycle events via `SSEEvents`:

```python
from mezon.constants import SSEEvents

client.on(SSEEvents.OPEN, lambda data: print("SSE opened", data))
client.on(SSEEvents.CLOSE, lambda: print("SSE closed"))
```
