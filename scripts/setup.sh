#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export UV_CACHE_DIR="${UV_CACHE_DIR:-$PWD/.cache/uv}"
export npm_config_cache="${npm_config_cache:-$PWD/.cache/npm}"
if command -v uv >/dev/null 2>&1; then
  if [ ! -x .venv/bin/python ]; then uv venv --python python3 .venv; fi
  uv pip install --python .venv/bin/python --require-hashes -r requirements.lock
else
  python3 -m venv .venv
  .venv/bin/python -m pip install --require-hashes -r requirements.lock
fi
if [ -f package-lock.json ]; then npm ci --no-audit --no-fund; else npm install --no-audit --no-fund; fi
npm run build:desktop
