# Changelog

All notable changes to the Mezon SDK Python.

## v1.6.2 (2025-12-03)

### Bug Fixes

- Execute default handler first before user handlers

## v1.6.1 (2025-12-03)

*Maintenance release*

## v1.6.0 (2025-12-03)

### Features

- Add interactive message structures (ButtonBuilder, InteractiveBuilder)
- Add methods for clan and notification management

## v1.5.3 (2025-11-30)

### Bug Fixes

- Get zkproof using id_token for improved security

## v1.5.2 (2025-11-17)

### Bug Fixes

- Add rate limiting to WebSocket adapter
- Enhance message handling with update and reaction features
- Improve rate limiting in message queue

### Dependencies

- Added `aiolimiter` for rate limiting

## v1.5.1 (2025-11-05)

### Bug Fixes

- Enhance friend management
- Improve role handling

## v1.5.0 (2025-11-04)

### Features

- **Token Sending** - Integrate MMN and ZK clients
- Add `send_token()` method to MezonClient
- Automatic ZK proof generation for transactions

### Bug Fixes

- Enhance event handling with unified handler invocation

## v1.4.1 (2025-11-04)

### Bug Fixes

- Enhanced event handling with unified handler invocation

## v1.4.0 (2025-11-03)

### Features

- Implement `on_channel_created` event handler

## v1.3.0 (2025-11-01)

### Features

- **Caching** - Add caching and database support
- SQLite-based message caching with `aiosqlite`
- `MessageDB` class for message persistence

## v1.2.0 (2025-10-31)

### Features

- Enhance socket management
- Improve event handling

## v1.1.0 (2025-10-31)

### Features

- Add Apache 2.0 license
- Update project configuration

## v1.0.0 (2025-10-31)

### Initial Release

- Async/await native implementation
- WebSocket real-time messaging
- Event-driven architecture
- Protocol Buffers support
- Type-safe with Pydantic models
- Channel and clan management
- Message sending and receiving
- User management
