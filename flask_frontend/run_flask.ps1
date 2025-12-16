# Flask frontend startup script
Write-Host "Starting Voice Agent Flask Frontend..." -ForegroundColor Green

# Activate virtual environment
if (Test-Path .venv\Scripts\Activate.ps1) {
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    & .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
}

# Start Flask server
Write-Host "Starting Flask server on http://127.0.0.1:5173" -ForegroundColor Cyan
python app.py
