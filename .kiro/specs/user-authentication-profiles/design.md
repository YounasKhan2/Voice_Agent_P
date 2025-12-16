# Design Document: User Authentication and Profiles

## Overview

This design extends the existing Voice Agent system with user authentication, profiles, preferences, and conversation history while maintaining full backward compatibility with anonymous sessions. The implementation uses Django's built-in authentication and session framework, ensuring security and simplicity.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flask Frontend                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  /login  │  │ /signup  │  │  /chat   │  │ /history │       │
│  │  (new)   │  │  (new)   │  │(existing)│  │  (new)   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│       │             │              │              │              │
│       └─────────────┴──────────────┴──────────────┘              │
│                          │                                        │
│                   Session Cookie                                 │
└───────────────────────────┼──────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│  Django Backend  │                  │ FastAPI Backend  │
│   (Enhanced)     │◄─────────────────│   (Enhanced)     │
│                  │  Validate Session│                  │
│  ┌────────────┐  │                  │  ┌────────────┐  │
│  │   Auth     │  │                  │  │  Agent     │  │
│  │ Endpoints  │  │                  │  │  Manager   │  │
│  │   (new)    │  │                  │  │ (existing) │  │
│  └────────────┘  │                  │  └────────────┘  │
│  ┌────────────┐  │                  │                  │
│  │   User     │  │                  │                  │
│  │   Models   │  │                  │                  │
│  │   (new)    │  │                  │                  │
│  └────────────┘  │                  │                  │
│  ┌────────────┐  │                  │                  │
│  │  Session   │  │                  │                  │
│  │  Utterance │  │                  │                  │
│  │ (existing) │  │                  │                  │
│  └────────────┘  │                  │                  │
└──────────────────┘                  └──────────────────┘
         │                                     │
         └─────────────┬───────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  LiveKit Server │
              │   (unchanged)   │
              └─────────────────┘
```

## Key Design Principles

### 1. Backward Compatibility
- All existing endpoints remain unchanged
- Anonymous sessions continue to work without modification
- No changes to existing database tables (only additions)
- FastAPI backend remains functional for anonymous users

### 2. Separation of Concerns
- Django: Authentication, user data, persistence
- FastAPI: LiveKit orchestration, real-time voice
- Flask: UI rendering, static assets

### 3. Security First
- HTTP-only session cookies
- CSRF protection enabled
- Password hashing via Django's PBKDF2
- Secure cookie flags in production

## Data Models

### New Models (Django)

#### User Model
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Uses email as the primary identifier.
    """
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']
    
    class Meta:
        db_table = 'auth_user'
        indexes = [
            models.Index(fields=['email']),
        ]
```

#### UserPreferences Model
```python
class UserPreferences(models.Model):
    """
    Stores user-specific preferences for voice agent behavior.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_voice = models.CharField(max_length=50, default='alloy')
    preferred_language = models.CharField(max_length=10, default='en')
    favorite_topics = models.JSONField(default=list, blank=True)
    system_prompt_override = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'
```

### Modified Models (Django)

#### Session Model (No Changes Required)
```python
class Session(models.Model):
    """
    Existing model - NO MODIFICATIONS.
    The user_id field already exists and is nullable.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.CharField(max_length=128)
    user_id = models.CharField(max_length=128, blank=True, null=True)  # Already exists!
    system_prompt = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
```

**Migration Strategy**: Add a foreign key relationship in a new migration without modifying existing data:
```python
# New migration only
user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
```

#### Utterance Model (No Changes)
```python
class Utterance(models.Model):
    """
    Existing model - NO MODIFICATIONS NEEDED.
    """
    # ... existing fields remain unchanged
```

## API Endpoints

### New Django Endpoints

#### Authentication Endpoints

**POST /api/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "password": "securepass123",
  "display_name": "John Doe"
}

Response (201 Created):
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}

Sets session cookie: sessionid=<encrypted-session-id>
```

**POST /api/auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "securepass123"
}

Response (200 OK):
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "John Doe"
}

Sets session cookie: sessionid=<encrypted-session-id>
```

