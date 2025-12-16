# Voice Agent (FastAPI + Flask + Django + LiveKit)

End‑to‑end voice assistant with user authentication and conversation history:
- FastAPI backend orchestrating a LiveKit Agents session (VAD + STT + LLM + TTS)
- Flask UI (Jinja) with authentication pages and conversation history
- Django backend for user authentication, profiles, and persistence
- LiveKit Cloud (recommended) or local server

The system supports both authenticated and anonymous sessions. Authenticated users can save conversation history, set preferences (voice, language), and manage their profile. The backend mints browser tokens, starts/stops the server‑side agent, and broadcasts transcripts via WebSocket.

## Features

### Core Voice Features
- Real-time voice conversations with AI agent
- Speech-to-text (STT) using Deepgram or OpenAI
- Large language model (LLM) using OpenAI GPT-4o-mini or Grok
- Text-to-speech (TTS) using Cartesia or OpenAI
- Voice Activity Detection (VAD) using Silero
- Live transcript streaming via WebSocket

### User Authentication & Profiles
- User registration and login with email/password
- Session-based authentication with HTTP-only cookies
- User profile management (display name, email)
- Password change functionality
- Secure password hashing with PBKDF2

### User Preferences
- Preferred TTS voice selection (alloy, nova, etc.)
- Preferred language setting
- Favorite topics configuration
- Custom system prompt override
- Preferences automatically applied to voice sessions

### Conversation History
- Save and retrieve past conversations
- View full transcripts with timestamps
- Filter sessions by date
- Pagination support for large histories
- Anonymous sessions supported (not saved to history)

### Guest Mode
- Use the voice agent without creating an account
- Quick access for one-time conversations
- No data persistence for anonymous sessions

## Project Structure

```
Backend/                # FastAPI + LiveKit Agents core
	app/
		main.py             # REST + WS endpoints
		agent.py            # AgentSession pipeline (silero VAD + STT/LLM/TTS)
		config.py           # .env settings
		utils/
			livekit.py      # token minting helpers
			auth.py         # session validation with Django
	requirements.txt
	run_backend.ps1       # create venv, install, run uvicorn

flask_frontend/         # Flask UI (Jinja + vanilla JS)
	app.py                # serves pages and handles routing
	templates/
		base.html           # base template with navigation
		login.html          # user login page
		signup.html         # user registration page
		chat.html           # voice conversation interface
		profile.html        # user profile and preferences
		history.html        # conversation history list
		history_detail.html # full conversation transcript
	static/
		js/voice-agent.js   # LiveKit connection and UI logic
		css/style.css       # application styling
	requirements.txt
	run_flask.ps1

django_persistence/     # Django backend for auth and persistence
	config/
		settings.py         # Django configuration
		urls.py             # URL routing
	conversation/
		models.py           # User, UserPreferences, Session, Utterance
		views.py            # API endpoints
		serializers.py      # DRF serializers
		urls.py             # API URL patterns
	manage.py
	requirements.txt
```

## API Endpoints

### FastAPI Backend (Port 8000)
- `GET /health` — health check
- `GET /token?room=<room>&identity=<id>&name=<name>` — mint LiveKit client token
- `POST /session` — start server‑side agent in a room `{ room, identity, system_prompt? }`
- `DELETE /session/{session_id}` — stop agent session
- `WS /ws/transcript/{session_id}` — live transcripts/events

### Django Backend (Port 9000)

#### Authentication Endpoints
- `POST /api/auth/register` — register new user
- `POST /api/auth/login` — authenticate and create session
- `POST /api/auth/logout` — destroy session
- `GET /api/auth/me` — get current authenticated user

#### User Profile Endpoints
- `GET /api/users/profile` — get user profile with preferences
- `PATCH /api/users/profile` — update display name or email
- `PUT /api/users/preferences` — update user preferences
- `POST /api/users/change-password` — change password

