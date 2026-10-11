#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -d frontend/dist ]; then (cd frontend && npm ci && npm run build); fi
exec .venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}" "$@"
