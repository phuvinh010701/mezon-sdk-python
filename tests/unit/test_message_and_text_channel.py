from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from mezon.constants import ChannelType
from mezon.models import ApiChannelDescription, ChannelMessage, ChannelMessageContent
from mezon.structures.message import Message
from mezon.structures.text_channel import TextChannel


class TestMessageAndTextChannel:
    def make_channel(self):
        socket_manager = SimpleNamespace(
            write_chat_message=AsyncMock(return_value="ack"),
            write_ephemeral_message=AsyncMock(return_value="ephemeral-ack"),
            update_chat_message=AsyncMock(return_value="updated"),
            write_message_reaction=AsyncMock(return_value="reacted"),
            remove_chat_message=AsyncMock(return_value="deleted"),
        )
        clan = SimpleNamespace(
            id=99,
            client=SimpleNamespace(
                users=SimpleNamespace(
                    fetch=AsyncMock(
                        return_value=SimpleNamespace(
                            clan_nick="Clan Nick",
                            display_name="Display Name",
                            username="username",
                            clan_avatar="clan-avatar",
                            avatar="avatar",
                        )
                    )
                )
            ),
            users=SimpleNamespace(
                fetch=AsyncMock(
                    return_value=SimpleNamespace(
                        clan_nick="Clan Nick",
                        display_name="Display Name",
                        username="username",
                        clan_avatar="clan-avatar",
                        avatar="avatar",
                    )
                )
            ),
        )
        channel = TextChannel(
            ApiChannelDescription(
                channel_id=10,
                channel_label="general",
                type=ChannelType.CHANNEL_TYPE_CHANNEL,
                channel_private=0,
                clan_id=99,
            ),
            clan,
            socket_manager,
            SimpleNamespace(get_message_by_id=AsyncMock()),
        )
        return channel, socket_manager

    def make_message_raw(self):
        return ChannelMessage(
            message_id=123,
            clan_id=99,
            channel_id=10,
            sender_id=321,
            content={"t": "hello"},
            topic_id=555,
        )

    @pytest.mark.asyncio
    async def test_text_channel_send_delegates_to_socket_manager(self):
        channel, socket_manager = self.make_channel()

        result = await channel.send(
            ChannelMessageContent(t="hello"), mention_everyone=True
        )

        assert result == "ack"
        call = socket_manager.write_chat_message.await_args.kwargs
        assert call["clan_id"] == 99
        assert call["channel_id"] == 10
        assert call["is_public"] is True
        assert call["mention_everyone"] is True

    @pytest.mark.asyncio
    async def test_text_channel_send_ephemeral_builds_reference_when_requested(self):
        channel, socket_manager = self.make_channel()
        referenced_message = Message(self.make_message_raw(), channel, socket_manager)
        channel.messages.fetch = AsyncMock(return_value=referenced_message)

        result = await channel.send_ephemeral(
            [1, 2], {"t": "secret"}, reference_message_id=123
        )

        assert result == "ephemeral-ack"
        references = socket_manager.write_ephemeral_message.await_args.kwargs[
            "references"
        ]
        assert references[0].message_ref_id == 123
        assert references[0].message_sender_id == 321

    @pytest.mark.asyncio
    async def test_message_reply_uses_original_message_as_reference(self):
        channel, socket_manager = self.make_channel()
        message = Message(self.make_message_raw(), channel, socket_manager)

        result = await message.reply(ChannelMessageContent(t="reply"))

        assert result == "ack"
        references = socket_manager.write_chat_message.await_args.kwargs["references"]
        assert references[0].message_ref_id == 123
        assert references[0].message_sender_username == "Clan Nick"

    @pytest.mark.asyncio
    async def test_message_update_react_and_delete_delegate(self):
        channel, socket_manager = self.make_channel()
        message = Message(self.make_message_raw(), channel, socket_manager)

        updated = await message.update(ChannelMessageContent(t="updated"))
        reacted = await message.react(emoji_id=1, emoji="👍", count=1)
        deleted = await message.delete()

        assert updated == "updated"
        assert reacted == "reacted"
        assert deleted == "deleted"
        assert socket_manager.update_chat_message.await_count == 1
        assert socket_manager.write_message_reaction.await_count == 1
        assert socket_manager.remove_chat_message.await_count == 1

    @pytest.mark.asyncio
    async def test_text_channel_message_fetcher_wraps_database_message(self):
        channel, socket_manager = self.make_channel()
        message_raw = self.make_message_raw()
        channel.message_db.get_message_by_id = AsyncMock(return_value=message_raw)

        message = await channel.message_fetcher(123)

        assert isinstance(message, Message)
        assert message.id == 123

    def test_repr_methods_include_key_fields(self):
        channel, socket_manager = self.make_channel()
        message = Message(self.make_message_raw(), channel, socket_manager)

        assert "TextChannel" in repr(channel)
        assert "Message id=123" in repr(message)
