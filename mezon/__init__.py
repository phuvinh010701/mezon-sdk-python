"""
Mezon SDK Python

A Python implementation of the Mezon TypeScript SDK with 1:1 logic mapping.

Copyright 2020 The Mezon Authors
Licensed under the Apache License, Version 2.0
"""

from importlib.metadata import version

__version__ = version("mezon-sdk")

# Core imports
from .api import MezonApi

# Import client
from .client import MezonClient
from .constants import (
    ChannelStreamMode,
    ChannelType,
    Events,
    TypeMessage,
)

# Managers imports
from .managers import (
    CacheManager,
    ChannelManager,
    Collection,
    SessionManager,
    SocketManager,
)
from .models import (
    ApiChannelDescList,
    ApiChannelDescription,
    ApiClanDesc,
    ApiClanDescList,
    ApiMessageAttachment,
    ApiMessageMention,
    ApiMessageReaction,
    ApiMessageRef,
    # API Models
    ApiSession,
    ApiVoiceChannelUserList,
    Channel,
    ChannelMessageAck,
    # Client Models
    ChannelMessageContent,
    MessagePayLoad,
    # Socket Models
    Presence,
)
from .session import Session

# Socket imports
from .socket import Socket, WebSocketAdapter, WebSocketAdapterPb

# Structure imports
from .structures import (
    ButtonBuilder,
    Clan,
    InteractiveBuilder,
    Message,
    TextChannel,
    User,
)

# Utils imports
from .utils import disable_logging, enable_logging, get_logger, setup_logger

__all__ = [
    # Version
    "__version__",
    # Core
    "Session",
    "MezonApi",
    "MezonClient",
    # Models
    "ApiSession",
    "ApiClanDesc",
    "ApiClanDescList",
    "ApiChannelDescription",
    "ApiChannelDescList",
    "ApiMessageAttachment",
    "ApiMessageMention",
    "ApiMessageReaction",
    "ApiMessageRef",
    "ApiVoiceChannelUserList",
    "ChannelMessageContent",
    "MessagePayLoad",
    "ChannelMessageAck",
    "Presence",
    "Channel",
    # Constants
    "Events",
    "ChannelType",
    "ChannelStreamMode",
    "TypeMessage",
    # Socket
    "WebSocketAdapter",
    "WebSocketAdapterPb",
    "Socket",
    "ChannelManager",
    "SessionManager",
    "SocketManager",
    "CacheManager",
    "Collection",
    # Structures
    "Clan",
    "Message",
    "TextChannel",
    "User",
    "ButtonBuilder",
    "InteractiveBuilder",
    # Utils
    "setup_logger",
    "get_logger",
    "disable_logging",
    "enable_logging",
]