#### History Endpoints
- `GET /api/users/history` — list user's conversation sessions
- `GET /api/users/history/{session_id}` — get full session transcript

#### Internal Endpoints (not public)
- `POST /api/internal/validate-session` — validate session for FastAPI

For detailed API documentation, see:
- [Authentication Endpoints](django_persistence/AUTH_ENDPOINTS.md)
- [User Profile Endpoints](django_persistence/USER_PROFILE_ENDPOINTS.md)
- [History Endpoints](django_persistence/HISTORY_ENDPOINTS.md)
- [Internal Endpoints](django_persistence/INTERNAL_ENDPOINTS.md)

### Flask Frontend Routes
- `GET /` — home page
- `GET /login` — login page
- `POST /login` — handle login form
- `GET /signup` — registration page
- `POST /signup` — handle registration form
- `GET /logout` — logout and redirect
- `GET /chat` — voice conversation interface
- `GET /profile` — user profile and preferences
- `POST /profile` — update profile
- `GET /history` — conversation history list
- `GET /history/<session_id>` — view specific conversation

## Configuration (.env)

### Backend Configuration
Create `Backend/.env` (not committed) with at least LiveKit + model keys:

```
LIVEKIT_URL=wss://<your-livekit>.livekit.cloud
LIVEKIT_API_KEY=<key>
LIVEKIT_API_SECRET=<secret>

# Provider keys (optional but recommended)
OPENAI_API_KEY=<key>
DEEPGRAM_API_KEY=<key>
CARTESIA_API_KEY=<key>

# Agent behavior
SYSTEM_PROMPT=You are a friendly travel assistant.

# CORS for local dev (keep defaults or customize)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Persistence service
DJANGO_BASE_URL=http://127.0.0.1:9000
INGEST_TOKEN=super-secret-token

# Optional provider selection
STT_PROVIDER=deepgram   # or openai
TTS_PROVIDER=openai     # or cartesia
LLM_PROVIDER=openai
TTS_VOICE=alloy

# Voice Activity Detection (VAD) Performance Tuning
VAD_MIN_SPEECH_DURATION=0.1
VAD_MIN_SILENCE_DURATION=0.3
VAD_PADDING_DURATION=0.1
```

### Flask Frontend Configuration
Create `flask_frontend/.env` to point UI at the backend and LiveKit URL (websocket scheme):

```
FASTAPI_BASE_URL=http://127.0.0.1:8000
LIVEKIT_URL=wss://<your-livekit>.livekit.cloud
DEFAULT_ROOM=quickstart
SYSTEM_PROMPT=You are a friendly travel assistant.
PORT=5173
DJANGO_API_URL=http://127.0.0.1:9000/api
SECRET_KEY=your-secret-key-here-change-in-production
```

### Django Persistence Configuration
Create `django_persistence/.env` for the persistence service:

```
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
ALLOW_INGEST_TOKEN=super-secret-token

# Session Configuration
SESSION_COOKIE_AGE=1209600
SESSION_COOKIE_SECURE=False

# CORS Configuration (comma-separated list of allowed origins)
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:8000,http://localhost:8000
```

## How to Run (Windows PowerShell)

From the repo root:

### 1) Start the Django persistence service
```powershell
cd django_persistence
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:9000
```

### 2) Start the FastAPI backend
```powershell
cd Backend
powershell -ExecutionPolicy Bypass -File run_backend.ps1
```

### 3) Start the Flask UI
```powershell
cd flask_frontend
powershell -ExecutionPolicy Bypass -File run_flask.ps1
```

### 4) Open the app
```
http://127.0.0.1:5173/
```

## User Flows

### Guest Mode (Anonymous)
1. Visit http://127.0.0.1:5173/chat
2. Click "Continue as Guest"
3. Start voice conversation
4. Conversation works but is not saved

