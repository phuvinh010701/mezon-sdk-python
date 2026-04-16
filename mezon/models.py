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
import logging
from enum import Enum
from typing import Any, Literal, Optional

from google.protobuf import json_format
from pydantic import BaseModel, Field

from mezon.protobuf.api import api_pb2

logger = logging.getLogger(__name__)


def protobuf_to_pydantic(proto_message, pydantic_class: type[BaseModel]) -> BaseModel:
    """Convert protobuf message to Pydantic model via JSON.

    Args:
        proto_message: Protobuf message instance
        pydantic_class: Target Pydantic model class

    Returns:
        Pydantic model instance
    """
    json_data = json_format.MessageToJson(
        proto_message, preserving_proto_field_name=True
    )
    return pydantic_class.model_validate_json(json_data)


# API Models


class MezonBaseModel(BaseModel):
    """Base model with protobuf conversion support.

    Subclasses automatically get a `from_protobuf` classmethod that converts
    a protobuf message to the Pydantic model via JSON serialization.

    Usage:
        class MyModel(MezonBaseModel):
            name: Optional[str] = None

        model = MyModel.from_protobuf(proto_message)
    """

    @classmethod
    def from_protobuf(cls, message: Any) -> "MezonBaseModel":
        """Convert protobuf message to Pydantic model.

        Args:
            message: Protobuf message instance

        Returns:
            Pydantic model instance
        """
        return protobuf_to_pydantic(message, cls)


class ApiClanDesc(MezonBaseModel):
    """Clan description"""

    banner: Optional[str] = None
    clan_id: Optional[int] = None
    clan_name: Optional[str] = None
    creator_id: Optional[int] = None
    logo: Optional[str] = None
    status: Optional[int] = None
    badge_count: Optional[int] = None
    is_onboarding: Optional[bool] = None
    welcome_channel_id: Optional[int] = None
    onboarding_banner: Optional[str] = None


class ApiClanDescList(MezonBaseModel):
    """A list of clan descriptions"""

    clandesc: list[ApiClanDesc] = []


class ApiSession(MezonBaseModel):
    refresh_token: Optional[str] = None
    token: Optional[str] = None
    user_id: Optional[int] = None
    api_url: Optional[str] = None
    id_token: Optional[str] = None
    ws_url: Optional[str] = None


class ApiAccountApp(BaseModel):
    """Send a app token to the server"""

    appid: Optional[str] = None
    appname: Optional[str] = None
    token: Optional[str] = None
    vars: Optional[dict[str, str]] = None


class ApiAuthenticateRequest(BaseModel):
    account: Optional[ApiAccountApp] = None


class ApiChannelMessageHeader(BaseModel):
    attachment: Optional[str] = None
    content: Optional[str] = None
    id: Optional[int] = None
    mention: Optional[str] = None
    reaction: Optional[str] = None
    referece: Optional[str] = None
    sender_id: Optional[int] = None
    timestamp_seconds: Optional[int] = None


class ApiChannelDescription(BaseModel):
    """Channel description model"""

    active: Optional[int] = None
    avatars: Optional[list[str]] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    channel_avatar: Optional[list[str]] = None
    channel_id: Optional[int] = None
    channel_label: Optional[str] = None
    channel_private: Optional[int] = None
    clan_id: Optional[int] = None
    clan_name: Optional[str] = None
    count_mess_unread: Optional[int] = None
    create_time_seconds: Optional[int] = None
    creator_id: Optional[int] = None
    creator_name: Optional[str] = None
    display_names: Optional[list[str]] = None
    last_pin_message: Optional[str] = None
    last_seen_message: Optional[ApiChannelMessageHeader] = None
    last_sent_message: Optional[ApiChannelMessageHeader] = None
    meeting_code: Optional[str] = None
    meeting_uri: Optional[str] = None
    onlines: Optional[list[bool]] = None
    parent_id: Optional[int] = None
    status: Optional[int] = None
    type: Optional[int] = None
    update_time_seconds: Optional[int] = None
    user_id: Optional[list[int]] = None
    user_ids: Optional[list[int]] = None
    usernames: Optional[list[str]] = None

    @classmethod
    def from_protobuf(
        cls, message: api_pb2.ChannelDescription
    ) -> "ApiChannelDescription":
        """Convert API protobuf ChannelDescription to Pydantic model."""
        json_data = json_format.MessageToJson(message, preserving_proto_field_name=True)
        data_dict = json.loads(json_data)

        if message.type is not None:
            data_dict["type"] = message.type

        return cls.model_validate(data_dict)


class ApiChannelDescList(MezonBaseModel):
    """A list of channel descriptions"""

    channeldesc: Optional[list[ApiChannelDescription]] = None
    cursor: Optional[str] = None


