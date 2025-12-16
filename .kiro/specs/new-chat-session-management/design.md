# Design Document

## Overview

This design implements a "New Chat" feature that allows users to start fresh conversations while automatically preserving their current session in chat history. The solution integrates with the existing voice agent architecture, Django persistence layer, and Flask frontend to provide seamless session management.

## Architecture

### High-Level Flow

```
User clicks "New Chat" button
    ↓
Frontend saves current session to Django API
    ↓
Frontend disconnects from current LiveKit room
    ↓
Frontend clears UI state and message history
    ↓
Frontend initializes new agent session
    ↓
Frontend connects to new LiveKit room
    ↓
User begins new conversation
```

### Component Interaction

```
┌─────────────────┐
│  Flask Frontend │
│   (chat.html)   │
└────────┬────────┘
         │
         ├─── New Chat Button Click
         │
         ├─── Save Session (POST /api/users/sessions/save)
         │    └──> Django Persistence API
         │
         ├─── Disconnect Agent
         │    └──> voice-agent.js cleanup()
         │         └──> FastAPI (DELETE /session/{id})
         │              └──> LiveKit disconnect
         │
         ├─── Clear UI State
         │    └──> Reset messages, interim tracking
         │
         └─── Initialize New Session
              └──> voice-agent.js connect()
                   └──> FastAPI (POST /session)
                        └──> LiveKit connect
```

## Components and Interfaces

### 1. Frontend UI Component (chat.html)

**New Chat Button Handler**
- Location: `flask_frontend/templates/chat.html`
- Trigger: User clicks "New Chat" button in sidebar
- Responsibilities:
  - Validate current session has messages before saving
  - Call session save API
  - Trigger agent cleanup
  - Reset UI state
  - Initialize new agent session

**UI State Management**
- Track current session ID
- Track message count
- Manage interim message state
- Handle loading indicators during transitions

### 2. Voice Agent JavaScript (voice-agent.js)

**Session Management Functions**

```javascript
// New function to save current session
async function saveCurrentSession() {
  if (!sessionId || messageSequence.length === 0) {
    return null; // Nothing to save
  }
  
  const response = await fetch(`${DJANGO_API_URL}/api/users/sessions/save`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      messages: messageSequence
    })
  });
  
  if (!response.ok) {
    throw new Error('Failed to save session');
  }
  
  return await response.json();
}

// Enhanced cleanup function
async function cleanup(saveSession = false) {
  if (saveSession) {
    await saveCurrentSession();
  }
  
  // Existing cleanup logic...
  // - Hide speaking animations
  // - Clear interim messages
  // - Close WebSocket
  // - Stop agent session
  // - Disconnect LiveKit
  // - Reset UI state
}

// New function to start fresh session
async function startNewChat() {
  // Save current session if it has messages
  await cleanup(true);
  
  // Clear message tracking
  messageSequence = [];
  messageIdCounter = 0;
  currentInterimMessages = {
    agent: { text: null, messageId: null },
    user: { text: null, messageId: null }
  };
  
  // Clear UI
  const messagesContainer = document.getElementById('messages-container');
  messagesContainer.innerHTML = '';
  
  // Show empty state
  const emptyState = document.getElementById('empty-state');
  if (emptyState) {
    emptyState.style.display = 'flex';
  }
  
  // Update conversation title
  const titleEl = document.getElementById('conversation-title');
  if (titleEl) {
    titleEl.textContent = 'New Conversation';
  }
  
  // Initialize new agent session
  await connect();
}
```

**State Variables**
- `sessionId`: Current LiveKit session identifier
- `messageSequence`: Array of all messages in current session
- `messageIdCounter`: Counter for generating unique message IDs
- `currentInterimMessages`: Tracking object for interim transcriptions

### 3. Django API Endpoints

**New Endpoint: Save Session**

