# Trail Whisperer

**A trail ends. The wonder stays.** An offline trail companion and a memory book for Hacktoberfest 2026 · Touch Grass.

Act I: listen to a bird or photograph a plant, save the discovery, put the phone away. Act II: at home, revisit a timeline, grow a lifelist, explore species field notes and search your own encounters.

**Local application:** http://localhost:8000 (after setup) · **Source:** [GitHub](https://github.com/akshatshahh/trail-whisperer) · **Evidence:** [VALIDATION.md](VALIDATION.md)

There is no public hosted website. GitHub hosts the source code; run the application on your own laptop. For offline trail use, open the laptop's LAN address on your phone as described below. Optional online integrations can run from a local basecamp service when connected.

## Technologies and sponsor integrations

- **Gemma:** `gemma3n` for trail Q&A, field notes and journal summaries; `gemma3:4b` for vision. Ollama serves downloaded open-weight models locally on your laptop. No Google/Gemini API key is used.
- **MongoDB Atlas:** `sightings`, `species` and `trips` collections store basecamp records. Atlas Vector Search uses local `nomic-embed-text` embeddings (768 dimensions, cosine). The index and real search results have been verified.
- **ElevenLabs:** Scribe transcription is available only through the authenticated basecamp endpoint; the transcript is summarized by local Gemma. A real seven-second synthetic recording passed the complete local endpoint with HTTP 200. The automated local check used synthetic audio rather than personal voice notes.

- **Sentry (local basecamp):** opt-in basecamp agent/model traces report model names, durations, token counts and failure statuses. Automatic SDK integrations are disabled, and request bodies, prompts, recordings, location, credentials and raw exception values are excluded. Trail mode never initializes Sentry. Real SDK envelopes are tested with an in-memory transport, and a synthetic real-Gemma trace was accepted by Sentry with HTTP 200. The project owner has also checked Sentry and confirmed it working.
- **SerpApi (local basecamp workflow verified):** basecamp searches public species names/scientific names, keeps up to three organic reference links, and feeds snippets to local Gemma for sourced field notes. Results are cached for seven days. No GPS, personal journal text or uploaded media are sent to search. Tests verify authentication, caching, safe links and redacted provider errors. A real search returned three public reference links and local Gemma generated sourced notes using isolated test data.

Other building blocks: Python 3.12, FastAPI, Uvicorn, Pydantic, HTTPX, PyMongo, certifi, python-dotenv, Pillow, python-multipart, SQLite, official BirdNET-Analyzer/TensorFlow, ffmpeg/imageio-ffmpeg, React 19, Vite, vite-plugin-pwa/Workbox, Lucide icons, browser MediaRecorder/geolocation/camera APIs, Wikipedia APIs and OpenStreetMap coordinate links. Tests use pytest, Vitest, jsdom and React Testing Library. Git/GitHub retain incremental implementation commits; development used Codex. GitHub hosting is not claimed as Copilot use.

Five partner technologies are used in the current local setup: Gemma, MongoDB Atlas, ElevenLabs, Sentry and SerpApi. Atlas and the optional online providers require connectivity at basecamp; trail inference and SQLite journaling remain local. Render hosting has been discontinued and is not claimed as a current prize category. Prize eligibility is determined by the challenge organizers.

## Photo capture and the memory book

**Identify photo** is available in the header and **Take photo** in field mode. The chooser offers phone-native camera capture, desktop webcam capture on HTTPS/localhost, and a separate image upload option. Denied/unavailable webcam access leaves upload available; camera tracks stop when the dialog closes. Review the model's description, uncertainty and caution before saving.

The memory book includes a timeline with time filters, a lifelist, species profiles with Wikipedia context and Gemma field notes, encounter dates/GPS links, trips, statistics, milestones and semantic text search. The How it works dialog embeds a 20-second interface walkthrough made from public test fixtures.

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

### Optional online integrations from local basecamp

Run basecamp on port 8001 as shown above. To use Atlas, set `MONGODB_URI` in the ignored `.env` and allow your own connection's public IP in Atlas network access. Omit the URI to keep basecamp in SQLite. Add `ELEVENLABS_API_KEY` only if you want online voice-note transcription.

Set `BASECAMP_URL=http://localhost:8001` on the trail service and the same `SYNC_TOKEN` on both services, then restart them. No paid web hosting is required. Optional providers may have their own quotas or charges; the local SQLite/model workflow needs none of their keys.

Sync sends one sighting and its media at a time. Basecamp acknowledges stored records before local sync flags change. Retries are idempotent, and local copies remain available. Retry enrichment when connected and models are ready:

```sh
curl -X POST -H 'X-Sync-Token: YOUR_TOKEN' http://localhost:8001/api/enrich
```

Atlas collections are `sightings`, `species` and `trips`. Create a Vector Search index on `sightings`, named `sighting_embeddings`, using `scripts/atlas-vector-index.json` (768 dimensions, cosine), and wait until READY. Local basecamp serves `/api/similar` using that index. Without Atlas, search uses local cosine similarity. Media live in the local basecamp data directory, so back up that directory.