class ApiMessageAttachment(BaseModel):
    """Message attachment"""

    filename: Optional[str] = None
    filetype: Optional[str] = None
    height: Optional[int] = None
    size: Optional[int] = None
    url: Optional[str] = None
    width: Optional[int] = None
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    channel_id: Optional[int] = None
    mode: Optional[int] = None
    channel_label: Optional[str] = None
    message_id: Optional[int] = None
    sender_id: Optional[int] = None


class ApiMessageDeleted(BaseModel):
    """Deleted message"""

    deletor: Optional[str] = None
    message_id: Optional[int] = None


class ApiMessageMention(BaseModel):
    """Message mention"""

    create_time: Optional[str] = None
    id: Optional[int] = None
    user_id: Optional[int] = None
    username: Optional[str] = None
    role_id: Optional[int] = None
    rolename: Optional[str] = None
    s: Optional[int] = None  # start position
    e: Optional[int] = None  # end position
    channel_id: Optional[int] = None
    mode: Optional[int] = None
    channel_label: Optional[str] = None
    message_id: Optional[int] = None
    sender_id: Optional[int] = None


class ApiMessageReaction(BaseModel):
    """Message reaction"""

    action: Optional[bool] = None
    emoji_id: Optional[int] = None
    emoji: Optional[str] = None
    id: Optional[int] = None
    sender_id: Optional[int] = None
    sender_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    count: Optional[int] = None
    channel_id: Optional[int] = None
    mode: Optional[int] = None
    channel_label: Optional[str] = None
    message_id: Optional[int] = None


class ApiMessageRef(BaseModel):
    """Message reference"""

    message_id: Optional[int] = None
    message_ref_id: int
    ref_type: Optional[int] = None
    message_sender_id: int
    message_sender_username: Optional[str] = None
    message_sender_avatar: Optional[str] = None
    message_sender_clan_nick: Optional[str] = None
    message_sender_display_name: Optional[str] = None
    content: Optional[str] = None
    has_attachment: Optional[bool] = None
    channel_id: Optional[int] = None
    mode: Optional[int] = None
    channel_label: Optional[str] = None


class ApiVoiceChannelUser(MezonBaseModel):
    """Voice channel user"""

    id: Optional[int] = None
    channel_id: Optional[int] = None
    participant: Optional[str] = None
    user_id: Optional[int] = None


class ApiVoiceChannelUserList(MezonBaseModel):
    """Voice channel user list"""

    voice_channel_users: Optional[list[ApiVoiceChannelUser]] = None


class ApiPermission(BaseModel):
    """Permission"""

    id: Optional[int] = None
    active: Optional[int] = None
    description: Optional[str] = None
    level: Optional[int] = None
    scope: Optional[int] = None
    slug: Optional[str] = None
    title: Optional[str] = None


class ApiPermissionList(BaseModel):
    """Permission list"""

    max_level_permission: Optional[int] = None
    permissions: Optional[list[ApiPermission]] = None


class RoleUserListRoleUser(BaseModel):
    """Role user in role user list"""

    id: Optional[int] = None
    avatar_url: Optional[str] = None
    display_name: Optional[str] = None
    lang_tag: Optional[str] = None
    location: Optional[str] = None
    online: Optional[bool] = None
    username: Optional[str] = None


class ApiRoleUserList(BaseModel):
    """Role user list"""

    cursor: Optional[str] = None
    role_users: Optional[list[RoleUserListRoleUser]] = None


class ApiRole(MezonBaseModel):
    """Role"""

    id: Optional[int] = None
    title: Optional[str] = None
    color: Optional[str] = None
    role_icon: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    creator_id: Optional[int] = None
    clan_id: Optional[int] = None
    active: Optional[int] = None
    display_online: Optional[int] = None
    allow_mention: Optional[int] = None
    max_level_permission: Optional[int] = None
    order_role: Optional[int] = None
    channel_ids: Optional[list[int]] = None
    permission_list: Optional[ApiPermissionList] = None
    role_user_list: Optional[ApiRoleUserList] = None
    role_channel_active: Optional[int] = None


class ApiRoleList(MezonBaseModel):
    """Role list"""

    cacheable_cursor: Optional[str] = None
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    roles: Optional[list[ApiRole]] = None


class ApiRoleListEventResponse(MezonBaseModel):
    """Role list event response"""

    clan_id: Optional[int] = None
    cursor: Optional[str] = None
    limit: Optional[str] = None
    roles: Optional[ApiRoleList] = None
    state: Optional[str] = None


class ApiQuickMenuAccess(MezonBaseModel):
    """Quick menu access item"""

    id: Optional[int] = None
    bot_id: Optional[int] = None
    clan_id: Optional[int] = None
    channel_id: Optional[int] = None
    menu_name: Optional[str] = None
    background: Optional[str] = None
    action_msg: Optional[str] = None
    menu_type: Optional[int] = None


