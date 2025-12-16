# Backend (FastAPI) for Voice Agent

This FastAPI app orchestrates a real-time voice AI pipeline with LiveKit Agents:

STT (Deepgram) -> LLM (Grok via OpenRouter-compatible; falls back to OpenAI) -> TTS (Cartesia; falls back to OpenAI)

It mints LiveKit access tokens for the browser client and starts/stops agent sessions.

## Endpoints
- GET /health: health check
- GET /token?room=<room>&identity=<id>: mint a LiveKit client token
- POST /session: start an agent session in a room
- DELETE /session/{session_id}: stop an agent session
- WS /ws/transcript/{session_id}: live transcripts (data-channel mirrored)

## Config (.env)
Create `Backend/.env` with:

```
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=

DEEPGRAM_API_KEY=
OPENAI_API_KEY=
GROK_API_KEY=
CARTESIA_API_KEY=

SYSTEM_PROMPT=You are a friendly travel assistant.
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Persistence service
DJANGO_BASE_URL=http://127.0.0.1:9000
INGEST_TOKEN=super-secret-token

# Voice Activity Detection (VAD) Performance Tuning
VAD_MIN_SPEECH_DURATION=0.1
VAD_MIN_SILENCE_DURATION=0.3
VAD_PADDING_DURATION=0.1
```

## Environment Variables

### Required Variables
- `LIVEKIT_URL`: WebSocket URL for LiveKit server
- `LIVEKIT_API_KEY`: LiveKit API key
- `LIVEKIT_API_SECRET`: LiveKit API secret

### Provider Keys (Optional but Recommended)
- `DEEPGRAM_API_KEY`: For Deepgram STT
- `OPENAI_API_KEY`: For OpenAI STT/LLM/TTS
- `GROK_API_KEY`: For Grok LLM
- `CARTESIA_API_KEY`: For Cartesia TTS

### Agent Configuration
- `SYSTEM_PROMPT`: Default system prompt for the agent
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins

### Persistence Service
- `DJANGO_BASE_URL`: Base URL for Django persistence service (for session validation)
- `INGEST_TOKEN`: Token for authenticating with Django ingest endpoint

### Provider Selection (Optional)
- `STT_PROVIDER`: Speech-to-text provider (deepgram or openai)
- `TTS_PROVIDER`: Text-to-speech provider (openai or cartesia)
- `LLM_PROVIDER`: Language model provider (openai)
- `TTS_VOICE`: Voice to use for TTS (e.g., alloy, nova)

### Voice Activity Detection (VAD) Tuning
- `VAD_MIN_SPEECH_DURATION`: Minimum speech duration in seconds
- `VAD_MIN_SILENCE_DURATION`: Minimum silence duration in seconds
- `VAD_PADDING_DURATION`: Padding duration in seconds

## Run (Windows PowerShell)
1. Create venv and install deps
```
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r backend/requirements.txt
```
2. Start server
```
$env:PORT=8000; uvicorn backend.app.main:app --host 0.0.0.0 --port $env:PORT --reload
```

The server will serve API at http://localhost:8000.
