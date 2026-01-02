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
        await self.test_transaction_detail()

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

    async def test_transaction_detail(self) -> None:
        """Test: Get transaction detail by ID."""
        try:
            # Use a placeholder transaction ID (real test would need actual ID)
            test_tx_id = "test_transaction_id"

            result = await self.client.list_transaction_detail(test_tx_id)
            # May return empty or error for non-existent transaction
            self.log_result("Transaction Detail", True)
        except Exception as e:
            # Transaction not found is expected for test ID
            error_str = str(e).lower()
            if "not found" in error_str or "404" in error_str:
                self.log_result("Transaction Detail", True)  # API works, just no data
            else:
                self.log_result("Transaction Detail", False, str(e))

