"""
Unit tests for PromiseExecutor class.
"""

import asyncio

import pytest

from mezon.socket.promise_executor import PromiseExecutor


class TestPromiseExecutor:
    """Test PromiseExecutor class."""

    def test_resolve_sets_result(self):
        """Test that resolve sets the future result."""

        async def test():
            loop = asyncio.get_event_loop()
            executor = PromiseExecutor(loop)
            executor.timeout_handle = loop.call_later(10, lambda: None)

            executor.resolve("success")
            result = await executor.future
            assert result == "success"

        asyncio.run(test())

    def test_reject_sets_exception(self):
        """Test that reject sets the future exception."""

        async def test():
            loop = asyncio.get_event_loop()
            executor = PromiseExecutor(loop)
            executor.timeout_handle = loop.call_later(10, lambda: None)

            error = ValueError("test error")
            executor.reject(error)

            with pytest.raises(ValueError, match="test error"):
                await executor.future

        asyncio.run(test())

    def test_reject_with_string_converts_to_exception(self):
        """Test that reject with string converts to Exception."""

        async def test():
            loop = asyncio.get_event_loop()
            executor = PromiseExecutor(loop)
            executor.timeout_handle = loop.call_later(10, lambda: None)

            executor.reject("error message")

            with pytest.raises(Exception, match="error message"):
                await executor.future

        asyncio.run(test())

    def test_set_timeout_calls_callback(self):
        """Test that set_timeout calls the callback after delay."""

        async def test():
            loop = asyncio.get_event_loop()
            executor = PromiseExecutor(loop)
            called = []

            def callback():
                called.append(True)

            executor.set_timeout(0.01, callback)
            await asyncio.sleep(0.02)

            assert len(called) == 1

        asyncio.run(test())

    def test_cancel_cancels_timeout_and_future(self):
        """Test that cancel cancels both timeout and future."""

        async def test():
            loop = asyncio.get_event_loop()
            executor = PromiseExecutor(loop)
            called = []

            def callback():
                called.append(True)

            executor.set_timeout(0.01, callback)
            executor.cancel()

            await asyncio.sleep(0.02)

            # Callback should not have been called
            assert len(called) == 0
            assert executor.future.cancelled()

        asyncio.run(test())

    def test_resolve_cancels_timeout(self):
        """Test that resolve cancels the timeout."""

        async def test():
            loop = asyncio.get_event_loop()
            executor = PromiseExecutor(loop)
            timeout_called = []

            def timeout_callback():
                timeout_called.append(True)

            executor.set_timeout(0.01, timeout_callback)
            executor.resolve("done")

            await asyncio.sleep(0.02)

            # Timeout should have been cancelled
            assert len(timeout_called) == 0
            assert await executor.future == "done"

        asyncio.run(test())

    def test_reject_cancels_timeout(self):
        """Test that reject cancels the timeout."""

        async def test():
            loop = asyncio.get_event_loop()
            executor = PromiseExecutor(loop)
            timeout_called = []

            def timeout_callback():
                timeout_called.append(True)

            executor.set_timeout(0.01, timeout_callback)
            executor.reject(ValueError("error"))

            await asyncio.sleep(0.02)

            # Timeout should have been cancelled
            assert len(timeout_called) == 0

        asyncio.run(test())

    def test_resolve_only_once(self):
        """Test that resolve only works once (future already done)."""

        async def test():
            loop = asyncio.get_event_loop()
            executor = PromiseExecutor(loop)
            executor.timeout_handle = loop.call_later(10, lambda: None)

            executor.resolve("first")
            executor.resolve("second")  # Should be ignored

            result = await executor.future
            assert result == "first"

        asyncio.run(test())

    def test_reject_only_once(self):
        """Test that reject only works once (future already done)."""

        async def test():
            loop = asyncio.get_event_loop()
            executor = PromiseExecutor(loop)
            executor.timeout_handle = loop.call_later(10, lambda: None)

            executor.reject(ValueError("first"))
            executor.reject(ValueError("second"))  # Should be ignored

            with pytest.raises(ValueError, match="first"):
                await executor.future

        asyncio.run(test())