```python
# django_persistence/conversation/views.py

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def save_session_view(request):
    """
    POST /api/users/sessions/save
    Save current voice session to user's history.
    
    Request body:
    {
      "session_id": "uuid",
      "messages": [
        {"role": "user", "text": "...", "timestamp": 1234567890},
        {"role": "agent", "text": "...", "timestamp": 1234567891}
      ]
    }
    
    - Verify session_id exists
    - Associate session with authenticated user
    - Mark session as ended
    - Return saved session metadata
    """
    session_id = request.data.get('session_id')
    messages = request.data.get('messages', [])
    
    if not session_id:
        return Response(
            {"detail": "session_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get session and verify it's not already associated with another user
        session = Session.objects.get(id=session_id)
        
        # Associate with current user if not already set
        if not session.user_account:
            session.user_account = request.user
            session.ended_at = timezone.now()
            session.save()
        elif session.user_account != request.user:
            return Response(
                {"detail": "Session belongs to another user"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create final utterances from message sequence if needed
        # (This ensures we have the complete conversation even if
        # some messages weren't captured via the ingest endpoint)
        existing_utterances = set(
            session.utterances.filter(is_final=True)
            .values_list('text', 'role')
        )
        
        new_utterances = []
        for msg in messages:
            msg_tuple = (msg.get('text'), msg.get('role'))
            if msg_tuple not in existing_utterances:
                new_utterances.append(
                    Utterance(
                        session=session,
                        role=msg.get('role', 'user'),
                        text=msg.get('text', ''),
                        is_final=True,
                        created_at=timezone.datetime.fromtimestamp(
                            msg.get('timestamp', 0) / 1000,
                            tz=timezone.utc
                        ) if msg.get('timestamp') else timezone.now()
                    )
                )
        
        if new_utterances:
            Utterance.objects.bulk_create(new_utterances)
        
        # Return session metadata
        serializer = SessionHistoryListSerializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Session.DoesNotExist:
        return Response(
            {"detail": "Session not found"},
            status=status.HTTP_404_NOT_FOUND
        )
```

**URL Configuration**
```python
# django_persistence/conversation/urls.py
urlpatterns = [
    # ... existing patterns ...
    path('users/sessions/save', views.save_session_view, name='save-session'),
]
```

### 4. Backend Agent Management

**No Changes Required**
- The existing `AgentManager.start_session()` already creates new sessions with unique UUIDs
- The existing `AgentManager.stop_session()` handles cleanup properly
- Session association with users is handled at the Django layer

## Data Models

### Session Association

**Current State**
```python
class Session(models.Model):
    id = models.UUIDField(primary_key=True)
    room = models.CharField(max_length=128)
    user_id = models.CharField(max_length=128, blank=True, null=True)  # Legacy
    user_account = models.ForeignKey(User, ...)  # New FK relationship
    system_prompt = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
```

**Session Lifecycle**
1. **Creation**: Session created by FastAPI when user starts voice conversation
   - `user_account` is NULL initially (anonymous session)
   - `started_at` is set automatically
   - `ended_at` is NULL

2. **Active**: Session is active while user is conversing
   - Utterances are ingested via `/api/ingest` endpoint
   - Session remains unassociated with user account

3. **Save**: User clicks "New Chat" button
   - Frontend calls `/api/users/sessions/save`
   - Django associates session with authenticated user
   - `ended_at` is set to current timestamp
   - Session becomes part of user's history

4. **Retrieval**: User views history
   - Sessions filtered by `user_account` foreign key
   - Only sessions with `user_account` set are visible in history

### Message Tracking

**Frontend Message Sequence**
```javascript
messageSequence = [
  {
    role: 'user',
    text: 'Hello, I want to plan a trip',
    timestamp: 1234567890123
  },
  {
    role: 'agent',
    text: 'I would be happy to help you plan your trip!',
    timestamp: 1234567891456
  }
]
```

This array is maintained in `voice-agent.js` and sent to Django when saving the session.

## Error Handling

### Frontend Error Scenarios

**1. Save Session Fails**
```javascript
try {
  await saveCurrentSession();
} catch (error) {
  console.error('Failed to save session:', error);
  // Show user-friendly error toast
  if (window.showToast) {
    window.showToast('Failed to save conversation. Please try again.', 'error');
  }
  // Don't proceed with new chat if save failed
  return;
}
```

**2. Agent Initialization Fails**
```javascript
try {
  await connect();
} catch (error) {
  console.error('Failed to start new session:', error);
  // Show error message
  if (window.showToast) {
    window.showToast('Failed to start new conversation. Please try again.', 'error');
  }
  // Reset button state
  voiceButton.disabled = false;
}
```

**3. Network Timeout**
- Set reasonable timeout for save operation (10 seconds)
- Show loading indicator during save
- Allow user to retry if timeout occurs

### Backend Error Scenarios

**1. Session Not Found**
- Return 404 with clear error message
- Frontend should log error and proceed with new session

