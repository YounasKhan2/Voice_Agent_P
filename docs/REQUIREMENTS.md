# Voice Agent – Requirements

This document captures functional and non-functional requirements for migrating to a Flask (Jinja) frontend and a Django backend (DRF + Channels), preserving the current system’s behavior.

## Functional Requirements

1) Token Minting
- The backend exposes GET /token to return a LiveKit JWT for a given room and identity.
- The token grants room_join for the specified room.

2) Session Lifecycle
- POST /session starts a server-side agent session bound to a room and returns a session_id.
- DELETE /session/{session_id} stops the session, disconnects agent, frees resources.

3) Real-time Transcripts and Events
- The backend exposes WS /ws/transcript/{session_id} to broadcast:
  - Interim transcripts: { role: "user", text, final: false }
  - Final transcripts:   { role: "user"|"agent", text, final: true }
  - Speech events:       { role: "user"|"agent", event: "speech_started"|"speech_ended" }

4) Flask UI (Isolated)
- Serves server-rendered pages (Jinja):
  - /chat – main voice interaction page
  - optional / – landing page, /history – if persistence is enabled
- Static JS implements the flow currently in React:
  - GET /token → connect to LiveKit → publish mic
  - POST /session → connect WS → render transcripts/events
  - Stop → DELETE /session → close WS → disconnect LiveKit

5) LiveKit Media
- Browser connects directly to LiveKit using the minted token.
- Publishes microphone and subscribes to agent audio.

6) Agent Pipeline (Parity)
- AgentSession with:
  - VAD: Silero
  - STT: OpenAI STT
  - LLM: OpenAI GPT-4o-mini
  - TTS: OpenAI TTS
- Emits the same events as today.

7) Optional Persistence
- (Optional) Save sessions and transcripts in Django models.
- Expose a read-only /transcripts/{session_id} endpoint for history.

## Non-Functional Requirements

- Performance: End-to-end response ≈ 6–8 seconds typical.
- Availability: Single-node dev acceptable; prod must support multiple workers.
- Scalability: Channels with Redis layer for multi-instance WS.
- Security:
  - CORS allow-listed for dev (Flask origin); locked down in prod (same-origin).
  - HTTPS/WSS in production; secure handling of API keys.
- Privacy: Don’t log raw audio; redact secrets from logs.
- Observability: Basic structured logs for session start/stop and errors.
- Compatibility: Latest Chrome/Edge; recent Firefox and Safari preferred.
- Dev Experience: Windows-friendly scripts and instructions (PowerShell).

## External Dependencies

- LiveKit server (URL, API key/secret)
- OpenAI API key (STT/LLM/TTS)
- Python 3.10+
- Django, DRF, Channels (ASGI), optional Redis for channel layer
- Flask (templates), Jinja2

## Environment Variables

- LIVEKIT_URL
- LIVEKIT_API_KEY
- LIVEKIT_API_SECRET
- OPENAI_API_KEY
- SYSTEM_PROMPT (default fallback)
- DJANGO_ALLOWED_HOSTS (prod)
- CORS_ORIGINS (dev; include Flask origin)
- CHANNEL_LAYERS (Redis URL, production)

## Acceptance Tests (High-level)

- Start Flow:
  - Flask page loads; clicking Start fetches a token, connects to LiveKit, publishes mic, starts session, opens WS.
  - Agent greets; agent audio audible; interim and final transcripts visible; speaking indicators toggle.
- Stop Flow:
  - Stop button deletes session; WS closes; LiveKit disconnects; UI resets.
- Resilience:
  - Closing the tab or disconnecting network cleans up server session within reasonable timeout.
- Multiple Sessions:
  - Two different identities/rooms can converse simultaneously without cross-talk.
