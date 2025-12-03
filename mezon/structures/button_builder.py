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

from typing import List, Dict, Any
from mezon.models import ButtonMessageStyle, MessageComponentType


class ButtonBuilder:
    """
    Builder class for creating interactive button components.

    Example:
        >>> builder = ButtonBuilder()
        >>> builder.add_button("btn1", "Click Me", ButtonMessageStyle.PRIMARY)
        >>> builder.add_button("btn2", "Cancel", ButtonMessageStyle.DANGER)
        >>> components = builder.build()
    """

    def __init__(self):
        """Initialize an empty ButtonBuilder."""
        self.components: List[Dict[str, Any]] = []

    def add_button(
        self,
        component_id: str,
        label: str,
        style: ButtonMessageStyle,
        url: str = None,
        disabled: bool = False,
    ) -> "ButtonBuilder":
        """
        Add a button to the builder.

        Args:
            component_id: Unique identifier for the button
            label: Text to display on the button
            style: Button style (PRIMARY, SECONDARY, SUCCESS, DANGER, LINK)
            url: Optional URL for link-style buttons
            disabled: Whether the button is disabled

        Returns:
            Self for method chaining
        """
        button_component = {
            "id": component_id,
            "type": MessageComponentType.BUTTON.value,
            "component": {
                "label": label,
                "style": style.value
                if isinstance(style, ButtonMessageStyle)
                else style,
            },
        }

        if url:
            button_component["component"]["url"] = url

        if disabled:
            button_component["component"]["disable"] = disabled

        self.components.append(button_component)
        return self

    def build(self) -> List[Dict[str, Any]]:
        """
        Build and return the list of button components.

        Returns:
            List of button component dictionaries
        """
        return self.components

    def clear(self) -> "ButtonBuilder":
        """
        Clear all buttons from the builder.

        Returns:
            Self for method chaining
        """
        self.components = []
        return self
