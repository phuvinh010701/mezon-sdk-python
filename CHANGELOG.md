# CHANGELOG

<!-- version list -->

## v1.6.19 (2026-02-18)

### Bug Fixes

- Streamline session initialization in MezonClient and update ApiSession model to use optional
  fields
  ([`8992b49`](https://github.com/phuvinh010701/mezon-sdk-python/commit/8992b4951152e731b3fe20382ff545ccf87b1047))


## v1.6.18 (2026-02-18)

### Bug Fixes

- Enhance URL handling in MezonClient and related modules by introducing build_url function and
  updating session management
  ([`2ef41fb`](https://github.com/phuvinh010701/mezon-sdk-python/commit/2ef41fbf016cef6238284d11d57d9c958709fa36))


## v1.6.17 (2026-02-18)

### Bug Fixes

- Remove retry decorator from init_all_dm_channels and add it to connect_socket for improved error
  handling
  ([`0e81975`](https://github.com/phuvinh010701/mezon-sdk-python/commit/0e8197517fea57dbae2c67a08c6536b1fe34b840))


## v1.6.16 (2026-02-17)

### Bug Fixes

- Add retry mechanism in MezonClient for improved error handling
  ([`31c2d8c`](https://github.com/phuvinh010701/mezon-sdk-python/commit/31c2d8cd0ff47c4c2152267e0449821ee5909c71))

### Chores

- Add protobuf dependency to pyproject.toml and update uv.lock for consistency
  ([`839053d`](https://github.com/phuvinh010701/mezon-sdk-python/commit/839053d70807c2132a645a5f6eb017e1bb17f6f6))

- Remove version from __init__.py in version_toml for streamlined version management
  ([`a0dc9e5`](https://github.com/phuvinh010701/mezon-sdk-python/commit/a0dc9e5bc43edccf0a7a98cd164ecca5fed6eb88))

- Update version_toml format in pyproject.toml for improved clarity
  ([`5108a1e`](https://github.com/phuvinh010701/mezon-sdk-python/commit/5108a1e4dc02459684d83267eef79eac61e60a7c))

- Update version_toml in pyproject.toml to include version from __init__.py for better version
  management
  ([`6d49f74`](https://github.com/phuvinh010701/mezon-sdk-python/commit/6d49f74366efa67d8b51085171ba9d6a40310c97))


## v1.6.15 (2026-02-16)

### Bug Fixes

- Standardize variable names in ApiMessageRef and TextChannel models for consistency
  ([`cfda2aa`](https://github.com/phuvinh010701/mezon-sdk-python/commit/cfda2aa6d7eb48156ad346e85e02cd78834db8c3))

### Chores

- Add pre-commit hook for automated code checks and formatting with ruff
  ([`3979233`](https://github.com/phuvinh010701/mezon-sdk-python/commit/3979233dede19f957d21a09a24868af42aadfb23))

- **deps-dev**: Bump ruff from 0.14.10 to 0.15.1
  ([`46d1337`](https://github.com/phuvinh010701/mezon-sdk-python/commit/46d133781bdde3506681aececb66976ead330498))

### Refactoring

- Enhance Pydantic model structure by introducing MezonBaseModel for protobuf conversion support and
  streamline session expiration checks
  ([`deacc56`](https://github.com/phuvinh010701/mezon-sdk-python/commit/deacc569d12f35c4ec4f88824fa7c467f2c2d8c0))

- Remove unused friend management and transaction detail methods from MezonClient for cleaner code
  ([`dfe5622`](https://github.com/phuvinh010701/mezon-sdk-python/commit/dfe5622564417ed6c5ff0b67d167677871a0577b))

- Reorganize imports and enhance structure in Mezon SDK for improved readability and maintainability
  ([`7e73fac`](https://github.com/phuvinh010701/mezon-sdk-python/commit/7e73fac97346b232fbf25e16de89d3f490e0bc38))

- Reorganize imports in Mezon SDK to improve clarity and maintainability
  ([`d6b125b`](https://github.com/phuvinh010701/mezon-sdk-python/commit/d6b125b888f856c1c0f3e8e3b39bb05a81c5ef9f))

- Reorganize imports in Mezon SDK to improve clarity and maintainability
  ([`a875fc4`](https://github.com/phuvinh010701/mezon-sdk-python/commit/a875fc4a7722261a06d050f1e04c696c1146bce9))

- Simplify response handling in MezonApi by removing redundant type checks
  ([`9aca08b`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9aca08b94a89db346ff74412c181cbc94f82a2fe))


## v1.6.14 (2026-02-15)

### Bug Fixes

- Add user_ids parameter to MezonApi for enhanced request handling
  ([`de70885`](https://github.com/phuvinh010701/mezon-sdk-python/commit/de70885cc1b00cf1d8517e3341b87d2ae9d4f9cf))

- **deps**: Bump pyjwt from 2.10.1 to 2.11.0
  ([`42a9a31`](https://github.com/phuvinh010701/mezon-sdk-python/commit/42a9a31505d2641634851cf9e7f42fa5fb9e8818))

- **deps**: Bump tenacity from 9.1.2 to 9.1.4
  ([`0457bbc`](https://github.com/phuvinh010701/mezon-sdk-python/commit/0457bbcca485e1fc8bd5fc375f9365859b40fd10))

- **deps**: Bump websockets from 15.0.1 to 16.0
  ([`828bc99`](https://github.com/phuvinh010701/mezon-sdk-python/commit/828bc9961877d7cbcaa3dbca2911aec6d784119e))

- **deps-dev**: Bump fastapi from 0.128.0 to 0.129.0
  ([`0a8c7b1`](https://github.com/phuvinh010701/mezon-sdk-python/commit/0a8c7b19732de43da3f3093d10a4fa9691eb0b7f))

- **deps-dev**: Bump protobuf from 6.33.2 to 6.33.5
  ([`24b9cfb`](https://github.com/phuvinh010701/mezon-sdk-python/commit/24b9cfb1ee3cf5ed2135ee30e9bfbde60979b387))

### Chores

- Add dependabot configuration for tracking uv and GitHub Actions dependencies
  ([`105e76c`](https://github.com/phuvinh010701/mezon-sdk-python/commit/105e76cfe490594dd3ab120e40714dd4153ec29f))

- Update dependabot commit message prefix from fix to chore for consistency
  ([`32e0d6f`](https://github.com/phuvinh010701/mezon-sdk-python/commit/32e0d6f6062e5f66718ae4ff16bb616ca1433c61))

### Continuous Integration

- **deps**: Bump actions/checkout from 4 to 6
  ([`7b21033`](https://github.com/phuvinh010701/mezon-sdk-python/commit/7b21033ab618d1d261f90899ce94f1d586809680))

- **deps**: Bump actions/setup-python from 5 to 6
  ([`4e8877a`](https://github.com/phuvinh010701/mezon-sdk-python/commit/4e8877aa77f8864b529991c5a76a6bdeb63a1e76))

- **deps**: Bump astral-sh/setup-uv from 3 to 7
  ([`9cb146e`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9cb146e9c98ebbb4729f22c57bb68ca8229880e6))

### Refactoring

- Improve reconnection logic in MezonClient with enhanced error handling and configurable retry
  parameters
  ([`50c2ffc`](https://github.com/phuvinh010701/mezon-sdk-python/commit/50c2ffceae76f6652710313b1c1b4151a0e62787))


## v1.6.13 (2026-02-14)

### Bug Fixes

- Add AI agent enabled event handler to MezonClient and update event enums
  ([`b2f1123`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b2f1123990267376922df4116e2a763137bf875c))

- Enhance MezonClient and MezonApi with ApiQuickMenuAccess integration and update type annotations
  for improved clarity
  ([`72ffb95`](https://github.com/phuvinh010701/mezon-sdk-python/commit/72ffb95d7ee5bfe050bb33b998011731d90b4060))


## v1.6.12 (2026-02-08)

### Bug Fixes

- Add 'text/plain' to BINARY_CONTENT_TYPES for improved content handling
  ([`9773836`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9773836c085362b6fcd2bc2c12e233a62364e819))

- Update content type handling in parse_response to default to 'text/plain; charset=utf-8' for
  improved response parsing
  ([`92ed19a`](https://github.com/phuvinh010701/mezon-sdk-python/commit/92ed19afbf55c192bbd5add036b6782195ae879b))

- Update write_ephemeral_message method to accept multiple receiver IDs as a list for improved
  message handling
  ([`cc82b85`](https://github.com/phuvinh010701/mezon-sdk-python/commit/cc82b85618c63fddddf7a2dfc03e7a75b2c5fe8f))

### Chores

- Update documentation links in README to reflect new URL structure
  ([`b59f9c7`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b59f9c7036c20720afe44b4ba32122572afa8402))

### Refactoring

- Format __init__ method in MezonApi for improved readability
  ([`da24aef`](https://github.com/phuvinh010701/mezon-sdk-python/commit/da24aef012e1ed51a3f86872d24616ee9052665e))

- Remove default notification handler from MezonClient to simplify event processing
  ([`9d70604`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9d706047d0a8ab6194109ca5a7300fd3646de8af))

- Update default parameter values in list_channel_voice_users method for consistency and clarity
  ([`6155854`](https://github.com/phuvinh010701/mezon-sdk-python/commit/61558541e1ac9ef502fb14c68b519bf749dd8c68))

- Update default parameter values in list_clans_descs method for consistency and clarity
  ([`3878cbd`](https://github.com/phuvinh010701/mezon-sdk-python/commit/3878cbd500cc9321fd5f3a12f2681c14d6d832b1))


## v1.6.11 (2026-02-03)

### Bug Fixes

- Update type annotations in MezonClient and MezonApi to support str | int for client_id and bot_id,
  improve handling of IDs, and adjust related methods for consistency
  ([`94303de`](https://github.com/phuvinh010701/mezon-sdk-python/commit/94303ded449e26ff12421975a59d2ae812606458))

### Chores

- Add documentation workflow with MkDocs, create initial documentation structure, and include
  changelog and examples
  ([`2871e8a`](https://github.com/phuvinh010701/mezon-sdk-python/commit/2871e8a46189291a30c5a337cf94cc11a8712aa4))


## v1.6.10 (2026-02-02)

### Bug Fixes

- Update MezonClient and MezonApi to enhance quick menu access handling, improve type annotations,
  and streamline protobuf usage
  ([`8a08df7`](https://github.com/phuvinh010701/mezon-sdk-python/commit/8a08df7b87e417fb5a4186c647821f40ca3aa5ab))


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
