import asyncio

import pytest

from mezon.constants import Events
from mezon.managers.event import EventManager


class TestEventManager:
    def test_on_off_and_has_listeners(self):
        manager = EventManager()

        def handler(message):
            return message

        manager.on(Events.CHANNEL_MESSAGE, handler)

        assert manager.has_listeners(Events.CHANNEL_MESSAGE) is True

        manager.off(Events.CHANNEL_MESSAGE, handler)

        assert manager.has_listeners(Events.CHANNEL_MESSAGE) is False

    def test_off_without_handler_removes_all(self):
        manager = EventManager()

        def handler_one(message):
            return message

        def handler_two(message):
            return message

        manager.on(Events.CHANNEL_MESSAGE, handler_one)
        manager.on(Events.CHANNEL_MESSAGE, handler_two)
        manager.off(Events.CHANNEL_MESSAGE)

        assert manager.has_listeners(Events.CHANNEL_MESSAGE) is False

    @pytest.mark.asyncio
    async def test_emit_runs_default_handlers_before_user_handlers(self):
        manager = EventManager()
        calls = []
        user_done = asyncio.Event()

        async def default_async(message):
            await asyncio.sleep(0)
            calls.append(("default_async", message))

        def default_sync(message):
            calls.append(("default_sync", message))

        async def user_async(message):
            calls.append(("user_async", message))
            user_done.set()

        def user_sync(message):
            calls.append(("user_sync", message))

        default_async._is_default_handler = True
        default_sync._is_default_handler = True

        manager.on(Events.CHANNEL_MESSAGE, user_async)
        manager.on(Events.CHANNEL_MESSAGE, default_async)
        manager.on(Events.CHANNEL_MESSAGE, user_sync)
        manager.on(Events.CHANNEL_MESSAGE, default_sync)

        await manager.emit(Events.CHANNEL_MESSAGE, "payload")
        await asyncio.wait_for(user_done.wait(), timeout=1)
        await asyncio.sleep(0)

        default_calls = [name for name, _ in calls[:2]]
        user_calls = [name for name, _ in calls[2:]]

        assert set(default_calls) == {"default_sync", "default_async"}
        assert set(user_calls) == {"user_async", "user_sync"}

    @pytest.mark.asyncio
    async def test_emit_ignores_missing_event(self):
        manager = EventManager()

        await manager.emit(Events.CHANNEL_MESSAGE, "payload")

    def test_handle_task_exception_consumes_failure(self):
        manager = EventManager()

        async def explode():
            raise RuntimeError("boom")

        async def run():
            task = asyncio.create_task(explode())
            await asyncio.sleep(0)
            manager._handle_task_exception(task, Events.CHANNEL_MESSAGE)

        asyncio.run(run())
