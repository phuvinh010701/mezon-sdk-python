# FastAPI Integration

Run a Mezon bot alongside a FastAPI application lifecycle.

## Full example

```python
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mezon import MezonClient
from mezon.models import ApiSentTokenRequest, ChannelMessageContent
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2

client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    enable_logging=True,
    log_level=logging.INFO,
)

async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

    payload = json.loads(message.content)
    text = payload.get("t", "")

    if text.startswith("!hello"):
        channel = await client.channels.fetch(message.channel_id)
        await channel.send(content=ChannelMessageContent(t="Hello from FastAPI bot!"))

async def on_channel_created(event: realtime_pb2.ChannelCreatedEvent):
    print(event.channel_id)

async def on_user_joined(event: realtime_pb2.UserChannelAdded):
    print(event.user_id, event.channel_id)

client.on_channel_message(handle_message)
client.on_channel_created(on_channel_created)
client.on_user_channel_added(on_user_joined)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await client.login()
    try:
        yield
    finally:
        await client.close_socket()

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/clan/{clan_id}/voice-users")
async def get_voice_users(clan_id: int):
    clan = await client.clans.fetch(clan_id)
    voice_users = await clan.list_channel_voice_users()
    return {"voice_users": voice_users}

@app.post("/channel/{channel_id}/send")
async def send_message(channel_id: int, text: str):
    channel = await client.channels.fetch(channel_id)
    ack = await channel.send(content=ChannelMessageContent(t=text))
    return {"message_id": ack.message_id}

@app.post("/user/{user_id}/tip")
async def tip_user(user_id: int, amount: int = 1, note: str = "Tip"):
    result = await client.send_token(
        ApiSentTokenRequest(
            receiver_id=user_id,
            amount=amount,
            note=note,
        )
    )
    return {"success": result.ok, "tx_hash": result.tx_hash if result.ok else None}

@app.get("/clan/{clan_id}/roles")
async def get_roles(clan_id: int):
    clan = await client.clans.fetch(clan_id)
    return {"roles": await clan.list_roles()}
```

## Run it

```bash
uvicorn main:app --reload
```

## Notes

- Attach the bot connection to FastAPI lifespan so startup/shutdown stay symmetric.
- Prefer `client.close_socket()` during shutdown.
- Use typed route parameters (`int`) to match the SDK's ID-heavy API surface.
