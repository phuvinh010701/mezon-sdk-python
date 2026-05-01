# Builders

The SDK ships with two high-level builders for interactive payloads: `ButtonBuilder` and `InteractiveBuilder`.

## ButtonBuilder

Source: `mezon/structures/button_builder.py`

### Create buttons

```python
from mezon import ButtonBuilder, ButtonMessageStyle

buttons = ButtonBuilder()
buttons.add_button("yes", "Yes", ButtonMessageStyle.SUCCESS)
buttons.add_button("no", "No", ButtonMessageStyle.DANGER)
```

### `add_button(...) -> ButtonBuilder`

| Parameter | Type | Description |
|---|---|---|
| `component_id` | `str` | Unique button ID |
| `label` | `str` | Button label |
| `style` | `ButtonMessageStyle` | Visual style |
| `url` | `str | None` | URL for link buttons |
| `disabled` | `bool` | Disabled state |

### Other methods

- `build() -> list[dict[str, Any]]`
- `clear() -> ButtonBuilder`

## InteractiveBuilder

Source: `mezon/structures/interactive_message.py`

### Create an interactive payload

```python
from mezon import InteractiveBuilder

form = InteractiveBuilder("Registration Form")
form.set_description("Please complete the form")
form.set_color("#5865F2")
```

### Layout and style methods

- `set_title(title)`
- `set_description(description)`
- `set_color(color)`
- `set_url(url)`
- `set_author(name, icon_url=None, url=None)`
- `set_thumbnail(url)`
- `set_image(url, width=None, height=None)`
- `set_footer(text, icon_url=None)`

### Field methods

- `add_field(name, value, inline=False)`
- `add_input_field(field_id, name, placeholder=None, options=None, description=None)`
- `add_select_field(field_id, name, options, value_selected=None, description=None)`
- `add_radio_field(field_id, name, options, description=None, max_options=None)`
- `add_datepicker_field(field_id, name, description=None)`
- `add_animation(url)`
- `build() -> dict[str, Any]`

## Example payload

```python
from mezon import ButtonBuilder, ButtonMessageStyle, InteractiveBuilder
from mezon.models import ChannelMessageContent, SelectFieldOption

form = InteractiveBuilder("Survey")
form.add_select_field(
    "country",
    "Country",
    options=[SelectFieldOption(label="Vietnam", value="vn")],
)

buttons = ButtonBuilder()
buttons.add_button("submit", "Submit", ButtonMessageStyle.SUCCESS)

await channel.send(
    content=ChannelMessageContent(
        embed=[form.build()],
        components=[{"components": buttons.build()}],
    )
)
```
