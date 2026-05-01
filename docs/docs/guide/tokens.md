# Token Sending

The SDK can send MMN-backed token transfers through `client.send_token(...)` after `login()` has initialized the MMN and ZK clients.

## Basic usage

```python
from mezon.models import ApiSentTokenRequest

result = await client.send_token(
    ApiSentTokenRequest(
        receiver_id=123456789,
        amount=10,
        note="Thanks for your help!",
    )
)

if result.ok:
    print(result.tx_hash)
else:
    print(result.error)
```

## Request fields

| Field | Type | Required | Description |
|---|---|---|---|
| `receiver_id` | `int | str` | yes | Recipient user ID |
| `amount` | `int` | yes | Amount to transfer |
| `note` | `str | None` | no | Human-readable note |
| `sender_name` | `str | None` | no | Override sender display name |
| `sender_id` | `str | None` | no | Optional sender override |
| `extra_attribute` | `str | None` | no | Extra metadata |
| `mmn_extra_info` | `dict | None` | no | Additional MMN payload |

## Example inside a message handler

```python
import json
from mezon.models import ApiSentTokenRequest, ChannelMessageContent
from mezon.protobuf.api import api_pb2

async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

    payload = json.loads(message.content)
    if payload.get("t") == "!daily":
        result = await client.send_token(
            ApiSentTokenRequest(
                receiver_id=message.sender_id,
                amount=10,
                note="Daily reward!",
            )
        )

        channel = await client.channels.fetch(message.channel_id)
        if result.ok:
            await channel.send(content=ChannelMessageContent(t="You received 10 tokens"))
        else:
            await channel.send_ephemeral(
                receiver_ids=[message.sender_id],
                content=ChannelMessageContent(text=f"Failed: {result.error}"),
            )

client.on_channel_message(handle_message)
```

## Requirements

Before calling `send_token(...)`:

- `await client.login()` must have completed successfully
- MMN and ZK endpoints must be reachable
- the bot must have permission/balance to send tokens

## Token events

```python
async def on_token_sent(event):
    print(event)

client.on_token_send(on_token_sent)
```
