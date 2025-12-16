# API Reference

Complete API reference for the Voice Agent system.

## Table of Contents

1. [FastAPI Backend](#fastapi-backend)
2. [Django Authentication API](#django-authentication-api)
3. [Django User Profile API](#django-user-profile-api)
4. [Django History API](#django-history-api)
5. [Django Internal API](#django-internal-api)
6. [Error Responses](#error-responses)

---

## FastAPI Backend

Base URL: `http://127.0.0.1:8000` (development)

### Health Check

**GET /health**

Check if the FastAPI service is running.

**Response (200 OK)**:
```json
{
  "status": "ok"
}
```

---

### Get LiveKit Token

**GET /token**

Mint a LiveKit access token for browser client.

**Query Parameters**:
- `room` (required): Room name to join
- `identity` (required): User identity/ID
- `name` (optional): Display name for the participant

**Example Request**:
```
GET /token?room=quickstart&identity=user123&name=John
```

**Response (200 OK)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### Start Agent Session

**POST /session**

Start a server-side voice agent session.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (optional, for authenticated sessions)

**Request Body**:
```json
{
  "room": "quickstart",
  "identity": "user123",
  "system_prompt": "You are a friendly travel assistant."
}
```

**Response (200 OK)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Behavior**:
- If session cookie is present and valid, the session is linked to the user
- User preferences (voice, language, prompt) are automatically applied
- If no session cookie, creates an anonymous session

---

### Stop Agent Session

**DELETE /session/{session_id}**

Stop a running agent session.

**Path Parameters**:
- `session_id` (UUID): Session identifier

**Response (200 OK)**:
```json
{
  "stopped": true
}
```

---

### WebSocket Transcript Stream

**WS /ws/transcript/{session_id}**

Real-time transcript and event stream.

**Path Parameters**:
- `session_id` (UUID): Session identifier

**Server → Client Messages**:

Interim transcript:
```json
{
  "role": "user",
  "text": "I want to visit",
  "final": false
}
```

Final transcript:
```json
{
  "role": "user",
  "text": "I want to visit Paris",
  "final": true
}
```

Speech event:
```json
{
  "role": "agent",
  "event": "speech_started"
}
```

---

## Django Authentication API

Base URL: `http://127.0.0.1:9000/api/auth` (development)

### Register User

**POST /api/auth/register**

Create a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "display_name": "John Doe"
}
```

**Response (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "display_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Sets Cookie**: `sessionid=<encrypted-session-id>`

**Validation Rules**:
- Email must be valid format and unique
- Password must be at least 8 characters
- Display name is required

**Error Response (400 Bad Request)**:
```json
{
  "email": ["User with this email already exists."],
  "password": ["This password is too short. It must contain at least 8 characters."]
}
```

---

### Login

**POST /api/auth/login**

Authenticate user and create session.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "display_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Sets Cookie**: `sessionid=<encrypted-session-id>`

**Error Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid credentials"
}
```

---

### Logout

**POST /api/auth/logout**

Destroy user session.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (required)

**Response (200 OK)**:
```json
{
  "message": "Logged out successfully"
}
```

**Clears Cookie**: `sessionid`

---

### Get Current User

**GET /api/auth/me**

Get authenticated user information.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (required)

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "display_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Response (401 Unauthorized)**:
```json
{
  "authenticated": false
}
```

---

## Django User Profile API

Base URL: `http://127.0.0.1:9000/api/users` (development)

All endpoints require authentication via session cookie.

### Get User Profile

**GET /api/users/profile**

Get user profile with preferences.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (required)

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "display_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "preferences": {
    "preferred_voice": "alloy",
    "preferred_language": "en",
    "favorite_topics": ["travel", "food"],
    "system_prompt_override": ""
  }
}
```

---

### Update User Profile

**PATCH /api/users/profile**

Update display name or email.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (required)

**Request Body** (partial update):
```json
{
  "display_name": "Jane Doe"
}
```

Or:
```json
{
  "email": "newemail@example.com"
}
```

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "newemail@example.com",
  "display_name": "Jane Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "preferences": {
    "preferred_voice": "alloy",
    "preferred_language": "en",
    "favorite_topics": ["travel", "food"],
    "system_prompt_override": ""
  }
}
```

**Error Response (400 Bad Request)**:
```json
{
  "email": ["User with this email already exists."]
}
```

---

### Update User Preferences

**PUT /api/users/preferences**

Update user preferences for voice agent.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (required)

**Request Body**:
```json
{
  "preferred_voice": "nova",
  "preferred_language": "es",
  "favorite_topics": ["travel", "technology"],
  "system_prompt_override": "You are a helpful travel assistant."
}
```

**Response (200 OK)**:
```json
{
  "preferred_voice": "nova",
  "preferred_language": "es",
  "favorite_topics": ["travel", "technology"],
  "system_prompt_override": "You are a helpful travel assistant."
}
```

**Available Voices**:
- OpenAI: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`
- Cartesia: Various voices (check Cartesia documentation)

**Language Codes**:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese

---

### Change Password

**POST /api/users/change-password**

Change user password.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (required)

**Request Body**:
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response (200 OK)**:
```json
{
  "message": "Password changed successfully"
}
```

**Error Response (400 Bad Request)**:
```json
{
  "current_password": ["Current password is incorrect."]
}
```

Or:
```json
{
  "new_password": ["This password is too short. It must contain at least 8 characters."]
}
```

---

## Django History API

Base URL: `http://127.0.0.1:9000/api/users/history` (development)

All endpoints require authentication via session cookie.

### List Conversation History

**GET /api/users/history**

Get paginated list of user's conversation sessions.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (required)

**Query Parameters**:
- `limit` (optional): Results per page (default: 20, max: 100)
- `offset` (optional): Number of results to skip (default: 0)

**Example Request**:
```
GET /api/users/history?limit=20&offset=0
```

**Response (200 OK)**:
```json
{
  "count": 45,
  "next": "/api/users/history?limit=20&offset=20",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "room": "quickstart",
      "started_at": "2024-01-01T10:00:00Z",
      "ended_at": "2024-01-01T10:15:00Z",
      "system_prompt": "You are a friendly travel assistant.",
      "utterance_count": 24
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "room": "quickstart",
      "started_at": "2024-01-01T09:00:00Z",
      "ended_at": "2024-01-01T09:10:00Z",
      "system_prompt": "You are a helpful assistant.",
      "utterance_count": 12
    }
  ]
}
```

**Ordering**: Sessions are ordered by `started_at` descending (most recent first)

---

### Get Session Detail

**GET /api/users/history/{session_id}**

Get full transcript for a specific session.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (required)

**Path Parameters**:
- `session_id` (UUID): Session identifier

**Example Request**:
```
GET /api/users/history/550e8400-e29b-41d4-a716-446655440000
```

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "room": "quickstart",
  "started_at": "2024-01-01T10:00:00Z",
  "ended_at": "2024-01-01T10:15:00Z",
  "system_prompt": "You are a friendly travel assistant.",
  "metadata": {
    "user_id": "user-123"
  },
  "utterances": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "session": "550e8400-e29b-41d4-a716-446655440000",
      "role": "agent",
      "text": "Hello! How can I help you today?",
      "event": "",
      "is_final": true,
      "created_at": "2024-01-01T10:00:05Z"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "session": "550e8400-e29b-41d4-a716-446655440000",
      "role": "user",
      "text": "I want to plan a trip to Paris.",
      "event": "",
      "is_final": true,
      "created_at": "2024-01-01T10:00:12Z"
    }
  ]
}
```

**Error Response (404 Not Found)**:
```json
{
  "detail": "Session not found"
}
```

**Note**: Returns 404 if session doesn't exist or doesn't belong to the authenticated user.

---

## Django Internal API

Base URL: `http://127.0.0.1:9000/api/internal` (development)

