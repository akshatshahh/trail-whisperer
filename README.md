# Trail Whisperer

**A trail ends. The wonder stays.** An offline trail companion and a memory book for Hacktoberfest 2026 · Touch Grass.

Act I: listen to a bird or photograph a plant, save the discovery, put the phone away. Act II: at home, revisit a timeline, grow a lifelist, explore species field notes and search your own encounters.

## What runs where

Phone → local hotspot → laptop FastAPI → **BirdNET / Ollama on that same laptop** → SQLite. No cloud inference and no cloud SDKs in identification, Q&A or journal summarization. All model assets must be downloaded before leaving home. The PWA caches the app shell, not inference: the laptop must remain reachable.

At home only, **Sync at home** sends records and their media to your configured basecamp. The same code with `MODE=basecamp` uses MongoDB Atlas when configured, otherwise SQLite. Wikipedia supplies reference summaries; local Gemma supplies field notes; local nomic-embed-text supplies embeddings. ElevenLabs transcription is an explicitly requested, online-only, optional basecamp step. It is the sole third-party AI hook requested by the brief; it cannot run in trail mode.

### Verified model choice

Ollama's installed `gemma3n` build exposes **completion only**, not vision. Use it for Q&A and field notes, and **`gemma3:4b` for photographs** (`OLLAMA_VISION_MODEL`). Both remain local. If the 3n pull fails, set `OLLAMA_MODEL=gemma3:4b`. Never use a `:cloud` model.

