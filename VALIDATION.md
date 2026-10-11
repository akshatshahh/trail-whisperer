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
- **Render deployment:** Dockerfile/render.yaml are provided; no remote project, billing or credentials were configured. Container image build was not run here (no Docker runtime verified). Render's same-machine Ollama requires enough RAM/disk; CPU inference can be slow.
- **ElevenLabs transcription:** endpoint is gated to basecamp and authenticated; no API key was supplied, so actual transcription is untested. Offline audio storage/playback is verified.
- **Fifteen-minute reproduction:** guide and bootstrap are supplied; not independently timed on a stranger's machine. Model downloads can exceed the target on a slow connection.

## Scoped omissions

Online Leaflet maps are replaced with coordinate links; image-query semantic search is deferred (text search works). Voice transcription is exposed through the API, while the UI stores and plays notes. No multi-user authentication is included; use a private/trusted basecamp for your personal journal.

## Source fixtures

BirdNET's soundscape: https://github.com/birdnet-team/BirdNET-Analyzer/blob/main/birdnet_analyzer/example/soundscape.wav

Flower photo: TensorFlow flower_photos archive, roses/14810868100_87eb739f26_m.jpg, https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz (dataset license/attribution remain with the upstream archive).
