from typing import Any, Optional, Dict
import base64
import json
from urllib.parse import urlparse
from pydantic import BaseModel


def build_headers(
    bearer_token: Optional[str] = None, basic_auth: Optional[tuple] = None
) -> Dict[str, Any]:
    """
    Build headers for API requests.

    Args:
        bearer_token (Optional[str]): Bearer token for authentication
        basic_auth (Optional[tuple]): Tuple of (username, password) for basic auth

    Returns:
        Dict[str, Any]: Headers dictionary
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    elif basic_auth:
        username, password = basic_auth
        credentials = base64.b64encode(f"{username}:{password}".encode())
        headers["Authorization"] = f"Basic {credentials}"
    return headers


def build_body(body: BaseModel) -> str:
    """
    Build body for API requests.

    Args:
        body (BaseModel): Body model

    Returns:
        str: Body string
    """
    return json.dumps(body.model_dump(mode="json", exclude_none=True))


def parse_url_components(url: str) -> Dict[str, Any]:
    """
    Parse URL components.

    Args:
        url (str): URL string to parse

    Returns:
        Dict[str, Any]: Dictionary with scheme, hostname, use_ssl, and port
    """
    parsed_url = urlparse(url)

    port = parsed_url.port
    use_ssl = parsed_url.scheme == "https"
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


def build_params(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build parameters for API requests, filtering out None values.

    Args:
        params (Optional[Dict[str, Any]]): Parameters dictionary

    Returns:
        Dict[str, Any]: Parameters dictionary with None values filtered out
    """
    if not params:
        return {}
    return {k: v for k, v in params.items() if v is not None}