BirdNET uses the official [BirdNET-Analyzer](https://github.com/birdnet-team/BirdNET-Analyzer) V2.4 package in an isolated subprocess. ffmpeg converts incoming phone recordings to 48 kHz mono WAV, capped at five seconds. Candidates are deduplicated, sorted and limited to three with confidence ≥ 0.5. The UI always lists available alternatives; it does not fabricate alternatives below the threshold. No confident result is an honest empty result. Model downloads are disabled in the runtime worker.

**License correction:** current official Analyzer source is MIT, and V2.4 model weights are CC BY-NC-SA 4.0, not Apache-2.0. Review the [upstream license](https://github.com/birdnet-team/BirdNET-Analyzer#license) before commercial use. Gemma is open weights under the Gemma terms.

## Reproduce in approximately 15 minutes

Requires Python 3.12, Node 22+, [Ollama](https://ollama.com), and enough disk/RAM for Gemma (3n ~7.5 GB download; 3 4B ~3.3 GB). Initial downloads and CPU speed can exceed 15 minutes on slow hardware/connections. No Atlas or ElevenLabs keys needed.

1. In one terminal, start a strictly local model server:
   ```sh
   OLLAMA_NO_CLOUD=1 OLLAMA_HOST=127.0.0.1:11434 ollama serve
   ```
   If Ollama is already running, quit that instance before starting this one.
2. In the project directory, while online:
   ```sh
   bash scripts/bootstrap.sh
   cp -n .env.example .env
   ```
   This installs dependencies, downloads BirdNET models/labels into `birdnet_models/`, pulls Ollama models, checks real text/vision/embedding inference and builds React. imageio-ffmpeg includes a local ffmpeg executable if a system binary is unavailable. Downloading is setup, never a trail action.
3. Start the app:
   ```sh
   bash scripts/start.sh
   ```
   Open [localhost:8000](http://localhost:8000). Swagger is at `/docs`. On desktop the memory book is the first view; on small screens field mode opens first.
4. Connect the laptop to the phone hotspot; find its assigned address:
   ```sh
   ipconfig getifaddr en0
   ```
   If empty, check System Settings → Wi-Fi → Details → TCP/IP, or `networksetup -listallhardwareports` to find the correct interface. Open `http://<laptop-ip>:8000` on the phone. Permit the local network connection in your OS firewall if prompted.
5. Set your trail name, select a five-second bird clip or take a plant photo, inspect the candidates, and save. Optional location and field notes attach to each find. One trip is created per local calendar day and laptop. Records and uploaded media live in `data/` and survive restarts. Back up that directory.

### Phone capture, GPS and offline Wi-Fi: important reality checks

Plain HTTP on a LAN IP is **not a secure browser context**. Browsers normally block `getUserMedia`, geolocation and service workers there. The HTTP field UI therefore offers an audio file picker and camera file capture (`capture=environment`). You can identify those files entirely over local Wi-Fi without internet. Use the phone's recorder for 3–5 second clips. Unsupported HEIC photos should be exported as JPEG.

For live five-second microphone capture, GPS and PWA installation, use **trusted local HTTPS**. Before the trip, install `mkcert` using its official setup, create a local CA and a certificate for the actual laptop IP, install and trust that CA on the phone (iOS also needs full trust in Settings → General → About → Certificate Trust Settings), then start:

```sh
mkcert -install
mkcert -cert-file /tmp/trail-cert.pem -key-file /tmp/trail-key.pem <laptop-ip> localhost 127.0.0.1
bash scripts/start.sh --ssl-certfile /tmp/trail-cert.pem --ssl-keyfile /tmp/trail-key.pem
```

Open `https://<laptop-ip>:8000` and grant microphone/location permissions. Do not bypass certificate warnings; establish trust correctly. Hotspot IP changes require a new certificate. GPS may take longer without assisted location; absence of a fix never blocks saving. Some phones disable hotspot with cellular/airplane mode off/on combinations. If the phone cannot keep a hotspot without internet, use a disconnected Wi-Fi router or laptop-hosted Wi-Fi. Verify that the LAN stays reachable after removing upstream connectivity.

## Airplane-mode acceptance procedure

Prepare all assets while online, then restart backend and Ollama so counters start at zero. Disconnect internet/upstream cellular while keeping a working phone↔laptop LAN. Do not click Sync at home.

```sh
curl http://localhost:8000/api/health
curl -F file=@/path/to/bird.wav http://localhost:8000/api/identify/audio
curl -F file=@/path/to/plant.jpg http://localhost:8000/api/identify/photo
curl -H 'Content-Type: application/json' -d '{"question":"What birds did I see today?"}' http://localhost:8000/api/ask
curl http://localhost:8000/api/health
```

Expect real identifications and `cloud_calls_this_session: 0`. Save both discoveries using the phone UI. Restart the backend; sightings must remain. Use your OS network monitor to corroborate offline behavior: the counter counts app cloud requests, not a packet audit of unrelated OS apps. Explicit sync increments the counter even in `MODE=trail`; it is an at-home action. A fresh backend session resets the counter for the next outing.

## Basecamp, sync and enrichment

### Local basecamp without keys

Run a second instance on the **same laptop**, with its own storage directory:

```sh
MODE=basecamp DATA_DIR=data-basecamp SYNC_TOKEN=choose-a-long-random-token \
  .venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

Set `BASECAMP_URL=http://localhost:8001` and the same `SYNC_TOKEN` in the trail `.env`, restart the trail backend, and click Sync at home once online. Both services share the local Ollama daemon. Without Atlas, the memory book still works and similarity search uses local cosine similarity over the exact same embeddings. Basecamp species enrichment needs internet for Wikipedia; if disconnected, profiles/embeddings may be incomplete but sightings persist.

### Render deployment

Push this repository to your Git provider and create a Render Blueprint from `render.yaml`. **No deployment or paid resources are created by this repository alone.** Configure:

- `MONGODB_URI`: Atlas connection string with a user scoped to `trail_whisperer`. Allow Render's outbound addresses in Atlas network access.
- `SYNC_TOKEN`: the same strong secret on the laptop and basecamp. Never put it in frontend source.
- `ELEVENLABS_API_KEY`: optional, for explicit transcription only.

The Docker image builds the frontend and BirdNET assets. Its entrypoint runs **Ollama on the same Render machine**, loopback-only, cloud-disabled, and prepares local Gemma/embedding models. Render cannot reach your laptop's localhost. An ordinary free web service is insufficient: the blueprint proposes a paid 8 GB-class service and a persistent disk for media/models. Confirm the current plan availability and cost before deploying. CPU generation can be slow and concurrent requests contend for RAM. Use `OLLAMA_MODEL=gemma3:4b` if memory is limited; you can also set that in the blueprint. Models download once onto the persistent disk. Health means the API is live, not that all models are ready.

Set the laptop's `BASECAMP_URL=https://<your-render-service>.onrender.com`. `/api/sync` sends one sighting with its media at a time. Basecamp acknowledges only after storage; local `synced` becomes true only for acknowledged IDs. Retries are idempotent. Background enrichment builds species summaries/field notes and adds each sighting's embedding; `enrichment_status=pending` survives failures. Retry after models/connectivity recover:

```sh
curl -X POST -H 'X-Sync-Token: YOUR_TOKEN' https://YOUR_BASECAMP/api/enrich
```

The three Atlas collections are `sightings`, `species`, `trips`. In Atlas create a **Vector Search** index on `sightings`, named `sighting_embeddings`, using `scripts/atlas-vector-index.json` (768 dimensions, cosine). Wait until ready. Then `/api/similar?query_text=oak%20woodland%20bird` returns related synced encounters. MongoDB stores metadata/embeddings; uploaded media are on the Render disk, so keep that disk backed up. Deploy as a personal journal on a trusted/private service; this hackathon app does not supply multi-user account isolation. The ingest/enrichment/transcription endpoints require the token; ordinary journal reads and local capture routes do not.

## API

- `POST /api/identify/audio`, `POST /api/identify/photo`: multipart `file`; result includes local media path. Save selected identity with `POST /api/sightings`.
- `GET/POST /api/sightings`: sighting records (species, scientific, kind, trip_id, trail_name, lat/lon, timestamp, confidence, media paths, note, synced).
- `POST /api/ask`: `{question, lat?, lon?}`; local time and today's discoveries supply context.
- `POST /api/voicenote`: multipart audio, optional note; stores locally as a journal entry.
- `POST /api/voicenote/transcribe`: basecamp only, token header, `{sighting_id}`; optional ElevenLabs transcription then local Gemma summary.
- `POST /api/sync`: explicit at-home push from trail; `POST /api/sync/ingest`: basecamp receive, authenticated.
- `POST /api/enrich`: authenticated, retry pending enrichment.
- `GET /api/species`, `GET /api/species/{name}`: profile and your encounters.
- `GET /api/similar?query_text=...`: basecamp semantic text search. Image-query search is deferred.
- `GET /api/trips`, `GET /api/stats`, `GET /api/health`.

Voice transcription is wired at the API level; the field UI stores voice notes and plays them back. Leaflet tiles are deferred: saved GPS points link to online OpenStreetMap. A silent interface walkthrough at `frontend/public/demo.mp4` shows the verified bird/flower fixtures in isolated test storage. It is embedded in How it works and is not a physical trail recording. Replace it with your submission recording and rebuild. No sample sightings are seeded into your actual journal.

## Validation

```sh
.venv/bin/pip install pytest
.venv/bin/python -m pytest -q
(cd frontend && npm run build)
.venv/bin/python scripts/check_models.py
```

The test suite covers durable storage, daily trips, lifelist counts, API media contracts, missing optional keys, trail-mode blocking, idempotent ingest/enrichment, semantic fallback and failed-sync recovery. Mocked inference tests verify wiring, not model accuracy. See `VALIDATION.md` for real model checks and outstanding physical/cloud acceptance tests.
