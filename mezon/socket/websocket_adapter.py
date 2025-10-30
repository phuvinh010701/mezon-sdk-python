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
import json
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
import websockets
from websockets.asyncio.client import ClientConnection
from urllib.parse import quote

from websockets.protocol import State
from mezon.managers.event import EventManager
from mezon.protobuf.rtapi import realtime_pb2
from mezon.constants import InternalEventsSocket


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


class WebSocketAdapterText(WebSocketAdapter):
    """
    A text-based socket adapter that accepts and transmits payloads over UTF-8.
    """

    async def connect(
        self, scheme: str, host: str, port: str, create_status: bool, token: str
    ) -> None:
        """Connect to WebSocket server with text protocol."""
        url = f"{scheme}{host}:{port}/ws?lang=en&status={quote(str(create_status).lower())}&token={quote(token)}"

        self._socket = await websockets.connect(
            url,
        )
        self._listen_task = asyncio.create_task(self._listen())

    async def _listen(self) -> None:
        """Listen for incoming messages."""
        try:
            async for message in self._socket:
                if isinstance(message, str):
                    try:
                        decoded = json.loads(message)

                    except json.JSONDecodeError as e:
                        print(f"Error decoding message: {e}")

        except websockets.exceptions.ConnectionClosed as e:
            if self.on_close:
                if asyncio.iscoroutinefunction(self.on_close):
                    await self.on_close(e)
                else:
                    self.on_close(e)
        except Exception as e:
            if self.on_error:
                if asyncio.iscoroutinefunction(self.on_error):
                    await self.on_error(e)
                else:
                    self.on_error(e)

    async def send(self, message: Any) -> None:
        """Send text message."""
        if self._socket and not self._socket.closed:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            await self._socket.send(message)

    async def close(self) -> None:
        """Close WebSocket connection."""
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self._socket and not self._socket.closed:
            await self._socket.close()

    def is_open(self) -> bool:
        """Check if WebSocket is open."""
        return self._socket is not None and not self._socket.closed


