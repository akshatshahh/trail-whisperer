#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-birdnet.txt
.venv/bin/python scripts/setup_birdnet.py
(cd frontend && npm ci && npm run build)
ollama pull gemma3n || ollama pull gemma3:4b
ollama pull gemma3:4b
ollama pull nomic-embed-text
.venv/bin/python scripts/check_models.py
printf '\nReady. Run: bash scripts/start.sh\n'
