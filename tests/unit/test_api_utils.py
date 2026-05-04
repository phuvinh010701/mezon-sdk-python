from unittest.mock import AsyncMock

import aiohttp
import pytest
from google.protobuf.message import DecodeError

from mezon.api.utils import (
    build_body,
    build_headers,
    build_params,
    build_url,
    is_binary_response,
    is_schema_secure,
    parse_binary_response,
    parse_response,
    parse_url_components,
)
from mezon.models import ApiAuthenticateRequest
from mezon.protobuf.api import api_pb2


class TestApiUtils:
    def test_build_headers_supports_bearer_and_basic_auth(self):
        bearer_headers = build_headers(
            bearer_token="token", accept_binary=True, send_binary=True
        )
        basic_headers = build_headers(basic_auth=("user", "pass"))

        assert bearer_headers["Authorization"] == "Bearer token"
        assert bearer_headers["Accept"] == "application/proto"
        assert bearer_headers["Content-Type"] == "application/proto"
        assert basic_headers["Authorization"].startswith("Basic ")

    def test_build_url_body_params_and_security_helpers(self):
        body = build_body(
            ApiAuthenticateRequest.model_validate(
                {"account": {"appid": "1", "appname": "bot", "token": "secret"}}
            )
        )

        assert (
            build_url("https", "example.com", 443, "/v1", query={"a": 1})
            == "https://example.com:443/v1?a=1"
        )
        assert '"appid": "1"' in body
        assert build_params({"a": 1, "b": None}) == {"a": 1}
        assert is_schema_secure("https") is True
        assert is_schema_secure("ws") is False
        assert is_binary_response("application/x-protobuf") is True
        assert is_binary_response("application/json") is False

    def test_parse_url_components_sets_default_ports(self):
        https_result = parse_url_components("https://example.com")
        ws_result = parse_url_components("ws://example.com:8080")

        assert https_result == {
            "scheme": "https",
            "hostname": "example.com",
            "use_ssl": True,
            "port": "443",
        }
        assert ws_result["hostname"] == "example.com"
        assert ws_result["port"] == "8080"
        assert ws_result["use_ssl"] is False

    @pytest.mark.asyncio
    async def test_parse_binary_response_and_json_fallbacks(self):
        proto = api_pb2.Session(token="token")
        binary_resp = AsyncMock(spec=aiohttp.ClientResponse)
        binary_resp.read = AsyncMock(return_value=proto.SerializeToString())

        parsed = await parse_binary_response(binary_resp, api_pb2.Session)
        assert parsed.token == "token"

        json_resp = AsyncMock(spec=aiohttp.ClientResponse)
        json_resp.headers = {"Content-Type": "application/json"}
        json_resp.json = AsyncMock(return_value={"ok": True})
        fallback = await parse_response(json_resp, True, api_pb2.Session)
        assert fallback == {"ok": True}

    @pytest.mark.asyncio
    async def test_parse_response_parses_binary_and_wraps_decode_error(self):
        proto = api_pb2.Session(token="token")
        resp = AsyncMock(spec=aiohttp.ClientResponse)
        resp.headers = {"Content-Type": "application/x-protobuf"}
        resp.read = AsyncMock(return_value=proto.SerializeToString())

        parsed = await parse_response(resp, True, api_pb2.Session)
        assert parsed.token == "token"

        bad_resp = AsyncMock(spec=aiohttp.ClientResponse)
        bad_resp.read = AsyncMock(side_effect=DecodeError("bad protobuf"))
        with pytest.raises(ValueError, match="Invalid protobuf response"):
            await parse_binary_response(bad_resp, api_pb2.Session)
