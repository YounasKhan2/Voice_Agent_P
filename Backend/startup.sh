#!/bin/bash
# Azure App Service startup script for FastAPI Backend

echo "Starting FastAPI Backend deployment..."

# Install dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Get port from Azure environment variable (default 8000)
PORT=${PORT:-8000}

echo "Starting uvicorn on port $PORT..."
# Start uvicorn with production settings
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