### Authenticated Mode
1. Visit http://127.0.0.1:5173/signup
2. Create account with email and password
3. Automatically logged in and redirected to chat
4. Start voice conversation
5. Conversation is saved to history
6. View past conversations at /history
7. Update preferences at /profile

### Preference Application
1. Login to your account
2. Go to /profile
3. Set preferred voice (e.g., "nova")
4. Set preferred language (e.g., "es")
5. Start new conversation
6. Agent uses your preferred settings automatically

## Database Schema

### User Model
- `id` (UUID, primary key)
- `email` (unique, used for login)
- `password` (hashed with PBKDF2)
- `display_name` (shown in UI)
- `created_at`, `updated_at`

### UserPreferences Model
- `user` (one-to-one with User)
- `preferred_voice` (e.g., "alloy", "nova")
- `preferred_language` (e.g., "en", "es")
- `favorite_topics` (JSON array)
- `system_prompt_override` (custom prompt)

### Session Model
- `id` (UUID, primary key)
- `room` (LiveKit room name)
- `user_account` (foreign key to User, nullable)
- `user_id` (legacy string field, nullable)
- `system_prompt` (prompt used for session)
- `started_at`, `ended_at`
- `metadata` (JSON)

### Utterance Model
- `id` (UUID, primary key)
- `session` (foreign key to Session)
- `role` ("user", "agent", or "event")
- `text` (transcript text)
- `is_final` (boolean)
- `event` (event type if role is "event")
- `created_at`

## Security Features

### Authentication
- Session-based authentication using Django sessions
- HTTP-only cookies prevent XSS attacks
- Secure cookies in production (HTTPS only)
- SameSite=Lax prevents CSRF attacks
- 14-day session expiration

### Password Security
- PBKDF2 hashing with 100,000+ iterations
- Minimum 8 character requirement
- Common password validation
- Numeric password validation
- No password hashes in API responses or logs

### API Security
- CORS restricted to allowed origins
- Session validation for authenticated endpoints
- User data isolation (users only see their own data)
- Internal endpoints not exposed publicly

## Troubleshooting

### Common Issues

#### "CORS error when calling Django API"
**Solution**: Ensure `CORS_ALLOWED_ORIGINS` in Django `.env` includes your Flask frontend URL:
```
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

#### "Session cookie not being set"
**Solution**: 
- Check that `CORS_ALLOW_CREDENTIALS=True` in Django settings
- Ensure Flask and Django are on same domain or CORS is properly configured
- In production, set `SESSION_COOKIE_SECURE=True` and use HTTPS

#### "User preferences not applying to voice session"
**Solution**:
- Verify `DJANGO_BASE_URL` is set in FastAPI `.env`
- Check that FastAPI can reach Django at the configured URL
- Look for session validation errors in FastAPI logs
- Ensure user has set preferences in their profile

#### "Cannot access conversation history"
**Solution**:
- Verify you're logged in (check for "Welcome, [name]" in chat page)
- Ensure sessions were created while authenticated
- Anonymous sessions are not saved to history
- Check Django logs for database errors

#### "Audio not playing in browser"
**Solution**:
- Click "Start Conversation" button (user gesture required for autoplay)
- Check browser console for autoplay policy errors
- Ensure LiveKit URL is correct (wss:// for cloud, ws:// for local)
- Verify microphone permissions are granted

#### "Agent not responding"
**Solution**:
- Check that all three services are running (Django, FastAPI, Flask)
- Verify API keys are set correctly in Backend/.env
- Check FastAPI logs for errors
- Ensure LiveKit server is reachable

#### "Database migration errors"
**Solution**:
```powershell
cd django_persistence
python manage.py makemigrations
python manage.py migrate
```

#### "Port already in use"
**Solution**:
- Django: Change port in runserver command (default 9000)
- FastAPI: Change PORT in Backend/.env (default 8000)
- Flask: Change PORT in flask_frontend/.env (default 5173)

### Logging and Debugging

#### Enable Django Debug Mode
In `django_persistence/.env`:
```
DEBUG=True
```

#### View FastAPI Logs
FastAPI logs appear in the terminal where you ran `run_backend.ps1`

#### View Django Logs
Django logs appear in the terminal where you ran `manage.py runserver`

#### Browser Console
Open browser DevTools (F12) to see:
- JavaScript errors
- Network requests
- WebSocket messages
- LiveKit connection status

## Notes
- LiveKit URL for the browser must be websocket (`wss://` in cloud or `ws://` locally), not `https://`.
- The UI includes a hidden `<audio id="agent-audio">` element where the agent's TTS track is attached.
- Provider selection is driven by env; if a provider/key is missing, the backend falls back to OpenAI where possible.
- Session cookies expire after 14 days by default (configurable via `SESSION_COOKIE_AGE`).
- Anonymous sessions work without authentication and are not saved to history.

