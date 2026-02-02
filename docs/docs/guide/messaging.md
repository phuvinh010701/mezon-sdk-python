# Sending Messages

Learn how to send various types of messages using the SDK.

## Basic Messages

### Using Channel Objects (Recommended)

```python
from mezon.models import ChannelMessageContent

# Get the channel
channel = await client.channels.fetch("channel_id")

# Send a text message
await channel.send(content=ChannelMessageContent(t="Hello, world!"))
```

### Message Content

The `ChannelMessageContent` model supports:

```python
from mezon.models import ChannelMessageContent

# Text message
content = ChannelMessageContent(t="Hello!")

# With text (alternative field)
content = ChannelMessageContent(text="Hello!")
```

## Mentions

Mention users in your messages:

```python
from mezon.models import ChannelMessageContent, ApiMessageMention

await channel.send(
    content=ChannelMessageContent(t="Hello @user!"),
    mentions=[
        ApiMessageMention(user_id="user_id_here")
    ]
)
```

## Attachments

Send messages with attachments:

```python
from mezon.models import ChannelMessageContent, ApiMessageAttachment

await channel.send(
    content=ChannelMessageContent(t="Check out this image!"),
    attachments=[
        ApiMessageAttachment(
            url="https://example.com/image.png",
            filename="image.png"
        )
    ]
)
```

## Ephemeral Messages

Ephemeral messages are only visible to a specific user:

```python
await channel.send_ephemeral(
    receiver_id="user_id",
    content=ChannelMessageContent(text="Only you can see this!")
)
```

## Replying to Messages

Reply to a specific message:

```python
# Get the message object
message = channel.messages.get("message_id")

# Send a reply
await message.reply(
    content=ChannelMessageContent(t="This is a reply!")
)
```

## Updating Messages

Edit a previously sent message:

```python
# Send a message
sent = await channel.send(content=ChannelMessageContent(t="Original text"))

# Update it
message = channel.messages.get(sent.message_id)
await message.update(
    content=ChannelMessageContent(t="Updated text (edited)")
)
```

## Adding Reactions

React to messages:

```python
message = channel.messages.get("message_id")
await message.react(
    emoji_id="emoji_id",
    emoji="emoji_name",
    count=1
)
```

## Legacy Method

The client also provides a direct method (legacy):

```python
await client.send_message(
    clan_id="clan_id",
    channel_id="channel_id",
    mode=1,  # Channel mode
    is_public=True,
    msg="Your message here",
    mentions=None,      # Optional: List[ApiMessageMention]
    attachments=None,   # Optional: List[ApiMessageAttachment]
    ref=None,           # Optional: List[ApiMessageRef] for replies
)
```

## Message References

For replies using the legacy method:

```python
from mezon.models import ApiMessageRef

await client.send_message(
    clan_id="clan_id",
    channel_id="channel_id",
    mode=1,
    is_public=True,
    msg="This is a reply",
    ref=[ApiMessageRef(message_id="original_message_id")]
)
```

## Best Practices

1. **Use channel objects** - They provide a cleaner API than the legacy method
2. **Handle errors** - Wrap sends in try/except for network issues
3. **Rate limiting** - The SDK handles rate limiting automatically, but avoid spamming
4. **Ephemeral for sensitive info** - Use ephemeral messages for user-specific content
