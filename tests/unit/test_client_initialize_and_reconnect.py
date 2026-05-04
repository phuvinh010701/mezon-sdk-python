from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mezon.client import MezonClient


class TestClientInitializeAndReconnect:
    @pytest.mark.asyncio
    async def test_initialize_managers_sets_clients_and_connects(self):
        client = MezonClient(
            client_id="1", api_key="key", mmn_api_url=None, zk_api_url=None
        )
        sock_session = SimpleNamespace(
            api_url="https://api.example.com",
            ws_url="wss://socket.example.com",
            token="token",
        )

        with (
            patch("mezon.client.SocketManager") as socket_manager_cls,
            patch("mezon.client.ChannelManager") as channel_manager_cls,
            patch("mezon.client.SessionManager") as session_manager_cls,
        ):
            socket_manager = socket_manager_cls.return_value
            socket_manager.connect = AsyncMock()
            socket_manager.connect_socket = AsyncMock()
            channel_manager = channel_manager_cls.return_value
            channel_manager.init_all_dm_channels = AsyncMock()

            await client.initialize_managers(sock_session)

            socket_manager.connect.assert_awaited_once_with(sock_session)
            socket_manager.connect_socket.assert_awaited_once_with("token")
            channel_manager.init_all_dm_channels.assert_awaited_once_with("token")
            session_manager_cls.assert_called()

    @pytest.mark.asyncio
    async def test_retry_connection_stops_on_hard_disconnect_and_succeeds(self):
        client = MezonClient(client_id="1", api_key="key")
        client.get_session = AsyncMock(return_value="session")
        client.initialize_managers = AsyncMock()

        await client._retry_connection(max_retries=1, initial_delay=0, max_delay=0)
        client.initialize_managers.assert_awaited_once_with("session")

        client._is_hard_disconnect = True
        client.get_session.reset_mock()
        await client._retry_connection(max_retries=1, initial_delay=0, max_delay=0)
        client.get_session.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_setup_reconnect_handlers_wraps_socket_callbacks(self):
        client = MezonClient(client_id="1", api_key="key")
        original_disconnect = Mock()
        original_error = Mock()
        fake_socket = SimpleNamespace(
            ondisconnect=original_disconnect, onerror=original_error
        )
        client.socket_manager = SimpleNamespace(get_socket=lambda: fake_socket)
        client._retry_connection = AsyncMock()
        client._enable_auto_reconnect = True
        client._is_hard_disconnect = False

        client._setup_reconnect_handlers()
        await fake_socket.ondisconnect("bye")
        await fake_socket.onerror("err")

        assert client._retry_connection.await_count == 2

    @pytest.mark.asyncio
    async def test_login_sets_state_and_disconnect_cleans_up(self):
        client = MezonClient(client_id="1", api_key="key")
        client.get_session = AsyncMock(return_value="session")
        client.initialize_managers = AsyncMock()
        client.get_ephemeral_key_pair = Mock(
            return_value=SimpleNamespace(public_key="pub", private_key="priv")
        )
        client.get_address_from_user_id = Mock(return_value="addr")
        client.get_zk_proof = AsyncMock(return_value="proof")
        client._setup_reconnect_handlers = Mock()
        client.disconnect_ai_agent_sse = AsyncMock()
        client.close_socket = AsyncMock()
        client.message_db = SimpleNamespace(close=AsyncMock())

        await client.login(enable_auto_reconnect=True)

        assert client._enable_auto_reconnect is True
        assert client._is_hard_disconnect is False
        client._setup_reconnect_handlers.assert_called_once()

        await client.disconnect()
        client.disconnect_ai_agent_sse.assert_awaited_once()
        client.close_socket.assert_awaited_once()
        client.message_db.close.assert_awaited_once()
