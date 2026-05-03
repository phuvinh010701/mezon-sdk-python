from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from mezon.managers.event import EventManager
from mezon.managers.socket import SocketManager
from mezon.messages.db import MessageDB
from mezon.models import ApiClanDesc


class TestSocketManager:
    def make_manager(self):
        api_client = SimpleNamespace(list_clans_descs=AsyncMock())
        mezon_client = SimpleNamespace(
            clans=SimpleNamespace(set=lambda *args, **kwargs: None)
        )
        return SocketManager(
            ws_url="socket.example.com",
            use_ssl=True,
            api_client=api_client,
            event_manager=EventManager(),
            mezon_client=mezon_client,
            message_db=MessageDB(":memory:"),
        )

    @pytest.mark.asyncio
    async def test_connect_closes_existing_socket_before_reconnect(self):
        manager = self.make_manager()
        manager.socket.is_open = lambda: True
        manager.socket.close = AsyncMock()
        manager.socket.connect = AsyncMock(return_value="connected-session")

        result = await manager.connect("session")

        manager.socket.close.assert_awaited_once()
        manager.socket.connect.assert_awaited_once_with("session", create_status=True)
        assert result == "connected-session"

    @pytest.mark.asyncio
    async def test_is_connected_reads_socket_state(self):
        manager = self.make_manager()
        manager.socket.is_open = lambda: True

        assert await manager.is_connected() is True

    @pytest.mark.asyncio
    async def test_connect_socket_appends_dm_clan_and_joins_all(self):
        manager = self.make_manager()
        clans = SimpleNamespace(clandesc=[ApiClanDesc(clan_id=1, clan_name="One")])
        manager.api_client.list_clans_descs = AsyncMock(return_value=clans)
        manager.join_all_clans = AsyncMock()

        await manager.connect_socket("token")

        manager.api_client.list_clans_descs.assert_awaited_once_with("token")
        manager.join_all_clans.assert_awaited_once()
        joined_clans = manager.join_all_clans.await_args.args[0]
        assert [clan.clan_id for clan in joined_clans] == [1, 0]

    @pytest.mark.asyncio
    async def test_join_all_clans_joins_and_populates_cache(self):
        clan_cache = {}
        mezon_client = SimpleNamespace(
            client_id=123,
            clans=SimpleNamespace(
                set=lambda key, value: clan_cache.setdefault(key, value)
            ),
        )
        manager = SocketManager(
            ws_url="socket.example.com",
            use_ssl=True,
            api_client=SimpleNamespace(),
            event_manager=EventManager(),
            mezon_client=mezon_client,
            message_db=MessageDB(":memory:"),
        )
        manager.socket.join_clan_chat = AsyncMock()

        clans = [
            ApiClanDesc(clan_id=1, clan_name="One", welcome_channel_id=10),
            ApiClanDesc(clan_id=2, clan_name="Two", welcome_channel_id=20),
        ]

        await manager.join_all_clans(clans, "token")

        assert manager.socket.join_clan_chat.await_count == 2
        assert set(clan_cache) == {1, 2}

    @pytest.mark.asyncio
    async def test_write_chat_message_delegates_to_socket(self):
        manager = self.make_manager()
        manager.socket.write_chat_message = AsyncMock(return_value="ack")

        result = await manager.write_chat_message(1, 2, 3, True, {"t": "hello"})

        assert result == "ack"
        manager.socket.write_chat_message.assert_awaited_once()