Use the service as a personal journal on a trusted network: this application does not provide multi-user account isolation. Ingest, enrichment, research and transcription require the sync token; ordinary journal reads and capture routes do not.

The Dockerfile remains available for self-managed use; no hosting Blueprint is included.

## API

- `POST /api/identify/audio`, `POST /api/identify/photo`: multipart `file`; result includes local media path. Save selected identity with `POST /api/sightings`.
- `GET/POST /api/sightings`: sighting records (species, scientific, kind, trip_id, trail_name, lat/lon, timestamp, confidence, media paths, note, synced).
- `POST /api/ask`: `{question, lat?, lon?}`; local time and today's discoveries supply context.
- `POST /api/voicenote`: multipart audio, optional note; stores locally as a journal entry.
- `POST /api/voicenote/transcribe`: basecamp only, token header, `{sighting_id}`; optional ElevenLabs transcription then local Gemma summary.
- `POST /api/sync`: explicit at-home push from trail; `POST /api/sync/ingest`: basecamp receive, authenticated.
- `POST /api/enrich`: authenticated, retry pending enrichment.
- `POST /api/research`: basecamp only, token header, `{species, refresh?}`; cached SerpApi research and local Gemma notes for a synced species.
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

**27 automated tests pass:** eighteen backend/integration tests and nine frontend tests. The production build passes. Real model checks identified a Rose photograph and a Black-capped Chickadee recording (0.8141 confidence). Local sync/enrichment, Atlas semantic search and the local ElevenLabs-to-Gemma pipeline were also verified. The project owner additionally confirmed Sentry and ElevenLabs working. Mocked inference tests verify wiring, not model accuracy. See `VALIDATION.md` for automated evidence, owner-confirmed checks and test scope.

The offline regression server blocked external DNS/TCP while a 390-pixel browser uploaded, identified, saved and reloaded a plant photo. Real bird identification and Q&A also worked; records/media survived a backend restart and health stayed at zero cloud calls. This is a server-network-blocked simulation, not a physical phone hotspot test. Automated checks cover the scenarios described here; identification results should still be reviewed rather than treated as an accuracy guarantee for every species.

## Mobile/offline regression checks

Run the backend suite and the photo-flow regressions:

```sh
.venv/bin/python -m pytest -q
(cd frontend && npm test)
```

Nine frontend tests cover missing-photo fallbacks as well as phone-native capture, upload/cancellation, insecure-HTTP fallback, denied webcam permission and camera-track cleanup (including closing during permission setup).

For real local-model tests, download your sample plant image and 3–5 second bird clip **before** disconnecting. The provided check expects `data/fixtures/plant.jpg` and `data/fixtures/soundscape.wav` (source fixtures are documented in VALIDATION.md). It never downloads assets automatically. Start the isolated test server in one terminal:

```sh
.venv/bin/python scripts/offline_server.py
```

This server runs on port 8004 with temporary SQLite/media storage, no optional keys, and all external DNS/TCP connections blocked. Loopback is allowed for the already-running, cloud-disabled Ollama daemon. It does not disconnect other apps or change production records. In another terminal:

```sh
.venv/bin/python scripts/check_offline.py
```

The check performs real photo/audio identification, saves/re-reads records, serves media, runs Q&A, checks online-action gates and verifies zero cloud calls. Open `http://localhost:8004` to exercise the same flow in a phone-width browser. A width test is not a physical iOS/Android camera or hotspot test. The full manual phone/LAN procedure above remains necessary for that acceptance criterion.

## Enable Sentry and SerpApi at basecamp

Add `SENTRY_DSN` (Sentry project Settings → Client Keys/DSN) and `SERPAPI_API_KEY` (SerpApi account API Key page) to your ignored `.env` for local basecamp only. Restart the local basecamp after changing them. Neither key is needed on the trail, and neither integration activates in `MODE=trail` even if keys are present.

When configured, sync enrichment automatically researches newly encountered species. Existing species can be researched through authenticated `POST /api/research` with `{ "species": "Black-capped Chickadee" }` and the `X-Sync-Token` header. Set `refresh: true` to explicitly bypass the seven-day cache. Species profiles display the returned reference links. Missing keys, provider outages and quota errors keep the Wikipedia/local-model path functional.

For a private, synthetic-data verification run with both new settings configured:

```sh
.venv/bin/python scripts/check_sponsors.py
```

The script researches a public species in temporary SQLite storage, invokes local Gemma and flushes Sentry traces. It does not access your actual journal. To reproduce the verified Sentry check, inspect `species.research`, `gen_ai.invoke_agent`, `gen_ai.chat` and web-search spans in Sentry's trace/AI insights views. The script never prints credentials. Trace sending is included in the session cloud-call counter at basecamp. No hosted LLM provider is added by these integrations.
