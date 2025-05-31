#!/bin/bash
# Production startup script for AI-Ticker

set -e

# Production environment variables
export FLASK_ENV=production
export FLASK_HOST=127.0.0.1  # Secure default - use 0.0.0.0 only if needed
export FLASK_PORT=5000
export FLASK_DEBUG=false

# Security settings
export SECURE_SSL_REDIRECT=true
export SESSION_COOKIE_SECURE=true
export SESSION_COOKIE_HTTPONLY=true

echo "🚀 Starting AI-Ticker in production mode..."
echo "   Host: $FLASK_HOST"
echo "   Port: $FLASK_PORT"
echo "   Debug: $FLASK_DEBUG"

# Use Gunicorn in production
if command -v gunicorn &> /dev/null; then
    echo "📦 Using Gunicorn for production deployment"
    exec gunicorn --bind $FLASK_HOST:$FLASK_PORT --workers 2 --timeout 30 app:app
else
    echo "⚠️  Gunicorn not found, using Flask development server"
    echo "   Install Gunicorn for production: pip install gunicorn"
    python app.py
fi
