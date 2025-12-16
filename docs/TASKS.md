# Voice Agent – Project Tasks

This is the actionable backlog to deliver a Flask (Jinja) frontend and a Django (DRF + Channels) backend with feature parity.

## Phase 0 – Bootstrap & Env
- [ ] Create `django_backend/` project (ASGI enabled)
- [ ] Add dependencies: django, djangorestframework, channels, python-dotenv, httpx, livekit-agents, livekit-plugins-*, openai
- [ ] Create `flask_frontend/` app with templates/static, add Flask & Jinja2
- [ ] Prepare `.env` files (LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, OPENAI_API_KEY, SYSTEM_PROMPT)

Acceptance: Both servers start (Django :8000, Flask :5173/:5000) and render basic pages.

## Phase 1 – Django REST Endpoints
- [ ] Implement GET `/health` → `{ status: "ok" }`
- [ ] Implement GET `/token` (room, identity, name?) → `{ token }`
- [ ] Implement POST `/session` → `{ session_id }`
- [ ] Implement DELETE `/session/{id}` → `{ stopped: true }`
- [ ] Wire settings for CORS to allow Flask origin in dev

Acceptance: curl or Postman can exercise all endpoints with correct responses.

## Phase 2 – Agent Manager (ported)
- [ ] Copy/port `AgentManager` from FastAPI code into `django_backend/agent_manager/agent.py`
- [ ] Build `AgentSession` with silero.VAD, openai.STT, openai.LLM("gpt-4o-mini"), openai.TTS
- [ ] Keep event hooks and payloads identical to current system
- [ ] Add start/stop lifecycle and background task handling

Acceptance: Starting a session connects an agent to the LiveKit room; stopping fully cleans up.

## Phase 3 – WebSocket (Channels)
- [ ] Add Channels consumer at `/ws/transcript/{session_id}`
- [ ] On connect: join group `{session_id}`; on disconnect: leave group
- [ ] Provide broadcaster callback to AgentManager to `group_send` transcript/speech events
- [ ] Configure ASGI routing and (optional) Redis channel layer

Acceptance: A WS client receives events as the user speaks and agent responds.

## Phase 4 – Flask Frontend (Isolated)
- [ ] Build `templates/base.html`, `templates/chat.html` (room, identity, mic, system prompt, start/stop)
- [ ] Implement `static/js/voice-agent.js`
  - [ ] GET `/token` (Django) to obtain JWT
  - [ ] Connect to LiveKit and publish mic
  - [ ] POST `/session` (Django) and open WS `/ws/transcript/{session_id}`
  - [ ] Render interim/final transcripts and speaking indicators
  - [ ] Stop flow: DELETE `/session/{id}`, close WS, disconnect LiveKit
- [ ] Style parity: copy visual layout idea; no dependency on React

Acceptance: From Flask UI, a user can hold a full voice session with live transcripts and audio.

## Phase 5 – QA & Parity Checks
- [ ] Verify interim/final transcript behavior and indicators
- [ ] Validate error handling: token failure, LiveKit connect failure, WS drops
- [ ] Confirm resource cleanup and no dangling background tasks
- [ ] Test multi-session isolation (different rooms/identities)

Acceptance: Behavior matches current React + FastAPI experience.

## Phase 6 – Optional Enhancements
- [ ] Add Django models for Session & Transcript; migrations
- [ ] Persist transcripts; add `/transcripts/{session_id}` (GET)
- [ ] `/history` page in Flask to browse sessions
- [ ] Logging improvements and metrics hooks

Acceptance: History is visible (if enabled) and data model verified.

## Runbook (Dev)
- Django (ASGI):
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  # from django_backend
  daphne -b 0.0.0.0 -p 8000 config.asgi:application
  # or: uvicorn config.asgi:application --host 0.0.0.0 --port 8000
  ```

- Flask:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  # from flask_frontend
  $env:FLASK_APP="app.py"
  flask run --host 0.0.0.0 --port 5173
  ```

## Definition of Done
- Parity demo: Flask UI + Django backend reproduces live voice conversation, transcripts, indicators, and clean stop.
- Documentation: SPEC, REQUIREMENTS, DESIGN, and TASKS are current and accurate.
