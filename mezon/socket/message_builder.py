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

import json
from typing import Any, List, Optional

from mezon.protobuf.rtapi import realtime_pb2
from mezon.models import (
    ApiMessageMention,
    ApiMessageAttachment,
    ApiMessageRef,
)


class ChannelMessageBuilder:
    """
    Builder class for constructing ChannelMessageSend protobuf messages.
    Separates message construction logic from socket operations.
    """

    @staticmethod
    def _prepare_content(content: Any) -> str:
        """
        Prepare message content for sending.

        Args:
            content: Message content (can be string or dict)

        Returns:
            Serialized content string
        """
        content_dict = {"t": content}
        return (
            json.dumps(content_dict)
            if isinstance(content_dict, dict)
            else str(content_dict)
        )

    @staticmethod
    def _add_mentions(
        message: realtime_pb2.ChannelMessageSend,
        mentions: List[ApiMessageMention],
    ) -> None:
        """
        Add mentions to the channel message.

        Args:
            message: The protobuf message to add mentions to
            mentions: List of mentions to add
        """
        for mention in mentions:
            msg_mention = message.mentions.add()
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

    @staticmethod
    def _add_attachments(
        message: realtime_pb2.ChannelMessageSend,
        attachments: List[ApiMessageAttachment],
    ) -> None:
        """
        Add attachments to the channel message.

        Args:
            message: The protobuf message to add attachments to
            attachments: List of attachments to add
        """
        for attachment in attachments:
            msg_attachment = message.attachments.add()
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

    @staticmethod
    def _add_references(
        message: realtime_pb2.ChannelMessageSend,
        references: List[ApiMessageRef],
    ) -> None:
        """
        Add message references to the channel message.

        Args:
            message: The protobuf message to add references to
            references: List of message references to add
        """
        for ref in references:
            msg_ref = message.references.add()
            msg_ref.message_ref_id = ref.message_ref_id
            msg_ref.message_sender_id = ref.message_sender_id
            if ref.message_sender_username:
                msg_ref.message_sender_username = ref.message_sender_username
            if ref.content:
                msg_ref.content = ref.content
            if ref.has_attachment is not None:
                msg_ref.has_attachment = ref.has_attachment

    @staticmethod
    def _set_optional_fields(
        message: realtime_pb2.ChannelMessageSend,
        anonymous_message: Optional[bool] = None,
        mention_everyone: Optional[bool] = None,
        avatar: Optional[str] = None,
        code: Optional[int] = None,
        topic_id: Optional[str] = None,
    ) -> None:
        """
        Set optional fields on the channel message.

        Args:
            message: The protobuf message to update
            anonymous_message: Whether to send as anonymous
            mention_everyone: Whether to mention everyone
            avatar: Avatar URL for the message
            code: Message code
            topic_id: Topic ID for threaded messages
        """
        if anonymous_message is not None:
            message.anonymous_message = anonymous_message
        if mention_everyone is not None:
            message.mention_everyone = mention_everyone
        if avatar:
            message.avatar = avatar
        if code is not None:
            message.code = code
        if topic_id:
            message.topic_id = topic_id

    @classmethod
    def build(
        cls,
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
    ) -> realtime_pb2.ChannelMessageSend:
        """
        Build a complete ChannelMessageSend protobuf message.

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
            Configured ChannelMessageSend protobuf message
        """
        content_str = cls._prepare_content(content)
        message = realtime_pb2.ChannelMessageSend(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            content=content_str,
        )
        if mentions:
            cls._add_mentions(message, mentions)
        if attachments:
            cls._add_attachments(message, attachments)
        if references:
            cls._add_references(message, references)

        cls._set_optional_fields(
            message,
            anonymous_message=anonymous_message,
            mention_everyone=mention_everyone,
            avatar=avatar,
            code=code,
            topic_id=topic_id,
        )

        return message


class EphemeralMessageBuilder:
    """
    Builder class for constructing EphemeralMessageSend protobuf messages.
    Separates message construction logic from socket operations.
    """

    @staticmethod
    def build(
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
    ) -> realtime_pb2.EphemeralMessageSend:
        """
        Build a complete EphemeralMessageSend protobuf message.
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
        return realtime_pb2.EphemeralMessageSend(
            receiver_id=receiver_id,
            message=channel_message_send,
        )
