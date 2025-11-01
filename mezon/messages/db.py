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

import aiosqlite
import json
import os
from typing import Optional, Dict, Any, List
from mezon.utils.logger import get_logger

logger = get_logger(__name__)


class MessageDB:
    """
    Async SQLite-based message database for caching Mezon messages.
    """

    def __init__(self, db_path: str = "./mezon-cache/mezon-messages-cache.db"):
        """
        Initialize the message database.

        Args:
            db_path: Path to the SQLite database file (default: ./mezon-cache/mezon-messages-cache.db)
        """
        self.db_path = db_path
        self._ensure_directory()
        self.db: Optional[aiosqlite.Connection] = None
        self._initialized = False

    def _ensure_directory(self) -> None:
        """Create the database directory if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")

    async def _ensure_connection(self) -> None:
        """Ensure database connection is established and initialized."""
        if self.db is None or not self._initialized:
            self.db = await aiosqlite.connect(self.db_path)
            self.db.row_factory = aiosqlite.Row
            await self._init_tables()
            self._initialized = True

    async def _init_tables(self) -> None:
        """Initialize database tables and indexes."""
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                clan_id TEXT,
                sender_id TEXT,
                content TEXT,
                mentions TEXT,
                attachments TEXT,
                reactions TEXT,
                msg_references TEXT,
                topic_id TEXT,
                create_time_seconds INTEGER,
                PRIMARY KEY (id, channel_id)
            )
        """
        )

        await self.db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_channel_id
            ON messages(channel_id)
        """
        )

        await self.db.commit()
        logger.debug("Database tables initialized")

    async def save_message(self, message: Dict[str, Any]) -> None:
        """
        Save or update a message in the database.

        Args:
            message: Message data dictionary containing:
                - message_id: The message ID
                - channel_id: The channel ID
                - clan_id: The clan ID (optional)
                - sender_id: The sender's user ID (optional)
                - content: Message content (will be JSON serialized)
                - mentions: List of mentions (optional)
                - attachments: List of attachments (optional)
                - reactions: List of reactions (optional)
                - references: Message references (optional)
                - topic_id: Topic ID (optional)
                - create_time_seconds: Creation timestamp (optional)
        """
        await self._ensure_connection()

        await self.db.execute(
            """
            INSERT OR REPLACE INTO messages (
                id, clan_id, channel_id, sender_id,
                content, mentions, attachments, reactions,
                msg_references, topic_id, create_time_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                message.get("message_id"),
                message.get("clan_id"),
                message.get("channel_id"),
                message.get("sender_id"),
                json.dumps(message.get("content", {})),
                json.dumps(message.get("mentions", [])),
                json.dumps(message.get("attachments", [])),
                json.dumps(message.get("reactions", [])),
                json.dumps(message.get("references", [])),
                message.get("topic_id"),
                message.get("create_time_seconds"),
            ),
        )

        await self.db.commit()
        logger.debug(
            f"Saved message {message.get('message_id')} in channel {message.get('channel_id')}"
        )

    async def get_message_by_id(
        self, message_id: str, channel_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a message by its ID and channel ID.

        Args:
            message_id: The message ID
            channel_id: The channel ID

        Returns:
            Message dictionary if found, None otherwise
        """
        await self._ensure_connection()

        async with self.db.execute(
            """
            SELECT * FROM messages
            WHERE channel_id = ? AND id = ?
            LIMIT 1
        """,
            (channel_id, message_id),
        ) as cursor:
            row = await cursor.fetchone()

        if not row:
            return None

        message = dict(row)
        message["content"] = json.loads(message["content"])
        message["mentions"] = json.loads(message["mentions"])
        message["attachments"] = json.loads(message["attachments"])
        message["reactions"] = json.loads(message["reactions"])
        message["references"] = json.loads(message["msg_references"])
        del message["msg_references"]

        return message

    async def get_messages_by_channel(
        self, channel_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve messages from a specific channel.

        Args:
            channel_id: The channel ID
            limit: Maximum number of messages to retrieve (default: 50)
            offset: Number of messages to skip (default: 0)

        Returns:
            List of message dictionaries
        """
        await self._ensure_connection()

        async with self.db.execute(
            """
            SELECT * FROM messages
            WHERE channel_id = ?
            ORDER BY create_time_seconds DESC
            LIMIT ? OFFSET ?
        """,
            (channel_id, limit, offset),
        ) as cursor:
            rows = await cursor.fetchall()

        messages = []
        for row in rows:
            message = dict(row)
            message["content"] = json.loads(message["content"])
            message["mentions"] = json.loads(message["mentions"])
            message["attachments"] = json.loads(message["attachments"])
            message["reactions"] = json.loads(message["reactions"])
            message["references"] = json.loads(message["msg_references"])
            del message["msg_references"]
            messages.append(message)

        return messages

    async def delete_message(self, message_id: str, channel_id: str) -> bool:
        """
        Delete a message from the database.

        Args:
            message_id: The message ID
            channel_id: The channel ID

        Returns:
            True if the message was deleted, False otherwise
        """
        await self._ensure_connection()

        cursor = await self.db.execute(
            """
            DELETE FROM messages
            WHERE id = ? AND channel_id = ?
        """,
            (message_id, channel_id),
        )

        await self.db.commit()
        deleted = cursor.rowcount > 0

        if deleted:
            logger.debug(f"Deleted message {message_id} from channel {channel_id}")

        return deleted

    async def clear_channel_messages(self, channel_id: str) -> int:
        """
        Clear all messages from a specific channel.

        Args:
            channel_id: The channel ID

        Returns:
            Number of messages deleted
        """
        await self._ensure_connection()

        cursor = await self.db.execute(
            """
            DELETE FROM messages
            WHERE channel_id = ?
        """,
            (channel_id,),
        )

        await self.db.commit()
        deleted_count = cursor.rowcount

        logger.info(f"Cleared {deleted_count} messages from channel {channel_id}")
        return deleted_count

    async def get_message_count(self, channel_id: Optional[str] = None) -> int:
        """
        Get the total number of messages in the database or in a specific channel.

        Args:
            channel_id: The channel ID (optional). If None, returns total message count.

        Returns:
            Number of messages
        """
        await self._ensure_connection()

        if channel_id:
            async with self.db.execute(
                """
                SELECT COUNT(*) FROM messages
                WHERE channel_id = ?
            """,
                (channel_id,),
            ) as cursor:
                row = await cursor.fetchone()
        else:
            async with self.db.execute("SELECT COUNT(*) FROM messages") as cursor:
                row = await cursor.fetchone()

        return row[0]

    async def close(self) -> None:
        """Close the database connection."""
        if self.db:
            await self.db.close()
            self.db = None
            self._initialized = False
            logger.debug("Database connection closed")

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
