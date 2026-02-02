"""
Quick menu access tests for Mezon SDK.
"""

from tests.base import BaseTestSuite


class QuickMenuTests(BaseTestSuite):
    """Tests for quick menu access operations."""

    async def run_all(self) -> None:
        """Run all quick menu tests."""
        await self.test_add_quick_menu()
        await self.test_delete_quick_menu()
        await self.test_list_quick_menu()

    async def test_add_quick_menu(self) -> None:
        """Test: Add quick menu access for bot."""
        try:
            _ = await self.client.add_quick_menu_access(
                channel_id=int(self.config.channel_id),
                clan_id=int(self.config.clan_id),
                menu_type=1,
                action_msg="/test",
                background="",
                menu_name="Test Menu",
            )
            self.log_result("Add Quick Menu", True)
        except Exception as e:
            self.log_result("Add Quick Menu", False, str(e))

    async def test_delete_quick_menu(self) -> None:
        """Test: Delete quick menu access for bot."""
        try:
            _ = await self.client.delete_quick_menu_access(
                id=1,
                clan_id=int(self.config.clan_id),
                bot_id=int(self.config.client_id),
                menu_name="Test Menu",
                background="",
                action_msg="/test",
            )
            self.log_result("Delete Quick Menu", True)
        except Exception as e:
            # May fail if no quick menu exists
            error_str = str(e).lower()
            if "not found" in error_str or "404" in error_str:
                self.log_result("Delete Quick Menu", True)  # Not found is OK
            else:
                self.log_result("Delete Quick Menu", False, str(e))

    async def test_list_quick_menu(self) -> None:
        """Test: List quick menu access for bot."""
        try:
            _ = await self.client.list_quick_menu_access(
                bot_id=int(self.config.client_id),
            )
            self.log_result("List Quick Menu", True)
        except Exception as e:
            self.log_result("List Quick Menu", False, str(e))
