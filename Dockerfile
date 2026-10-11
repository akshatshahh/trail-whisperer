FROM node:22-bookworm-slim AS frontend
WORKDIR /ui
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl ca-certificates libsndfile1 zstd && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://ollama.com/install.sh | sh
WORKDIR /app
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-birdnet.txt
COPY backend/ backend/
COPY scripts/ scripts/
RUN python scripts/setup_birdnet.py
COPY --from=frontend /ui/dist frontend/dist/
ENV MODE=basecamp DATA_DIR=/app/data BIRDNET_DIR=/app/birdnet_models OLLAMA_NO_CLOUD=1
EXPOSE 8000
CMD ["bash", "scripts/container-start.sh"]
