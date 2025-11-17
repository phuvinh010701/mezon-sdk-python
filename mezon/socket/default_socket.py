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
from typing import Dict, Optional, Any, List

from mezon.protobuf.rtapi import realtime_pb2
from mezon.utils.logger import get_logger
from mezon.protobuf.utils import parse_protobuf

from .promise_executor import PromiseExecutor
from .websocket_adapter import WebSocketAdapterPb
from .message_builder import ChannelMessageBuilder, EphemeralMessageBuilder
from mezon.managers.event import EventManager
from ..session import Session
from ..models import (
    ChannelMessageAck,
    ApiMessageMention,
    ApiMessageAttachment,
    ApiMessageRef,
)

logger = get_logger(__name__)


class Socket:
    """
    A socket connection to Mezon server
    """

    DEFAULT_HEARTBEAT_TIMEOUT_MS = 10000
    DEFAULT_SEND_TIMEOUT_MS = 10000
    DEFAULT_CONNECT_TIMEOUT_MS = 30000

    def __init__(
        self,
        host: str,
        port: str,
        use_ssl: bool = False,
        adapter: Optional[WebSocketAdapterPb] = None,
        send_timeout_ms: int = DEFAULT_SEND_TIMEOUT_MS,
        event_manager: Optional[EventManager] = None,
    ):
        """
        Initialize Socket.

        Args:
            host: Server host
            port: Server port
            use_ssl: Whether to use SSL (wss://)
            adapter: WebSocket adapter instance
            send_timeout_ms: Timeout for send operations
            event_manager: EventManager instance for handling events
        """
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.websocket_scheme = "wss://" if use_ssl else "ws://"
        self.send_timeout_ms = send_timeout_ms
        self.event_manager = event_manager or EventManager()

        self.cids: Dict[str, PromiseExecutor] = {}
        self.next_cid = 1

        self.adapter = adapter or WebSocketAdapterPb()

        self.session: Optional[Session] = None

        self._heartbeat_timeout_ms = self.DEFAULT_HEARTBEAT_TIMEOUT_MS
        self._heartbeat_task: Optional[asyncio.Task] = None

        self.ondisconnect: Optional[callable] = None
        self.onerror: Optional[callable] = None
        self.onheartbeattimeout: Optional[callable] = None

    def generate_cid(self) -> str:
        """
        Generate a unique command ID for RPC calls.

        Returns:
            Command ID as string
        """
        cid = str(self.next_cid)
        self.next_cid += 1
        return cid

    def is_open(self) -> bool:
        """
        Check if socket is open.

        Returns:
            True if open, False otherwise
        """
        return self.adapter.is_open()

    async def close(self) -> None:
        """Close the socket connection."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        await self.adapter.close()

    async def connect(
        self,
        session: Session,
        create_status: bool = False,
        connect_timeout_ms: int = DEFAULT_CONNECT_TIMEOUT_MS,
    ) -> Session:
        """
        Connect to the WebSocket server.

        Args:
            session: User session with token
            create_status: Whether to create status
            connect_timeout_ms: Connection timeout in milliseconds

        Returns:
            The session object

        Raises:
            TimeoutError: If connection times out
            Exception: If connection fails
        """
        if self.adapter.is_open():
            return self.session

        self.session = session

        try:
            await asyncio.wait_for(
                self.adapter.connect(
                    self.websocket_scheme,
                    self.host,
                    self.port,
                    create_status,
                    session.token,
                ),
                timeout=connect_timeout_ms / 1000,
            )
            await self._start_listen()

            return session
        except asyncio.TimeoutError:
            raise TimeoutError("The socket timed out when trying to connect.")

    async def _listen(self) -> None:
        """Listen for incoming protobuf messages."""
        async for message in self.adapter._socket:
            if isinstance(message, bytes):
                envelope = parse_protobuf(message)
                logger.debug(f"Received envelope: {envelope}")

                if envelope.cid:
                    executor = self.cids.get(envelope.cid)
                    if executor:
                        if envelope.HasField("error"):
                            executor.reject(envelope.error)
                        else:
                            executor.resolve(envelope)
                    else:
                        logger.debug(f"No executor found for cid: {envelope.cid}")
                else:
                    if self.event_manager:
                        await self._emit_event_from_envelope(envelope)

    async def _start_listen(self) -> None:
        """Start the heartbeat ping-pong task."""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._ping_pong())
        asyncio.create_task(self._listen())

    def _cleanup_cid(self, cid: str, executor: PromiseExecutor) -> None:
        """
        Cleanup executor and remove from tracking dict.

        Args:
            cid: Command ID to cleanup
            executor: The executor to cleanup
        """
        if cid in self.cids:
            del self.cids[cid]
        executor.cancel()

    async def _ping_pong(self) -> None:
        """
        Heartbeat ping-pong implementation.
        Sends periodic ping messages to keep connection alive and detect timeouts.
        """
        while True:
            await asyncio.sleep(self._heartbeat_timeout_ms / 1000)

            if not self.adapter.is_open():
                logger.debug("Adapter closed, stopping heartbeat")
                return

            try:
                envelope = realtime_pb2.Envelope()
                envelope.ping.CopyFrom(realtime_pb2.Ping())

                await self._send_with_cid(envelope, self._heartbeat_timeout_ms)
                logger.debug("Heartbeat ping sent successfully")

            except Exception:
                if self.adapter.is_open():
                    logger.error("Server unreachable from heartbeat")

                    if self.onheartbeattimeout:
                        try:
                            if asyncio.iscoroutinefunction(self.onheartbeattimeout):
                                await self.onheartbeattimeout()
                            else:
                                self.onheartbeattimeout()
                        except Exception as callback_error:
                            logger.error(
                                f"Error in heartbeat timeout callback: {callback_error}"
                            )

                    await self.adapter.close()

                return

    async def _send_with_cid(
        self, message: realtime_pb2.Envelope, timeout_ms: int = None
    ) -> Any:
        """
        Send message with command ID and wait for response.
        Matches TypeScript implementation pattern.

        Args:
            message: Message to send (will have cid added)
            timeout_ms: Timeout in milliseconds (defaults to self.send_timeout_ms)

        Returns:
            Response from server (or None on timeout)

        Raises:
            Exception: If server returns error or socket is not connected
        """
        if not self.adapter.is_open():
            raise Exception("Socket connection has not been established yet.")

        loop = asyncio.get_event_loop()
        cid = self.generate_cid()
        message.cid = cid

        executor = PromiseExecutor(loop)
        self.cids[cid] = executor

        timeout_ms = timeout_ms or self.send_timeout_ms

        def on_timeout():
            """Called when timeout occurs"""
            logger.warning(
                f"Timeout waiting for response with cid: {cid} (waited {timeout_ms}ms)"
            )
            self._cleanup_cid(cid, executor)

        executor.set_timeout(timeout_ms / 1000, on_timeout)

        try:
            await self.adapter.send(message)
            result = await executor.future

            logger.debug(f"Received response for cid: {cid}")
            return result

        except asyncio.CancelledError:
            logger.debug(f"Request with cid {cid} was cancelled")
            return None

        except Exception as e:
            logger.error(f"Error with message cid {cid}: {e}")
            raise

        finally:
            self._cleanup_cid(cid, executor)

    async def _emit_event_from_envelope(self, envelope: realtime_pb2.Envelope) -> None:
        """
        Parse the envelope and emit the appropriate event.

        Args:
            envelope: The protobuf envelope to parse
        """

        field_name = envelope.WhichOneof("message")
        if field_name:
            payload = envelope.__getattribute__(field_name)
            logger.debug(f"Field name: {field_name}")
            logger.debug(f"Payload: {payload}")
            await self.event_manager.emit(field_name, payload)

    async def join_clan_chat(self, clan_id: str) -> realtime_pb2.ClanJoin:
        """
        Join a clan chat.

        Args:
            clan_id: Clan ID to join
        """

        envelope = realtime_pb2.Envelope()
        clan_join = realtime_pb2.ClanJoin(clan_id=clan_id)
        envelope.clan_join.CopyFrom(clan_join)

        await self._send_with_cid(envelope)
        return clan_join

    async def join_chat(
        self,
        clan_id: str,
        channel_id: str,
        channel_type: int,
        is_public: bool = True,
    ) -> realtime_pb2.ChannelJoin:
        """
        Join a channel chat.

        Args:
            clan_id: Clan ID
            channel_id: Channel ID to join
            channel_type: Type of the channel
            is_public: Whether the channel is public

        Returns:
            ChannelJoin message
        """
        envelope = realtime_pb2.Envelope()
        channel_join = realtime_pb2.ChannelJoin(
            clan_id=clan_id,
            channel_id=channel_id,
            channel_type=channel_type,
            is_public=is_public,
        )
        envelope.channel_join.CopyFrom(channel_join)

        await self._send_with_cid(envelope)
        return channel_join

    async def write_chat_message(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        content: Any,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        references: Optional[List[ApiMessageRef]] = None,
        anonymous_message: Optional[bool] = None,
        mention_everyone: Optional[bool] = None,
        avatar: Optional[str] = None,
        code: Optional[int] = None,
        topic_id: Optional[str] = None,
    ) -> ChannelMessageAck:
        """
        Write a message to a channel.

        Args:
            clan_id: Clan ID
            channel_id: Channel ID to send message to
            mode: Channel mode
            is_public: Whether the channel is public
            content: Message content (can be string or dict)
            mentions: Optional list of message mentions
            attachments: Optional list of message attachments
            references: Optional list of message references
            anonymous_message: Whether to send as anonymous
            mention_everyone: Whether to mention everyone
            avatar: Avatar URL for the message
            code: Message code
            topic_id: Topic ID for threaded messages

        Returns:
            ChannelMessageAck: Acknowledgement of the sent message

        Raises:
            Exception: If sending fails
        """
        channel_message_send = ChannelMessageBuilder.build(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            content=content,
            mentions=mentions,
            attachments=attachments,
            references=references,
            anonymous_message=anonymous_message,
            mention_everyone=mention_everyone,
            avatar=avatar,
            code=code,
            topic_id=topic_id,
        )

        envelope = realtime_pb2.Envelope()
        envelope.channel_message_send.CopyFrom(channel_message_send)
        await self._send_with_cid(envelope)

    async def write_ephemeral_message(
        self,
        receiver_id: str,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        content: Any,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        references: Optional[List[ApiMessageRef]] = None,
        anonymous_message: Optional[bool] = None,
        mention_everyone: Optional[bool] = None,
        avatar: Optional[str] = None,
        code: Optional[int] = None,
        topic_id: Optional[str] = None,
    ) -> ChannelMessageAck:
        ephemeral_message_send = EphemeralMessageBuilder.build(
            receiver_id=receiver_id,
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            content=content,
            mentions=mentions,
            attachments=attachments,
            references=references,
            anonymous_message=anonymous_message,
            mention_everyone=mention_everyone,
            avatar=avatar,
            code=code,
            topic_id=topic_id,
        )
        envelope = realtime_pb2.Envelope()
        envelope.ephemeral_message_send.CopyFrom(ephemeral_message_send)
        await self._send_with_cid(envelope)
