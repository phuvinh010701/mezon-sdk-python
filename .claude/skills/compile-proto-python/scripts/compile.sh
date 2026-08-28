#!/usr/bin/env bash
set -euo pipefail

# Move to project root (repo root of mezon-sdk-python, four levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
cd "$PROJECT_ROOT"

# The .proto source files live in the separate public repo:
# https://github.com/mezonai/mezon-protocol
# Default to a sibling checkout of this repo; override with PROTO_REPO if yours lives elsewhere.
PROTO_REPO="${PROTO_REPO:-$PROJECT_ROOT/../mezon-protocol}"

if [ -d "$PROTO_REPO/.git" ]; then
  echo "Updating mezon-protocol at $PROTO_REPO..."
  git -C "$PROTO_REPO" fetch origin main
  git -C "$PROTO_REPO" checkout main
  git -C "$PROTO_REPO" pull origin main
else
  echo "Cloning mezon-protocol into $PROTO_REPO..."
  git clone --branch main https://github.com/mezonai/mezon-protocol "$PROTO_REPO"
fi

OUT_DIR="mezon/protobuf"
mkdir -p "$OUT_DIR"

echo "Compiling protos → $OUT_DIR"

protoc \
  --python_out="$OUT_DIR" \
  --mypy_out="$OUT_DIR" \
  --proto_path="$PROTO_REPO" \
  rtapi/realtime.proto \
  api/api.proto

# Fix absolute import injected by protoc so it resolves inside the package
REALTIME_PB2="$OUT_DIR/rtapi/realtime_pb2.py"
sed -i '' \
  's|from api import api_pb2 as api_dot_api__pb2|from mezon.protobuf.api import api_pb2 as api_dot_api__pb2|g' \
  "$REALTIME_PB2"

echo "Done. Generated files:"
ls -lh \
  "$OUT_DIR/api/api_pb2.py" \
  "$OUT_DIR/api/api_pb2.pyi" \
  "$OUT_DIR/rtapi/realtime_pb2.py" \
  "$OUT_DIR/rtapi/realtime_pb2.pyi"
