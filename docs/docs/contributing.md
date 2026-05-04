# Contributing

## Development setup

```bash
git clone https://github.com/phuvinh010701/mezon-sdk-python.git
cd mezon-sdk-python
uv pip install -e ".[dev]"
```

## Tooling

Project conventions from the repo:

- use `uv` instead of `pip`
- run lint after Python code changes
- do not edit `pyproject.toml` directly to add/remove packages; use `uv` commands

## Common commands

```bash
uv run ruff check . --fix
uv run ruff format
pytest
```

## Testing socket / protobuf / login changes

Use pytest as the primary path for focused unit and regression coverage.

Start with a deterministic regression run that does not require network access:

```bash
uv run pytest tests/unit/test_socket_regressions.py
```

For a broader local sweep of unit/model tests, run:

```bash
uv run pytest tests/
```

When you need to verify real login and reconnect behavior, run the integration suite with environment variables configured:

```bash
uv run python -m tests.test_runner
```

The integration runner requires these environment variables:

- `MEZON_CLIENT_ID`
- `MEZON_API_KEY`
- `MEZON_CLAN_ID`
- `MEZON_CHANNEL_ID`
- `MEZON_USER_ID`
- `MEZON_USER_NAME`
- `MEZON_USER_ID_2`
- `MEZON_USER_NAME_2`

Use the focused regression test for protocol compatibility bugs such as `ws_url` normalization, URL building, integer `cid` handling, and safe disconnect cleanup.

## Docs structure

The documentation site is driven by:

- `docs/mkdocs.yml`
- `docs/docs/`
- top-level `README.md`

If you add a new page under `docs/docs/`, also update `docs/mkdocs.yml` navigation.

## Updating examples

When changing examples, prefer matching the current public SDK surface in:

- `mezon/client.py`
- `mezon/structures/`
- `mezon/managers/`
- `mezon/models.py`

## Validation

Before opening a PR for doc changes:

```bash
cd docs && mkdocs build --strict
```

If your change also edits Python files, run the repo lint/test commands as well.
