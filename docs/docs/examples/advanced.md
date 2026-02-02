# Advanced Patterns

Advanced usage patterns and best practices.

## Custom Reconnection Logic

```python
from mezon.socket import Socket

socket = Socket(host="gw.mezon.ai", port="443", use_ssl=True)

async def on_heartbeat_timeout():
    print("Connection lost - reconnecting...")
    # Custom reconnection logic

socket.onheartbeattimeout = on_heartbeat_timeout
```

## Command Framework

Build a simple command framework:

```python
import json
from dataclasses import dataclass
from typing import Callable, Dict

@dataclass
class CommandContext:
    message: any
    client: any
    channel: any
    args: list

class CommandHandler:
    def __init__(self, client):
        self.client = client
        self.commands: Dict[str, Callable] = {}
        self.prefix = "!"

    def command(self, name: str):
        def decorator(func):
            self.commands[name] = func
            return func
        return decorator

    async def handle(self, message):
        if message.sender_id == self.client.client_id:
            return

        content = json.loads(message.content)
        text = content.get("t", "").strip()

        if not text.startswith(self.prefix):
            return

        parts = text[len(self.prefix):].split()
        if not parts:
            return

        cmd_name = parts[0].lower()
        args = parts[1:]

        if cmd_name in self.commands:
            channel = await self.client.channels.fetch(message.channel_id)
            ctx = CommandContext(
                message=message,
                client=self.client,
                channel=channel,
                args=args,
            )
            await self.commands[cmd_name](ctx)

# Usage
handler = CommandHandler(client)

@handler.command("ping")
async def ping(ctx: CommandContext):
    await ctx.channel.send(content=ChannelMessageContent(t="Pong!"))

@handler.command("echo")
async def echo(ctx: CommandContext):
    text = " ".join(ctx.args) or "Nothing to echo"
    await ctx.channel.send(content=ChannelMessageContent(t=text))

client.on_channel_message(handler.handle)
```

## Conversation State

Track conversation state per user:

```python
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class UserState:
    step: str = "start"
    data: Dict = field(default_factory=dict)
    expires: Optional[datetime] = None

class ConversationManager:
    def __init__(self):
        self.states: Dict[str, UserState] = {}

    def get(self, user_id: str) -> UserState:
        return self.states.get(user_id, UserState())

    def set(self, user_id: str, state: UserState):
        self.states[user_id] = state

    def clear(self, user_id: str):
        self.states.pop(user_id, None)

# Usage
conversations = ConversationManager()

async def handle_message(message):
    if message.sender_id == client.client_id:
        return

    user_id = message.sender_id
    state = conversations.get(user_id)
    content = json.loads(message.content)
    text = content.get("t", "")
    channel = await client.channels.fetch(message.channel_id)

    if text == "!survey":
        # Start survey
        state.step = "name"
        conversations.set(user_id, state)
        await channel.send(content=ChannelMessageContent(t="What's your name?"))

    elif state.step == "name":
        state.data["name"] = text
        state.step = "age"
        conversations.set(user_id, state)
        await channel.send(content=ChannelMessageContent(t="How old are you?"))

    elif state.step == "age":
        state.data["age"] = text
        conversations.clear(user_id)
        name = state.data["name"]
        age = state.data["age"]
        await channel.send(
            content=ChannelMessageContent(t=f"Thanks {name}! You're {age} years old.")
        )

client.on_channel_message(handle_message)
```

## Scheduled Tasks

Run periodic tasks:

```python
import asyncio
from datetime import datetime

async def daily_announcement():
    while True:
        now = datetime.now()
        # Run at 9 AM
        if now.hour == 9 and now.minute == 0:
            channel = await client.channels.fetch("announcement_channel_id")
            await channel.send(
                content=ChannelMessageContent(t="Good morning everyone!")
            )
        await asyncio.sleep(60)  # Check every minute

async def main():
    await client.login()

    # Start scheduled task
    asyncio.create_task(daily_announcement())

    await asyncio.Event().wait()
```

## Error Handling Middleware

```python
import traceback
from functools import wraps

def error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            traceback.print_exc()
            # Optionally notify admin
    return wrapper

@error_handler
async def handle_message(message):
    # Your logic here
    pass

client.on_channel_message(handle_message)
```

## Caching API Responses

```python
from functools import lru_cache
from datetime import datetime, timedelta

class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str):
        if key in self.cache:
            value, expires = self.cache[key]
            if datetime.now() < expires:
                return value
            del self.cache[key]
        return None

    def set(self, key: str, value):
        expires = datetime.now() + timedelta(seconds=self.ttl)
        self.cache[key] = (value, expires)

# Usage
role_cache = TTLCache(ttl_seconds=300)

async def get_user_roles(clan_id: str):
    cached = role_cache.get(clan_id)
    if cached:
        return cached

    clan = await client.clans.get(clan_id)
    roles = await clan.list_roles()
    role_cache.set(clan_id, roles)
    return roles
```

## Plugin System

```python
from abc import ABC, abstractmethod
from typing import List

class Plugin(ABC):
    @abstractmethod
    async def on_message(self, client, message):
        pass

    @abstractmethod
    def get_commands(self) -> List[str]:
        pass

class GreetingPlugin(Plugin):
    async def on_message(self, client, message):
        content = json.loads(message.content)
        text = content.get("t", "")
        if text == "!hi":
            channel = await client.channels.fetch(message.channel_id)
            await channel.send(content=ChannelMessageContent(t="Hello!"))

    def get_commands(self) -> List[str]:
        return ["!hi"]

class PluginManager:
    def __init__(self, client):
        self.client = client
        self.plugins: List[Plugin] = []

    def register(self, plugin: Plugin):
        self.plugins.append(plugin)

    async def handle_message(self, message):
        for plugin in self.plugins:
            await plugin.on_message(self.client, message)

# Usage
plugins = PluginManager(client)
plugins.register(GreetingPlugin())
client.on_channel_message(plugins.handle_message)
```
