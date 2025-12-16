from __future__ import annotations
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Optional

from .config import get_settings
from .models import TokenRequest, TokenResponse, SessionStartRequest, SessionStartResponse, SessionStopResponse
from .utils.livekit import mint_token
from .utils.persistence import get_ingest_stats
from .utils.auth import validate_session_cookie
from .agent import AgentManager

app = FastAPI(title="Voice Agent Backend")
settings = get_settings()

# CORS Configuration
origins = []
if settings.cors_origins:
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

# If no origins specified or in development, allow common development origins
if not origins or settings.cors_origins == "*":
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175"
    ]

print(f"CORS Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

agent_manager = AgentManager()
_transcript_ws_rooms: Dict[str, set[WebSocket]] = {}


async def _broadcast_transcript(session_id: str, payload: dict) -> None:
    # send to all ws clients in this session
    conns = list(_transcript_ws_rooms.get(session_id, set()))
    if not conns:
        return
    text = JSONResponse(content=payload).body.decode()
    # best-effort; drop broken sockets
    for ws in conns:
        try:
            await ws.send_text(text)
        except Exception:
            try:
                _transcript_ws_rooms.get(session_id, set()).discard(ws)
            except Exception:
                pass


agent_manager.set_transcript_broadcaster(_broadcast_transcript)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/diagnostics")
async def diagnostics():
    settings = get_settings()
    ingest = get_ingest_stats()
    return {
        "livekit": {
            "url": bool(settings.livekit_url),
            "api_key": bool(settings.livekit_api_key),
            "api_secret": bool(settings.livekit_api_secret),
        },
        "providers": {
            "stt": settings.stt_provider,
            "tts": settings.tts_provider,
            "llm": settings.llm_provider,
            "tts_voice": settings.tts_voice,
        },
        "persistence": {
            "django_base_url": settings.django_base_url,
            "configured": ingest["configured"],
            "last_ingest_ts": ingest["last_ingest_ts"],
            "event_count": ingest["event_count"],
            "session_ids": ingest["session_ids"],
        },
    }


@app.get("/token", response_model=TokenResponse)
def get_token(room: str = Query(...), identity: str = Query(...), name: str | None = Query(None)):
    if not settings.livekit_url or not settings.livekit_api_key or not settings.livekit_api_secret:
        raise HTTPException(status_code=500, detail="LiveKit credentials not configured")
    token = mint_token(room=room, identity=identity, name=name)
    return {"token": token}


@app.options("/session")
async def options_session():
    return {"message": "OK"}

@app.post("/session", response_model=SessionStartResponse)
async def start_session(req: SessionStartRequest, sessionid: Optional[str] = Cookie(None)):
    """
    Start a voice agent session.
    
    If a session cookie is provided, validates it with Django and applies user preferences.
    Otherwise, creates an anonymous session with default settings.
    """
    user_data = None
    user_id = None
    user_preferences = None
    
    # Validate session cookie if present
    if sessionid:
        user_data = await validate_session_cookie(sessionid)
        if user_data:
            user_id = user_data.get('user_id')
            user_preferences = user_data.get('preferences', {})
    
    # Determine system prompt (user override takes precedence)
    instructions = req.system_prompt or settings.system_prompt
    if user_preferences and user_preferences.get('system_prompt_override'):
        instructions = user_preferences['system_prompt_override']
    
    # Start session with user context
    session_id = await agent_manager.start_session(
        room_name=req.room,
        instructions=instructions,
        user_id=user_id,
        user_preferences=user_preferences
    )
    
    return {"session_id": session_id}


@app.delete("/session/{session_id}", response_model=SessionStopResponse)
async def stop_session(session_id: str):
    stopped = await agent_manager.stop_session(session_id)
    if not stopped:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"stopped": True}


@app.websocket("/ws/transcript/{session_id}")
async def transcript_ws(ws: WebSocket, session_id: str):
    await ws.accept()
    # register client into session room
    room = _transcript_ws_rooms.setdefault(session_id, set())
    room.add(ws)
    try:
        while True:
            # keep alive; messages are unidirectional from server -> client
            _ = await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        try:
            _transcript_ws_rooms.get(session_id, set()).discard(ws)
        except Exception:
            pass
