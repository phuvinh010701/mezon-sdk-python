"""
Unit tests for ButtonBuilder class.
"""

from mezon.models import ButtonMessageStyle, MessageComponentType
from mezon.structures.button_builder import ButtonBuilder


class TestButtonBuilder:
    """Test ButtonBuilder class."""

    def test_init_creates_empty_components(self):
        """Test that initialization creates empty components list."""
        builder = ButtonBuilder()
        assert builder.components == []

    def test_add_button_basic(self):
        """Test adding a basic button."""
        builder = ButtonBuilder()
        result = builder.add_button("btn1", "Click Me", ButtonMessageStyle.PRIMARY)

        assert result is builder  # Check method chaining
        assert len(builder.components) == 1
        assert builder.components[0]["id"] == "btn1"
        assert builder.components[0]["type"] == MessageComponentType.BUTTON.value
        assert builder.components[0]["component"]["label"] == "Click Me"
        assert (
            builder.components[0]["component"]["style"]
            == ButtonMessageStyle.PRIMARY.value
        )

    def test_add_button_with_url(self):
        """Test adding a button with URL."""
        builder = ButtonBuilder()
        builder.add_button(
            "link_btn",
            "Visit Site",
            ButtonMessageStyle.LINK,
            url="https://example.com",
        )

        assert builder.components[0]["component"]["url"] == "https://example.com"

    def test_add_button_disabled(self):
        """Test adding a disabled button."""
        builder = ButtonBuilder()
        builder.add_button(
            "disabled_btn",
            "Disabled",
            ButtonMessageStyle.SECONDARY,
            disabled=True,
        )

        assert builder.components[0]["component"]["disable"] is True

    def test_add_button_not_disabled_by_default(self):
        """Test that buttons are not disabled by default."""
        builder = ButtonBuilder()
        builder.add_button("btn", "Label", ButtonMessageStyle.PRIMARY)

        assert "disable" not in builder.components[0]["component"]

    def test_add_multiple_buttons(self):
        """Test adding multiple buttons."""
        builder = ButtonBuilder()
        builder.add_button("btn1", "Primary", ButtonMessageStyle.PRIMARY)
        builder.add_button("btn2", "Secondary", ButtonMessageStyle.SECONDARY)
        builder.add_button("btn3", "Success", ButtonMessageStyle.SUCCESS)
        builder.add_button("btn4", "Danger", ButtonMessageStyle.DANGER)

        assert len(builder.components) == 4
        assert builder.components[0]["component"]["label"] == "Primary"
        assert builder.components[1]["component"]["label"] == "Secondary"
        assert builder.components[2]["component"]["label"] == "Success"
        assert builder.components[3]["component"]["label"] == "Danger"

    def test_method_chaining(self):
        """Test that add_button supports method chaining."""
        builder = ButtonBuilder()
        result = (
            builder.add_button("btn1", "First", ButtonMessageStyle.PRIMARY)
            .add_button("btn2", "Second", ButtonMessageStyle.SECONDARY)
            .add_button("btn3", "Third", ButtonMessageStyle.SUCCESS)
        )

        assert result is builder
        assert len(builder.components) == 3

    def test_build_returns_components(self):
        """Test that build returns the components list."""
        builder = ButtonBuilder()
        builder.add_button("btn1", "Button 1", ButtonMessageStyle.PRIMARY)
        builder.add_button("btn2", "Button 2", ButtonMessageStyle.DANGER)

        components = builder.build()

        assert components == builder.components
        assert len(components) == 2

    def test_clear_removes_all_buttons(self):
        """Test that clear removes all buttons."""
        builder = ButtonBuilder()
        builder.add_button("btn1", "Button 1", ButtonMessageStyle.PRIMARY)
        builder.add_button("btn2", "Button 2", ButtonMessageStyle.SECONDARY)

        assert len(builder.components) == 2

        result = builder.clear()

        assert result is builder  # Check method chaining
        assert len(builder.components) == 0

    def test_clear_and_rebuild(self):
        """Test clearing and rebuilding buttons."""
        builder = ButtonBuilder()
        builder.add_button("btn1", "First", ButtonMessageStyle.PRIMARY)
        builder.clear()
        builder.add_button("btn2", "Second", ButtonMessageStyle.DANGER)

        assert len(builder.components) == 1
        assert builder.components[0]["id"] == "btn2"

    def test_button_style_enum_value(self):
        """Test that ButtonMessageStyle enum is properly converted to value."""
        builder = ButtonBuilder()
        builder.add_button("btn", "Label", ButtonMessageStyle.PRIMARY)

        # Should store the enum value, not the enum itself
        style = builder.components[0]["component"]["style"]
        assert isinstance(style, int)

    def test_button_style_as_int(self):
        """Test that button style can be passed as int directly."""
        builder = ButtonBuilder()
        builder.add_button("btn", "Label", 1)  # Pass int instead of enum

        assert builder.components[0]["component"]["style"] == 1

    def test_complete_button_workflow(self):
        """Test a complete workflow of building buttons."""
        builder = ButtonBuilder()

        # Build a set of action buttons
        components = (
            builder.add_button("save", "Save", ButtonMessageStyle.SUCCESS)
            .add_button("cancel", "Cancel", ButtonMessageStyle.SECONDARY)
            .add_button(
                "delete",
                "Delete",
                ButtonMessageStyle.DANGER,
                disabled=False,
            )
            .add_button(
                "help",
                "Help",
                ButtonMessageStyle.LINK,
                url="https://help.example.com",
            )
            .build()
        )

        assert len(components) == 4
        assert components[0]["id"] == "save"
        assert components[1]["id"] == "cancel"
        assert components[2]["id"] == "delete"
        assert components[3]["id"] == "help"
        assert components[3]["component"]["url"] == "https://help.example.com"
