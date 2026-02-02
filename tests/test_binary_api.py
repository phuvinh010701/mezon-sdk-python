"""
Binary API (protobuf) tests for Mezon SDK.
"""

import time


from tests.base import BaseTestSuite


class BinaryApiTests(BaseTestSuite):
    """Tests for binary protobuf API responses."""

    async def run_all(self) -> None:
        """Run all binary API tests."""
        await self.test_binary_clan_list()
        await self.test_binary_channel_list()
        await self.test_binary_channel_detail()
        await self.test_binary_voice_users()
        await self.test_binary_roles()
        await self.test_binary_performance()

    async def test_binary_clan_list(self) -> None:
        """Test: List clans with binary protobuf response."""
        try:
            session = await self.client.get_session()
            result = await self.client.api_client.list_clans_descs(
                token=session.token, limit=10
            )
            assert result is not None, "Result should not be None"
            assert hasattr(result, "clandesc"), "Should have clandesc attribute"
            self.log_result("Binary API - List Clans", True)
        except Exception as e:
            self.log_result("Binary API - List Clans", False, str(e))

    async def test_binary_channel_list(self) -> None:
        """Test: List channels with binary protobuf response."""
        try:
            session = await self.client.get_session()
            result = await self.client.api_client.list_channel_descs(
                token=session.token,
                channel_type=0,
                clan_id=self.config.clan_id,
                limit=20,
            )
            assert result is not None, "Result should not be None"
            assert hasattr(result, "channeldesc"), "Should have channeldesc attribute"
            self.log_result("Binary API - List Channels", True)
        except Exception as e:
            self.log_result("Binary API - List Channels", False, str(e))

    async def test_binary_channel_detail(self) -> None:
        """Test: Get channel detail with binary protobuf response."""
        try:
            session = await self.client.get_session()
            result = await self.client.api_client.get_channel_detail(
                token=session.token,
                channel_id=self.config.channel_id,
            )
            assert result is not None, "Result should not be None"
            assert result.channel_id == self.config.channel_id, "Channel ID mismatch"
            self.log_result("Binary API - Channel Detail", True)
        except Exception as e:
            self.log_result("Binary API - Channel Detail", False, str(e))

    async def test_binary_voice_users(self) -> None:
        """Test: List voice users with binary protobuf response."""
        try:
            session = await self.client.get_session()
            result = await self.client.api_client.list_channel_voice_users(
                token=session.token,
                clan_id=self.config.clan_id,
                channel_id=self.config.voice_channel_id,
                limit=50,
            )
            assert result is not None, "Result should not be None"
            assert hasattr(result, "voice_channel_users"), (
                "Should have voice_channel_users"
            )
            self.log_result("Binary API - Voice Users", True)
        except Exception as e:
            self.log_result("Binary API - Voice Users", False, str(e))

    async def test_binary_roles(self) -> None:
        """Test: List roles with binary protobuf response."""
        try:
            session = await self.client.get_session()
            result = await self.client.api_client.list_roles(
                token=session.token,
                clan_id=self.config.clan_id,
                limit=100,
            )
            assert result is not None, "Result should not be None"
            assert hasattr(result, "roles"), "Should have roles attribute"
            self.log_result("Binary API - List Roles", True)
        except Exception as e:
            self.log_result("Binary API - List Roles", False, str(e))

    async def test_binary_performance(self) -> None:
        """Test: Measure binary API performance."""
        try:
            session = await self.client.get_session()

            # Measure binary response time
            start_binary = time.time()
            await self.client.api_client.list_clans_descs(token=session.token, limit=10)
            binary_time = time.time() - start_binary

            print(f"    📊 Binary API response time: {binary_time:.3f}s")

            self.log_result("Binary Performance", True)
        except Exception as e:
            self.log_result("Binary Performance", False, str(e))
