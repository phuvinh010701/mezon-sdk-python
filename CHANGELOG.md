# CHANGELOG

<!-- version list -->

## v1.6.7 (2026-01-05)

### Bug Fixes

- Update dependencies and enhance MezonClient with improved socket management and event handling
  ([`5df770f`](https://github.com/phuvinh010701/mezon-sdk-python/commit/5df770ff226623b384859b79fd5bab6fcc09c8da))


## v1.6.6 (2026-01-02)

### Bug Fixes

- Added support for binary protobuf responses in API calls
  ([`85da121`](https://github.com/phuvinh010701/mezon-sdk-python/commit/85da12172fec14d44b8d78f8ed41144bc7154ed5))


## v1.6.5 (2025-12-30)

### Bug Fixes

- Enhance MezonClient with additional event handlers and improve channel management logic
  ([`fe13897`](https://github.com/phuvinh010701/mezon-sdk-python/commit/fe13897f34094011ea6cf7ec0d4bce48dd1a0991))


## v1.6.4 (2025-12-11)

### Bug Fixes

- Remove MessageQueue from MezonClient and related structures; add new ApiPermission and ApiRole
  models
  ([`af66d3f`](https://github.com/phuvinh010701/mezon-sdk-python/commit/af66d3fc02798d635fdf5f1d4f7f6eb6d7f9180e))


## v1.6.3 (2025-12-09)

### Bug Fixes

- Add user caching and DM channel creation to MezonClient
  ([`c4fb221`](https://github.com/phuvinh010701/mezon-sdk-python/commit/c4fb221f43947fd02bcc07af7b8bdda50a4b2a5a))


## v1.6.2 (2025-12-03)

### Bug Fixes

- Execute default handler first
  ([`21b96fb`](https://github.com/phuvinh010701/mezon-sdk-python/commit/21b96fb27eb5de7de34daaecc5915b134a1cbebd))


## v1.6.1 (2025-12-03)


## v1.6.0 (2025-12-03)

### Features

- Add new interactive message structures and methods for clan and notification management
  ([`13cc0df`](https://github.com/phuvinh010701/mezon-sdk-python/commit/13cc0dfb47c244e88654d107608a4960742458f7))


## v1.5.3 (2025-11-30)

### Bug Fixes

- Get zkproof using id_token
  ([`cdd956a`](https://github.com/phuvinh010701/mezon-sdk-python/commit/cdd956a753800684651252610dbd62213978f0bb))


## v1.5.2 (2025-11-17)

### Bug Fixes

- Add rate limiting to WebSocket adapter and include aiolimiter dependency
  ([`30769bf`](https://github.com/phuvinh010701/mezon-sdk-python/commit/30769bfdac567d193641fdc17a6b0a4d06fba7ec))

- Enhance message handling with new update and reaction features, and improve rate limiting in
  message queue
  ([`aef2e96`](https://github.com/phuvinh010701/mezon-sdk-python/commit/aef2e96b9615e4f1e456a3b359cba2827909f34f))

### Chores

- Update README.md
  ([`b504a40`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b504a4002481af539f366e69575eaf6696fcc1d5))


## v1.5.1 (2025-11-05)

### Bug Fixes

- Enhance friend management, role handle
  ([`f350fa5`](https://github.com/phuvinh010701/mezon-sdk-python/commit/f350fa5e7531ba80433dc74e5afa0d04ae7cdd06))


## v1.5.0 (2025-11-04)

### Bug Fixes

- Enhance event handling with unified handler invocation
  ([`ae2cf2b`](https://github.com/phuvinh010701/mezon-sdk-python/commit/ae2cf2b874cc7e48a59f788d8e7145735844e059))

### Features

- Integrate MMN and ZK clients, add token sending functionality
  ([`9b26309`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9b2630903ce5fdd7fd58a3969006b7806680c400))


## v1.4.1 (2025-11-04)

### Bug Fixes

- Fix: enhance event handling with unified handler invocation
  ([`f1a9b22`](https://github.com/phuvinh010701/mezon-sdk-python/commit/f1a9b22d0fe192fa6b6e2f0d87dd8aec53da7932))


## v1.4.0 (2025-11-03)

### Features

- Implement on channel created event
  ([`9f06182`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9f06182136f7f3a4cbcac90cb8bdfe4792519e33))


## v1.3.0 (2025-11-01)

### Chores

- Remove fastapi_example.py as it is no longer needed
  ([`0644e17`](https://github.com/phuvinh010701/mezon-sdk-python/commit/0644e17da678310548c52443f158dde35ef6d55b))

### Features

- Enhance Mezon SDK with caching and database support
  ([`134a5fa`](https://github.com/phuvinh010701/mezon-sdk-python/commit/134a5fa9d97812d3c5bc93cc438ea893036fdf9c))


## v1.2.0 (2025-10-31)

### Features

- Enhance socket management, and improve event handling
  ([`a74190a`](https://github.com/phuvinh010701/mezon-sdk-python/commit/a74190a0d3a84d936ecdccc9154d184960680d45))


## v1.1.0 (2025-10-31)

### Features

- Add Apache 2.0 license and update project configuration
  ([`f4ce6ae`](https://github.com/phuvinh010701/mezon-sdk-python/commit/f4ce6ae39ec07097153e88cefca59b34a0d22118))


## v1.0.0 (2025-10-31)

- Initial Release
