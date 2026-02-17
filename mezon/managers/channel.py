from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential

import mezon.api as api
from mezon.constants import ChannelType
from mezon.models import ApiChannelDescription, ApiCreateChannelDescRequest

from .session import SessionManager
from .socket import SocketManager


class ChannelManager:
    """
    Manager for channel operations.

    This class provides methods for managing channels, including creating DM channels,
    listing channels, and caching DM channel mappings.
    """

    def __init__(
        self,
        api_client: api.MezonApi,
        socket_manager: SocketManager,
        session_manager: SessionManager,
    ):
        self.api_client = api_client
        self.socket_manager = socket_manager
        self.session_manager = session_manager
        self.all_dm_channels: Optional[dict[int, int]] = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1.5, max=15),
        reraise=True,
    )
    async def init_all_dm_channels(self, session_token: str) -> None:
        """
        Initialize and cache all DM channels for quick lookup.

        This method fetches all DM channels and creates a mapping from user_id to channel_id
        for faster access when creating or finding DM channels.

        Args:
            session_token: Session token for authentication
        """
        if not session_token:
            return

        channels_response = await self.api_client.list_channel_descs(
            token=session_token,
            channel_type=ChannelType.CHANNEL_TYPE_DM,
        )

        if not channels_response or not channels_response.channeldesc:
            return

        dm_mapping = {}
        for channel in channels_response.channeldesc:
            user_ids = channel.user_ids
            channel_type = channel.type
            channel_id = channel.channel_id

            if user_ids and channel_type == ChannelType.CHANNEL_TYPE_DM and channel_id:
                dm_mapping[user_ids[0]] = channel_id

        self.all_dm_channels = dm_mapping

    def get_all_dm_channels(self) -> Optional[dict[int, int]]:
        """
        Get all cached DM channels.

        Returns:
            Dictionary mapping user_id to channel_id, or None if not initialized
        """
        return self.all_dm_channels

    async def create_dm_channel(self, user_id: int) -> ApiChannelDescription:
        """
        Create a DM channel for a user.

        Args:
            user_id: User ID to create a DM channel for

        Returns:
            ApiChannelDescription: Created channel description
        """
        channel_dm_desc = await self.api_client.create_channel_desc(
            token=self.session_manager.get_session().token,
            request=ApiCreateChannelDescRequest(
                clan_id=0,
                channel_id=0,
                category_id=0,
                type=ChannelType.CHANNEL_TYPE_DM,
                user_ids=[user_id],
                channel_private=1,
            ),
        )

        await self.socket_manager.get_socket().join_chat(
            clan_id=channel_dm_desc.clan_id,
            channel_id=channel_dm_desc.channel_id,
            channel_type=channel_dm_desc.type,
            is_public=False,
        )

        return channel_dm_desc
