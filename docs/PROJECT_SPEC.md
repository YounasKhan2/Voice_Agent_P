# Voice Agent Migration Spec (Flask + Django)

## Summary
Migrate the current real-time Voice Agent system to use a fully isolated Flask (Jinja) frontend and a Django backend (REST + WebSockets via Channels), while keeping the exact runtime behavior: browser publishes microphone to LiveKit, server-side agent joins the same room, LLM generates responses, TTS plays back to the browser, and transcripts/speaking events stream in real time.

Current: React + Vite frontend, FastAPI backend, LiveKit Agents pipeline (Silero VAD → OpenAI STT → GPT-4o-mini → OpenAI TTS).
Target: Flask (templates) + Django (DRF + Channels). LiveKit remains the real-time media plane.

## Goals
- Keep UX and behavior identical to current app (feature parity).
- Replace React SPA with Flask-rendered pages (Jinja templates), fully isolated from React code.
- Replace FastAPI with Django for REST and WebSockets, or allow FastAPI to be removed after parity.
- Preserve LiveKit-based audio streaming and Agent pipeline.
- Maintain the same event payloads and endpoint semantics.

## Non‑Goals
- Changing the AI model or the voice pipeline stages.
- Introducing new product features beyond parity (history, auth, etc.), unless noted as optional.
- Tight coupling Flask and Django into a single process (keep them deployable independently).

## Deliverables
- Flask app: templates (HTML), static assets (CSS/JS), routes for UI pages.
- Django app: REST endpoints (/health, /token, /session), Channels consumer for /ws/transcript/{session_id}, ported AgentManager.
- Docs: Requirements, Design, Tasks, and run instructions.

## System Context
```
Browser (Flask-served HTML/CSS/JS)
  ├─ REST:   GET /token, POST /session, DELETE /session/{id}  → Django (DRF)
  ├─ WS:     /ws/transcript/{session_id}                      → Django (Channels)
  └─ WebRTC: connect/publish mic/subscribe agent audio        ↔ LiveKit Server

Django (ASGI)
  ├─ Mints LiveKit JWT tokens
  ├─ Starts/stops LiveKit Agent sessions (ported AgentManager)
  └─ Broadcasts transcripts/speech events over WebSocket

LiveKit
  ├─ Media transport for browser and agent participants
  └─ Room/track management, Opus codec, adaptive bitrate
```

## Interfaces (Contracts)
- REST
  - GET /health → { status: "ok" }
  - GET /token?room=<room>&identity=<id>&name=<optional> → { token: string }
  - POST /session { room, identity, system_prompt? } → { session_id: string }
  - DELETE /session/{session_id} → { stopped: true }

- WebSocket: /ws/transcript/{session_id}
  - Server → Client messages (JSON):
    - { role: "user" | "agent", text: string, final: boolean }
    - { role: "user" | "agent", event: "speech_started" | "speech_ended" }

- LiveKit
  - Browser connects to ENV-configured LIVEKIT_URL with token
  - Publishes microphone; subscribes to agent audio track
  - Agent connects with server-minted token, subscribes to user audio, publishes TTS

## Data Shapes
- TokenResponse: { token: string }
- SessionStartRequest: { room: string, identity: string, system_prompt?: string }
- SessionStartResponse: { session_id: string }
- SessionStopResponse: { stopped: boolean }
- TranscriptEvent (WS):
  - Interim: { role: "user", text: string, final: false }
  - Final: { role: "user"|"agent", text: string, final: true }
  - Speech: { role: "user"|"agent", event: "speech_started"|"speech_ended" }

## Assumptions
- LiveKit server is reachable from browser and backend.
- OpenAI API key is available for STT/LLM/TTS.
- Windows dev environment (PowerShell) is used for local setup.
- HTTPS/WSS required in production for mic access and secure sockets.

## Constraints
- Low latency target: end-to-end response ≈ 6–8 seconds (pipeline-bound).
- WebSocket is the only push channel for transcripts/events.
- CORS/CSRF must be configured for cross-origin Flask → Django in dev.

## Risks & Mitigations
- Cross-origin issues: Configure CORS in Django; use same-origin in prod.
- Audio autoplay policies: call room.startAudio() on a user gesture.
- Session cleanup leaks: ensure stop path cancels tasks and disconnects agent.
- Channels scaling: use Redis channel layer in multi-worker deployments.

## Acceptance Criteria
- Flask UI can start/stop a conversation and mirror the current React UX.
- Django REST returns valid tokens; session lifecycle works reliably.
- WS streams interim/final transcripts and speech events in real time.
- Agent audio plays back via LiveKit, and the user’s mic is published.
- Stop action tears down WS, LiveKit connection, and server session cleanly.