class WebSocketAdapterPb(WebSocketAdapter):
    """
    Protobuf-based WebSocket adapter.

    This adapter handles binary protobuf messages over WebSocket.
    """

    def __init__(self, event_manager: EventManager = None):
        super().__init__()
        self.on_message: Optional[Callable] = None
        self.on_close: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.event_manager = event_manager

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
            self._listen_task = asyncio.create_task(self._listen())

        except Exception:
            raise

    async def _listen(self) -> None:
        """Listen for incoming protobuf messages."""
        try:
            async for message in self._socket:
                if isinstance(message, bytes):
                    envelope = realtime_pb2.Envelope()
                    envelope.ParseFromString(message)

                    if self.event_manager:
                        print("emit event from envelope", envelope)
                        await self._emit_event_from_envelope(envelope)

                elif isinstance(message, str):
                    pass

        except websockets.exceptions.ConnectionClosed as e:
            if self.on_close:
                if asyncio.iscoroutinefunction(self.on_close):
                    await self.on_close(e)
                else:
                    self.on_close(e)
        except Exception as e:
            if self.on_error:
                if asyncio.iscoroutinefunction(self.on_error):
                    await self.on_error(e)
                else:
                    self.on_error(e)

    async def _emit_event_from_envelope(self, envelope: realtime_pb2.Envelope) -> None:
        """
        Parse the envelope and emit the appropriate event.

        Args:
            envelope: The protobuf envelope to parse
        """

        if envelope.HasField("channel_message"):
            await self.event_manager.emit(
                InternalEventsSocket.CHANNEL_MESSAGE.value, envelope.channel_message
            )
        elif envelope.HasField("message_reaction_event"):
            await self.event_manager.emit(
                InternalEventsSocket.MESSAGE_REACTION_EVENT.value,
                envelope.message_reaction_event,
            )
        elif envelope.HasField("user_channel_removed_event"):
            await self.event_manager.emit(
                InternalEventsSocket.USER_CHANNEL_REMOVED_EVENT.value,
                envelope.user_channel_removed_event,
            )
        elif envelope.HasField("user_clan_removed_event"):
            await self.event_manager.emit(
                InternalEventsSocket.USER_CLAN_REMOVED_EVENT.value,
                envelope.user_clan_removed_event,
            )
        elif envelope.HasField("user_channel_added_event"):
            await self.event_manager.emit(
                InternalEventsSocket.USER_CHANNEL_ADDED_EVENT.value,
                envelope.user_channel_added_event,
            )
        elif envelope.HasField("channel_created_event"):
            await self.event_manager.emit(
                InternalEventsSocket.CHANNEL_CREATED_EVENT.value,
                envelope.channel_created_event,
            )
        elif envelope.HasField("channel_deleted_event"):
            await self.event_manager.emit(
                InternalEventsSocket.CHANNEL_DELETED_EVENT.value,
                envelope.channel_deleted_event,
            )
        elif envelope.HasField("channel_updated_event"):
            await self.event_manager.emit(
                InternalEventsSocket.CHANNEL_UPDATED_EVENT.value,
                envelope.channel_updated_event,
            )
        elif envelope.HasField("role_event"):
            await self.event_manager.emit(
                InternalEventsSocket.ROLE_EVENT.value, envelope.role_event
            )
        elif envelope.HasField("give_coffee_event"):
            await self.event_manager.emit(
                InternalEventsSocket.GIVE_COFFEE_EVENT.value, envelope.give_coffee_event
            )
        elif envelope.HasField("role_assign_event"):
            await self.event_manager.emit(
                InternalEventsSocket.ROLE_ASSIGN_EVENT.value, envelope.role_assign_event
            )
        elif envelope.HasField("add_clan_user_event"):
            await self.event_manager.emit(
                InternalEventsSocket.ADD_CLAN_USER_EVENT.value,
                envelope.add_clan_user_event,
            )
        elif envelope.HasField("token_sent_event"):
            await self.event_manager.emit(
                InternalEventsSocket.TOKEN_SEND.value, envelope.token_sent_event
            )
        elif envelope.HasField("clan_event_created"):
            await self.event_manager.emit(
                InternalEventsSocket.CLAN_EVENT_CREATED.value,
                envelope.clan_event_created,
            )
        elif envelope.HasField("message_button_clicked"):
            await self.event_manager.emit(
                InternalEventsSocket.MESSAGE_BUTTON_CLICKED.value,
                envelope.message_button_clicked,
            )
        elif envelope.HasField("streaming_joined_event"):
            await self.event_manager.emit(
                InternalEventsSocket.STREAMING_JOINED_EVENT.value,
                envelope.streaming_joined_event,
            )
        elif envelope.HasField("streaming_leaved_event"):
            await self.event_manager.emit(
                InternalEventsSocket.STREAMING_LEAVED_EVENT.value,
                envelope.streaming_leaved_event,
            )
        elif envelope.HasField("dropdown_box_selected"):
            await self.event_manager.emit(
                InternalEventsSocket.DROPDOWN_BOX_SELECTED.value,
                envelope.dropdown_box_selected,
            )
        elif envelope.HasField("webrtc_signaling_fwd"):
            await self.event_manager.emit(
                InternalEventsSocket.WEBRTC_SIGNALING_FWD.value,
                envelope.webrtc_signaling_fwd,
            )
        elif envelope.HasField("voice_started_event"):
            await self.event_manager.emit(
                InternalEventsSocket.VOICE_STARTED_EVENT.value,
                envelope.voice_started_event,
            )
        elif envelope.HasField("voice_ended_event"):
            await self.event_manager.emit(
                InternalEventsSocket.VOICE_ENDED_EVENT.value, envelope.voice_ended_event
            )
        elif envelope.HasField("voice_joined_event"):
            await self.event_manager.emit(
                InternalEventsSocket.VOICE_JOINED_EVENT.value,
                envelope.voice_joined_event,
            )
        elif envelope.HasField("voice_leaved_event"):
            await self.event_manager.emit(
                InternalEventsSocket.VOICE_LEAVED_EVENT.value,
                envelope.voice_leaved_event,
            )
        elif envelope.HasField("notifications"):
            await self.event_manager.emit(
                InternalEventsSocket.NOTIFICATIONS.value, envelope.notifications
            )
        elif envelope.HasField("quick_menu_event"):
            await self.event_manager.emit(
                InternalEventsSocket.QUICK_MENU.value, envelope.quick_menu_event
            )
        elif envelope.HasField("message_typing_event"):
            await self.event_manager.emit(
                InternalEventsSocket.MESSAGE_TYPING_EVENT.value,
                envelope.message_typing_event,
            )
        elif envelope.HasField("channel_presence_event"):
            await self.event_manager.emit(
                InternalEventsSocket.CHANNEL_PRESENCE_EVENT.value,
                envelope.channel_presence_event,
            )
        elif envelope.HasField("last_pin_message_event"):
            await self.event_manager.emit(
                InternalEventsSocket.LAST_PIN_MESSAGE_EVENT.value,
                envelope.last_pin_message_event,
            )
        elif envelope.HasField("custom_status_event"):
            await self.event_manager.emit(
                InternalEventsSocket.CUSTOM_STATUS_EVENT.value,
                envelope.custom_status_event,
            )
        elif envelope.HasField("user_profile_updated_event"):
            await self.event_manager.emit(
                InternalEventsSocket.USER_PROFILE_UPDATED_EVENT.value,
                envelope.user_profile_updated_event,
            )
        elif envelope.HasField("clan_updated_event"):
            await self.event_manager.emit(
                InternalEventsSocket.CLAN_UPDATED_EVENT.value,
                envelope.clan_updated_event,
            )
        elif envelope.HasField("clan_profile_updated_event"):
            await self.event_manager.emit(
                InternalEventsSocket.CLAN_PROFILE_UPDATED_EVENT.value,
                envelope.clan_profile_updated_event,
            )
        elif envelope.HasField("stream_data"):
            await self.event_manager.emit(
                InternalEventsSocket.STREAM_DATA.value, envelope.stream_data
            )
        elif envelope.HasField("stream_presence_event"):
            await self.event_manager.emit(
                InternalEventsSocket.STREAM_PRESENCE_EVENT.value,
                envelope.stream_presence_event,
            )
        elif envelope.HasField("status_presence_event"):
            await self.event_manager.emit(
                InternalEventsSocket.STATUS_PRESENCE_EVENT.value,
                envelope.status_presence_event,
            )

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
        if self._socket:
            if isinstance(message, realtime_pb2.Envelope):
                await self._socket.send(self._encode_protobuf(message))
            elif isinstance(message, bytes):
                await self._socket.send(message)
            else:
                raise ValueError(f"Invalid message type: {type(message)}")

    async def close(self) -> None:
        """Close WebSocket connection."""
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self.is_open():
            await self._socket.close()

    def is_open(self) -> bool:
        """Check if WebSocket is open."""
        return self._socket is not None and self._socket.state == State.OPEN
