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

from typing import Optional, TYPE_CHECKING

from mezon import ApiMessageAttachment, ChannelMessageAck, ChannelType, TypeMessage
from mezon.models import ChannelMessageContent, UserInitData, ApiChannelDescription
from mezon.utils import convert_channeltype_to_channel_mode
from mezon.utils.logger import get_logger

if TYPE_CHECKING:
    from mezon.managers.channel import ChannelManager
    from mezon.managers.socket import SocketManager

logger = get_logger(__name__)


class User:
    """
    Represents a user in a Mezon clan.

    This class provides methods for user interactions including DM messaging,
    token transfers (MMN), and user profile management.
    """

    def __init__(
        self,
        user_init_data: UserInitData,
        socket_manager: "SocketManager",
        channel_manager: "ChannelManager",
    ):
        """
        Initialize a User.

        Args:
            user_init_data: User initialization data containing:
                - id: User ID
                - username: Username (optional)
                - clan_nick: Clan nickname (optional)
                - clan_avatar: Clan avatar URL (optional)
                - display_name: Display name (optional)
                - avatar: Avatar URL (optional)
                - dm_channel_id: DM channel ID (optional)
            socket_manager: Socket manager for sending messages
            channel_manager: Channel manager for creating DM channels
        """
        self.id = user_init_data.id
        self.avatar = user_init_data.avatar
        self.dm_channel_id = user_init_data.dm_channel_id
        self.username = user_init_data.username
        self.clan_nick = user_init_data.clan_nick
        self.clan_avatar = user_init_data.clan_avatar
        self.display_name = user_init_data.display_name

        self.channel_manager = channel_manager
        self.socket_manager = socket_manager

    async def create_dm_channel(self) -> ApiChannelDescription:
        logger.debug(f"Creating DM channel for user {self.id}")
        return await self.channel_manager.create_dm_channel(self.id)

    async def send_dm_message(
        self,
        content: ChannelMessageContent,
        code: int = TypeMessage.CHAT,
        attachments: Optional[list[ApiMessageAttachment]] = None,
    ) -> ChannelMessageAck:
        if not self.dm_channel_id:
            dm_channel = await self.create_dm_channel()
            self.dm_channel_id = dm_channel.channel_id

        logger.debug(
            f"Sending DM message to user {self.id} with channel {self.dm_channel_id}"
        )

        return await self.socket_manager.write_chat_message(
            clan_id="0",
            channel_id=self.dm_channel_id,
            mode=convert_channeltype_to_channel_mode(ChannelType.CHANNEL_TYPE_DM),
            is_public=False,
            content=content,
            code=code,
            attachments=attachments,
        )

    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User id={self.id} username={self.username} display_name={self.display_name}>"
