"""
User operation tests for Mezon SDK.
"""

from mezon import ChannelMessageContent

from tests.base import BaseTestSuite


class UserTests(BaseTestSuite):
    """Tests for user operations."""

    async def run_all(self) -> None:
        """Run all user tests."""
        await self.test_user_fetch()
        await self.test_dm_message()
        await self.test_user_cache()

    async def test_user_fetch(self) -> None:
        """Test: Fetch user by ID."""
        try:
            user = await self.client.users.fetch(self.config.user_id)
            assert user.id == self.config.user_id, "User ID mismatch"
            self.log_result("User Fetch", True)
        except Exception as e:
            self.log_result("User Fetch", False, str(e))

    async def test_dm_message(self) -> None:
        """Test: Send direct message to user."""
        try:
            user = await self.client.users.fetch(self.config.user_id)
            await user.send_dm_message(
                content=ChannelMessageContent(t="📬 Test DM from SDK")
            )
            self.log_result("DM Message", True)
        except Exception as e:
            self.log_result("DM Message", False, str(e))

    async def test_user_cache(self) -> None:
        """Test: User cache operations."""
        try:
            # Fetch user to populate cache
            user = await self.client.users.fetch(self.config.user_id)

            # Check cache hit
            cached_user = self.client.users.get(self.config.user_id)
            assert cached_user is not None, "User should be in cache"
            assert cached_user.id == user.id, "Cached user should match"

            # Check cache size
            cache_size = self.client.users.size
            assert cache_size > 0, "Cache should have entries"

            self.log_result("User Cache", True)
        except Exception as e:
            self.log_result("User Cache", False, str(e))

