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

from mezon.api import MezonApi
from mezon.managers.cache import CacheManager
from mezon.messages.db import MessageDB
from mezon.messages.queue import MessageQueue
from mezon.utils.logger import get_logger

from .text_channel import TextChannel
from .user import User

if TYPE_CHECKING:
    from mezon.client import MezonClient
    from mezon.managers.socket import SocketManager

logger = get_logger(__name__)


class Clan:
    """
    Represents a Mezon clan (server/guild).

    This class provides methods for managing channels, users, roles,
    and other clan-related operations.
    """

    def __init__(
        self,
        clan_id: str,
        clan_name: str,
        welcome_channel_id: str,
        client: "MezonClient",
        api_client: MezonApi,
        socket_manager: "SocketManager",
        session_token: str,
        message_queue: MessageQueue,
        message_db: MessageDB,
    ):
        """
        Initialize a Clan.

        Args:
            clan_id: Clan ID
            clan_name: Clan name
            welcome_channel_id: Welcome channel ID
            client: The MezonClient instance
            api_client: API client for making requests
            socket_manager: Socket manager for real-time communication
            session_token: Authentication session token
            message_queue: Message queue for rate limiting
            message_db: Database for message caching
        """
        self.id = clan_id
        self.name = clan_name
        self.welcome_channel_id = welcome_channel_id

        self.client = client
        self.client_id = self.client.client_id

        self.api_client = api_client
        self.socket_manager = socket_manager
        self.message_queue = message_queue
        self.session_token = session_token
        self.message_db = message_db

        self._channels_loaded = False
        self._loading_promise: Optional[Any] = None

        async def channel_fetcher(channel_id: str) -> TextChannel:
            return await self.client.channels.fetch(channel_id)

        self.channels: CacheManager[str, TextChannel] = CacheManager(
            fetcher=channel_fetcher
        )

        async def user_fetcher(user_id: str) -> User:
            dm_channel = await self.client.create_dm_channel(user_id)
            if not dm_channel or not dm_channel.get("channel_id"):
                raise ValueError(f"User {user_id} not found in this clan {self.id}!")

            user_data = {
                "id": user_id,
                "dmChannelId": dm_channel["channel_id"],
            }
            user = User(
                user_data,
                self,
                self.message_queue,
                self.socket_manager,
                channel_manager=getattr(self.client, "chanel_manager", None),
            )
            self.users.set(user_id, user)
            return user

        self.users: CacheManager[str, User] = CacheManager(fetcher=user_fetcher)

    def get_client_id(self) -> Optional[str]:
        """
        Get the client ID.

        Returns:
            The client ID if available, None otherwise
        """
        return getattr(self.client, "client_id", None)

    def __repr__(self) -> str:
        """String representation of the clan."""
        return f"<Clan id={self.id} name={self.name}>"