**2. Session Belongs to Another User**
- Return 403 Forbidden
- This should never happen in normal flow
- Log as potential security issue

**3. Database Write Failure**
- Return 500 with generic error message
- Log detailed error server-side
- Frontend should retry once before showing error to user

## Testing Strategy

### Unit Tests

**Frontend (JavaScript)**
```javascript
// Test saveCurrentSession function
describe('saveCurrentSession', () => {
  it('should not save empty sessions', async () => {
    messageSequence = [];
    const result = await saveCurrentSession();
    expect(result).toBeNull();
  });
  
  it('should send correct payload to API', async () => {
    messageSequence = [
      { role: 'user', text: 'Hello', timestamp: 123 }
    ];
    sessionId = 'test-uuid';
    
    const result = await saveCurrentSession();
    
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/users/sessions/save'),
      expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('test-uuid')
      })
    );
  });
});

// Test startNewChat function
describe('startNewChat', () => {
  it('should clear UI state', async () => {
    await startNewChat();
    
    const container = document.getElementById('messages-container');
    expect(container.innerHTML).toBe('');
  });
  
  it('should initialize new agent session', async () => {
    await startNewChat();
    
    expect(connect).toHaveBeenCalled();
  });
});
```

**Backend (Python)**
```python
# Test save_session_view
class SaveSessionViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            display_name='Test User'
        )
        self.client.force_login(self.user)
        
        self.session = Session.objects.create(
            id=uuid.uuid4(),
            room='test-room',
            system_prompt='Test prompt'
        )
    
    def test_save_session_associates_with_user(self):
        response = self.client.post(
            '/api/users/sessions/save',
            data={
                'session_id': str(self.session.id),
                'messages': [
                    {'role': 'user', 'text': 'Hello', 'timestamp': 123}
                ]
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.session.refresh_from_db()
        self.assertEqual(self.session.user_account, self.user)
        self.assertIsNotNone(self.session.ended_at)
    
    def test_save_session_requires_authentication(self):
        self.client.logout()
        
        response = self.client.post(
            '/api/users/sessions/save',
            data={'session_id': str(self.session.id)},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_save_session_prevents_cross_user_access(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            display_name='Other User'
        )
        self.session.user_account = other_user
        self.session.save()
        
        response = self.client.post(
            '/api/users/sessions/save',
            data={'session_id': str(self.session.id)},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
```

### Integration Tests

**End-to-End Flow**
1. User logs in
2. User starts voice conversation
3. User sends several messages
4. User clicks "New Chat" button
5. Verify:
   - Previous session saved to history
   - Previous session associated with user
   - UI cleared
   - New agent session initialized
   - New session has different ID
   - User can start new conversation

**Session Persistence**
1. User creates multiple conversations
2. User clicks "New Chat" between each
3. User navigates to history page
4. Verify:
   - All sessions appear in history
   - Sessions ordered by most recent first
   - Each session shows correct message count
   - Each session can be opened to view details

### Manual Testing Checklist

- [ ] New Chat button is visible and accessible
- [ ] Clicking New Chat saves current session (if has messages)
- [ ] Clicking New Chat clears UI completely
- [ ] Clicking New Chat initializes new agent
- [ ] New agent is ready to accept input
- [ ] Previous conversation appears in history
- [ ] Previous conversation can be viewed from history
- [ ] Empty sessions are not saved to history
- [ ] Loading indicator shows during save operation
- [ ] Error messages display if save fails
- [ ] User can retry if operation fails
- [ ] Session IDs are unique for each conversation
- [ ] Transcriptions are preserved in saved sessions
- [ ] Message order is maintained in saved sessions

## Performance Considerations

### Frontend Optimizations

**1. Debounce New Chat Button**
- Prevent rapid clicking during save operation
- Disable button while processing
- Show loading indicator

**2. Lazy Load History**
- Only load recent sessions initially
- Implement pagination for history list
- Load session details on demand

**3. Optimize Message Storage**
- Limit in-memory message sequence to reasonable size
- Clear old messages from DOM periodically
- Use efficient data structures for tracking

### Backend Optimizations

**1. Bulk Operations**
- Use `bulk_create()` for utterances
- Minimize database queries
- Use `select_related()` and `prefetch_related()` for history queries

**2. Indexing**
- Index on `user_account` and `started_at` (already exists)
- Index on `session_id` for fast lookups (primary key)

**3. Caching**
- Cache user preferences to avoid repeated queries
- Cache recent sessions for faster history loading

