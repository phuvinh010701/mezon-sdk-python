import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import jwt

from mezon import MezonClient
from mezon.api.utils import build_url
from mezon.models import ApiSession
from mezon.protobuf.rtapi import realtime_pb2
from mezon.session import Session
from mezon.socket.default_socket import Socket


class OpenAdapter:
    def is_open(self) -> bool:
        return True

    async def send(self, message) -> None:
        return None


class ClosedAdapter:
    def is_open(self) -> bool:
        return False


def make_jwt(exp: int = 1999999999) -> str:
    return jwt.encode({"exp": exp, "vrs": {}}, "test-secret", algorithm="HS256")


def test_restore_ws_url_keeps_existing_protocols() -> None:
    session_ws = Session(
        ApiSession(
            token=make_jwt(),
            refresh_token=make_jwt(),
            api_url="https://api.mezon.ai",
            id_token="token",
            ws_url="ws://sock.mezon.ai",
        )
    )
    session_wss = Session(
        ApiSession(
            token=make_jwt(),
            refresh_token=make_jwt(),
            api_url="https://api.mezon.ai",
            id_token="token",
            ws_url="wss://sock.mezon.ai",
        )
    )

    assert session_ws.ws_url == "ws://sock.mezon.ai"
    assert session_wss.ws_url == "wss://sock.mezon.ai"


def test_restore_ws_url_adds_secure_prefix_when_missing() -> None:
    session = Session(
        ApiSession(
            token=make_jwt(),
            refresh_token=make_jwt(),
            api_url="https://api.mezon.ai",
            id_token="token",
            ws_url="sock.mezon.ai",
        )
    )

    assert session.ws_url == "wss://sock.mezon.ai"


def test_build_url_uses_host_and_port_only_when_present() -> None:
    assert (
        build_url("https", "example.com", 8443, "/v1") == "https://example.com:8443/v1"
    )
    assert build_url("https", "example.com", "", "/v1") == "https://example.com/v1"


def test_generate_cid_returns_incrementing_ints() -> None:
    socket = Socket(ws_url="sock.mezon.ai", adapter=ClosedAdapter())

    first = socket.generate_cid()
    second = socket.generate_cid()

    assert isinstance(first, int)
    assert isinstance(second, int)
    assert (first, second) == (1, 2)


def test_send_with_cid_assigns_integer_cid_to_envelope() -> None:
    socket = Socket(ws_url="sock.mezon.ai", adapter=OpenAdapter())
    envelope = realtime_pb2.Envelope()

    async def exercise() -> None:
        task = asyncio.create_task(socket._send_with_cid(envelope, timeout_ms=5))
        await asyncio.sleep(0)
        assert isinstance(envelope.cid, int)
        assert envelope.cid == 1
        assert envelope.cid in socket.cids
        task.cancel()
        try:
            await task
        except TimeoutError:
            pass

    asyncio.run(exercise())


def test_disconnect_is_safe_before_reconnect_task_exists() -> None:
    client = MezonClient(client_id="1", api_key="key")
    client.disconnect_ai_agent_sse = AsyncMock()
    client.message_db = SimpleNamespace(close=AsyncMock())
    client.socket_manager = SimpleNamespace(
        get_socket=lambda: SimpleNamespace(close=AsyncMock())
    )

    asyncio.run(client.disconnect())

    client.disconnect_ai_agent_sse.assert_awaited_once()
    client.message_db.close.assert_awaited_once()
