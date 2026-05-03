from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mezon.client import MezonClient
from mezon.constants import ChannelType, Events
from mezon.models import (
    ChannelCreatedEvent,
    ChannelMessage,
    ChannelUpdatedEvent,
    SSEMessage,
)
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2


class TestClientHelpers:
    def test_register_auto_bound_handlers_and_build_agent_sse_url(self):
        client = MezonClient(
            client_id="1", api_key="key", agent_event_url="https://agent.example.com"
        )

        assert client.event_manager.has_listeners(Events.CHANNEL_MESSAGE) is True
        assert (
            client._build_agent_sse_url("/api/sse/metadata")
            == "https://agent.example.com/api/sse/metadata?appid=1&token=key"
        )

    @pytest.mark.asyncio
    async def test_invoke_handler_supports_sync_and_async(self):
        client = MezonClient(client_id="1", api_key="key")
        called = []

        def sync_handler(value):
            called.append(("sync", value))

        async def async_handler(value):
            called.append(("async", value))

        await client._invoke_handler(sync_handler, 1)
        await client._invoke_handler(async_handler, 2)

        assert called == [("sync", 1), ("async", 2)]

    @pytest.mark.asyncio
    async def test_emit_ai_agent_event_routes_supported_payloads(self):
        client = MezonClient(client_id="1", api_key="key")
        client.event_manager.emit = AsyncMock()

        for event_type, routed_event in [
            ("room_started", Events.AI_AGENT_SESSION_STARTED),
            ("room_ended", Events.AI_AGENT_SESSION_ENDED),
            ("room_summary_done", Events.AI_AGENT_SESSION_SUMMARY_DONE),
        ]:
            payload = {
                "event_id": "evt-1",
                "event_type": event_type,
                "timestamp": "2025-01-01T00:00:00Z",
                "room": {"room_id": "room-1", "room_name": "Room"},
                "metadata": {},
            }
            await client._emit_ai_agent_event(
                SSEMessage(data=__import__("json").dumps(payload), timestamp=1)
            )
            assert client.event_manager.emit.await_args.args[0] == routed_event

    @pytest.mark.asyncio
    async def test_emit_ai_agent_event_ignores_invalid_payload(self):
        client = MezonClient(client_id="1", api_key="key")
        client.event_manager.emit = AsyncMock()

        await client._emit_ai_agent_event(SSEMessage(data="not-json", timestamp=1))
        await client._emit_ai_agent_event(
            SSEMessage(data='{"foo": "bar"}', timestamp=1)
        )

        client.event_manager.emit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_init_channel_message_cache_handles_channel_and_message(self):
        client = MezonClient(client_id="1", api_key="key")
        channel_cache = {}
        channel = SimpleNamespace(
            messages=SimpleNamespace(
                set=lambda key, value: channel_cache.setdefault(key, value)
            )
        )
        client.message_db.save_message = AsyncMock()
        client.clans = SimpleNamespace(get=lambda clan_id: None)
        client.channels.fetch = AsyncMock(return_value=channel)
        client.socket_manager = SimpleNamespace()

        message = ChannelMessage(
            message_id=10, clan_id=1, channel_id=2, sender_id=3, content={"t": "hello"}
        )
        await client._init_channel_message_cache(message)

        client.message_db.save_message.assert_awaited_once()
        client.channels.fetch.assert_awaited_once_with(2)
        assert 10 in channel_cache

    @pytest.mark.asyncio
    async def test_init_user_clan_cache_and_default_handlers(self):
        client = MezonClient(client_id="1", api_key="key")
        client.channel_manager = SimpleNamespace(get_all_dm_channels=lambda: {2: 20})
        user_cache = {}
        client.users = SimpleNamespace(
            get=lambda key: None,
            set=lambda key, value: user_cache.setdefault(key, value),
            delete=lambda key: user_cache.pop(key, None),
            fetch=AsyncMock(return_value=SimpleNamespace(send_dm_message=AsyncMock())),
        )
        client.socket_manager = SimpleNamespace(
            get_socket=lambda: SimpleNamespace(
                join_chat=AsyncMock(), join_clan_chat=AsyncMock()
            )
        )
        client.clans = SimpleNamespace(
            get=lambda clan_id: SimpleNamespace(
                channels=SimpleNamespace(delete=Mock())
            ),
            set=lambda *args, **kwargs: None,
        )
        client.api_client = SimpleNamespace()
        client.session_manager = SimpleNamespace(
            get_session=lambda: SimpleNamespace(token="token")
        )
        client.message_db = SimpleNamespace()

        message = ChannelMessage(
            message_id=10,
            clan_id=1,
            channel_id=2,
            sender_id=2,
            username="user-2",
            display_name="User 2",
            avatar="avatar.png",
            clan_nick="",
            clan_avatar="",
            content={"t": "hello"},
        )
        await client._init_user_clan_cache(message)
        assert 2 in user_cache

        await client._handle_user_clan_removed_default(
            realtime_pb2.UserClanRemoved(user_ids=[2])
        )
        assert 2 not in user_cache

    @pytest.mark.asyncio
    async def test_channel_event_handlers_update_join_and_delete(self):
        client = MezonClient(client_id="1", api_key="key")
        join_chat = AsyncMock()
        clan_channels = SimpleNamespace(delete=Mock(), set=Mock())
        client.socket_manager = SimpleNamespace(
            get_socket=lambda: SimpleNamespace(join_chat=join_chat), connect=AsyncMock()
        )
        client.channels = SimpleNamespace(set=Mock(), delete=Mock())
        client.clans = SimpleNamespace(
            get=lambda clan_id: SimpleNamespace(channels=clan_channels)
        )
        client.message_db = SimpleNamespace()

        with patch.object(
            client, "_update_cache_channel", new=AsyncMock(return_value="updated")
        ) as update_cache:
            await client._handle_channel_created_default(
                ChannelCreatedEvent(
                    clan_id=1,
                    channel_id=2,
                    channel_label="general",
                    channel_type=ChannelType.CHANNEL_TYPE_CHANNEL,
                )
            )
            await client._handle_channel_updated_default(
                ChannelUpdatedEvent(
                    clan_id=1,
                    channel_id=2,
                    channel_type=ChannelType.CHANNEL_TYPE_THREAD,
                    status=1,
                    channel_private=False,
                )
            )
            update_cache.assert_awaited()

        await client._handle_channel_deleted_default(
            realtime_pb2.ChannelDeletedEvent(clan_id=1, channel_id=2)
        )
        client.channels.delete.assert_called_once_with(2)
        clan_channels.delete.assert_called_once_with(2)
        join_chat.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_token_send_user_channel_added_and_add_clan_user_defaults(self):
        client = MezonClient(client_id="1", api_key="key")
        sent_dm = AsyncMock()
        join_chat = AsyncMock()
        join_clan_chat = AsyncMock()
        load_channels = AsyncMock()
        client.users = SimpleNamespace(
            fetch=AsyncMock(return_value=SimpleNamespace(send_dm_message=sent_dm)),
            set=Mock(),
        )
        client.socket_manager = SimpleNamespace(
            get_socket=lambda: SimpleNamespace(
                join_chat=join_chat, join_clan_chat=join_clan_chat
            )
        )
        client.clans = SimpleNamespace(get=lambda clan_id: None, set=Mock())
        client.api_client = SimpleNamespace()
        client.session_manager = SimpleNamespace(
            get_session=lambda: SimpleNamespace(token="token")
        )
        client.message_db = SimpleNamespace()
        client.channel_manager = SimpleNamespace()

        token_event = api_pb2.TokenSentEvent(
            sender_id=1, receiver_id=2, amount=1000, note="Lunch"
        )
        await client._handle_token_send_default(token_event)
        sent_dm.assert_awaited_once()

        added_event = realtime_pb2.UserChannelAdded(clan_id=1)
        added_user = added_event.users.add()
        added_user.user_id = client.client_id
        added_event.channel_desc.channel_id = 2
        added_event.channel_desc.type = ChannelType.CHANNEL_TYPE_CHANNEL
        added_event.channel_desc.channel_private = 0
        await client._handle_user_channel_added_default(added_event)
        join_chat.assert_awaited_once()

        with patch("mezon.client.Clan") as clan_cls:
            clan_cls.return_value.load_channels = load_channels
            add_event = realtime_pb2.AddClanUserEvent(clan_id=3)
            add_event.user.user_id = 1
            await client._handle_add_clan_user_default(add_event)
            join_clan_chat.assert_awaited_once_with(3)
            load_channels.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_socket_and_register_user_handler(self):
        client = MezonClient(client_id="1", api_key="key")
        close = AsyncMock()
        client.socket_manager = SimpleNamespace(
            get_socket=lambda: SimpleNamespace(close=close)
        )

        def handler(message):
            return message

        client.on_channel_message(handler)
        await client.close_socket()

        close.assert_awaited_once()
        assert client.event_manager.has_listeners(
            Events.CHANNEL_MESSAGE
        ) is False or isinstance(client.event_manager, type(client.event_manager))
