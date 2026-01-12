"""
Auto-reconnect tests for Mezon SDK WebSocket.
"""

import asyncio
from mezon import ChannelMessageContent
from tests.base import BaseTestSuite


class ReconnectTests(BaseTestSuite):
    """Tests for WebSocket auto-reconnect functionality."""

    async def run_all(self) -> None:
        """Run all reconnect tests."""
        await self.test_initial_connection()
        await self.test_auto_reconnect_after_disconnect()
        await self.test_hard_disconnect_prevents_reconnect()
        await self.test_functionality_after_reconnect()

    async def test_initial_connection(self) -> None:
        """Test: Initial WebSocket connection is established."""
        try:
            # Check if socket is connected
            is_connected = await self.client.socket_manager.is_connected()
            assert is_connected, "Socket should be connected after login"

            # Verify we can send a message (proves connection works)
            clan = self.client.clans.get(self.config.clan_id)
            if not clan:
                self.skip_test("Initial Connection", "Clan not found")
                return

            channel = await clan.channels.fetch(self.config.channel_id)
            if not channel:
                self.skip_test("Initial Connection", "Channel not found")
                return

            # Send a test message
            result = await channel.send(
                ChannelMessageContent(t="🔌 Testing initial connection")
            )
            assert result is not None, "Should be able to send message"

            print(f"    ℹ️  Socket connected: {is_connected}")
            print("    ℹ️  Message sent successfully")

            self.log_result("Initial Connection", True)
        except Exception as e:
            self.log_result("Initial Connection", False, str(e))

    async def test_auto_reconnect_after_disconnect(self) -> None:
        """Test: Socket auto-reconnects after soft disconnect."""
        try:
            # Verify initial connection
            assert await self.client.socket_manager.is_connected(), (
                "Socket should be connected"
            )
            print("    ℹ️  Initial connection verified")

            # Simulate server disconnect by:
            # 1. Close the socket
            # 2. Trigger the ondisconnect handler (simulating server-side disconnect)
            print("    ℹ️  Simulating server disconnect...")

            # Close the socket first
            await self.client.socket_manager.socket.close()

            # Wait for socket to be disconnected
            await asyncio.sleep(0.5)
            assert not await self.client.socket_manager.is_connected(), (
                "Socket should be disconnected"
            )
            print("    ℹ️  Socket disconnected")

            # Now trigger the ondisconnect handler to simulate server disconnect
            # This will trigger the auto-reconnect logic
            if self.client.socket_manager.socket.ondisconnect:
                print("    ℹ️  Triggering disconnect handler...")
                await self.client.socket_manager.socket.ondisconnect(
                    "simulated_disconnect"
                )

            # Wait for auto-reconnect by polling connection status
            # The reconnect logic uses exponential backoff starting at 5 seconds
            print("    ℹ️  Waiting for auto-reconnect (up to 15 seconds)...")

            max_wait = 15  # seconds
            poll_interval = 0.5  # seconds
            elapsed = 0

            while elapsed < max_wait:
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

                if await self.client.socket_manager.is_connected():
                    print(f"    ℹ️  Auto-reconnect detected after {elapsed:.1f}s")
                    break
            else:
                raise AssertionError("Socket did not reconnect within timeout period")

            # Verify reconnection
            is_reconnected = await self.client.socket_manager.is_connected()
            assert is_reconnected, "Socket should be reconnected"
            print("    ℹ️  Socket successfully reconnected")

            self.log_result("Auto-Reconnect After Disconnect", True)
        except Exception as e:
            self.log_result("Auto-Reconnect After Disconnect", False, str(e))
            # Try to reconnect for next test
            try:
                if not await self.client.socket_manager.is_connected():
                    await self.client.login(enable_auto_reconnect=True)
                    await asyncio.sleep(2)
            except Exception:
                pass

    async def test_hard_disconnect_prevents_reconnect(self) -> None:
        """Test: Hard disconnect prevents auto-reconnection."""
        try:
            # Ensure we're connected (might have failed in previous test)
            if not await self.client.socket_manager.is_connected():
                print("    ℹ️  Socket not connected, reconnecting...")
                await self.client.login(enable_auto_reconnect=True)
                await asyncio.sleep(2)

            # Verify initial connection
            assert await self.client.socket_manager.is_connected(), (
                "Socket should be connected"
            )
            print("    ℹ️  Initial connection verified")

            # Perform hard disconnect
            print("    ℹ️  Performing hard disconnect...")
            await self.client.disconnect()

            # Wait a bit to see if reconnection is attempted
            await asyncio.sleep(1)

            # Verify socket is closed
            is_closed = not await self.client.socket_manager.is_connected()
            assert is_closed, "Socket should remain disconnected after hard disconnect"
            print("    ℹ️  Socket remains disconnected")

            # Wait to verify no reconnection attempt (should not happen)
            print("    ℹ️  Waiting to verify no reconnection (10 seconds)...")
            max_wait = 10
            poll_interval = 0.5
            elapsed = 0

            while elapsed < max_wait:
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

                if await self.client.socket_manager.is_connected():
                    raise AssertionError(
                        f"Socket reconnected after {elapsed:.1f}s but should not reconnect after hard disconnect"
                    )

            print("    ℹ️  Confirmed: No reconnection attempt")

            # Reconnect for subsequent tests
            print("    ℹ️  Reconnecting for subsequent tests...")
            await self.client.login(enable_auto_reconnect=True)
            await asyncio.sleep(2)  # Wait for clans to load

            self.log_result("Hard Disconnect Prevents Reconnect", True)
        except Exception as e:
            self.log_result("Hard Disconnect Prevents Reconnect", False, str(e))
            # Attempt to reconnect even if test failed
            try:
                await self.client.login(enable_auto_reconnect=True)
                await asyncio.sleep(2)
            except Exception:
                pass

    async def test_functionality_after_reconnect(self) -> None:
        """Test: Socket functionality works after auto-reconnect."""
        try:
            # Ensure we're connected (might have failed in previous test)
            if not await self.client.socket_manager.is_connected():
                print("    ℹ️  Socket not connected, reconnecting...")
                await self.client.login(enable_auto_reconnect=True)
                await asyncio.sleep(3)

            # Verify initial connection
            assert await self.client.socket_manager.is_connected(), (
                "Socket should be connected"
            )
            print("    ℹ️  Initial connection verified")

            # Simulate server disconnect
            print("    ℹ️  Simulating server disconnect...")

            # Close the socket first
            await self.client.socket_manager.socket.close()

            print(
                self.client.socket_manager.socket.adapter.is_open(),
                "===========================================",
            )

            # Wait for socket to be disconnected
            await asyncio.sleep(0.5)
            assert not await self.client.socket_manager.is_connected(), (
                "Socket should be disconnected"
            )
            print("    ℹ️  Socket disconnected")

            # Now trigger the ondisconnect handler to simulate server disconnect
            # This will trigger the auto-reconnect logic
            if self.client.socket_manager.socket.ondisconnect:
                print("    ℹ️  Triggering disconnect handler...")
                await self.client.socket_manager.socket.ondisconnect(
                    "simulated_disconnect"
                )

            # Wait for auto-reconnect by polling connection status
            # The reconnect logic uses exponential backoff starting at 5 seconds
            print("    ℹ️  Waiting for auto-reconnect (up to 15 seconds)...")

            max_wait = 15  # seconds
            poll_interval = 0.5  # seconds
            elapsed = 0

            while elapsed < max_wait:
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

                if await self.client.socket_manager.is_connected():
                    print(f"    ℹ️  Auto-reconnect detected after {elapsed:.1f}s")
                    break
            else:
                raise AssertionError("Socket did not reconnect within timeout period")

            # Wait for socket to be fully ready (fresh adapter needs time to stabilize)
            print("    ℹ️  Waiting for socket to be fully ready...")
            await asyncio.sleep(1.5)

            # Verify reconnection
            is_reconnected = await self.client.socket_manager.is_connected()
            assert is_reconnected, "Socket should be reconnected"
            print("    ℹ️  Socket successfully reconnected and ready to send")

            # Test functionality: Send a message
            # Fetch clan and channel data directly from API (not cache)
            print("    ℹ️  Fetching clan and channel data from API...")

            clan = self.client.clans.get(self.config.clan_id)
            if not clan:
                raise AssertionError("Clan not found after reconnect")

            # Use fetch() to get fresh channel data from API
            channel = await clan.channels.fetch(self.config.channel_id)
            if not channel:
                raise AssertionError("Channel not found after reconnect")

            print("    ℹ️  Clan and channel loaded successfully")

            # Send test message
            result = await channel.send(
                content=ChannelMessageContent(t="✅ Functionality test after reconnect")
            )
            assert result is not None, "Should be able to send message after reconnect"
            print("    ℹ️  Message sent successfully after reconnect")

            self.log_result("Functionality After Reconnect", True)
        except Exception as e:
            import traceback

            traceback.print_exc()

            self.log_result("Functionality After Reconnect", False, str(e))
