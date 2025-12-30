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

import json
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from mezon.protobuf.api import api_pb2
from mezon.protobuf.rtapi import realtime_pb2
from google.protobuf import json_format

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
    id_token: Optional[str] = None


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
    clan_name: Optional[str] = None
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

    @classmethod
    def from_protobuf(
        cls,
        message: realtime_pb2.ChannelCreatedEvent | realtime_pb2.ChannelUpdatedEvent,
    ) -> "ApiChannelDescription":
        channel_type_value = None
        if message.HasField("channel_type"):
            channel_type_value = message.channel_type.value

        json_data = json_format.MessageToJson(message, preserving_proto_field_name=True)
        data_dict = json.loads(json_data)

        if channel_type_value is not None:
            data_dict["type"] = channel_type_value

        return cls.model_validate(data_dict)


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


class ApiPermission(BaseModel):
    """Permission"""

    id: Optional[str] = None
    active: Optional[int] = None
    description: Optional[str] = None
    level: Optional[int] = None
    scope: Optional[int] = None
    slug: Optional[str] = None
    title: Optional[str] = None


class ApiPermissionList(BaseModel):
    """Permission list"""

    max_level_permission: Optional[int] = None
    permissions: Optional[List[ApiPermission]] = None


class RoleUserListRoleUser(BaseModel):
    """Role user in role user list"""

    id: Optional[str] = None
    avatar_url: Optional[str] = None
    display_name: Optional[str] = None
    lang_tag: Optional[str] = None
    location: Optional[str] = None
    online: Optional[bool] = None
    username: Optional[str] = None


class ApiRoleUserList(BaseModel):
    """Role user list"""

    cursor: Optional[str] = None
    role_users: Optional[List[RoleUserListRoleUser]] = None


class ApiRole(BaseModel):
    """Role"""

    id: Optional[str] = None
    title: Optional[str] = None
    color: Optional[str] = None
    role_icon: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    creator_id: Optional[str] = None
    clan_id: Optional[str] = None
    active: Optional[int] = None
    display_online: Optional[int] = None
    allow_mention: Optional[int] = None
    max_level_permission: Optional[int] = None
    order_role: Optional[int] = None
    channel_ids: Optional[List[str]] = None
    permission_list: Optional[ApiPermissionList] = None
    role_user_list: Optional[ApiRoleUserList] = None
    role_channel_active: Optional[int] = None


class ApiRoleList(BaseModel):
    """Role list"""

    cacheable_cursor: Optional[str] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    roles: Optional[List[ApiRole]] = None


class ApiRoleListEventResponse(BaseModel):
    """Role list event response"""

    clan_id: Optional[str] = None
    cursor: Optional[str] = None
    limit: Optional[str] = None
    roles: Optional[ApiRoleList] = None
    state: Optional[str] = None


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


class ApiSentTokenRequest(BaseModel):
    """Request to send tokens to another user"""

    receiver_id: str
    amount: int
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    note: Optional[str] = None
    extra_attribute: Optional[str] = None
    mmn_extra_info: Optional[Dict[str, Any]] = None
    timestamp: Optional[int] = None


# Client Models


class ClanDesc(BaseModel):
    """Clan description"""

    banner: Optional[str] = None
    clan_id: Optional[str] = None
    clan_name: Optional[str] = None
    creator_id: Optional[str] = None
    logo: Optional[str] = None
    status: Optional[int] = None


class StartEndIndex(BaseModel):
    """
    Start and end indexes for inline content metadata.
    """

    start: Optional[int] = Field(default=None, alias="s")
    end: Optional[int] = Field(default=None, alias="e")

    class Config:
        populate_by_name = True


class HashtagOnMessage(StartEndIndex):
    """
    Hashtag metadata embedded in a message.
    """

    channel_id: Optional[str] = Field(default=None, alias="channelid")

    class Config:
        populate_by_name = True


class EmojiOnMessage(StartEndIndex):
    """
    Emoji metadata embedded in a message.
    """

    emoji_id: Optional[str] = Field(default=None, alias="emojiid")

    class Config:
        populate_by_name = True


class LinkOnMessage(StartEndIndex):
    """
    Link metadata embedded in a message.
    """

    pass