class ApiQuickMenuAccessList(BaseModel):
    """Quick menu access list"""

    list_menus: Optional[list[ApiQuickMenuAccess]] = None

    @classmethod
    def from_protobuf(
        cls, message: api_pb2.QuickMenuAccessList
    ) -> "ApiQuickMenuAccessList":
        """Convert protobuf QuickMenuAccessList to Pydantic model."""
        menus = []
        for menu in message.list_menus:
            menus.append(ApiQuickMenuAccess.from_protobuf(menu))
        return cls(list_menus=menus if menus else None)


class ApiCreateChannelDescRequest(BaseModel):
    """Create channel description request"""

    category_id: Optional[int] = None
    channel_id: Optional[int] = None
    channel_label: Optional[str] = None
    channel_private: Optional[int] = None
    clan_id: Optional[int] = None
    parent_id: Optional[int] = None
    type: Optional[int] = None
    user_ids: Optional[list[int]] = None


class ApiSentTokenRequest(BaseModel):
    """Request to send tokens to another user"""

    receiver_id: int
    amount: int
    sender_id: Optional[int] = None
    sender_name: Optional[str] = None
    note: Optional[str] = None
    extra_attribute: Optional[str] = None
    mmn_extra_info: Optional[dict[str, Any]] = None
    timestamp: Optional[int] = None


# Client Models


class ClanDesc(BaseModel):
    """Clan description"""

    banner: Optional[str] = None
    clan_id: Optional[int] = None
    clan_name: Optional[str] = None
    creator_id: Optional[int] = None
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

    channel_id: Optional[int] = Field(default=None, alias="channelid")

    class Config:
        populate_by_name = True


class EmojiOnMessage(StartEndIndex):
    """
    Emoji metadata embedded in a message.
    """

    emoji_id: Optional[int] = Field(default=None, alias="emojiid")

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
    pool: list[str]
    repeat: Optional[int] = None
    duration: Optional[int] = None


class InteractiveMessageField(BaseModel):
    """
    Field for interactive/embedded message sections.
    """

    name: str
    value: str
    inline: Optional[bool] = None
    options: Optional[list[Any]] = None
    inputs: Optional[dict[str, Any]] = None
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
    fields: Optional[list[InteractiveMessageField]] = None
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
    component: dict[str, Any] = Field(default_factory=dict)

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

    components: list[MessageComponent]


class ChannelMessageContent(BaseModel):
    """
    Structured payload describing a channel message body.
    """

    text: Optional[str] = Field(default=None, alias="t")
    content_thread: Optional[str] = Field(default=None, alias="contentThread")
    hashtags: Optional[list[HashtagOnMessage]] = Field(default=None, alias="hg")
    emojis: Optional[list[EmojiOnMessage]] = Field(default=None, alias="ej")
    links: Optional[list[LinkOnMessage]] = Field(default=None, alias="lk")
    markdown: Optional[list[MarkdownOnMessage]] = Field(default=None, alias="mk")
    voice_links: Optional[list[LinkVoiceRoomOnMessage]] = Field(
        default=None, alias="vk"
    )
    embed: Optional[list[InteractiveMessageProps]] = None
    components: Optional[list[MessageActionRow]] = None

    class Config:
        populate_by_name = True


class MessagePayLoad(BaseModel):
    """Message payload"""

    clan_id: int
    channel_id: int
    mode: int
    is_public: bool
    msg: ChannelMessageContent
    mentions: Optional[list[ApiMessageMention]] = None
    attachments: Optional[list[ApiMessageAttachment]] = None
    ref: Optional[list[ApiMessageRef]] = None
    hideEditted: Optional[bool] = None
    topic_id: Optional[int] = None


class EphemeralMessageData(BaseModel):
    """Ephemeral message data"""

    receiver_id: int
    clan_id: int
    channel_id: int
    mode: int
    is_public: bool
    content: Any
    mentions: Optional[list[ApiMessageMention]] = None
    attachments: Optional[list[ApiMessageAttachment]] = None
    references: Optional[list[ApiMessageRef]] = None
    anonymous_message: Optional[bool] = None
    mention_everyone: Optional[bool] = None
    avatar: Optional[str] = None
    code: Optional[int] = None
    topic_id: Optional[int] = None
    message_id: Optional[int] = None


class ReplyMessageData(BaseModel):
    """Reply message data"""

    clan_id: int
    channel_id: int
    mode: int
    is_public: bool
    content: ChannelMessageContent
    mentions: Optional[list[ApiMessageMention]] = None
    attachments: Optional[list[ApiMessageAttachment]] = None
    references: Optional[list[ApiMessageRef]] = None
    anonymous_message: Optional[bool] = None
    mention_everyone: Optional[bool] = None
    avatar: Optional[str] = None
    code: Optional[int] = None
    topic_id: Optional[int] = None


class UpdateMessageData(BaseModel):
    """Update message data"""

    clan_id: int
    channel_id: int
    mode: int
    is_public: bool
    message_id: int
    content: Any
    mentions: Optional[list[ApiMessageMention]] = None
    attachments: Optional[list[ApiMessageAttachment]] = None
    hideEditted: Optional[bool] = None
    topic_id: Optional[int] = None
    is_update_msg_topic: Optional[bool] = None


