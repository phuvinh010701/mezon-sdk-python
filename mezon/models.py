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

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# API Models


class ApiClanDesc(BaseModel):
    """Clan description"""

    banner: Optional[str] = None
    clan_id: Optional[str] = None
    clan_name: Optional[str] = None
    creator_id: Optional[str] = None
    logo: Optional[str] = None
    status: Optional[int] = None
    badge_count: Optional[int] = None
    is_onboarding: Optional[bool] = None
    welcome_channel_id: Optional[str] = None
    onboarding_banner: Optional[str] = None


class ApiClanDescList(BaseModel):
    """A list of clan descriptions"""

    clandesc: Optional[List[ApiClanDesc]] = None


class ApiSession(BaseModel):
    refresh_token: Optional[str] = None
    token: Optional[str] = None
    user_id: str
    api_url: Optional[str] = None


class ApiAuthenticateLogoutRequest(BaseModel):
    """Log out a session, invalidate a refresh token"""

    refresh_token: Optional[str] = None
    token: Optional[str] = None


class ApiAuthenticateRefreshRequest(BaseModel):
    """Authenticate against the server with a refresh token"""

    refresh_token: Optional[str] = None


class ApiAccountApp(BaseModel):
    """Send a app token to the server"""

    appid: Optional[str] = None
    appname: Optional[str] = None
    token: Optional[str] = None
    vars: Optional[Dict[str, str]] = None


class ApiAuthenticateRequest(BaseModel):
    account: Optional[ApiAccountApp] = None


class ApiUpdateMessageRequest(BaseModel):
    consume_time: Optional[str] = None
    id: Optional[str] = None
    read_time: Optional[str] = None


class ApiChannelMessageHeader(BaseModel):
    attachment: Optional[str] = None
    content: Optional[str] = None
    id: Optional[str] = None
    mention: Optional[str] = None
    reaction: Optional[str] = None
    referece: Optional[str] = None
    sender_id: Optional[str] = None
    timestamp_seconds: Optional[int] = None


class ApiChannelDescription(BaseModel):
    """Channel description model"""

    active: Optional[int] = None
    avatars: Optional[List[str]] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    channel_avatar: Optional[List[str]] = None
    channel_id: Optional[str] = None
    channel_label: Optional[str] = None
    channel_private: Optional[int] = None
    clan_id: Optional[str] = None
    count_mess_unread: Optional[int] = None
    create_time_seconds: Optional[int] = None
    creator_id: Optional[str] = None
    creator_name: Optional[str] = None
    display_names: Optional[List[str]] = None
    last_pin_message: Optional[str] = None
    last_seen_message: Optional[ApiChannelMessageHeader] = None
    last_sent_message: Optional[ApiChannelMessageHeader] = None
    meeting_code: Optional[str] = None
    meeting_uri: Optional[str] = None
    onlines: Optional[List[bool]] = None
    parent_id: Optional[str] = None
    status: Optional[int] = None
    type: Optional[int] = None
    update_time_seconds: Optional[int] = None
    user_id: Optional[List[str]] = None
    user_ids: Optional[List[str]] = None
    usernames: Optional[List[str]] = None


class ApiChannelDescList(BaseModel):
    """A list of channel descriptions"""

    channeldesc: Optional[List[ApiChannelDescription]] = None
    cursor: Optional[str] = None


class ApiMessageAttachment(BaseModel):
    """Message attachment"""

    filename: Optional[str] = None
    filetype: Optional[str] = None
    height: Optional[int] = None
    size: Optional[int] = None
    url: Optional[str] = None
    width: Optional[int] = None
    channel_id: Optional[str] = None
    mode: Optional[int] = None
    channel_label: Optional[str] = None
    message_id: Optional[str] = None
    sender_id: Optional[str] = None


class ApiMessageDeleted(BaseModel):
    """Deleted message"""

    deletor: Optional[str] = None
    message_id: Optional[str] = None


class ApiMessageMention(BaseModel):
    """Message mention"""

    create_time: Optional[str] = None
    id: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    role_id: Optional[str] = None
    rolename: Optional[str] = None
    s: Optional[int] = None  # start position
    e: Optional[int] = None  # end position
    channel_id: Optional[str] = None
    mode: Optional[int] = None
    channel_label: Optional[str] = None
    message_id: Optional[str] = None
    sender_id: Optional[str] = None


class ApiMessageReaction(BaseModel):
    """Message reaction"""

    action: Optional[bool] = None
    emoji_id: Optional[str] = None
    emoji: Optional[str] = None
    id: Optional[str] = None
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    count: Optional[int] = None
    channel_id: Optional[str] = None
    mode: Optional[int] = None
    channel_label: Optional[str] = None
    message_id: Optional[str] = None


