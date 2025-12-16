from pydantic import BaseModel
from typing import Optional

class TokenRequest(BaseModel):
    room: str
    identity: str
    name: Optional[str] = None

class TokenResponse(BaseModel):
    token: str

class SessionStartRequest(BaseModel):
    room: str
    identity: str
    system_prompt: Optional[str] = None

class SessionStartResponse(BaseModel):
    session_id: str

class SessionStopResponse(BaseModel):
    stopped: bool
