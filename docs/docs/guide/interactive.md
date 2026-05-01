# Interactive Messages

The SDK includes builders for button components and rich interactive/embed payloads.

## ButtonBuilder

```python
from mezon import ButtonBuilder, ButtonMessageStyle
from mezon.models import ChannelMessageContent

buttons = ButtonBuilder()
buttons.add_button("accept", "Accept", ButtonMessageStyle.SUCCESS)
buttons.add_button("decline", "Decline", ButtonMessageStyle.DANGER)
buttons.add_button("docs", "Docs", ButtonMessageStyle.LINK, url="https://mezon.ai")

await channel.send(
    content=ChannelMessageContent(
        text="Do you accept?",
        components=[{"components": buttons.build()}],
    )
)
```

`add_button(...)` takes `component_id`, `label`, `style`, optional `url`, and optional `disabled`.

## InteractiveBuilder

```python
from mezon import InteractiveBuilder
from mezon.models import RadioFieldOption, SelectFieldOption

form = InteractiveBuilder("User Survey")
form.set_description("Please fill out this survey")
form.set_color("#5865F2")

form.add_input_field(
    "username",
    "Username",
    placeholder="Enter your username",
    description="Choose a unique username",
)

form.add_select_field(
    "country",
    "Country",
    options=[
        SelectFieldOption(label="United States", value="us"),
        SelectFieldOption(label="Vietnam", value="vn"),
    ],
)

form.add_radio_field(
    "plan",
    "Plan",
    options=[
        RadioFieldOption(label="Free", value="free", description="Basic"),
        RadioFieldOption(label="Pro", value="pro", description="Advanced"),
    ],
)
```

## Send form + buttons together

```python
buttons = ButtonBuilder()
buttons.add_button("submit", "Submit", ButtonMessageStyle.SUCCESS)

await channel.send(
    content=ChannelMessageContent(
        text="Please complete this form",
        embed=[form.build()],
        components=[{"components": buttons.build()}],
    )
)
```

## Common builder methods

### `InteractiveBuilder`

- `set_title(...)`
- `set_description(...)`
- `set_color(...)`
- `set_url(...)`
- `set_author(...)`
- `set_thumbnail(...)`
- `set_image(...)`
- `set_footer(...)`
- `add_field(...)`
- `add_input_field(...)`
- `add_select_field(...)`
- `add_radio_field(...)`
- `add_datepicker_field(...)`
- `add_animation(...)`
- `build()`

### `ButtonBuilder`

- `add_button(...)`
- `build()`
- `clear()`

## Handling button clicks

```python
async def on_button_click(event):
    if event.button_id == "submit":
        channel = await client.channels.fetch(event.channel_id)
        await channel.send_ephemeral(
            receiver_ids=[event.user_id],
            content=ChannelMessageContent(text="Received!"),
        )

client.on_message_button_clicked(on_button_click)
```
