import asyncio
import traceback
from typing import Callable, Dict, List


class EventManager:
    """
    EventManager handles registration and emission of events.

    This allows users to register handlers for specific events and have them
    called when those events are emitted from the websocket connection.
    """

    def __init__(self):
        self.event_handlers: Dict[str, List[Callable]] = {}

    def on(self, event_name: str, handler: Callable) -> None:
        """
        Register an event handler for a specific event.

        Args:
            event_name: The name of the event to listen for
            handler: The callback function to execute when the event occurs
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def off(self, event_name: str, handler: Callable = None) -> None:
        """
        Unregister an event handler.

        Args:
            event_name: The name of the event
            handler: The specific handler to remove. If None, removes all handlers for the event.
        """
        if event_name not in self.event_handlers:
            return

        if handler is None:
            del self.event_handlers[event_name]
        else:
            if handler in self.event_handlers[event_name]:
                self.event_handlers[event_name].remove(handler)

            if not self.event_handlers[event_name]:
                del self.event_handlers[event_name]

    async def emit(self, event_name: str, *args, **kwargs) -> None:
        """
        Emit an event to all registered handlers.

        Args:
            event_name: The name of the event to emit
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
        """
        if event_name not in self.event_handlers:
            return

        for handler in self.event_handlers[event_name]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                print(f"Error in event handler for '{event_name}': {e}")

    def has_listeners(self, event_name: str) -> bool:
        """
        Check if there are any listeners for a specific event.

        Args:
            event_name: The name of the event

        Returns:
            True if there are listeners, False otherwise
        """
        return (
            event_name in self.event_handlers
            and len(self.event_handlers[event_name]) > 0
        )
