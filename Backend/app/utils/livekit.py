from __future__ import annotations
from typing import Optional
from livekit import api
from ..config import get_settings
import uuid


def mint_token(room: str, identity: str, name: Optional[str] = None) -> str:
    """Mint a LiveKit access token for a web client."""
    s = get_settings()
    grant = api.VideoGrants(room_join=True, room=room)
    at = api.AccessToken(s.livekit_api_key, s.livekit_api_secret)
    at = at.with_grants(grant).with_identity(identity)
    if name:
        at = at.with_name(name)
    return at.to_jwt()


def new_session_id() -> str:
    return str(uuid.uuid4())
