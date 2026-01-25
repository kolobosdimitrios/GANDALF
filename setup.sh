#!/bin/bash
###############################################################################
# GANDALF VM Setup Script
#
# This script sets up the GANDALF application environment and makes it
# ready to play when the VM is initialized at boot.
#
# Usage:
#   sudo bash setup.sh [ANTHROPIC_API_KEY]
#
# The script will:
# 1. Install system dependencies (MySQL, Python, Node.js, Claude Code CLI)
# 2. Set up MySQL database with credentials
# 3. Create Python virtual environment and install packages
# 4. Configure environment variables
# 5. Set up systemd services for Flask API and Pipeline Agent
# 6. Start all services
# 7. Verify everything is running
#
###############################################################################

set -euo pipefail

# Configuration
APP_DIR="/opt/apps/gandlf"
WEB_DIR="/var/www/projects/gandlf"
VENV_DIR="${APP_DIR}/venv"
LOG_DIR="/var/log/gandlf"
CONFIG_DIR="/etc/gandalf"
DB_NAME="gandalf_db"
DB_USER="gandalf_user"
DB_PASS="PQnIQQkNTn90kKF4"
DB_HOST="localhost"
DB_PORT="3306"
CLAUDE_CODE_VERSION="0.2.3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Banner
echo ""
echo "============================================================"
echo "  GANDALF VM Setup"
echo "  Making the application ready to play..."
echo "============================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# Get Anthropic API key from argument or environment
ANTHROPIC_API_KEY="${1:-${ANTHROPIC_API_KEY:-}}"

if [ -z "$ANTHROPIC_API_KEY" ]; then
    log_error "Anthropic API key is required"
    echo ""
    echo "Usage: sudo bash setup.sh [ANTHROPIC_API_KEY]"
    echo "   or: export ANTHROPIC_API_KEY='your-key' && sudo -E bash setup.sh"
    echo ""
    exit 1
fi

log "Anthropic API key provided"

###############################################################################
# Step 1: Install System Dependencies
###############################################################################

log "Step 1: Installing system dependencies..."

# Update package list
log_info "Updating package list..."
apt-get update -qq

# Install MySQL
if ! command -v mysql &> /dev/null; then
    log_info "Installing MySQL..."
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq mysql-server mysql-client
else
    log_info "MySQL already installed"
fi

# Install Python
if ! command -v python3 &> /dev/null; then
    log_info "Installing Python..."
    apt-get install -y -qq python3 python3-venv python3-pip
else
    log_info "Python already installed"
fi

# Install other dependencies
log_info "Installing additional dependencies..."
apt-get install -y -qq curl git build-essential libssl-dev

# Install Node.js for Claude Code CLI
if ! command -v node &> /dev/null; then
    log_info "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y -qq nodejs
else
    log_info "Node.js already installed"
fi

# Install Claude Code CLI
if ! command -v claude-code &> /dev/null; then
    log_info "Installing Claude Code CLI..."
    npm install -g @anthropic-ai/claude-code-cli@${CLAUDE_CODE_VERSION} 2>&1 | grep -v "npm WARN" || true
else
    log_info "Claude Code CLI already installed"
fi

log "System dependencies installed successfully"

###############################################################################
# Step 2: Setup MySQL Database
###############################################################################

log "Step 2: Setting up MySQL database..."

# Ensure MySQL is running
systemctl start mysql || true
systemctl enable mysql || true

# Wait for MySQL to be ready
log_info "Waiting for MySQL to be ready..."
for i in {1..30}; do
    if mysql -e "SELECT 1" &> /dev/null; then
        break
    fi
    sleep 1
done

# Create database and user
log_info "Creating database and user..."
mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" || true
mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'${DB_HOST}' IDENTIFIED BY '${DB_PASS}';" || true
mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'${DB_HOST}';" || true
mysql -e "FLUSH PRIVILEGES;" || true

# Store database credentials
mkdir -p "${CONFIG_DIR}"
chmod 700 "${CONFIG_DIR}"
cat > "${CONFIG_DIR}/db.env" <<EOF
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASS=${DB_PASS}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
EOF
chmod 600 "${CONFIG_DIR}/db.env"

log "MySQL database setup completed"

###############################################################################
# Step 3: Setup Application Directories
###############################################################################

log "Step 3: Setting up application directories..."

# Create application directories
mkdir -p "${APP_DIR}"
mkdir -p "${LOG_DIR}"
chmod 755 "${APP_DIR}"
chmod 755 "${LOG_DIR}"

# Copy application files from web directory to app directory
if [ -d "${WEB_DIR}" ]; then
    log_info "Copying application files..."
    rsync -a --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' \
        "${WEB_DIR}/" "${APP_DIR}/"
