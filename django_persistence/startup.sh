#!/bin/bash
# Azure App Service startup script for Django Persistence Service

echo "Starting Django Persistence Service deployment..."

# Install dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Get port from Azure environment variable (default 9000)
PORT=${PORT:-9000}

echo "Starting gunicorn on port $PORT..."
# Start gunicorn with production settings
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
    