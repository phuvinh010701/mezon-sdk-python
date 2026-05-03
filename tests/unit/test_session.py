import time

import jwt

from mezon.models import ApiSession
from mezon.session import Session

SECRET = "this-is-a-longer-test-secret-key-for-jwt"


def make_jwt(exp: int, **extra) -> str:
    payload = {"exp": exp, "vrs": {"env": "test"}, **extra}
    return jwt.encode(payload, SECRET, algorithm="HS256")


class TestSession:
    def test_init_uses_api_session_user_id_when_present(self):
        session = Session(
            ApiSession(
                token=make_jwt(2_000_000_000),
                refresh_token=make_jwt(2_100_000_000),
                api_url="https://api.example.com",
                id_token="id-token",
                ws_url="socket.example.com",
                user_id=123,
            )
        )

        assert session.user_id == "123"
        assert session.ws_url == "wss://socket.example.com"
        assert session.vars == {"env": "test"}

    def test_init_reads_user_id_from_token_when_missing(self):
        session = Session(
            ApiSession(
                token=make_jwt(2_000_000_000, uid=456),
                refresh_token=make_jwt(2_100_000_000),
                api_url="https://api.example.com",
                id_token="id-token",
                ws_url="ws://socket.example.com",
            )
        )

        assert session.user_id == "456"
        assert session.ws_url == "ws://socket.example.com"

    def test_is_expired_and_is_refresh_expired(self):
        now = int(time.time())
        session = Session(
            ApiSession(
                token=make_jwt(now + 60),
                refresh_token=make_jwt(now + 120),
                api_url="https://api.example.com",
                id_token="id-token",
                ws_url="wss://socket.example.com",
            )
        )

        assert session.is_expired(now) is False
        assert session.is_refresh_expired(now) is False
        assert session.is_expired(now + 61) is True
        assert session.is_refresh_expired(now + 121) is True

    def test_update_replaces_tokens_and_expiry(self):
        session = Session(
            ApiSession(
                token=make_jwt(1000),
                refresh_token=make_jwt(2000),
                api_url="https://api.example.com",
                id_token="id-token",
                ws_url="wss://socket.example.com",
            )
        )

        session.update(make_jwt(3000, vrs={"env": "prod"}), make_jwt(4000))

        assert session.expires_at == 3000
        assert session.refresh_expires_at == 4000
        assert session.vars == {"env": "prod"}
