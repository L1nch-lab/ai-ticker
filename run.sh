#!/bin/bash
# AI-Ticker Development Server Runner
# Usage: ./run.sh [port] [host]

set -e

# Default values
PORT=${1:-5000}
HOST=${2:-"0.0.0.0"}
APP_FILE="app-cleaned.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🤖 AI-Ticker Development Server${NC}"
echo "================================="

# Check if virtual environment exists
if [[ ! -d ".venv" && ! -d "venv" && -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  No virtual environment detected${NC}"
    echo "Create one with: python -m venv .venv && source .venv/bin/activate"
    echo "Then install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "Copy .env.example-new to .env and configure your API keys"
    exit 1
fi

# Check if required files exist
if [[ ! -f "$APP_FILE" ]]; then
    echo -e "${RED}❌ Application file $APP_FILE not found${NC}"
    echo "Available app files:"
    ls -la app*.py 2>/dev/null || echo "No app files found"
    exit 1
fi

if [[ ! -f "config.py" ]]; then
    echo -e "${RED}❌ config.py not found${NC}"
    exit 1
fi

# Validate dependencies
echo -e "${GREEN}📦 Checking dependencies...${NC}"
python -c "import flask, openai, rapidfuzz" 2>/dev/null || {
    echo -e "${RED}❌ Missing dependencies${NC}"
    echo "Install with: pip install -r requirements.txt"
    exit 1
}

# Check for API keys
echo -e "${GREEN}🔑 Checking API configuration...${NC}"
if ! grep -q "API_KEY=" .env || ! grep -E "API_KEY=.+" .env >/dev/null; then
    echo -e "${YELLOW}⚠️  No API keys configured in .env${NC}"
    echo "The app will run but won't be able to generate new messages"
fi

# Start the server
echo -e "${GREEN}🚀 Starting server on $HOST:$PORT${NC}"
echo "Press Ctrl+C to stop"
echo ""

export FLASK_APP="$APP_FILE"
export FLASK_ENV="development"

# Use gunicorn for production-like setup or flask for development
if command -v gunicorn >/dev/null; then
    echo "Using Gunicorn (production-like)"
    exec gunicorn --bind "$HOST:$PORT" --workers 1 --timeout 60 --access-logfile - app-cleaned:app
else
    echo "Using Flask development server"
    exec python "$APP_FILE"
fi
