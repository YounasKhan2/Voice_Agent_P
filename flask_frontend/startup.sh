#!/bin/bash
# Azure App Service startup script for Flask Frontend

echo "Starting Flask Frontend deployment..."

# Install dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Get port from Azure environment variable (default 5173)
PORT=${PORT:-5173}

echo "Starting gunicorn on port $PORT..."
# Start gunicorn with production settings
gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120
