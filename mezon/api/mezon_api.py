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

from typing import Any, Optional

import aiohttp
from aiolimiter import AsyncLimiter

from mezon.api.utils import (
    build_body,
    build_headers,
    parse_response,
)
from mezon.models import (
    ApiAuthenticateRequest,
    ApiChannelDescList,
    ApiChannelDescription,
    ApiClanDescList,
    ApiCreateChannelDescRequest,
    ApiQuickMenuAccess,
    ApiRoleListEventResponse,
    ApiSession,
    ApiVoiceChannelUserList,
)
from mezon.protobuf.api import api_pb2
from mezon.protobuf.utils import encode_protobuf
from mezon.utils.logger import get_logger

logger = get_logger(__name__)


class MezonApi:
    # REST endpoints (JSON-based)
    REST_ENDPOINTS = {
        "authenticate": "/v2/apps/authenticate/token",
    }

    # Protobuf RPC endpoints (binary protobuf request/response)
    RPC_ENDPOINTS = {
        "list_clans_descs": "/mezon.api.Mezon/ListClanDescs",
        "list_channel_descs": "/mezon.api.Mezon/ListChannelDescs",
        "create_channel_desc": "/mezon.api.Mezon/CreateChannelDesc",
        "get_channel_detail": "/mezon.api.Mezon/ListChannelDetail",
        "list_channel_voice_users": "/mezon.api.Mezon/ListChannelVoiceUsers",
        "update_role": "/mezon.api.Mezon/UpdateRole",
        "list_roles": "/mezon.api.Mezon/ListRoles",
        "add_quick_menu_access": "/mezon.api.Mezon/AddQuickMenuAccess",
        "delete_quick_menu_access": "/mezon.api.Mezon/DeleteQuickMenuAccess",
        "list_quick_menu_access": "/mezon.api.Mezon/ListQuickMenuAccess",
    }

    # Keep ENDPOINTS for backward compatibility during migration
    ENDPOINTS = {**REST_ENDPOINTS, **RPC_ENDPOINTS}

    _rate_limiter = AsyncLimiter(max_rate=1, time_period=1.25)

    def __init__(
        self, client_id: str | int, api_key: str, base_url: str, timeout_ms: int
    ):
        """
        Initialize Mezon API client.

        Args:
            client_id: Bot ID for authentication
            api_key: API key for authentication
            base_url: Base URL for API
            timeout_ms: Timeout in milliseconds
        """
        self.client_id = int(client_id)
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_ms = timeout_ms
        self.client_timeout = aiohttp.ClientTimeout(total=timeout_ms / 1000)

    async def call_api(
        self,
        method: str,
        url_path: str,
        query_params: Optional[dict[str, Any]] = None,
        body: Optional[str | bytes] = None,
        headers: Optional[dict[str, Any]] = None,
        accept_binary: bool = False,
        response_proto_class: Optional[type] = None,
    ) -> Any:
        """
        Make API call with optional binary protobuf request/response support.

        Args:
            method (str): HTTP method
            url_path (str): API endpoint path
            query_params (Optional[dict[str, Any]]): URL query parameters
            body (Optional[str | bytes]): Request body (JSON string or protobuf bytes)
            headers (Optional[dict[str, Any]]): HTTP headers
            accept_binary (bool): If True, request binary protobuf response
            response_proto_class (Optional[type]): Protobuf message class for binary responses

        Returns:
            Any: Dict (from JSON) or protobuf message (from binary)
        """
        logger.debug(
            f"Method: {method}, URL: {url_path}, Binary: {accept_binary}, "
            f"Proto class: {response_proto_class}"
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
                    return await parse_response(
                        resp, accept_binary, response_proto_class
                    )

    async def mezon_authenticate(
        self,
        basic_auth_username: str | int,
        basic_auth_password: str,
        body: ApiAuthenticateRequest,
        options: Optional[dict[str, Any]] = None,
    ) -> ApiSession:
        """
        Authenticate a app with a token against the server.

        Args:
            basic_auth_username (str): Username for basic authentication
            basic_auth_password (str): Password for basic authentication
            body (ApiAuthenticateRequest): Authentication request body
            options (Optional[dict[str, Any]]): Additional options for the request

        Returns:
            ApiSession: Session object containing authentication details
        """

        headers = build_headers(
            basic_auth=(basic_auth_username, basic_auth_password),
            send_binary=True,
            additional_headers={"Accept": "application/x-protobuf"},
        )
        body = build_body(body=body)

        response = await self.call_api(
            method="POST",
            url_path=self.ENDPOINTS["authenticate"],
            query_params={},
            body=body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.Session,
        )
        return ApiSession.from_protobuf(response)

    async def list_clans_descs(
        self,
        token: str,
        limit: int = 0,
        state: int = 0,
        cursor: str = "",
        options: Optional[dict[str, Any]] = None,
    ) -> ApiClanDescList:
        """
        List clan descriptions.

        Args:
            token: Bearer token for authentication
            limit: Maximum number of results
            state: Filter state
            cursor: Pagination cursor
            options: Additional options for the request

        Returns:
            ApiClanDescList: Clan descriptions
        """
        request = api_pb2.ListClanDescRequest(
            limit=limit,
            state=state,
            cursor=cursor,
        )

        headers = build_headers(
            bearer_token=token, accept_binary=True, send_binary=True
        )
        body = encode_protobuf(request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["list_clans_descs"],
            query_params=None,
            body=body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.ClanDescList,
        )

        return ApiClanDescList.from_protobuf(response)

    async def list_channel_descs(
        self,
        token: str,
        channel_type: int = 0,
        clan_id: int = 0,
        limit: int = 0,
        state: int = 0,
        cursor: str = "",
        is_mobile: bool = False,
        options: Optional[dict[str, Any]] = None,
    ) -> ApiChannelDescList:
        """
        List channel descriptions.

        Args:
            token: Bearer token for authentication
            channel_type: Channel type to filter
            clan_id: Clan ID to filter channels
            limit: Maximum number of results
            state: Channel state filter
            cursor: Pagination cursor
            is_mobile: Whether request is from mobile client
            options: Additional options for the request

        Returns:
            ApiChannelDescList: List of channel descriptions with optional cursor
        """
        request = api_pb2.ListChannelDescsRequest(
            clan_id=clan_id,
            channel_type=channel_type,
            limit=limit,
            state=state,
            cursor=cursor,
            is_mobile=is_mobile,
        )

        headers = build_headers(
            bearer_token=token, accept_binary=True, send_binary=True
        )
        body = encode_protobuf(request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["list_channel_descs"],
            query_params=None,
            body=body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.ChannelDescList,
        )

        return ApiChannelDescList.from_protobuf(response)

    async def create_channel_desc(
        self,
        token: str,
        request: ApiCreateChannelDescRequest,
        options: Optional[dict[str, Any]] = None,
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
        proto_request = api_pb2.CreateChannelDescRequest(
            clan_id=request.clan_id if request.clan_id else 0,
            channel_id=request.channel_id if request.channel_id else 0,
            channel_label=request.channel_label if request.channel_label else "",
            channel_private=request.channel_private if request.channel_private else 0,
            parent_id=request.parent_id if request.parent_id else 0,
            category_id=request.category_id if request.category_id else 0,
            type=request.type if request.type else 0,
            user_ids=request.user_ids if request.user_ids else [],
        )

        headers = build_headers(
            bearer_token=token, accept_binary=True, send_binary=True
        )
        body = encode_protobuf(proto_request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["create_channel_desc"],
            query_params=None,
            body=body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.ChannelDescription,
        )

        return ApiChannelDescription.from_protobuf(response)

    async def get_channel_detail(
        self,
        token: str,
        channel_id: int,
        options: Optional[dict[str, Any]] = None,
    ) -> ApiChannelDescription:
        """
        Get channel detail by ID.

        Args:
            token: Bearer token for authentication
            channel_id: Channel ID to retrieve
            options: Additional options for the request

        Returns:
            ApiChannelDescription: Channel description details
        """
        request = api_pb2.ListChannelDetailRequest(channel_id=channel_id)

        headers = build_headers(
            bearer_token=token, accept_binary=True, send_binary=True
        )
        body = encode_protobuf(request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["get_channel_detail"],
            query_params=None,
            body=body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.ChannelDescription,
        )

        if isinstance(response, api_pb2.ChannelDescription):
            return ApiChannelDescription.from_protobuf(response)
        else:
            return ApiChannelDescription.model_validate(response)

    async def list_channel_voice_users(
        self,
        token: str,
        clan_id: Optional[int] = 0,
        channel_id: Optional[int] = 0,
        channel_type: Optional[int] = 0,
        limit: Optional[int] = 0,
        state: Optional[int] = 0,
        cursor: Optional[str] = "",
        options: Optional[dict[str, Any]] = None,
    ) -> ApiVoiceChannelUserList:
        """
        List voice channel users.

        Args:
            token: Bearer token for authentication
            clan_id: Clan ID to filter
            channel_id: Channel ID
            channel_type: Channel type
            limit: Maximum number of results
            state: State filter
            cursor: Pagination cursor
            options: Additional options for the request

        Returns:
            ApiVoiceChannelUserList: List of voice channel users
        """
        request = api_pb2.ListChannelUsersRequest(
            clan_id=clan_id,
            channel_id=channel_id,
            channel_type=channel_type,
            limit=limit,
            state=state,
            cursor=cursor,
        )

        headers = build_headers(
            bearer_token=token, accept_binary=True, send_binary=True
        )
        body = encode_protobuf(request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["list_channel_voice_users"],
            query_params=None,
            body=body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.VoiceChannelUserList,
        )

        return ApiVoiceChannelUserList.from_protobuf(response)

    async def update_role(
        self,
        token: str,
        role_id: int,
        request: dict[str, Any],
        options: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Update a role.

        Args:
            token: Bearer token for authentication
            role_id: Role ID to update
            request: Role update request data
            options: Additional options for the request

        Returns:
            Any: Update response
        """
        proto_request = api_pb2.UpdateRoleRequest(
            role_id=role_id if role_id else 0,
            title=request.get("title", ""),
            color=request.get("color", ""),
            role_icon=request.get("role_icon", ""),
            description=request.get("description", ""),
            display_online=request.get("display_online", 0),
            allow_mention=request.get("allow_mention", 0),
            clan_id=request.get("clan_id", 0) if request.get("clan_id") else 0,
        )

        headers = build_headers(
            bearer_token=token, accept_binary=True, send_binary=True
        )
        body = encode_protobuf(proto_request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["update_role"],
            query_params=None,
            body=body,
            headers=headers,
            accept_binary=True,
        )
        return response

    async def list_roles(
        self,
        token: str,
        clan_id: Optional[int] = None,
        limit: Optional[int] = None,
        state: Optional[int] = None,
        cursor: Optional[str] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> ApiRoleListEventResponse:
        """
        List roles in a clan.

        Args:
            token: Bearer token for authentication
            clan_id: Clan ID to list roles for
            limit: Maximum number of results
            state: State filter
            cursor: Pagination cursor
            options: Additional options for the request

        Returns:
            ApiRoleListEventResponse: Role list response
        """
        request = api_pb2.RoleListEventRequest(
            clan_id=clan_id if clan_id is not None else 0,
            limit=limit if limit is not None else 0,
            state=state if state is not None else 0,
            cursor=cursor if cursor is not None else "",
        )

        headers = build_headers(
            bearer_token=token, accept_binary=True, send_binary=True
        )
        body = encode_protobuf(request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["list_roles"],
            query_params=None,
            body=body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.RoleListEventResponse,
        )

        return ApiRoleListEventResponse.from_protobuf(response)

    async def add_quick_menu_access(
        self,
        bearer_token: str,
        channel_id: int,
        clan_id: int,
        menu_type: int,
        action_msg: str,
        background: str,
        menu_name: str,
        menu_id: int,
        bot_id: int,
        options: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Add quick menu access for a bot.

        Args:
            bearer_token: Bearer token for authentication
            channel_id: Channel ID
            clan_id: Clan ID
            menu_type: Menu type
            action_msg: Action message
            background: Background image URL
            menu_name: Menu name
            menu_id: Menu ID
            bot_id: Bot ID
            options: Additional options for the request

        Returns:
            Any: Quick menu access response
        """
        request = api_pb2.QuickMenuAccess(
            id=menu_id,
            bot_id=bot_id,
            clan_id=clan_id,
            channel_id=channel_id,
            menu_name=menu_name,
            background=background,
            action_msg=action_msg,
            menu_type=menu_type,
        )

        headers = build_headers(
            bearer_token=bearer_token, accept_binary=True, send_binary=True
        )
        proto_body = encode_protobuf(request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["add_quick_menu_access"],
            query_params=None,
            body=proto_body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.QuickMenuAccess,
        )
        return ApiQuickMenuAccess.from_protobuf(response)

    async def delete_quick_menu_access(
        self,
        bearer_token: str,
        id: Optional[int] = None,
        clan_id: Optional[int] = None,
        bot_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        menu_name: Optional[str] = None,
        background: Optional[str] = None,
        action_msg: Optional[str] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Delete quick menu access for a bot.

        Args:
            bearer_token: Bearer token for authentication
            id: Menu ID
            clan_id: Clan ID
            bot_id: Bot ID
            menu_name: Menu name
            background: Background image URL
            action_msg: Action message
            options: Additional options for the request

        Returns:
            Any: Delete response
        """
        request = api_pb2.QuickMenuAccess(
            id=id if id is not None else 0,
            bot_id=bot_id if bot_id is not None else 0,
            clan_id=clan_id if clan_id is not None else 0,
            channel_id=channel_id if channel_id is not None else 0,
            menu_name=menu_name if menu_name is not None else "",
            background=background if background is not None else "",
            action_msg=action_msg if action_msg is not None else "",
        )

        headers = build_headers(
            bearer_token=bearer_token, accept_binary=True, send_binary=True
        )
        body = encode_protobuf(request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["delete_quick_menu_access"],
            query_params=None,
            body=body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.QuickMenuAccess,
        )
        return response

    async def list_quick_menu_access(
        self,
        bearer_token: str,
        bot_id: Optional[int] = 0,
        channel_id: Optional[int] = 0,
        menu_type: Optional[int] = 0,
        options: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        List quick menu access items.

        Args:
            bearer_token: Bearer token for authentication
            bot_id: Bot ID to filter
            channel_id: Channel ID to filter
            menu_type: Menu type to filter
            options: Additional options for the request

        Returns:
            Any: List of quick menu access items
        """
        request = api_pb2.ListQuickMenuAccessRequest(
            bot_id=bot_id,
            channel_id=channel_id,
            menu_type=menu_type,
        )

        headers = build_headers(
            bearer_token=bearer_token, accept_binary=True, send_binary=True
        )
        body = encode_protobuf(request)

        response = await self.call_api(
            method="POST",
            url_path=self.RPC_ENDPOINTS["list_quick_menu_access"],
            query_params=None,
            body=body,
            headers=headers,
            accept_binary=True,
            response_proto_class=api_pb2.QuickMenuAccessList,
        )
        return response

    async def play_media(
        self,
        bearer_token: str,
        body: dict[str, Any],
        options: Optional[dict[str, Any]] = None,
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