class EMarkdownType(str, Enum):
    """
    Markdown segment types supported by channel messages.
    """

    TRIPLE = "t"
    SINGLE = "s"
    PRE = "pre"
    CODE = "c"
    BOLD = "b"
    LINK = "lk"
    VOICE_LINK = "vk"
    LINK_YOUTUBE = "lk_yt"


class MarkdownOnMessage(StartEndIndex):
    """
    Markdown metadata embedded in a message.
    """

    type: Optional[EMarkdownType] = None


class LinkVoiceRoomOnMessage(StartEndIndex):
    """
    Voice room link metadata embedded in a message.
    """

    pass


class InputFieldOption(BaseModel):
    """
    Input field configuration options.
    """

    defaultValue: Optional[str | int] = None
    type: Optional[str] = None
    textarea: Optional[bool] = None
    disabled: Optional[bool] = None


class SelectFieldOption(BaseModel):
    """
    Select field option.
    """

    label: str
    value: str


class RadioFieldOption(BaseModel):
    """
    Radio field option.
    """

    label: str
    value: str
    name: Optional[str] = None  # Apply when use multiple choice
    description: Optional[str] = None
    style: Optional[int] = None  # ButtonMessageStyle enum value
    disabled: Optional[bool] = None


class AnimationConfig(BaseModel):
    """
    Animation configuration for interactive messages.
    """

    url_image: str
    url_position: str
    pool: List[str]
    repeat: Optional[int] = None
    duration: Optional[int] = None


class InteractiveMessageField(BaseModel):
    """
    Field for interactive/embedded message sections.
    """

    name: str
    value: str
    inline: Optional[bool] = None
    options: Optional[List[Any]] = None
    inputs: Optional[Dict[str, Any]] = None
    max_options: Optional[int] = Field(default=None, alias="max_options")


class InteractiveMessageAuthor(BaseModel):
    """
    Author metadata for interactive messages.
    """

    name: str
    icon_url: Optional[str] = None
    url: Optional[str] = None


class InteractiveMessageMedia(BaseModel):
    """
    Media resource attached to an interactive message.
    """

    url: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None


class InteractiveMessageFooter(BaseModel):
    """
    Footer metadata for interactive messages.
    """

    text: Optional[str] = None
    icon_url: Optional[str] = None


class InteractiveMessageProps(BaseModel):
    """
    Embed-style payload attached to a message.
    """

    color: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    author: Optional[InteractiveMessageAuthor] = None
    description: Optional[str] = None
    thumbnail: Optional[InteractiveMessageMedia] = None
    fields: Optional[List[InteractiveMessageField]] = None
    image: Optional[InteractiveMessageMedia] = None
    timestamp: Optional[str] = None
    footer: Optional[InteractiveMessageFooter] = None


class ButtonMessageStyle(int, Enum):
    """
    Button message style types.
    """

    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class MessageComponentType(int, Enum):
    """
    Supported interactive component types.
    """

    BUTTON = 1
    SELECT = 2
    INPUT = 3
    DATEPICKER = 4
    RADIO = 5
    ANIMATION = 6
    GRID = 7


class MessageSelectType(int, Enum):
    """
    Message select types.
    """

    TEXT = 1
    USER = 2
    ROLE = 3
    CHANNEL = 4


class ButtonMessage(BaseModel):
    """
    Button message configuration.
    """

    label: str
    disable: Optional[bool] = None
    style: Optional[int] = None  # ButtonMessageStyle enum value
    url: Optional[str] = None


class MessageComponent(BaseModel):
    """
    Generic interactive component descriptor.

    Supports both enum-based and raw integer ``type`` values so we can
    match the exact payload shape expected by the backend.
    """

    type: Optional[MessageComponentType | int] = None
    component_id: str = Field(alias="id")
    component: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """
        Pydantic configuration for message components.

        Allows using ``component_id`` when constructing the model while
        still serializing the field name as ``id`` for the API payload.
        """

        populate_by_name = True


class MessageActionRow(BaseModel):
    """
    Group of interactive components displayed on a single row.
    """

    components: List[MessageComponent]


