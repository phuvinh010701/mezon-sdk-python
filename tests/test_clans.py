"""
Clan operation tests for Mezon SDK.
"""

from mezon import ChannelType

from tests.base import BaseTestSuite


class ClanTests(BaseTestSuite):
    """Tests for clan operations."""

    async def run_all(self) -> None:
        """Run all clan tests."""
        await self.test_clan_fetch()
        await self.test_clan_channels()
        await self.test_clan_roles()
        await self.test_voice_users()
        await self.test_clan_cache()
        await self.test_channel_types()

    async def test_clan_fetch(self) -> None:
        """Test: Fetch clan by ID."""
        try:
            clan = await self.client.clans.fetch(self.config.clan_id)
            assert clan is not None, "Clan should exist"
            assert clan.id == self.config.clan_id, "Clan ID mismatch"
            self.log_result("Clan Fetch", True)
        except Exception as e:
            self.log_result("Clan Fetch", False, str(e))

    async def test_clan_channels(self) -> None:
        """Test: List clan channels."""
        try:
            clan = await self.client.clans.fetch(self.config.clan_id)
            await clan.load_channels()
            channel_count = clan.channels.size
            assert channel_count > 0, "Clan should have channels"
            self.log_result("Clan Channels", True)
        except Exception as e:
            self.log_result("Clan Channels", False, str(e))

    async def test_clan_roles(self) -> None:
        """Test: List clan roles."""
        try:
            clan = await self.client.clans.fetch(self.config.clan_id)
            roles = await clan.list_roles(limit="100")
            assert roles is not None, "Roles response should exist"
            self.log_result("Clan Roles", True)
        except Exception as e:
            self.log_result("Clan Roles", False, str(e))

    async def test_voice_users(self) -> None:
        """Test: List voice channel users."""
        try:
            if not self.config.voice_channel_id:
                self.skip_test("Voice Users", "No voice channel ID configured")
                return

            clan = await self.client.clans.fetch(self.config.clan_id)
            users = await clan.list_channel_voice_users(
                channel_id=self.config.voice_channel_id, limit=100
            )
            assert users is not None, "Voice users response should exist"
            self.log_result("Voice Users", True)
        except Exception as e:
            self.log_result("Voice Users", False, str(e))

    async def test_clan_cache(self) -> None:
        """Test: Clan cache operations."""
        try:
            # Check clan cache
            clan_count = self.client.clans.size
            assert clan_count > 0, "Clan cache should have entries"

            # Fetch specific clan
            clan = await self.client.clans.fetch(self.config.clan_id)

            # Get all cached clans
            clan_list = list(self.client.clans.values())
            assert len(clan_list) > 0, "Should have cached clans"

            self.log_result("Clan Cache", True)
        except Exception as e:
            self.log_result("Clan Cache", False, str(e))

    async def test_channel_types(self) -> None:
        """Test: Filter channels by type."""
        try:
            clan = await self.client.clans.fetch(self.config.clan_id)
            await clan.load_channels()

            channel_list = list(clan.channels.values())

            # Count by type
            text_channels = [
                ch
                for ch in channel_list
                if ch.channel_type == ChannelType.CHANNEL_TYPE_CHANNEL
            ]
            voice_channels = [
                ch
                for ch in channel_list
                if ch.channel_type == ChannelType.CHANNEL_TYPE_GMEET_VOICE
                or ch.channel_type == ChannelType.CHANNEL_TYPE_MEZON_VOICE
            ]

            print(f"    ℹ️  Text channels: {len(text_channels)}")
            print(f"    ℹ️  Voice channels: {len(voice_channels)}")

            self.log_result("Channel Types", True)
        except Exception as e:
            self.log_result("Channel Types", False, str(e))

