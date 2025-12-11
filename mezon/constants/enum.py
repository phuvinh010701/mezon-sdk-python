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

from enum import Enum, IntEnum


class InternalEventsSocket(str, Enum):
    """Internal events socket will handle from MezonClient"""

    VOICE_STARTED_EVENT = "voice_started_event"
    VOICE_ENDED_EVENT = "voice_ended_event"
    VOICE_JOINED_EVENT = "voice_joined_event"
    VOICE_LEAVED_EVENT = "voice_leaved_event"
    CHANNEL_CREATED_EVENT = "channel_created_event"
    CHANNEL_DELETED_EVENT = "channel_deleted_event"
    CHANNEL_UPDATED_EVENT = "channel_updated_event"
    CLAN_PROFILE_UPDATED_EVENT = "clan_profile_updated_event"
    CLAN_UPDATED_EVENT = "clan_updated_event"
    STATUS_PRESENCE_EVENT = "status_presence_event"
    STREAM_PRESENCE_EVENT = "stream_presence_event"
    STREAM_DATA = "stream_data"
    CHANNEL_MESSAGE = "channel_message"
    MESSAGE_TYPING_EVENT = "message_typing_event"
    MESSAGE_REACTION_EVENT = "message_reaction_event"
    CHANNEL_PRESENCE_EVENT = "channel_presence_event"
    LAST_PIN_MESSAGE_EVENT = "last_pin_message_event"
    CUSTOM_STATUS_EVENT = "custom_status_event"
    USER_CHANNEL_ADDED_EVENT = "user_channel_added_event"
    ADD_CLAN_USER_EVENT = "add_clan_user_event"
    USER_PROFILE_UPDATED_EVENT = "user_profile_updated_event"
    USER_CHANNEL_REMOVED_EVENT = "user_channel_removed_event"
    USER_CLAN_REMOVED_EVENT = "user_clan_removed_event"
    ROLE_EVENT = "role_event"
    GIVE_COFFEE_EVENT = "give_coffee_event"
    ROLE_ASSIGN_EVENT = "role_assign_event"
    TOKEN_SEND = "token_sent_event"
    CLAN_EVENT_CREATED = "clan_event_created"
    MESSAGE_BUTTON_CLICKED = "message_button_clicked"
    STREAMING_JOINED_EVENT = "streaming_joined_event"
    STREAMING_LEAVED_EVENT = "streaming_leaved_event"
    DROPDOWN_BOX_SELECTED = "dropdown_box_selected"
    WEBRTC_SIGNALING_FWD = "webrtc_signaling_fwd"
    NOTIFICATIONS = "notifications"
    QUICK_MENU = "quick_menu_event"


