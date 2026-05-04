from unittest.mock import AsyncMock, Mock, patch

import pytest

from mezon.api.mezon_api import MezonApi
from mezon.models import ApiAuthenticateRequest, ApiCreateChannelDescRequest
from mezon.protobuf.api import api_pb2


class TestMezonApi:
    def test_init_casts_client_id_and_timeout(self):
        api = MezonApi(
            client_id="123",
            api_key="key",
            base_url="https://api.example.com",
            timeout_ms=5000,
        )

        assert api.client_id == 123
        assert api.client_timeout.total == 5

    @pytest.mark.asyncio
    async def test_mezon_authenticate_builds_binary_request(self):
        api = MezonApi(
            client_id="123",
            api_key="key",
            base_url="https://api.example.com",
            timeout_ms=5000,
        )
        session_proto = api_pb2.Session(
            token="token",
            refresh_token="refresh",
            api_url="https://api.example.com",
            id_token="id",
            ws_url="wss://ws.example.com",
        )
        api.call_api = AsyncMock(return_value=session_proto)

        body = ApiAuthenticateRequest.model_validate(
            {
                "account": {
                    "appid": "123",
                    "appname": "bot",
                    "token": "secret",
                    "vars": {},
                }
            }
        )
        session = await api.mezon_authenticate("123", "secret", body)

        assert session.token == "token"
        call = api.call_api.await_args
        assert call.kwargs["method"] == "POST"
        assert call.kwargs["accept_binary"] is True
        assert call.kwargs["response_proto_class"] is api_pb2.Session
        assert call.kwargs["headers"]["Accept"] == "application/x-protobuf"
        assert call.kwargs["headers"]["Content-Type"] == "application/proto"

    @pytest.mark.asyncio
    async def test_create_channel_desc_normalizes_optional_fields(self):
        api = MezonApi(
            client_id="123",
            api_key="key",
            base_url="https://api.example.com",
            timeout_ms=5000,
        )
        response_proto = api_pb2.ChannelDescription(
            channel_id=42, clan_id=7, channel_label="general"
        )
        api.call_api = AsyncMock(return_value=response_proto)

        request = ApiCreateChannelDescRequest.model_validate(
            {"clan_id": 7, "channel_label": "general", "user_ids": [10, 11]}
        )
        response = await api.create_channel_desc("token", request)

        assert response.channel_id == 42
        call = api.call_api.await_args
        proto_request = api_pb2.CreateChannelDescRequest()
        proto_request.ParseFromString(call.kwargs["body"])
        assert proto_request.clan_id == 7
        assert proto_request.channel_id == 0
        assert proto_request.channel_label == "general"
        assert list(proto_request.user_ids) == [10, 11]

    @pytest.mark.asyncio
    async def test_get_channel_detail_accepts_json_fallback(self):
        api = MezonApi(
            client_id="123",
            api_key="key",
            base_url="https://api.example.com",
            timeout_ms=5000,
        )
        api.call_api = AsyncMock(
            return_value={"channel_id": 42, "clan_id": 7, "channel_label": "general"}
        )

        response = await api.get_channel_detail("token", 42)

        assert response.channel_id == 42
        assert response.clan_id == 7
        assert response.channel_label == "general"

    @pytest.mark.asyncio
    async def test_list_clans_descs_builds_binary_request(self):
        api = MezonApi(
            client_id="123",
            api_key="key",
            base_url="https://api.example.com",
            timeout_ms=5000,
        )
        api.call_api = AsyncMock(return_value=api_pb2.ClanDescList())

        await api.list_clans_descs("token", limit=5, state=2, cursor="next")

        call = api.call_api.await_args
        request = api_pb2.ListClanDescRequest()
        request.ParseFromString(call.kwargs["body"])
        assert call.kwargs["url_path"] == api.RPC_ENDPOINTS["list_clans_descs"]
        assert request.limit == 5
        assert request.state == 2
        assert request.cursor == "next"

    @pytest.mark.asyncio
    async def test_list_channel_descs_builds_binary_request(self):
        api = MezonApi(
            client_id="123",
            api_key="key",
            base_url="https://api.example.com",
            timeout_ms=5000,
        )
        api.call_api = AsyncMock(return_value=api_pb2.ChannelDescList())

        await api.list_channel_descs(
            "token",
            channel_type=3,
            clan_id=9,
            limit=4,
            state=1,
            cursor="cursor",
            is_mobile=True,
        )

        call = api.call_api.await_args
        request = api_pb2.ListChannelDescsRequest()
        request.ParseFromString(call.kwargs["body"])
        assert call.kwargs["url_path"] == api.RPC_ENDPOINTS["list_channel_descs"]
        assert request.channel_type == 3
        assert request.clan_id == 9
        assert request.limit == 4
        assert request.state == 1
        assert request.cursor == "cursor"
        assert request.is_mobile is True

    @pytest.mark.asyncio
    async def test_role_and_voice_rpc_helpers_build_expected_payloads(self):
        api = MezonApi(
            client_id="123",
            api_key="key",
            base_url="https://api.example.com",
            timeout_ms=5000,
        )
        api.call_api = AsyncMock(
            side_effect=[
                api_pb2.VoiceChannelUserList(),
                {"ok": True},
                api_pb2.RoleListEventResponse(),
            ]
        )

        await api.list_channel_voice_users(
            "token",
            clan_id=1,
            channel_id=2,
            channel_type=3,
            limit=4,
            state=5,
            cursor="v",
        )
        with (
            patch(
                "mezon.api.mezon_api.api_pb2.UpdateRoleRequest", return_value=Mock()
            ) as update_role_request,
            patch(
                "mezon.api.mezon_api.encode_protobuf", return_value=b"encoded-role"
            ) as encode_protobuf_mock,
        ):
            await api.update_role(
                "token",
                7,
                {
                    "title": "admin",
                    "color": "#fff",
                    "display_online": 1,
                    "allow_mention": 1,
                    "clan_id": 9,
                },
            )

        await api.list_roles("token", clan_id=3, limit=10, state=2, cursor="r")

        voice_request = api_pb2.ListChannelUsersRequest()
        voice_request.ParseFromString(api.call_api.await_args_list[0].kwargs["body"])
        assert voice_request.channel_id == 2
        assert voice_request.cursor == "v"

        update_role_request.assert_called_once_with(
            role_id=7,
            title="admin",
            color="#fff",
            role_icon="",
            description="",
            display_online=1,
            allow_mention=1,
            clan_id=9,
        )
        encode_protobuf_mock.assert_called_once()
        assert api.call_api.await_args_list[1].kwargs["body"] == b"encoded-role"

        role_list_request = api_pb2.RoleListEventRequest()
        role_list_request.ParseFromString(
            api.call_api.await_args_list[2].kwargs["body"]
        )
        assert role_list_request.clan_id == 3
        assert role_list_request.limit == 10
        assert role_list_request.state == 2
        assert role_list_request.cursor == "r"

    @pytest.mark.asyncio
    async def test_quick_menu_and_play_media_helpers_build_requests(self):
        api = MezonApi(
            client_id="123",
            api_key="key",
            base_url="https://api.example.com",
            timeout_ms=5000,
        )
        quick_menu = api_pb2.QuickMenuAccess(id=1, menu_name="Menu")
        api.call_api = AsyncMock(
            side_effect=[quick_menu, {"deleted": True}, {"items": []}, {"played": True}]
        )

        added = await api.add_quick_menu_access(
            "token", 2, 3, 4, "action", "bg", "Menu", 1, 5
        )
        deleted = await api.delete_quick_menu_access(
            "token",
            id=1,
            clan_id=3,
            bot_id=5,
            channel_id=2,
            menu_name="Menu",
            background="bg",
            action_msg="action",
        )
        listed = await api.list_quick_menu_access(
            "token", bot_id=5, channel_id=2, menu_type=4
        )
        played = await api.play_media(
            "token",
            {
                "room_name": "room",
                "participant_identity": "bot",
                "participant_name": "Bot",
                "url": "https://media.example.com/a.mp3",
                "name": "song",
            },
        )

        add_request = api_pb2.QuickMenuAccess()
        add_request.ParseFromString(api.call_api.await_args_list[0].kwargs["body"])
        assert added.id == 1
        assert add_request.channel_id == 2
        assert add_request.menu_type == 4

        delete_request = api_pb2.QuickMenuAccess()
        delete_request.ParseFromString(api.call_api.await_args_list[1].kwargs["body"])
        assert deleted == {"deleted": True}
        assert delete_request.id == 1
        assert delete_request.bot_id == 5

        list_request = api_pb2.ListQuickMenuAccessRequest()
        list_request.ParseFromString(api.call_api.await_args_list[2].kwargs["body"])
        assert listed == {"items": []}
        assert list_request.bot_id == 5
        assert list_request.channel_id == 2
        assert list_request.menu_type == 4

        assert played == {"played": True}
        assert (
            api.call_api.await_args_list[3].kwargs["url_path"]
            == "https://stn.mezon.ai/api/playmedia"
        )
        assert api.call_api.await_args_list[3].kwargs["body"] is not None
