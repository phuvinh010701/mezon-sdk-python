"""
Token transfer tests for Mezon SDK.
"""

from mezon.models import ApiSentTokenRequest

from tests.base import BaseTestSuite


class TokenTests(BaseTestSuite):
    """Tests for token transfer operations."""

    async def run_all(self) -> None:
        """Run all token tests."""
        await self.test_send_token()

    async def test_send_token(self) -> None:
        """Test: Send token to another user via blockchain."""
        try:
            if not self.config.token_receiver_id:
                self.skip_test("Send Token", "No token receiver ID configured")
                return

            token_request = ApiSentTokenRequest(
                receiver_id=self.config.token_receiver_id,
                amount=1,  # Minimum amount
                note="SDK Test Token Transfer",
            )

            result = await self.client.send_token(token_request)
            assert result is not None, "Transaction result should exist"
            print(f"    ℹ️  Transaction hash: {getattr(result, 'hash', 'N/A')}")
            self.log_result("Send Token", True)
        except Exception as e:
            # May fail due to insufficient balance or MMN not initialized
            error_str = str(e).lower()
            if "insufficient" in error_str or "balance" in error_str:
                self.skip_test("Send Token", "Insufficient balance")
            elif "not initialized" in error_str:
                self.skip_test("Send Token", "MMN client not initialized")
            else:
                self.log_result("Send Token", False, str(e))
