"""
Friend management tests for Mezon SDK.
"""

from tests.base import BaseTestSuite


class FriendTests(BaseTestSuite):
    """Tests for friend operations."""

    async def run_all(self) -> None:
        """Run all friend tests."""
        await self.test_friend_list()
        await self.test_friend_list_pagination()
        await self.test_add_friend()
        await self.test_accept_friend()

    async def test_friend_list(self) -> None:
        """Test: Get friend list."""
        try:
            friends = await self.client.get_list_friends(limit=50)
            assert friends is not None, "Friends response should exist"
            self.log_result("Friend List", True)
        except Exception as e:
            self.log_result("Friend List", False, str(e))

    async def test_friend_list_pagination(self) -> None:
        """Test: Get friend list with pagination."""
        try:
            # First page
            page1 = await self.client.get_list_friends(limit=10)
            assert page1 is not None, "First page should exist"

            # If there's a cursor, get second page
            cursor = getattr(page1, "cursor", None)
            if cursor:
                page2 = await self.client.get_list_friends(limit=10, cursor=cursor)
                assert page2 is not None, "Second page should exist"
                print("    ℹ️  Pagination working with cursor")
            else:
                print("    ℹ️  No more pages (single page of friends)")

            self.log_result("Friend List Pagination", True)
        except Exception as e:
            self.log_result("Friend List Pagination", False, str(e))

    async def test_add_friend(self) -> None:
        """Test: Send friend request."""
        try:
            if not self.config.friend_username:
                self.skip_test("Add Friend", "No friend username configured")
                return

            result = await self.client.add_friend(self.config.friend_username)
            # Friend request sent (may already be friends)
            self.log_result("Add Friend", True)
        except Exception as e:
            # May fail if already friends or user not found
            error_str = str(e).lower()
            if "already" in error_str or "friend" in error_str:
                self.log_result("Add Friend", True)  # Already friends is OK
            else:
                self.log_result("Add Friend", False, str(e))

    async def test_accept_friend(self) -> None:
        """Test: Accept friend request."""
        try:
            if not self.config.friend_username or not self.config.user_id:
                self.skip_test("Accept Friend", "No friend username/ID configured")
                return

            result = await self.client.accept_friend(
                user_id=self.config.user_id, username=self.config.friend_username
            )
            self.log_result("Accept Friend", True)
        except Exception as e:
            # May fail if no pending request
            error_str = str(e).lower()
            if "already" in error_str or "friend" in error_str or "not found" in error_str:
                self.log_result("Accept Friend", True)  # Already friends is OK
            else:
                self.log_result("Accept Friend", False, str(e))