class ApiMessageRef(BaseModel):
    """Message reference"""

    message_id: Optional[str] = None
    message_ref_id: str
    ref_type: Optional[int] = None
    message_sender_id: str
    message_sender_username: Optional[str] = None
    mesages_sender_avatar: Optional[str] = None
    message_sender_clan_nick: Optional[str] = None
    message_sender_display_name: Optional[str] = None
    content: Optional[str] = None
    has_attachment: Optional[bool] = None
    channel_id: Optional[str] = None
    mode: Optional[int] = None
    channel_label: Optional[str] = None


class ApiVoiceChannelUser(BaseModel):
    """Voice channel user"""

    id: Optional[str] = None
    channel_id: Optional[str] = None
    participant: Optional[str] = None
    user_id: Optional[str] = None


class ApiVoiceChannelUserList(BaseModel):
    """Voice channel user list"""

    voice_channel_users: Optional[List[ApiVoiceChannelUser]] = None


class ApiCreateChannelDescRequest(BaseModel):
    """Create channel description request"""

    category_id: Optional[str] = None
    channel_id: Optional[str] = None
    channel_label: Optional[str] = None
    channel_private: Optional[int] = None
    clan_id: Optional[str] = None
    parent_id: Optional[str] = None
    type: Optional[int] = None
    user_ids: Optional[List[str]] = None


class ApiRegisterStreamingChannelRequest(BaseModel):
    """Register streaming channel request"""

    clan_id: Optional[str] = None
    channel_id: Optional[str] = None


# Client Models


class ClanDesc(BaseModel):
    """Clan description"""

    banner: Optional[str] = None
    clan_id: Optional[str] = None
    clan_name: Optional[str] = None
    creator_id: Optional[str] = None
    logo: Optional[str] = None
    status: Optional[int] = None


class ChannelMessageContent(BaseModel):
    """Channel message content"""

    clan_id: str
    channel_id: str
    mode: int
    is_public: bool
    msg: Any
    mentions: Optional[List[ApiMessageMention]] = Field(default_factory=list)
    attachments: Optional[List[ApiMessageAttachment]] = Field(default_factory=list)
    ref: Optional[List[ApiMessageRef]] = Field(default_factory=list)


class MessagePayLoad(BaseModel):
    """Message payload"""

    clan_id: str
    channel_id: str
    mode: int
    is_public: bool
    msg: ChannelMessageContent
    mentions: Optional[List[ApiMessageMention]] = None
    attachments: Optional[List[ApiMessageAttachment]] = None
    ref: Optional[List[ApiMessageRef]] = None
    hideEditted: Optional[bool] = None
    topic_id: Optional[str] = None


class EphemeralMessageData(BaseModel):
    """Ephemeral message data"""

    receiver_id: str
    clan_id: str
    channel_id: str
    mode: int
    is_public: bool
    content: Any
    mentions: Optional[List[ApiMessageMention]] = None
    attachments: Optional[List[ApiMessageAttachment]] = None
    references: Optional[List[ApiMessageRef]] = None
    anonymous_message: Optional[bool] = None
    mention_everyone: Optional[bool] = None
    avatar: Optional[str] = None
    code: Optional[int] = None
    topic_id: Optional[str] = None


class ReplyMessageData(BaseModel):
    """Reply message data"""

    clan_id: str
    channel_id: str
    mode: int
    is_public: bool
    content: ChannelMessageContent
    mentions: Optional[List[ApiMessageMention]] = None
    attachments: Optional[List[ApiMessageAttachment]] = None
    references: Optional[List[ApiMessageRef]] = None
    anonymous_message: Optional[bool] = None
    mention_everyone: Optional[bool] = None
    avatar: Optional[str] = None
    code: Optional[int] = None
    topic_id: Optional[str] = None


class UpdateMessageData(BaseModel):
    """Update message data"""

    clan_id: str
    channel_id: str
    mode: int
    is_public: bool
    message_id: str
    content: Any
    mentions: Optional[List[ApiMessageMention]] = None
    attachments: Optional[List[ApiMessageAttachment]] = None
    hideEditted: Optional[bool] = None
    topic_id: Optional[str] = None
    is_update_msg_topic: Optional[bool] = None


class ReactMessagePayload(BaseModel):
    """React message payload"""

    id: Optional[str] = None
    emoji_id: str
    emoji: str
    count: int
    action_delete: Optional[bool] = None


class ReactMessageData(BaseModel):
    """React message data"""

    id: Optional[str] = None
    clan_id: str
    channel_id: str
    mode: int
    is_public: bool
    message_id: str
    emoji_id: str
    emoji: str
    count: int
    message_sender_id: str
    action_delete: Optional[bool] = None


