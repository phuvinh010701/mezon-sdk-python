"""
Streaming channel tests for Mezon SDK.
"""

from mezon.models import ApiRegisterStreamingChannelRequest

from tests.base import BaseTestSuite


class StreamingTests(BaseTestSuite):
    """Tests for streaming channel operations."""

    async def run_all(self) -> None:
        """Run all streaming tests."""
        await self.test_register_streaming_channel()

    async def test_register_streaming_channel(self) -> None:
        """Test: Register a streaming channel."""
        try:
            if not self.config.voice_channel_id:
                self.skip_test(
                    "Register Streaming Channel", "No voice channel ID configured"
                )
                return

            session = await self.client.get_session()

            request = ApiRegisterStreamingChannelRequest(
                clan_id=self.config.clan_id,
                channel_id=self.config.voice_channel_id,
                streaming_url="rtmp://test.example.com/live",
            )

            result = await self.client.api_client.register_streaming_channel(
                bearer_token=session.token, body=request
            )
            self.log_result("Register Streaming Channel", True)
        except Exception as e:
            # May fail due to permissions or already registered
            error_str = str(e).lower()
            if "permission" in error_str or "already" in error_str:
                self.skip_test("Register Streaming Channel", "Permission/already registered")
            else:
                self.log_result("Register Streaming Channel", False, str(e))

