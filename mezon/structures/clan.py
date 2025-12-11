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
from mezon.constants.enum import ChannelType
from mezon.managers.cache import CacheManager
from mezon.messages.db import MessageDB
from mezon.models import ApiVoiceChannelUserList, ApiRoleListEventResponse
from mezon.utils.logger import get_logger

from .text_channel import TextChannel

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
            message_db: Database for message caching
        """
        self.id = clan_id
        self.name = clan_name
        self.welcome_channel_id = welcome_channel_id

        self.client = client
        self.client_id = self.client.client_id

        self.api_client = api_client
        self.socket_manager = socket_manager
        self.session_token = session_token
        self.message_db = message_db

        self._channels_loaded = False
        self._loading_promise: Optional[Any] = None

        async def channel_fetcher(channel_id: str) -> TextChannel:
            return await self.client.channels.fetch(channel_id)

        self.channels: CacheManager[str, TextChannel] = CacheManager(
            fetcher=channel_fetcher
        )

    def __repr__(self) -> str:
        """String representation of the clan."""
        return f"<Clan id={self.id} name={self.name}>"

    async def load_channels(self) -> None:
        if self._channels_loaded:
            return

        channels = await self.api_client.list_channel_descs(
            token=self.session_token,
            channel_type=ChannelType.CHANNEL_TYPE_CHANNEL,
            clan_id=self.id,
        )

        valid_channels = [
            c
            for c in (channels.channeldesc if channels and channels.channeldesc else [])
            if c.channel_id
        ]

        for channel in valid_channels:
            channel_obj = TextChannel(
                init_channel_data=channel,
                clan=self,
                socket_manager=self.socket_manager,
                message_db=self.message_db,
            )
            self.channels.set(channel.channel_id, channel_obj)
            self.client.channels.set(channel.channel_id, channel_obj)

        self._channels_loaded = True

    async def list_channel_voice_users(
        self,
        channel_id: str = "",
        channel_type: int = None,
        limit: int = 500,
        state: int = None,
        cursor: str = None,
    ) -> ApiVoiceChannelUserList:
        if channel_type is None:
            channel_type = ChannelType.CHANNEL_TYPE_GMEET_VOICE

        if limit <= 0 or limit > 500:
            logger.error("0 < limit <= 500")
            raise ValueError("0 < limit <= 500")

        return await self.api_client.list_channel_voice_users(
            token=self.session_token,
            clan_id=self.id,
            channel_id=channel_id,
            channel_type=channel_type,
            limit=limit,
            state=state,
            cursor=cursor,
        )

    async def update_role(self, role_id: str, request: dict) -> bool:
        return await self.api_client.update_role(
            token=self.session_token,
            role_id=role_id,
            request=request,
        )

    async def list_roles(
        self,
        limit: str = None,
        state: str = None,
        cursor: str = None,
    ) -> ApiRoleListEventResponse:
        return await self.api_client.list_roles(
            token=self.session_token,
            clan_id=self.id,
            limit=limit,
            state=state,
            cursor=cursor,
        )
