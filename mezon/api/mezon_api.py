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
from aiolimiter import AsyncLimiter


from mezon.api.utils import build_body, build_headers, build_params
from mezon.utils.logger import get_logger

from ..models import (
    ApiClanDescList,
    ApiSession,
    ApiAuthenticateRequest,
    ApiAuthenticateRefreshRequest,
    ApiAuthenticateLogoutRequest,
    ApiChannelDescription,
    ApiChannelDescList,
    ApiCreateChannelDescRequest,
    ApiUpdateMessageRequest,
    ApiRegisterStreamingChannelRequest,
    ApiSentTokenRequest,
    ApiVoiceChannelUserList,
    ApiRoleListEventResponse,
)

logger = get_logger(__name__)


class MezonApi:
    ENDPOINTS = {
        "authenticate": "/v2/apps/authenticate/token",
        "authenticate_refresh": "/v2/apps/authenticate/refresh",
        "authenticate_logout": "/v2/apps/authenticate/logout",
        "healthcheck": "/healthcheck",
        "readycheck": "/readycheck",
        "list_clans_descs": "/v2/clandesc",
        "list_channel_descs": "/v2/channeldesc",
        "create_channel_desc": "/v2/channeldesc",
        "get_channel_detail": "/v2/channeldesc/{channel_id}",
        "request_friend": "/v2/friend",
        "get_list_friends": "/v2/friend",
        "list_channel_voice_users": "/v2/channelvoice",
        "update_role": "/v2/roles/{role_id}",
        "list_roles": "/v2/roles",
        "delete_message": "/v2/messages/{message_id}",
        "update_message": "/v2/messages/{message_id}",
        "send_token": "/v2/sendtoken",
        "register_streaming_channel": "/v2/streaming-channels",
        "add_quick_menu_access": "/v2/quickmenuaccess",
        "delete_quick_menu_access": "/v2/quickmenuaccess",
    }

    _rate_limiter = AsyncLimiter(max_rate=1, time_period=1.25)

    def __init__(self, client_id: str, api_key: str, base_url: str, timeout_ms: int):
        """
        Initialize Mezon API client.

        Args:
            client_id: Bot ID for authentication
            api_key: API key for authentication
            base_url: Base URL for API
            timeout_ms: Timeout in milliseconds
        """
        self.client_id = client_id
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
        logger.debug(
            f"Method: {method}, URL: {url_path}, Query Params: {query_params}, Body: {body}, Headers: {headers}"
        )
        async with self._rate_limiter:
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
            url_path=self.ENDPOINTS["healthcheck"],
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
        params = build_params(params={"limit": limit, "state": state, "cursor": cursor})
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
                "channel_type": channel_type,
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

    async def get_channel_detail(
        self, token: str, channel_id: str
    ) -> ApiChannelDescription:
        headers = build_headers(bearer_token=token)
        response = await self.call_api(
            method="GET",
            url_path=self.ENDPOINTS["get_channel_detail"].format(channel_id=channel_id),
            query_params={},
            body=None,
            headers=headers,
        )
        return ApiChannelDescription.model_validate(response)

    async def request_friend(
        self,
        token: str,
        usernames: str,
        ids: Optional[str] = None,
    ) -> Any:
        headers = build_headers(bearer_token=token)
        params = build_params(params={"usernames": usernames, "ids": ids})

        response = await self.call_api(
            method="POST",
            url_path=self.ENDPOINTS["request_friend"],
            query_params=params,
            body=None,
            headers=headers,
        )
        return response

    async def get_list_friends(
        self,
        token: str,
        limit: Optional[int] = None,
        state: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> Any:
        headers = build_headers(bearer_token=token)
        params = build_params(params={"limit": limit, "state": state, "cursor": cursor})

        response = await self.call_api(
            method="GET",
            url_path=self.ENDPOINTS["get_list_friends"],
            query_params=params,
            body=None,
            headers=headers,
        )
        return response

    async def list_channel_voice_users(
        self,
        token: str,
        clan_id: str,
        channel_id: str = "",
        channel_type: int = 4,
        limit: int = 500,
        state: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> ApiVoiceChannelUserList:
        headers = build_headers(bearer_token=token)
        params = build_params(
            params={
                "clan_id": clan_id,
                "channel_id": channel_id,
                "channel_type": channel_type,
                "limit": limit,
                "state": state,
                "cursor": cursor,
            }
        )

        response = await self.call_api(
            method="GET",
            url_path=self.ENDPOINTS["list_channel_voice_users"],
            query_params=params,
            body=None,
            headers=headers,
        )
        return ApiVoiceChannelUserList.model_validate(response)

    async def update_role(
        self,
        token: str,
        role_id: str,
        request: Dict[str, Any],
    ) -> bool:
        headers = build_headers(bearer_token=token)
        body = build_body(body=request)

        response = await self.call_api(
            method="PUT",
            url_path=self.ENDPOINTS["update_role"].format(role_id=role_id),
            query_params={},
            body=body,
            headers=headers,
        )
        return response

    async def list_roles(
        self,
        token: str,
        clan_id: str,
        limit: Optional[str] = None,
        state: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> ApiRoleListEventResponse:
        headers = build_headers(bearer_token=token)
        params = build_params(
            params={
                "clan_id": clan_id,
                "limit": limit,
                "state": state,
                "cursor": cursor,
            }
        )

        response = await self.call_api(
            method="GET",
            url_path=self.ENDPOINTS["list_roles"],
            query_params=params,
            body=None,
            headers=headers,
        )
        return response

    async def mezon_authenticate_refresh(
        self,
        basic_auth_username: str,
        basic_auth_password: str,
        body: ApiAuthenticateRefreshRequest,
        options: Optional[Dict[str, Any]] = None,
    ) -> ApiSession:
        """
        Refresh a user's session using a refresh token.

        Args:
            basic_auth_username: Username for basic authentication
            basic_auth_password: Password for basic authentication
            body: Refresh request containing refresh token
            options: Additional options for the request

        Returns:
            ApiSession: New session with updated tokens
        """
        headers = build_headers(basic_auth=(basic_auth_username, basic_auth_password))
        body_json = build_body(body=body)

        response = await self.call_api(
            method="POST",
            url_path=self.ENDPOINTS["authenticate_refresh"],
            query_params={},
            body=body_json,
            headers=headers,
        )
        return ApiSession.model_validate(response)

    async def mezon_authenticate_logout(
        self,
        bearer_token: str,
        body: ApiAuthenticateLogoutRequest,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Log out a session, invalidate a refresh token, or log out all sessions.

        Args:
            bearer_token: Bearer token for authentication
            body: Logout request with token and refresh_token
            options: Additional options for the request

        Returns:
            Any: Response from logout endpoint
        """
        headers = build_headers(bearer_token=bearer_token)
        body_json = build_body(body=body)

        response = await self.call_api(
            method="POST",
            url_path=self.ENDPOINTS["authenticate_logout"],
            query_params={},
            body=body_json,
            headers=headers,
        )
        return response

    async def mezon_delete_message(
        self,
        bearer_token: str,
        message_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Delete a message by ID.

        Args:
            bearer_token: Bearer token for authentication
            message_id: ID of the message to delete
            options: Additional options for the request

        Returns:
            Any: Response from delete endpoint
        """
        headers = build_headers(bearer_token=bearer_token)

        response = await self.call_api(
            method="DELETE",
            url_path=self.ENDPOINTS["delete_message"].format(message_id=message_id),
            query_params={},
            body=None,
            headers=headers,
        )
        return response

    async def mezon_update_message(
        self,
        bearer_token: str,
        message_id: str,
        body: ApiUpdateMessageRequest,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Update a message by ID.

        Args:
            bearer_token: Bearer token for authentication
            message_id: ID of the message to update
            body: Update request with new message content
            options: Additional options for the request

        Returns:
            Any: Updated message response
        """
        headers = build_headers(bearer_token=bearer_token)
        body_json = build_body(body=body)

        response = await self.call_api(
            method="PUT",
            url_path=self.ENDPOINTS["update_message"].format(message_id=message_id),
            query_params={},
            body=body_json,
            headers=headers,
        )
        return response

    async def send_token(
        self,
        bearer_token: str,
        body: ApiSentTokenRequest,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send token to another user.

        Args:
            bearer_token: Bearer token for authentication
            body: Token send request with receiver_id, amount, note
            options: Additional options for the request

        Returns:
            Any: Token send response
        """
        headers = build_headers(bearer_token=bearer_token)
        body_json = build_body(body=body)

        response = await self.call_api(
            method="POST",
            url_path=self.ENDPOINTS["send_token"],
            query_params={},
            body=body_json,
            headers=headers,
        )
        return response

    async def register_streaming_channel(
        self,
        bearer_token: str,
        body: ApiRegisterStreamingChannelRequest,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Register a streaming channel.

        Args:
            bearer_token: Bearer token for authentication
            body: Streaming channel registration request
            options: Additional options for the request

        Returns:
            Any: Registration response
        """
        headers = build_headers(bearer_token=bearer_token)
        body_json = build_body(body=body)

        response = await self.call_api(
            method="POST",
            url_path=self.ENDPOINTS["register_streaming_channel"],
            query_params={},
            body=body_json,
            headers=headers,
        )
        return response

    async def list_transaction_detail(
        self,
        bearer_token: str,
        transaction_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Get transaction detail by ID.

        Args:
            bearer_token: Bearer token for authentication
            transaction_id: Transaction ID to retrieve
            options: Additional query parameters

        Returns:
            Any: Transaction detail response
        """
        headers = build_headers(bearer_token=bearer_token)
        query_params = options if options else {}

        response = await self.call_api(
            method="GET",
            url_path=f"/v2/transaction/{transaction_id}",
            query_params=query_params,
            body=None,
            headers=headers,
        )
        return response

    async def add_quick_menu_access(
        self,
        bearer_token: str,
        body: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Add quick menu access for a bot.

        Args:
            bearer_token: Bearer token for authentication
            body: Quick menu access payload with fields:
                - channel_id: Channel ID
                - clan_id: Clan ID
                - menu_type: Menu type (default 1)
                - action_msg: Action message
                - background: Background image URL
                - menu_name: Menu name
                - id: Menu ID
                - bot_id: Bot ID
            options: Additional options for the request

        Returns:
            Any: Quick menu access response
        """
        headers = build_headers(bearer_token=bearer_token)
        body_json = build_body(body=body)

        response = await self.call_api(
            method="POST",
            url_path=self.ENDPOINTS["add_quick_menu_access"],
            query_params={},
            body=body_json,
            headers=headers,
        )
        return response

    async def delete_quick_menu_access(
        self,
        bearer_token: str,
        bot_id: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Delete quick menu access for a bot.

        Args:
            bearer_token: Bearer token for authentication
            bot_id: Bot ID to delete quick menu for
            options: Additional options for the request

        Returns:
            Any: Delete response
        """
        headers = build_headers(bearer_token=bearer_token)

        response = await self.call_api(
            method="DELETE",
            url_path=self.ENDPOINTS["delete_quick_menu_access"],
            query_params={"bot_id": bot_id},
            body=None,
            headers=headers,
        )
        return response

    async def play_media(
        self,
        bearer_token: str,
        body: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Play media in a voice channel.

        Args:
            bearer_token: Bearer token for authentication
            body: Media playback payload with fields:
                - room_name: Voice room name
                - participant_identity: Participant identity
                - participant_name: Participant name
                - url: URL of media to play
                - name: Media name
            options: Additional options for the request

        Returns:
            Any: Media playback response
        """
        headers = build_headers(bearer_token=bearer_token)
        body_json = build_body(body=body)

        response = await self.call_api(
            method="POST",
            url_path="https://stn.mezon.ai/api/playmedia",
            query_params={},
            body=body_json,
            headers=headers,
        )
        return response