## Roadmap

### Completed Features
- ✅ Django persistence + admin (sessions/utterances)
- ✅ User authentication (registration, login, logout)
- ✅ User profiles and preferences
- ✅ Conversation history with full transcripts
- ✅ Session-based authentication with secure cookies
- ✅ Authenticated and anonymous session support
- ✅ User preference application to voice sessions
- ✅ Password management and security
- ✅ Flask UI for all user features

### Future Enhancements
- [ ] Email verification for new accounts
- [ ] Password reset via email
- [ ] Social login (Google, Microsoft)
- [ ] Advanced preference controls (voice speed, pitch)
- [ ] Session sharing and export
- [ ] Analytics dashboard
- [ ] Multi-language UI support
- [ ] Mobile-responsive improvements
- [ ] Voice activity visualization
- [ ] Conversation search and filtering

## Azure Deployment

Ready to deploy to Azure? We've got you covered:

- **[Quick Start Guide](AZURE_QUICK_START.md)** - Deploy in 30 minutes
- **[Full Deployment Guide](DEPLOYMENT.md)** - Comprehensive step-by-step instructions
- **[Deployment Checklist](DEPLOYMENT_CHECKLIST.md)** - Ensure nothing is missed
- **[Azure Architecture Guide](AZURE_DEPLOYMENT_GUIDE.md)** - Detailed architecture overview

### Quick Deploy to Azure

```bash
# 1. Create Azure resources
az group create --name wanderbot-rg --location eastus
az postgres flexible-server create --resource-group wanderbot-rg --name wanderbot-db ...
az webapp create --resource-group wanderbot-rg --name wanderbot-django ...

# 2. Configure environment variables
az webapp config appsettings set --name wanderbot-django --settings ...

# 3. Deploy via GitHub Actions
git push origin main
```

See [AZURE_QUICK_START.md](AZURE_QUICK_START.md) for complete commands.

## Documentation

### Project Documentation
- [Project Specification](docs/PROJECT_SPEC.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Design Document](docs/DESIGN.md)
- [Implementation Tasks](docs/TASKS.md)
- [Project Phases](docs/PHASES.md)

### API Documentation
- [Authentication Endpoints](django_persistence/AUTH_ENDPOINTS.md)
- [User Profile Endpoints](django_persistence/USER_PROFILE_ENDPOINTS.md)
- [History Endpoints](django_persistence/HISTORY_ENDPOINTS.md)
- [Internal Endpoints](django_persistence/INTERNAL_ENDPOINTS.md)

### Deployment Documentation
- [Azure Quick Start](AZURE_QUICK_START.md) - 30-minute deployment guide
- [Full Deployment Guide](DEPLOYMENT.md) - Comprehensive instructions
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) - Pre-flight checklist
- [Azure Architecture](AZURE_DEPLOYMENT_GUIDE.md) - Architecture overview

### Technical Documentation
- [Migration Summary](django_persistence/MIGRATION_SUMMARY.md)
- [Integration Test Results](django_persistence/INTEGRATION_TEST_RESULTS.md)

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
