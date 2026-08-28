import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field

from mezon.constants import Events

logger = logging.getLogger(__name__)


@dataclass
class _HandlerBucket:
    """Handlers for one event, pre-partitioned by how `emit` must run them."""

    sync_default: list[Callable] = field(default_factory=list)
    async_default: list[Callable] = field(default_factory=list)
    user: list[Callable] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.sync_default or self.async_default or self.user)

    def remove(self, handler: Callable) -> None:
        for bucket in (self.sync_default, self.async_default, self.user):
            if handler in bucket:
                bucket.remove(handler)


class EventManager:
    """
    EventManager handles registration and emission of events.

    This allows users to register handlers for specific events and have them
    called when those events are emitted from the websocket connection.
    """

    def __init__(self):
        self._buckets: dict[str, _HandlerBucket] = {}

    def on(self, event_name: Events, handler: Callable) -> None:
        """
        Register an event handler for a specific event.

        Args:
            event_name: The name of the event to listen for
            handler: The callback function to execute when the event occurs
        """
        bucket = self._buckets.setdefault(event_name, _HandlerBucket())
        if getattr(handler, "_is_default_handler", False):
            if asyncio.iscoroutinefunction(handler):
                bucket.async_default.append(handler)
            else:
                bucket.sync_default.append(handler)
        else:
            bucket.user.append(handler)

    def off(self, event_name: Events, handler: Callable = None) -> None:
        """
        Unregister an event handler.

        Args:
            event_name: The name of the event
            handler: The specific handler to remove. If None, removes all handlers for the event.
        """
        bucket = self._buckets.get(event_name)
        if bucket is None:
            return

        if handler is None:
            del self._buckets[event_name]
        else:
            bucket.remove(handler)
            if bucket.is_empty():
                del self._buckets[event_name]

    async def emit(self, event_name: Events, *args, **kwargs) -> None:
        """
        Emit an event to all registered handlers.

        Default handlers run first in parallel and are awaited.
        User handlers are fired and forgotten (run concurrently without blocking).

        Args:
            event_name: The name of the event to emit
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        bucket = self._buckets.get(event_name)
        if bucket is None or bucket.is_empty():
            return

        for handler in bucket.sync_default:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in sync default handler for '{event_name}': {e}",
                    exc_info=True,
                )

        if bucket.async_default:
            try:
                async with asyncio.TaskGroup() as tg:
                    for handler in bucket.async_default:
                        tg.create_task(handler(*args, **kwargs))
            except* Exception as eg:
                for exc in eg.exceptions:
                    logger.error(
                        f"Error in async default handler for '{event_name}': {exc}",
                        exc_info=exc,
                    )

        for handler in bucket.user:
            try:
                if asyncio.iscoroutinefunction(handler):
                    task = asyncio.create_task(handler(*args, **kwargs))
                    task.add_done_callback(
                        lambda t, ev=event_name: self._handle_task_exception(t, ev)
                    )
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error scheduling user handler for '{event_name}': {e}",
                    exc_info=True,
                )

    def _handle_task_exception(self, task: asyncio.Task, event_name: str) -> None:
        """Handle exceptions from background event handler tasks."""
        try:
            task.result()
        except Exception as e:
            logger.exception(f"Error in async event handler for '{event_name}': {e}")

    def has_listeners(self, event_name: Events) -> bool:
        """
        Check if there are any listeners for a specific event.

        Args:
            event_name: The name of the event

        Returns:
            True if there are listeners, False otherwise
        """
        bucket = self._buckets.get(event_name)
        return bucket is not None and not bucket.is_empty()
