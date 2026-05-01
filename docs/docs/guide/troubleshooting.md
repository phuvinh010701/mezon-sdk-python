# Troubleshooting

## Authentication fails during `login()`

Check these first:

- `client_id` and `api_key` are correct
- the configured `host`, `port`, and `use_ssl` match the target environment
- outbound access to the Mezon API and WebSocket endpoints is available

If you need more visibility, enable SDK logging:

```python
client = MezonClient(
    client_id="YOUR_BOT_ID",
    api_key="YOUR_API_KEY",
    enable_logging=True,
)
```

## Messages are not being handled

Common causes:

- your handler is registered after `login()` but no message has arrived yet
- the bot is filtering its own messages incorrectly
- incoming `message.content` is JSON and your handler assumes plain text

Typical pattern:

```python
import json

async def handle_message(message):
    if message.sender_id == client.client_id:
        return

    payload = json.loads(message.content)
    text = payload.get("t", "")
```

## `get(...)` returns `None`

The SDK uses caches for clans, channels, users, and messages. If you are not sure the object is already cached, use `fetch(...)` instead of `get(...)`.

```python
channel = await client.channels.fetch(123456789)
message = await channel.messages.fetch(987654321)
```

## Ephemeral messages do not send

`TextChannel.send_ephemeral(...)` expects `receiver_ids: list[int]`, not a single `receiver_id` value.

```python
await channel.send_ephemeral(
    receiver_ids=[user_id],
    content=ChannelMessageContent(text="Private message"),
)
```

## Token sending fails

`send_token(...)` depends on MMN and ZK clients initialized during `login()`.

Make sure:

- `await client.login()` completed successfully
- `mmn_api_url` and `zk_api_url` are reachable
- the bot has the necessary balance/permissions

## SQLite cache issues

Message caching uses SQLite under `./mezon-cache/mezon-messages-cache.db` by default.

If you hit local DB issues:

- ensure the process can write to the cache directory
- avoid deleting the DB while the bot is running
- prefer one runtime owner per local cache path if you suspect file locking issues

## Reconnect-related confusion

When reconnect occurs, managers are rebuilt from a fresh session. Keep your app logic attached to the long-lived `client` object rather than storing stale low-level transport references.
