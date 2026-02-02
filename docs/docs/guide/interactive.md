# Interactive Messages

Create rich interactive messages with buttons, forms, and embeds.

## ButtonBuilder

Create interactive buttons:

```python
from mezon import ButtonBuilder, ButtonMessageStyle
from mezon.models import ChannelMessageContent

# Create buttons
buttons = ButtonBuilder()
buttons.add_button("accept", "Accept", ButtonMessageStyle.SUCCESS)
buttons.add_button("decline", "Decline", ButtonMessageStyle.DANGER)
buttons.add_button("help", "Help", ButtonMessageStyle.LINK, url="https://help.mezon.ai")

# Send with buttons
channel = await client.channels.fetch(channel_id)
await channel.send(
    content=ChannelMessageContent(
        text="Do you accept?",
        components=[{"components": buttons.build()}]
    )
)
```

### Button Styles

| Style | Appearance | Use Case |
|-------|------------|----------|
| `ButtonMessageStyle.PRIMARY` | Blue | Primary action |
| `ButtonMessageStyle.SECONDARY` | Gray | Secondary action |
| `ButtonMessageStyle.SUCCESS` | Green | Confirm/accept |
| `ButtonMessageStyle.DANGER` | Red | Cancel/delete |
| `ButtonMessageStyle.LINK` | Link | External URL (requires `url` param) |

## InteractiveBuilder

Build rich forms with multiple field types:

```python
from mezon import InteractiveBuilder
from mezon.models import SelectFieldOption, RadioFieldOption

# Create form
form = InteractiveBuilder("User Survey")
form.set_description("Please fill out this survey")
form.set_color("#5865F2")
form.set_author("Survey Bot", icon_url="https://example.com/icon.png")

# Add fields
form.add_input_field(
    "username",
    "Username",
    placeholder="Enter your username",
    description="Choose a unique username"
)

form.add_select_field(
    "country",
    "Country",
    options=[
        SelectFieldOption(label="United States", value="us"),
        SelectFieldOption(label="Vietnam", value="vn"),
    ],
    description="Select your country"
)

form.add_radio_field(
    "plan",
    "Plan",
    options=[
        RadioFieldOption(label="Free", value="free", description="Basic"),
        RadioFieldOption(label="Pro", value="pro", description="Advanced"),
    ]
)

form.add_datepicker_field("birthdate", "Birth Date")

# Send with form and buttons
buttons = ButtonBuilder()
buttons.add_button("submit", "Submit", ButtonMessageStyle.SUCCESS)
buttons.add_button("cancel", "Cancel", ButtonMessageStyle.SECONDARY)

await channel.send(
    content=ChannelMessageContent(
        text="Please complete this form:",
        embed=[form.build()],
        components=[{"components": buttons.build()}]
    )
)
```

### Field Types

| Method | Description |
|--------|-------------|
| `add_input_field()` | Text input (single/multi-line) |
| `add_select_field()` | Dropdown selection |
| `add_radio_field()` | Radio buttons |
| `add_datepicker_field()` | Date picker |
| `add_animation()` | Animated content |
| `add_field()` | Simple text field |

## Customizing Embeds

```python
embed = InteractiveBuilder("Custom Embed")

# Styling
embed.set_color("#FF5733")
embed.set_title("My Title")
embed.set_url("https://mezon.ai")
embed.set_description("Description here")

# Author
embed.set_author(
    "Author Name",
    icon_url="https://example.com/author.png",
    url="https://example.com/author"
)

# Images
embed.set_thumbnail("https://example.com/thumb.png")
embed.set_image(
    "https://example.com/banner.png",
    width="800",
    height="400"
)

# Footer
embed.set_footer("Footer Text", icon_url="https://example.com/footer.png")

# Simple fields
embed.add_field("Field 1", "Value 1", inline=True)
embed.add_field("Field 2", "Value 2", inline=True)

await channel.send(
    content=ChannelMessageContent(embed=[embed.build()])
)
```

## Handling Button Clicks

```python
async def on_button_click(event):
    button_id = event.button_id  # The ID you set in add_button()
    user_id = event.user_id

    if button_id == "accept":
        # Handle accept
        pass
    elif button_id == "decline":
        # Handle decline
        pass

client.on_message_button_clicked(on_button_click)
```

## Complete Example

```python
import json
from mezon import MezonClient, ButtonBuilder, InteractiveBuilder, ButtonMessageStyle
from mezon.models import ChannelMessageContent, SelectFieldOption
from mezon.protobuf.api import api_pb2

client = MezonClient(client_id="...", api_key="...")

async def handle_message(message: api_pb2.ChannelMessage):
    if message.sender_id == client.client_id:
        return

    content = json.loads(message.content)
    text = content.get("t", "")

    if text == "!survey":
        channel = await client.channels.fetch(message.channel_id)

        # Build form
        form = InteractiveBuilder("Quick Survey")
        form.set_color("#5865F2")
        form.add_select_field(
            "rating",
            "How's your experience?",
            options=[
                SelectFieldOption(label="Excellent", value="5"),
                SelectFieldOption(label="Good", value="4"),
                SelectFieldOption(label="Okay", value="3"),
            ]
        )

        # Build buttons
        buttons = ButtonBuilder()
        buttons.add_button("submit_survey", "Submit", ButtonMessageStyle.SUCCESS)

        await channel.send(
            content=ChannelMessageContent(
                embed=[form.build()],
                components=[{"components": buttons.build()}]
            )
        )

async def handle_button(event):
    if event.button_id == "submit_survey":
        # Process survey response
        channel = await client.channels.fetch(event.channel_id)
        await channel.send_ephemeral(
            receiver_id=event.user_id,
            content=ChannelMessageContent(text="Thanks for your feedback!")
        )

client.on_channel_message(handle_message)
client.on_message_button_clicked(handle_button)
```
