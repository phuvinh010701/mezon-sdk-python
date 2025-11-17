"""
Copyright 2020 The Mezon Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
import time
from typing import Callable, TypeVar, Awaitable, List, Tuple
from mezon.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")

MAX_PER_SECOND = 80


class MessageQueue:
    """
    An async throttle queue using a sliding window rate limiter.

    This queue ensures operations are rate-limited using a sliding window
    approach, allowing up to max_per_second operations within any 1-second window.
    """

    def __init__(self, max_per_second: int = MAX_PER_SECOND):
        """
        Initialize the message queue.

        Args:
            max_per_second: Maximum number of operations per second (default: 80)
        """
        self._timestamps: List[float] = []
        self._queue: List[Tuple[Callable[[], Awaitable[T]], asyncio.Future]] = []
        self._max_per_second = max_per_second
        self._is_running = False
        self._loop_task: asyncio.Task | None = None

    def enqueue(self, task: Callable[[], Awaitable[T]]) -> asyncio.Future[T]:
        """
        Enqueue an async operation to be executed.

        Args:
            task: An async callable that returns a value

        Returns:
            A Future that will contain the result of the operation
        """
        future: asyncio.Future[T] = asyncio.Future()
        self._queue.append((task, future))

        if not self._is_running:
            self._start()

        return future

    def _start(self) -> None:
        """Start the processing loop."""
        if self._is_running:
            return

        self._is_running = True
        self._loop_task = asyncio.create_task(self._loop())

    async def _loop(self) -> None:
        """
        Main processing loop using sliding window rate limiting.

        Continuously processes queued tasks while respecting the rate limit.
        """
        try:
            while True:
                self._cleanup_timestamps()

                if (
                    len(self._queue) > 0
                    and len(self._timestamps) < self._max_per_second
                ):
                    task, future = self._queue.pop(0)

                    self._timestamps.append(time.time())

                    try:
                        result = await task()
                        if not future.done():
                            future.set_result(result)
                    except Exception as e:
                        logger.error(f"Error executing queued operation: {e}")
                        if not future.done():
                            future.set_exception(e)

                await asyncio.sleep(0.01)

                if len(self._queue) == 0 and len(self._timestamps) == 0:
                    await asyncio.sleep(0.1)
                    if len(self._queue) == 0:
                        break

        finally:
            self._is_running = False

    def _cleanup_timestamps(self) -> None:
        """
        Remove timestamps older than 1 second.

        This implements the sliding window by keeping only timestamps
        from the last second.
        """
        now = time.time()
        self._timestamps = [t for t in self._timestamps if now - t < 1.0]

    @property
    def size(self) -> int:
        """Get the current queue size."""
        return len(self._queue)

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._queue) == 0

    @property
    def current_rate(self) -> int:
        """
        Get the current number of operations in the last second.

        Returns:
            Number of operations executed in the last 1 second
        """
        self._cleanup_timestamps()
        return len(self._timestamps)

    async def wait_for_completion(self) -> None:
        """
        Wait for all queued operations to complete.

        This method will block until the queue is empty and all tasks
        have finished executing.
        """
        while len(self._queue) > 0 or self._is_running:
            await asyncio.sleep(0.01)
