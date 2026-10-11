#!/usr/bin/env bash
set -euo pipefail
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_NO_CLOUD=1
export OLLAMA_MODELS="${DATA_DIR:-/app/data}/ollama"
ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
trap 'kill "$OLLAMA_PID" 2>/dev/null || true' EXIT
# Serve immediately; enrichment is retryable while local model preparation runs.
(
  for i in {1..60}; do if ollama list >/dev/null 2>&1; then break; fi; sleep 1; done
  ollama pull "${OLLAMA_MODEL:-gemma3n}" || true
  ollama pull "${OLLAMA_VISION_MODEL:-gemma3:4b}" || true
  ollama pull nomic-embed-text || true
) > /tmp/model-setup.log 2>&1 &
# Render may set WEB_CONCURRENCY; use one process for shared local inference
# and a consistent per-session cloud-call counter.
uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1
