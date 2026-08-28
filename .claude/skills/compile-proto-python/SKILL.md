---
name: compile-proto-python
description: Compile .proto files in this project into Python stubs using protoc. Use when the user asks to compile, regenerate, or build proto files, mentions protobuf, .proto, or wants to update the generated Python files (api_pb2.py, realtime_pb2.py).
---

# Compile Proto → Python

Regenerates Python protobuf bindings for this project.

## Source of the .proto files

The `.proto` definitions do **not** live in this repo. They live in the separate public repo
[mezon-protocol](https://github.com/mezonai/mezon-protocol) (`rtapi/realtime.proto`, `api/api.proto`).
The compile script clones/updates a checkout of that repo (default: sibling directory
`../mezon-protocol` next to this repo; override with the `PROTO_REPO` env var) and reads the
`.proto` files from there. It does **not** touch this repo's own git branch/checkout — only
`mezon-protocol`'s `main` branch is fetched/pulled.

## Proto targets

Output root (inside this repo): `mezon/protobuf/`

| Proto file (in `mezon-protocol`) | Generated files (in `mezon-sdk-python`) |
|---|---|
| `api/api.proto` | `mezon/protobuf/api/api_pb2.py`, `…api_pb2.pyi` |
| `rtapi/realtime.proto` | `mezon/protobuf/rtapi/realtime_pb2.py`, `…realtime_pb2.pyi` |

After compilation the script patches the import in `realtime_pb2.py`:

```python
# before (protoc default)
from api import api_pb2 as api_dot_api__pb2

# after (patched)
from mezon.protobuf.api import api_pb2 as api_dot_api__pb2
```

## Compile

Run the compile script from anywhere (it cd's into the SDK project root itself, then
clones/pulls the `mezon-protocol` repo before compiling):

```bash
bash .claude/skills/compile-proto-python/scripts/compile.sh
```

Or run the steps manually from the `mezon-sdk-python` project root:

```bash
PROTO_REPO=../mezon-protocol   # or wherever you keep it; cloned automatically if missing
if [ -d "$PROTO_REPO/.git" ]; then
  git -C "$PROTO_REPO" fetch origin main && git -C "$PROTO_REPO" checkout main && git -C "$PROTO_REPO" pull origin main
else
  git clone --branch main https://github.com/mezonai/mezon-protocol "$PROTO_REPO"
fi
OUT=mezon/protobuf
mkdir -p "$OUT"
protoc --python_out="$OUT" --mypy_out="$OUT" --proto_path="$PROTO_REPO" rtapi/realtime.proto api/api.proto
sed -i '' 's|from api import api_pb2 as api_dot_api__pb2|from mezon.protobuf.api import api_pb2 as api_dot_api__pb2|g' "$OUT/rtapi/realtime_pb2.py"
```

## Prerequisites check

If the command fails, verify the required tools are installed:

```bash
which protoc           # Protocol Buffers compiler
pip show grpcio-tools  # alternative: python -m grpc_tools.protoc
pip show mypy-protobuf # provides --mypy_out plugin
```

### Install missing tools

```bash
# protoc (macOS)
brew install protobuf

# mypy-protobuf plugin
pip install mypy-protobuf

# grpcio-tools (alternative compiler)
pip install grpcio-tools
```

## Verify output

After compiling, the generated files should be updated:

```bash
ls -lh mezon/protobuf/api/api_pb2.py mezon/protobuf/api/api_pb2.pyi mezon/protobuf/rtapi/realtime_pb2.py mezon/protobuf/rtapi/realtime_pb2.pyi
```