class ReactMessagePayload(BaseModel):
    """React message payload"""

    id: Optional[int] = None
    emoji_id: int
    emoji: str
    count: int
    action_delete: Optional[bool] = None


class ReactMessageData(BaseModel):
    """React message data"""

    id: Optional[int] = None
    clan_id: int
    channel_id: int
    mode: int
    is_public: bool
    message_id: int
    emoji_id: int
    emoji: str
    count: int
    message_sender_id: int
    action_delete: Optional[bool] = None


class RemoveMessageData(BaseModel):
    """Remove message data"""

    clan_id: int
    channel_id: int
    mode: int
    is_public: bool
    message_id: int
    topic_id: Optional[int] = None


class SendTokenData(BaseModel):
    """Send token data"""

    amount: int
    note: Optional[str] = None
    extra_attribute: Optional[str] = None


class MessageUserPayLoad(BaseModel):
    """Message user payload"""

    userId: int
    msg: str
    messOptions: Optional[dict[str, Any]] = None
    attachments: Optional[list[ApiMessageAttachment]] = None
    refs: Optional[list[ApiMessageRef]] = None


# Socket Models


class SocketMessage(BaseModel):
    """Socket message"""

    cid: Optional[str] = None


class Presence(BaseModel):
    """An object which represents a connected user in the server"""

    user_id: int
    session_id: str
    username: str
    node: str
    status: str


class Channel(BaseModel):
    """A response from a channel join operation"""

    id: int
    chanel_label: str
    presences: list[Presence]
    self_presence: Presence = Field(alias="self")
    clan_logo: str
    category_name: str


class ClanJoin(SocketMessage):
    """Clan join"""

    clan_id: int


class ChannelJoin(BaseModel):
    """Join a realtime chat channel"""

    channel_join: dict[str, Any]


class ChannelLeave(BaseModel):
    """Leave a realtime chat channel"""

    channel_leave: dict[str, Any]


class FCMTokens(BaseModel):
    """FCM tokens"""

    device_id: str
    token_id: str
    platform: str


class UserProfileRedis(BaseModel):
    """User profile from Redis"""

    user_id: int
    username: Optional[str] = None
    avatar: Optional[str] = None
    display_name: Optional[str] = None
    user_status: Optional[str] = None
    status: Optional[str] = None
    online: Optional[bool] = None
    fcm_tokens: list[FCMTokens] = Field(default_factory=list)
    joined_clans: list[int] = Field(default_factory=list)
    app_token: Optional[str] = None
    create_time_second: Optional[int] = None
    app_url: Optional[str] = None
    is_bot: Optional[bool] = None
    voip_token: Optional[str] = None


class AddUsers(BaseModel):
    """Add users"""

    user_id: int
    avatar: str
    username: str
    display_name: str


class UserChannelAddedEvent(BaseModel):
    """User channel added event"""

    clan_id: int
    channel_desc: Optional[ApiChannelDescription] = None
    users: list[UserProfileRedis] = Field(default_factory=list)
    status: Optional[str] = None
    caller: Optional[UserProfileRedis] = None
    create_time_seconds: Optional[int] = None
    active: Optional[int] = None


class UserChannelRemoved(BaseModel):
    """User channel removed"""

    channel_id: int
    user_ids: list[int]
    channel_type: int
    clan_id: int


class UserClanRemovedEvent(BaseModel):
    """User clan removed event"""

    clan_id: int
    user_ids: list[int]


class LastPinMessageEvent(BaseModel):
    """Last pin message event"""

    channel_id: int
    mode: int
    channel_label: str
    message_id: int
    user_id: int
    operation: int
    is_public: bool


class LastSeenMessageEvent(BaseModel):
    """Last seen message event"""

    channel_id: int
    mode: int
    channel_label: str
    message_id: int
    timestamp_seconds: str


class MessageTypingEvent(BaseModel):
    """Message typing event"""

    channel_id: int
    sender_id: int
    sender_username: Optional[str] = None
    sender_display_name: Optional[str] = None
    mode: Optional[int] = None
    is_public: Optional[bool] = None
    clan_id: Optional[int] = None
    channel_label: Optional[str] = None


class TokenSentEvent(BaseModel):
    """Token sent event"""

    receiver_id: int
    sender_id: Optional[int] = None
    sender_name: Optional[str] = None
    amount: int
    note: Optional[str] = None
    extra_attribute: Optional[str] = None
    transaction_id: Optional[str] = None


class UserProfileUpdatedEvent(BaseModel):
    """User profile updated event"""

    user_id: int
    display_name: str
    avatar: str
    about_me: str
    channel_id: int
    clan_id: int


