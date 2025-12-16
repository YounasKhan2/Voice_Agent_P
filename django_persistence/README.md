# Django Persistence Service

Stores voice sessions and utterances for the Travel Voice Agent.

## Components
- Django + Django REST Framework
- Models: Session, Utterance
- Ingest endpoint secured by header (X-INGEST-TOKEN)
- Admin UI enabled

## Quick Start (Windows PowerShell)
```
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:9000
```

Env file `.env` (not committed):
```
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
ALLOW_INGEST_TOKEN=super-secret-token

# Session Configuration
SESSION_COOKIE_AGE=1209600
SESSION_COOKIE_SECURE=False

# CORS Configuration (comma-separated list of allowed origins)
# Include Flask frontend and FastAPI backend for internal API calls
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:8000,http://localhost:8000
```

## Environment Variables

### Required Variables
- `SECRET_KEY`: Django secret key for cryptographic signing (change in production!)
- `DEBUG`: Enable debug mode (set to False in production)
- `ALLOWED_HOSTS`: Comma-separated list of allowed host/domain names
- `ALLOW_INGEST_TOKEN`: Token for authenticating ingest requests from FastAPI backend

### Session Configuration
- `SESSION_COOKIE_AGE`: Session cookie lifetime in seconds (default: 1209600 = 14 days)
- `SESSION_COOKIE_SECURE`: Set to True in production to require HTTPS (default: False for local dev)

### CORS Configuration
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS requests
  - Must include Flask frontend URL for browser requests
  - Must include FastAPI backend URL for internal API calls
