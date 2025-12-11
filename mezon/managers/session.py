from typing import Optional
from mezon.api.mezon_api import MezonApi
from mezon.models import (
    ApiAccountApp,
    ApiAuthenticateLogoutRequest,
    ApiAuthenticateRequest,
)
from mezon.session import Session


class SessionManager:
    def __init__(self, api_client: MezonApi, session: Optional[Session] = None):
        self.api_client = api_client
        self.session = session

    def get_session(self) -> Session:
        return self.session

    async def authenticate(self, client_id: str, client_secret: str) -> Session:
        return await self.api_client.mezon_authenticate(
            basic_auth_username=client_id,
            basic_auth_password=client_secret,
            body=ApiAuthenticateRequest(
                account=ApiAccountApp(appid=client_id, token=client_secret)
            ),
        )

    async def logout(self):
        if not self.session:
            return

        return await self.api_client.mezon_authenticate_logout(
            bearer_token=self.session.token,
            body=ApiAuthenticateLogoutRequest(
                token=self.session.token,
                refresh_token=self.session.refresh_token,
            ),
        )
