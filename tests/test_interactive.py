"""
Interactive message tests (buttons, embeds, forms) for Mezon SDK.
"""

from mezon import ChannelMessageContent
from mezon.models import ButtonMessageStyle
from mezon.structures.button_builder import ButtonBuilder
from mezon.structures.interactive_message import InteractiveBuilder

from tests.base import BaseTestSuite


class InteractiveTests(BaseTestSuite):
    """Tests for interactive message features."""

    async def run_all(self) -> None:
        """Run all interactive tests."""
        await self.test_buttons()
        await self.test_embeds()
        await self.test_forms()
        await self.test_button_styles()
        await self.test_multi_row_buttons()

    async def test_buttons(self) -> None:
        """Test: Button builder with basic buttons."""
        try:
            builder = ButtonBuilder()
            builder.add_button("btn1", "Click Me", ButtonMessageStyle.PRIMARY)
            builder.add_button("btn2", "Danger", ButtonMessageStyle.DANGER)
            buttons = builder.build()

            action_rows = [{"components": buttons}]

            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)
            await channel.send(
                content=ChannelMessageContent(
                    t="🔘 Button test", components=action_rows
                )
            )
            self.log_result("Button Builder", True)
        except Exception as e:
            self.log_result("Button Builder", False, str(e))

    async def test_button_styles(self) -> None:
        """Test: All button styles."""
        try:
            builder = ButtonBuilder()
            builder.add_button("primary", "Primary", ButtonMessageStyle.PRIMARY)
            builder.add_button("secondary", "Secondary", ButtonMessageStyle.SECONDARY)
            builder.add_button("success", "Success", ButtonMessageStyle.SUCCESS)
            builder.add_button("danger", "Danger", ButtonMessageStyle.DANGER)
            buttons = builder.build()

            action_rows = [{"components": buttons}]

            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)
            await channel.send(
                content=ChannelMessageContent(
                    t="🎨 All button styles", components=action_rows
                )
            )
            self.log_result("Button Styles", True)
        except Exception as e:
            self.log_result("Button Styles", False, str(e))

    async def test_multi_row_buttons(self) -> None:
        """Test: Multiple rows of buttons."""
        try:
            builder1 = ButtonBuilder()
            builder1.add_button("row1_btn1", "Row 1 - Button 1", ButtonMessageStyle.PRIMARY)
            builder1.add_button("row1_btn2", "Row 1 - Button 2", ButtonMessageStyle.PRIMARY)

            builder2 = ButtonBuilder()
            builder2.add_button("row2_btn1", "Row 2 - Button 1", ButtonMessageStyle.SECONDARY)
            builder2.add_button("row2_btn2", "Row 2 - Button 2", ButtonMessageStyle.SECONDARY)

            action_rows = [
                {"components": builder1.build()},
                {"components": builder2.build()},
            ]

            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)
            await channel.send(
                content=ChannelMessageContent(
                    t="📊 Multi-row buttons", components=action_rows
                )
            )
            self.log_result("Multi-row Buttons", True)
        except Exception as e:
            self.log_result("Multi-row Buttons", False, str(e))

    async def test_embeds(self) -> None:
        """Test: Interactive embeds with fields."""
        try:
            embed = InteractiveBuilder()
            embed.set_title("Test Embed")
            embed.set_description("Testing embed features")
            embed.set_color("#FF5733")
            embed.add_field("Field 1", "Value 1", inline=True)
            embed.add_field("Field 2", "Value 2", inline=True)
            embed.add_field("Field 3", "Value 3", inline=False)

            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)
            await channel.send(content=ChannelMessageContent(embed=[embed.build()]))
            self.log_result("Interactive Embed", True)
        except Exception as e:
            self.log_result("Interactive Embed", False, str(e))

    async def test_forms(self) -> None:
        """Test: Form fields with inputs and selects."""
        try:
            form = InteractiveBuilder()
            form.set_title("Test Form")
            form.add_input_field("input1", "Name", placeholder="Enter your name")
            form.add_input_field("input2", "Email", placeholder="Enter your email")
            form.add_select_field(
                "select1",
                "Choice",
                options=[
                    {"label": "Option A", "value": "a"},
                    {"label": "Option B", "value": "b"},
                    {"label": "Option C", "value": "c"},
                ],
            )

            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)
            await channel.send(content=ChannelMessageContent(embed=[form.build()]))
            self.log_result("Form Fields", True)
        except Exception as e:
            self.log_result("Form Fields", False, str(e))