**POST /api/auth/logout**
```json
Request: (empty body, requires session cookie)

Response (200 OK):
{
  "message": "Logged out successfully"
}

Clears session cookie
```

**GET /api/auth/me**
```json
Request: (requires session cookie)

Response (200 OK):
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z"
}

Response (401 Unauthorized) if not authenticated:
{
  "authenticated": false
}
```

#### User Profile Endpoints

**GET /api/users/profile**
```json
Request: (requires session cookie)

Response (200 OK):
{
  "id": "uuid",
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

**PATCH /api/users/profile**
```json
Request:
{
  "display_name": "Jane Doe"
}

Response (200 OK):
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "Jane Doe",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**PUT /api/users/preferences**
```json
Request:
{
  "preferred_voice": "nova",
  "preferred_language": "es",
  "favorite_topics": ["travel", "technology"]
}

Response (200 OK):
{
  "preferred_voice": "nova",
  "preferred_language": "es",
  "favorite_topics": ["travel", "technology"],
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### History Endpoints

**GET /api/users/history**
```json
Request: (requires session cookie)
Query params: ?limit=20&offset=0

Response (200 OK):
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
      "utterance_count": 24,
      "system_prompt": "You are a friendly travel assistant."
    }
  ]
}
```

**GET /api/users/history/{session_id}**
```json
Request: (requires session cookie)

Response (200 OK):
{
  "id": "session-uuid",
  "room": "quickstart",
  "started_at": "2024-01-01T10:00:00Z",
  "ended_at": "2024-01-01T10:15:00Z",
  "system_prompt": "You are a friendly travel assistant.",
  "utterances": [
    {
      "id": "utterance-uuid",
      "role": "agent",
      "text": "Hello! How can I help you today?",
      "created_at": "2024-01-01T10:00:05Z"
    },
    {
      "id": "utterance-uuid",
      "role": "user",
      "text": "I want to plan a trip to Paris.",
      "created_at": "2024-01-01T10:00:12Z"
    }
  ]
}

Response (404 Not Found) if session doesn't belong to user:
{
  "detail": "Session not found"
}
```

### Enhanced FastAPI Endpoints

#### Session Start (Enhanced)

**POST /session** (existing endpoint, enhanced)
```json
Request:
{
  "room": "quickstart",
  "identity": "user-123",
  "system_prompt": "You are a friendly travel assistant."
}

Headers (optional):
Cookie: sessionid=<session-cookie>

Response (200 OK):
{
  "session_id": "uuid"
}

Behavior:
- If session cookie present and valid:
  - Validate with Django
  - Extract user_id
  - Apply user preferences (voice, language, prompt override)
  - Link session to user in metadata
- If no session cookie:
  - Create anonymous session (existing behavior)
  - No user_id in metadata
```

## Component Design

### Django Backend Components

#### Authentication Views
```python
# django_backend/api/auth_views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer, RegisterSerializer

