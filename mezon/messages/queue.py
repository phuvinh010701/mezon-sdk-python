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
from typing import Callable, TypeVar, Awaitable, Tuple
from aiolimiter import AsyncLimiter
from mezon.utils.logger import get_logger
from mezon.constants.rate_limit import (
    WEBSOCKET_PB_RATE_LIMIT,
    WEBSOCKET_PB_RATE_LIMIT_PERIOD,
)

logger = get_logger(__name__)

T = TypeVar("T")


class MessageQueue:
    """
    An async throttle queue using aiolimiter for rate limiting.
    """

    def __init__(
        self,
        max_per_second: int = WEBSOCKET_PB_RATE_LIMIT,
        rate_limit_period: float = WEBSOCKET_PB_RATE_LIMIT_PERIOD,
    ):
        """
        Initialize the message queue.

        Args:
            max_per_second: Maximum number of operations per second (default: WEBSOCKET_PB_RATE_LIMIT)
            rate_limit_period: Time period in seconds (default: WEBSOCKET_PB_RATE_LIMIT_PERIOD)
        """
        self._limiter = AsyncLimiter(max_per_second, rate_limit_period)
        self._queue: asyncio.Queue[
            Tuple[Callable[[], Awaitable[T]], asyncio.Future]
        ] = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None
        self._shutdown = False

    def enqueue(self, task: Callable[[], Awaitable[T]]) -> asyncio.Future[T]:
        """
        Enqueue an async operation to be executed.

        Args:
            task: An async callable that returns a value

        Returns:
            A Future that will contain the result of the operation
        """
        if self._shutdown:
            raise RuntimeError("Cannot enqueue to a shutdown queue")

        future: asyncio.Future[T] = asyncio.Future()
        self._queue.put_nowait((task, future))

        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())

        return future

    async def _worker(self) -> None:
        """
        Worker loop that processes queue items with rate limiting.
        Blocks indefinitely until items are available or shutdown is called.
        """
        try:
            while not self._shutdown:
                task, future = await self._queue.get()

                async with self._limiter:
                    try:
                        result = await task()
                        if not future.done():
                            future.set_result(result)
                    except Exception as e:
                        logger.error(f"Error executing queued operation: {e}")
                        if not future.done():
                            future.set_exception(e)
                    finally:
                        self._queue.task_done()

        except Exception as e:
            logger.error(f"Worker loop error: {e}")
        finally:
            logger.debug("Worker shut down")

    @property
    def size(self) -> int:
        """Get the current queue size."""
        return self._queue.qsize()

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return self._queue.empty()

    @property
    def current_rate(self) -> float:
        """
        Get the current available capacity from the rate limiter.

        Returns:
            Current available capacity (operations that can be executed immediately)
        """
        return self._limiter.max_rate - self._limiter._level

    async def wait_for_completion(self) -> None:
        """
        Wait for all queued operations to complete.

        This method will block until the queue is empty and all tasks
        have finished executing.
        """
        await self._queue.join()

    async def shutdown(self) -> None:
        """
        Gracefully shutdown the worker.

        Waits for all pending tasks to complete, then stops the worker.
        """
        if self._shutdown:
            return

        await self.wait_for_completion()

        self._shutdown = True

        if self._worker_task and not self._worker_task.done():
            try:
                self._queue.put_nowait((lambda: None, asyncio.Future()))
            except asyncio.QueueFull:
                pass

            try:
                await asyncio.wait_for(self._worker_task, timeout=1.0)
            except asyncio.TimeoutError:
                logger.warning("Worker did not shutdown gracefully, cancelling")
                self._worker_task.cancel()
