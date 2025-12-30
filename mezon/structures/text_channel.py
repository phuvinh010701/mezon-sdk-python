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

from typing import Optional, List, Any, TYPE_CHECKING
from mezon.models import (
    ApiChannelDescription,
    ApiMessageAttachment,
    ApiMessageMention,
    ApiMessageRef,
    ChannelMessageAck,
    ChannelMessageContent,
)
from mezon.managers.cache import CacheManager
from mezon.messages.db import MessageDB

from mezon.utils.helper import (
    convert_channeltype_to_channel_mode,
)
from mezon.constants import TypeMessage
from mezon.utils.logger import get_logger
from .message import Message

if TYPE_CHECKING:
    from mezon.managers.socket import SocketManager
    from .clan import Clan

logger = get_logger(__name__)


class TextChannel:
    """
    Represents a text channel in a Mezon clan.

    This class provides methods for sending messages, managing quick menus,
    and interacting with voice channels.
    """

    def __init__(
        self,
        init_channel_data: ApiChannelDescription,
        clan: "Clan",
        socket_manager: "SocketManager",
        message_db: MessageDB,
    ):
        """
        Initialize a TextChannel.

        Args:
            init_channel_data: Channel description data
            clan: The clan this channel belongs to
            socket_manager: Socket manager for sending messages
            message_db: Database for message caching
        """
        self.id: Optional[str] = init_channel_data.channel_id
        self.name: Optional[str] = init_channel_data.channel_label
        self.channel_type: Optional[int] = init_channel_data.type
        self.is_private: bool = bool(init_channel_data.channel_private)
        self.category_id: str = init_channel_data.category_id or ""
        self.category_name: str = init_channel_data.category_name or ""
        self.parent_id: str = init_channel_data.parent_id or ""
        self.meeting_code: str = init_channel_data.meeting_code or ""
        self.clan = clan

        self.messages: CacheManager[str, Message] = CacheManager(
            fetcher=self.message_fetcher, max_size=200
        )

        self.socket_manager = socket_manager
        self.message_db = message_db

    async def message_fetcher(self, message_id: str) -> "Message":
        message_data = await self.message_db.get_message_by_id(message_id, self.id)
        if not message_data:
            raise ValueError(f"Message {message_id} not found on channel {self.id}!")
        return Message(message_data, self, self.socket_manager)

    async def send(
        self,
        content: ChannelMessageContent,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        mention_everyone: Optional[bool] = None,
        anonymous_message: Optional[bool] = None,
        topic_id: Optional[str] = None,
        code: Optional[int] = None,
    ) -> ChannelMessageAck:
        """
        Send a message to this channel.

        Args:
            content: Message content
            mentions: List of user mentions
            attachments: List of attachments
            mention_everyone: Whether to mention everyone
            anonymous_message: Whether the message is anonymous
            topic_id: Topic ID for threaded messages
            code: Message type code

        Returns:
            The message acknowledgement
        """
        data_send = {
            "clan_id": self.clan.id,
            "channel_id": self.id,
            "mode": convert_channeltype_to_channel_mode(self.channel_type),
            "is_public": not self.is_private,
            "content": content,
            "mentions": mentions,
            "attachments": attachments,
            "anonymous_message": anonymous_message,
            "mention_everyone": mention_everyone,
            "code": code,
            "topic_id": topic_id,
        }
        return await self.socket_manager.write_chat_message(**data_send)

    async def send_ephemeral(
        self,
        receiver_id: str,
        content: Any,
        reference_message_id: Optional[str] = None,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        mention_everyone: Optional[bool] = None,
        anonymous_message: Optional[bool] = None,
        topic_id: Optional[str] = None,
        code: int = TypeMessage.EPHEMERAL,
    ) -> Any:
        """
        Send an ephemeral message (visible only to specific user).

        Args:
            receiver_id: The user ID who will receive the message
            content: Message content
            reference_message_id: ID of message being referenced
            mentions: List of user mentions
            attachments: List of attachments
            mention_everyone: Whether to mention everyone
            anonymous_message: Whether the message is anonymous
            topic_id: Topic ID for threaded messages
            code: Message type code (default: TypeMessage.Ephemeral)

        Returns:
            The message acknowledgement
        """
        references: List[ApiMessageRef] = []

        if reference_message_id:
            message_ref = await self.messages.fetch(reference_message_id)
            user = await self.clan.users.fetch(message_ref.sender_id)

            references = [
                ApiMessageRef(
                    message_ref_id=message_ref.id,
                    message_sender_id=message_ref.sender_id,
                    message_sender_username=user.clan_nick
                    or user.display_name
                    or user.username,
                    mesages_sender_avatar=user.clan_avatar or user.avatar,
                    content=str(message_ref.content),
                )
            ]

        data_send = {
            "receiver_id": receiver_id,
            "clan_id": self.clan.id,
            "channel_id": self.id,
            "mode": convert_channeltype_to_channel_mode(self.channel_type),
            "is_public": not self.is_private,
            "content": content,
            "mentions": mentions,
            "attachments": attachments,
            "references": references,
            "anonymous_message": anonymous_message,
            "mention_everyone": mention_everyone,
            "code": code,
            "topic_id": topic_id,
        }
        return await self.socket_manager.write_ephemeral_message(**data_send)

    def __repr__(self) -> str:
        """String representation of the channel."""
        return f"<TextChannel id={self.id} name={self.name} type={self.channel_type}>"
