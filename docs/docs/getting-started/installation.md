# Installation

## Requirements

- Python 3.13 or higher

## Using pip

```bash
pip install mezon-sdk
```

## Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer.

```bash
uv pip install mezon-sdk
```

## Using Poetry

```bash
poetry add mezon-sdk
```

## Dependencies

The SDK automatically installs these dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| pydantic | >=2.12.3 | Data validation and settings |
| aiohttp | >=3.9.0 | Async HTTP client |
| websockets | >=12.0 | WebSocket protocol |
| protobuf | >=6.33.2 | Protocol Buffers serialization |
| pyjwt | >=2.8.0 | JWT token handling |
| aiosqlite | >=0.20.0 | Async SQLite for message caching |
| mmn-sdk | ==1.0.1 | Token transfer support |
| aiolimiter | >=1.2.1 | WebSocket send rate limiting |
| tenacity | >=9.1.2 | Retry handling |

## Development Installation

To contribute or develop with the SDK:

```bash
# Clone the repository
git clone https://github.com/phuvinh010701/mezon-sdk-python.git
cd mezon-sdk-python

# Install with dev dependencies
uv pip install -e ".[dev]"
```

## Verify Installation

```python
import mezon
print(mezon.__version__)
```

## Next Steps

Once installed, head to the [Quick Start](quickstart.md) guide to build your first bot.
