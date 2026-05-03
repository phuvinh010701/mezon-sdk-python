from unittest.mock import AsyncMock, patch

import pytest
from websockets.protocol import State

from mezon.protobuf.rtapi import realtime_pb2
from mezon.socket.websocket_adapter import WebSocketAdapterPb


class TestWebSocketAdapterPb:
    @pytest.mark.asyncio
    async def test_connect_builds_protobuf_websocket_url(self):
        adapter = WebSocketAdapterPb()
        fake_socket = object()

        with patch(
            "mezon.socket.websocket_adapter.websockets.connect",
            new=AsyncMock(return_value=fake_socket),
        ) as connect_mock:
            await adapter.connect("wss", "socket.example.com", True, "token-123")

        assert adapter._socket is fake_socket
        connect_mock.assert_awaited_once_with(
            "wss://socket.example.com/ws?lang=en&status=true&token=token-123&format=protobuf",
            subprotocols=["protobuf"],
            ping_interval=None,
        )

    @pytest.mark.asyncio
    async def test_send_serializes_envelope(self):
        adapter = WebSocketAdapterPb()
        adapter._socket = AsyncMock()
        adapter._socket.state = State.OPEN
        envelope = realtime_pb2.Envelope()
        envelope.cid = 7

        await adapter.send(envelope)

        adapter._socket.send.assert_awaited_once()
        sent_payload = adapter._socket.send.await_args.args[0]
        assert isinstance(sent_payload, bytes)
        assert sent_payload

    @pytest.mark.asyncio
    async def test_send_accepts_raw_bytes(self):
        adapter = WebSocketAdapterPb()
        adapter._socket = AsyncMock()
        adapter._socket.state = State.OPEN

        await adapter.send(b"raw-bytes")

        adapter._socket.send.assert_awaited_once_with(b"raw-bytes")

    @pytest.mark.asyncio
    async def test_send_rejects_invalid_message_type(self):
        adapter = WebSocketAdapterPb()
        adapter._socket = AsyncMock()
        adapter._socket.state = State.OPEN

        with pytest.raises(ValueError, match="Invalid message type"):
            await adapter.send("bad-message")

    @pytest.mark.asyncio
    async def test_close_waits_for_socket_shutdown(self):
        adapter = WebSocketAdapterPb()
        adapter._socket = AsyncMock()
        adapter._socket.state = State.OPEN

        await adapter.close()

        adapter._socket.close.assert_awaited_once()
        adapter._socket.wait_closed.assert_awaited_once()

    def test_is_open_checks_socket_state(self):
        adapter = WebSocketAdapterPb()
        adapter._socket = AsyncMock()
        adapter._socket.state = State.OPEN

        assert adapter.is_open() is True

        adapter._socket.state = State.CLOSED
        assert adapter.is_open() is False
