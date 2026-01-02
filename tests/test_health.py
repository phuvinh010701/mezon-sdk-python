"""
Health check and system tests for Mezon SDK.
"""

from tests.base import BaseTestSuite


class HealthTests(BaseTestSuite):
    """Tests for health check and system operations."""

    async def run_all(self) -> None:
        """Run all health tests."""
        await self.test_healthcheck()
        await self.test_readycheck()
        await self.test_logout()
        await self.test_disconnect()

    async def test_healthcheck(self) -> None:
        """Test: Server health check endpoint."""
        try:
            session = await self.client.get_session()
            result = await self.client.api_client.mezon_healthcheck(
                bearer_token=session.token
            )
            self.log_result("Health Check", True)
        except Exception as e:
            self.log_result("Health Check", False, str(e))

    async def test_readycheck(self) -> None:
        """Test: Server ready check endpoint."""
        try:
            session = await self.client.get_session()
            result = await self.client.api_client.mezon_readycheck(
                bearer_token=session.token
            )
            self.log_result("Ready Check", True)
        except Exception as e:
            self.log_result("Ready Check", False, str(e))

    async def test_logout(self) -> None:
        """Test: Logout functionality (skipped to preserve session)."""
        # Note: Actually logging out would break subsequent tests
        # This test verifies the method exists and is callable
        try:
            assert hasattr(self.client, "logout"), "Client should have logout method"
            assert callable(self.client.logout), "logout should be callable"
            self.skip_test("Logout", "Skipped to preserve session for other tests")
        except Exception as e:
            self.log_result("Logout", False, str(e))

    async def test_disconnect(self) -> None:
        """Test: Disconnect functionality (skipped to preserve connection)."""
        # Note: Actually disconnecting would break subsequent tests
        try:
            assert hasattr(
                self.client, "disconnect"
            ), "Client should have disconnect method"
            assert callable(self.client.disconnect), "disconnect should be callable"
            self.skip_test("Disconnect", "Skipped to preserve connection for other tests")
        except Exception as e:
            self.log_result("Disconnect", False, str(e))

