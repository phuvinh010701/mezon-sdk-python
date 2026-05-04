from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from mezon.managers.session import SessionManager


class TestSessionManager:
    def test_get_session_returns_current_session(self):
        session = SimpleNamespace(token="token")
        manager = SessionManager(api_client=SimpleNamespace(), session=session)

        assert manager.get_session() is session

    @pytest.mark.asyncio
    async def test_authenticate_delegates_to_api_client(self):
        api_client = SimpleNamespace(
            mezon_authenticate=AsyncMock(return_value="session")
        )
        manager = SessionManager(api_client=api_client)

        result = await manager.authenticate("123", "secret")

        assert result == "session"
        kwargs = api_client.mezon_authenticate.await_args.kwargs
        assert kwargs["basic_auth_username"] == "123"
        assert kwargs["basic_auth_password"] == "secret"
        assert kwargs["body"].account.appid == "123"
        assert kwargs["body"].account.token == "secret"
