import base64
import json
from typing import Any, Optional
from urllib.parse import urlencode, urlparse, urlunparse

import aiohttp
from google.protobuf.message import DecodeError
from pydantic import BaseModel

from mezon.protobuf.utils import parse_api_protobuf
from mezon.utils.logger import get_logger

logger = get_logger(__name__)

BINARY_CONTENT_TYPES = (
    "application/proto",
    "application/x-protobuf",
    "application/protobuf",
    "application/octet-stream",
    "text/plain; charset=utf-8",
)


def build_headers(
    bearer_token: Optional[str] = None,
    basic_auth: Optional[tuple[str | int, str]] = None,
    accept_binary: bool = False,
    send_binary: bool = False,
    additional_headers: dict[str, Any] = {},
) -> dict[str, Any]:
    """
    Build headers for API requests.

    Args:
        bearer_token (Optional[str]): Bearer token for authentication
        basic_auth (Optional[tuple]): Tuple of (username, password) for basic auth
        accept_binary (bool): Whether to accept binary protobuf responses. Defaults to False.
        send_binary (bool): Whether to send binary protobuf request body. Defaults to False.

    Returns:
        dict[str, Any]: Headers dictionary
    """
    headers = {
        "Accept": "application/proto" if accept_binary else "application/json",
        "Content-Type": "application/proto" if send_binary else "application/json",
    }
    if additional_headers:
        headers.update(additional_headers)
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    elif basic_auth:
        username, password = basic_auth
        credentials = base64.b64encode(f"{username}:{password}".encode())
        headers["Authorization"] = f"Basic {credentials}"
    return headers


def build_url(
    scheme: str,
    host: str,
    port: str | int = "",
    path: str = "",
    params: str = "",
    query: dict[str, Any] = {},
    fragment: str = "",
) -> str:
    """
    Build URL for API requests.

    Args:
        scheme (str): Scheme string
        host (str): Host string
        port (str | int): Port string or integer
        path (str): Path string
        params (str): Params string
        query (dict[str, Any]): Query dictionary
        fragment (str): Fragment string

    Returns:
        str: URL string
    """
    netloc = f"{host}" if port else f"{host}:{port}"
    return urlunparse((scheme, netloc, path, params, urlencode(query), fragment))


def build_body(body: BaseModel | dict[str, Any]) -> str:
    """
    Build JSON body for API requests.

    Args:
        body (BaseModel): Body model

    Returns:
        str: Body string
    """
    if isinstance(body, BaseModel):
        return json.dumps(body.model_dump(mode="json", exclude_none=True))
    elif isinstance(body, dict):
        return json.dumps(body)
    else:
        raise ValueError(f"Invalid body type: {type(body)}")


def parse_url_components(url: str, use_ssl: bool = False) -> dict[str, Any]:
    """
    Parse URL components.

    Args:
        url (str): URL string to parse
        use_ssl (bool): Whether to use SSL
    Returns:
        dict[str, Any]: Dictionary with scheme, hostname, use_ssl, and port
    """
    parsed_url = urlparse(url)

    port = parsed_url.port
    use_ssl = use_ssl or is_schema_secure(parsed_url.scheme)
    if port is None:
        port = "443" if use_ssl else "80"
    else:
        port = str(port)

    return {
        "scheme": parsed_url.scheme,
        "hostname": parsed_url.hostname,
        "use_ssl": use_ssl,
        "port": port,
    }


def is_schema_secure(schema: str) -> bool:
    """
    Check if schema is secure.

    Args:
        schema (str): Schema string

    Returns:
        bool: True if schema is secure
    """
    return schema == "https" or schema == "wss"


def build_params(params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    Build parameters for API requests, filtering out None values.

    Args:
        params (Optional[dict[str, Any]]): Parameters dictionary

    Returns:
        dict[str, Any]: Parameters dictionary with None values filtered out
    """
    if not params:
        return {}
    return {k: v for k, v in params.items() if v is not None}


def is_binary_response(content_type: str) -> bool:
    """
    Check if content type indicates a binary protobuf response.

    Args:
        content_type (str): Content-Type header value

    Returns:
        bool: True if response is binary protobuf
    """
    return any(binary_type in content_type for binary_type in BINARY_CONTENT_TYPES)


async def parse_binary_response(
    resp: aiohttp.ClientResponse,
    response_proto_class: type,
) -> Any:
    """
    Parse binary protobuf response.

    Args:
        resp (aiohttp.ClientResponse): HTTP response object
        response_proto_class (Type): Protobuf message class

    Returns:
        Any: Parsed protobuf message

    Raises:
        ValueError: If protobuf decoding fails
    """
    try:
        binary_data = await resp.read()
        return parse_api_protobuf(binary_data, response_proto_class)
    except DecodeError as e:
        logger.error(f"Failed to decode binary protobuf: {e}")
        raise ValueError(f"Invalid protobuf response: {e}") from e


async def parse_response(
    resp: aiohttp.ClientResponse,
    accept_binary: bool,
    response_proto_class: Optional[type],
) -> Any:
    """
    Parse API response based on content type.

    Args:
        resp (aiohttp.ClientResponse): HTTP response object
        accept_binary (bool): Whether binary response was requested
        response_proto_class (Optional[type]): Protobuf class for binary parsing

    Returns:
        Any: Parsed response (dict from JSON or protobuf message)
    """
    # TODO: some api that returns binary response doesn't have Content-Type header
    content_type = resp.headers.get("Content-Type", "text/plain; charset=utf-8")

    if is_binary_response(content_type):
        if not response_proto_class:
            logger.warning(
                "Binary response received but no response_proto_class provided. "
                "Falling back to JSON parsing."
            )
            return await resp.json()
        return await parse_binary_response(resp, response_proto_class)

    if accept_binary and response_proto_class:
        logger.warning(
            f"Requested binary response but got {content_type}. "
            f"Falling back to JSON parsing."
        )
    return await resp.json()
