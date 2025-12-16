# Voice Agent – Design

This design describes how to implement an isolated Flask frontend and a Django backend (DRF + Channels) that preserves the current behavior of the React + FastAPI system.

## Architecture Overview

```
Flask (UI / Templates)
  ├─ Routes: /, /chat, /history (optional)
  ├─ Templates: base.html, chat.html
  └─ Static JS: voice-agent.js (LiveKit + REST + WS)

Django (ASGI)
  ├─ DRF Endpoints: /health, /token, /session
  ├─ Channels: WS /ws/transcript/{session_id}
  ├─ AgentManager: Ported from FastAPI version
  └─ Optional: Django ORM models for Session/Transcript

LiveKit Server
  └─ Real-time media transport (WebRTC)
```

## Key Components

- Flask Jinja Templates
  - Render UI that mirrors current React UX (room/identity/prompt controls, transcript pane, speaking indicators, start/stop buttons).
  - Include a single JS bundle that performs the interaction flow.

- Frontend JS (voice-agent.js)
  - Get token → connect LiveKit → publish mic → start session → open WS → render updates.
  - DOM updates for interim/final transcripts and speaking badges.
  - Cleanup on stop/unload (close WS, disconnect LiveKit, remove audio elements).

- Django REST (DRF)
  - /token: Mint LiveKit JWT using API key/secret and target room/identity.
  - /session (POST): Start AgentSession; return session_id.
  - /session/{id} (DELETE): Stop AgentSession and disconnect from room.

- Django Channels (WebSocket)
  - Consumer binds clients to a session-specific group.
  - AgentManager is provided a broadcaster callback that group-sends transcript and speech events.

- AgentManager (ported)
  - Build AgentSession with: silero.VAD, openai.STT, openai.LLM("gpt-4o-mini"), openai.TTS.
  - Register event handlers to emit identical payloads as current system.
  - Manage background task lifecycle and room connection via LiveKit SDK.

## Sequence (Start Conversation)

```
User clicks Start (Flask page)
1) JS → Django: GET /token?room=&identity=
2) JS → LiveKit: connect(url, token); publish microphone
3) JS → Django: POST /session { room, identity, system_prompt }
4) JS → Django WS: connect /ws/transcript/{session_id}
5) Django → Agent: join room with agent token; start AgentSession
6) Agent → Events: user_speech_started/ended, user_input_transcribed, conversation_item_added, agent_speech_started/ended
7) Django WS → Browser: broadcast transcript/speech events
8) Agent TTS → LiveKit: publish audio track; browser plays
```

## Sequence (Stop Conversation)

```
User clicks Stop
1) JS → Django: DELETE /session/{session_id}
2) Django: stop AgentSession, cancel task, disconnect agent
3) JS: close WS, disconnect LiveKit, remove audio elements, reset UI
```

## Folder Structure (proposed)

```
root/
├─ django_backend/
│  ├─ manage.py
│  ├─ config/ (settings.py, urls.py, asgi.py)
│  ├─ api/ (views.py, serializers.py, urls.py)
│  ├─ channels_app/ (consumers.py, routing.py)
│  ├─ agent_manager/ (agent.py, livekit_utils.py)
│  └─ requirements.txt
│
└─ flask_frontend/
   ├─ app.py
   ├─ templates/ (base.html, chat.html)
   ├─ static/
   │  ├─ css/style.css
   │  └─ js/voice-agent.js
   └─ requirements.txt
```

## Configuration & Environment

- LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
- OPENAI_API_KEY
- SYSTEM_PROMPT (default)
- CORS_ORIGINS (include Flask origin in dev)
- DJANGO_ALLOWED_HOSTS (prod)
- CHANNEL_LAYERS (Redis URL for Channels in prod)

## Error Handling

- Wrap LiveKit connections and agent start in try/except; return informative HTTP errors (JSON).
- In WS consumer, drop dead sockets and continue broadcasting to remaining clients.
- On agent failure, emit a final error event to the WS group (optional) and auto-stop session.

## Logging & Observability

- Structured logs for: token requests, session start/stop, agent connect/disconnect, WS joins, and errors.
- Optional: request ID correlation between REST and WS for a session.

## Testing Strategy

- Unit: serializers, token minting, simple consumer tests.
- Integration: fake LiveKit (where possible) or connect to a dev instance; run start/stop flows.
- E2E manual: Launch Flask + Django and verify parity with current React + FastAPI behavior.

## Deployment

- Dev: Flask on :5173 or :5000; Django ASGI on :8000; LiveKit reachable; CORS open to Flask origin.
- Prod: Serve Flask and Django behind HTTPS reverse proxy; Django Channels with Redis; lock CORS to same-origin; use wss:// for WS.

## Alternatives Considered

- Keep FastAPI for the agent and make Django a proxy. Rejected for extra moving parts.
- Use Flask-SocketIO for WS. Rejected to centralize backend concerns in Django.

## Risks & Mitigations

- Cross-origin friction → configure CORS; prefer same-origin in prod.
- Audio autoplay denial → call startAudio() after a user gesture.
- Channels scaling → Redis; ensure sticky sessions if needed at the proxy.
