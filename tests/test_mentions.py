"""
Mention functionality tests for Mezon SDK.
"""

import asyncio

from mezon import ChannelMessageContent
from mezon.models import ApiMessageMention
from tests.base import BaseTestSuite
from tests.helpers import compute_mention_indices

# Separator text used between the two mentions in test_multiple_mentions.
_MULTI_MENTION_SEPARATOR = " Hey! "


class MentionTests(BaseTestSuite):
    """Tests for message mention operations."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_message_id = None

    async def run_all(self) -> None:
        """Run all mention tests."""
        await self.test_mention_user()
        await asyncio.sleep(1)
        await self.test_mention_everyone()
        await asyncio.sleep(1)
        await self.test_multiple_mentions()
        await asyncio.sleep(1)
        if self.config.role_id:
            await self.test_mention_role()
        else:
            self.skip_test("Mention Role", "role_id not configured in test config")

    async def test_mention_user(self) -> None:
        """Test: Mention a specific user in a message."""
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
                    t=f"@{self.config.user_name} Test mention"
                ),
                mentions=[mention],
            )
            self.test_message_id = result.message_id
            self.log_result("Mention User", True)
        except Exception as e:
            self.log_result("Mention User", False, str(e))

    async def test_mention_everyone(self) -> None:
        """Test: Mention everyone in the channel."""
        try:
            channel = await self.client.channels.fetch(self.config.channel_id)
            result = await channel.send(
                content=ChannelMessageContent(t="@here 🧪 Test mention everyone"),
                mention_everyone=True,
            )
            self.test_message_id = result.message_id
            self.log_result("Mention Everyone", True)
        except Exception as e:
            self.log_result("Mention Everyone", False, str(e))

    async def test_multiple_mentions(self) -> None:
        """Test: Mention multiple users in a single message."""
        try:
            channel = await self.client.channels.fetch(self.config.channel_id)

            text = (
                f"@{self.config.user_name}{_MULTI_MENTION_SEPARATOR}"
                f"@{self.config.user_name_2} 🧪 Multiple mentions test"
            )
            mention1_s, mention1_e = compute_mention_indices(
                text, f"@{self.config.user_name}"
            )
            mention2_s, mention2_e = compute_mention_indices(
                text, f"@{self.config.user_name_2}"
            )
            mention1 = ApiMessageMention(
                user_id=self.config.user_id,
                username=self.config.user_name,
                s=mention1_s,
                e=mention1_e,
            )

            mention2 = ApiMessageMention(
                user_id=self.config.user_id_2,
                username=self.config.user_name_2,
                s=mention2_s,
                e=mention2_e,
            )

            result = await channel.send(
                content=ChannelMessageContent(t=text),
                mentions=[mention1, mention2],
            )
            self.test_message_id = result.message_id
            self.log_result("Multiple Mentions", True)
        except Exception as e:
            self.log_result("Multiple Mentions", False, str(e))

    async def test_mention_role(self) -> None:
        """Test: Mention a role in a message."""
        try:
            channel = await self.client.channels.fetch(self.config.channel_id)
            mention = ApiMessageMention(
                role_id=self.config.role_id,
                rolename="Dev",
                s=0,
                e=len("Dev") + 1,
            )

            result = await channel.send(
                content=ChannelMessageContent(t="@Dev 🧪 Test role mention"),
                mentions=[mention],
            )
            self.test_message_id = result.message_id
            self.log_result("Mention Role", True)
        except Exception as e:
            self.log_result("Mention Role", False, str(e))
