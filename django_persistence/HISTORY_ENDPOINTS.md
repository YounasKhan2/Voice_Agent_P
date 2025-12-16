# Conversation History Endpoints

This document describes the conversation history endpoints implemented in the Django backend.

## Endpoints

### 1. Get Conversation History List
**GET /api/users/history**

Retrieves the authenticated user's conversation history with pagination support.

**Authentication:** Required (session cookie)

**Query Parameters:**
- `limit` (optional): Number of results to return (default: 20, max: 100)
- `offset` (optional): Number of results to skip (default: 0)

**Example Request:**
```
GET /api/users/history?limit=20&offset=0
```

**Response (200 OK):**
```json
{
  "count": 45,
  "next": "/api/users/history?limit=20&offset=20",
  "previous": null,
  "results": [
    {
      "id": "session-uuid",
      "room": "quickstart",
      "started_at": "2024-01-01T10:00:00Z",
      "ended_at": "2024-01-01T10:15:00Z",
      "system_prompt": "You are a friendly travel assistant.",
      "utterance_count": 24
    },
    {
      "id": "another-session-uuid",
      "room": "quickstart",
      "started_at": "2024-01-01T09:00:00Z",
      "ended_at": "2024-01-01T09:10:00Z",
      "system_prompt": "You are a helpful assistant.",
      "utterance_count": 12
    }
  ]
}
```

**Response (401 Unauthorized):** If not authenticated

**Response (400 Bad Request):** If pagination parameters are invalid

---

### 2. Get Session Detail
**GET /api/users/history/{session_id}**

Retrieves a specific session's details with all utterances.

**Authentication:** Required (session cookie)

**Path Parameters:**
- `session_id` (UUID): The unique identifier of the session

**Example Request:**
```
GET /api/users/history/123e4567-e89b-12d3-a456-426614174000
```

**Response (200 OK):**
```json
{
  "id": "session-uuid",
  "room": "quickstart",
  "started_at": "2024-01-01T10:00:00Z",
  "ended_at": "2024-01-01T10:15:00Z",
  "system_prompt": "You are a friendly travel assistant.",
  "metadata": {
    "user_id": "user-123"
  },
  "utterances": [
    {
      "id": "utterance-uuid-1",
      "session": "session-uuid",
      "role": "agent",
      "text": "Hello! How can I help you today?",
      "event": "",
      "is_final": true,
      "created_at": "2024-01-01T10:00:05Z"
    },
    {
      "id": "utterance-uuid-2",
      "session": "session-uuid",
      "role": "user",
      "text": "I want to plan a trip to Paris.",
      "event": "",
      "is_final": true,
      "created_at": "2024-01-01T10:00:12Z"
    },
    {
      "id": "utterance-uuid-3",
      "session": "session-uuid",
      "role": "agent",
      "text": "Paris is a wonderful destination! When are you planning to visit?",
      "event": "",
      "is_final": true,
      "created_at": "2024-01-01T10:00:18Z"
    }
  ]
}
```

**Response (404 Not Found):** If session doesn't exist or doesn't belong to the authenticated user
```json
{
  "detail": "Session not found"
}
```

**Response (401 Unauthorized):** If not authenticated

---

## Implementation Details

### Serializers
- `SessionHistoryListSerializer`: Returns session metadata with utterance count
  - Uses `SerializerMethodField` to calculate utterance count efficiently
  - Includes: id, room, started_at, ended_at, system_prompt, utterance_count
  
- `SessionHistoryDetailSerializer`: Returns full session with all utterances
  - Includes nested `UtteranceSerializer` for all utterances
  - Includes: id, room, started_at, ended_at, system_prompt, metadata, utterances

### Views
- `history_list_view`: Handles GET for /api/users/history
  - Filters sessions by `user_account` foreign key
  - Orders by `started_at` descending (most recent first)
  - Uses `prefetch_related('utterances')` for efficient query
  - Implements pagination with limit/offset
  - Returns paginated response with count, next, previous URLs
  
- `history_detail_view`: Handles GET for /api/users/history/{session_id}
  - Verifies session belongs to authenticated user
  - Uses `prefetch_related('utterances')` for efficient query
  - Returns 404 if session not found or doesn't belong to user
  - Utterances are ordered by `created_at` (via model Meta ordering)

### Security
- Both endpoints require authentication via Django session cookie
- Sessions are filtered by `user_account` foreign key to ensure users only see their own sessions
- Session detail endpoint verifies ownership before returning data
- Returns 404 (not 403) to avoid leaking information about session existence

### Performance Optimizations
- Uses `prefetch_related('utterances')` to avoid N+1 queries
- Limits maximum page size to 100 results
- Uses database indexes on `user_account` and `started_at` fields

### Requirements Satisfied
- Requirement 7.1: Return all sessions linked to user ID ordered by most recent first
- Requirement 7.2: Return session metadata and all associated utterances
- Requirement 7.3: Do not return sessions belonging to other users
- Requirement 7.4: Include session start time, end time, room name, and utterance count
- Requirement 7.5: Return empty list where user has no conversation history

## Usage Examples

### Fetching First Page of History
```bash
curl -X GET http://localhost:9000/api/users/history \
  -H "Cookie: sessionid=your-session-cookie"
```

### Fetching Second Page with Custom Limit
```bash
curl -X GET "http://localhost:9000/api/users/history?limit=10&offset=10" \
  -H "Cookie: sessionid=your-session-cookie"
```

### Fetching Specific Session Details
```bash
curl -X GET http://localhost:9000/api/users/history/123e4567-e89b-12d3-a456-426614174000 \
  -H "Cookie: sessionid=your-session-cookie"
```

## Database Schema

The endpoints rely on the following relationships:

```
User (conversation_user table)
  └─ sessions (one-to-many via user_account foreign key)
       └─ utterances (one-to-many via session foreign key)
```

### Key Fields
- `Session.user_account`: Foreign key to User (nullable for anonymous sessions)
- `Session.started_at`: Timestamp for ordering
- `Utterance.created_at`: Timestamp for ordering within session
- `Utterance.role`: "user", "agent", or "event"

## Testing Checklist

- [ ] Authenticated user can retrieve their history list
- [ ] History list is ordered by most recent first
- [ ] Pagination works correctly (limit, offset)
- [ ] Utterance count is accurate for each session
- [ ] Authenticated user can retrieve specific session details
- [ ] Session details include all utterances in correct order
- [ ] User cannot access another user's sessions (returns 404)
- [ ] Unauthenticated requests return 401
- [ ] Invalid pagination parameters return 400
- [ ] Empty history returns empty results array
