# Models

Pydantic models for API requests and responses.

## Message Models

### ChannelMessageContent

Message content structure.

```python
from mezon.models import ChannelMessageContent

content = ChannelMessageContent(
    t="Message text",              # Text content
    text="Alternative text field", # Alternative text field
    embed=[...],                   # Embed objects
    components=[...],              # Interactive components
)
```

| Field | Type | Description |
|-------|------|-------------|
| `t` | `str` | Message text |
| `text` | `str` | Alternative text field |
| `embed` | `List[dict]` | Embed objects |
| `components` | `List[dict]` | Interactive components |

### ApiMessageMention

User mention in a message.

```python
from mezon.models import ApiMessageMention

mention = ApiMessageMention(
    user_id="user_id_here",
    username="optional_username",
)
```

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | `str` | User ID to mention |
| `username` | `str` | Optional username |

### ApiMessageAttachment

Message attachment.

```python
from mezon.models import ApiMessageAttachment

attachment = ApiMessageAttachment(
    url="https://example.com/file.png",
    filename="file.png",
    filetype="image/png",
    size=1024,
)
```

| Field | Type | Description |
|-------|------|-------------|
| `url` | `str` | Attachment URL |
| `filename` | `str` | File name |
| `filetype` | `str` | MIME type |
| `size` | `int` | File size in bytes |

### ApiMessageRef

Message reference (for replies).

```python
from mezon.models import ApiMessageRef

ref = ApiMessageRef(
    message_id="original_message_id",
)
```

| Field | Type | Description |
|-------|------|-------------|
| `message_id` | `str` | Referenced message ID |

### ChannelMessageAck

Message send acknowledgment.

```python
result = await channel.send(...)
print(result.message_id)
```

| Field | Type | Description |
|-------|------|-------------|
| `message_id` | `str` | Sent message ID |

## Token Models

### ApiSentTokenRequest

Token sending request.

```python
from mezon.models import ApiSentTokenRequest

request = ApiSentTokenRequest(
    receiver_id="user_id",
    amount=10,
    note="Thanks!",
    sender_name="Bot Name",      # Optional
    sender_id="custom_sender",   # Optional
    extra_attribute="metadata",  # Optional
    mmn_extra_info={...},        # Optional
)
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `receiver_id` | `str` | Yes | Recipient user ID |
| `amount` | `int` | Yes | Token amount |
| `note` | `str` | No | Transaction note |
| `sender_name` | `str` | No | Custom sender name |
| `sender_id` | `str` | No | Override sender ID |
| `extra_attribute` | `str` | No | Extra metadata |
| `mmn_extra_info` | `dict` | No | MMN-specific info |

## Interactive Field Options

### SelectFieldOption

Option for select dropdowns.

```python
from mezon.models import SelectFieldOption

option = SelectFieldOption(
    label="Display Text",
    value="option_value",
)
```

| Field | Type | Description |
|-------|------|-------------|
| `label` | `str` | Display text |
| `value` | `str` | Option value |

### RadioFieldOption

Option for radio buttons.

```python
from mezon.models import RadioFieldOption

option = RadioFieldOption(
    label="Option Label",
    value="option_value",
    description="Optional description",
)
```

| Field | Type | Description |
|-------|------|-------------|
| `label` | `str` | Display text |
| `value` | `str` | Option value |
| `description` | `str` | Optional description |

## Clan & Channel Models

### ApiClanDesc

Clan description/info.

| Field | Type | Description |
|-------|------|-------------|
| `clan_id` | `str` | Clan ID |
| `clan_name` | `str` | Clan name |
| `creator_id` | `str` | Creator user ID |
| `logo` | `str` | Logo URL |
| `banner` | `str` | Banner URL |

### ApiChannelDescription

Channel description/info.

| Field | Type | Description |
|-------|------|-------------|
| `channel_id` | `str` | Channel ID |
| `channel_label` | `str` | Channel name |
| `channel_type` | `int` | Channel type |
| `clan_id` | `str` | Parent clan ID |
| `category_id` | `str` | Parent category ID |

### ApiVoiceChannelUserList

Voice channel user list.

| Field | Type | Description |
|-------|------|-------------|
| `voice_channel_users` | `List` | List of users in voice |

## Session Models

### ApiSession

Authentication session.

| Field | Type | Description |
|-------|------|-------------|
| `token` | `str` | JWT access token |
| `refresh_token` | `str` | Refresh token |
| `created` | `bool` | Whether newly created |

## Usage Example

```python
from mezon.models import (
    ChannelMessageContent,
    ApiMessageMention,
    ApiMessageAttachment,
    ApiSentTokenRequest,
    SelectFieldOption,
)

# Send message with mentions and attachments
await channel.send(
    content=ChannelMessageContent(t="Hello @user!"),
    mentions=[ApiMessageMention(user_id="123")],
    attachments=[
        ApiMessageAttachment(
            url="https://example.com/image.png",
            filename="image.png"
        )
    ]
)

# Send tokens
await client.send_token(
    ApiSentTokenRequest(
        receiver_id="user_id",
        amount=10,
        note="Reward!"
    )
)
```
