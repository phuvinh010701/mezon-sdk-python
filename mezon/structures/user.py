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

from typing import Optional, Any, TYPE_CHECKING

from mezon.messages.queue import MessageQueue
from mezon.models import UserInitData
from mezon.utils.logger import get_logger

if TYPE_CHECKING:
    from mezon.managers.socket import SocketManager
    from .clan import Clan

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
        clan: "Clan",
        message_queue: MessageQueue,
        socket_manager: "SocketManager",
        channel_manager: Optional[Any] = None,
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
            clan: The clan this user belongs to
            message_queue: Message queue for rate limiting
            socket_manager: Socket manager for sending messages
            channel_manager: Channel manager for creating DM channels (optional)
        """
        self.id = user_init_data.id
        self.avatar = user_init_data.avatar
        self.dm_channel_id = user_init_data.dm_channel_id
        self.username = user_init_data.username
        self.clan_nick = user_init_data.clan_nick
        self.clan_avatar = user_init_data.clan_avatar
        self.display_name = user_init_data.display_name

        self.clan = clan
        self.channel_manager = channel_manager
        self.message_queue = message_queue
        self.socket_manager = socket_manager

    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User id={self.id} username={self.username} display_name={self.display_name}>"
