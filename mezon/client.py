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
from typing import Callable
import logging

from mezon import ApiChannelDescription, CacheManager, ChannelType, Events
from mezon.api.utils import parse_url_components
from mezon.protobuf.api import api_pb2
from mezon.managers.channel import ChannelManager
from mezon.managers.event import EventManager
from mezon.managers.session import SessionManager
from mezon.managers.socket import SocketManager
from mezon.messages.db import MessageDB
from mezon.messages.queue import MessageQueue
from mezon.models import ApiCreateChannelDescRequest, ChannelMessageRaw, UserInitData
from mezon.structures.clan import Clan
from mezon.structures.message import Message
from mezon.structures.text_channel import TextChannel
from mezon.structures.user import User
from mezon.utils import is_valid_user_id
from mezon.utils.logger import get_logger, setup_logger

from .api import MezonApi
from .session import Session

DEFAULT_HOST = "gw.mezon.ai"
DEFAULT_PORT = "443"
DEFAULT_API_KEY = ""
DEFAULT_SSL = True
DEFAULT_TIMEOUT_MS = 7000
DEFAULT_EXPIRED_TIMESPAN_MS = 5 * 60 * 1000
DEFAULT_SEND_BULK_INTERVAL = 1000
DEFAULT_MESSAGE_PER_TIME = 5
DEFAULT_MMN_API = "https://dong.mezon.ai/mmn-api/"
DEFAULT_ZK_API = "https://dong.mezon.ai/zk-api/"

logger = get_logger(__name__)


