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

from typing import Optional, List, Any, Dict, TYPE_CHECKING
import json
from mezon.models import (
    ApiMessageAttachment,
    ApiMessageMention,
    ApiMessageReaction,
    ApiMessageRef,
    ChannelMessageContent,
    ChannelMessageRaw,
)
from mezon.messages.queue import MessageQueue
from mezon.utils.helper import convert_channeltype_to_channel_mode
from mezon.utils.logger import get_logger

if TYPE_CHECKING:
    from .text_channel import TextChannel
    from mezon.managers.socket import SocketManager

logger = get_logger(__name__)


class Message:
    """
    Represents a message in a Mezon channel.

    This class provides methods for interacting with messages including
    replying, updating, reacting, and deleting.
    """

    def __init__(
        self,
        message_raw: ChannelMessageRaw,
        channel: "TextChannel",
        socket_manager: "SocketManager",
        message_queue: MessageQueue,
    ):
        """
        Initialize a Message.
        message_raw: ChannelMessageRaw,
        Args:
            message_raw: ChannelMessageRaw
            channel: The TextChannel this message belongs to
            socket_manager: Socket manager for sending updates
            message_queue: Message queue for rate limiting
        """
        self.id: str = message_raw.id
        self.sender_id: str = message_raw.sender_id
        self.content: ChannelMessageContent = message_raw.content
        self.mentions: Optional[List[ApiMessageMention]] = message_raw.mentions
        self.attachments: Optional[List[ApiMessageAttachment]] = message_raw.attachments
        self.reactions: Optional[List[ApiMessageReaction]] = message_raw.reactions
        self.references: Optional[List[ApiMessageRef]] = message_raw.references
        self.topic_id: Optional[str] = message_raw.topic_id
        self.create_time_seconds: Optional[int] = message_raw.create_time_seconds

        self.channel = channel
        self.socket_manager = socket_manager
        self.message_queue = message_queue

    async def reply(
        self,
        content: ChannelMessageContent,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        mention_everyone: Optional[bool] = None,
        anonymous_message: Optional[bool] = None,
        topic_id: Optional[str] = None,
        code: Optional[int] = None,
    ) -> Any:
        """
        Reply to this message.

        Args:
            content: Reply message content
            mentions: List of user mentions (optional)
            attachments: List of attachments (optional)
            mention_everyone: Whether to mention everyone (optional)
            anonymous_message: Whether the reply is anonymous (optional)
            topic_id: Topic ID (optional, defaults to this message's topic)
            code: Message type code (optional)

        Returns:
            Message acknowledgement
        """

        async def reply_operation():
            user = await self.channel.clan.users.fetch(self.sender_id)

            references: List[ApiMessageRef] = [
                ApiMessageRef(
                    message_ref_id=self.id,
                    message_sender_id=self.sender_id,
                    message_sender_username=user.clan_nick
                    or user.display_name
                    or user.username,
                    mesages_sender_avatar=user.clan_avatar or user.avatar,
                    content=json.dumps(self.content)
                    if isinstance(self.content, dict)
                    else str(self.content),
                )
            ]

            data_reply = {
                "clan_id": self.channel.clan.id,
                "mode": convert_channeltype_to_channel_mode(self.channel.channel_type),
                "is_public": not self.channel.is_private,
                "channel_id": self.channel.id,
                "content": content,
                "mentions": mentions,
                "attachments": attachments,
                "references": references,
                "anonymous_message": anonymous_message,
                "mention_everyone": mention_everyone,
                "code": code,
                "topic_id": topic_id or self.topic_id,
            }

            return await self.socket_manager.write_chat_message(**data_reply)

        return await self.message_queue.enqueue(reply_operation)

    async def update(
        self,
        content: ChannelMessageContent,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        topic_id: Optional[str] = None,
    ) -> Any:
        """
        Update (edit) this message.

        Args:
            content: Updated message content
            mentions: Updated list of mentions (optional)
            attachments: Updated list of attachments (optional)
            topic_id: Topic ID (optional, defaults to this message's topic)

        Returns:
            Update acknowledgement
        """

        async def update_operation():
            data_update = {
                "clan_id": self.channel.clan.id,
                "channel_id": self.channel.id,
                "mode": convert_channeltype_to_channel_mode(self.channel.channel_type),
                "is_public": not self.channel.is_private,
                "message_id": self.id,
                "content": content,
                "mentions": mentions,
                "attachments": attachments,
                "topic_id": topic_id or self.topic_id,
            }

            return await self.socket_manager.update_chat_message(**data_update)

        return await self.message_queue.enqueue(update_operation)

    async def react(self, data_react_message: Dict[str, Any]) -> Any:
        """
        Add or remove a reaction to this message.

        Args:
            data_react_message: Reaction data containing:
                - id: Reaction ID (optional)
                - emoji_id: Emoji ID
                - emoji: Emoji string
                - count: Reaction count
                - action_delete: Whether to remove the reaction (optional, default: False)

        Returns:
            Reaction acknowledgement
        """

        async def react_operation():
            data_react = {
                "id": data_react_message.get("id", ""),
                "clan_id": self.channel.clan.id,
                "channel_id": self.channel.id,
                "mode": convert_channeltype_to_channel_mode(self.channel.channel_type),
                "is_public": not self.channel.is_private,
                "message_id": self.id,
                "emoji_id": data_react_message["emoji_id"],
                "emoji": data_react_message["emoji"],
                "count": data_react_message["count"],
                "message_sender_id": self.sender_id,
                "action_delete": data_react_message.get("action_delete", False),
            }

            return await self.socket_manager.write_message_reaction(**data_react)

        return await self.message_queue.enqueue(react_operation)

    async def delete(self) -> Any:
        """
        Delete this message.

        Returns:
            Delete acknowledgement
        """

        async def delete_operation():
            data_remove = {
                "clan_id": self.channel.clan.id,
                "channel_id": self.channel.id,
                "mode": convert_channeltype_to_channel_mode(self.channel.channel_type),
                "is_public": not self.channel.is_private,
                "message_id": self.id,
            }

            return await self.socket_manager.remove_chat_message(**data_remove)

        return await self.message_queue.enqueue(delete_operation)

    def __repr__(self) -> str:
        """String representation of the message."""
        content_preview = str(self.content)[:50]
        if len(str(self.content)) > 50:
            content_preview += "..."
        return f"<Message id={self.id} sender={self.sender_id} content='{content_preview}'>"
