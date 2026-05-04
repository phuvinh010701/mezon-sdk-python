from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from mezon.models import ChannelMessageAck
from mezon.protobuf.rtapi import realtime_pb2
from mezon.socket.default_socket import Socket


class OpenAdapter:
    def __init__(self):
        self.close = AsyncMock()
        self.send = AsyncMock()
        self._socket = []

    def is_open(self):
        return True


class ClosedAdapter:
    def __init__(self):
        self.close = AsyncMock()
        self.send = AsyncMock()
        self._socket = []

    def is_open(self):
        return False


class TestDefaultSocketExtended:
    def make_ack_envelope(self):
        envelope = realtime_pb2.Envelope()
        envelope.channel_message_ack.channel_id = 1
        envelope.channel_message_ack.message_id = 2
        return envelope

    def make_channel_message_envelope(self):
        envelope = realtime_pb2.Envelope()
        envelope.channel_message.channel_id = 1
        envelope.channel_message.message_id = 2
        envelope.channel_message.sender_id = 3
        envelope.channel_message.content = '{"t":"secret"}'
        return envelope

    def test_handle_response_returns_model_and_raises_when_missing(self):
        socket = Socket(ws_url="socket.example.com", adapter=ClosedAdapter())
        envelope = self.make_ack_envelope()

        ack = socket._handle_response(
            envelope, "channel_message_ack", ChannelMessageAck, "missing"
        )
        assert ack.channel_id == 1

        with pytest.raises(Exception, match="missing"):
            socket._handle_response(
                None, "channel_message_ack", ChannelMessageAck, "missing"
            )

    @pytest.mark.asyncio
    async def test_send_envelope_with_field_copies_message(self):
        socket = Socket(ws_url="socket.example.com", adapter=ClosedAdapter())
        socket._send_with_cid = AsyncMock(return_value="ok")
        message = realtime_pb2.ChannelMessageSend(clan_id=1, channel_id=2)

        result = await socket._send_envelope_with_field("channel_message_send", message)

        assert result == "ok"
        sent_envelope = socket._send_with_cid.await_args.args[0]
        assert sent_envelope.channel_message_send.clan_id == 1
        assert sent_envelope.channel_message_send.channel_id == 2

    @pytest.mark.asyncio
    async def test_join_and_leave_chat_build_expected_payloads(self):
        socket = Socket(ws_url="socket.example.com", adapter=ClosedAdapter())
        socket._send_with_cid = AsyncMock(return_value=self.make_ack_envelope())

        clan_join = await socket.join_clan_chat(10)
        channel_join = await socket.join_chat(10, 20, 7, False)
        await socket.leave_chat(10, 20, 7, False)

        assert clan_join.clan_id == 10
        assert channel_join.channel_id == 20
        leave_envelope = socket._send_with_cid.await_args_list[2].args[0]
        assert leave_envelope.channel_leave.channel_id == 20

    @pytest.mark.asyncio
    async def test_write_methods_use_expected_response_fields(self):
        socket = Socket(ws_url="socket.example.com", adapter=ClosedAdapter())
        socket._send_envelope_with_field = AsyncMock(
            side_effect=[
                self.make_ack_envelope(),
                self.make_ack_envelope(),
                self.make_channel_message_envelope(),
            ]
        )
        socket._send_with_cid = AsyncMock(return_value=self.make_ack_envelope())

        ack1 = await socket.write_chat_message(1, 2, 3, True, {"t": "hello"})
        ack2 = await socket.update_chat_message(1, 2, 3, True, 9, {"t": "updated"})
        ack3 = await socket.write_ephemeral_message([1], 1, 2, 3, True, {"t": "secret"})
        ack4 = await socket.remove_chat_message(1, 2, 3, True, 9, 99)

        assert ack1.message_id == 2
        assert ack2.channel_id == 1
        assert ack3.channel_id == 1
        assert ack4.channel_id == 1

    @pytest.mark.asyncio
    async def test_typing_and_status_helpers_return_dicts(self):
        socket = Socket(ws_url="socket.example.com", adapter=ClosedAdapter())

        typing_envelope = realtime_pb2.Envelope()
        typing_envelope.message_typing_event.channel_id = 2
        typing_envelope.message_typing_event.clan_id = 1

        seen_envelope = realtime_pb2.Envelope()
        seen_envelope.last_seen_message_event.channel_id = 2
        seen_envelope.last_seen_message_event.message_id = 9

        pin_envelope = realtime_pb2.Envelope()
        pin_envelope.last_pin_message_event.channel_id = 2
        pin_envelope.last_pin_message_event.message_id = 9

        status_envelope = realtime_pb2.Envelope()
        status_envelope.custom_status_event.clan_id = 1
        status_envelope.custom_status_event.status = "busy"

        voice_join_envelope = realtime_pb2.Envelope()
        voice_join_envelope.voice_joined_event.clan_id = 1
        voice_join_envelope.voice_joined_event.voice_channel_id = 2

        socket._send_with_cid = AsyncMock(
            side_effect=[
                typing_envelope,
                seen_envelope,
                pin_envelope,
                status_envelope,
                voice_join_envelope,
                None,
            ]
        )

        assert (await socket.write_message_typing(1, 2, 3, True))["channelId"] == "2"
        assert (await socket.write_last_seen_message(1, 2, 3, 9, 100))[
            "messageId"
        ] == "9"
        assert (await socket.write_last_pin_message(1, 2, 3, True, 9, 100, 1))[
            "messageId"
        ] == "9"
        assert (await socket.write_custom_status(1, "busy"))["status"] == "busy"
        assert (await socket.write_voice_joined("id", 1, "clan", 2, "voice", "user"))[
            "voiceChannelId"
        ] == "2"
        assert await socket.write_voice_leaved("id", 1, 2, 3) is None

    @pytest.mark.asyncio
    async def test_emit_event_from_envelope_routes_payload(self):
        socket = Socket(
            ws_url="socket.example.com",
            adapter=ClosedAdapter(),
            event_manager=SimpleNamespace(emit=AsyncMock()),
        )
        envelope = realtime_pb2.Envelope()
        envelope.channel_created_event.clan_id = 1
        envelope.channel_created_event.channel_id = 2

        await socket._emit_event_from_envelope(envelope)

        socket.event_manager.emit.assert_awaited_once()
        event_name, payload = socket.event_manager.emit.await_args.args
        assert event_name == "channel_created_event"
        assert payload.clan_id == 1

    @pytest.mark.asyncio
    async def test_connect_returns_existing_session_when_already_open(self):
        adapter = OpenAdapter()
        socket = Socket(ws_url="socket.example.com", adapter=adapter)
        socket.session = "existing"

        assert await socket.connect(SimpleNamespace(token="token")) == "existing"

    @pytest.mark.asyncio
    async def test_connect_timeout_raises_timeout_error(self):
        adapter = ClosedAdapter()

        async def slow_connect(*args, **kwargs):
            raise TimeoutError

        adapter.connect = slow_connect
        socket = Socket(ws_url="socket.example.com", adapter=adapter)

        with patch(
            "mezon.socket.default_socket.asyncio.wait_for",
            side_effect=__import__("asyncio").TimeoutError,
        ):
            with pytest.raises(TimeoutError, match="timed out"):
                await socket.connect(SimpleNamespace(token="token"))
