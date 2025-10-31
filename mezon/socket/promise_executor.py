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
from typing import Optional, Any


class PromiseExecutor:
    """
    Promise executor for handling async request/response pattern.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.future: asyncio.Future = loop.create_future()
        self.timeout_handle: Optional[asyncio.TimerHandle]

    def resolve(self, result: Any) -> None:
        """Resolve the future with a result."""
        self.timeout_handle.cancel()
        if not self.future.done():
            self.future.set_result(result)

    def reject(self, error: Any) -> None:
        """Reject the future with an error."""
        self.timeout_handle.cancel()
        if not self.future.done():
            self.future.set_exception(
                error if isinstance(error, Exception) else Exception(str(error))
            )

    def set_timeout(self, delay_seconds: float, callback) -> None:
        """Set a timeout that will call the callback after delay_seconds."""
        loop = self.future.get_loop()
        self.timeout_handle = loop.call_later(delay_seconds, callback)

    def cancel(self) -> None:
        """Cancel the executor and cleanup resources."""
        self.timeout_handle.cancel()
        self.future.cancel()