class MezonClient:
    """
    A client for Mezon server.
    """

    def __init__(
        self,
        client_id: str,
        api_key: str,
        host: str = DEFAULT_HOST,
        port: str = DEFAULT_PORT,
        use_ssl: bool = DEFAULT_SSL,
        timeout: int = DEFAULT_TIMEOUT_MS,
        mmn_api_url: str = DEFAULT_MMN_API,
        zk_api_url: str = DEFAULT_ZK_API,
        log_level: int = logging.INFO,
        enable_logging: bool = False,
    ):
        """
        Initialize the MezonClient.

        Args:
            client_id: The client ID for authentication
            api_key: The API key for authentication
            host: The server host
            port: The server port
            use_ssl: Whether to use SSL connection
            timeout: The timeout for requests in milliseconds
            mmn_api_url: The URL for the MMN API
            zk_api_url: The URL for the ZK API
            log_level: The logging level (default: logging.INFO)
            enable_logging: Whether to enable logging output (default: True)
        """
        if enable_logging:
            setup_logger(log_level=log_level)

        self.client_id = client_id
        self.api_key = api_key
        self.mmn_api_url = mmn_api_url
        self.zk_api_url = zk_api_url
        self.login_url = f"{use_ssl and 'https' or 'http'}://{host}:{port}"
        self.timeout_ms = timeout
        self.clans: CacheManager[str, Clan] = CacheManager(None, max_size=1000)
        self.channels: CacheManager[str, TextChannel] = CacheManager(
            self.get_channel_from_id, max_size=1000
        )

        self.event_manager = EventManager()
        self.message_queue = MessageQueue()
        self.message_db = MessageDB()

        logger.info(f"MezonClient initialized for client_id: {client_id}")

    async def get_session(self) -> Session:
        """
        Get the session for the client. Initialize the temporary session manager to get the session.

        Returns:
            The session for the client.
        """
        temp_session_manager = SessionManager(
            api_client=MezonApi(
                self.client_id,
                self.api_key,
                self.login_url,
                self.timeout_ms,
            )
        )
        session = await temp_session_manager.authenticate(self.client_id, self.api_key)
        return Session(session)

    async def initialize_managers(self, sock_session: Session) -> None:
        url_components = parse_url_components(sock_session.api_url)
        self.api_client = MezonApi(
            self.client_id,
            self.api_key,
            f"{url_components['scheme']}://{url_components['hostname']}:{url_components['port']}",
            self.timeout_ms,
        )
        self.socket_manager = SocketManager(
            host=url_components["hostname"],
            port=url_components["port"],
            use_ssl=url_components["use_ssl"],
            api_client=self.api_client,
            event_manager=self.event_manager,
            message_queue=self.message_queue,
            mezon_client=self,
            message_db=self.message_db,
        )
        self.session_manager = SessionManager(
            api_client=self.api_client, session=sock_session
        )
        self.chanel_manager = ChannelManager(
            api_client=self.api_client,
            socket_manager=self.socket_manager,
            session_manager=self.session_manager,
        )

        if self.mmn_api_url:
            # TODO: Implement MMN API
            pass
        if self.zk_api_url:
            # TODO: Implement ZK API
            pass

        await self.socket_manager.connect(sock_session)

        if sock_session.token:
            await asyncio.gather(
                self.socket_manager.connect_socket(sock_session.token),
                self.chanel_manager.init_all_dm_channels(sock_session.token),
            )

    async def login(self) -> None:
        session = await self.get_session()
        await self.initialize_managers(session)

    def on(self, event_name: str, handler: Callable) -> None:
        """
        Override the default event manager

        """
        self.event_manager.on(event_name, handler)

    async def get_channel_from_id(self, channel_id: str) -> TextChannel:
        """
        Get a channel by ID, creating necessary clan objects if needed.

        Args:
            channel_id: The channel ID to fetch

        Returns:
            TextChannel object

        Raises:
            ValueError: If channel has no clan_id
        """
        session = self.session_manager.get_session()
        channel_detail = await self.api_client.get_channel_detail(
            session.token, channel_id
        )

        clan_id = channel_detail.clan_id
        if not clan_id:
            raise ValueError(f"Channel {channel_id} has no clan_id!")

        clan = self.clans.get(clan_id)

        channel = TextChannel(
            init_channel_data=channel_detail,
            clan=clan,
            socket_manager=self.socket_manager,
            message_queue=self.message_queue,
            message_db=self.message_db,
        )
        self.channels.set(channel_id, channel)
        return channel

    async def _init_channel_message_cache(
        self, message: api_pb2.ChannelMessage
    ) -> None:
        """
        Initialize channel message cache when receiving a message.

        Args:
            message: The channel message from protobuf

        Raises:
            ValueError: If the channel is not found
        """
        message_raw = ChannelMessageRaw.from_protobuf(message)

        channel = await self.channels.fetch(message_raw.channel_id)
        if not channel:
            raise ValueError(f"Channel {message_raw.channel_id} not found!")

        message_obj = Message(
            message_raw,
            channel,
            self.socket_manager,
            self.message_queue,
        )

        channel.messages.set(message_raw.id, message_obj)

        try:
            await self.message_db.save_message(message_raw.to_db_dict())
        except Exception as err:
            logger.warning(f"Failed to save message {message_raw.id}: {err}")

    async def _init_user_clan_cache(self, message: api_pb2.ChannelMessage) -> None:
        """
        Initialize user and clan cache when receiving a message.

        Args:
            message: The channel message from protobuf
        """

        clan = self.clans.get(message.clan_id or "0")
        if not clan:
            return

        clan_dm = self.clans.get("0")

        all_dm_channels = self.chanel_manager.get_all_dm_channels()
        user_cache = clan.users.get(message.sender_id)

        if not user_cache and message.sender_id != self.client_id and all_dm_channels:
            for user_id, dm_channel_id in all_dm_channels.items():
                if not user_id:
                    continue

                user_data = UserInitData(
                    sender_id=user_id,
                    dmChannelId=dm_channel_id,
                )

                user = User(
                    user_init_data=user_data,
                    clan=clan,
                    message_queue=self.message_queue,
                    socket_manager=self.socket_manager,
                    channel_manager=self.chanel_manager,
                )

                if clan_dm and not clan_dm.users.get(user_id):
                    clan_dm.users.set(user_id, user)

                if not clan.users.get(user_id):
                    clan.users.set(user_id, user)

        sender_dm_channel = (
            all_dm_channels.get(message.sender_id, "") if all_dm_channels else ""
        )
        user_data = UserInitData.from_protobuf(message, sender_dm_channel)

        sender_user = User(
            user_init_data=user_data,
            clan=clan,
            message_queue=self.message_queue,
            socket_manager=self.socket_manager,
            channel_manager=self.chanel_manager,
        )

        clan.users.set(message.sender_id, sender_user)

        if clan_dm:
            clan_dm.users.set(message.sender_id, sender_user)

    async def create_dm_channel(self, user_id: str) -> ApiChannelDescription:
        if not is_valid_user_id(user_id):
            logger.error(f"Invalid user ID: {user_id}")
            return None

        socket = self.socket_manager.get_socket()
        channel_dm = await self.api_client.create_channel_desc(
            token=self.session_manager.get_session().token,
            request=ApiCreateChannelDescRequest(
                clan_id="",
                channel_id="0",
                category_id="0",
                channel_type=ChannelType.CHANNEL_TYPE_DM,
                user_ids=[user_id],
                channel_private=1,
            ),
        )
        if channel_dm:
            await socket.join_chat(
                channel_id=channel_dm.channel_id,
                clan_id=channel_dm.clan_id,
                channel_type=channel_dm.type,
                is_public=False,
            )
            clan_dm = self.clans.get("0")
            if clan_dm:
                user = User(
                    user_init_data=UserInitData(
                        id=user_id,
                        dm_channel_id=channel_dm.channel_id,
                    ),
                    clan=clan_dm,
                    message_queue=self.message_queue,
                    socket_manager=self.socket_manager,
                    channel_manager=self.chanel_manager,
                )
                clan_dm.users.set(user_id, user)
                return channel_dm

        return None

    def on_channel_message(
        self, handler: Callable[[api_pb2.ChannelMessage], None]
    ) -> None:
        async def wrapper(message: api_pb2.ChannelMessage) -> None:
            await self._init_channel_message_cache(message)
            await self._init_user_clan_cache(message)
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)

        self.event_manager.on(Events.CHANNEL_MESSAGE, wrapper)
