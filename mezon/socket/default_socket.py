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
from typing import Dict, Optional, Any, List, TypeVar, Type

from mezon.protobuf.rtapi import realtime_pb2
from mezon.utils.logger import get_logger
from mezon.protobuf.utils import parse_protobuf
from google.protobuf import json_format
from pydantic import BaseModel
import google.protobuf.message

from .promise_executor import PromiseExecutor
from .websocket_adapter import WebSocketAdapterPb
from .message_builder import (
    ChannelMessageBuilder,
    ChannelMessageUpdateBuilder,
    EphemeralMessageBuilder,
    MessageReactionBuilder,
)
from mezon.managers.event import EventManager
from ..session import Session
from ..models import (
    ChannelMessageAck,
    ApiMessageMention,
    ApiMessageAttachment,
    ApiMessageRef,
    ApiMessageReaction,
    ChannelMessageContent,
)

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


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
                        asyncio.create_task(self._emit_event_from_envelope(envelope))

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
    ) -> Optional[realtime_pb2.Envelope]:
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
            logger.error(f"Request with cid {cid} was cancelled due to timeout")
            raise TimeoutError(f"Request with cid {cid} timed out after {timeout_ms}ms")

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

    async def _send_envelope_with_field(
        self,
        field_name: str,
        message: google.protobuf.message.Message,
        timeout_ms: Optional[int] = None,
    ) -> Optional[realtime_pb2.Envelope]:
        """
        Generic method to send an envelope with a specific field set.

        Args:
            field_name: Name of the field to set in the envelope
            message: Protobuf message to attach to the envelope
            timeout_ms: Optional timeout in milliseconds

        Returns:
            Response envelope from server
        """
        envelope = realtime_pb2.Envelope()
        getattr(envelope, field_name).CopyFrom(message)
        return await self._send_with_cid(envelope, timeout_ms)

    def _handle_response(
        self,
        response: Optional[realtime_pb2.Envelope],
        field_name: str,
        model_class: Type[T],
        error_message: str,
    ) -> T:
        """
        Generic method to handle protobuf response and convert to Pydantic model.

        Args:
            response: Envelope response from server
            field_name: Expected field name in the response
            model_class: Pydantic model class to validate against
            error_message: Error message to raise if validation fails

        Returns:
            Validated Pydantic model instance

        Raises:
            Exception: If response doesn't contain expected field
        """
        if response and response.HasField(field_name):
            payload = getattr(response, field_name)
            payload_dict = json_format.MessageToDict(
                payload, preserving_proto_field_name=True
            )
            return model_class.model_validate(payload_dict)

        logger.debug(f"Response: {response}")
        raise Exception(error_message)

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

        response = await self._send_envelope_with_field(
            "channel_message_send", channel_message_send
        )
        return self._handle_response(
            response,
            "channel_message_ack",
            ChannelMessageAck,
            "Server did not return a channel_message_send acknowledgement.",
        )

    async def update_chat_message(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        message_id: str,
        content: ChannelMessageContent,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        hide_editted: bool = False,
        topic_id: Optional[str] = None,
        is_update_msg_topic: Optional[bool] = None,
    ) -> ChannelMessageAck:
        """
        Update a previously sent channel message.

        Args:
            clan_id: Clan ID
            channel_id: Channel ID where the message exists
            mode: Channel mode
            is_public: Whether the channel is public
            message_id: Identifier of the message to update
            content: Updated message content
            mentions: Updated mentions list
            attachments: Updated attachments list
            hide_editted: Whether to suppress the edited indicator
            topic_id: Topic ID for threaded messages
            is_update_msg_topic: Whether to update the topic metadata

        Returns:
            ChannelMessageAck acknowledging the update
        """

        channel_message_update = ChannelMessageUpdateBuilder.build(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            message_id=message_id,
            content=content,
            mentions=mentions,
            attachments=attachments,
            hide_editted=hide_editted,
            topic_id=topic_id,
            is_update_msg_topic=is_update_msg_topic,
        )

        response = await self._send_envelope_with_field(
            "channel_message_update", channel_message_update
        )
        return self._handle_response(
            response,
            "channel_message_ack",
            ChannelMessageAck,
            "Server did not return a channel_message_update acknowledgement.",
        )

    async def write_message_reaction(
        self,
        id: str,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        message_id: str,
        emoji_id: str,
        emoji: str,
        count: int,
        message_sender_id: str,
        action_delete: bool = False,
    ) -> ApiMessageReaction:
        """
        Send a reaction event for a channel message.

        Args:
            id: Identifier of the reaction payload
            clan_id: Clan ID containing the channel
            channel_id: Channel ID containing the message
            mode: Channel mode
            is_public: Whether the channel is public
            message_id: Message identifier to react to
            emoji_id: Emoji identifier
            emoji: Emoji short name
            count: Emoji count
            message_sender_id: Original message sender identifier
            action_delete: Whether to remove the reaction

        Returns:
            ApiMessageReaction acknowledgement from the server.
        """

        message_reaction = MessageReactionBuilder.build(
            id=id,
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            message_id=message_id,
            emoji_id=emoji_id,
            emoji=emoji,
            count=count,
            message_sender_id=message_sender_id,
            action_delete=action_delete,
        )

        response = await self._send_envelope_with_field(
            "message_reaction_event", message_reaction
        )
        return self._handle_response(
            response,
            "message_reaction_event",
            ApiMessageReaction,
            "Server did not return a message_reaction_event acknowledgement.",
        )

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

        response = await self._send_envelope_with_field(
            "ephemeral_message_send", ephemeral_message_send
        )
        return self._handle_response(
            response,
            "channel_message",
            ChannelMessageAck,
            "Server did not return an ephemeral_message_send acknowledgement.",
        )

    async def leave_chat(
        self,
        clan_id: str,
        channel_id: str,
        channel_type: int,
        is_public: bool,
    ) -> None:
        """
        Leave a channel chat.

        Args:
            clan_id: Clan ID
            channel_id: Channel ID to leave
            channel_type: Type of the channel
            is_public: Whether the channel is public
        """
        envelope = realtime_pb2.Envelope()
        channel_leave = realtime_pb2.ChannelLeave(
            clan_id=clan_id,
            channel_id=channel_id,
            channel_type=channel_type,
            is_public=is_public,
        )
        envelope.channel_leave.CopyFrom(channel_leave)
        await self._send_with_cid(envelope)

    async def remove_chat_message(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        message_id: str,
        topic_id: Optional[str] = None,
    ) -> ChannelMessageAck:
        """
        Remove/delete a message from a channel.

        Args:
            clan_id: Clan ID
            channel_id: Channel ID where the message exists
            mode: Channel mode
            is_public: Whether the channel is public
            message_id: ID of the message to remove
            topic_id: Optional topic ID for threaded messages

        Returns:
            ChannelMessageAck: Acknowledgement of the deletion
        """
        envelope = realtime_pb2.Envelope()
        channel_message_remove = realtime_pb2.ChannelMessageRemove(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            message_id=message_id,
        )
        if topic_id:
            channel_message_remove.topic_id = topic_id

        envelope.channel_message_remove.CopyFrom(channel_message_remove)
        response = await self._send_with_cid(envelope)

        return self._handle_response(
            response,
            "channel_message_ack",
            ChannelMessageAck,
            "Server did not return a channel_message_remove acknowledgement.",
        )

    async def write_message_typing(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
    ) -> Any:
        """
        Send typing indicator to a channel.

        Args:
            clan_id: Clan ID
            channel_id: Channel ID where user is typing
            mode: Channel mode
            is_public: Whether the channel is public

        Returns:
            MessageTypingEvent acknowledgement
        """
        envelope = realtime_pb2.Envelope()
        message_typing = realtime_pb2.MessageTypingEvent(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
        )
        envelope.message_typing_event.CopyFrom(message_typing)
        response = await self._send_with_cid(envelope)

        if response and response.HasField("message_typing_event"):
            return json_format.MessageToDict(response.message_typing_event)
        return None

    async def write_last_seen_message(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        message_id: str,
        timestamp_seconds: int,
    ) -> Any:
        """
        Mark a message as last seen/read.

        Args:
            clan_id: Clan ID
            channel_id: Channel ID where the message exists
            mode: Channel mode
            message_id: ID of the last seen message
            timestamp_seconds: Timestamp when the message was seen

        Returns:
            LastSeenMessageEvent acknowledgement
        """
        envelope = realtime_pb2.Envelope()
        last_seen = realtime_pb2.LastSeenMessageEvent(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            message_id=message_id,
            timestamp_seconds=timestamp_seconds,
        )
        envelope.last_seen_message_event.CopyFrom(last_seen)
        response = await self._send_with_cid(envelope)

        if response and response.HasField("last_seen_message_event"):
            return json_format.MessageToDict(response.last_seen_message_event)
        return None

    async def write_last_pin_message(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        message_id: str,
        timestamp_seconds: int,
        operation: int,
    ) -> Any:
        """
        Pin or unpin a message in a channel.

        Args:
            clan_id: Clan ID
            channel_id: Channel ID where the message exists
            mode: Channel mode
            is_public: Whether the channel is public
            message_id: ID of the message to pin/unpin
            timestamp_seconds: Timestamp of the operation
            operation: 1 for pin, 0 for unpin

        Returns:
            LastPinMessageEvent acknowledgement
        """
        envelope = realtime_pb2.Envelope()
        last_pin = realtime_pb2.LastPinMessageEvent(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            message_id=message_id,
            timestamp_seconds=timestamp_seconds,
            operation=operation,
        )
        envelope.last_pin_message_event.CopyFrom(last_pin)
        response = await self._send_with_cid(envelope)

        if response and response.HasField("last_pin_message_event"):
            return json_format.MessageToDict(response.last_pin_message_event)
        return None

    async def write_custom_status(
        self,
        clan_id: str,
        status: str,
    ) -> Any:
        """
        Set a custom status for a clan.

        Args:
            clan_id: Clan ID to set status for
            status: Custom status text

        Returns:
            CustomStatusEvent acknowledgement
        """
        envelope = realtime_pb2.Envelope()
        custom_status = realtime_pb2.CustomStatusEvent(
            clan_id=clan_id,
            status=status,
        )
        envelope.custom_status_event.CopyFrom(custom_status)
        response = await self._send_with_cid(envelope)

        if response and response.HasField("custom_status_event"):
            return json_format.MessageToDict(response.custom_status_event)
        return None

    async def write_voice_joined(
        self,
        id: str,
        clan_id: str,
        clan_name: str,
        voice_channel_id: str,
        voice_channel_label: str,
        participant: str,
        last_screenshot: str = "",
    ) -> Any:
        """
        Notify that a user joined a voice channel.

        Args:
            id: Event ID
            clan_id: Clan ID
            clan_name: Clan name
            voice_channel_id: Voice channel ID
            voice_channel_label: Voice channel name/label
            participant: Participant user ID
            last_screenshot: Optional screenshot URL

        Returns:
            VoiceJoinedEvent acknowledgement
        """
        envelope = realtime_pb2.Envelope()
        voice_joined = realtime_pb2.VoiceJoinedEvent(
            id=id,
            clan_id=clan_id,
            clan_name=clan_name,
            voice_channel_id=voice_channel_id,
            voice_channel_label=voice_channel_label,
            participant=participant,
            last_screenshot=last_screenshot,
        )
        envelope.voice_joined_event.CopyFrom(voice_joined)
        response = await self._send_with_cid(envelope)

        if response and response.HasField("voice_joined_event"):
            return json_format.MessageToDict(response.voice_joined_event)
        return None

    async def write_voice_leaved(
        self,
        id: str,
        clan_id: str,
        voice_channel_id: str,
        voice_user_id: str,
    ) -> Any:
        """
        Notify that a user left a voice channel.

        Args:
            id: Event ID
            clan_id: Clan ID
            voice_channel_id: Voice channel ID
            voice_user_id: User ID who left

        Returns:
            VoiceLeavedEvent acknowledgement
        """
        envelope = realtime_pb2.Envelope()
        voice_leaved = realtime_pb2.VoiceLeavedEvent(
            id=id,
            clan_id=clan_id,
            voice_channel_id=voice_channel_id,
            voice_user_id=voice_user_id,
        )
        envelope.voice_leaved_event.CopyFrom(voice_leaved)
        response = await self._send_with_cid(envelope)

        if response and response.HasField("voice_leaved_event"):
            return json_format.MessageToDict(response.voice_leaved_event)
        return None

    async def check_duplicate_clan_name(self, clan_name: str) -> Dict[str, Any]:
        """
        Check if a clan name already exists.

        Args:
            clan_name: The clan name to check

        Returns:
            ClanNameExistedEvent with exists status
        """
        envelope = realtime_pb2.Envelope()
        clan_name_check = realtime_pb2.CheckNameExistedEvent(name=clan_name)
        envelope.check_name_existed_event.CopyFrom(clan_name_check)
        response = await self._send_with_cid(envelope)

        if response and response.HasField("check_name_existed_event"):
            return json_format.MessageToDict(response.check_name_existed_event)
        return None

    async def list_clan_emoji_by_clan_id(self, clan_id: str) -> Dict[str, Any]:
        """
        List all emojis for a specific clan.

        Args:
            clan_id: The clan ID

        Returns:
            Dict with emoji list from EmojiListedEvent
        """
        # TODO: Implement this method
        return None

    async def list_channel_by_user_id(self) -> Dict[str, Any]:
        """
        List all channels for the current user.

        Returns:
            ChannelDescListEvent with channel list
        """
        # TODO: Implement this method
        return None

    async def hashtag_dm_list(self, user_ids: List[str], limit: int) -> Dict[str, Any]:
        """
        Get hashtag DM list.

        Args:
            user_ids: List of user IDs
            limit: Maximum number of results

        Returns:
            HashtagDmListEvent with DM list
        """
        # TODO: Implement this method
        return None

    async def list_clan_stickers_by_clan_id(self, clan_id: str) -> Dict[str, Any]:
        """
        List all stickers for a specific clan.

        Args:
            clan_id: The clan ID

        Returns:
            StickerListedEvent with sticker list
        """
        # TODO: Implement this method
        return None

    async def get_notification_channel_setting(self, channel_id: str) -> Dict[str, Any]:
        """
        Get notification settings for a channel.

        Args:
            channel_id: The channel ID

        Returns:
            NotificationChannelSettingEvent with settings
        """
        # TODO: Implement this method
        return None

    async def get_notification_category_setting(
        self, category_id: str
    ) -> Dict[str, Any]:
        """
        Get notification settings for a category.

        Args:
            category_id: The category ID

        Returns:
            NotificationCategorySettingEvent with settings
        """
        # TODO: Implement this method
        return None

    async def get_notification_clan_setting(self, clan_id: str) -> Dict[str, Any]:
        """
        Get notification settings for a clan.

        Args:
            clan_id: The clan ID

        Returns:
            NotificationClanSettingEvent with settings
        """
        # TODO: Implement this method
        return None

    async def get_notification_react_message(self, channel_id: str) -> Dict[str, Any]:
        """
        Get notification settings for message reactions.

        Args:
            channel_id: The channel ID

        Returns:
            NotifiReactMessageEvent with settings
        """
        # TODO: Implement this method
        return None

    async def update_status(self, status: Optional[str] = None) -> None:
        """
        Update the user's online status.

        Args:
            status: Optional status string. If None, user appears offline.
        """
        # TODO: Implement this method
        return None
