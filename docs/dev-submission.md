Suggested title: No Signal, Still Curious: I Built an Offline AI Trail Companion

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 1: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05).*

## What I Built

A bird calls above you. A plant catches your eye. You take a photo, promise to look it up later, and eventually lose it among hundreds of other pictures.

I built **Trail Whisperer** to give those discoveries somewhere to live: an offline-first trail companion and personal memory book for curious walkers and beginner birders.

Capture a photo or short bird recording, review the AI identification suggestion, save the moment, and keep exploring. Back home, browse your discovery timeline, species collection, trips, and encounter statistics.

The goal is a short interaction with the screen that helps you notice more outside.

Offline means a prepared laptop runs the backend and downloaded AI models, while your phone connects to it over local Wi-Fi. That network needs no upstream internet, but the laptop must remain reachable. Installing the web app alone does not install inference on the phone.

## Demo

{% youtube yq-PGzqCRfs %}

The video is an AI-assisted product showcase made with app screenshots. The retained Squirrel and Kingfisher photos are clearly labeled demo data, not verified wildlife encounters.

**This is a local application; there is no public hosted website.** GitHub contains the source and reproducible setup instructions. After setup, open `http://localhost:8000` on the laptop, or its LAN address on your phone.

[Local setup and offline testing instructions](https://github.com/akshatshahh/trail-whisperer#reproduce-in-approximately-15-minutes)

I initially tried Render hosting, but discontinued that deployment after encountering hosting costs. The current project runs locally, and Render is not included among the categories I’m entering.

## Code

{% github akshatshahh/trail-whisperer %}

[Source, setup scripts, and regression tests](https://github.com/akshatshahh/trail-whisperer)

Credentials and personal uploads are excluded from Git.

## How I Built It

Trail Whisperer has two modes: trail and basecamp. Both can run on your own laptop.

The React interface talks to FastAPI. Ollama serves local Gemma models for questions and field notes, with Gemma 3 4B handling photos. BirdNET analyzes short bird recordings. SQLite stores discoveries, while uploaded media remain in a local data directory.

The trail path is **phone → local Wi-Fi → laptop → local models → local journal**.

The installed Gemma 3n build exposed text completion but not vision, so I used a separate local vision model rather than assuming one model could handle both tasks.

At home, an explicit sync sends records and media to a second local service: basecamp. It uses SQLite without extra keys, or MongoDB Atlas when configured. Atlas Vector Search uses locally generated `nomic-embed-text` embeddings to find related encounters.

Optional connected features run at basecamp:

- ElevenLabs transcribes saved voice notes through an authenticated endpoint; local Gemma summarizes the transcript.
- SerpApi retrieves public species reference links and snippets for sourced field notes.
- Sentry Agent Tracing records model and research timings and statuses, excluding prompts, recordings, location, and credentials from trace payloads.

These integrations remain disabled in trail mode. They need internet at basecamp; the core local workflow does not require their keys or paid web hosting.

### What I checked

The latest run passed **27 automated tests** and the production frontend build.

Real-model checks identified a rose photo and returned a Black-capped Chickadee candidate from a recording. An offline regression blocked external backend network connections while identification, saving, retrieval, and local questions continued working. Records and media survived a backend restart.

A mobile-width browser exercised the photo workflow. This was a backend-network-blocked simulation and browser layout check, not a physical phone-and-hotspot field test. The README supplies that manual acceptance procedure.

Atlas semantic search, local ElevenLabs-to-Gemma transcription, SerpApi research, and Sentry tracing were also exercised. Tests establish those workflows, not identification accuracy for every species.

## Why Does Open Innovation Matter?

Where inference runs determines whether this app can help when connectivity disappears.

Downloadable model weights and local inference let a prepared setup identify and journal discoveries without a remote inference API. Photos and recordings stay on the local machine until the user chooses to sync.

The modular setup also lets me replace models, inspect outputs, adjust prompts, and improve the recording pipeline. I can adapt the application around its users and hardware.

There are tradeoffs: advance downloads, CPU latency, and a reachable laptop. Gemma has its own model terms, and BirdNET weights have separate licensing requirements. Those constraints are documented rather than hidden behind an offline label.

## My Agent Session

I used Codex to help implement the application, troubleshoot deployment, and add regression coverage. Incremental repository commits document the implementation and fixes.

## Prize Categories

- **Best Use of Gemma:** local photo identification, questions, summaries, and field notes.
- **Best Use of MongoDB Atlas:** optional synced journal storage and vector search over encounter embeddings.
- **Best Use of ElevenLabs:** basecamp voice-note transcription.
- **Best Use of Sentry Agent Tracing:** observability for model and research workflows.
- **Best Use of SerpApi:** species research with public reference links.

Notice something. Learn a little. Save the memory. Keep exploring.
