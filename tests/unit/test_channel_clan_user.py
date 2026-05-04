from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from mezon.constants import ChannelType, TypeMessage
from mezon.managers.channel import ChannelManager
from mezon.models import ApiChannelDescList, ApiChannelDescription, UserInitData
from mezon.structures.clan import Clan
from mezon.structures.user import User


class TestChannelManagerClanAndUser:
    @pytest.mark.asyncio
    async def test_channel_manager_init_all_dm_channels_builds_mapping(self):
        api_client = SimpleNamespace(
            list_channel_descs=AsyncMock(
                return_value=ApiChannelDescList(
                    channeldesc=[
                        ApiChannelDescription(
                            channel_id=10,
                            type=ChannelType.CHANNEL_TYPE_DM,
                            user_ids=[100],
                        ),
                        ApiChannelDescription(
                            channel_id=20,
                            type=ChannelType.CHANNEL_TYPE_CHANNEL,
                            user_ids=[200],
                        ),
                    ]
                )
            )
        )
        manager = ChannelManager(api_client, SimpleNamespace(), SimpleNamespace())

        await manager.init_all_dm_channels("token")

        assert manager.get_all_dm_channels() == {100: 10}

    @pytest.mark.asyncio
    async def test_channel_manager_create_dm_channel_joins_socket(self):
        channel = ApiChannelDescription(
            channel_id=10, clan_id=0, type=ChannelType.CHANNEL_TYPE_DM
        )
        socket = SimpleNamespace(join_chat=AsyncMock())
        socket_manager = SimpleNamespace(get_socket=lambda: socket)
        session_manager = SimpleNamespace(
            get_session=lambda: SimpleNamespace(token="token")
        )
        api_client = SimpleNamespace(
            create_channel_desc=AsyncMock(return_value=channel)
        )
        manager = ChannelManager(api_client, socket_manager, session_manager)

        result = await manager.create_dm_channel(100)

        assert result.channel_id == 10
        socket.join_chat.assert_awaited_once_with(
            clan_id=0,
            channel_id=10,
            channel_type=ChannelType.CHANNEL_TYPE_DM,
            is_public=False,
        )

    @pytest.mark.asyncio
    async def test_clan_load_channels_and_repr(self):
        client_channel_cache = {}
        client = SimpleNamespace(
            client_id=1,
            channels=SimpleNamespace(
                set=lambda key, value: client_channel_cache.setdefault(key, value)
            ),
        )
        api_client = SimpleNamespace(
            list_channel_descs=AsyncMock(
                return_value=ApiChannelDescList(
                    channeldesc=[
                        ApiChannelDescription(
                            channel_id=10,
                            channel_label="general",
                            type=ChannelType.CHANNEL_TYPE_CHANNEL,
                        )
                    ]
                )
            ),
            list_channel_voice_users=AsyncMock(return_value="voice-users"),
            update_role=AsyncMock(return_value=True),
            list_roles=AsyncMock(return_value="roles"),
        )
        clan = Clan(
            1,
            "Test Clan",
            9,
            client,
            api_client,
            SimpleNamespace(),
            "token",
            SimpleNamespace(),
        )

        await clan.load_channels()
        voice_users = await clan.list_channel_voice_users(channel_id=10)
        updated = await clan.update_role(5, {"title": "Admin"})
        roles = await clan.list_roles(limit=10)

        assert 10 in client_channel_cache
        assert voice_users == "voice-users"
        assert updated is True
        assert roles == "roles"
        assert "Test Clan" in repr(clan)

    @pytest.mark.asyncio
    async def test_clan_list_channel_voice_users_validates_limit(self):
        clan = Clan(
            1,
            "Test Clan",
            9,
            SimpleNamespace(
                client_id=1, channels=SimpleNamespace(set=lambda *args, **kwargs: None)
            ),
            SimpleNamespace(),
            SimpleNamespace(),
            "token",
            SimpleNamespace(),
        )

        with pytest.raises(ValueError, match="0 < limit <= 500"):
            await clan.list_channel_voice_users(limit=0)

    @pytest.mark.asyncio
    async def test_user_send_dm_message_creates_channel_when_missing(self):
        socket_manager = SimpleNamespace(
            write_chat_message=AsyncMock(return_value="ack")
        )
        channel_manager = SimpleNamespace(
            create_dm_channel=AsyncMock(
                return_value=ApiChannelDescription(channel_id=77)
            )
        )
        user = User(
            UserInitData(id=123, username="alice", dm_channel_id=0),
            socket_manager,
            channel_manager,
        )

        result = await user.send_dm_message(
            content={"t": "hello"}, code=TypeMessage.CHAT
        )

        assert result == "ack"
        channel_manager.create_dm_channel.assert_awaited_once_with(123)
        assert user.dm_channel_id == 77

    def test_user_repr_includes_identity_fields(self):
        user = User(
            UserInitData(id=123, username="alice", display_name="Alice"),
            SimpleNamespace(),
            SimpleNamespace(),
        )

        assert "alice" in repr(user)
        assert "Alice" in repr(user)
