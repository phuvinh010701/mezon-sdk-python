# Mezon SDK Development Guide

## Quick References
- **Coding Conventions**: .claude/coding_conventions.md - Type annotations and code style conventions
- **CRITICAL**: After ANY Python code changes, **ALWAYS** run lint - this is mandatory and must never be skipped.
- **Always** use uv instead of pip
- **NEVER** change `pyproject.toml` directly when add/remove package, use uv command instead

## Build and Development Commands

```bash
uv pip install -e ".[dev]"

# Lint
uv run ruff check . --fix
uv run run ruff format 
```

## Architecture Overview

The SDK is an async-first Python implementation of the Mezon TypeScript SDK for building bots and applications on the Mezon platform (community/collaboration platform with clans, channels, DMs, voice, and token transfers).

### Core Components

```
MezonClient (mezon/client.py)
├── SessionManager (mezon/managers/session.py)
│   └── Session (mezon/session.py) - JWT token management
├── SocketManager (mezon/managers/socket.py)
│   ├── Socket (mezon/socket/socket.py) - WebSocket connection
│   ├── WebSocketAdapterPb - Protobuf message handling
│   └── MessageBuilders - Message construction utilities
├── ChannelManager (mezon/managers/channel.py)
├── EventManager (mezon/managers/event.py)
├── CacheManager[Clan, TextChannel, User]
└── MessageDB (mezon/messages/db.py) - SQLite persistence
```

### Key Flows

**Authentication**: `client.login()` → `SessionManager.authenticate()` → `MezonApi` HTTP call → JWT token extraction → Socket connection
**Message Sending**: `channel.send()` → `SocketManager.write_chat_message()` → `Socket.MessageBuilder` → WebSocket send → MessageDB save
**Incoming Messages**: WebSocket receive → `EventManager.emit()` → Default handlers (cache/DB update) → User handlers (fire-and-forget)

## Important Directories

| Directory | Purpose |
|-----------|---------|
| `mezon/client.py` | Main entry point (MezonClient) |
| `mezon/api/` | HTTP API client (MezonApi) |
| `mezon/socket/` | WebSocket layer, message builders |
| `mezon/managers/` | Session, Socket, Channel, Event, Cache managers |
| `mezon/structures/` | Domain objects (Clan, TextChannel, User, Message) |
| `mezon/protobuf/` | Generated protobuf messages (excluded from ruff) |
| `mezon/models.py` | Pydantic API models |
