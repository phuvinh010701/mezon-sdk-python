import asyncio
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mezon.client import MezonClient

from mezon.api import MezonApi
from mezon.socket import WebSocketAdapterPb, Socket
from mezon.managers.event import EventManager
from mezon.messages import MessageQueue, MessageDB
from mezon.structures.clan import Clan

from mezon.models import (
    ApiClanDesc,
    ApiMessageAttachment,
    ApiMessageMention,
    ApiMessageRef,
    ChannelMessageAck,
)
from mezon.session import Session


class SocketManager:
    """
    Manager for socket operations.
    """

    def __init__(
        self,
        host: str,
        port: str,
        use_ssl: bool,
        api_client: MezonApi,
        event_manager: EventManager,
        message_queue: MessageQueue,
        mezon_client: "MezonClient",
        message_db: MessageDB,
    ):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.api_client = api_client
        self.event_manager = event_manager
        self.message_queue = message_queue
        self.mezon_client = mezon_client
        self.message_db = message_db
        self.adapter = WebSocketAdapterPb()
        self.socket = Socket(
            host=host, port=port, use_ssl=use_ssl, event_manager=event_manager
        )

    def get_socket(self) -> Socket:
        return self.socket

    async def connect(self, api_session: Session) -> Session:
        return await self.socket.connect(api_session, create_status=True)

    async def is_connected(self) -> bool:
        return self.socket.is_open()

    async def connect_socket(self, token: str) -> None:
        """
        Connect to the socket and join all clans.

        Args:
            token: The token to connect to the socket

        Returns:
            None
        """
        clans = await self.api_client.list_clans_descs(token)
        clans.clandesc.append(
            ApiClanDesc(clan_id="0", clan_name="DM", welcome_channel_id="0")
        )
        await asyncio.gather(
            self.join_all_clans(clans.clandesc, token),
        )

    async def join_all_clans(self, clans: List[ApiClanDesc], token: str) -> None:
        async with asyncio.TaskGroup() as tg:
            for clan_desc in clans:
                tg.create_task(self.socket.join_clan_chat(clan_desc.clan_id))

                clan = Clan(
                    clan_id=clan_desc.clan_id,
                    clan_name=clan_desc.clan_name,
                    welcome_channel_id=clan_desc.welcome_channel_id,
                    client=self.mezon_client,
                    api_client=self.api_client,
                    socket_manager=self,
                    session_token=token,
                    message_queue=self.message_queue,
                    message_db=self.message_db,
                )
                self.mezon_client.clans.set(clan_desc.clan_id, clan)

    async def join_dm(self, default_dm_channel_id: str = "0") -> None:
        await self.socket.join_clan_chat(default_dm_channel_id)

    async def write_ephemeral_message(
        self,
        receiver_id: str,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        content: Any,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        references: Optional[List[ApiMessageRef]] = None,
        anonymous_message: Optional[bool] = None,
        mention_everyone: Optional[bool] = None,
        avatar: Optional[str] = None,
        code: Optional[int] = None,
        topic_id: Optional[str] = None,
    ) -> ChannelMessageAck:
        return await self.socket.write_ephemeral_message(
            receiver_id=receiver_id,
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            content=content,
            mentions=mentions,
            attachments=attachments,
            references=references,
            anonymous_message=anonymous_message,
            mention_everyone=mention_everyone,
            avatar=avatar,
            code=code,
            topic_id=topic_id,
        )

    async def write_chat_message(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        content: Any,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        references: Optional[List[ApiMessageRef]] = None,
        anonymous_message: Optional[bool] = None,
        mention_everyone: Optional[bool] = None,
        avatar: Optional[str] = None,
        code: Optional[int] = None,
        topic_id: Optional[str] = None,
    ) -> ChannelMessageAck:
        return await self.socket.write_chat_message(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            content=content,
            mentions=mentions,
            attachments=attachments,
            references=references,
            anonymous_message=anonymous_message,
            mention_everyone=mention_everyone,
            avatar=avatar,
            code=code,
            topic_id=topic_id,
        )

    async def disconnect(self) -> None:
        """Close the socket connection and cleanup resources."""
        await self.socket.close()
