# Changelog

All notable changes to the Mezon SDK Python.

## Unreleased

### Performance

- Close temporary/replaced `MezonApi` clients to stop HTTP session leaks
- Bound background socket tasks, lock DB connect, and expire raw streams
- Use `MessageToDict` instead of a `MessageToJson` round-trip for protobuf message conversion
- Pre-partition event handlers by kind instead of re-filtering on every emit
- De-duplicate in-flight cache fetches and make cache eviction a real LRU
- Scope the rate limiter per client instance and cache clan list lookups
- Make event-emit debug logging lazy
- Stop rebuilding `User` cache entries on every incoming message
- Enable SQLite WAL journal mode and `NORMAL` synchronous for `MessageDB`
- Reuse a single `aiohttp.ClientSession` per `MezonApi` instance

## v1.8.1 (2026-05-06)

### Bug Fixes

- Fix typo in `ChannelMessage` sender avatar field

## v1.8.0 (2026-05-03)

### Features

- Sync with mezon-sdk-js v2.8.46

### Other

- Add unit tests and coverage reporting; remove the binary perf comparison tooling

## v1.7.2 (2026-05-01)

### Bug Fixes

- Close the message DB properly so it no longer keeps the event loop alive

## v1.7.1 (2026-04-20)

### Bug Fixes

- Allow partial user profile update payloads

## v1.7.0 (2026-04-16)

### Features

- Sync with mezon-sdk-js v2.8.44
- Add AI Agent SSE support: `agent_event_url`, `connect_ai_agent_sse()` / `disconnect_ai_agent_sse()`, and the `AI_AGENT_*` events

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
