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
import json
from typing import Any, Callable, Literal
import logging

from mezon import ApiChannelDescription, CacheManager, ChannelType, Events
from mezon.api.utils import parse_url_components
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2
from mezon.managers.channel import ChannelManager
from mezon.managers.event import EventManager
from mezon.managers.session import SessionManager
from mezon.managers.socket import SocketManager
from mezon.messages.db import MessageDB
from mezon.messages.queue import MessageQueue
from mezon.models import (
    ApiCreateChannelDescRequest,
    ApiSentTokenRequest,
    ChannelMessageRaw,
    UserInitData,
)
from mezon.structures.clan import Clan
from mezon.structures.message import Message
from mezon.structures.text_channel import TextChannel
from mezon.structures.user import User
from mezon.utils import is_valid_user_id
from mezon.utils.logger import get_logger, setup_logger
from mmn import (
    EphemeralKeyPair,
    MmnClient,
    MmnClientConfig,
    ZkClient,
    ZkClientConfig,
    ZkProof,
    AddTxResponse,
    ExtraInfo,
    SendTransactionRequest,
    TransferType,
)

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
            self.mmn_client = MmnClient(
                MmnClientConfig(
                    base_url=self.mmn_api_url,
                    timeout=self.timeout_ms,
                )
            )
        if self.zk_api_url:
            self.zk_client = ZkClient(
                ZkClientConfig(
                    endpoint=self.zk_api_url,
                    timeout=self.timeout_ms,
                )
            )

        await self.socket_manager.connect(sock_session)

        if sock_session.token:
            await asyncio.gather(
                self.socket_manager.connect_socket(sock_session.token),
                self.chanel_manager.init_all_dm_channels(sock_session.token),
            )

    async def _invoke_handler(self, handler: Callable, *args, **kwargs) -> None:
        """
        Invoke a handler function, automatically handling both sync and async callables.

        Args:
            handler: The handler function to invoke
            *args: Positional arguments to pass to the handler
            **kwargs: Keyword arguments to pass to the handler
        """
        logger.debug(f"Invoking handler {handler} with args {args} and kwargs {kwargs}")
        if asyncio.iscoroutinefunction(handler):
            await handler(*args, **kwargs)
        else:
            handler(*args, **kwargs)

    async def login(self) -> None:
        session = await self.get_session()
        await self.initialize_managers(session)

        if session.user_id:
            self.key_gen = self.get_ephemeral_key_pair()
            self.address = self.get_address_from_user_id(self.client_id)
            self.zk_proof = await self.get_zk_proof()

    def get_ephemeral_key_pair(self) -> EphemeralKeyPair:
        if self.mmn_client:
            return self.mmn_client.generate_ephemeral_key_pair()
        raise ValueError("MMN client not initialized!")

    def get_address_from_user_id(self, user_id: str) -> str:
        if self.mmn_client:
            return self.mmn_client.get_address_from_user_id(user_id)
        raise ValueError("MMN client not initialized!")

    async def get_zk_proof(self) -> ZkProof:
        if self.zk_client:
            return await self.zk_client.get_zk_proofs(
                user_id=self.client_id,
                jwt=self.session_manager.get_session().token,
                address=self.address,
                ephemeral_public_key=self.key_gen.public_key,
            )
        raise ValueError("ZK client not initialized!")

    async def get_current_nonce(
        self, user_id: str, tag: Literal["latest", "pending"] = "latest"
    ) -> int:
        if self.mmn_client:
            return await self.mmn_client.get_current_nonce(
                user_id=user_id,
                tag=tag,
            )
        raise ValueError("MMN client not initialized!")

    async def send_token(self, token_event: ApiSentTokenRequest) -> AddTxResponse:
        if not self.mmn_client:
            raise ValueError("MMN client not initialized")

        sender_id = self.client_id
        receiver_id = token_event.receiver_id

        nonce_response = await self.get_current_nonce(sender_id, "pending")

        extra_info = ExtraInfo(
            type=TransferType.TRANSFER_TOKEN.value,
            UserSenderId=sender_id,
            UserSenderUsername="",
            UserReceiverId=receiver_id,
        )
        tx_request = SendTransactionRequest(
            sender=sender_id,
            recipient=receiver_id,
            amount=self.mmn_client.scale_amount_to_decimals(token_event.amount),
            nonce=nonce_response.nonce + 1,
            text_data=token_event.note,
            extra_info=extra_info,
            public_key=self.key_gen.public_key,
            private_key=self.key_gen.private_key,
            zk_proof=self.zk_proof.proof,
            zk_pub=self.zk_proof.public_input,
        )

        logger.debug(f"Sending transaction: {tx_request}")

        result = await self.mmn_client.send_transaction(tx_request)
        return result

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

    async def _update_cache_channel(
        self,
        message: realtime_pb2.ChannelCreatedEvent | realtime_pb2.ChannelUpdatedEvent,
    ) -> None:
        clan = self.clans.get(message.clan_id)
        if not clan:
            return

        channel = TextChannel(
            ApiChannelDescription.from_protobuf(message),
            clan,
            self.socket_manager,
            self.message_queue,
            self.message_db,
        )
        self.channels.set(message.channel_id, channel)
        clan.channels.set(message.channel_id, channel)
        await self.socket_manager.get_socket().join_chat(
            channel.clan.id, channel.id, channel.channel_type, channel.is_private
        )
        return channel

    def on_channel_message(
        self, handler: Callable[[api_pb2.ChannelMessage], None]
    ) -> None:
        async def wrapper(message: api_pb2.ChannelMessage) -> None:
            await self._init_channel_message_cache(message)
            await self._init_user_clan_cache(message)
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.CHANNEL_MESSAGE, wrapper)

    def on_channel_created(
        self,
        handler: Callable[[realtime_pb2.ChannelCreatedEvent], None],
    ) -> None:
        async def wrapper(message: realtime_pb2.ChannelCreatedEvent) -> None:
            await self._update_cache_channel(message)
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.CHANNEL_CREATED, wrapper)

    def on_channel_updated(
        self, handler: Callable[[realtime_pb2.ChannelUpdatedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.ChannelUpdatedEvent) -> None:
            if (
                message.channel_type == ChannelType.CHANNEL_TYPE_THREAD
                and message.status == 1
            ):
                await self.socket_manager.get_socket().join_chat(
                    message.clan_id, message.channel_id, message.channel_type, False
                )
            await self._update_cache_channel(message)
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.CHANNEL_UPDATED, wrapper)

    def on_channel_deleted(
        self, handler: Callable[[realtime_pb2.ChannelDeletedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.ChannelDeletedEvent) -> None:
            clan = self.clans.get(message.clan_id)
            if not clan:
                logger.debug(f"Clan {message.clan_id} not found!")
                return

            self.channels.delete(message.channel_id)
            clan.channels.delete(message.channel_id)

            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.CHANNEL_DELETED, wrapper)

    def on_message_reaction(
        self, handler: Callable[[api_pb2.MessageReaction], None]
    ) -> None:
        async def wrapper(message: api_pb2.MessageReaction) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.MESSAGE_REACTION, wrapper)

    def on_channel_user_removed(
        self, handler: Callable[[realtime_pb2.UserChannelRemoved], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.UserChannelRemoved) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.USER_CHANNEL_REMOVED, wrapper)

    def on_user_clan_removed(
        self, handler: Callable[[realtime_pb2.UserClanRemoved], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.UserClanRemoved) -> None:
            clan = self.clans.get(message.clan_id)
            if not clan:
                logger.debug(f"Clan {message.clan_id} not found!")
                return

            for user_id in message.user_ids:
                clan.users.delete(user_id)

            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.USER_CLAN_REMOVED, wrapper)

    def on_user_channel_added(
        self, handler: Callable[[realtime_pb2.UserChannelAdded], None]
    ) -> None:
        """
        Register a handler for when a user is added to a channel.

        Args:
            handler: The callback function to handle the event.
                     Can be either sync or async.
        """

        async def wrapper(message: realtime_pb2.UserChannelAdded) -> None:
            socket = self.socket_manager.get_socket()
            if message.users:
                for user in message.users:
                    if user.user_id == self.client_id:
                        await socket.join_chat(
                            clan_id=message.clan_id,
                            channel_id=message.channel_desc.channel_id,
                            channel_type=message.channel_desc.type.value,
                            is_public=not message.channel_desc.channel_private,
                        )
                        break

            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.USER_CHANNEL_ADDED, wrapper)

    def on_give_coffee(
        self, handler: Callable[[api_pb2.GiveCoffeeEvent], None]
    ) -> None:
        async def wrapper(message: api_pb2.GiveCoffeeEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.GIVE_COFFEE, wrapper)

    def on_role_event(
        self, handler: Callable[[realtime_pb2.RoleEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.RoleEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.ROLE_EVENT, wrapper)

    def on_role_assign(
        self, handler: Callable[[realtime_pb2.RoleAssignedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.RoleAssignedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.ROLE_ASSIGN, wrapper)

    def on_notification(
        self, handler: Callable[[realtime_pb2.Notifications], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.Notifications) -> None:
            notifications = message.notifications if message.notifications else []

            for notification in notifications:
                try:
                    content = json.loads(notification.content) if notification.content else {}

                    if notification.code == -2:
                        session = self.session_manager.get_session()
                        if session and session.token:
                            username = content.get("username", "")
                            sender_id = notification.sender_id

                            if hasattr(self.api_client, "request_friend"):
                                try:
                                    await self.api_client.request_friend(
                                        session.token, username, sender_id
                                    )
                                except Exception as err:
                                    logger.warning(f"Failed to request friend: {err}")
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse notification content: {noti.content}")
                except Exception as err:
                    logger.warning(f"Error processing notification: {err}")

            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.NOTIFICATIONS, wrapper)

    def on_add_clan_user(
        self, handler: Callable[[realtime_pb2.AddClanUserEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.AddClanUserEvent) -> None:
            if message.user and message.user.user_id == self.client_id:
                socket = self.socket_manager.get_socket()
                await socket.join_clan_chat(message.clan_id)

                clan = self.clans.get(message.clan_id)
                if not clan:
                    clan_obj = Clan(
                        clan_id=message.clan_id,
                        clan_name="unknown",
                        welcome_channel_id="",
                        client=self,
                        api_client=self.api_client,
                        socket_manager=self.socket_manager,
                        session_token=self.session_manager.get_session().token,
                        message_queue=self.message_queue,
                        message_db=self.message_db,
                    )
                    await clan_obj.load_channels()
                    self.clans.set(message.clan_id, clan_obj)
            else:
                user_init_data = UserInitData(
                    id=message.user.user_id if message.user else "",
                    username=message.user.username if message.user else "",
                    clan_nick="",
                    clan_avatar="",
                    avatar=message.user.avatar if message.user else "",
                    display_name=message.user.display_name if message.user else "",
                    dm_channel_id="",
                )

                clan = self.clans.get(message.clan_id)
                if clan and message.user:
                    user = User(
                        user_init_data=user_init_data,
                        clan=clan,
                        message_queue=self.message_queue,
                        socket_manager=self.socket_manager,
                        channel_manager=self.chanel_manager,
                    )
                    clan.users.set(message.user.user_id, user)

                clan_dm = self.clans.get("0")
                if clan_dm and message.user:
                    user = User(
                        user_init_data=user_init_data,
                        clan=clan_dm,
                        message_queue=self.message_queue,
                        socket_manager=self.socket_manager,
                        channel_manager=self.chanel_manager,
                    )
                    clan_dm.users.set(message.user.user_id, user)

            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.ADD_CLAN_USER, wrapper)

    def on_clan_event_created(
        self, handler: Callable[[api_pb2.CreateEventRequest], None]
    ) -> None:
        async def wrapper(message: api_pb2.CreateEventRequest) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.CLAN_EVENT_CREATED, wrapper)

    def on_message_button_clicked(
        self, handler: Callable[[realtime_pb2.MessageButtonClicked], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.MessageButtonClicked) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.MESSAGE_BUTTON_CLICKED, wrapper)

    def on_streaming_joined_event(
        self, handler: Callable[[realtime_pb2.StreamingJoinedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.StreamingJoinedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.STREAMING_JOINED_EVENT, wrapper)

    def on_streaming_leaved_event(
        self, handler: Callable[[realtime_pb2.StreamingLeavedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.StreamingLeavedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.STREAMING_LEAVED_EVENT, wrapper)

    def on_dropdown_box_selected(
        self, handler: Callable[[realtime_pb2.DropdownBoxSelected], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.DropdownBoxSelected) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.DROPDOWN_BOX_SELECTED, wrapper)

    def on_webrtc_signaling_fwd(
        self, handler: Callable[[realtime_pb2.WebrtcSignalingFwd], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.WebrtcSignalingFwd) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.WEBRTC_SIGNALING_FWD, wrapper)

    def on_voice_started_event(
        self, handler: Callable[[realtime_pb2.VoiceStartedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.VoiceStartedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.VOICE_STARTED_EVENT, wrapper)

    def on_voice_ended_event(
        self, handler: Callable[[realtime_pb2.VoiceEndedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.VoiceEndedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.VOICE_ENDED_EVENT, wrapper)

    def on_voice_joined_event(
        self, handler: Callable[[realtime_pb2.VoiceJoinedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.VoiceJoinedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.VOICE_JOINED_EVENT, wrapper)

    def on_voice_leaved_event(
        self, handler: Callable[[realtime_pb2.VoiceLeavedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.VoiceLeavedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.VOICE_LEAVED_EVENT, wrapper)

    def on_quick_menu_event(
        self, handler: Callable[[realtime_pb2.QuickMenuDataEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.QuickMenuDataEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.QUICK_MENU, wrapper)

    async def close_socket(self) -> None:
        await self.socket_manager.get_socket().close()
        self.event_manager = EventManager()

    async def get_list_friends(
        self,
        limit: int = None,
        state: str = None,
        cursor: str = None,
    ) -> Any:
        session = self.session_manager.get_session()
        return await self.api_client.get_list_friends(
            session.token, limit, state, cursor
        )

    async def accept_friend(self, user_id: str, username: str) -> Any:
        session = self.session_manager.get_session()
        return await self.api_client.request_friend(session.token, username, user_id)

    async def add_friend(self, username: str) -> Any:
        session = self.session_manager.get_session()
        return await self.api_client.request_friend(session.token, username)