else
    log_warning "Web directory ${WEB_DIR} not found, skipping file copy"
fi

log "Application directories setup completed"

###############################################################################
# Step 4: Setup Python Virtual Environment
###############################################################################

log "Step 4: Setting up Python virtual environment..."

# Create virtual environment
if [ ! -d "${VENV_DIR}" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
else
    log_info "Virtual environment already exists"
fi

# Activate virtual environment
source "${VENV_DIR}/bin/activate"

# Upgrade pip
log_info "Upgrading pip..."
pip install --quiet --upgrade pip

# Install main requirements
if [ -f "${APP_DIR}/requirements.txt" ]; then
    log_info "Installing main requirements..."
    pip install --quiet -r "${APP_DIR}/requirements.txt"
else
    log_warning "Main requirements.txt not found, installing minimal packages..."
    pip install --quiet mysql-connector-python==8.3.0 flask==3.0.2 flask-cors==4.0.0 \
        gunicorn==21.2.0 python-dotenv==1.0.1 pydantic==2.6.1 httpx==0.26.0 \
        requests==2.31.0 orjson==3.9.15 structlog==24.1.0 anthropic==0.40.0
fi

# Install multi-agent requirements
if [ -f "${APP_DIR}/multi-agent/requirements.txt" ]; then
    log_info "Installing multi-agent requirements..."
    pip install --quiet -r "${APP_DIR}/multi-agent/requirements.txt"
fi

deactivate

log "Python environment setup completed"

###############################################################################
# Step 5: Configure Environment Variables
###############################################################################

log "Step 5: Configuring environment variables..."

# Create .env file
cat > "${APP_DIR}/.env" <<EOF
# GANDALF Environment Configuration
# Auto-generated by setup.sh on $(date)

# ===================================
# Anthropic API Key
# ===================================
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

# ===================================
# Model Configuration
# ===================================
GANDALF_ENABLE_HAIKU=true
GANDALF_ENABLE_OPUS=true
GANDALF_DEFAULT_MODEL=sonnet
GANDALF_FORCE_MODEL=

# ===================================
# Service Configuration
# ===================================
GANDALF_AGENT_PORT=8080
GANDALF_PIPELINE_PORT=8081
GANDALF_PIPELINE_ENDPOINT=http://localhost:8081
FLASK_PORT=5000
FLASK_ENV=production
FLASK_DEBUG=false

# ===================================
# Token Limits
# ===================================
GANDALF_MAX_TOKENS_HAIKU=2000
GANDALF_MAX_TOKENS_SONNET=4000
GANDALF_MAX_TOKENS_OPUS=8000

# ===================================
# Database Configuration
# ===================================
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASS=${DB_PASS}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}

# ===================================
# Logging Configuration
# ===================================
LOG_LEVEL=INFO
EOF

chmod 600 "${APP_DIR}/.env"

log "Environment configuration completed"

###############################################################################
# Step 6: Setup Systemd Services
###############################################################################

log "Step 6: Setting up systemd services..."

# Create Flask API service
log_info "Creating Flask API service..."
cat > /etc/systemd/system/gandalf-api.service <<EOF
[Unit]
Description=GANDALF Flask API Service
After=network.target mysql.service
Documentation=file://${APP_DIR}/QUICK_REFERENCE.md

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=${APP_DIR}/.env

ExecStart=${VENV_DIR}/bin/gunicorn \\
    --workers 4 \\
    --bind 0.0.0.0:5000 \\
    --timeout 120 \\
    --graceful-timeout 30 \\
    --access-logfile ${LOG_DIR}/api-access.log \\
    --error-logfile ${LOG_DIR}/api-error.log \\
    --log-level info \\
    api.app:app

Restart=on-failure
RestartSec=5s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=gandalf-api

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Create Pipeline Agent service
log_info "Creating Pipeline Agent service..."
cat > /etc/systemd/system/gandalf-pipeline.service <<EOF
[Unit]
Description=GANDALF Pipeline Agent Service
After=network.target
Documentation=file://${APP_DIR}/multi-agent/README.md

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}/multi-agent
Environment="PATH=${VENV_DIR}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=${APP_DIR}/.env

ExecStart=${VENV_DIR}/bin/python3 pipeline_agent_service.py

Restart=on-failure
RestartSec=5s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=gandalf-pipeline

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Create AI Agent service (legacy, for backward compatibility)
log_info "Creating AI Agent service..."
cat > /etc/systemd/system/gandalf-ai-agent.service <<EOF
[Unit]
Description=GANDALF AI Agent Service (Legacy)
After=network.target
Documentation=file://${APP_DIR}/multi-agent/README.md

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}/multi-agent
Environment="PATH=${VENV_DIR}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=${APP_DIR}/.env

