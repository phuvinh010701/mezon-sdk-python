"""
Unit tests for SSE / AI Agent models and enums added in v2.8.44 sync.

Tests cover:
- SSEConfig, SSEMessage, RoomInfo, RoomMetadataEvent
- AIAgentSessionStartedEvent, AIAgentSessionEndedEvent, AIAgentSessionSummaryDoneEvent
- InternalAgentEvents, SSEEvents, SSEConnectionState enums
- Events enum additions for AI agent session events
"""

import pytest
from pydantic import ValidationError

from mezon.constants.enum import (
    Events,
    InternalAgentEvents,
    SSEConnectionState,
    SSEEvents,
)
from mezon.models import (
    AIAgentSessionEndedEvent,
    AIAgentSessionStartedEvent,
    AIAgentSessionSummaryDoneEvent,
    RoomInfo,
    RoomMetadataEvent,
    SSEConfig,
    SSEMessage,
)

# ---------------------------------------------------------------------------
# SSEConfig
# ---------------------------------------------------------------------------


class TestSSEConfig:
    """Tests for SSEConfig model."""

    def test_required_fields(self) -> None:
        cfg = SSEConfig(url="https://example.com/sse", app_id="app-1", token="tok-123")
        assert cfg.url == "https://example.com/sse"
        assert cfg.app_id == "app-1"
        assert cfg.token == "tok-123"

    def test_default_auto_reconnect_is_true(self) -> None:
        cfg = SSEConfig(url="https://example.com/sse", app_id="app-1", token="tok")
        assert cfg.auto_reconnect is True

    def test_optional_fields_default_none(self) -> None:
        cfg = SSEConfig(url="https://example.com/sse", app_id="app-1", token="tok")
        assert cfg.reconnect_delay is None
        assert cfg.max_reconnect_attempts is None
        assert cfg.headers is None

    def test_optional_fields_set(self) -> None:
        cfg = SSEConfig(
            url="https://example.com/sse",
            app_id="app-1",
            token="tok",
            auto_reconnect=False,
            reconnect_delay=3000,
            max_reconnect_attempts=5,
            headers={"Authorization": "Bearer xyz"},
        )
        assert cfg.auto_reconnect is False
        assert cfg.reconnect_delay == 3000
        assert cfg.max_reconnect_attempts == 5
        assert cfg.headers == {"Authorization": "Bearer xyz"}

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises(ValidationError):
            SSEConfig(app_id="app-1", token="tok")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# SSEMessage
# ---------------------------------------------------------------------------


class TestSSEMessage:
    """Tests for SSEMessage model."""

    def test_required_fields(self) -> None:
        msg = SSEMessage(data="hello", timestamp=1700000000000)
        assert msg.data == "hello"
        assert msg.timestamp == 1700000000000

    def test_optional_fields_default_none(self) -> None:
        msg = SSEMessage(data="payload", timestamp=1)
        assert msg.id is None
        assert msg.event is None

    def test_all_fields(self) -> None:
        msg = SSEMessage(
            id="msg-1", event="room_started", data='{"key":"val"}', timestamp=42
        )
        assert msg.id == "msg-1"
        assert msg.event == "room_started"
        assert msg.data == '{"key":"val"}'
        assert msg.timestamp == 42

    def test_missing_data_raises(self) -> None:
        with pytest.raises(ValidationError):
            SSEMessage(timestamp=1)  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# RoomInfo
# ---------------------------------------------------------------------------


class TestRoomInfo:
    """Tests for RoomInfo model."""

    def test_basic(self) -> None:
        room = RoomInfo(room_id="room-abc", room_name="Test Room")
        assert room.room_id == "room-abc"
        assert room.room_name == "Test Room"

    def test_missing_field_raises(self) -> None:
        with pytest.raises(ValidationError):
            RoomInfo(room_name="Only name")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# RoomMetadataEvent
# ---------------------------------------------------------------------------


class TestRoomMetadataEvent:
    """Tests for RoomMetadataEvent base model."""

    def _make(self, **kwargs) -> RoomMetadataEvent:
        defaults = {
            "event_id": "evt-001",
            "event_type": "custom_event",
            "timestamp": "2026-04-16T06:00:00Z",
            "room": {"room_id": "r-1", "room_name": "My Room"},
        }
        defaults.update(kwargs)
        return RoomMetadataEvent(**defaults)

    def test_basic_creation(self) -> None:
        evt = self._make()
        assert evt.event_id == "evt-001"
        assert evt.event_type == "custom_event"
        assert isinstance(evt.room, RoomInfo)
        assert evt.room.room_id == "r-1"

    def test_metadata_defaults_to_empty_dict(self) -> None:
        evt = self._make()
        assert evt.metadata == {}

    def test_metadata_with_data(self) -> None:
        evt = self._make(metadata={"duration": 120, "summary": "done"})
        assert evt.metadata["duration"] == 120

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises(ValidationError):
            RoomMetadataEvent(
                event_type="x",
                timestamp="2026-01-01T00:00:00Z",
                room={"room_id": "r", "room_name": "n"},
            )  # event_id missing


# ---------------------------------------------------------------------------
# AIAgentSessionStartedEvent
# ---------------------------------------------------------------------------