class VoiceJoinedEvent(BaseModel):
    """Voice joined event"""

    clan_id: int
    user_id: int
    voice_channel_id: int
    clan_name: Optional[str] = None
    id: Optional[str] = None
    participant: Optional[str] = None
    voice_channel_label: Optional[str] = None
    last_screenshot: Optional[str] = None


class VoiceLeavedEvent(BaseModel):
    """Voice leaved event"""

    clan_id: int
    voice_channel_id: int
    voice_user_id: int
    id: Optional[str] = None


class VoiceStartedEvent(BaseModel):
    """Voice started event"""

    id: str
    clan_id: int
    voice_channel_id: int


class VoiceEndedEvent(BaseModel):
    """Voice ended event"""

    id: int
    clan_id: int
    voice_channel_id: str


class StreamingJoinedEvent(BaseModel):
    """Streaming joined event"""

    clan_id: int
    clan_name: str
    id: int
    participant: str
    user_id: int
    streaming_channel_label: str
    streaming_channel_id: int


class StreamingLeavedEvent(BaseModel):
    """Streaming leaved event"""

    id: int
    clan_id: int
    streaming_channel_id: str
    streaming_user_id: str


class CustomStatusEvent(BaseModel):
    """Custom status event"""

    clan_id: int
    user_id: int
    username: str
    status: str


class ChannelUpdatedEvent(BaseModel):
    """Channel updated event"""

    clan_id: int
    channel_id: int
    category_id: Optional[int] = None
    creator_id: Optional[int] = None
    parent_id: Optional[int] = None
    channel_label: Optional[str] = None
    channel_type: Optional[int] = None
    status: Optional[int] = None
    meeting_code: Optional[str] = None
    is_error: Optional[bool] = None
    channel_private: Optional[bool] = None
    app_id: Optional[int] = None
    e2ee: Optional[int] = None
    topic: Optional[str] = None
    age_restricted: Optional[int] = None
    active: Optional[int] = None
    count_mess_unread: Optional[int] = None
    user_ids: list[int] = Field(default_factory=list)
    role_ids: list[int] = Field(default_factory=list)
    channel_avatar: Optional[str] = None


class ChannelCreatedEvent(BaseModel):
    """Channel created event"""

    clan_id: int
    channel_id: int
    category_id: Optional[int] = None
    creator_id: Optional[int] = None
    parent_id: Optional[int] = None
    channel_label: Optional[str] = None
    channel_private: Optional[int] = None
    channel_type: Optional[int] = None
    status: Optional[int] = None
    app_id: Optional[int] = None
    clan_name: Optional[str] = None
    channel_avatar: Optional[str] = None


class ChannelDeletedEvent(BaseModel):
    """Channel deleted event"""

    clan_id: int
    channel_id: int
    category_id: Optional[int] = None
    parent_id: Optional[int] = None
    deletor: Optional[str] = None


class ClanUpdatedEvent(BaseModel):
    """Clan updated event"""

    clan_id: int
    clan_name: str
    clan_logo: str


class ClanProfileUpdatedEvent(BaseModel):
    """Clan profile updated event"""

    user_id: int
    clan_nick: str
    clan_avatar: str
    clan_id: int


class GiveCoffeeEvent(BaseModel):
    """Give coffee event"""

    sender_id: int
    receiver_id: int
    token_count: int
    message_ref_id: int
    channel_id: int
    clan_id: int


class ClanNameExistedEvent(BaseModel):
    """Clan name existed event"""

    clan_name: str
    exist: bool


class DropdownBoxSelected(BaseModel):
    """Dropdown box selected event"""

    message_id: int
    channel_id: int
    selectbox_id: str
    sender_id: int
    user_id: int
    values: list[str]


class NotificationEvent(BaseModel):
    """Notification event"""

    pass  # Will be defined based on requirements


class ChannelMessageSend(BaseModel):
    """Channel message send"""

    channel_id: int
    mode: int
    is_public: bool
    clan_id: int
    content: Any
    mentions: Optional[list[ApiMessageMention]] = None
    attachments: Optional[list[ApiMessageAttachment]] = None
    references: Optional[list[ApiMessageRef]] = None


class ChannelMessageUpdate(BaseModel):
    """Channel message update"""

    channel_id: int
    mode: int
    is_public: bool
    clan_id: int
    message_id: int
    content: Any


class ChannelMessageRemove(BaseModel):
    """Channel message remove"""

    channel_id: int
    mode: int
    is_public: bool
    clan_id: int
    message_id: int


class ChannelMessageAck(BaseModel):
    """Channel message acknowledgement"""

    channel_id: Optional[int] = None
    mode: Optional[int] = None
    message_id: Optional[int] = None
    code: Optional[int] = 0
    username: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    persistence: Optional[bool] = None
    clan_id: Optional[int] = None
    channel_label: Optional[str] = None
    is_public: Optional[bool] = None


class SocketError(BaseModel):
    """Socket error"""

    code: int
    message: str


