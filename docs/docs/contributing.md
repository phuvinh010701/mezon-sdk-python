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
