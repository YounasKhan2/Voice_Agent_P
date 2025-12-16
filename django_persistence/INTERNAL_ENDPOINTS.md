# Internal API Endpoints

This document describes internal API endpoints that are designed for inter-service communication within the Voice Agent system. These endpoints should not be exposed publicly.

## Session Validation

### POST /api/internal/validate-session

**Purpose**: Validate a user session cookie and retrieve user information and preferences.

**Use Case**: Called by the FastAPI backend to validate user sessions when starting authenticated voice conversations.

**Authentication**: Session cookie (sessionid)

**Request**:
```http
POST /api/internal/validate-session HTTP/1.1
Cookie: sessionid=<session-cookie-value>
Content-Type: application/json
```

**Response (200 OK - Valid Session)**:
```json
{
  "valid": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "display_name": "John Doe",
  "preferences": {
    "preferred_voice": "nova",
    "preferred_language": "en",
    "favorite_topics": ["travel", "technology"],
    "system_prompt_override": ""
  }
}
```

**Response (401 Unauthorized - Invalid Session)**:
```json
{
  "valid": false
}
```

**Fields**:
- `valid` (boolean): Whether the session is valid
- `user_id` (string, UUID): The authenticated user's unique identifier
- `email` (string): The user's email address
- `display_name` (string): The user's display name
- `preferences` (object): User preferences for voice agent behavior
  - `preferred_voice` (string): TTS voice identifier (e.g., "alloy", "nova")
  - `preferred_language` (string): Language code (e.g., "en", "es")
  - `favorite_topics` (array): List of favorite conversation topics
  - `system_prompt_override` (string): Custom system prompt override

**Security Notes**:
- This endpoint uses Django's session authentication
- The session cookie must be HTTP-only and secure in production
- CORS must be configured to allow the FastAPI backend origin
- This endpoint should only be accessible from internal services

**Example Usage (Python)**:
```python
import httpx

async def validate_session(session_cookie: str) -> dict | None:
    """Validate session with Django backend."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:9000/api/internal/validate-session",
                cookies={"sessionid": session_cookie},
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    return data
    except Exception:
        pass
    return None
```

**Integration Flow**:
1. Flask frontend authenticates user and receives session cookie
2. User starts voice conversation from Flask frontend
3. Flask sends session start request to FastAPI with session cookie
4. FastAPI calls this endpoint to validate the session
5. If valid, FastAPI retrieves user preferences and applies them to the agent
6. Voice conversation proceeds with personalized settings

**Error Handling**:
- If Django is unreachable, FastAPI should gracefully fall back to anonymous mode
- If session validation fails, treat the request as anonymous
- Network timeouts should be handled with appropriate fallback behavior

**CORS Configuration**:
Ensure the Django settings include the FastAPI backend in CORS_ALLOWED_ORIGINS:
```python
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",  # Flask frontend
    "http://localhost:5173",   # Flask frontend
    "http://127.0.0.1:8000",  # FastAPI backend
    "http://localhost:8000",   # FastAPI backend
]
CORS_ALLOW_CREDENTIALS = True
```