## Security Considerations

### Authentication & Authorization

**1. Session Ownership**
- Verify user owns session before saving
- Prevent cross-user session access
- Use Django's authentication middleware

**2. Input Validation**
- Validate session_id format (UUID)
- Sanitize message text
- Limit message array size to prevent DoS

**3. Rate Limiting**
- Limit save session requests per user
- Prevent abuse of history endpoints
- Implement exponential backoff for retries

### Data Privacy

**1. User Data Isolation**
- Sessions filtered by user_account FK
- No cross-user data leakage
- Proper permission checks on all endpoints

**2. Sensitive Data**
- Don't log message content
- Sanitize error messages
- Use HTTPS for all API calls

## Deployment Considerations

### Database Migration

**No Schema Changes Required**
- Existing `Session.user_account` FK supports this feature
- Existing `Session.ended_at` field tracks completion
- No migration needed

### Configuration

**Environment Variables**
- No new environment variables required
- Uses existing Django API URL configuration

### Rollout Strategy

**Phase 1: Backend Deployment**
1. Deploy new Django endpoint (`/api/users/sessions/save`)
2. Verify endpoint works with test requests
3. Monitor for errors

**Phase 2: Frontend Deployment**
1. Deploy updated `voice-agent.js` with save functionality
2. Deploy updated `chat.html` with New Chat button handler
3. Monitor user interactions
4. Verify sessions are being saved correctly

**Phase 3: Monitoring**
1. Track save session success rate
2. Monitor API response times
3. Track user engagement with New Chat feature
4. Gather user feedback

### Rollback Plan

**If Issues Occur**
1. Revert frontend changes (button handler)
2. Keep backend endpoint (no harm if not called)
3. Investigate and fix issues
4. Redeploy when ready

**Data Integrity**
- No data loss risk (sessions still created normally)
- Existing sessions unaffected
- History feature continues to work with manually saved sessions

## Future Enhancements

### Potential Improvements

**1. Auto-Save**
- Automatically save sessions after period of inactivity
- Save sessions when user navigates away
- Implement beforeunload handler

**2. Session Naming**
- Allow users to name conversations
- Auto-generate names from first message
- Support renaming from history view

**3. Session Search**
- Full-text search across conversation history
- Filter by date range
- Filter by topic or keywords

**4. Session Export**
- Export conversations as text files
- Export as JSON for backup
- Share conversations via link

**5. Session Analytics**
- Track conversation duration
- Track message count per session
- Identify popular topics

## Diagrams

### Sequence Diagram: New Chat Flow

```
User          Frontend         Django API       FastAPI        LiveKit
 |               |                 |               |              |
 |--Click New--->|                 |               |              |
 |   Chat        |                 |               |              |
 |               |                 |               |              |
 |               |--POST /save---->|               |              |
 |               |   session       |               |              |
 |               |                 |--Associate--->|              |
 |               |                 |   with user   |              |
 |               |<---200 OK-------|               |              |
 |               |                 |               |              |
 |               |--DELETE---------|-------------->|              |
 |               |   /session/{id} |               |              |
 |               |                 |               |--Disconnect->|
 |               |<---200 OK-------|<--------------|              |
 |               |                 |               |              |
 |               |--Clear UI------>|               |              |
 |               |   state         |               |              |
 |               |                 |               |              |
 |               |--POST-----------|-------------->|              |
 |               |   /session      |               |              |
 |               |                 |               |--Connect---->|
 |               |<---session_id---|<--------------|              |
 |               |                 |               |              |
 |<--Ready-------|                 |               |              |
 |   for new     |                 |               |              |
 |   chat        |                 |               |              |
```

### State Diagram: Session Lifecycle

```
┌─────────────┐
│   Created   │ (FastAPI creates session)
│ user_account│
│   = NULL    │
└──────┬──────┘
       │
       │ User converses
       │
       ▼
┌─────────────┐
│   Active    │ (Utterances ingested)
│ ended_at    │
│   = NULL    │
└──────┬──────┘
       │
       │ User clicks "New Chat"
       │
       ▼
┌─────────────┐
│    Saved    │ (Associated with user)
│ user_account│
│   = User FK │
│ ended_at    │
│   = now()   │
└──────┬──────┘
       │
       │ User views history
       │
       ▼
┌─────────────┐
│  Retrieved  │ (Displayed in history)
└─────────────┘
```
