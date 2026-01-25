#!/bin/bash
###############################################################################
# GANDALF Setup Verification Script
#
# This script verifies that the GANDALF setup completed successfully
# and all services are running correctly.
#
# Usage: bash verify_setup.sh
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo ""
echo "============================================================"
echo "  GANDALF Setup Verification"
echo "============================================================"
echo ""

# Check 1: MySQL
echo "Checking MySQL..."
if systemctl is-active --quiet mysql; then
    if mysql -e "SELECT 1" &> /dev/null; then
        check_pass "MySQL is running"
    else
        check_fail "MySQL is running but not accessible"
    fi
else
    check_fail "MySQL service is not running"
fi

# Check 2: Database
if mysql -e "USE gandalf_db" &> /dev/null; then
    check_pass "Database 'gandalf_db' exists"
else
    check_fail "Database 'gandalf_db' does not exist"
fi

# Check 3: Database user
if mysql -e "SELECT USER FROM mysql.user WHERE USER='gandalf_user'" | grep -q gandalf_user; then
    check_pass "Database user 'gandalf_user' exists"
else
    check_fail "Database user 'gandalf_user' does not exist"
fi

# Check 4: Application directory
echo ""
echo "Checking application files..."
if [ -d "/opt/apps/gandlf" ]; then
    check_pass "Application directory exists"
else
    check_fail "Application directory not found"
fi

# Check 5: Python virtual environment
if [ -d "/opt/apps/gandlf/venv" ]; then
    check_pass "Python virtual environment exists"
    PACKAGE_COUNT=$(/opt/apps/gandlf/venv/bin/pip freeze 2>/dev/null | wc -l)
    echo -e "  ${BLUE}→${NC} Installed packages: ${PACKAGE_COUNT}"
else
    check_fail "Python virtual environment not found"
fi

# Check 6: Configuration files
echo ""
echo "Checking configuration..."
if [ -f "/opt/apps/gandlf/.env" ]; then
    check_pass "Environment configuration exists"
    if grep -q "ANTHROPIC_API_KEY" /opt/apps/gandlf/.env; then
        check_pass "Anthropic API key configured"
    else
        check_fail "Anthropic API key not found in .env"
    fi
else
    check_fail "Environment configuration not found"
fi

if [ -f "/etc/gandalf/db.env" ]; then
    check_pass "Database credentials file exists"
else
    check_fail "Database credentials file not found"
fi

# Check 7: Log directory
if [ -d "/var/log/gandlf" ]; then
    check_pass "Log directory exists"
else
    check_fail "Log directory not found"
fi

# Check 8: Systemd services
echo ""
echo "Checking systemd services..."
if [ -f "/etc/systemd/system/gandalf-api.service" ]; then
    check_pass "Flask API service file exists"
else
    check_fail "Flask API service file not found"
fi

if [ -f "/etc/systemd/system/gandalf-pipeline.service" ]; then
    check_pass "Pipeline Agent service file exists"
else
    check_fail "Pipeline Agent service file not found"
fi

# Check 9: Service status
echo ""
echo "Checking service status..."
if systemctl is-active --quiet gandalf-pipeline.service; then
    check_pass "Pipeline Agent service is running"
else
    check_fail "Pipeline Agent service is not running"
    echo -e "  ${BLUE}→${NC} Check logs: journalctl -u gandalf-pipeline.service -n 20"
fi

if systemctl is-active --quiet gandalf-api.service; then
    check_pass "Flask API service is running"
else
    check_fail "Flask API service is not running"
    echo -e "  ${BLUE}→${NC} Check logs: journalctl -u gandalf-api.service -n 20"
fi

# Check 10: Service enabled on boot
if systemctl is-enabled --quiet gandalf-pipeline.service; then
    check_pass "Pipeline Agent service enabled on boot"
else
    check_warn "Pipeline Agent service not enabled on boot"
fi

if systemctl is-enabled --quiet gandalf-api.service; then
    check_pass "Flask API service enabled on boot"
else
    check_warn "Flask API service not enabled on boot"
fi

# Check 11: Port availability
echo ""
echo "Checking ports..."
if netstat -tlnp 2>/dev/null | grep -q ":5000"; then
    check_pass "Port 5000 (Flask API) is listening"
