"""
Mezon SDK Python

A Python implementation of the Mezon TypeScript SDK with 1:1 logic mapping.

Copyright 2020 The Mezon Authors
Licensed under the Apache License, Version 2.0
"""

__version__ = "0.1.0"

# Core imports
from .session import Session
from .models import (
    # API Models
    ApiSession,
    ApiClanDesc,
    ApiClanDescList,
    ApiChannelDescription,
    ApiChannelDescList,
    ApiMessageAttachment,
    ApiMessageMention,
    ApiMessageReaction,
    ApiMessageRef,
    ApiVoiceChannelUserList,
    # Client Models
    ChannelMessageContent,
    MessagePayLoad,
    ChannelMessageAck,
    # Socket Models
    Presence,
    Channel,
)
from .constants import (
    Events,
    ChannelType,
    ChannelStreamMode,
    TypeMessage,
)
from .api import MezonApi

# Managers imports
from .managers import (
    ChannelManager,
    SessionManager,
    SocketManager,
    CacheManager,
    Collection,
)

# Import client
from .client import MezonClient

# Socket imports
from .socket import WebSocketAdapter, WebSocketAdapterPb, Socket

# Structure imports
from .structures import (
    Clan,
    Message,
    TextChannel,
    User,
    ButtonBuilder,
    InteractiveBuilder,
)

# Utils imports
from .utils import setup_logger, get_logger, disable_logging, enable_logging


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
