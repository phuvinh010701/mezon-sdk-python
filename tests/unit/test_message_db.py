from pathlib import Path

import pytest

from mezon.messages.db import MessageDB


class TestMessageDB:
    @pytest.mark.asyncio
    async def test_ensure_directory_creates_parent(self, tmp_path: Path):
        db_path = tmp_path / "nested" / "messages.db"

        MessageDB(str(db_path))

        assert db_path.parent.exists()

    @pytest.mark.asyncio
    async def test_save_and_get_message_by_id(self, tmp_path: Path):
        db = MessageDB(str(tmp_path / "messages.db"))
        message = {
            "message_id": 1,
            "channel_id": 2,
            "clan_id": 3,
            "sender_id": 4,
            "content": {"t": "hello"},
            "mentions": [{"user_id": 5, "username": "alice"}],
            "attachments": [{"filename": "a.txt", "url": "https://example.com/a.txt"}],
            "reactions": [{"emoji": "👍", "count": 1}],
            "references": [
                {"message_ref_id": 99, "message_sender_id": 6, "content": "quoted"}
            ],
            "topic_id": 7,
            "create_time_seconds": 100,
        }

        await db.save_message(message)
        stored = await db.get_message_by_id(1, 2)

        assert stored is not None
        assert stored.message_id == 1
        assert stored.channel_id == 2
        assert stored.content == {"t": "hello"}
        assert stored.mentions[0].user_id == 5
        assert stored.attachments[0].filename == "a.txt"
        assert stored.references[0].message_ref_id == 99

        await db.close()

    @pytest.mark.asyncio
    async def test_get_messages_by_channel_orders_latest_first(self, tmp_path: Path):
        db = MessageDB(str(tmp_path / "messages.db"))

        await db.save_message(
            {
                "message_id": 1,
                "channel_id": 2,
                "content": {"t": "first"},
                "create_time_seconds": 10,
            }
        )
        await db.save_message(
            {
                "message_id": 2,
                "channel_id": 2,
                "content": {"t": "second"},
                "create_time_seconds": 20,
            }
        )

        messages = await db.get_messages_by_channel("2")

        assert [message["id"] for message in messages] == ["2", "1"]
        assert messages[0]["content"] == {"t": "second"}

        await db.close()

    @pytest.mark.asyncio
    async def test_delete_and_clear_channel_messages(self, tmp_path: Path):
        db = MessageDB(str(tmp_path / "messages.db"))

        await db.save_message({"message_id": 1, "channel_id": 2, "content": {"t": "a"}})
        await db.save_message({"message_id": 2, "channel_id": 2, "content": {"t": "b"}})
        await db.save_message({"message_id": 3, "channel_id": 3, "content": {"t": "c"}})

        deleted = await db.delete_message("1", "2")
        cleared = await db.clear_channel_messages("2")
        total_count = await db.get_message_count()
        channel_three_count = await db.get_message_count("3")

        assert deleted is True
        assert cleared == 1
        assert total_count == 1
        assert channel_three_count == 1

        await db.close()

    @pytest.mark.asyncio
    async def test_context_manager_closes_connection(self, tmp_path: Path):
        db = MessageDB(str(tmp_path / "messages.db"))

        async with db as opened:
            assert opened.db is not None
            assert opened._initialized is True

        assert db.db is None
        assert db._initialized is False
