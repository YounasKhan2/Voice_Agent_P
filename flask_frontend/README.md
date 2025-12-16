# Flask Frontend for LiveKit Voice Agent

This is a minimal Flask UI that talks to the existing FastAPI + LiveKit backend. It:

- Fetches a LiveKit token from FastAPI
- Connects your browser to LiveKit and publishes microphone audio
- Starts a server-side voice agent session via FastAPI
- Subscribes to transcripts/events via FastAPI WebSocket and displays them

## Prerequisites

- The FastAPI backend running locally (default http://127.0.0.1:8000)
- A reachable LiveKit server URL (e.g. ws://127.0.0.1:7880 or wss://...)
- LiveKit credentials configured in the backend (.env)

## Configure

Create a `.env` file next to `app.py` or set environment variables before running:

```
FASTAPI_BASE_URL=http://127.0.0.1:8000
LIVEKIT_URL=wss://your-livekit-host.livekit.cloud
DEFAULT_ROOM=quickstart
SYSTEM_PROMPT=You are a friendly travel assistant.
PORT=5173
DJANGO_API_URL=http://127.0.0.1:9000/api
SECRET_KEY=your-secret-key-here-change-in-production
```

## Environment Variables

- `FASTAPI_BASE_URL`: Base URL for FastAPI backend (default: http://127.0.0.1:8000)
- `LIVEKIT_URL`: WebSocket URL for LiveKit server (default: http://127.0.0.1:7880)
- `DEFAULT_ROOM`: Default room name for voice sessions (default: quickstart)
- `SYSTEM_PROMPT`: Default system prompt for the agent
- `PORT`: Port to run Flask server on (default: 5173)
- `DJANGO_API_URL`: Base URL for Django API endpoints (for authentication and user features)
- `SECRET_KEY`: Flask secret key for session management (change in production!)

Note: The backend currently allows CORS for ports 3000 and 5173 by default. Running Flask on port 5173 avoids CORS issues.

## Install and Run (Windows PowerShell)

```powershell
# (Optional) Create and activate a virtualenv
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# Install Flask
pip install -r requirements.txt

# Run Flask on port 5173 to match backend CORS allowlist
$env:FASTAPI_BASE_URL = "http://127.0.0.1:8000"
$env:LIVEKIT_URL = "ws://127.0.0.1:7880"  # or wss://your-livekit-host
$env:PORT = "5173"
python .\app.py
```

Open http://127.0.0.1:5173/chat in your browser, enter your name and room, and click "Join + Start Agent".

## How it Works

- GET /token (FastAPI): mints a LiveKit token for the browser client
- POST /session (FastAPI): starts a server-side agent that joins the same room
- WS /ws/transcript/{session_id} (FastAPI): one-way server->client transcript stream; the client keeps the socket alive by sending a simple ping

## Troubleshooting

- CORS: If you run Flask on a different port (e.g., 5000), update backend CORS settings or set `CORS_ORIGINS` to include your origin.
- Autoplay: Start the session from a user click so the browser allows audio playback from the agent.
- LiveKit URL: Use ws:// for local dev unless your server has TLS (then use wss://).