class RemoveMessageData(BaseModel):
    """Remove message data"""

    clan_id: str
    channel_id: str
    mode: int
    is_public: bool
    message_id: str


class SendTokenData(BaseModel):
    """Send token data"""

    amount: float
    note: Optional[str] = None
    extra_attribute: Optional[str] = None


class MessageUserPayLoad(BaseModel):
    """Message user payload"""

    userId: str
    msg: str
    messOptions: Optional[Dict[str, Any]] = None
    attachments: Optional[List[ApiMessageAttachment]] = None
    refs: Optional[List[ApiMessageRef]] = None


# Socket Models


class SocketMessage(BaseModel):
    """Socket message"""

    cid: Optional[str] = None


class Presence(BaseModel):
    """An object which represents a connected user in the server"""

    user_id: str
    session_id: str
    username: str
    node: str
    status: str


class Channel(BaseModel):
    """A response from a channel join operation"""

    id: str
    chanel_label: str
    presences: List[Presence]
    self_presence: Presence = Field(alias="self")
    clan_logo: str
    category_name: str


class ClanJoin(SocketMessage):
    """Clan join"""

    clan_id: str


class ChannelJoin(BaseModel):
    """Join a realtime chat channel"""

    channel_join: Dict[str, Any]


class ChannelLeave(BaseModel):
    """Leave a realtime chat channel"""

    channel_leave: Dict[str, Any]


class FCMTokens(BaseModel):
    """FCM tokens"""

    device_id: str
    token_id: str
    platform: str


class UserProfileRedis(BaseModel):
    """User profile from Redis"""

    user_id: str
    username: str
    avatar: str
    display_name: str
    about_me: str
    custom_status: str
    create_time_second: int
    fcm_tokens: List[FCMTokens]
    online: bool
    metadata: str
    is_disabled: bool
    joined_clans: List[str]
    pubkey: str
    mezon_id: str
    app_token: str


class AddUsers(BaseModel):
    """Add users"""

    user_id: str
    avatar: str
    username: str
    display_name: str


class ChannelDescription(BaseModel):
    """Channel description for events"""

    pass  # Will be same as ApiChannelDescription


class UserChannelAddedEvent(BaseModel):
    """User channel added event"""

    channel_desc: ChannelDescription
    users: List[UserProfileRedis]
    status: str
    clan_id: str
    caller: Optional[UserProfileRedis] = None
    create_time_second: int
    active: int


class UserChannelRemoved(BaseModel):
    """User channel removed"""

    channel_id: str
    user_ids: List[str]
    channel_type: int
    clan_id: str


class UserClanRemovedEvent(BaseModel):
    """User clan removed event"""

    clan_id: str
    user_ids: List[str]


class LastPinMessageEvent(BaseModel):
    """Last pin message event"""

    channel_id: str
    mode: int
    channel_label: str
    message_id: str
    user_id: str
    operation: int
    is_public: bool


class LastSeenMessageEvent(BaseModel):
    """Last seen message event"""

    channel_id: str
    mode: int
    channel_label: str
    message_id: str
    timestamp_seconds: str


class MessageTypingEvent(BaseModel):
    """Message typing event"""

    channel_id: str
    mode: int
    is_public: bool
    clan_id: str
    sender_id: str


class TokenSentEvent(BaseModel):
    """Token sent event"""

    receiver_id: str
    sender_id: str
    amount: float
    token: str


class NotificationEvent(BaseModel):
    """Notification event"""

    pass  # Will be defined based on requirements


class ChannelMessageSend(BaseModel):
    """Channel message send"""

    channel_id: str
    mode: int
    is_public: bool
    clan_id: str
    content: Any
    mentions: Optional[List[ApiMessageMention]] = None
    attachments: Optional[List[ApiMessageAttachment]] = None
    references: Optional[List[ApiMessageRef]] = None


class ChannelMessageUpdate(BaseModel):
    """Channel message update"""

    channel_id: str
    mode: int
    is_public: bool
    clan_id: str
    message_id: str
    content: Any


class ChannelMessageRemove(BaseModel):
    """Channel message remove"""

    channel_id: str
    mode: int
    is_public: bool
    clan_id: str
    message_id: str


class ChannelMessageAck(BaseModel):
    """Channel message acknowledgement"""

    channel_id: str
    mode: int
    message_id: str
    code: int
    username: str
    create_time: str
    update_time: str
    persistence: bool
    clan_id: Optional[str] = None
    channel_label: Optional[str] = None


class SocketError(BaseModel):
    """Socket error"""

    code: int
    message: str


class Ping(BaseModel):
    """Ping message"""

    pass


class Rpc(BaseModel):
    """RPC call"""

    id: str
    payload: Any
