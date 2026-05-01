# Models

This page covers the Pydantic models most commonly used directly by SDK consumers.

## Base conversion helper

Many models inherit from `MezonBaseModel` and provide `from_protobuf(...)` for converting protobuf payloads into Pydantic objects.

## Message models

### `ChannelMessageContent`

Used to build outgoing message payloads.

```python
from mezon.models import ChannelMessageContent

content = ChannelMessageContent(
    t="Hello",
    text="Alternative text field",
    embed=[],
    components=[],
)
```

Common fields:

| Field | Type | Description |
|---|---|---|
| `t` | `str | None` | Primary text field |
| `text` | `str | None` | Alternate text field used in some examples |
| `embed` | `list | None` | Embed/interactive payloads |
| `components` | `list | None` | Message components such as buttons |

### `ApiMessageMention`

```python
from mezon.models import ApiMessageMention

mention = ApiMessageMention(user_id=123456789)
```

Useful fields include:

- `user_id`
- `username`
- `role_id`
- `rolename`
- `s` / `e` for mention offsets

### `ApiMessageAttachment`

```python
from mezon.models import ApiMessageAttachment

attachment = ApiMessageAttachment(
    url="https://example.com/file.png",
    filename="file.png",
    filetype="image/png",
    size=1024,
)
```

Common fields include `url`, `filename`, `filetype`, `size`, `width`, `height`, `thumbnail`, and `duration`.

### `ApiMessageRef`

Used for reply/reference metadata.

```python
from mezon.models import ApiMessageRef

ref = ApiMessageRef(
    message_ref_id=987654321,
    message_sender_id=123456789,
    content="Original message",
)
```

`ApiMessageRef` carries more than just an ID: sender metadata, optional content preview, attachment flags, and channel context may be included.

### `ChannelMessageAck`

Returned by send/update operations.

```python
ack = await channel.send(content=ChannelMessageContent(t="Hello"))
print(ack.message_id)
```

## Session model

### `ApiSession`

```python
session = await client.get_session()
print(session.token, session.ws_url)
```

Fields include:

- `token`
- `refresh_token`
- `user_id`
- `api_url`
- `id_token`
- `ws_url`

## Clan and channel descriptions

### `ApiClanDesc`

Represents a clan description returned by clan-list APIs. Common fields include `clan_id`, `clan_name`, `creator_id`, `logo`, `banner`, and `welcome_channel_id`.

### `ApiChannelDescription`

Represents a channel description returned by channel APIs. Common fields include:

- `channel_id`
- `channel_label`
- `category_id`
- `category_name`
- `clan_id`
- `type`
- `channel_private`
- `meeting_code`
- `user_ids`

## Token model

### `ApiSentTokenRequest`

```python
from mezon.models import ApiSentTokenRequest

request = ApiSentTokenRequest(
    receiver_id=123456789,
    amount=10,
    note="Reward",
)
```

| Field | Type | Description |
|---|---|---|
| `receiver_id` | `int | str` | Recipient user ID |
| `amount` | `int` | Amount to transfer |
| `note` | `str | None` | Transfer note |
| `sender_name` | `str | None` | Optional sender display name |
| `sender_id` | `str | None` | Optional sender override |
| `extra_attribute` | `str | None` | Extra metadata |
| `mmn_extra_info` | `dict | None` | MMN-specific payload |

## Interactive form option models

### `SelectFieldOption`

```python
from mezon.models import SelectFieldOption

option = SelectFieldOption(label="Vietnam", value="vn")
```

### `RadioFieldOption`

```python
from mezon.models import RadioFieldOption

option = RadioFieldOption(label="Pro", value="pro", description="Advanced")
```

These option models are passed into `InteractiveBuilder` field helpers.
