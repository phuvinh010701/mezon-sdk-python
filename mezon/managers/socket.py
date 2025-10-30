from typing import Any, List, Optional
from mezon.api.mezon_api import MezonApi
from mezon.managers.event import EventManager
from mezon.messages.queue import MessageQueue
from mezon.messages.db import MessageDB
from mezon.models import (
    ApiMessageAttachment,
    ApiMessageMention,
    ApiMessageRef,
    ChannelMessageAck,
    EphemeralMessageData,
)
from mezon.session import Session
from mezon.socket.default_socket import Socket
from mezon.socket.websocket_adapter import WebSocketAdapterPb


class SocketManager:
    def __init__(
        self,
        host: str,
        port: str,
        use_ssl: bool,
        api_client: MezonApi,
        event_manager: EventManager,
        message_queue: MessageQueue,
        mezon_client,
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
        self.adapter = WebSocketAdapterPb(event_manager=event_manager)
        self.socket = Socket(
            host=host, port=port, use_ssl=use_ssl, event_manager=event_manager
        )

    async def connect(self, api_session: Session) -> Session:
        return await self.socket.connect(api_session, create_status=True)

    async def is_connected(self) -> bool:
        return self.socket.is_open()

    async def connect_socket(self, token: str) -> None:
        clans = await self.api_client.list_clans_descs(token)

        for clan in clans.clandesc:
            await self.socket.join_clan_chat(clan.clan_id)

    async def write_ephemeral_message(
        self, message: EphemeralMessageData
    ) -> ChannelMessageAck:
        # TODO: Implement write ephemeral message
        raise NotImplementedError("Not implemented yet")

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