class ChannelMessageContent(BaseModel):
    """
    Structured payload describing a channel message body.
    """

    text: Optional[str] = Field(default=None, alias="t")
    content_thread: Optional[str] = Field(default=None, alias="contentThread")
    hashtags: Optional[List[HashtagOnMessage]] = Field(default=None, alias="hg")
    emojis: Optional[List[EmojiOnMessage]] = Field(default=None, alias="ej")
    links: Optional[List[LinkOnMessage]] = Field(default=None, alias="lk")
    markdown: Optional[List[MarkdownOnMessage]] = Field(default=None, alias="mk")
    voice_links: Optional[List[LinkVoiceRoomOnMessage]] = Field(
        default=None, alias="vk"
    )
    embed: Optional[List[InteractiveMessageProps]] = None
    components: Optional[List[MessageActionRow]] = None

    class Config:
        populate_by_name = True


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
    message_id: Optional[str] = None


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
    topic_id: Optional[str] = None


class SendTokenData(BaseModel):
    """Send token data"""

    amount: int
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
    channel_label: Optional[str] = None


class TokenSentEvent(BaseModel):
    """Token sent event"""

    receiver_id: str
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    amount: int
    note: Optional[str] = None
    extra_attribute: Optional[str] = None
    transaction_id: Optional[str] = None


class UserProfileUpdatedEvent(BaseModel):
    """User profile updated event"""

    user_id: str
    display_name: str
    avatar: str
    about_me: str
    channel_id: str
    clan_id: str


class VoiceJoinedEvent(BaseModel):
    """Voice joined event"""

    clan_id: str
    clan_name: str
    id: str
    participant: str
    user_id: str
    voice_channel_label: str
    voice_channel_id: str
    last_screenshot: Optional[str] = None


class VoiceLeavedEvent(BaseModel):
    """Voice leaved event"""

    id: str
    clan_id: str
    voice_channel_id: str
    voice_user_id: str


class VoiceStartedEvent(BaseModel):
    """Voice started event"""

    id: str
    clan_id: str
    voice_channel_id: str


class VoiceEndedEvent(BaseModel):
    """Voice ended event"""

    id: str
    clan_id: str
    voice_channel_id: str


class StreamingJoinedEvent(BaseModel):
    """Streaming joined event"""

    clan_id: str
    clan_name: str
    id: str
    participant: str
    user_id: str
    streaming_channel_label: str
    streaming_channel_id: str


class StreamingLeavedEvent(BaseModel):
    """Streaming leaved event"""

    id: str
    clan_id: str
    streaming_channel_id: str
    streaming_user_id: str


class CustomStatusEvent(BaseModel):
    """Custom status event"""

    clan_id: str
    user_id: str
    username: str
    status: str


class ChannelUpdatedEvent(BaseModel):
    """Channel updated event"""

    clan_id: str
    category_id: str
    creator_id: str
    parent_id: str
    channel_id: str
    channel_label: str
    channel_type: Optional[int] = None
    status: int
    meeting_code: str
    is_error: bool
    channel_private: bool
    app_url: str
    e2ee: int
    topic: str
    age_restricted: int
    active: int


class ChannelCreatedEvent(BaseModel):
    """Channel created event"""

    clan_id: str
    category_id: str
    creator_id: str
    parent_id: str
    channel_id: str
    channel_label: str
    channel_private: int
    channel_type: Optional[int] = None
    status: int
    app_url: str
    clan_name: str


class ChannelDeletedEvent(BaseModel):
    """Channel deleted event"""

    clan_id: str
    category_id: str
    parent_id: str
    channel_id: str
    deletor: str


class ClanUpdatedEvent(BaseModel):
    """Clan updated event"""

    clan_id: str
    clan_name: str
    clan_logo: str


class ClanProfileUpdatedEvent(BaseModel):
    """Clan profile updated event"""

    user_id: str
    clan_nick: str
    clan_avatar: str
    clan_id: str


class GiveCoffeeEvent(BaseModel):
    """Give coffee event"""

    sender_id: str
    receiver_id: str
    token_count: int
    message_ref_id: str
    channel_id: str
    clan_id: str


class ClanNameExistedEvent(BaseModel):
    """Clan name existed event"""

    clan_name: str
    exist: bool


