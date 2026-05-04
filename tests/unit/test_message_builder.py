"""
Unit tests for message builder classes.
"""

from mezon.models import (
    ApiMessageAttachment,
    ApiMessageMention,
    ApiMessageRef,
    ChannelMessageContent,
)
from mezon.socket.message_builder import (
    ChannelMessageBuilder,
    ChannelMessageUpdateBuilder,
    EphemeralMessageBuilder,
    MessageReactionBuilder,
)


class TestChannelMessageBuilder:
    """Test ChannelMessageBuilder class."""

    def test_build_basic_message(self):
        """Test building a basic channel message."""
        message = ChannelMessageBuilder.build(
            clan_id=123,
            channel_id=456,
            mode=2,
            is_public=True,
            content={"text": "Hello World"},
        )

        assert message.clan_id == 123
        assert message.channel_id == 456
        assert message.mode == 2
        assert message.is_public is True
        assert '"text": "Hello World"' in message.content

    def test_build_with_content_model(self):
        """Test building message with ChannelMessageContent model."""
        content = ChannelMessageContent(t="Hello from model")
        message = ChannelMessageBuilder.build(
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=False,
            content=content,
        )

        assert message.clan_id == 1
        assert '"t":' in message.content or '"t" :' in message.content

    def test_build_with_mentions(self):
        """Test building message with mentions."""
        mentions = [
            ApiMessageMention(user_id=1001, username="Alice", s=0, e=5),
            ApiMessageMention(user_id=1002, username="Bob", s=10, e=13),
        ]

        message = ChannelMessageBuilder.build(
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=True,
            content={"text": "Hello @Alice and @Bob"},
            mentions=mentions,
        )

        assert len(message.mentions) == 2
        assert message.mentions[0].user_id == 1001
        assert message.mentions[0].username == "Alice"
        assert message.mentions[0].s == 0
        assert message.mentions[0].e == 5
        assert message.mentions[1].user_id == 1002

    def test_build_with_attachments(self):
        """Test building message with attachments."""
        attachments = [
            ApiMessageAttachment(
                filename="image.png",
                url="https://example.com/image.png",
                filetype="image/png",
                size=1024,
                width=800,
                height=600,
            ),
        ]

        message = ChannelMessageBuilder.build(
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=True,
            content={"text": "Check this out"},
            attachments=attachments,
        )

        assert len(message.attachments) == 1
        assert message.attachments[0].filename == "image.png"
        assert message.attachments[0].url == "https://example.com/image.png"
        assert message.attachments[0].size == 1024
        assert message.attachments[0].width == 800
        assert message.attachments[0].height == 600

    def test_build_with_references(self):
        """Test building message with references."""
        references = [
            ApiMessageRef(
                message_ref_id=12345,
                message_sender_id=67890,
                message_sender_username="Alice",
                content="Original message",
                has_attachment=True,
            ),
        ]

        message = ChannelMessageBuilder.build(
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=True,
            content={"text": "Reply to message"},
            references=references,
        )

        assert len(message.references) == 1
        assert message.references[0].message_ref_id == 12345
        assert message.references[0].message_sender_id == 67890
        assert message.references[0].message_sender_username == "Alice"
        assert message.references[0].has_attachment is True

    def test_build_with_optional_fields(self):
        """Test building message with optional fields."""
        message = ChannelMessageBuilder.build(
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=True,
            content={"text": "Anonymous message"},
            anonymous_message=True,
            mention_everyone=True,
            avatar="https://example.com/avatar.png",
            code=42,
            topic_id=999,
        )

        assert message.anonymous_message is True
        assert message.mention_everyone is True
        assert message.avatar == "https://example.com/avatar.png"
        assert message.code == 42
        assert message.topic_id == 999


class TestEphemeralMessageBuilder:
    """Test EphemeralMessageBuilder class."""

    def test_build_ephemeral_message(self):
        """Test building an ephemeral message."""
        message = EphemeralMessageBuilder.build(
            receiver_ids=[100, 200, 300],
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=False,
            content={"text": "Private message"},
        )

        assert len(message.receiver_ids) == 3
        assert 100 in message.receiver_ids
        assert 200 in message.receiver_ids
        assert 300 in message.receiver_ids
        assert message.message.clan_id == 1
        assert message.message.channel_id == 2

    def test_build_ephemeral_with_message_id(self):
        """Test building ephemeral message with message ID."""
        message = EphemeralMessageBuilder.build(
            receiver_ids=[100],
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=True,
            content={"text": "Update"},
            message_id=12345,
        )

        assert message.message.id == 12345


class TestChannelMessageUpdateBuilder:
    """Test ChannelMessageUpdateBuilder class."""

    def test_build_message_update(self):
        """Test building a message update."""
        message = ChannelMessageUpdateBuilder.build(
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=True,
            message_id=999,
            content={"text": "Updated content"},
        )

        assert message.clan_id == 1
        assert message.channel_id == 2
        assert message.message_id == 999
        assert "Updated content" in message.content

    def test_build_update_with_mentions_and_attachments(self):
        """Test building update with mentions and attachments."""
        mentions = [ApiMessageMention(user_id=1001, username="Alice")]
        attachments = [
            ApiMessageAttachment(filename="doc.pdf", url="https://example.com/doc.pdf")
        ]

        message = ChannelMessageUpdateBuilder.build(
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=True,
            message_id=999,
            content={"text": "Updated with files"},
            mentions=mentions,
            attachments=attachments,
        )

        assert len(message.mentions) == 1
        assert len(message.attachments) == 1

    def test_build_update_with_optional_fields(self):
        """Test building update with optional fields."""
        message = ChannelMessageUpdateBuilder.build(
            clan_id=1,
            channel_id=2,
            mode=2,
            is_public=True,
            message_id=999,
            content={"text": "Updated"},
            hide_editted=True,
            topic_id=555,
            is_update_msg_topic=True,
        )

        assert message.hide_editted is True
        assert message.topic_id == 555
        assert message.is_update_msg_topic is True


class TestMessageReactionBuilder:
    """Test MessageReactionBuilder class."""

    def test_build_reaction(self):
        """Test building a message reaction."""
        reaction = MessageReactionBuilder.build(
            id=1,
            clan_id=100,
            channel_id=200,
            mode=2,
            is_public=True,
            message_id=300,
            emoji_id=10,
            emoji="👍",
            count=5,
            message_sender_id=400,
            action_delete=False,
        )

        assert reaction.id == 1
        assert reaction.clan_id == 100
        assert reaction.channel_id == 200
        assert reaction.message_id == 300
        assert reaction.emoji_id == 10
        assert reaction.emoji == "👍"
        assert reaction.count == 5
        assert reaction.message_sender_id == 400
        assert reaction.action is False

    def test_build_reaction_delete(self):
        """Test building a reaction deletion."""
        reaction = MessageReactionBuilder.build(
            id=1,
            clan_id=100,
            channel_id=200,
            mode=2,
            is_public=True,
            message_id=300,
            emoji_id=10,
            emoji="👍",
            count=4,
            message_sender_id=400,
            action_delete=True,
        )

        assert reaction.action is True

    def test_build_reaction_with_none_id(self):
        """Test building reaction with None ID defaults to 0."""
        reaction = MessageReactionBuilder.build(
            id=None,
            clan_id=100,
            channel_id=200,
            mode=2,
            is_public=True,
            message_id=300,
            emoji_id=None,
            emoji="❤️",
            count=1,
            message_sender_id=400,
            action_delete=False,
        )

        assert reaction.id == 0
        assert reaction.emoji_id == 0
