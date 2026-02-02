"""
Session management tests for Mezon SDK.
"""

from tests.base import BaseTestSuite


class SessionTests(BaseTestSuite):
    """Tests for session management operations."""

    async def run_all(self) -> None:
        """Run all session tests."""
        await self.test_session_get()
        await self.test_session_properties()
        await self.test_session_serialization()

    async def test_session_get(self) -> None:
        """Test: Get current session."""
        try:
            session = await self.client.get_session()
            assert session is not None, "Session should exist"
            assert session.user_id, "Session should have user_id"
            assert session.token, "Session should have token"
            self.log_result("Session Get", True)
        except Exception as e:
            self.log_result("Session Get", False, str(e))

    async def test_session_properties(self) -> None:
        """Test: Session properties."""
        try:
            session = await self.client.get_session()

            # Check required properties
            assert session.user_id, "Should have user_id"
            assert session.token, "Should have token"

            # Check optional properties exist
            _ = session.refresh_token
            _ = session.api_url

            print(f"    ℹ️  User ID: {session.user_id}")
            print(f"    ℹ️  Has refresh token: {bool(session.refresh_token)}")

            self.log_result("Session Properties", True)
        except Exception as e:
            self.log_result("Session Properties", False, str(e))

    async def test_session_serialization(self) -> None:
        """Test: Session to_dict serialization."""
        try:
            session = await self.client.get_session()
            session_dict = session.to_dict()

            assert "user_id" in session_dict, "Should have user_id in dict"
            assert "token" in session_dict, "Should have token in dict"
            assert isinstance(session_dict, dict), "Should be a dict"

            self.log_result("Session Serialization", True)
        except Exception as e:
            self.log_result("Session Serialization", False, str(e))
