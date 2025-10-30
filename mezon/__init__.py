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

# Import client
from .client import MezonClient

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
]
