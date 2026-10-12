# Validation · October 11, 2026

Implemented and committed both acts: local trail capture/identification and the basecamp memory book. The app is available at http://localhost:8000 while the local server runs.

## Passed

- Production React/Vite build, with app-shell PWA caching.
- Eight regression tests: durable SQLite records/daily trips, stats/lifelist, media API contracts, missing optional keys, trail-mode online-action blocking, idempotent ingest/enrichment, failed-sync recovery, offline voice storage, and BirdNET settings-CSV exclusion/threshold/deduplication/top-three ordering.
- Real Gemma 3n text inference; real Gemma 3 4B image inference; real nomic-embed-text embedding (768 dimensions).
- Real official BirdNET V2.4 inference on the first five seconds of its own soundscape fixture: **Black-capped Chickadee, 0.8141 confidence**.
- Real HTTP plant-photo endpoint on a TensorFlow flower dataset photo: **Rose (Rosa spp.)**, with uncertainty about exact species and a caution. Not a poison-oak accuracy benchmark.
- Health before/after real audio, photo and trail Q&A: **0 cloud calls**. Models were local; internet was available on the machine, so this is not yet the physical airplane-mode test.
- Two isolated live local services: identify → save → sync media + records → real Wikipedia API summary → local Gemma field notes → local embeddings → semantic search. Both species completed enrichment, the lifelist reached 2, related text search returned the bird sighting, and the trail records survived a backend restart.
- Browser checks at desktop and 390-pixel phone breakpoints. Populated timeline, lifelist, species profile and stats rendered from the verified fixtures. Fixtures remain in isolated storage; the actual journal is empty.
- A 20-second silent interface walkthrough is embedded in How it works. It shows test fixtures, not a field expedition.
- Real Atlas connection verified with TLS certificate validation using the trusted certifi CA bundle. Four sightings, four species profiles and one trip migrated with user approval; local copies retained. Live basecamp reads Atlas successfully.
- Atlas `sighting_embeddings` index verified READY and queryable. All four migrated sightings have embeddings. A related text query returned HTTP 200 with the Atlas search engine.

Machine-readable evidence: [docs/validation.json](docs/validation.json). The full local integration proof (including generated field notes) is retained in the ignored data/integration-1791756084/proof.json. Screenshots are in docs/demo-frames/ and docs/field-preview.jpg.

## Pending acceptance checks

- **Physical phone + disconnected internet:** requires the user's phone and a working local Wi-Fi network. Trusted local HTTPS is needed for browser microphone, GPS and PWA; plain HTTP supports file capture. Follow README's airplane-mode procedure.
- **Render media transfer:** deployment is live; frontend/health, sync authentication and Atlas semantic search returned HTTP 200. Existing local photo/audio transfer to the deployed persistent disk has not been verified. CPU inference can be slow.
- **Hosted ElevenLabs transcription:** the complete local basecamp endpoint transcribed a generated seven-second test recording with ElevenLabs, then summarized it with local Gemma (HTTP 200). Render has a key configured, but full hosted transcription has not been tested. Personal voice notes were untouched.
- **Fifteen-minute reproduction:** guide and bootstrap are supplied; not independently timed on a stranger's machine. Model downloads can exceed the target on a slow connection.

## Scoped omissions

Online Leaflet maps are replaced with coordinate links; image-query semantic search is deferred (text search works). Voice transcription is exposed through the API, while the UI stores and plays notes. No multi-user authentication is included; use a private/trusted basecamp for your personal journal.

## Source fixtures

BirdNET's soundscape: https://github.com/birdnet-team/BirdNET-Analyzer/blob/main/birdnet_analyzer/example/soundscape.wav

Flower photo: TensorFlow flower_photos archive, roses/14810868100_87eb739f26_m.jpg, https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz (dataset license/attribution remain with the upstream archive).

## Additional mobile/offline regression run

- **15 automated tests pass:** eight backend tests plus seven new photo-flow tests. Frontend production build passes.
- A 390 × 844 browser completed real plant-image upload → local Gemma identification (Rose) → save → page reload. Document/content widths both measured 390 px; no horizontal overflow.
- An isolated server denied non-loopback DNS and TCP connections. Its deliberate external probe was blocked. Identification, Q&A and saving triggered no additional denied attempts and health remained at zero cloud calls. Ollama was independently running with `OLLAMA_NO_CLOUD=true`; BirdNET's worker disallows runtime network downloads.
- Real BirdNET identified Black-capped Chickadee at 0.8141 confidence through that server. Real Gemma Q&A used the saved sightings.
- Two saved fixture sightings and their media persisted across a real test-server restart. Production journal and Atlas were untouched.
- All observed image/script/style/manifest URLs in the tested phone page were local paths. Browser-wide internet was not disabled; the backend network policy and page asset inspection are the limits of this simulation.
- Screenshot: `docs/offline-mobile.jpg`. Repeatable commands: `scripts/offline_server.py` and `scripts/check_offline.py`. Detailed local proof is retained in ignored `data/offline-regression-proof.json`.
- A physical phone hotspot/airplane-mode test and actual native camera capture are still unverified.

## Sentry and SerpApi implementation

Eight additional regressions pass, bringing the total to 23 (16 backend/integration + 7 frontend). Real Sentry SDK envelopes were captured in-memory: agent/model spans include token counts and failures while excluding tested secret values and journal content. Trail mode does not initialize Sentry even when a DSN is supplied. SerpApi tests verify trail blocking, token authorization, missing keys, seven-day caching, link filtering, safe provider errors and preservation of Wikipedia/embeddings during an optional provider failure. The build passes.

Both new providers still require credentials and real external verification. They are implemented, not yet counted as demonstrated sponsor entries. `scripts/check_sponsors.py` performs a synthetic-data live test when keys are supplied; confirm Sentry dashboard receipt separately.

Sentry follow-up: a synthetic real local-Gemma trace was sent to the configured project and ingestion returned HTTP 200. Render still reports Sentry disabled; deployed environment setup and dashboard receipt remain to be confirmed. No prompts, credentials or private journal records were included in the trace.

SerpApi follow-up: a real public-species search returned three reference links and local Gemma generated sourced field notes. The combined sponsor check flushed research/model traces to Sentry using temporary SQLite data; no personal journal records were accessed or changed. Render still reports both sponsors disabled until its environment settings are updated.
