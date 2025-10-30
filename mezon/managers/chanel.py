from typing import Optional, Dict

from mezon.api.mezon_api import MezonApi
from mezon.managers.session import SessionManager
from mezon.managers.socket import SocketManager
from mezon.constants import ChannelType


class ChanelManager:
    """
    Manager for channel operations.

    This class provides methods for managing channels, including creating DM channels,
    listing channels, and caching DM channel mappings.
    """

    def __init__(
        self,
        api_client: MezonApi,
        socket_manager: SocketManager,
        session_manager: SessionManager,
    ):
        self.api_client = api_client
        self.socket_manager = socket_manager
        self.session_manager = session_manager
        self.all_dm_channels: Optional[Dict[str, str]] = None

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

    def get_all_dm_channels(self) -> Optional[Dict[str, str]]:
        """
        Get all cached DM channels.

        Returns:
            Dictionary mapping user_id to channel_id, or None if not initialized
        """
        return self.all_dm_channels