class Ping(BaseModel):
    """Ping message"""

    pass


class Pong(BaseModel):
    """Pong message"""

    pass


class Rpc(BaseModel):
    """RPC call"""

    id: str
    payload: Any


class ChannelMessage(BaseModel):
    """A message sent on a channel"""

    message_id: int
    clan_id: int
    channel_id: int
    sender_id: int

    content: dict[str, Any] = Field(default_factory=dict)

    mentions: list[ApiMessageMention] = Field(default_factory=list)
    attachments: list[ApiMessageAttachment] = Field(default_factory=list)
    reactions: list[ApiMessageReaction] = Field(default_factory=list)
    references: list[ApiMessageRef] = Field(default_factory=list)

    username: Optional[str] = None
    avatar: Optional[str] = None
    display_name: Optional[str] = None
    clan_nick: Optional[str] = None
    clan_avatar: Optional[str] = None
    channel_label: Optional[str] = None
    clan_logo: Optional[str] = None
    category_name: Optional[str] = None

    create_time_seconds: Optional[int] = None
    update_time_seconds: Optional[int] = None
    mode: Optional[int] = None
    is_public: Optional[bool] = None
    hide_editted: Optional[bool] = None
    topic_id: Optional[int] = None
    code: Optional[int] = None
    referenced_message: Optional[bytes] = None

    class Config:
        populate_by_name = True

    @property
    def id(self) -> int:
        """Alias for message_id (backward compatibility)"""
        return self.message_id

    @classmethod
    def from_protobuf(cls, message: api_pb2.ChannelMessage) -> "ChannelMessage":
        """
        Create a ChannelMessage from a protobuf ChannelMessage.

        Args:
            message: Protobuf ChannelMessage object

        Returns:
            ChannelMessage instance
        """

        def safe_json_parse(value: Optional[str | bytes], default):
            """Safely parse JSON string, return default on error or None"""
            if not value:
                return default
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
                return default

        def decode_protobuf_mentions(data: bytes) -> list[ApiMessageMention]:
            """Decode protobuf bytes to list of mentions"""
            if not data or not isinstance(data, bytes):
                return []
            try:
                mention_list = api_pb2.MessageMentionList()
                mention_list.ParseFromString(data)
                return [
                    ApiMessageMention(
                        id=m.id,
                        user_id=m.user_id,
                        username=m.username,
                        role_id=m.role_id,
                        rolename=m.rolename,
                        s=m.s,
                        e=m.e,
                    )
                    for m in mention_list.mentions
                ]
            except Exception as e:
                logger.error(f"Failed to decode mentions: {e}")
                return []

        def decode_protobuf_attachments(data: bytes) -> list[ApiMessageAttachment]:
            """Decode protobuf bytes to list of attachments"""
            if not data or not isinstance(data, bytes):
                return []
            try:
                attachment_list = api_pb2.MessageAttachmentList()
                attachment_list.ParseFromString(data)
                return [
                    ApiMessageAttachment(
                        filename=a.filename,
                        filetype=a.filetype,
                        height=a.height,
                        size=a.size,
                        url=a.url,
                        width=a.width,
                        thumbnail=a.thumbnail,
                        duration=a.duration,
                    )
                    for a in attachment_list.attachments
                ]
            except Exception as e:
                logger.error(f"Failed to decode attachments: {e}")
                return []

        def decode_protobuf_reactions(data: bytes) -> list[ApiMessageReaction]:
            """Decode protobuf bytes to list of reactions"""
            if not data or not isinstance(data, bytes):
                return []
            try:
                reaction_list = api_pb2.MessageReactionList()
                reaction_list.ParseFromString(data)
                return [
                    ApiMessageReaction(
                        action=r.action,
                        emoji_id=r.emoji_id,
                        emoji=r.emoji,
                        id=r.id,
                        sender_id=r.sender_id,
                        sender_name=r.sender_name,
                        sender_avatar=r.sender_avatar,
                        count=r.count,
                    )
                    for r in reaction_list.reactions
                ]
            except Exception as e:
                logger.error(f"Failed to decode reactions: {e}")
                return []

        def decode_protobuf_references(data: bytes) -> list[ApiMessageRef]:
            """Decode protobuf bytes to list of references"""
            if not data or not isinstance(data, bytes):
                return []
            try:
                ref_list = api_pb2.MessageRefList()
                ref_list.ParseFromString(data)
                return [
                    ApiMessageRef(
                        message_id=r.message_id,
                        message_ref_id=r.message_ref_id,
                        ref_type=r.ref_type,
                        message_sender_id=r.message_sender_id,
                        message_sender_username=r.message_sender_username,
                        message_sender_display_name=r.message_sender_display_name,
                        message_sender_avatar=r.mesages_sender_avatar,
                        has_attachment=r.has_attachment,
                        message_sender_clan_nick=r.message_sender_clan_nick,
                        content=r.content,
                    )
                    for r in ref_list.refs
                ]
            except Exception as e:
                logger.error(f"Failed to decode references: {e}")
                return []

        return cls(
            message_id=message.message_id,
            clan_id=message.clan_id,
            channel_id=message.channel_id,
            sender_id=message.sender_id,
            content=safe_json_parse(getattr(message, "content", None), {}),
            mentions=decode_protobuf_mentions(getattr(message, "mentions", b"")),
            attachments=decode_protobuf_attachments(
                getattr(message, "attachments", b"")
            ),
            reactions=decode_protobuf_reactions(getattr(message, "reactions", b"")),
            references=decode_protobuf_references(getattr(message, "references", b"")),
            username=getattr(message, "username", None),
            avatar=getattr(message, "avatar", None),
            display_name=getattr(message, "display_name", None),
            clan_nick=getattr(message, "clan_nick", None),
            clan_avatar=getattr(message, "clan_avatar", None),
            channel_label=getattr(message, "channel_label", None),
            clan_logo=getattr(message, "clan_logo", None),
            category_name=getattr(message, "category_name", None),
            create_time_seconds=getattr(message, "create_time_seconds", None),
            update_time_seconds=getattr(message, "update_time_seconds", None),
            mode=getattr(message, "mode", None),
            is_public=getattr(message, "is_public", None),
            hide_editted=getattr(message, "hide_editted", None),
            topic_id=getattr(message, "topic_id", None),
            code=getattr(message, "code", None),
            referenced_message=getattr(message, "referenced_message", None),
        )

    def to_message_dict(self) -> dict[str, Any]:
        """
        Convert to Message initialization dictionary.

        Returns:
            Dictionary suitable for Message class initialization
        """
        return self.model_dump(by_alias=False)

    def to_db_dict(self) -> dict[str, Any]:
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

    @classmethod
    def from_db_dict(cls, dict: dict[str, Any]) -> "ChannelMessage":
        """
        Create a ChannelMessage from a database dictionary.
        """
        reactions_data = (
            json.loads(dict["reactions"])
            if isinstance(dict["reactions"], str)
            else dict["reactions"]
        )
        mentions_data = (
            json.loads(dict["mentions"])
            if isinstance(dict["mentions"], str)
            else dict["mentions"]
        )
        attachments_data = (
            json.loads(dict["attachments"])
            if isinstance(dict["attachments"], str)
            else dict["attachments"]
        )
        references_data = (
            json.loads(dict.get("msg_references", "[]"))
            if isinstance(dict.get("msg_references"), str)
            else dict.get("msg_references", [])
        )
        content_data = (
            json.loads(dict["content"])
            if isinstance(dict["content"], str)
            else dict["content"]
        )

        return cls.model_validate(
            {
                "id": dict["id"],
                "clan_id": dict["clan_id"],
                "channel_id": dict["channel_id"],
                "sender_id": dict["sender_id"],
                "content": content_data,
                "reactions": [
                    ApiMessageReaction.model_validate(r) for r in reactions_data
                ],
                "mentions": [
                    ApiMessageMention.model_validate(m) for m in mentions_data
                ],
                "attachments": [
                    ApiMessageAttachment.model_validate(a) for a in attachments_data
                ],
                "references": [
                    ApiMessageRef.model_validate(r) for r in references_data
                ],
                "create_time_seconds": dict["create_time_seconds"],
                "topic_id": dict["topic_id"],
            }
        )


