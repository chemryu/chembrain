#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/python ] || [ ! -d dist ]; then
  printf '먼저 ./scripts/setup.sh를 실행하세요.\n' >&2
  exit 1
fi
exec .venv/bin/python -m uvicorn server.app:app --host 127.0.0.1 --port "${CHEMBRAIN_PORT:-8000}"
