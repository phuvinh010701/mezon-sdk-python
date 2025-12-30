import asyncio
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mezon.client import MezonClient

from mezon.api import MezonApi
from mezon.socket import WebSocketAdapterPb, Socket
from mezon.managers.event import EventManager
from mezon.messages import MessageDB
from mezon.structures.clan import Clan

from mezon.models import (
    ApiClanDesc,
    ApiMessageAttachment,
    ApiMessageMention,
    ApiMessageReaction,
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
        mezon_client: "MezonClient",
        message_db: MessageDB,
    ):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.api_client = api_client
        self.event_manager = event_manager
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
        await self.join_all_clans(clans.clandesc, token)

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
                    message_db=self.message_db,
                )
                self.mezon_client.clans.set(clan_desc.clan_id, clan)

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

    async def update_chat_message(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        message_id: str,
        content: Any,
        mentions: Optional[List[ApiMessageMention]] = None,
        attachments: Optional[List[ApiMessageAttachment]] = None,
        hide_editted: bool = False,
        topic_id: Optional[str] = None,
        is_update_msg_topic: Optional[bool] = None,
    ) -> ChannelMessageAck:
        """
        Update (edit) an existing channel message.

        Args:
            clan_id: Clan ID that owns the channel
            channel_id: Channel ID containing the message
            mode: Channel mode
            is_public: Whether the channel is public
            message_id: Identifier of the message to update
            content: Updated message content
            mentions: Updated mentions list
            attachments: Updated attachments list
            hide_editted: Whether to hide the edited indicator
            topic_id: Topic identifier for the message
            is_update_msg_topic: Whether to change topic metadata

        Returns:
            ChannelMessageAck acknowledging the edit
        """

        return await self.socket.update_chat_message(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            message_id=message_id,
            content=content,
            mentions=mentions,
            attachments=attachments,
            hide_editted=hide_editted,
            topic_id=topic_id,
            is_update_msg_topic=is_update_msg_topic,
        )

    async def write_message_reaction(
        self,
        id: str,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        message_id: str,
        emoji_id: str,
        emoji: str,
        count: int,
        message_sender_id: str,
        action_delete: bool = False,
    ) -> ApiMessageReaction:
        """
        Add or remove a reaction on a channel message.

        Args:
            id: Identifier of the reaction payload (optional)
            clan_id: Clan ID that owns the channel
            channel_id: Channel ID containing the message
            mode: Channel mode
            is_public: Whether the channel is public
            message_id: Identifier of the target message
            emoji_id: Emoji identifier
            emoji: Emoji short name
            count: Emoji count
            message_sender_id: Identifier of the original message sender
            action_delete: Whether to remove the reaction

        Returns:
            ApiMessageReaction acknowledgement from the server.
        """

        return await self.socket.write_message_reaction(
            id=id,
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            message_id=message_id,
            emoji_id=emoji_id,
            emoji=emoji,
            count=count,
            message_sender_id=message_sender_id,
            action_delete=action_delete,
        )

    async def remove_chat_message(
        self,
        clan_id: str,
        channel_id: str,
        mode: int,
        is_public: bool,
        message_id: str,
        topic_id: Optional[str] = None,
    ) -> ChannelMessageAck:
        return await self.socket.remove_chat_message(
            clan_id=clan_id,
            channel_id=channel_id,
            mode=mode,
            is_public=is_public,
            message_id=message_id,
            topic_id=topic_id,
        )

    async def disconnect(self) -> None:
        """Close the socket connection and cleanup resources."""
        await self.socket.close()
