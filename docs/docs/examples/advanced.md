# Advanced Patterns

This page collects a few reusable patterns for larger bots and applications.

## TTL caching around SDK calls

```python
from datetime import datetime, timedelta

class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self.cache = {}

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

role_cache = TTLCache(ttl_seconds=300)

async def get_roles(clan_id: int):
    cached = role_cache.get(str(clan_id))
    if cached:
        return cached

    clan = await client.clans.fetch(clan_id)
    roles = await clan.list_roles()
    role_cache.set(str(clan_id), roles)
    return roles
```

## Plugin-style message dispatch

```python
import json
from abc import ABC, abstractmethod
from typing import List

from mezon.models import ChannelMessageContent

class Plugin(ABC):
    @abstractmethod
    async def on_message(self, client, message):
        pass

    @abstractmethod
    def get_commands(self) -> List[str]:
        pass

class GreetingPlugin(Plugin):
    async def on_message(self, client, message):
        payload = json.loads(message.content)
        if payload.get("t") == "!hi":
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

plugins = PluginManager(client)
plugins.register(GreetingPlugin())
client.on_channel_message(plugins.handle_message)
```

## Guidance

- Prefer wrapping SDK calls in your own service layer once your app has more than a few handlers.
- Use `fetch(...)` instead of `get(...)` whenever cache misses are possible.
- Keep long-lived references at the `client` level; reconnect can rebuild lower-level managers.
