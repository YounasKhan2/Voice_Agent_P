# Backend startup script
Write-Host "Starting Voice Agent Backend..." -ForegroundColor Green

# Activate virtual environment
if (Test-Path .venv\Scripts\Activate.ps1) {
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    & .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
}

# Start uvicorn server
Write-Host "Starting FastAPI server on http://0.0.0.0:8000" -ForegroundColor Cyan
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
