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
from abc import ABC, abstractmethod
from typing import Optional, Any
import websockets
from websockets.asyncio.client import ClientConnection
from urllib.parse import quote

from aiolimiter import AsyncLimiter
from websockets.protocol import State
from mezon.protobuf.rtapi import realtime_pb2
import logging
from mezon.protobuf.utils import encode_protobuf
from mezon.constants.rate_limit import (
    WEBSOCKET_PB_RATE_LIMIT,
    WEBSOCKET_PB_RATE_LIMIT_PERIOD,
)

logger = logging.getLogger(__name__)


class WebSocketAdapter(ABC):
    """
    An interface used by Mezon's web socket to determine the payload protocol.
    """

    def __init__(self):
        self._socket: Optional[ClientConnection] = None
        self._listen_task: Optional[asyncio.Task] = None

    @abstractmethod
    async def connect(
        self, scheme: str, host: str, port: str, create_status: bool, token: str
    ) -> None:
        """
        Connect to WebSocket server.

        Args:
            scheme: URL scheme (ws:// or wss://)
            host: Server host
            port: Server port
            create_status: Whether to create status
            token: Authentication token
        """
        pass

    @abstractmethod
    async def send(self, message: Any) -> None:
        """
        Send message through WebSocket.

        Args:
            message: Message to send
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close WebSocket connection."""
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """
        Check if WebSocket is open.

        Returns:
            True if open, False otherwise
        """
        pass


class WebSocketAdapterPb(WebSocketAdapter):
    """
    Protobuf-based WebSocket adapter.

    This adapter handles binary protobuf messages over WebSocket.
    """

    def __init__(
        self,
        rate_limit: float = WEBSOCKET_PB_RATE_LIMIT,
        rate_limit_period: float = WEBSOCKET_PB_RATE_LIMIT_PERIOD,
    ):
        """
        Initialize WebSocket adapter with rate limiting.

        Args:
            rate_limit: Maximum number of messages per period (default: 10)
            rate_limit_period: Time period in seconds (default: 1.0)
        """
        super().__init__()
        self._rate_limiter = AsyncLimiter(rate_limit, rate_limit_period)

    async def connect(
        self, scheme: str, host: str, port: str, create_status: bool, token: str
    ) -> None:
        """Connect to WebSocket server with protobuf protocol."""
        url = f"{scheme}{host}:{port}/ws?lang=en&status={quote(str(create_status).lower())}&token={quote(token)}&format=protobuf"
        try:
            self._socket = await websockets.connect(
                url,
                subprotocols=["protobuf"],
            )
        except Exception:
            raise

    def _encode_protobuf(self, message: realtime_pb2.Envelope) -> bytes:
        """
        Encode message to protobuf.

        Args:
            message: Message envelope

        Returns:
            Encoded protobuf bytes
        """

        return message.SerializeToString()

    async def send(self, message: Any) -> None:
        """
        Send message through WebSocket with rate limiting.

        This method applies rate limiting to all outgoing messages to prevent
        hitting API rate limits on the server side.

        Args:
            message: Message to send (Envelope or bytes)

        Raises:
            ValueError: If message type is invalid
        """
        if self._socket:
            async with self._rate_limiter:
                if isinstance(message, realtime_pb2.Envelope):
                    await self._socket.send(encode_protobuf(message))
                elif isinstance(message, bytes):
                    await self._socket.send(message)
                else:
                    raise ValueError(f"Invalid message type: {type(message)}")

    async def close(self) -> None:
        """Close WebSocket connection."""
        if self.is_open():
            try:
                await self._socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")

    def is_open(self) -> bool:
        """Check if WebSocket is open."""
        return self._socket is not None and self._socket.state == State.OPEN
