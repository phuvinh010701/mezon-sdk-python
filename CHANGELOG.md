# CHANGELOG

<!-- version list -->

## v1.6.9 (2026-01-27)

### Bug Fixes

- Add ApiSentTokenRequest model for token transfer requests
  ([`1560049`](https://github.com/phuvinh010701/mezon-sdk-python/commit/15600492459bdda7df1f03becb176154cdf2ee17))

### Chores

- **deps**: Update mmn-sdk dependency to version 1.0.1 and remove unused logout method from
  MezonClient
  ([`1322c19`](https://github.com/phuvinh010701/mezon-sdk-python/commit/1322c19463f4e562ad29609017cefcda7f6e0684))

### Refactoring

- Enhance MezonApi with support for protobuf-based API calls, restructure endpoints, and improve
  request handling
  ([`d84305e`](https://github.com/phuvinh010701/mezon-sdk-python/commit/d84305ea6de0c335a446a9bcfd1401264318f668))

- Remove debug print statement from MezonClient to clean up code
  ([`d78cd44`](https://github.com/phuvinh010701/mezon-sdk-python/commit/d78cd44408f404bd3d5a2883b5dd2e6878b2d0d9))

- Remove list_transaction_detail method from MezonApi to streamline code and improve maintainability
  ([`28478ac`](https://github.com/phuvinh010701/mezon-sdk-python/commit/28478aca446681b4a2f4ed4baf9809874922bdd6))

- Remove unused API request models and endpoints from MezonApi, streamline code for better
  maintainability
  ([`8516329`](https://github.com/phuvinh010701/mezon-sdk-python/commit/851632979c9c0fb8ef6009f1931643dc79013af7))

- Update MezonClient and related models to use integer type annotations for IDs, enhance protobuf
  handling, and improve dependency management
  ([`d40fa71`](https://github.com/phuvinh010701/mezon-sdk-python/commit/d40fa71329eafec8e51a7c608f07cb1933f8571f))

- Update Socket class to use protobuf-based envelope and event for clan name existence check
  ([`accd38d`](https://github.com/phuvinh010701/mezon-sdk-python/commit/accd38df40c4abaf612e2b7599795261b53f9c3a))


## v1.6.8 (2026-01-14)

### Bug Fixes

- Correct channel type assignment in ApiChannelDescription model
  ([`47fe7fb`](https://github.com/phuvinh010701/mezon-sdk-python/commit/47fe7fb1bc302e35af8c60d3ef8792d3d24b7f27))

### Chores

- **deps**: Update dependencies for build step, exclude test file after build, add test reconnect
  ([`ad9a1f5`](https://github.com/phuvinh010701/mezon-sdk-python/commit/ad9a1f519646e471063a378dbc69e595d14e5d4a))

### Refactoring

- Enhance MezonClient with improved event handler registration, update type annotations, and add
  detailed docstrings for better clarity
  ([`f79c3eb`](https://github.com/phuvinh010701/mezon-sdk-python/commit/f79c3ebf49a85217bd1b3a7975937398b1d568f7))

- Update type annotations to use built-in types, enhance coding conventions documentation, and
  adjust Ruff configuration for linting exclusions
  ([`8e99e1e`](https://github.com/phuvinh010701/mezon-sdk-python/commit/8e99e1e375a2f5ece0bec67589c0fbf2a82e4cc9))


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
