#!/bin/bash
# GANDALF Web API Startup Script
# Starts the Flask API using gunicorn

set -e

# Configuration
APP_DIR="/var/www/projects/gandlf"
VENV_DIR="${APP_DIR}/venv"
WORKERS=4
BIND_ADDRESS="0.0.0.0:7000"
LOG_LEVEL="info"
ACCESS_LOG="/var/log/gandlf/web-access.log"
ERROR_LOG="/var/log/gandlf/web-error.log"

# Create log directory
mkdir -p /var/log/gandlf

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    source "${VENV_DIR}/bin/activate"
else
    echo "Error: Virtual environment not found at $VENV_DIR"
    exit 1
fi

# Change to app directory
cd "$APP_DIR"

# Start gunicorn
exec gunicorn \
    --workers $WORKERS \
    --bind $BIND_ADDRESS \
    --log-level $LOG_LEVEL \
    --access-logfile $ACCESS_LOG \
    --error-logfile $ERROR_LOG \
    --timeout 120 \
    --graceful-timeout 30 \
    api.app:app
