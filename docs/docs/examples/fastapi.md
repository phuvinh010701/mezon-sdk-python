# FastAPI Integration

Integrate your Mezon bot with a FastAPI web application.

## Full Example

```python
from contextlib import asynccontextmanager
import json
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mezon import MezonClient
from mezon.models import ChannelMessageContent, ApiSentTokenRequest
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2

# Initialize client
client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    enable_logging=True,
    log_level=logging.INFO,
)

# Message handler
async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

    content = json.loads(message.content)
    text = content.get("t", "")

    if text.startswith("!hello"):
        channel = await client.channels.fetch(message.channel_id)
        await channel.send(content=ChannelMessageContent(t="Hello from FastAPI bot!"))

# Channel events
async def on_channel_created(event: realtime_pb2.ChannelCreatedEvent):
    print(f"Channel created: {event.channel_id}")

async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(f"User {event.user_id} joined channel {event.channel_id}")

# Register handlers
client.on_channel_message(handle_message)
client.on_channel_created(on_channel_created)
client.on_user_channel_added(on_user_joined)

# FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Connecting to Mezon...")
    await client.login()
    print("Connected!")

    yield

    # Shutdown
    print("Disconnecting...")
    if client.socket_manager:
        await client.socket_manager.disconnect()
    print("Disconnected!")

app = FastAPI(lifespan=lifespan)

# API endpoints
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/clan/{clan_id}/voice-users")
async def get_voice_users(clan_id: str):
    """List users in voice channels"""
    clan = await client.clans.get(clan_id)
    voice_users = await clan.list_channel_voice_users()
    return {"voice_users": voice_users}

@app.post("/channel/{channel_id}/send")
async def send_message(channel_id: str, text: str):
    """Send a message to a channel"""
    channel = await client.channels.fetch(channel_id)
    result = await channel.send(content=ChannelMessageContent(t=text))
    return {"message_id": result.message_id}

@app.post("/user/{user_id}/tip")
async def tip_user(user_id: str, amount: int = 1, note: str = "Tip"):
    """Send tokens to a user"""
    result = await client.send_token(
        ApiSentTokenRequest(
            receiver_id=user_id,
            amount=amount,
            note=note,
        )
    )
    return {"success": result.ok, "tx_hash": result.tx_hash if result.ok else None}

@app.get("/clan/{clan_id}/roles")
async def get_roles(clan_id: str):
    """List roles in a clan"""
    clan = await client.clans.get(clan_id)
    roles = await clan.list_roles()
    return {"roles": roles}
```

## Running

```bash
uvicorn main:app --reload
```

Access:

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Project Structure

```
my-bot/
├── main.py          # FastAPI app + Mezon client
├── handlers/
│   ├── messages.py  # Message handlers
│   └── events.py    # Event handlers
├── api/
│   └── routes.py    # API routes
└── requirements.txt
```

## Modular Example

### handlers/messages.py

```python
import json
from mezon.models import ChannelMessageContent

async def handle_message(client, message):
    if message.sender_id == client.client_id:
        return

    content = json.loads(message.content)
    text = content.get("t", "")

    if text == "!ping":
        channel = await client.channels.fetch(message.channel_id)
        await channel.send(content=ChannelMessageContent(t="Pong!"))
```

### main.py

```python
from handlers.messages import handle_message

# Wrap handler to pass client
client.on_channel_message(lambda msg: handle_message(client, msg))
```

## Production Tips

1. **Use environment variables** for credentials
2. **Add error handling** around API calls
3. **Implement rate limiting** on API endpoints
4. **Use structured logging** for debugging
5. **Add authentication** to sensitive endpoints

```python
import os
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.environ.get("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")

@app.post("/channel/{channel_id}/send", dependencies=[Depends(verify_api_key)])
async def send_message(channel_id: str, text: str):
    # ...
```
