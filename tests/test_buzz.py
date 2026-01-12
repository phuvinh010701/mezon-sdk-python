"""
Message buzz functionality tests for Mezon SDK.
"""

import asyncio
from mezon import ChannelMessageContent, TypeMessage
from mezon.models import ApiMessageMention

from tests.base import BaseTestSuite


class BuzzTests(BaseTestSuite):
    """Tests for message buzz operations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buzz_message_id = None

    async def run_all(self) -> None:
        """Run all buzz tests."""
        await self.test_send_buzz()
        await asyncio.sleep(1)
        await self.test_send_buzz_with_mention()
        await asyncio.sleep(1)
        await self.test_send_buzz_mention_everyone()

    async def test_send_buzz(self) -> None:
        """Test: Send a buzz message to channel."""
        try:
            channel = await self.client.channels.fetch(self.config.channel_id)
            result = await channel.send(
                content=ChannelMessageContent(t="🔔 Test buzz message"),
                code=TypeMessage.MESSAGE_BUZZ,
            )
            self.buzz_message_id = result.message_id
            self.log_result("Send Buzz", True)
        except Exception as e:
            self.log_result("Send Buzz", False, str(e))

    async def test_send_buzz_with_mention(self) -> None:
        """Test: Send a buzz message with user mention."""
        try:
            channel = await self.client.channels.fetch(self.config.channel_id)
            mention = ApiMessageMention(
                user_id=self.config.user_id,
                username=self.config.user_name,
                s=0,
                e=len(self.config.user_name) + 1,
            )

            result = await channel.send(
                content=ChannelMessageContent(
                    t=f"@{self.config.user_name} 🔔 Buzz with mention"
                ),
                mentions=[mention],
                code=TypeMessage.MESSAGE_BUZZ,
            )
            self.buzz_message_id = result.message_id
            self.log_result("Buzz with Mention", True)
        except Exception as e:
            self.log_result("Buzz with Mention", False, str(e))

    async def test_send_buzz_mention_everyone(self) -> None:
        """Test: Send a buzz message mentioning everyone."""
        try:
            channel = await self.client.channels.fetch(self.config.channel_id)
            result = await channel.send(
                content=ChannelMessageContent(t="@everyone 🔔 Buzz mention everyone"),
                mention_everyone=True,
                code=TypeMessage.MESSAGE_BUZZ,
            )
            self.buzz_message_id = result.message_id
            self.log_result("Buzz Mention Everyone", True)
        except Exception as e:
            self.log_result("Buzz Mention Everyone", False, str(e))