**Warning**: These endpoints are for inter-service communication only and should not be exposed publicly.

### Validate Session

**POST /api/internal/validate-session**

Validate user session and retrieve user data.

**Headers**:
- `Cookie: sessionid=<session-cookie>` (required)

**Use Case**: Called by FastAPI backend to validate sessions when starting authenticated voice conversations.

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

---

## Error Responses

### Standard Error Format

All API errors follow this format:

```json
{
  "detail": "Error message"
}
```

Or for validation errors:

```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Another error message"]
}
```

### HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data or validation error
- `401 Unauthorized` - Authentication required or invalid credentials
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Common Error Scenarios

#### Authentication Required
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### Invalid Credentials
```json
{
  "detail": "Invalid credentials"
}
```

#### Validation Error
```json
{
  "email": ["Enter a valid email address."],
  "password": ["This password is too short. It must contain at least 8 characters."]
}
```

#### Resource Not Found
```json
{
  "detail": "Session not found"
}
```

#### CORS Error
If you see CORS errors in the browser console, ensure:
1. `CORS_ALLOWED_ORIGINS` includes your frontend URL in Django `.env`
2. `CORS_ALLOW_CREDENTIALS=True` in Django settings
3. Requests include credentials (cookies)

---

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider adding rate limiting to prevent abuse.

## Pagination

List endpoints support pagination with `limit` and `offset` parameters:

- `limit`: Number of results per page (default: 20, max: 100)
- `offset`: Number of results to skip (default: 0)

Response includes:
- `count`: Total number of results
- `next`: URL for next page (null if last page)
- `previous`: URL for previous page (null if first page)
- `results`: Array of results for current page

## Authentication

The system uses session-based authentication with HTTP-only cookies:

1. User logs in via `/api/auth/login`
2. Django creates a server-side session
3. Session ID is stored in HTTP-only cookie
4. Cookie is automatically sent with subsequent requests
5. Django validates session on each request

**Security Features**:
- HTTP-only cookies prevent XSS attacks
- Secure flag in production (HTTPS only)
- SameSite=Lax prevents CSRF attacks
- 14-day session expiration (configurable)

## CORS Configuration

For local development, ensure these origins are allowed in Django:

```python
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",  # Flask frontend
    "http://localhost:5173",   # Flask frontend
    "http://127.0.0.1:8000",  # FastAPI backend
    "http://localhost:8000",   # FastAPI backend
]
CORS_ALLOW_CREDENTIALS = True
```

In production, restrict to your actual domain.
