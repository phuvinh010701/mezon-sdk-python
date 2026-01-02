"""
Message operation tests for Mezon SDK.
"""

import asyncio
from mezon import ChannelMessageContent
from mezon.models import ApiMessageAttachment

from tests.base import BaseTestSuite


class MessageTests(BaseTestSuite):
    """Tests for message operations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sent_message_id = None

    async def run_all(self) -> None:
        """Run all message tests."""
        await self.test_message_send()
        await asyncio.sleep(1)
        await self.test_message_edit()
        await self.test_message_react()
        await self.test_message_reply()
        await self.test_message_with_attachment()
        await self.test_ephemeral_message()
        await self.test_message_delete()

    async def test_message_send(self) -> None:
        """Test: Send message to channel."""
        try:
            clan = await self.client.clans.fetch(self.config.clan_id)
            if not clan:
                raise ValueError(f"Clan {self.config.clan_id} not found")

            await clan.load_channels()
            channel = await clan.channels.fetch(self.config.channel_id)
            if not channel:
                raise ValueError(f"Channel {self.config.channel_id} not found")

            result = await channel.send(
                content=ChannelMessageContent(t="🧪 Test message from SDK test suite")
            )
            self.sent_message_id = result.message_id
            self.log_result("Message Send", True)
        except Exception as e:
            self.log_result("Message Send", False, str(e))

    async def test_message_edit(self) -> None:
        """Test: Edit existing message."""
        try:
            if not self.sent_message_id:
                raise ValueError("No message to edit")

            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)
            message = await channel.messages.fetch(self.sent_message_id)
            await message.update(
                content=ChannelMessageContent(t="🧪 Test message (edited)")
            )
            self.log_result("Message Edit", True)
        except Exception as e:
            self.log_result("Message Edit", False, str(e))

    async def test_message_react(self) -> None:
        """Test: Add reaction to message."""
        try:
            if not self.sent_message_id:
                raise ValueError("No message to react to")

            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)
            message = await channel.messages.fetch(self.sent_message_id)
            await message.react(emoji_id="7386985750250017344", emoji="👍", count=1)
            self.log_result("Message React", True)
        except Exception as e:
            self.log_result("Message React", False, str(e))

    async def test_message_reply(self) -> None:
        """Test: Reply to message."""
        try:
            if not self.sent_message_id:
                raise ValueError("No message to reply to")

            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)
            message = await channel.messages.fetch(self.sent_message_id)
            await message.reply(content=ChannelMessageContent(t="🧪 Test reply"))
            self.log_result("Message Reply", True)
        except Exception as e:
            self.log_result("Message Reply", False, str(e))

    async def test_message_delete(self) -> None:
        """Test: Delete message."""
        try:
            if not self.sent_message_id:
                raise ValueError("No message to delete")

            channel = await self.client.channels.fetch(self.config.channel_id)
            message = await channel.messages.fetch(self.sent_message_id)
            await message.delete()
            self.sent_message_id = None
            self.log_result("Message Delete", True)
        except Exception as e:
            self.log_result("Message Delete", False, str(e))

    async def test_message_with_attachment(self) -> None:
        """Test: Send message with attachment."""
        try:
            attachment = ApiMessageAttachment(
                filename="test.png",
                filetype="image/png",
                size=11222,
                url="https://cdn.mezon.ai/1840673138057154560/1999324370807296000.png",
            )

            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)

            await channel.send(
                content=ChannelMessageContent(t="📎 Message with attachment"),
                attachments=[attachment],
            )
            self.log_result("Message with Attachment", True)
        except Exception as e:
            self.log_result("Message with Attachment", False, str(e))

    async def test_ephemeral_message(self) -> None:
        """Test: Send ephemeral message (only visible to one user)."""
        try:
            clan = await self.client.clans.fetch(self.config.clan_id)
            channel = await clan.channels.fetch(self.config.channel_id)
            await channel.send_ephemeral(
                receiver_id=self.config.user_id,
                content=ChannelMessageContent(t="👻 Ephemeral test message"),
            )
            self.log_result("Ephemeral Message", True)
        except Exception as e:
            self.log_result("Ephemeral Message", False, str(e))

