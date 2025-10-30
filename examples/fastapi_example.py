from contextlib import asynccontextmanager
from mezon import MezonClient, Events
from mezon.protobuf.rtapi import realtime_pb2

client = MezonClient(bot_id="", api_key="")

import json


async def handle_channel_message(message: realtime_pb2.ChannelMessageSend):
    message_content = json.loads(message.content)
    content = message_content.get("t")
    if content.startswith("*hello"):
        await client.send_message(
            clan_id=message.clan_id,
            channel_id=message.channel_id,
            mode=message.mode,
            is_public=message.is_public,
            msg="Xin chao",
        )


async def handle_on_give_coffee(message):
    print("Handle on give coffee")


client.on(Events.CHANNEL_MESSAGE, handle_channel_message)
client.on(Events.GIVE_COFFEE, handle_on_give_coffee)


from fastapi import FastAPI
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    await client.login()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return JSONResponse(content={"message": "OK"})
