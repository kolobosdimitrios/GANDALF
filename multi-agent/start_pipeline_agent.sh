#!/bin/bash

###############################################################################
# GANDALF Pipeline Agent Service Startup Script
#
# Starts the multi-model pipeline AI agent service for GANDALF.
#
# Usage:
#   ./start_pipeline_agent.sh
#
# Environment Variables:
#   ANTHROPIC_API_KEY - Required: Your Anthropic API key
#   GANDALF_ENABLE_HAIKU - Optional: Enable Haiku model (default: true)
#   GANDALF_ENABLE_OPUS - Optional: Enable Opus model (default: true)
#   GANDALF_DEFAULT_MODEL - Optional: Default model (default: sonnet)
#   GANDALF_AGENT_PORT - Optional: Service port (default: 8080)
#   FLASK_DEBUG - Optional: Debug mode (default: false)
###############################################################################

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "GANDALF Pipeline Agent Service"
echo "============================================================"
echo ""

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ERROR: ANTHROPIC_API_KEY environment variable not set"
    echo ""
    echo "Please set your Anthropic API key:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    exit 1
fi

echo "✓ ANTHROPIC_API_KEY is set"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check if required packages are installed
echo ""
echo "Checking dependencies..."

if ! python3 -c "import anthropic" 2>/dev/null; then
    echo "❌ ERROR: anthropic package not installed"
    echo ""
    echo "Install with: pip install anthropic"
    echo ""
    exit 1
fi
echo "✓ anthropic package installed"

if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ ERROR: flask package not installed"
    echo ""
    echo "Install with: pip install flask"
    echo ""
    exit 1
fi
echo "✓ flask package installed"

if ! python3 -c "import httpx" 2>/dev/null; then
    echo "⚠️  WARNING: httpx package not installed (needed for client)"
    echo "   Install with: pip install httpx"
fi

# Display configuration
echo ""
echo "Configuration:"
echo "  Enable Haiku: ${GANDALF_ENABLE_HAIKU:-true}"
echo "  Enable Opus: ${GANDALF_ENABLE_OPUS:-true}"
echo "  Default Model: ${GANDALF_DEFAULT_MODEL:-sonnet}"
echo "  Force Model: ${GANDALF_FORCE_MODEL:-none}"
echo "  Service Port: ${GANDALF_AGENT_PORT:-8080}"
echo "  Debug Mode: ${FLASK_DEBUG:-false}"
echo ""

# Check if port is already in use
PORT=${GANDALF_AGENT_PORT:-8080}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  WARNING: Port $PORT is already in use"
    echo ""
    echo "Existing process:"
    lsof -Pi :$PORT -sTCP:LISTEN
    echo ""
    read -p "Kill existing process and continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Killing existing process..."
        lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        echo "Exiting..."
        exit 1
    fi
fi

# Run tests before starting
echo "Running tests..."
if python3 test_pipeline.py; then
    echo ""
    echo "✓ All tests passed!"
else
    echo ""
    echo "❌ Tests failed. Please fix before starting service."
    exit 1
fi

echo ""
echo "============================================================"
echo "Starting Pipeline Agent Service on port $PORT"
echo "============================================================"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the service
python3 pipeline_agent_service.py
