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
from dataclasses import dataclass


from mezon.protobuf.rtapi import realtime_pb2

from .websocket_adapter import WebSocketAdapter, WebSocketAdapterPb
from ..session import Session
from ..models import (
    ChannelMessageAck,
    ApiMessageMention,
    ApiMessageAttachment,
    ApiMessageRef,
    EphemeralMessageData,
)
import json


@dataclass
class PromiseExecutor:
    event: asyncio.Event
    result: Optional[Any] = None
    error: Optional[Any] = None


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
        adapter: Optional[WebSocketAdapter] = None,
        send_timeout_ms: int = DEFAULT_SEND_TIMEOUT_MS,
        event_manager=None,
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
        self.adapter = adapter or WebSocketAdapterPb(event_manager=event_manager)
        self.send_timeout_ms = send_timeout_ms
        self.event_manager = event_manager

        # Promise executors for RPC calls
        self.cids: Dict[str, PromiseExecutor] = {}
        self.next_cid = 1

        # Session and events
        self.session: Optional[Session] = None

        # Heartbeat
        self._heartbeat_timeout_ms = self.DEFAULT_HEARTBEAT_TIMEOUT_MS
        self._heartbeat_task: Optional[asyncio.Task] = None

        # Event handlers
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

            return session
        except asyncio.TimeoutError:
            raise TimeoutError("The socket timed out when trying to connect.")

    async def _send_with_cid(self, message: realtime_pb2.Envelope) -> Any:
        """
        Send message with command ID and wait for response.

        Args:
            message: Message to send (will have cid added)

        Returns:
            Response from server

        Raises:
            TimeoutError: If response times out
            Exception: If server returns error
        """
        message.cid = self.generate_cid()
        # future = asyncio.Future()
        # self.cids[message.cid] = future
        await self.adapter.send(message)
        # result = await future
        # del self.cids[message.cid]
        # return result

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

        # TODO: Improve code quality

        content = {"t": content}
        content_str = json.dumps(content) if isinstance(content, dict) else str(content)

        channel_message_send = realtime_pb2.ChannelMessageSend(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            content=content_str,
        )

        if mentions:
            for mention in mentions:
                msg_mention = channel_message_send.mentions.add()
                if mention.user_id:
                    msg_mention.user_id = mention.user_id
                if mention.username:
                    msg_mention.username = mention.username
                if mention.role_id:
                    msg_mention.role_id = mention.role_id
                if mention.s is not None:
                    msg_mention.s = mention.s
                if mention.e is not None:
                    msg_mention.e = mention.e

        if attachments:
            for attachment in attachments:
                msg_attachment = channel_message_send.attachments.add()
                if attachment.filename:
                    msg_attachment.filename = attachment.filename
                if attachment.url:
                    msg_attachment.url = attachment.url
                if attachment.filetype:
                    msg_attachment.filetype = attachment.filetype
                if attachment.size is not None:
                    msg_attachment.size = attachment.size
                if attachment.width is not None:
                    msg_attachment.width = attachment.width
                if attachment.height is not None:
                    msg_attachment.height = attachment.height

        if references:
            for ref in references:
                msg_ref = channel_message_send.references.add()
                msg_ref.message_ref_id = ref.message_ref_id
                msg_ref.message_sender_id = ref.message_sender_id
                if ref.message_sender_username:
                    msg_ref.message_sender_username = ref.message_sender_username
                if ref.content:
                    msg_ref.content = ref.content
                if ref.has_attachment is not None:
                    msg_ref.has_attachment = ref.has_attachment

        if anonymous_message is not None:
            channel_message_send.anonymous_message = anonymous_message

        if mention_everyone is not None:
            channel_message_send.mention_everyone = mention_everyone

        if avatar:
            channel_message_send.avatar = avatar

        if code is not None:
            channel_message_send.code = code

        if topic_id:
            channel_message_send.topic_id = topic_id

        envelope = realtime_pb2.Envelope()
        envelope.channel_message_send.CopyFrom(channel_message_send)

        await self._send_with_cid(envelope)

    async def write_ephemeral_message(
        self, message: EphemeralMessageData
    ) -> ChannelMessageAck:
        raise NotImplementedError("Not implemented yet")
