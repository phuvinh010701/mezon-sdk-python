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

from typing import Optional, List, Any, Callable

from mezon.api.utils import parse_url_components
from mezon.managers.chanel import ChanelManager
from mezon.managers.event import EventManager
from mezon.managers.session import SessionManager
from mezon.managers.socket import SocketManager
from mezon.messages.queue import MessageQueue
from mezon.messages.db import MessageDB

from .api import MezonApi
from .session import Session
from .models import (
    ChannelMessageAck,
    ApiMessageMention,
    ApiMessageAttachment,
    ApiMessageRef,
)


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


class MezonClient:
    """
    A client for Mezon server.
    """

    def __init__(
        self,
        bot_id: str,
        api_key: str,
        host: str = DEFAULT_HOST,
        port: str = DEFAULT_PORT,
        use_ssl: bool = DEFAULT_SSL,
        timeout: int = DEFAULT_TIMEOUT_MS,
        mmn_api_url: str = DEFAULT_MMN_API,
        zk_api_url: str = DEFAULT_ZK_API,
    ):
        """
        Initialize the MezonClient.

        Args:
            bot_id: The bot ID for authentication
            api_key: The API key for authentication
            host: The server host
            port: The server port
            use_ssl: Whether to use SSL connection
            timeout: The timeout for requests in milliseconds
            mmn_api_url: The URL for the MMN API
            zk_api_url: The URL for the ZK API
        """
        self.bot_id = bot_id
        self.api_key = api_key
        self.mmn_api_url = mmn_api_url
        self.zk_api_url = zk_api_url
        self.login_url = f"{use_ssl and 'https' or 'http'}://{host}:{port}"
        self.timeout_ms = timeout

        self.event_manager = EventManager()
        self.message_queue = MessageQueue()
        self.message_db = MessageDB()

    async def get_session(self) -> Session:
        temp_api = MezonApi(
            self.bot_id,
            self.api_key,
            self.login_url,
            self.timeout_ms,
        )
        temp_session_manager = SessionManager(api_client=temp_api)
        session = await temp_session_manager.authenticate(self.bot_id, self.api_key)
        return session

    async def initialize_managers(self, sock_session: Session) -> None:
        url_components = parse_url_components(sock_session.api_url)
        self.api_client = MezonApi(
            self.bot_id,
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
        self.chanel_manager = ChanelManager(
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
            await self.socket_manager.connect_socket(sock_session.token)
            await self.chanel_manager.init_all_dm_channels(sock_session.token)

    async def login(self) -> None:
        session = await self.get_session()
        sock_session = Session(session)

        await self.initialize_managers(sock_session)

    async def send_message(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        msg: Any,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        ref: Optional[List[ApiMessageRef]] = None,
        anonymous_message: Optional[bool] = None,
        mention_everyone: Optional[bool] = None,
        avatar: Optional[str] = None,
        code: Optional[int] = None,
        topic_id: Optional[str] = None,
    ) -> ChannelMessageAck:
        """
        Send message to channel.

        Args:
            clan_id: The clan ID
            channel_id: The channel ID
            mode: The channel mode
            is_public: Whether the message is public
            msg: The message content
            mentions: List of mentions
            attachments: List of attachments
            ref: List of message references
            anonymous_message: Whether anonymous
            mention_everyone: Whether to mention everyone
            avatar: Avatar URL
            code: Message code
            topic_id: Topic ID

        Returns:
            The message acknowledgement

        Raises:
            ValueError: If message exceeds character limit
        """

        return await self.socket_manager.write_chat_message(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            content=msg,
            mentions=mentions,
            attachments=attachments,
            references=ref,
            anonymous_message=anonymous_message,
            mention_everyone=mention_everyone,
            avatar=avatar,
            code=code,
            topic_id=topic_id,
        )

    def on(self, event_name: str, handler: Callable) -> None:
        self.event_manager.on(event_name, handler)
