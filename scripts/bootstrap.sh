#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-birdnet.txt
.venv/bin/python scripts/setup_birdnet.py
(cd frontend && npm ci && npm run build)
if ! ollama pull "${OLLAMA_MODEL:-gemma3n}"; then
  ollama pull gemma3:4b
  export OLLAMA_MODEL=gemma3:4b
  if [ ! -f .env ]; then cp .env.example .env; fi
  .venv/bin/python -c "from dotenv import set_key; set_key('.env', 'OLLAMA_MODEL', 'gemma3:4b')"
fi
ollama pull gemma3:4b
ollama pull nomic-embed-text
.venv/bin/python scripts/check_models.py
printf '\nReady. Run: bash scripts/start.sh\n'
