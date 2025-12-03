"""
Copyright 2020 The Mezon Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import random
from datetime import datetime
from typing import List, Optional, Dict, Any
from mezon.models import (
    MessageComponentType,
    InputFieldOption,
    SelectFieldOption,
    RadioFieldOption,
    AnimationConfig,
)


def get_random_color() -> str:
    """Generate a random hex color."""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


class InteractiveBuilder:
    """
    Builder class for creating interactive message embeds with various field types.

    Example:
        >>> builder = InteractiveBuilder("Welcome Message")
        >>> builder.set_description("Please fill out the form below")
        >>> builder.add_input_field("name", "Full Name", "Enter your name")
        >>> builder.add_select_field("country", "Country", [
        ...     SelectFieldOption(label="USA", value="us"),
        ...     SelectFieldOption(label="UK", value="uk")
        ... ])
        >>> interactive = builder.build()
    """

    def __init__(self, title: Optional[str] = None):
        """
        Initialize an InteractiveBuilder.

        Args:
            title: Optional title for the interactive message
        """
        self.interactive: Dict[str, Any] = {
            "color": get_random_color(),
            "title": title,
            "fields": [],
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Powered by Mezon",
                "icon_url": "https://cdn.mezon.vn/1837043892743049216/1840654271217930240/1827994776956309500/857_0246x0w.webp",
            },
        }

    def set_color(self, color: str) -> "InteractiveBuilder":
        """
        Set the color of the interactive message.

        Args:
            color: Hex color string (e.g., "#FF5733")

        Returns:
            Self for method chaining
        """
        self.interactive["color"] = color
        return self

    def set_title(self, title: str) -> "InteractiveBuilder":
        """
        Set the title of the interactive message.

        Args:
            title: Title text

        Returns:
            Self for method chaining
        """
        self.interactive["title"] = title
        return self

    def set_url(self, url: str) -> "InteractiveBuilder":
        """
        Set the URL for the title link.

        Args:
            url: URL string

        Returns:
            Self for method chaining
        """
        self.interactive["url"] = url
        return self

    def set_author(
        self, name: str, icon_url: Optional[str] = None, url: Optional[str] = None
    ) -> "InteractiveBuilder":
        """
        Set the author information.

        Args:
            name: Author name
            icon_url: Optional author icon URL
            url: Optional author URL

        Returns:
            Self for method chaining
        """
        author = {"name": name}
        if icon_url:
            author["icon_url"] = icon_url
        if url:
            author["url"] = url
        self.interactive["author"] = author
        return self

    def set_description(self, description: str) -> "InteractiveBuilder":
        """
        Set the description text.

        Args:
            description: Description text

        Returns:
            Self for method chaining
        """
        self.interactive["description"] = description
        return self

    def set_thumbnail(self, url: str) -> "InteractiveBuilder":
        """
        Set the thumbnail image.

        Args:
            url: Thumbnail image URL

        Returns:
            Self for method chaining
        """
        self.interactive["thumbnail"] = {"url": url}
        return self

    def set_image(
        self, url: str, width: Optional[str] = None, height: Optional[str] = None
    ) -> "InteractiveBuilder":
        """
        Set the main image.

        Args:
            url: Image URL
            width: Optional image width
            height: Optional image height

        Returns:
            Self for method chaining
        """
        self.interactive["image"] = {
            "url": url,
            "width": width or "auto",
            "height": height or "auto",
        }
        return self

    def set_footer(
        self, text: str, icon_url: Optional[str] = None
    ) -> "InteractiveBuilder":
        """
        Set the footer information.

        Args:
            text: Footer text
            icon_url: Optional footer icon URL

        Returns:
            Self for method chaining
        """
        footer = {"text": text}
        if icon_url:
            footer["icon_url"] = icon_url
        self.interactive["footer"] = footer
        return self

    def add_field(
        self, name: str, value: str, inline: bool = False
    ) -> "InteractiveBuilder":
        """
        Add a simple text field.

        Args:
            name: Field name
            value: Field value
            inline: Whether the field should be displayed inline

        Returns:
            Self for method chaining
        """
        self.interactive["fields"].append(
            {
                "name": name,
                "value": value,
                "inline": inline,
            }
        )
        return self

    def add_input_field(
        self,
        field_id: str,
        name: str,
        placeholder: Optional[str] = None,
        options: Optional[InputFieldOption] = None,
        description: Optional[str] = None,
    ) -> "InteractiveBuilder":
        """
        Add an input field for user text entry.

        Args:
            field_id: Unique identifier for the field
            name: Field label/name
            placeholder: Placeholder text
            options: Input field configuration options
            description: Field description

        Returns:
            Self for method chaining
        """
        field_data = {
            "name": name,
            "value": description or "",
            "inputs": {
                "id": field_id,
                "type": MessageComponentType.INPUT.value,
                "component": {
                    "id": f"{field_id}-component",
                    "placeholder": placeholder,
                    "defaultValue": options.defaultValue if options else "",
                    "type": options.type if options else "text",
                    "textarea": options.textarea if options else False,
                },
            },
        }
        self.interactive["fields"].append(field_data)
        return self

    def add_select_field(
        self,
        field_id: str,
        name: str,
        options: List[SelectFieldOption],
        value_selected: Optional[SelectFieldOption] = None,
        description: Optional[str] = None,
    ) -> "InteractiveBuilder":
        """
        Add a select dropdown field.

        Args:
            field_id: Unique identifier for the field
            name: Field label/name
            options: List of select options
            value_selected: Pre-selected option
            description: Field description

        Returns:
            Self for method chaining
        """
        field_data = {
            "name": name,
            "value": description or "",
            "inputs": {
                "id": field_id,
                "type": MessageComponentType.SELECT.value,
                "component": {
                    "options": [
                        opt.model_dump() if hasattr(opt, "model_dump") else opt
                        for opt in options
                    ],
                    "valueSelected": value_selected.model_dump()
                    if value_selected and hasattr(value_selected, "model_dump")
                    else value_selected,
                },
            },
        }
        self.interactive["fields"].append(field_data)
        return self

    def add_radio_field(
        self,
        field_id: str,
        name: str,
        options: List[RadioFieldOption],
        description: Optional[str] = None,
        max_options: Optional[int] = None,
    ) -> "InteractiveBuilder":
        """
        Add a radio button field.

        Args:
            field_id: Unique identifier for the field
            name: Field label/name
            options: List of radio options
            description: Field description
            max_options: Maximum number of options that can be selected (for multiple choice)

        Returns:
            Self for method chaining
        """
        field_data = {
            "name": name,
            "value": description or "",
            "inputs": {
                "id": field_id,
                "type": MessageComponentType.RADIO.value,
                "component": [
                    opt.model_dump() if hasattr(opt, "model_dump") else opt
                    for opt in options
                ],
            },
        }
        if max_options:
            field_data["inputs"]["max_options"] = max_options
        self.interactive["fields"].append(field_data)
        return self

    def add_datepicker_field(
        self, field_id: str, name: str, description: Optional[str] = None
    ) -> "InteractiveBuilder":
        """
        Add a date picker field.

        Args:
            field_id: Unique identifier for the field
            name: Field label/name
            description: Field description

        Returns:
            Self for method chaining
        """
        field_data = {
            "name": name,
            "value": description or "",
            "inputs": {
                "id": field_id,
                "type": MessageComponentType.DATEPICKER.value,
                "component": {},
            },
        }
        self.interactive["fields"].append(field_data)
        return self

    def add_animation(
        self,
        field_id: str,
        config: AnimationConfig,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "InteractiveBuilder":
        """
        Add an animation field.

        Args:
            field_id: Unique identifier for the field
            config: Animation configuration
            name: Optional field name
            description: Field description

        Returns:
            Self for method chaining
        """
        field_data = {
            "name": name or "",
            "value": description or "",
            "inputs": {
                "id": field_id,
                "type": MessageComponentType.ANIMATION.value,
                "component": config.model_dump()
                if hasattr(config, "model_dump")
                else config,
            },
        }
        self.interactive["fields"].append(field_data)
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build and return the interactive message dictionary.

        Returns:
            Interactive message props dictionary
        """
        return self.interactive