class DropdownBoxSelected(BaseModel):
    """Dropdown box selected event"""

    message_id: str
    channel_id: str
    selectbox_id: str
    sender_id: str
    user_id: str
    values: List[str]


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
    mode: Optional[int] = None
    message_id: Optional[str] = None
    code: Optional[int] = 0
    username: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    persistence: Optional[bool] = None
    clan_id: Optional[str] = None
    channel_label: Optional[str] = None
    is_public: Optional[bool] = None


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


class ChannelMessageRaw(BaseModel):
    """Raw channel message data from protobuf"""

    id: str = Field(alias="message_id")
    clan_id: str
    channel_id: str
    sender_id: str
    content: Dict[str, Any] = Field(default_factory=dict)
    reactions: List[ApiMessageReaction] = Field(default_factory=list)
    mentions: List[ApiMessageMention] = Field(default_factory=list)
    attachments: List[ApiMessageAttachment] = Field(default_factory=list)
    references: List[ApiMessageRef] = Field(default_factory=list)
    create_time_seconds: Optional[int] = None
    topic_id: Optional[str] = None

    class Config:
        populate_by_name = True

    @classmethod
    def from_protobuf(cls, message: api_pb2.ChannelMessage) -> "ChannelMessageRaw":
        """
        Create a ChannelMessageRaw from a protobuf ChannelMessage.

        Args:
            message: Protobuf ChannelMessage object

        Returns:
            ChannelMessageRaw instance
        """

        def safe_json_parse(value: Optional[str], default):
            """Safely parse JSON string, return default on error or None"""
            if not value:
                return default
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return default

        return cls(
            message_id=message.message_id,
            clan_id=message.clan_id,
            channel_id=message.channel_id,
            sender_id=message.sender_id,
            content=safe_json_parse(getattr(message, "content", None), {}),
            reactions=safe_json_parse(getattr(message, "reactions", None), []),
            mentions=safe_json_parse(getattr(message, "mentions", None), []),
            attachments=safe_json_parse(getattr(message, "attachments", None), []),
            references=safe_json_parse(getattr(message, "references", None), []),
            create_time_seconds=getattr(message, "create_time_seconds", None),
            topic_id=getattr(message, "topic_id", None),
        )

    def to_message_dict(self) -> Dict[str, Any]:
        """
        Convert to Message initialization dictionary.

        Returns:
            Dictionary suitable for Message class initialization
        """
        return self.model_dump(by_alias=False)

    def to_db_dict(self) -> Dict[str, Any]:
        """
        Convert to database storage dictionary.

        Returns:
            Dictionary suitable for MessageDB.save_message()
        """
        return {
            "message_id": self.id,
            "clan_id": self.clan_id,
            "channel_id": self.channel_id,
            "sender_id": self.sender_id,
            "content": self.content,
            "reactions": [r.model_dump() for r in self.reactions],
            "mentions": [m.model_dump() for m in self.mentions],
            "attachments": [a.model_dump() for a in self.attachments],
            "references": [r.model_dump() for r in self.references],
            "create_time_seconds": self.create_time_seconds,
        }


class UserInitData(BaseModel):
    """User initialization data from protobuf message"""

    id: str = Field(alias="sender_id")
    username: str = Field(default="")
    clan_nick: str = Field(default="")
    clan_avatar: str = Field(default="")
    avatar: str = Field(default="")
    display_name: str = Field(default="")
    dm_channel_id: str = Field(default="", alias="dmChannelId")

    class Config:
        populate_by_name = True

    @classmethod
    def from_protobuf(
        cls, message: api_pb2.ChannelMessage, dm_channel_id: str = ""
    ) -> "UserInitData":
        """
        Create UserInitData from a protobuf ChannelMessage.

        Args:
            message: Protobuf ChannelMessage object
            dm_channel_id: DM channel ID for this user (optional)

        Returns:
            UserInitData instance
        """
        return cls(
            sender_id=message.sender_id,
            username=getattr(message, "username", ""),
            clan_nick=getattr(message, "clan_nick", ""),
            clan_avatar=getattr(message, "clan_avatar", ""),
            avatar=getattr(message, "avatar", ""),
            display_name=getattr(message, "display_name", ""),
            dm_channel_id=dm_channel_id,
        )

    def to_user_dict(self) -> Dict[str, Any]:
        """
        Convert to User class initialization dictionary.

        Returns:
            Dictionary suitable for User class initialization
        """
        return self.model_dump(by_alias=True)