@api_view(['POST'])
def register_view(request):
    """Register a new user and create session."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)  # Creates session
        return Response(UserSerializer(user).data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def login_view(request):
    """Authenticate user and create session."""
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)
    if user:
        login(request, user)  # Creates session
        return Response(UserSerializer(user).data)
    return Response({'detail': 'Invalid credentials'}, status=401)

@api_view(['POST'])
def logout_view(request):
    """Destroy session."""
    logout(request)  # Destroys session
    return Response({'message': 'Logged out successfully'})

@api_view(['GET'])
def me_view(request):
    """Get current authenticated user."""
    if request.user.is_authenticated:
        return Response(UserSerializer(request.user).data)
    return Response({'authenticated': False}, status=401)
```

#### Session Validation Endpoint
```python
# django_backend/api/session_validation.py

@api_view(['POST'])
def validate_session(request):
    """
    Internal endpoint for FastAPI to validate session cookies.
    Not exposed publicly.
    """
    if request.user.is_authenticated:
        # Get user preferences
        try:
            prefs = request.user.preferences
            preferences = {
                'preferred_voice': prefs.preferred_voice,
                'preferred_language': prefs.preferred_language,
                'system_prompt_override': prefs.system_prompt_override,
            }
        except UserPreferences.DoesNotExist:
            preferences = {}
        
        return Response({
            'valid': True,
            'user_id': str(request.user.id),
            'email': request.user.email,
            'display_name': request.user.display_name,
            'preferences': preferences
        })
    return Response({'valid': False}, status=401)
```

### FastAPI Backend Enhancements

#### Session Validation Utility
```python
# Backend/app/utils/auth.py

import httpx
from typing import Optional, Dict
from ..config import get_settings

async def validate_session_cookie(session_cookie: str) -> Optional[Dict]:
    """
    Validate session cookie with Django backend.
    Returns user data if valid, None if invalid.
    """
    settings = get_settings()
    if not settings.django_base_url:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.django_base_url}/api/internal/validate-session",
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

#### Enhanced Session Start
```python
# Backend/app/main.py (enhanced)

from fastapi import Cookie
from .utils.auth import validate_session_cookie

@app.post("/session", response_model=SessionStartResponse)
async def start_session(
    req: SessionStartRequest,
    sessionid: Optional[str] = Cookie(None)
):
    """
    Start agent session.
    If sessionid cookie present, validate and link to user.
    """
    user_data = None
    if sessionid:
        user_data = await validate_session_cookie(sessionid)
    
    # Determine system prompt
    instructions = req.system_prompt or settings.system_prompt
    if user_data and user_data.get('preferences', {}).get('system_prompt_override'):
        instructions = user_data['preferences']['system_prompt_override']
    
    # Start session with user context
    session_id = await agent_manager.start_session(
        room_name=req.room,
        instructions=instructions,
        user_id=user_data.get('user_id') if user_data else None,
        user_preferences=user_data.get('preferences') if user_data else None
    )
    
    return {"session_id": session_id}
```

#### Enhanced Agent Manager
```python
# Backend/app/agent.py (enhanced)

class AgentManager:
    async def start_session(
        self,
        room_name: str,
        instructions: str,
        user_id: Optional[str] = None,
        user_preferences: Optional[Dict] = None
    ) -> str:
        """
        Start agent session with optional user context.
        """
        settings = get_settings()
        
        # Apply user preferences if available
        tts_voice = settings.tts_voice
        if user_preferences and user_preferences.get('preferred_voice'):
            tts_voice = user_preferences['preferred_voice']
        
        # Build pipeline with user preferences
        # ... existing STT/LLM setup ...
        
        if settings.tts_provider.lower() == "cartesia" and settings.cartesia_api_key:
            tts_engine = cartesia.TTS(
                api_key=settings.cartesia_api_key,
                voice=tts_voice
            )
        else:
            tts_engine = openai.TTS(
                api_key=settings.openai_api_key,
                voice=tts_voice
            )
        
        # ... rest of existing session setup ...
        
        session_id = str(uuid.uuid4())
        
        # Enhanced metadata with user context
        session_meta = {
            "id": session_id,
            "room": room_name,
            "system_prompt": instructions,
            "user_id": user_id,  # Will be None for anonymous sessions
        }
        
        # ... rest of existing code ...
```

### Flask Frontend Components

#### New Routes
```python
# flask_frontend/app.py (enhanced)

from flask import session, redirect, url_for, request
import requests

DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://127.0.0.1:9000/api")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Forward to Django
        response = requests.post(
            f"{DJANGO_API_URL}/auth/login",
            json=request.form.to_dict()
        )
        if response.status_code == 200:
            # Django sets session cookie automatically
            return redirect(url_for("chat"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        response = requests.post(
            f"{DJANGO_API_URL}/auth/register",
            json=request.form.to_dict()
        )
        if response.status_code == 201:
            return redirect(url_for("chat"))
        return render_template("signup.html", error=response.json())
    return render_template("signup.html")

@app.route("/logout")
def logout():
    requests.post(f"{DJANGO_API_URL}/auth/logout")
    return redirect(url_for("index"))

@app.route("/history")
def history():
    # Check if user is authenticated
    response = requests.get(f"{DJANGO_API_URL}/auth/me")
    if response.status_code != 200:
        return redirect(url_for("login"))
    
    # Get user's history
    history_response = requests.get(f"{DJANGO_API_URL}/users/history")
    sessions = history_response.json().get('results', [])
    
    return render_template("history.html", sessions=sessions)

@app.route("/history/<session_id>")
def history_detail(session_id):
    response = requests.get(f"{DJANGO_API_URL}/users/history/{session_id}")
    if response.status_code != 200:
        return redirect(url_for("history"))
    
    session_data = response.json()
    return render_template("history_detail.html", session=session_data)

@app.route("/profile")
def profile():
    response = requests.get(f"{DJANGO_API_URL}/users/profile")
    if response.status_code != 200:
        return redirect(url_for("login"))
    
    user_data = response.json()
    return render_template("profile.html", user=user_data)
```

#### Enhanced Chat Page
```python
@app.route("/chat")
def chat():
    # Check authentication status
    auth_response = requests.get(f"{DJANGO_API_URL}/auth/me")
    user = None
    if auth_response.status_code == 200:
        user = auth_response.json()
    
    config = {
        "fastapiBaseUrl": FASTAPI_BASE_URL,
        "livekitUrl": LIVEKIT_URL,
        "defaultRoom": DEFAULT_ROOM,
        "systemPrompt": SYSTEM_PROMPT,
        "user": user  # Pass user data to template
    }
    return render_template("chat.html", config=config)
```

## UI Templates

### Login Page Template
```html
<!-- flask_frontend/templates/login.html -->
{% extends "base.html" %}

{% block content %}
<div class="auth-container">
  <h1>Login</h1>
  
  {% if error %}
  <div class="error-message">{{ error }}</div>
  {% endif %}
  
  <form method="POST" action="{{ url_for('login') }}">
    <div class="form-group">
      <label for="email">Email</label>
      <input type="email" id="email" name="email" required>
    </div>
    
    <div class="form-group">
      <label for="password">Password</label>
      <input type="password" id="password" name="password" required>
    </div>
    
    <button type="submit" class="btn-primary">Login</button>
  </form>
  
  <p>Don't have an account? <a href="{{ url_for('signup') }}">Sign up</a></p>
  <p><a href="{{ url_for('chat') }}">Continue as guest</a></p>
</div>
{% endblock %}
```

### Enhanced Chat Page Template
```html
<!-- flask_frontend/templates/chat.html (enhanced) -->
{% extends "base.html" %}

{% block content %}
<div class="chat-container">
  <!-- User info bar (new) -->
  {% if config.user %}
  <div class="user-bar">
    <span>Welcome, {{ config.user.display_name }}</span>
    <a href="{{ url_for('profile') }}">Profile</a>
    <a href="{{ url_for('history') }}">History</a>
    <a href="{{ url_for('logout') }}">Logout</a>
  </div>
  {% else %}
  <div class="user-bar">
    <span>Guest Mode</span>
    <a href="{{ url_for('login') }}">Login</a>
    <a href="{{ url_for('signup') }}">Sign Up</a>
  </div>
  {% endif %}
  
  <!-- Existing chat UI -->
  <div id="transcript-container"></div>
  <button id="start-btn">Start Conversation</button>
  <button id="stop-btn" disabled>Stop</button>
  
  <audio id="agent-audio" autoplay></audio>
</div>

<script>
  window.APP_CONFIG = {{ config | tojson }};
</script>
<script src="{{ url_for('static', filename='js/voice-agent.js') }}"></script>
{% endblock %}
```

### History Page Template
```html
<!-- flask_frontend/templates/history.html -->
{% extends "base.html" %}

{% block content %}
<div class="history-container">
  <h1>Conversation History</h1>
  
  <div class="session-list">
    {% for session in sessions %}
    <div class="session-card">
      <h3>{{ session.started_at | format_datetime }}</h3>
      <p>Room: {{ session.room }}</p>
      <p>Duration: {{ session.ended_at - session.started_at }}</p>
      <p>Messages: {{ session.utterance_count }}</p>
      <a href="{{ url_for('history_detail', session_id=session.id) }}">View Transcript</a>
    </div>
    {% endfor %}
  </div>
  
  {% if not sessions %}
  <p>No conversation history yet. <a href="{{ url_for('chat') }}">Start a conversation</a></p>
  {% endif %}
</div>
{% endblock %}
```

## Security Considerations

### Session Cookie Configuration
```python
# django_backend/config/settings.py

# Session configuration
SESSION_COOKIE_AGE = 1209600  # 14 days
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS only in production
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_NAME = 'sessionid'

# CSRF configuration
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Lax'

# CORS configuration (allow Flask frontend)
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:5173',
    'http://localhost:5173',
]
CORS_ALLOW_CREDENTIALS = True  # Required for cookies
```

### Password Security
```python
# Django's default password hashers (already configured)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

## Migration Strategy

### Phase 1: Database Setup (No Breaking Changes)
1. Create User and UserPreferences models
2. Run migrations (adds new tables only)
3. Add foreign key to Session model (nullable, no data changes)
4. Verify existing sessions still work

### Phase 2: Django Backend (Additive)
1. Add authentication endpoints
2. Add user profile endpoints
3. Add history endpoints
4. Add session validation endpoint
5. Test with Postman/curl

### Phase 3: FastAPI Enhancement (Backward Compatible)
1. Add session cookie validation utility
2. Enhance session start endpoint (optional cookie)
3. Test anonymous sessions still work
4. Test authenticated sessions work

### Phase 4: Flask Frontend (Additive)
1. Add login/signup templates
2. Add history templates
3. Add profile template
4. Enhance chat template with user bar
5. Test guest mode still works

### Phase 5: Integration Testing
1. Test anonymous flow (existing behavior)
2. Test registration → login → chat → history
3. Test preferences application
4. Test logout and re-login

## Error Handling

### Authentication Errors
```python
# Consistent error responses
{
  "detail": "Invalid credentials",
  "code": "invalid_credentials"
}

{
  "detail": "Session expired",
  "code": "session_expired"
}

{
  "detail": "Email already registered",
  "code": "email_exists"
}
```

### Graceful Degradation
- If Django is down: Anonymous sessions continue to work
- If session validation fails: Fall back to anonymous mode
- If preferences can't be loaded: Use system defaults

## Testing Strategy

### Unit Tests
- User model creation and validation
- Password hashing and verification
- Session cookie generation
- Preference storage and retrieval

### Integration Tests
- Registration flow end-to-end
- Login flow end-to-end
- Session validation between FastAPI and Django
- History retrieval with proper filtering

### Manual Testing Checklist
- [ ] Anonymous session works (existing behavior)
- [ ] User can register
- [ ] User can login
- [ ] User can start authenticated session
- [ ] User preferences are applied
- [ ] User can view history
- [ ] User can logout
- [ ] Session persists across browser refresh
- [ ] Session expires after configured time

## Deployment Considerations

### Environment Variables
```bash
# Django
SECRET_KEY=<random-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# FastAPI
DJANGO_BASE_URL=https://yourdomain.com

# Flask
DJANGO_API_URL=https://yourdomain.com/api
```

### Database Indexes
```python
# Add indexes for performance
class Meta:
    indexes = [
        models.Index(fields=['user', '-started_at']),  # History queries
        models.Index(fields=['email']),  # Login queries
    ]
```

### Caching (Optional)
```python
# Use Redis for session storage in production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## Alternatives Considered

### JWT Tokens
- **Rejected**: More complex, requires manual token management, harder to revoke
- **Session-based is better**: Simpler, more secure, Django native

### Combined Flask+Django App
- **Rejected**: Tight coupling, harder to deploy independently
- **Separate services is better**: Clear separation of concerns, easier to scale

### OAuth2/Social Login
- **Deferred**: Can be added later without breaking changes
- **Email/password first**: Simpler MVP, covers core use case

## Future Enhancements

### Email Verification
- Add email verification flow
- Send verification emails on registration
- Require verification before full access

### Password Reset
- Add "Forgot Password" flow
- Send reset emails
- Secure token-based reset

### Social Login
- Add Google/Microsoft OAuth
- Link social accounts to existing users

### Advanced Preferences
- Custom agent personalities
- Voice speed/pitch controls
- Language-specific prompts

### Analytics
- Track user engagement
- Session duration metrics
- Popular topics analysis
