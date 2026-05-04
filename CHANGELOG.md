# CHANGELOG

<!-- version list -->

## v1.8.0 (2026-05-03)

### Features

- Upgrade reflect 2.8.46 ts sdk
  ([`d0c5075`](https://github.com/phuvinh010701/mezon-sdk-python/commit/d0c50751b9827af6d6ad6732b043efdfdf6acbf8))

### Refactoring

- Remove binary perf compare, add unit test, test cov
  ([`9de4256`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9de425693fe9069666b45878894bbc8b61d11bb2))


## v1.7.2 (2026-05-01)

### Bug Fixes

- Close message db, avoid keep event loop
  ([`94d36fc`](https://github.com/phuvinh010701/mezon-sdk-python/commit/94d36fcfe853374ad67e6202263e52d7090efa5c))

### Chores

- **deps**: Bump pydantic from 2.12.5 to 2.13.2
  ([`b4e3833`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b4e3833ef9a89d4ff30459d07c6be7a2d3692183))

- **deps**: Bump pydantic from 2.13.2 to 2.13.3
  ([`643b1af`](https://github.com/phuvinh010701/mezon-sdk-python/commit/643b1af800c14bd1ea45650c202a347ebe562256))

- **deps**: Update mkdocs requirement from >=1.5.0 to >=1.6.1
  ([`3fbe143`](https://github.com/phuvinh010701/mezon-sdk-python/commit/3fbe1433e08fc2e1b868bfa606b98e0a371a65de))

- **deps**: Update mkdocs-material requirement from >=9.5.0 to >=9.7.6
  ([`8c4b0a5`](https://github.com/phuvinh010701/mezon-sdk-python/commit/8c4b0a5b07dfddd27b23ae7281aa2f64bbe19864))

- **deps-dev**: Bump fastapi from 0.135.3 to 0.136.0
  ([`742c4e4`](https://github.com/phuvinh010701/mezon-sdk-python/commit/742c4e4b8839df9e34d69f8db5671a3c0acc091f))

- **deps-dev**: Bump fastapi from 0.136.0 to 0.136.1
  ([`33ba137`](https://github.com/phuvinh010701/mezon-sdk-python/commit/33ba137639a144593762c6e382b4133102af527f))

- **deps-dev**: Bump ruff from 0.15.10 to 0.15.11
  ([`b9736f9`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b9736f9bbe5f84dea745282f67451481d797dd20))

- **deps-dev**: Bump ruff from 0.15.11 to 0.15.12
  ([`8d2863d`](https://github.com/phuvinh010701/mezon-sdk-python/commit/8d2863d8b62ab59ba8791d62e5709a8ba1fa7b81))

### Continuous Integration

- **deps**: Bump actions/checkout from 4 to 6
  ([`6b362f9`](https://github.com/phuvinh010701/mezon-sdk-python/commit/6b362f90fcfcb28ea8a75f32bde9dbe6df90cd6d))

- **deps**: Bump actions/setup-python from 5 to 6
  ([`3efe4af`](https://github.com/phuvinh010701/mezon-sdk-python/commit/3efe4afe98969fee195db3d2a87c910474a88e02))

- **deps**: Bump astral-sh/setup-uv from 5 to 7
  ([`9d465f5`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9d465f57be5c7bbfd7c2e235cd328f9f96add6fb))

### Documentation

- Update document relate to new ts sdk
  ([`f594a76`](https://github.com/phuvinh010701/mezon-sdk-python/commit/f594a76102cb8e348697695623e1777d19ce8a49))


## v1.7.1 (2026-04-20)

### Bug Fixes

- Allow partial user profile update payloads
  ([`9170fe2`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9170fe2683cb43ff41dcd23139c773c7393b26e9))


## v1.7.0 (2026-04-16)

### Bug Fixes

- Address code review items #1-3
  ([`a701cb6`](https://github.com/phuvinh010701/mezon-sdk-python/commit/a701cb6bc06e1773ce97a9c166de0362794b0e40))

- Resolve conflict
  ([`4b68bfe`](https://github.com/phuvinh010701/mezon-sdk-python/commit/4b68bfe1448df7ff6b7fd0d3f2f8046a1437c572))

- Resolve integration test failures
  ([`3bef172`](https://github.com/phuvinh010701/mezon-sdk-python/commit/3bef172dacbd657ae9c0374de9a604ce84502539))

### Chores

- Bump version to 1.6.22 and update CHANGELOG
  ([`c8436b9`](https://github.com/phuvinh010701/mezon-sdk-python/commit/c8436b991b72d62ab77877a47287b3400f46cdd5))

- Update mezon-sdk version to 1.6.22 and clean up test files by removing unnecessary blank lines
  ([`ccc87d9`](https://github.com/phuvinh010701/mezon-sdk-python/commit/ccc87d998e3bbad9d93d6b7893462c6d9552a826))

### Continuous Integration

- Add GitHub Actions workflow to run unit tests on PR to dev
  ([`7606b8c`](https://github.com/phuvinh010701/mezon-sdk-python/commit/7606b8cba213955ad295c099da02ead2ba717245))

- Add uv caching and use --frozen flag
  ([`a2c1974`](https://github.com/phuvinh010701/mezon-sdk-python/commit/a2c19749305df54b1612e0a966f37480f89facfa))

- Inject Mezon secrets as env vars in test step
  ([`b055b48`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b055b483932fcb2046d17f40ee12c9a4c3979263))

### Features

- Sync with mezon-sdk-js v2.8.44
  ([`397c936`](https://github.com/phuvinh010701/mezon-sdk-python/commit/397c936c7c43264a021c644604dd98520b2817e9))

### Testing

- Add unit tests for SSE/AI agent models and enums (v2.8.44)
  ([`3675f0b`](https://github.com/phuvinh010701/mezon-sdk-python/commit/3675f0b2452754e8fcc51c546d240aa06fedffb3))


## v1.6.22 (2026-04-16)

### Bug Fixes

- Correct mention s/e index computation for multiple mentions
  ([`8096252`](https://github.com/phuvinh010701/mezon-sdk-python/commit/8096252f0cb7a98589ea79c5e673b90a56ebcb73))

### Chores

- **deps**: Bump aiohttp from 3.13.3 to 3.13.4
  ([`db786a3`](https://github.com/phuvinh010701/mezon-sdk-python/commit/db786a30da5d7e3812db4d4dc481707a4ce47c6e))

- **deps**: Bump aiohttp from 3.13.4 to 3.13.5
  ([`0c96e73`](https://github.com/phuvinh010701/mezon-sdk-python/commit/0c96e73a8c735ca567d4321719a7b2d6cee7b99d))

- **deps**: Bump protobuf from 7.34.0 to 7.34.1
  ([`340287c`](https://github.com/phuvinh010701/mezon-sdk-python/commit/340287cb465251cee15237326dfcc997295df918))

- **deps**: Bump pyjwt from 2.11.0 to 2.12.1
  ([`48e7277`](https://github.com/phuvinh010701/mezon-sdk-python/commit/48e7277ea9e406ad64e62d455a2561daeae4ce6d))

- **deps-dev**: Bump build from 1.4.0 to 1.4.2
  ([`b13e207`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b13e2078c845c3d2924d9afd27135c11b3072fa4))

- **deps-dev**: Bump build from 1.4.2 to 1.4.3
  ([`52e5a31`](https://github.com/phuvinh010701/mezon-sdk-python/commit/52e5a312a552890138519122b03d6c88cff38233))

- **deps-dev**: Bump fastapi from 0.135.1 to 0.135.2
  ([`6610ce2`](https://github.com/phuvinh010701/mezon-sdk-python/commit/6610ce24b0bee43924039753b61d27bd0746b4a2))

- **deps-dev**: Bump fastapi from 0.135.2 to 0.135.3
  ([`57a7127`](https://github.com/phuvinh010701/mezon-sdk-python/commit/57a71271efb771749985d186f5e8a293b21469e1))

- **deps-dev**: Bump pytest from 9.0.2 to 9.0.3
  ([`aef32f5`](https://github.com/phuvinh010701/mezon-sdk-python/commit/aef32f59dc19f64dff70e8fcd2177add4b1b22d3))

- **deps-dev**: Bump ruff from 0.15.5 to 0.15.6
  ([`cb86034`](https://github.com/phuvinh010701/mezon-sdk-python/commit/cb8603409100d95c3e4ae2c45236ce979e5018cd))

- **deps-dev**: Bump ruff from 0.15.6 to 0.15.7
  ([`b6e78e9`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b6e78e937e8434cd6fb04f0b01225a3c19106611))

- **deps-dev**: Bump ruff from 0.15.7 to 0.15.8
  ([`57e6a80`](https://github.com/phuvinh010701/mezon-sdk-python/commit/57e6a80fdb7b3dd0beedbecb22b234b3c04723e2))

- **deps-dev**: Bump ruff from 0.15.8 to 0.15.9
  ([`3773106`](https://github.com/phuvinh010701/mezon-sdk-python/commit/3773106e1a457aa5ea183de5e239cbf953da468a))

- **deps-dev**: Bump ruff from 0.15.9 to 0.15.10
  ([`d0630dc`](https://github.com/phuvinh010701/mezon-sdk-python/commit/d0630dc79c862358e61722cc58e918b4216318bb))

- **deps-dev**: Bump uvicorn from 0.41.0 to 0.42.0
  ([`00b2e8c`](https://github.com/phuvinh010701/mezon-sdk-python/commit/00b2e8c89f50ae25bf8216e3cc6a92d8ab36b2cd))

- **deps-dev**: Bump uvicorn from 0.42.0 to 0.44.0
  ([`9e0672a`](https://github.com/phuvinh010701/mezon-sdk-python/commit/9e0672a9bb3793723f3786190c3c391f2819075f))

### Refactoring

- **tests**: Eliminate magic numbers and promote mention helper
  ([`6883eb1`](https://github.com/phuvinh010701/mezon-sdk-python/commit/6883eb14951b96bff078a0736cdc267c983fe188))


## v1.6.21 (2026-03-11)

### Bug Fixes

- Update channel event handling and model definitions
  ([`b544983`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b544983e0a3d5d29f03c3996ba3793c4032a7346))


## v1.6.20 (2026-03-11)

### Bug Fixes

- Decode message ref, message attachment, message mentions
  ([`e74f7f1`](https://github.com/phuvinh010701/mezon-sdk-python/commit/e74f7f1c631d05623c7a1264132ec0097b2a285f))

- Decode message ref, message attachment, message mentions
  ([`e69b70e`](https://github.com/phuvinh010701/mezon-sdk-python/commit/e69b70e4d96b746276c6c265e06c633b53163774))

### Chores

- **deps**: Bump protobuf from 6.33.5 to 7.34.0
  ([`38402d5`](https://github.com/phuvinh010701/mezon-sdk-python/commit/38402d553b7d13bc5c25b6285f60041c54eee743))

- **deps-dev**: Bump fastapi from 0.129.0 to 0.131.0
  ([`c1e0e1e`](https://github.com/phuvinh010701/mezon-sdk-python/commit/c1e0e1e83f36f7a63bda7f61fb3ea57e68c15b8f))

- **deps-dev**: Bump fastapi from 0.131.0 to 0.135.1
  ([`f1675a0`](https://github.com/phuvinh010701/mezon-sdk-python/commit/f1675a094b6ea4dc1257c7d3c0bdae5e81988c50))

- **deps-dev**: Bump python-dotenv from 1.2.1 to 1.2.2
  ([`e66222d`](https://github.com/phuvinh010701/mezon-sdk-python/commit/e66222d9971b1ebe97d688bf388118d493d0277b))

- **deps-dev**: Bump ruff from 0.15.1 to 0.15.2
  ([`d55a58b`](https://github.com/phuvinh010701/mezon-sdk-python/commit/d55a58bbb6b0573c1f038db5e875f16caeb38dde))

- **deps-dev**: Bump ruff from 0.15.2 to 0.15.4
  ([`b0961e8`](https://github.com/phuvinh010701/mezon-sdk-python/commit/b0961e89975323c1a34197850bd077878f7f5b16))

- **deps-dev**: Bump ruff from 0.15.4 to 0.15.5
  ([`44aee69`](https://github.com/phuvinh010701/mezon-sdk-python/commit/44aee6974f237cec3c84451711008860461c4b7f))

- **deps-dev**: Bump uvicorn from 0.40.0 to 0.41.0
  ([`24e167e`](https://github.com/phuvinh010701/mezon-sdk-python/commit/24e167e458e2ab8dccdbcde31641ff7ea179393c))


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