class UserInitData(BaseModel):
    """User initialization data from protobuf message"""

    id: int = Field(alias="sender_id")
    username: str = Field(default="")
    clan_nick: str = Field(default="")
    clan_avatar: str = Field(default="")
    avatar: str = Field(default="")
    display_name: str = Field(default="")
    dm_channel_id: int = Field(default=0, alias="dmChannelId")

    class Config:
        populate_by_name = True

    @classmethod
    def from_protobuf(
        cls, message: api_pb2.ChannelMessage, dm_channel_id: int = 0
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

    def to_user_dict(self) -> dict[str, Any]:
        """
        Convert to User class initialization dictionary.

        Returns:
            Dictionary suitable for User class initialization
        """
        return self.model_dump(by_alias=True)


# SSE / AI Agent Models


class SSEConfig(MezonBaseModel):
    """Server-Sent Events connection configuration."""

    url: str
    app_id: str
    token: str
    auto_reconnect: Optional[bool] = True
    reconnect_delay: Optional[int] = None
    max_reconnect_attempts: Optional[int] = None
    headers: Optional[dict[str, str]] = None


class SSEMessage(MezonBaseModel):
    """A message received over a Server-Sent Events connection."""

    id: Optional[str] = None
    event: Optional[str] = None
    data: str
    timestamp: int


class RoomInfo(MezonBaseModel):
    """Room info embedded in AI agent metadata events."""

    room_id: str
    room_name: str


class RoomMetadataEvent(MezonBaseModel):
    """Base room metadata event received from AI agent SSE stream.

    ``event_type`` is the value carried inside the SSE data payload
    (e.g. ``"room_started"``).  It is *not* the same as the internal
    routing key used by ``Events``/``InternalAgentEvents`` — the dispatch
    layer translates between the two, mirroring the JS SDK
    ``_emitAIAgentEvent`` switch.
    """

    event_id: str
    event_type: str
    timestamp: str
    room: RoomInfo
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIAgentSessionStartedEvent(RoomMetadataEvent):
    """AI agent session started.

    SSE payload ``event_type`` value; dispatch routing key is
    ``Events.AI_AGENT_SESSION_STARTED`` (``"session_started"``).
    """

    event_type: Literal["room_started"] = "room_started"


class AIAgentSessionEndedEvent(RoomMetadataEvent):
    """AI agent session ended.

    SSE payload ``event_type`` value; dispatch routing key is
    ``Events.AI_AGENT_SESSION_ENDED`` (``"session_ended"``).
    """

    event_type: Literal["room_ended"] = "room_ended"


class AIAgentSessionSummaryDoneEvent(RoomMetadataEvent):
    """AI agent session summary completed.

    SSE payload ``event_type`` value matches the dispatch routing key
    ``Events.AI_AGENT_SESSION_SUMMARY_DONE`` (``"room_summary_done"``).
    """

    event_type: Literal["room_summary_done"] = "room_summary_done"


# Envelope message type to Pydantic model mapping
ENVELOPE_TO_PYDANTIC_MAP: dict[str, type[BaseModel]] = {
    # Channel operations
    "channel_message": ChannelMessage,
    "channel_message_ack": ChannelMessageAck,
    "channel_message_send": ChannelMessageSend,
    "channel_message_update": ChannelMessageUpdate,
    "channel_message_remove": ChannelMessageRemove,
    "channel_join": ChannelJoin,
    "channel_leave": ChannelLeave,
    # Clan operations
    "clan_join": ClanJoin,
    # Events
    "channel_created_event": ChannelCreatedEvent,
    "channel_deleted_event": ChannelDeletedEvent,
    "channel_updated_event": ChannelUpdatedEvent,
    "clan_updated_event": ClanUpdatedEvent,
    "clan_profile_updated_event": ClanProfileUpdatedEvent,
    "custom_status_event": CustomStatusEvent,
    "message_typing_event": MessageTypingEvent,
    "last_seen_message_event": LastSeenMessageEvent,
    "last_pin_message_event": LastPinMessageEvent,
    "voice_joined_event": VoiceJoinedEvent,
    "voice_leaved_event": VoiceLeavedEvent,
    "voice_started_event": VoiceStartedEvent,
    "voice_ended_event": VoiceEndedEvent,
    "streaming_joined_event": StreamingJoinedEvent,
    "streaming_leaved_event": StreamingLeavedEvent,
    "user_channel_added_event": UserChannelAddedEvent,
    "user_channel_removed_event": UserChannelRemoved,
    "user_clan_removed_event": UserClanRemovedEvent,
    "user_profile_updated_event": UserProfileUpdatedEvent,
    "check_name_existed_event": ClanNameExistedEvent,
    "give_coffee_event": GiveCoffeeEvent,
    "token_sent_event": TokenSentEvent,
    "dropdown_box_selected": DropdownBoxSelected,
    "notifications": NotificationEvent,
    # Socket messages
    "ping": Ping,
    "pong": Pong,
    "rpc": Rpc,
    "error": SocketError,
}


def convert_envelope_to_pydantic(
    field_name: str, protobuf_message: Any
) -> BaseModel | Any:
    """
    Convert a protobuf envelope message to its corresponding Pydantic model.

    This function automatically converts protobuf messages to Pydantic models based on
    the ENVELOPE_TO_PYDANTIC_MAP. If no mapping exists, returns the original protobuf.

    Args:
        field_name: The envelope field name (from WhichOneof)
        protobuf_message: The protobuf message instance

    Returns:
        Pydantic model instance if mapping exists and has from_protobuf(),
        otherwise returns the original protobuf message

    Example:
        >>> envelope = parse_protobuf(message_bytes)
        >>> field_name = envelope.WhichOneof("message")
        >>> payload = getattr(envelope, field_name)
        >>> pydantic_model = convert_envelope_to_pydantic(field_name, payload)
        >>> # pydantic_model is now a Pydantic instance, not protobuf
    """
    pydantic_class = ENVELOPE_TO_PYDANTIC_MAP.get(field_name)

    if pydantic_class:
        try:
            if hasattr(pydantic_class, "from_protobuf"):
                return pydantic_class.from_protobuf(protobuf_message)
            else:
                return protobuf_to_pydantic(protobuf_message, pydantic_class)
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to convert {field_name} to Pydantic: {e}. "
                f"Falling back to protobuf object."
            )
            return protobuf_message

    return protobuf_message
