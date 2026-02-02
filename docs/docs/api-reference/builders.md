# Builders

Builder classes for creating rich interactive content.

## ButtonBuilder

Create interactive buttons for messages.

### Constructor

```python
from mezon import ButtonBuilder

buttons = ButtonBuilder()
```

### Methods

#### `add_button(id, label, style, url=None, disabled=False) -> ButtonBuilder`

Add a button to the builder.

```python
from mezon import ButtonMessageStyle

buttons.add_button(
    id="btn_accept",           # Button ID (for handling clicks)
    label="Accept",            # Display text
    style=ButtonMessageStyle.SUCCESS,  # Button style
    url=None,                  # URL (only for LINK style)
    disabled=False,            # Disable the button
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `str` | Required | Unique button ID |
| `label` | `str` | Required | Button text |
| `style` | `ButtonMessageStyle` | Required | Button style |
| `url` | `str` | `None` | URL for LINK buttons |
| `disabled` | `bool` | `False` | Disable button |

**Returns:** `ButtonBuilder` (for chaining)

#### `build() -> List[dict]`

Build the button components.

```python
components = buttons.build()
```

### Button Styles

```python
from mezon import ButtonMessageStyle

ButtonMessageStyle.PRIMARY     # Blue - primary action
ButtonMessageStyle.SECONDARY   # Gray - secondary action
ButtonMessageStyle.SUCCESS     # Green - confirm/accept
ButtonMessageStyle.DANGER      # Red - cancel/delete
ButtonMessageStyle.LINK        # Link - requires url param
```

### Example

```python
from mezon import ButtonBuilder, ButtonMessageStyle
from mezon.models import ChannelMessageContent

buttons = ButtonBuilder()
buttons.add_button("yes", "Yes", ButtonMessageStyle.SUCCESS)
buttons.add_button("no", "No", ButtonMessageStyle.DANGER)
buttons.add_button("docs", "Documentation", ButtonMessageStyle.LINK, url="https://docs.mezon.ai")

await channel.send(
    content=ChannelMessageContent(
        text="Do you agree?",
        components=[{"components": buttons.build()}]
    )
)
```

---

## InteractiveBuilder

Create rich interactive forms and embeds.

### Constructor

```python
from mezon import InteractiveBuilder

form = InteractiveBuilder(title="Form Title")
```

### Styling Methods

#### `set_title(title: str) -> InteractiveBuilder`

Set the embed title.

#### `set_description(description: str) -> InteractiveBuilder`

Set the embed description.

#### `set_color(color: str) -> InteractiveBuilder`

Set the embed color (hex format).

```python
form.set_color("#5865F2")
```

#### `set_url(url: str) -> InteractiveBuilder`

Set the title URL.

#### `set_author(name, icon_url=None, url=None) -> InteractiveBuilder`

Set author information.

```python
form.set_author(
    name="Bot Name",
    icon_url="https://example.com/icon.png",
    url="https://example.com"
)
```

#### `set_thumbnail(url: str) -> InteractiveBuilder`

Set thumbnail image.

#### `set_image(url, width=None, height=None) -> InteractiveBuilder`

Set main image.

```python
form.set_image("https://example.com/image.png", width="800", height="400")
```

#### `set_footer(text, icon_url=None) -> InteractiveBuilder`

Set footer text.

### Field Methods

#### `add_field(name, value, inline=False) -> InteractiveBuilder`

Add a simple text field.

```python
form.add_field("Name", "Value", inline=True)
```

#### `add_input_field(id, label, placeholder=None, description=None) -> InteractiveBuilder`

Add a text input field.

```python
form.add_input_field(
    id="username",
    label="Username",
    placeholder="Enter username...",
    description="Your display name"
)
```

#### `add_select_field(id, label, options, description=None) -> InteractiveBuilder`

Add a dropdown select field.

```python
from mezon.models import SelectFieldOption

form.add_select_field(
    id="country",
    label="Country",
    options=[
        SelectFieldOption(label="USA", value="us"),
        SelectFieldOption(label="Vietnam", value="vn"),
    ],
    description="Select your country"
)
```

#### `add_radio_field(id, label, options, description=None) -> InteractiveBuilder`

Add radio button options.

```python
from mezon.models import RadioFieldOption

form.add_radio_field(
    id="plan",
    label="Subscription",
    options=[
        RadioFieldOption(label="Free", value="free", description="Basic"),
        RadioFieldOption(label="Pro", value="pro", description="Advanced"),
    ]
)
```

#### `add_datepicker_field(id, label, description=None) -> InteractiveBuilder`

Add a date picker field.

```python
form.add_datepicker_field(
    id="birthdate",
    label="Birth Date",
    description="Select your birth date"
)
```

#### `add_animation(url) -> InteractiveBuilder`

Add animated content.

```python
form.add_animation("https://example.com/animation.gif")
```

#### `build() -> dict`

Build the embed dictionary.

```python
embed = form.build()
```

### Complete Example

```python
from mezon import InteractiveBuilder, ButtonBuilder, ButtonMessageStyle
from mezon.models import ChannelMessageContent, SelectFieldOption, RadioFieldOption

# Build form
form = InteractiveBuilder("Registration Form")
form.set_color("#5865F2")
form.set_description("Please complete the form below")
form.set_author("Registration Bot", icon_url="https://example.com/bot.png")

form.add_input_field("name", "Full Name", placeholder="John Doe")
form.add_input_field("email", "Email", placeholder="john@example.com")

form.add_select_field(
    "role",
    "Role",
    options=[
        SelectFieldOption(label="Developer", value="dev"),
        SelectFieldOption(label="Designer", value="design"),
        SelectFieldOption(label="Manager", value="mgmt"),
    ]
)

form.add_radio_field(
    "newsletter",
    "Subscribe to newsletter?",
    options=[
        RadioFieldOption(label="Yes", value="yes"),
        RadioFieldOption(label="No", value="no"),
    ]
)

form.set_footer("Powered by Mezon")

# Build buttons
buttons = ButtonBuilder()
buttons.add_button("submit", "Submit", ButtonMessageStyle.SUCCESS)
buttons.add_button("cancel", "Cancel", ButtonMessageStyle.SECONDARY)

# Send
await channel.send(
    content=ChannelMessageContent(
        embed=[form.build()],
        components=[{"components": buttons.build()}]
    )
)
```