class TestAIAgentSessionStartedEvent:
    """Tests for AIAgentSessionStartedEvent."""

    def _make(self, **kwargs) -> AIAgentSessionStartedEvent:
        defaults = {
            "event_id": "start-001",
            "timestamp": "2026-04-16T06:00:00Z",
            "room": {"room_id": "r-1", "room_name": "Room 1"},
        }
        defaults.update(kwargs)
        return AIAgentSessionStartedEvent(**defaults)

    def test_event_type_is_room_started(self) -> None:
        evt = self._make()
        assert evt.event_type == "room_started"

    def test_event_type_cannot_be_overridden(self) -> None:
        """Literal field should reject wrong value."""
        with pytest.raises(ValidationError):
            AIAgentSessionStartedEvent(
                event_id="x",
                event_type="room_ended",  # wrong literal
                timestamp="2026-01-01T00:00:00Z",
                room={"room_id": "r", "room_name": "n"},
            )

    def test_inherits_room_metadata(self) -> None:
        evt = self._make()
        assert isinstance(evt.room, RoomInfo)
        assert evt.metadata == {}


# ---------------------------------------------------------------------------
# AIAgentSessionEndedEvent
# ---------------------------------------------------------------------------


class TestAIAgentSessionEndedEvent:
    """Tests for AIAgentSessionEndedEvent."""

    def test_event_type_is_room_ended(self) -> None:
        evt = AIAgentSessionEndedEvent(
            event_id="end-001",
            timestamp="2026-04-16T07:00:00Z",
            room={"room_id": "r-2", "room_name": "Room 2"},
        )
        assert evt.event_type == "room_ended"

    def test_event_type_rejects_wrong_literal(self) -> None:
        with pytest.raises(ValidationError):
            AIAgentSessionEndedEvent(
                event_id="x",
                event_type="room_started",
                timestamp="2026-01-01T00:00:00Z",
                room={"room_id": "r", "room_name": "n"},
            )


# ---------------------------------------------------------------------------
# AIAgentSessionSummaryDoneEvent
# ---------------------------------------------------------------------------


class TestAIAgentSessionSummaryDoneEvent:
    """Tests for AIAgentSessionSummaryDoneEvent."""

    def test_event_type_is_room_summary_done(self) -> None:
        evt = AIAgentSessionSummaryDoneEvent(
            event_id="sum-001",
            timestamp="2026-04-16T08:00:00Z",
            room={"room_id": "r-3", "room_name": "Room 3"},
        )
        assert evt.event_type == "room_summary_done"

    def test_metadata_populated(self) -> None:
        evt = AIAgentSessionSummaryDoneEvent(
            event_id="sum-002",
            timestamp="2026-04-16T08:01:00Z",
            room={"room_id": "r-3", "room_name": "Room 3"},
            metadata={"transcript": "...", "tokens_used": 800},
        )
        assert evt.metadata["tokens_used"] == 800


# ---------------------------------------------------------------------------
# InternalAgentEvents enum
# ---------------------------------------------------------------------------


class TestInternalAgentEvents:
    """Tests for InternalAgentEvents enum values."""

    def test_session_started_value(self) -> None:
        assert InternalAgentEvents.SESSION_STARTED == "session_started"

    def test_session_ended_value(self) -> None:
        assert InternalAgentEvents.SESSION_ENDED == "session_ended"

    def test_room_summary_done_value(self) -> None:
        assert InternalAgentEvents.ROOM_SUMMARY_DONE == "room_summary_done"

    def test_is_str_enum(self) -> None:
        assert isinstance(InternalAgentEvents.SESSION_STARTED, str)


# ---------------------------------------------------------------------------
# SSEEvents enum
# ---------------------------------------------------------------------------


class TestSSEEvents:
    """Tests for SSEEvents lifecycle enum."""

    def test_all_values_present(self) -> None:
        expected = {
            "OPEN": "sse_open",
            "MESSAGE": "sse_message",
            "ERROR": "sse_error",
            "CLOSE": "sse_close",
            "RECONNECTING": "sse_reconnecting",
            "RECONNECTED": "sse_reconnected",
        }
        for attr, value in expected.items():
            assert getattr(SSEEvents, attr) == value

    def test_is_str_enum(self) -> None:
        assert isinstance(SSEEvents.OPEN, str)


# ---------------------------------------------------------------------------
# SSEConnectionState enum
# ---------------------------------------------------------------------------


class TestSSEConnectionState:
    """Tests for SSEConnectionState enum."""

    def test_values(self) -> None:
        assert SSEConnectionState.CONNECTING == 0
        assert SSEConnectionState.OPEN == 1
        assert SSEConnectionState.CLOSED == 2

    def test_is_int_enum(self) -> None:
        assert isinstance(SSEConnectionState.CONNECTING, int)


# ---------------------------------------------------------------------------
# Events enum — new AI agent session entries
# ---------------------------------------------------------------------------


class TestEventsAgentEntries:
    """Tests for new Events enum entries for AI agent sessions."""

    def test_ai_agent_session_started(self) -> None:
        assert Events.AI_AGENT_SESSION_STARTED == InternalAgentEvents.SESSION_STARTED

    def test_ai_agent_session_ended(self) -> None:
        assert Events.AI_AGENT_SESSION_ENDED == InternalAgentEvents.SESSION_ENDED

    def test_ai_agent_session_summary_done(self) -> None:
        assert (
            Events.AI_AGENT_SESSION_SUMMARY_DONE
            == InternalAgentEvents.ROOM_SUMMARY_DONE
        )

    def test_routing_key_matches_internal_agent_event(self) -> None:
        """Dispatch routing keys must match InternalAgentEvents values."""
        assert Events.AI_AGENT_SESSION_STARTED.value == "session_started"
        assert Events.AI_AGENT_SESSION_ENDED.value == "session_ended"
        assert Events.AI_AGENT_SESSION_SUMMARY_DONE.value == "room_summary_done"