ExecStart=${VENV_DIR}/bin/gunicorn \\
    --workers 2 \\
    --bind 0.0.0.0:8080 \\
    --timeout 120 \\
    --graceful-timeout 30 \\
    --access-logfile ${LOG_DIR}/ai-agent-access.log \\
    --error-logfile ${LOG_DIR}/ai-agent-error.log \\
    --log-level info \\
    ai_agent_service:app

Restart=on-failure
RestartSec=5s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=gandalf-ai-agent

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
systemctl daemon-reload

log "Systemd services created"

###############################################################################
# Step 7: Start Services
###############################################################################

log "Step 7: Starting services..."

# Enable services to start on boot
log_info "Enabling services..."
systemctl enable gandalf-pipeline.service
systemctl enable gandalf-api.service

# Start Pipeline Agent first (API depends on it)
log_info "Starting Pipeline Agent service..."
systemctl start gandalf-pipeline.service
sleep 3

# Start Flask API
log_info "Starting Flask API service..."
systemctl start gandalf-api.service
sleep 3

log "Services started"

###############################################################################
# Step 8: Verification
###############################################################################

log "Step 8: Verifying installation..."

# Check MySQL
log_info "Checking MySQL..."
if mysql -e "SELECT 1" &> /dev/null; then
    log_info "✓ MySQL is running"
else
    log_error "✗ MySQL is not running"
fi

# Check database exists
if mysql -e "USE ${DB_NAME}" &> /dev/null; then
    log_info "✓ Database '${DB_NAME}' exists"
else
    log_error "✗ Database '${DB_NAME}' does not exist"
fi

# Check Python virtual environment
if [ -d "${VENV_DIR}" ]; then
    log_info "✓ Python virtual environment exists"
    PACKAGE_COUNT=$(${VENV_DIR}/bin/pip freeze | wc -l)
    log_info "  Installed packages: ${PACKAGE_COUNT}"
else
    log_error "✗ Python virtual environment not found"
fi

# Check Claude Code CLI
if command -v claude-code &> /dev/null; then
    log_info "✓ Claude Code CLI installed"
else
    log_warning "✗ Claude Code CLI not found"
fi

# Check services
log_info "Checking services status..."
if systemctl is-active --quiet gandalf-pipeline.service; then
    log_info "✓ Pipeline Agent service is running"
else
    log_error "✗ Pipeline Agent service is not running"
    systemctl status gandalf-pipeline.service --no-pager || true
fi

if systemctl is-active --quiet gandalf-api.service; then
    log_info "✓ Flask API service is running"
else
    log_error "✗ Flask API service is not running"
    systemctl status gandalf-api.service --no-pager || true
fi

# Test API health endpoint
log_info "Testing API health endpoint..."
sleep 2
if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
    log_info "✓ API health check passed"
    curl -s http://localhost:5000/health | head -n 5
else
    log_warning "✗ API health check failed (may need more time to start)"
fi

# Test Pipeline Agent status
log_info "Testing Pipeline Agent status..."
if curl -f -s http://localhost:8081/health > /dev/null 2>&1; then
    log_info "✓ Pipeline Agent health check passed"
else
    log_warning "✗ Pipeline Agent health check failed (may need more time to start)"
fi

log "Verification completed"

###############################################################################
# Summary
###############################################################################

echo ""
echo "============================================================"
echo "  GANDALF SETUP COMPLETE"
echo "============================================================"
echo ""
log_info "Application Directory: ${APP_DIR}"
log_info "Log Directory: ${LOG_DIR}"
log_info "Configuration Directory: ${CONFIG_DIR}"
echo ""
log_info "Database:"
log_info "  Name: ${DB_NAME}"
log_info "  User: ${DB_USER}"
log_info "  Host: ${DB_HOST}:${DB_PORT}"
echo ""
log_info "Services:"
log_info "  Flask API:       http://localhost:5000"
log_info "  Pipeline Agent:  http://localhost:8081"
log_info "  AI Agent:        http://localhost:8080 (legacy)"
echo ""
log_info "Service Management:"
log_info "  Status:  systemctl status gandalf-api.service"
log_info "           systemctl status gandalf-pipeline.service"
log_info "  Logs:    journalctl -u gandalf-api.service -f"
log_info "           journalctl -u gandalf-pipeline.service -f"
log_info "  Restart: systemctl restart gandalf-api.service"
log_info "           systemctl restart gandalf-pipeline.service"
echo ""
log_info "Test API:"
log_info "  curl http://localhost:5000/health"
log_info "  curl http://localhost:5000/api/agent/status"
echo ""
log_info "Logs available at: ${LOG_DIR}/"
echo ""
echo "============================================================"
echo "  VM is ready to play!"
echo "============================================================"
echo ""
