import asyncio
import re
import time
from typing import Dict, TypeVar, Any
from urllib.parse import urlparse

from ..constants import ChannelType, ChannelStreamMode, InternalEventsSocket


_sequence = 0
_last_timestamp = 0

T = TypeVar("T")


def convert_internal_event_to_events(input: InternalEventsSocket) -> str:
    """
    Convert internal event to event string.

    Args:
        input: Internal event socket enum

    Returns:
        Converted event string
    """
    return input.value.replace("_event", "").replace("_", "")


def convert_channeltype_to_channel_mode(channel_type: int) -> int:
    """
    Convert channel type to channel mode.

    Args:
        channel_type: Channel type value

    Returns:
        Channel stream mode value
    """
    if channel_type == ChannelType.CHANNEL_TYPE_DM:
        return ChannelStreamMode.STREAM_MODE_DM
    elif channel_type == ChannelType.CHANNEL_TYPE_GROUP:
        return ChannelStreamMode.STREAM_MODE_GROUP
    elif channel_type == ChannelType.CHANNEL_TYPE_CHANNEL:
        return ChannelStreamMode.STREAM_MODE_CHANNEL
    elif channel_type == ChannelType.CHANNEL_TYPE_THREAD:
        return ChannelStreamMode.STREAM_MODE_THREAD

    return 0


def is_valid_user_id(user_id: Any) -> bool:
    """
    Check if user ID is valid (numeric string or number).

    Args:
        user_id: User ID to validate

    Returns:
        True if valid, False otherwise
    """
    if isinstance(user_id, (str, int)):
        str_id = str(user_id)
        return bool(re.match(r"^\d+$", str_id))
    return False


async def sleep(ms: int) -> None:
    """
    Async sleep for specified milliseconds.

    Args:
        ms: Milliseconds to sleep
    """
    await asyncio.sleep(ms / 1000)


def parse_url_to_host_and_ssl(url_str: str) -> Dict[str, Any]:
    """
    Parse URL to extract host, port, and SSL information.

    Args:
        url_str: URL string to parse

    Returns:
        Dictionary with host, port, and useSSL keys
    """
    parsed = urlparse(url_str)
    port = parsed.port

    if port is None:
        port = "443" if parsed.scheme == "https" else "80"
    else:
        port = str(port)

    return {
        "host": parsed.hostname,
        "port": port,
        "useSSL": parsed.scheme == "https",
    }


def generate_snowflake_id() -> str:
    """
    Generate a Snowflake ID for unique identification.

    Returns:
        Snowflake ID as string
    """
    global _sequence, _last_timestamp

    epoch = 1577836800000  # Custom epoch
    timestamp = int(time.time() * 1000)

    if timestamp == _last_timestamp:
        _sequence += 1
    else:
        _sequence = 0
        _last_timestamp = timestamp

    worker_id = 1
    datacenter_id = 1

    snowflake_id = (
        ((timestamp - epoch) << 22)
        | (datacenter_id << 17)
        | (worker_id << 12)
        | _sequence
    )

    return str(snowflake_id)
