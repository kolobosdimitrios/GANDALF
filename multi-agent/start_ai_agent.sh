#!/bin/bash
#
# Start GANDALF AI Agent Service
# This script starts the multi-model AI agent service on port 8080
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}GANDALF AI Agent Service Startup${NC}"
echo -e "${GREEN}=====================================${NC}"

# Check if we're in the right directory
if [ ! -f "ai_agent_service.py" ]; then
    echo -e "${RED}Error: ai_agent_service.py not found${NC}"
    echo "Please run this script from /opt/apps/gandlf/multi-agent/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "/opt/gandalf/venv" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not found${NC}"
    echo "Creating virtual environment..."
    python3 -m venv /opt/gandalf/venv
    source /opt/gandalf/venv/bin/activate
    pip install -r ../requirements.txt
else
    source /opt/gandalf/venv/bin/activate
fi

# Check for .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}Loading environment from .env file${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Using environment variables or defaults"
fi

# Check for Anthropic API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY not set${NC}"
    echo "Please set ANTHROPIC_API_KEY environment variable or add it to .env file"
    echo "Get your key from: https://console.anthropic.com"
    exit 1
fi

# Create log directory if it doesn't exist
LOG_DIR="/var/log/gandalf"
if [ ! -d "$LOG_DIR" ]; then
    echo "Creating log directory: $LOG_DIR"
    sudo mkdir -p "$LOG_DIR"
    sudo chown -R $(whoami) "$LOG_DIR"
fi

# Display configuration
echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Working Directory: $(pwd)"
echo "  Virtual Env: /opt/gandalf/venv"
echo "  Port: ${GANDALF_AGENT_PORT:-8080}"
echo "  Enable Haiku: ${GANDALF_ENABLE_HAIKU:-true}"
echo "  Enable Opus: ${GANDALF_ENABLE_OPUS:-true}"
echo "  Default Model: ${GANDALF_DEFAULT_MODEL:-sonnet}"
echo "  Force Model: ${GANDALF_FORCE_MODEL:-none}"
echo "  Log Directory: $LOG_DIR"
echo ""

# Check if port is already in use
PORT=${GANDALF_AGENT_PORT:-8080}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Warning: Port $PORT is already in use${NC}"
    echo "Kill existing process? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        echo "Killing process on port $PORT..."
        kill $(lsof -t -i:$PORT) || true
        sleep 2
    else
        echo "Exiting..."
        exit 1
    fi
fi

# Start the service
echo -e "${GREEN}Starting AI Agent Service...${NC}"
echo ""

# Check if we should use gunicorn or development server
if [ "${FLASK_ENV}" = "development" ] || [ "${FLASK_DEBUG}" = "true" ]; then
    echo "Starting in development mode (Flask development server)"
    python ai_agent_service.py
else
    echo "Starting in production mode (Gunicorn)"
    gunicorn \
        --workers 2 \
        --bind 0.0.0.0:${PORT} \
        --timeout 120 \
        --graceful-timeout 30 \
        --access-logfile "${LOG_DIR}/ai-agent-access.log" \
        --error-logfile "${LOG_DIR}/ai-agent-error.log" \
        --log-level info \
        ai_agent_service:app
fi
