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
from typing import Any, Callable, Literal, Dict
import logging

from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_never,
    wait_exponential,
    before_sleep_log,
)

from mezon import ApiChannelDescription, CacheManager, ChannelType, Events
from mezon.api.utils import parse_url_components
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2
from mezon.managers.channel import ChannelManager
from mezon.managers.event import EventManager
from mezon.managers.session import SessionManager
from mezon.managers.socket import SocketManager
from mezon.messages.db import MessageDB
from mezon.models import (
    ApiAuthenticateLogoutRequest,
    ApiAuthenticateRefreshRequest,
    ApiSentTokenRequest,
    ChannelMessageRaw,
    UserInitData,
)
from mezon.structures.clan import Clan
from mezon.structures.message import Message
from mezon.structures.text_channel import TextChannel
from mezon.structures.user import User
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
    ZkClientType,
)

from .api import MezonApi
from .session import Session
from mezon.utils.helper import generate_snowflake_id
from mezon.models import ChannelMessageContent
from mezon.constants import TypeMessage

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


def auto_bind(event_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to auto-bind a default event handler to the client's event manager.

    This decorator is intended for instance methods of ``MezonClient`` that
    should always be registered, even if the user does not explicitly call an
    ``on_*`` registration method. The actual binding happens when the client
    is initialized and scans for decorated methods.

    Args:
        event_name: Name of the event in ``Events`` to subscribe to.

    Returns:
        The original function, annotated with metadata for later registration.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "_auto_bind_event", event_name)
        return func

    return decorator


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
        self.users: CacheManager[str, User] = CacheManager(
            self.get_user_from_id, max_size=1000
        )

        self.event_manager = EventManager()
        self.message_db = MessageDB()

        logger.info(f"MezonClient initialized for client_id: {client_id}")

        self._register_auto_bound_handlers()

    def _register_auto_bound_handlers(self) -> None:
        """
        Register all methods decorated with ``@auto_bind`` on this client.

        This scans the instance for callables annotated with the
        ``_auto_bind_event`` attribute and wires them into the
        ``EventManager`` so they are always active as default handlers.
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            event_name = getattr(attr, "_auto_bind_event", None)
            if not event_name or not callable(attr):
                continue

            async def wrapper(message: Any, method: Callable[..., Any] = attr) -> None:
                await self._invoke_handler(method, message)

            setattr(wrapper, "_is_default_handler", True)

            self.event_manager.on(event_name, wrapper)

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
            mezon_client=self,
            message_db=self.message_db,
        )
        self.session_manager = SessionManager(
            api_client=self.api_client, session=sock_session
        )
        self.channel_manager = ChannelManager(
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
                self.channel_manager.init_all_dm_channels(sock_session.token),
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

    async def login(self, enable_auto_reconnect: bool = True) -> None:
        """
        Authenticate and initialize the client.

        Args:
            enable_auto_reconnect: Whether to enable automatic reconnection on disconnect
        """
        session = await self.get_session()
        await self.initialize_managers(session)

        if session.user_id:
            self.key_gen = self.get_ephemeral_key_pair()
            self.address = self.get_address_from_user_id(self.client_id)
            self.zk_proof = await self.get_zk_proof()

        self._enable_auto_reconnect = enable_auto_reconnect
        self._is_hard_disconnect = False

        if enable_auto_reconnect:
            self._setup_reconnect_handlers()

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
                ephemeral_public_key=self.key_gen.public_key,
                jwt=self.session_manager.get_session().id_token,
                address=self.address,
                client_type=ZkClientType.MEZON,
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
        existing_channel = self.channels.get(channel_id)
        if existing_channel:
            return existing_channel

        session = self.session_manager.get_session()
        channel_detail = await self.api_client.get_channel_detail(
            session.token, channel_id
        )

        clan_id = channel_detail.clan_id
        if not clan_id:
            raise ValueError(f"Channel {channel_id} has no clan_id!")

        clan = self.clans.get(clan_id)
        if not clan:
            clans_response = await self.api_client.list_clans_descs(token=session.token)
            clan_desc = None
            for desc in (
                clans_response.clandesc
                if clans_response and clans_response.clandesc
                else []
            ):
                if desc.clan_id == clan_id:
                    clan_desc = desc
                    break

            if clan_desc:
                clan = Clan(
                    clan_id=clan_desc.clan_id,
                    clan_name=clan_desc.clan_name,
                    welcome_channel_id=clan_desc.welcome_channel_id,
                    client=self,
                    api_client=self.api_client,
                    socket_manager=self.socket_manager,
                    session_token=session.token,
                    message_db=self.message_db,
                )
                self.clans.set(clan_id, clan)
            else:
                raise ValueError(f"Clan {clan_id} not found for channel {channel_id}!")

        channel = TextChannel(
            init_channel_data=channel_detail,
            clan=clan,
            socket_manager=self.socket_manager,
            message_db=self.message_db,
        )
        self.channels.set(channel_id, channel)
        return channel

    async def get_user_from_id(self, user_id: str) -> User:
        dm_channel = await self.channel_manager.create_dm_channel(user_id)
        if not dm_channel or not dm_channel.channel_id:
            raise ValueError(f"User {user_id} not found in this clan {self.client_id}!")

        user = User(
            user_init_data=UserInitData(
                id=user_id,
                dm_channel_id=dm_channel.channel_id,
            ),
            socket_manager=self.socket_manager,
            channel_manager=self.channel_manager,
        )
        self.users.set(user_id, user)
        return user

    async def add_quick_menu_access(self, body: Dict[str, Any]) -> Any:
        id = generate_snowflake_id()
        session = self.session_manager.get_session()
        if not session:
            return None

        bot_id = self.client_id
        payload = {
            "channel_id": "0",
            "clan_id": body.get("clan_id", "0"),
            "menu_type": body.get("menu_type", 1),
            "action_msg": body.get("action_msg"),
            "background": body.get("background", ""),
            "menu_name": body.get("menu_name"),
            "id": id,
            "bot_id": bot_id,
        }

        return await self.api_client.add_quick_menu_access(session.token, payload)

    async def delete_quick_menu_access(self, bot_id: str = None) -> Any:
        session = self.session_manager.get_session()
        if not session:
            return None

        target_bot_id = bot_id if bot_id else self.client_id
        return await self.api_client.delete_quick_menu_access(
            session.token, target_bot_id
        )

    async def get_list_friends(
        self, limit: int = None, state: str = None, cursor: str = None
    ) -> Any:
        session = self.session_manager.get_session()
        if not session:
            return None
        return await self.api_client.get_list_friends(
            session.token, limit, state, cursor
        )

    async def accept_friend(self, user_id: str, username: str) -> Any:
        session = self.session_manager.get_session()
        if not session:
            return None
        return await self.api_client.request_friend(session.token, username, user_id)

    async def add_friend(self, username: str) -> Any:
        session = self.session_manager.get_session()
        if not session:
            return None
        return await self.api_client.request_friend(session.token, username)

    async def list_transaction_detail(self, transaction_id: str) -> Any:
        session = self.session_manager.get_session()
        if not session:
            return None
        return await self.api_client.list_transaction_detail(
            session.token, transaction_id
        )

    async def _init_channel_message_cache(
        self, message: api_pb2.ChannelMessage
    ) -> None:
        """
        Initialize channel message cache when receiving a message.

        Args:
            message: The channel message from protobuf
        """
        message_raw = ChannelMessageRaw.from_protobuf(message)

        try:
            await self.message_db.save_message(message_raw.to_db_dict())
        except Exception as err:
            logger.warning(f"Failed to save message {message_raw.id}: {err}")

        if message_raw.clan_id and message_raw.clan_id != "0":
            clan = self.clans.get(message_raw.clan_id)
            if clan:
                try:
                    await clan.load_channels()
                except Exception as err:
                    logger.warning(f"Failed to load channels: {err}")

        try:
            channel = await self.channels.fetch(message_raw.channel_id)
        except Exception as err:
            logger.warning(f"Fetch channel {message_raw.channel_id} failed: {err}")
            channel = None

        if not channel:
            return

        if not message_raw.id:
            return

        message_obj = Message(
            message_raw,
            channel,
            self.socket_manager,
        )

        channel.messages.set(message_raw.id, message_obj)

    async def _init_user_clan_cache(self, message: api_pb2.ChannelMessage) -> None:
        """
        Initialize user and clan cache when receiving a message.

        Args:
            message: The channel message from protobuf
        """

        all_dm_channels = self.channel_manager.get_all_dm_channels()
        user_cache = self.users.get(message.sender_id)

        if not user_cache and message.sender_id != self.client_id and all_dm_channels:
            for user_id, dm_channel_id in all_dm_channels.items():
                if not user_id:
                    continue

                user = User(
                    user_init_data=UserInitData(
                        sender_id=user_id,
                        dm_channel_id=dm_channel_id,
                    ),
                    socket_manager=self.socket_manager,
                    channel_manager=self.channel_manager,
                )

                self.users.set(user_id, user)

        sender_dm_channel = (
            all_dm_channels.get(message.sender_id, "") if all_dm_channels else ""
        )
        user_data = UserInitData.from_protobuf(message, sender_dm_channel)

        sender_user = User(
            user_init_data=user_data,
            socket_manager=self.socket_manager,
            channel_manager=self.channel_manager,
        )
        self.users.set(message.sender_id, sender_user)

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
            self.message_db,
        )
        self.channels.set(message.channel_id, channel)
        clan.channels.set(message.channel_id, channel)
        return channel

    def on_channel_message(
        self, handler: Callable[[api_pb2.ChannelMessage], None]
    ) -> None:
        """
        Register a user-defined handler for channel messages.

        Default internal behavior (initializing channel & user caches) is always
        active via an auto-bound handler. This method only wires an additional
        user callback.

        Args:
            handler: Callback to invoke when a channel message is received.
        """

        async def wrapper(message: api_pb2.ChannelMessage) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.CHANNEL_MESSAGE, wrapper)

    @auto_bind(Events.CHANNEL_MESSAGE)
    async def _handle_channel_message_default(
        self, message: api_pb2.ChannelMessage
    ) -> None:
        """
        Default handler for ``ChannelMessage`` events.

        This handler is automatically registered and is responsible for keeping
        the channel and user caches in sync with incoming messages.

        Args:
            message: The ``ChannelMessage`` payload from the server.
        """
        await self._init_channel_message_cache(message)
        await self._init_user_clan_cache(message)

    def on_channel_created(
        self,
        handler: Callable[[realtime_pb2.ChannelCreatedEvent], None],
    ) -> None:
        async def wrapper(message: realtime_pb2.ChannelCreatedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.CHANNEL_CREATED, wrapper)

    @auto_bind(Events.CHANNEL_CREATED)
    async def _handle_channel_created_default(
        self, message: realtime_pb2.ChannelCreatedEvent
    ) -> None:
        """
        Default handler for channel created events.
        """
        await self._update_cache_channel(message)

    def on_channel_updated(
        self, handler: Callable[[realtime_pb2.ChannelUpdatedEvent], None]
    ) -> None:
        """
        Register a user-defined handler for channel updated events.

        Default internal behavior (joining new threads and updating caches) is
        always active via an auto-bound handler. This method only wires an
        additional user callback.
        """

        async def wrapper(message: realtime_pb2.ChannelUpdatedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.CHANNEL_UPDATED, wrapper)

    @auto_bind(Events.CHANNEL_UPDATED)
    async def _handle_channel_updated_default(
        self, message: realtime_pb2.ChannelUpdatedEvent
    ) -> None:
        """
        Default handler for ``ChannelUpdatedEvent``.

        Auto-joins newly activated threads and refreshes channel cache state.
        """
        if (
            message.channel_type == ChannelType.CHANNEL_TYPE_THREAD
            and message.status == 1
        ):
            await self.socket_manager.get_socket().join_chat(
                clan_id=message.clan_id,
                channel_id=message.channel_id,
                channel_type=message.channel_type,
                is_public=False,
            )

        await self._update_cache_channel(message)

    def on_channel_deleted(
        self, handler: Callable[[realtime_pb2.ChannelDeletedEvent], None]
    ) -> None:
        """
        Register a user-defined handler for channel deleted events.

        Default internal behavior (removing channel from caches) is always
        active via an auto-bound handler. This method only wires an additional
        user callback.
        """

        async def wrapper(message: realtime_pb2.ChannelDeletedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.CHANNEL_DELETED, wrapper)

    @auto_bind(Events.CHANNEL_DELETED)
    async def _handle_channel_deleted_default(
        self, message: realtime_pb2.ChannelDeletedEvent
    ) -> None:
        """
        Default handler for ``ChannelDeletedEvent``.

        Cleans up channel entries from the client and clan caches.
        """
        clan = self.clans.get(message.clan_id)
        if not clan:
            logger.debug(f"Clan {message.clan_id} not found!")
            return

        self.channels.delete(message.channel_id)
        clan.channels.delete(message.channel_id)

    def on_token_send(self, handler: Callable[[api_pb2.TokenSentEvent], None]) -> None:
        async def wrapper(message: api_pb2.TokenSentEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.TOKEN_SEND, wrapper)

    @auto_bind(Events.TOKEN_SEND)
    async def _handle_token_send_default(self, message: api_pb2.TokenSentEvent) -> None:
        if message.sender_id == self.client_id:
            receiver = await self.users.fetch(message.receiver_id)
            if receiver:
                await receiver.send_dm_message(
                    content=ChannelMessageContent(
                        t=f"Funds Transferred: {(int(message.amount)):,}₫ | {message.note or 'Transfer funds'}"
                    ),
                    code=TypeMessage.SEND_TOKEN,
                )

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
        """
        Register a user-defined handler for user clan removal events.

        Default internal behavior (removing users from clan cache) is always
        active via an auto-bound handler. This method only wires an additional
        user callback.
        """

        async def wrapper(message: realtime_pb2.UserClanRemoved) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.USER_CLAN_REMOVED, wrapper)

    @auto_bind(Events.USER_CLAN_REMOVED)
    async def _handle_user_clan_removed_default(
        self, message: realtime_pb2.UserClanRemoved
    ) -> None:
        """
        Default handler for ``UserClanRemoved`` events.

        Ensures the clan user cache reflects the server state when users are
        removed from a clan.
        """
        for user_id in message.user_ids:
            self.users.delete(user_id)

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
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.USER_CHANNEL_ADDED, wrapper)

    @auto_bind(Events.USER_CHANNEL_ADDED)
    async def _handle_user_channel_added_default(
        self, message: realtime_pb2.UserChannelAdded
    ) -> None:
        """
        Default handler for ``UserChannelAdded`` events.

        Automatically joins channels when the current client is added, keeping
        the socket subscription state in sync.
        """
        if message.users:
            for user in message.users:
                if user.user_id == self.client_id:
                    await self.socket_manager.get_socket().join_chat(
                        clan_id=message.clan_id,
                        channel_id=message.channel_desc.channel_id,
                        channel_type=message.channel_desc.type.value,
                        is_public=not message.channel_desc.channel_private,
                    )
                    break

    def on_give_coffee(
        self, handler: Callable[[api_pb2.GiveCoffeeEvent], None]
    ) -> None:
        async def wrapper(message: api_pb2.GiveCoffeeEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.GIVE_COFFEE, wrapper)

    def on_role_event(self, handler: Callable[[realtime_pb2.RoleEvent], None]) -> None:
        async def wrapper(message: realtime_pb2.RoleEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.ROLE_EVENT, wrapper)

    def on_clan_event_created(self, handler: Callable[[Any], None]) -> None:
        async def wrapper(message: Any) -> None:
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

    def on_quick_menu_event(self, handler: Callable[[Any], None]) -> None:
        async def wrapper(message: Any) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.QUICK_MENU, wrapper)

    def on_role_assign(
        self, handler: Callable[[realtime_pb2.RoleAssignedEvent], None]
    ) -> None:
        async def wrapper(message: realtime_pb2.RoleAssignedEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.ROLE_ASSIGN, wrapper)

    def on_notification(
        self, handler: Callable[[realtime_pb2.Notifications], None]
    ) -> None:
        """
        Register a user-defined handler for notification events.

        Default internal behavior (e.g. auto-handling certain notification
        codes like friend requests) is always active via an auto-bound handler.
        This method only wires an additional user callback.
        """

        async def wrapper(message: realtime_pb2.Notifications) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.NOTIFICATIONS, wrapper)

    @auto_bind(Events.NOTIFICATIONS)
    async def _handle_notifications_default(
        self, message: realtime_pb2.Notifications
    ) -> None:
        """
        Default handler for ``Notifications`` events.

        Processes built-in behaviors such as auto-accepting certain friend
        requests based on notification codes.
        """
        notifications = message.notifications if message.notifications else []

        for notification in notifications:
            try:
                content = (
                    json.loads(notification.content) if notification.content else {}
                )

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
                logger.warning(
                    f"Failed to parse notification content: {notification.content}"
                )
            except Exception as err:
                logger.warning(f"Error processing notification: {err}")

    def on_add_clan_user(
        self, handler: Callable[[realtime_pb2.AddClanUserEvent], None]
    ) -> None:
        """
        Register a user-defined handler for ``AddClanUserEvent``.

        Default internal behavior (joining clan chats and updating caches) is
        always active via an auto-bound handler, even if this method is never
        called. This method only wires an additional user callback.

        Args:
            handler: Callback to invoke when a clan user is added.
        """

        async def wrapper(message: realtime_pb2.AddClanUserEvent) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(Events.ADD_CLAN_USER, wrapper)

    @auto_bind(Events.ADD_CLAN_USER)
    async def _handle_add_clan_user_default(
        self, message: realtime_pb2.AddClanUserEvent
    ) -> None:
        """
        Default handler for ``AddClanUserEvent``.

        This handler is automatically registered at client initialization and
        is responsible for joining clan chats and populating user caches when
        the current client or other users are added to a clan.

        Args:
            message: The ``AddClanUserEvent`` payload from the server.
        """
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
                    message_db=self.message_db,
                )
                await clan_obj.load_channels()
                self.clans.set(message.clan_id, clan_obj)
            return

        user_init_data = UserInitData(
            id=message.user.user_id if message.user else "",
            username=message.user.username if message.user else "",
            clan_nick="",
            clan_avatar="",
            avatar=message.user.avatar if message.user else "",
            display_name=message.user.display_name if message.user else "",
            dm_channel_id="",
        )

        user = User(
            user_init_data=user_init_data,
            socket_manager=self.socket_manager,
            channel_manager=self.channel_manager,
        )
        self.users.set(message.user.user_id, user)
        return user

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

    async def session_refresh(self) -> Session:
        """
        Refresh the current session using the refresh token.

        Returns:
            Session: New session with refreshed tokens

        Raises:
            ValueError: If no refresh token is available
        """

        current_session = self.session_manager.get_session()

        if not current_session.refresh_token:
            raise ValueError("No refresh token available for session refresh")

        refresh_request = ApiAuthenticateRefreshRequest(
            token=current_session.token,
            refresh_token=current_session.refresh_token,
        )

        new_api_session = await self.api_client.mezon_authenticate_refresh(
            basic_auth_username=self.client_id,
            basic_auth_password=self.api_key,
            body=refresh_request,
        )

        new_session = Session(new_api_session)
        self.session_manager.session = new_session

        logger.info("Session refreshed successfully")
        return new_session

    async def logout(self) -> bool:
        """
        Log out the current session and invalidate tokens.

        Returns:
            bool: True if logout was successful
        """

        session = self.session_manager.get_session()

        logout_request = ApiAuthenticateLogoutRequest(
            token=session.token,
            refresh_token=session.refresh_token or "",
        )

        self._is_hard_disconnect = True

        try:
            await self.api_client.mezon_authenticate_logout(
                bearer_token=session.token,
                body=logout_request,
            )
            await self.close_socket()
            logger.info("Logged out successfully")
            return True
        except Exception as err:
            logger.error(f"Logout failed: {err}")
            return False

    def _setup_reconnect_handlers(self) -> None:
        """
        Setup event handlers for automatic reconnection.
        """
        socket = self.socket_manager.get_socket()

        original_ondisconnect = socket.ondisconnect
        original_onerror = socket.onerror

        async def handle_disconnect(event):
            logger.warning(f"Socket disconnected: {event}")
            if original_ondisconnect:
                await original_ondisconnect(event) if asyncio.iscoroutinefunction(
                    original_ondisconnect
                ) else original_ondisconnect(event)

            if not self._is_hard_disconnect and self._enable_auto_reconnect:
                await self._retry_connection()

        async def handle_error(event):
            logger.error(f"Socket error: {event}")
            if original_onerror:
                await original_onerror(event) if asyncio.iscoroutinefunction(
                    original_onerror
                ) else original_onerror(event)

            if not self._is_hard_disconnect and self._enable_auto_reconnect:
                if self.socket_manager.is_connected():
                    await self._retry_connection()

        socket.ondisconnect = handle_disconnect
        socket.onerror = handle_error

    async def _reconnect_attempt(self) -> None:
        """
        Attempt to reconnect to the server.

        Raises:
            Exception: If reconnection fails
            asyncio.CancelledError: If hard disconnect is detected
        """
        if self._is_hard_disconnect:
            raise asyncio.CancelledError("Hard disconnect, stopping reconnection")

        session = await self.get_session()
        await self.initialize_managers(session)
        logger.info("Reconnected successfully!")

    async def _retry_connection(self) -> None:
        """
        Retry connection with exponential backoff using tenacity.

        Retries with exponential backoff starting at 5 seconds, doubling each time,
        up to a maximum of 60 seconds between attempts. Stops if hard disconnect
        is detected or reconnection succeeds.
        """
        logger.info("Starting reconnection attempts...")

        def before_sleep_with_check(retry_state):
            """Check for hard disconnect and log before waiting."""
            if self._is_hard_disconnect:
                logger.info("Hard disconnect detected, stopping reconnection")
                raise asyncio.CancelledError("Hard disconnect")
            before_sleep_log(logger, logging.INFO)(retry_state)

        try:
            async for attempt in AsyncRetrying(
                wait=wait_exponential(multiplier=2, min=5, max=60),
                stop=stop_never,
                retry=retry_if_exception_type(Exception),
                before_sleep=before_sleep_with_check,
                reraise=True,
            ):
                with attempt:
                    if self._is_hard_disconnect:
                        logger.info("Hard disconnect detected, stopping reconnection")
                        break

                    logger.info(
                        f"Attempting to reconnect (attempt {attempt.retry_state.attempt_number})..."
                    )
                    await self._reconnect_attempt()
                    break

        except asyncio.CancelledError:
            logger.info("Hard disconnect detected, stopping reconnection")
        except Exception as err:
            logger.error(f"Reconnection failed after all retries: {err}")

    async def disconnect(self) -> None:
        """
        Disconnect from the socket without logging out.
        Sets hard disconnect flag to prevent auto-reconnection.
        """
        self._is_hard_disconnect = True
        await self.close_socket()
        logger.info("Client disconnected")
