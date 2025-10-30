"""
Copyright 2020 The Mezon Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import aiohttp
from typing import Dict, Any, Optional


from mezon.api.utils import build_body, build_headers, build_params

from ..models import (
    ApiClanDescList,
    ApiSession,
    ApiAuthenticateRequest,
    ApiChannelDescription,
    ApiChannelDescList,
    ApiCreateChannelDescRequest,
)


class MezonApi:
    ENDPOINTS = {
        "authenticate": "/v2/apps/authenticate/token",
        "healthcheck": "/healthcheck",
        "readycheck": "/readycheck",
        "list_clans_descs": "/v2/clandesc",
        "list_channel_descs": "/v2/channeldesc",
        "create_channel_desc": "/v2/channeldesc",
    }

    def __init__(self, bot_id: str, api_key: str, base_url: str, timeout_ms: int):
        """
        Initialize Mezon API client.

        Args:
            bot_id: Bot ID for authentication
            api_key: API key for authentication
            base_url: Base URL for API
            timeout_ms: Timeout in milliseconds
        """
        self.bot_id = bot_id
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_ms = timeout_ms
        self.client_timeout = aiohttp.ClientTimeout(total=timeout_ms / 1000)

    async def call_api(
        self,
        method: str,
        url_path: str,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Any:
        async with aiohttp.ClientSession(timeout=self.client_timeout) as session:
            async with session.request(
                method,
                f"{self.base_url}{url_path}",
                params=query_params,
                data=body,
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def mezon_healthcheck(
        self, bearer_token: str, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Check if the Mezon service is healthy.

        Args:
            bearer_token (str): Bearer token for authentication
            options (Optional[Dict[str, Any]]): Additional options for the request

        Returns:
            Any: Response from the healthcheck endpoint
        """
        headers = build_headers(bearer_token=bearer_token)
        return await self.call_api(
            method="GET",
            url_path="/healthcheck",
            query_params={},
            body=None,
            headers=headers,
        )

    async def mezon_readycheck(
        self, bearer_token: str, options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Check if the Mezon service is ready.

        Args:
            bearer_token (str): Bearer token for authentication
            options (Optional[Dict[str, Any]]): Additional options for the request

        Returns:
            Any: Response from the readycheck endpoint
        """
        headers = build_headers(bearer_token=bearer_token)
        return await self.call_api(
            method="GET",
            url_path=self.ENDPOINTS["readycheck"],
            query_params={},
            body=None,
            headers=headers,
        )

    async def mezon_authenticate(
        self,
        basic_auth_username: str,
        basic_auth_password: str,
        body: ApiAuthenticateRequest,
        options: Optional[Dict[str, Any]] = None,
    ) -> ApiSession:
        """
        Authenticate a app with a token against the server.

        Args:
            basic_auth_username (str): Username for basic authentication
            basic_auth_password (str): Password for basic authentication
            body (ApiAuthenticateRequest): Authentication request body
            options (Optional[Dict[str, Any]]): Additional options for the request

        Returns:
            ApiSession: Session object containing authentication details
        """

        headers = build_headers(basic_auth=(basic_auth_username, basic_auth_password))
        body = build_body(body=body)

        response = await self.call_api(
            method="POST",
            url_path=self.ENDPOINTS["authenticate"],
            query_params={},
            body=body,
            headers=headers,
        )
        return ApiSession.model_validate(response)

    async def list_clans_descs(
        self,
        token: str,
        limit: Optional[int] = None,
        state: Optional[int] = None,
        cursor: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ApiClanDescList:
        headers = build_headers(bearer_token=token)
        params = build_params(
            params={"lang": "en", "limit": limit, "state": state, "cursor": cursor}
        )
        response = await self.call_api(
            method="GET",
            url_path=self.ENDPOINTS["list_clans_descs"],
            query_params=params,
            body=None,
            headers=headers,
        )
        return ApiClanDescList.model_validate(response)

    async def list_channel_descs(
        self,
        token: str,
        channel_type: int,
        clan_id: Optional[str] = None,
        limit: Optional[int] = None,
        state: Optional[int] = None,
        cursor: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ApiChannelDescList:
        """
        List channel descriptions.

        Args:
            token: Bearer token for authentication
            channel_type: Channel type to filter (required)
            clan_id: Clan ID to filter channels
            limit: Maximum number of results
            state: Channel state filter
            cursor: Pagination cursor
            parent_id: Parent channel ID
            options: Additional options for the request

        Returns:
            ApiChannelDescList: List of channel descriptions with optional cursor
        """
        headers = build_headers(bearer_token=token)
        params = build_params(
            params={
                "clan_id": clan_id,
                "type": channel_type,
                "limit": limit,
                "state": state,
                "cursor": cursor,
            }
        )
        response = await self.call_api(
            method="GET",
            url_path=self.ENDPOINTS["list_channel_descs"],
            query_params=params,
            body=None,
            headers=headers,
        )
        return ApiChannelDescList.model_validate(response)

    async def create_channel_desc(
        self,
        token: str,
        request: ApiCreateChannelDescRequest,
        options: Optional[Dict[str, Any]] = None,
    ) -> ApiChannelDescription:
        """
        Create a channel description.

        Args:
            token: Bearer token for authentication
            request: Channel creation request
            options: Additional options for the request

        Returns:
            ApiChannelDescription: Created channel description
        """
        headers = build_headers(bearer_token=token)
        body = build_body(body=request)

        response = await self.call_api(
            method="POST",
            url_path=self.ENDPOINTS["create_channel_desc"],
            query_params={},
            body=body,
            headers=headers,
        )
        return ApiChannelDescription.model_validate(response)
