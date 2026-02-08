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
import inspect
import json
import logging
from collections.abc import Callable
from typing import Any, Literal

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


EventHandler = Callable[..., Any]


def auto_bind(event_name: str) -> Callable[[EventHandler], EventHandler]:
    """
    Decorator to auto-bind a default event handler to the client's event manager.

    This decorator is intended for instance methods of ``MezonClient`` that
    should always be registered, even if the user does not explicitly call an
    ``on_*`` registration method. The actual binding happens when the client
    is initialized and scans for decorated methods.

    Args:
        event_name (str): Name of the event in ``Events`` to subscribe to.

    Returns:
        Callable: The original function, annotated with metadata for later registration.
    """

    def decorator(func: EventHandler) -> EventHandler:
        func._auto_bind_event = event_name  # type: ignore[attr-defined]
        return func

    return decorator


class MezonClient:
    """
    A client for Mezon server.
    """

    def __init__(
        self,
        client_id: str | int,
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

        self.client_id = int(client_id)
        self.api_key = api_key
        self.mmn_api_url = mmn_api_url
        self.zk_api_url = zk_api_url
        self.login_url = f"{use_ssl and 'https' or 'http'}://{host}:{port}"
        self.timeout_ms = timeout
        self.clans: CacheManager[int, Clan] = CacheManager(None, max_size=1000)
        self.channels: CacheManager[int, TextChannel] = CacheManager(
            self.get_channel_from_id, max_size=1000
        )
        self.users: CacheManager[int, User] = CacheManager(
            self.get_user_from_id, max_size=1000
        )

        self.event_manager = EventManager()
        self.message_db = MessageDB()

        logger.info(f"MezonClient initialized for client_id: {client_id}")

        self._register_auto_bound_handlers()

    def _register_auto_bound_handlers(self) -> None:
        """
        Register all methods decorated with ``@auto_bind`` on this client.

        This scans the class for callables annotated with the
        ``_auto_bind_event`` attribute and wires them into the
        ``EventManager`` so they are always active as default handlers.
        """
        for attr_name in vars(type(self)):
            unbound_method = getattr(type(self), attr_name)
            event_name = getattr(unbound_method, "_auto_bind_event", None)
            if not event_name:
                continue

            bound_method = getattr(self, attr_name)

            async def wrapper(
                message: Any, method: EventHandler = bound_method
            ) -> None:
                await self._invoke_handler(method, message)

            wrapper._is_default_handler = True  # type: ignore[attr-defined]
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
        """
        Initialize or reinitialize managers for the client.

        Args:
            sock_session: Session object with authentication token
        """
        url_components = parse_url_components(sock_session.api_url)
        self.api_client = MezonApi(
            self.client_id,
            self.api_key,
            f"{url_components['scheme']}://{url_components['hostname']}:{url_components['port']}",
            self.timeout_ms,
        )

        if not hasattr(self, "socket_manager"):
            self.socket_manager = SocketManager(
                host=url_components["hostname"],
                port=url_components["port"],
                use_ssl=url_components["use_ssl"],
                api_client=self.api_client,
                event_manager=self.event_manager,
                mezon_client=self,
                message_db=self.message_db,
            )
        else:
            self.socket_manager.api_client = self.api_client

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

    async def _invoke_handler(
        self, handler: EventHandler, *args: Any, **kwargs: Any
    ) -> None:
        """
        Invoke a handler function, automatically handling both sync and async callables.

        Args:
            handler (EventHandler): The handler function to invoke.
            *args (Any): Positional arguments to pass to the handler.
            **kwargs (Any): Keyword arguments to pass to the handler.
        """
        logger.debug(f"Invoking handler {handler} with args {args} and kwargs {kwargs}")
        if inspect.iscoroutinefunction(handler):
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
            self.ephemeral_key_pair = self.get_ephemeral_key_pair()
            self.address = self.get_address_from_user_id(self.client_id)
            self.zk_proof = await self.get_zk_proof()

        self._enable_auto_reconnect = enable_auto_reconnect
        self._is_hard_disconnect = False

        if enable_auto_reconnect:
            self._setup_reconnect_handlers()

    def get_ephemeral_key_pair(self) -> EphemeralKeyPair:
        """
        Generate an ephemeral key pair for secure transactions.

        Returns:
            EphemeralKeyPair: The generated ephemeral key pair.

        Raises:
            ValueError: If MMN client is not initialized.
        """
        if self.mmn_client:
            return self.mmn_client.generate_ephemeral_key_pair()
        raise ValueError("MMN client not initialized!")

    def get_address_from_user_id(self, user_id: str) -> str:
        """
        Get the blockchain address for a user ID.

        Args:
            user_id (str): The user ID to convert.

        Returns:
            str: The blockchain address.

        Raises:
            ValueError: If MMN client is not initialized.
        """
        if self.mmn_client:
            return self.mmn_client.get_address_from_user_id(user_id)
        raise ValueError("MMN client not initialized!")

    async def get_zk_proof(self) -> ZkProof:
        """
        Get a zero-knowledge proof for the current session.

        Returns:
            ZkProof: The zero-knowledge proof.

        Raises:
            ValueError: If ZK client is not initialized.
        """
        if self.zk_client:
            return await self.zk_client.get_zk_proofs(
                user_id=self.client_id,
                ephemeral_public_key=self.ephemeral_key_pair.public_key,
                jwt=self.session_manager.get_session().id_token,
                address=self.address,
                client_type=ZkClientType.MEZON,
            )
        raise ValueError("ZK client not initialized!")

    async def get_current_nonce(
        self, user_id: str, tag: Literal["latest", "pending"] = "latest"
    ) -> int:
        """
        Get the current transaction nonce for a user.

        Args:
            user_id (str): The user ID to get nonce for.
            tag (Literal["latest", "pending"]): The nonce tag type.

        Returns:
            int: The current nonce value.

        Raises:
            ValueError: If MMN client is not initialized.
        """
        if self.mmn_client:
            return await self.mmn_client.get_current_nonce(
                user_id=user_id,
                tag=tag,
            )
        raise ValueError("MMN client not initialized!")

    async def send_token(self, token_event: ApiSentTokenRequest) -> AddTxResponse:
        """
        Send tokens to another user.

        Args:
            token_event (ApiSentTokenRequest): The token transfer request details.

        Returns:
            AddTxResponse: The transaction response.

        Raises:
            ValueError: If MMN client is not initialized.
        """
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
            public_key=self.ephemeral_key_pair.public_key,
            private_key=self.ephemeral_key_pair.private_key,
            zk_proof=self.zk_proof.proof,
            zk_pub=self.zk_proof.public_input,
        )

        logger.debug(f"Sending transaction: {tx_request}")

        return await self.mmn_client.send_transaction(tx_request)

    def on(self, event_name: str, handler: EventHandler) -> None:
        """
        Register a custom event handler.

        Args:
            event_name (str): The name of the event to listen for.
            handler (EventHandler): The callback function to handle the event.
        """
        self.event_manager.on(event_name, handler)

    def _register_event_handler(self, event_name: str, handler: EventHandler) -> None:
        """
        Register an event handler with automatic async wrapper.

        This helper wraps the given handler in an async function that properly
        invokes it via ``_invoke_handler``, ensuring consistent behavior for
        both sync and async handlers.

        Args:
            event_name (str): The name of the event to listen for.
            handler (EventHandler): The callback function to handle the event.
        """

        async def wrapper(message: Any) -> None:
            await self._invoke_handler(handler, message)

        self.event_manager.on(event_name, wrapper)

    async def get_channel_from_id(self, channel_id: int) -> TextChannel:
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

        clan_id = channel_detail.clan_id or 0

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

    async def get_user_from_id(self, user_id: int) -> User:
        dm_channel = await self.channel_manager.create_dm_channel(user_id)
        if not dm_channel or not dm_channel.channel_id:
            raise ValueError(f"User {user_id} not found in this clan {self.client_id}!")

        user = User(
            user_init_data=UserInitData(
                sender_id=user_id,
                dm_channel_id=dm_channel.channel_id,
            ),
            socket_manager=self.socket_manager,
            channel_manager=self.channel_manager,
        )
        self.users.set(user_id, user)
        return user

    async def add_quick_menu_access(
        self,
        channel_id: int,
        clan_id: int,
        menu_type: int,
        action_msg: str,
        background: str,
        menu_name: str,
    ) -> Any:
        """
        Add a quick menu access entry for this bot.

        Args:
            channel_id: Channel ID
            clan_id: Clan ID
            menu_type: Menu type
            action_msg: Action message
            background: Background image URL
            menu_name: Menu name

        Returns:
            Any: The API response or None if session is unavailable.
        """
        menu_id = generate_snowflake_id()
        session = self.session_manager.get_session()

        if not session:
            return None

        return await self.api_client.add_quick_menu_access(
            session.token,
            channel_id,
            clan_id,
            menu_type,
            action_msg,
            background,
            menu_name,
            menu_id,
            self.client_id,
        )

    async def delete_quick_menu_access(
        self,
        id: int | None = None,
        clan_id: int | None = None,
        bot_id: int | None = None,
        menu_name: str | None = None,
        background: str | None = None,
        action_msg: str | None = None,
    ) -> Any:
        """
        Delete a quick menu access entry.

        Args:
            id: Menu ID to delete.
            clan_id: Clan ID.
            bot_id: Bot ID. Defaults to this client's ID.
            menu_name: Menu name.
            background: Background image URL.
            action_msg: Action message.

        Returns:
            Any: The API response or None if session is unavailable.
        """
        session = self.session_manager.get_session()
        if not session:
            return None

        return await self.api_client.delete_quick_menu_access(
            bearer_token=session.token,
            id=id,
            clan_id=clan_id,
            bot_id=bot_id or self.client_id if self.client_id else None,
            menu_name=menu_name,
            background=background,
            action_msg=action_msg,
        )

    async def list_quick_menu_access(
        self,
        bot_id: str | int | None = None,
        channel_id: int | None = None,
        menu_type: int | None = None,
    ) -> Any:
        """
        List quick menu access items.

        Args:
            bot_id: Bot ID to filter. Defaults to this client's ID.
            channel_id: Channel ID to filter.
            menu_type: Menu type to filter.

        Returns:
            Any: List of quick menu access items or None if session is unavailable.
        """
        session = self.session_manager.get_session()
        if not session:
            return None

        return await self.api_client.list_quick_menu_access(
            bearer_token=session.token,
            bot_id=bot_id,
            channel_id=channel_id,
            menu_type=menu_type,
        )

    async def get_list_friends(
        self,
        limit: int | None = None,
        state: str | None = None,
        cursor: str | None = None,
    ) -> Any:
        """
        Get the list of friends for this client.

        Args:
            limit (int | None): Maximum number of friends to return.
            state (str | None): Filter by friend state.
            cursor (str | None): Pagination cursor.

        Returns:
            Any: The friends list or None if session is unavailable.
        """
        session = self.session_manager.get_session()
        if not session:
            return None
        return await self.api_client.get_list_friends(
            session.token, limit, state, cursor
        )

    async def accept_friend(self, user_id: int, username: str) -> Any:
        """
        Accept a friend request from a user.

        Args:
            user_id (int): The ID of the user to accept.
            username (str): The username of the user to accept.

        Returns:
            Any: The API response or None if session is unavailable.
        """
        session = self.session_manager.get_session()
        if not session:
            return None
        return await self.api_client.request_friend(session.token, username, user_id)

    async def add_friend(self, username: str) -> Any:
        """
        Send a friend request to a user.

        Args:
            username (str): The username of the user to add.

        Returns:
            Any: The API response or None if session is unavailable.
        """
        session = self.session_manager.get_session()
        if not session:
            return None
        return await self.api_client.request_friend(session.token, username)

    async def list_transaction_detail(self, transaction_id: str) -> Any:
        """
        Get details of a specific transaction.

        Args:
            transaction_id (str): The ID of the transaction.

        Returns:
            Any: The transaction details or None if session is unavailable.
        """
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
            all_dm_channels.get(message.sender_id, 0) if all_dm_channels else 0
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
            handler (Callable): Callback to invoke when a channel message is received.
        """
        self._register_event_handler(Events.CHANNEL_MESSAGE, handler)

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
        """
        Register a user-defined handler for channel created events.

        Args:
            handler (Callable): Callback to invoke when a channel is created.
        """
        self._register_event_handler(Events.CHANNEL_CREATED, handler)

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

        Args:
            handler (Callable): Callback to invoke when a channel is updated.
        """
        self._register_event_handler(Events.CHANNEL_UPDATED, handler)

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

        Args:
            handler (Callable): Callback to invoke when a channel is deleted.
        """
        self._register_event_handler(Events.CHANNEL_DELETED, handler)

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
        """
        Register a user-defined handler for token send events.

        Args:
            handler (Callable): Callback to invoke when tokens are sent.
        """
        self._register_event_handler(Events.TOKEN_SEND, handler)

    @auto_bind(Events.TOKEN_SEND)
    async def _handle_token_send_default(self, message: api_pb2.TokenSentEvent) -> None:
        if message.sender_id == int(self.client_id):
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
        """
        Register a user-defined handler for message reaction events.

        Args:
            handler (Callable): Callback to invoke when a message reaction occurs.
        """
        self._register_event_handler(Events.MESSAGE_REACTION, handler)

    def on_channel_user_removed(
        self, handler: Callable[[realtime_pb2.UserChannelRemoved], None]
    ) -> None:
        """
        Register a user-defined handler for channel user removal events.

        Args:
            handler (Callable): Callback to invoke when a user is removed from a channel.
        """
        self._register_event_handler(Events.USER_CHANNEL_REMOVED, handler)

    def on_user_clan_removed(
        self, handler: Callable[[realtime_pb2.UserClanRemoved], None]
    ) -> None:
        """
        Register a user-defined handler for user clan removal events.

        Default internal behavior (removing users from clan cache) is always
        active via an auto-bound handler. This method only wires an additional
        user callback.

        Args:
            handler (Callable): Callback to invoke when a user is removed from a clan.
        """
        self._register_event_handler(Events.USER_CLAN_REMOVED, handler)

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
            handler (Callable): The callback function to handle the event.
                Can be either sync or async.
        """
        self._register_event_handler(Events.USER_CHANNEL_ADDED, handler)

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
                        channel_type=message.channel_desc.type,
                        is_public=not message.channel_desc.channel_private,
                    )
                    break

    def on_give_coffee(
        self, handler: Callable[[api_pb2.GiveCoffeeEvent], None]
    ) -> None:
        """
        Register a user-defined handler for give coffee events.

        Args:
            handler (Callable): Callback to invoke when coffee is given.
        """
        self._register_event_handler(Events.GIVE_COFFEE, handler)

    def on_role_event(self, handler: Callable[[realtime_pb2.RoleEvent], None]) -> None:
        """
        Register a user-defined handler for role events.

        Args:
            handler (Callable): Callback to invoke when a role event occurs.
        """
        self._register_event_handler(Events.ROLE_EVENT, handler)

    def on_clan_event_created(self, handler: Callable[[Any], None]) -> None:
        """
        Register a user-defined handler for clan event creation.

        Args:
            handler (Callable): Callback to invoke when a clan event is created.
        """
        self._register_event_handler(Events.CLAN_EVENT_CREATED, handler)

    def on_message_button_clicked(
        self, handler: Callable[[realtime_pb2.MessageButtonClicked], None]
    ) -> None:
        """
        Register a user-defined handler for message button click events.

        Args:
            handler (Callable): Callback to invoke when a message button is clicked.
        """
        self._register_event_handler(Events.MESSAGE_BUTTON_CLICKED, handler)

    def on_streaming_joined_event(
        self, handler: Callable[[realtime_pb2.StreamingJoinedEvent], None]
    ) -> None:
        """
        Register a user-defined handler for streaming joined events.

        Args:
            handler (Callable): Callback to invoke when a user joins streaming.
        """
        self._register_event_handler(Events.STREAMING_JOINED_EVENT, handler)

    def on_streaming_leaved_event(
        self, handler: Callable[[realtime_pb2.StreamingLeavedEvent], None]
    ) -> None:
        """
        Register a user-defined handler for streaming left events.

        Args:
            handler (Callable): Callback to invoke when a user leaves streaming.
        """
        self._register_event_handler(Events.STREAMING_LEAVED_EVENT, handler)

    def on_dropdown_box_selected(
        self, handler: Callable[[realtime_pb2.DropdownBoxSelected], None]
    ) -> None:
        """
        Register a user-defined handler for dropdown box selection events.

        Args:
            handler (Callable): Callback to invoke when a dropdown box is selected.
        """
        self._register_event_handler(Events.DROPDOWN_BOX_SELECTED, handler)

    def on_webrtc_signaling_fwd(
        self, handler: Callable[[realtime_pb2.WebrtcSignalingFwd], None]
    ) -> None:
        """
        Register a user-defined handler for WebRTC signaling forward events.

        Args:
            handler (Callable): Callback to invoke when WebRTC signaling is forwarded.
        """
        self._register_event_handler(Events.WEBRTC_SIGNALING_FWD, handler)

    def on_voice_started_event(
        self, handler: Callable[[realtime_pb2.VoiceStartedEvent], None]
    ) -> None:
        """
        Register a user-defined handler for voice started events.

        Args:
            handler (Callable): Callback to invoke when voice starts.
        """
        self._register_event_handler(Events.VOICE_STARTED_EVENT, handler)

    def on_voice_ended_event(
        self, handler: Callable[[realtime_pb2.VoiceEndedEvent], None]
    ) -> None:
        """
        Register a user-defined handler for voice ended events.

        Args:
            handler (Callable): Callback to invoke when voice ends.
        """
        self._register_event_handler(Events.VOICE_ENDED_EVENT, handler)

    def on_voice_joined_event(
        self, handler: Callable[[realtime_pb2.VoiceJoinedEvent], None]
    ) -> None:
        """
        Register a user-defined handler for voice joined events.

        Args:
            handler (Callable): Callback to invoke when a user joins voice.
        """
        self._register_event_handler(Events.VOICE_JOINED_EVENT, handler)

    def on_voice_leaved_event(
        self, handler: Callable[[realtime_pb2.VoiceLeavedEvent], None]
    ) -> None:
        """
        Register a user-defined handler for voice left events.

        Args:
            handler (Callable): Callback to invoke when a user leaves voice.
        """
        self._register_event_handler(Events.VOICE_LEAVED_EVENT, handler)

    def on_quick_menu_event(self, handler: Callable[[Any], None]) -> None:
        """
        Register a user-defined handler for quick menu events.

        Args:
            handler (Callable): Callback to invoke when a quick menu event occurs.
        """
        self._register_event_handler(Events.QUICK_MENU, handler)

    def on_role_assign(
        self, handler: Callable[[realtime_pb2.RoleAssignedEvent], None]
    ) -> None:
        """
        Register a user-defined handler for role assignment events.

        Args:
            handler (Callable): Callback to invoke when a role is assigned.
        """
        self._register_event_handler(Events.ROLE_ASSIGN, handler)

    def on_notification(
        self, handler: Callable[[realtime_pb2.Notifications], None]
    ) -> None:
        """
        Register a user-defined handler for notification events.

        Default internal behavior (e.g. auto-handling certain notification
        codes like friend requests) is always active via an auto-bound handler.
        This method only wires an additional user callback.

        Args:
            handler (Callable): Callback to invoke when a notification is received.
        """
        self._register_event_handler(Events.NOTIFICATIONS, handler)

    def on_add_clan_user(
        self, handler: Callable[[realtime_pb2.AddClanUserEvent], None]
    ) -> None:
        """
        Register a user-defined handler for ``AddClanUserEvent``.

        Default internal behavior (joining clan chats and updating caches) is
        always active via an auto-bound handler, even if this method is never
        called. This method only wires an additional user callback.

        Args:
            handler (Callable): Callback to invoke when a clan user is added.
        """
        self._register_event_handler(Events.ADD_CLAN_USER, handler)

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
            id=message.user.user_id if message.user else 0,
            username=message.user.username if message.user else "",
            clan_nick="",
            clan_avatar="",
            avatar=message.user.avatar if message.user else "",
            display_name=message.user.display_name if message.user else "",
            dm_channel_id=0,
        )

        user = User(
            user_init_data=user_init_data,
            socket_manager=self.socket_manager,
            channel_manager=self.channel_manager,
        )
        self.users.set(message.user.user_id, user)
        return user

    async def close_socket(self) -> None:
        await self.socket_manager.get_socket().close()
        self.event_manager = EventManager()

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
                if asyncio.iscoroutinefunction(original_ondisconnect):
                    asyncio.create_task(original_ondisconnect(event))
                else:
                    asyncio.create_task(asyncio.to_thread(original_ondisconnect, event))

            if not self._is_hard_disconnect and self._enable_auto_reconnect:
                await self._retry_connection()

        async def handle_error(event):
            logger.error(f"Socket error: {event}")
            if original_onerror:
                if asyncio.iscoroutinefunction(original_onerror):
                    asyncio.create_task(original_onerror(event))
                else:
                    asyncio.create_task(asyncio.to_thread(original_onerror, event))

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
        logger.debug("Reconnected successfully!")

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
