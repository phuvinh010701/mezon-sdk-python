# Token Sending

The SDK allows you to send tokens to other users on the Mezon platform.

## Overview

Token sending uses:

- **ZK Proof Generation** - Zero-knowledge proofs for transaction authentication
- **Nonce Management** - Automatic nonce handling for each transaction
- **Transaction Signing** - Signatures using ephemeral key pairs

## Basic Usage

```python
from mezon.models import ApiSentTokenRequest
from mmn import AddTxResponse

# Send tokens to a user
result: AddTxResponse = await client.send_token(
    ApiSentTokenRequest(
        receiver_id="user_id",
        amount=10,  # Amount in tokens
        note="Thanks for your help!",
    )
)

# Check result
if result.ok:
    print(f"Success! TX Hash: {result.tx_hash}")
else:
    print(f"Failed: {result.error}")
```

## Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `receiver_id` | `str` | Yes | Recipient user ID |
| `amount` | `int` | Yes | Token amount |
| `note` | `str` | No | Transaction note |
| `sender_name` | `str` | No | Custom sender display name |
| `sender_id` | `str` | No | Override sender ID |
| `extra_attribute` | `str` | No | Additional metadata |
| `mmn_extra_info` | `dict` | No | MMN-specific extra info |

## Advanced Usage

```python
result = await client.send_token(
    ApiSentTokenRequest(
        receiver_id="user_id",
        amount=10,
        note="Event reward",
        sender_name="My Bot",
        extra_attribute="event_2024",
        mmn_extra_info={
            "event_id": "12345",
            "reward_type": "participation",
        },
    )
)
```

## Error Handling

```python
try:
    result = await client.send_token(
        ApiSentTokenRequest(
            receiver_id="user_id",
            amount=1,
            note="Test",
        )
    )

    if not result.ok:
        print(f"Transaction failed: {result.error}")
    else:
        print(f"TX Hash: {result.tx_hash}")

except ValueError as e:
    # MMN client not initialized
    print(f"MMN unavailable: {e}")
except Exception as e:
    print(f"Error: {e}")
```

## In Message Handlers

Common pattern - reward users for actions:

```python
import json
from mezon.models import ApiSentTokenRequest, ChannelMessageContent

async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

    content = json.loads(message.content)
    text = content.get("t", "")

    if text == "!daily":
        # Send daily reward
        result = await client.send_token(
            ApiSentTokenRequest(
                receiver_id=message.sender_id,
                amount=10,
                note="Daily reward!",
            )
        )

        channel = await client.channels.fetch(message.channel_id)

        if result.ok:
            await channel.send(
                content=ChannelMessageContent(t="You received 10 tokens!")
            )
        else:
            await channel.send_ephemeral(
                receiver_id=message.sender_id,
                content=ChannelMessageContent(text=f"Failed: {result.error}")
            )

client.on_channel_message(handle_message)
```

## Requirements

Before using `send_token`:

1. Client must be logged in (`await client.login()`)
2. Bot must have sufficient token balance
3. Receiver user ID must be valid

The SDK automatically initializes MMN and ZK clients during login.

## Token Events

Listen for token-related events:

```python
from mezon import Events

async def on_token_sent(event):
    print(f"Token sent: {event}")

client.on(Events.TOKEN_SEND, on_token_sent)
```