else
    check_fail "Port 5000 (Flask API) is not listening"
fi

if netstat -tlnp 2>/dev/null | grep -q ":8081"; then
    check_pass "Port 8081 (Pipeline Agent) is listening"
else
    check_fail "Port 8081 (Pipeline Agent) is not listening"
fi

if netstat -tlnp 2>/dev/null | grep -q ":3306"; then
    check_pass "Port 3306 (MySQL) is listening"
else
    check_fail "Port 3306 (MySQL) is not listening"
fi

# Check 12: API health endpoint
echo ""
echo "Testing API endpoints..."
if curl -f -s http://localhost:5000/health > /dev/null 2>&1; then
    check_pass "Flask API health check passed"
    HEALTH_RESPONSE=$(curl -s http://localhost:5000/health)
    echo -e "  ${BLUE}→${NC} Response: ${HEALTH_RESPONSE}"
else
    check_fail "Flask API health check failed"
    echo -e "  ${BLUE}→${NC} Try: curl http://localhost:5000/health"
fi

# Check 13: Pipeline Agent health
if curl -f -s http://localhost:8081/health > /dev/null 2>&1; then
    check_pass "Pipeline Agent health check passed"
else
    check_warn "Pipeline Agent health check failed (may be normal if no /health endpoint)"
fi

# Check 14: Agent status endpoint
if curl -f -s http://localhost:5000/api/agent/status > /dev/null 2>&1; then
    check_pass "Agent status endpoint responding"
    STATUS_RESPONSE=$(curl -s http://localhost:5000/api/agent/status | head -n 3)
    echo -e "  ${BLUE}→${NC} Status: ${STATUS_RESPONSE}"
else
    check_warn "Agent status endpoint not responding (may need more time)"
fi

# Check 15: Claude Code CLI
echo ""
echo "Checking Claude Code CLI..."
if command -v claude-code &> /dev/null; then
    check_pass "Claude Code CLI is installed"
    CLAUDE_VERSION=$(claude-code --version 2>&1 || echo "installed")
    echo -e "  ${BLUE}→${NC} Version: ${CLAUDE_VERSION}"
else
    check_warn "Claude Code CLI not found in PATH"
fi

# Check 16: Node.js
if command -v node &> /dev/null; then
    check_pass "Node.js is installed"
    NODE_VERSION=$(node --version)
    echo -e "  ${BLUE}→${NC} Version: ${NODE_VERSION}"
else
    check_warn "Node.js not found"
fi

# Check 17: Python packages
echo ""
echo "Checking critical Python packages..."
if /opt/apps/gandlf/venv/bin/python3 -c "import flask" 2>/dev/null; then
    check_pass "Flask package installed"
else
    check_fail "Flask package not installed"
fi

if /opt/apps/gandlf/venv/bin/python3 -c "import anthropic" 2>/dev/null; then
    check_pass "Anthropic package installed"
else
    check_fail "Anthropic package not installed"
fi

if /opt/apps/gandlf/venv/bin/python3 -c "import mysql.connector" 2>/dev/null; then
    check_pass "MySQL connector package installed"
else
    check_fail "MySQL connector package not installed"
fi

# Summary
echo ""
echo "============================================================"
echo "  Verification Summary"
echo "============================================================"
echo ""
echo -e "${GREEN}Passed:${NC} ${PASSED}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed:${NC} ${FAILED}"
else
    echo -e "${GREEN}Failed:${NC} 0"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "GANDALF is ready to play! 🎮"
    echo ""
    echo "Try this test command:"
    echo ""
    echo "  curl -X POST http://localhost:5000/api/intent \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{"
    echo "      \"date\": \"2024-01-25T12:00:00Z\","
    echo "      \"generate_for\": \"AI-AGENT\","
    echo "      \"user_prompt\": \"Add a logout button to the navigation bar\""
    echo "    }'"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed${NC}"
    echo ""
    echo "Review the failed checks above and:"
    echo "  1. Check setup log: /var/log/gandalf-setup.log"
    echo "  2. Check service logs: journalctl -u gandalf-api.service -n 50"
    echo "  3. Try running setup again: sudo bash setup.sh"
    echo ""
    exit 1
fi
