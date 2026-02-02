# Client Configuration

The `MezonClient` is the main entry point for interacting with the Mezon platform.

## Initialization

```python
from mezon import MezonClient
import logging

client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    host="gw.mezon.ai",      # Optional: API host
    port="443",               # Optional: API port
    use_ssl=True,             # Optional: Use SSL
    timeout=7000,             # Optional: Request timeout in ms
    enable_logging=True,      # Optional: Enable logging
    log_level=logging.INFO,   # Optional: Log level
)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client_id` | `str` | Required | Your bot's client ID |
| `api_key` | `str` | Required | Your API key |
| `host` | `str` | `"gw.mezon.ai"` | API host |
| `port` | `str` | `"443"` | API port |
| `use_ssl` | `bool` | `True` | Use SSL connection |
| `timeout` | `int` | `7000` | Request timeout in milliseconds |
| `enable_logging` | `bool` | `False` | Enable SDK logging |
| `log_level` | `int` | `logging.INFO` | Python logging level |

## Authentication

Call `login()` to authenticate and establish connections:

```python
async def main():
    await client.login()
    print(f"Logged in as {client.client_id}")
```

The login process:

1. Authenticates with the Mezon API using your credentials
2. Obtains a JWT session token
3. Establishes a WebSocket connection for real-time events
4. Initializes managers (session, socket, channel, event, cache)

## Auto-Reconnection

By default, the client automatically reconnects if the connection is lost:

```python
await client.login(enable_auto_reconnect=True)  # Default
```

To disable auto-reconnection:

```python
await client.login(enable_auto_reconnect=False)
```

## Accessing Managers

After login, you can access various managers:

```python
# Channel manager - fetch and manage channels
channel = await client.channels.fetch("channel_id")

# Clan manager - access clans
clan = await client.clans.get("clan_id")

# Session manager - access session info
session = client.session_manager.get_session()
print(f"Token: {session.token}")

# Socket manager - access WebSocket
socket = client.socket_manager.get_socket()
```

## Graceful Shutdown

Always close connections when shutting down:

```python
import signal
import asyncio

async def shutdown(client):
    print("Shutting down...")
    if client.socket_manager:
        await client.socket_manager.disconnect()

async def main():
    client = MezonClient(client_id="...", api_key="...")
    await client.login()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(shutdown(client))
        )

    await asyncio.Event().wait()
```

## Timeout Configuration

Increase timeout for slow connections:

```python
client = MezonClient(
    client_id="...",
    api_key="...",
    timeout=15000  # 15 seconds
)
```