class Events(str, Enum):
    """Events that can be listened to from the MezonClient"""

    # Listen to messages user sends on the channel, thread
    CHANNEL_MESSAGE = InternalEventsSocket.CHANNEL_MESSAGE.value

    # Listen to user react to messages on the channel, thread
    MESSAGE_REACTION = InternalEventsSocket.MESSAGE_REACTION_EVENT.value

    # Listen to user removed from the channel
    USER_CHANNEL_REMOVED = InternalEventsSocket.USER_CHANNEL_REMOVED_EVENT.value

    # Listen to user leaved/removed in the clan
    USER_CLAN_REMOVED = InternalEventsSocket.USER_CLAN_REMOVED_EVENT.value

    # Listen to user added in the channel
    USER_CHANNEL_ADDED = InternalEventsSocket.USER_CHANNEL_ADDED_EVENT.value

    # Listen to channel created
    CHANNEL_CREATED = InternalEventsSocket.CHANNEL_CREATED_EVENT.value

    # Listen to channel deleted
    CHANNEL_DELETED = InternalEventsSocket.CHANNEL_DELETED_EVENT.value

    # Listen to channel updated
    CHANNEL_UPDATED = InternalEventsSocket.CHANNEL_UPDATED_EVENT.value

    # Listen to clan create new role
    ROLE_EVENT = InternalEventsSocket.ROLE_EVENT.value

    # Listen to users give coffee to each other
    GIVE_COFFEE = InternalEventsSocket.GIVE_COFFEE_EVENT.value

    # Listen to assigning a role to user
    ROLE_ASSIGN = InternalEventsSocket.ROLE_ASSIGN_EVENT.value

    # Listen to user added in CLAN
    ADD_CLAN_USER = InternalEventsSocket.ADD_CLAN_USER_EVENT.value

    # Listen to user send token to each other
    TOKEN_SEND = InternalEventsSocket.TOKEN_SEND.value

    # Listen to clan create a new event
    CLAN_EVENT_CREATED = InternalEventsSocket.CLAN_EVENT_CREATED.value

    # Listen to user click a button on embed message
    MESSAGE_BUTTON_CLICKED = InternalEventsSocket.MESSAGE_BUTTON_CLICKED.value

    # Listen to user joined a stream room
    STREAMING_JOINED_EVENT = InternalEventsSocket.STREAMING_JOINED_EVENT.value

    # Listen to user leaved a stream room
    STREAMING_LEAVED_EVENT = InternalEventsSocket.STREAMING_LEAVED_EVENT.value

    # Listen to user selected a input dropdown
    DROPDOWN_BOX_SELECTED = InternalEventsSocket.DROPDOWN_BOX_SELECTED.value

    # Listen to user accepted call 1-1
    WEBRTC_SIGNALING_FWD = InternalEventsSocket.WEBRTC_SIGNALING_FWD.value

    # Listen to start voice
    VOICE_STARTED_EVENT = InternalEventsSocket.VOICE_STARTED_EVENT.value

    # Listen to end voice
    VOICE_ENDED_EVENT = InternalEventsSocket.VOICE_ENDED_EVENT.value

    # Listen to user join voice room
    VOICE_JOINED_EVENT = InternalEventsSocket.VOICE_JOINED_EVENT.value

    # Listen to user leave voice room
    VOICE_LEAVED_EVENT = InternalEventsSocket.VOICE_LEAVED_EVENT.value

    # Listen to add friend
    NOTIFICATIONS = InternalEventsSocket.NOTIFICATIONS.value

    # Listen to add quick menu
    QUICK_MENU = InternalEventsSocket.QUICK_MENU.value


class ChannelType(IntEnum):
    """Channel types"""

    CHANNEL_TYPE_CHANNEL = 1
    CHANNEL_TYPE_GROUP = 2
    CHANNEL_TYPE_DM = 3
    CHANNEL_TYPE_GMEET_VOICE = 4
    CHANNEL_TYPE_FORUM = 5
    CHANNEL_TYPE_STREAMING = 6
    CHANNEL_TYPE_THREAD = 7
    CHANNEL_TYPE_APP = 8
    CHANNEL_TYPE_ANNOUNCEMENT = 9
    CHANNEL_TYPE_MEZON_VOICE = 10


class ChannelStreamMode(IntEnum):
    """Channel stream modes"""

    STREAM_MODE_CHANNEL = 2
    STREAM_MODE_GROUP = 3
    STREAM_MODE_DM = 4
    STREAM_MODE_CLAN = 5
    STREAM_MODE_THREAD = 6


class TypeMessage(IntEnum):
    """Message types"""

    CHAT = 0
    CHAT_UPDATE = 1
    CHAT_REMOVE = 2
    TYPING = 3
    INDICATOR = 4
    WELCOME = 5
    CREATE_THREAD = 6
    CREATE_PIN = 7
    MESSAGE_BUZZ = 8
    TOPIC = 9
    AUDIT_LOG = 10
    SEND_TOKEN = 11
    EPHEMERAL = 12
    UPCOMING_EVENT = 13
    UPDATE_EPHEMERAL_MSG = 14
    DELETE_EPHEMERAL_MSG = 15
