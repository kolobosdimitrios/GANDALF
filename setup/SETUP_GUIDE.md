# GANDALF Setup Guide

This guide explains how to use the `setup.sh` script to make GANDALF ready to play.

## Overview

The `setup.sh` script is a single, comprehensive script that sets up the entire GANDALF application environment from scratch. It can be run:

1. **Manually** on a fresh Ubuntu 24.04 VM
2. **Automatically** via cloud-init during VM provisioning
3. **On boot** as a startup script

## What the Script Does

The setup script performs these steps automatically:

1. **Install System Dependencies**
   - MySQL Server 8.0
   - Python 3.12 with pip and venv
   - Node.js 20.x
   - Claude Code CLI
   - Build tools and utilities

2. **Setup MySQL Database**
   - Creates database: `gandalf_db`
   - Creates user: `gandalf_user`
   - Sets up credentials securely
   - Stores credentials in `/etc/gandalf/db.env`

3. **Setup Application**
   - Creates application directory at `/opt/apps/gandlf`
   - Copies files from `/var/www/projects/gandlf`
   - Sets up proper permissions

4. **Setup Python Environment**
   - Creates virtual environment at `/opt/apps/gandlf/venv`
   - Installs all required Python packages
   - Installs main and multi-agent requirements

5. **Configure Environment**
   - Creates `.env` file with all configuration
   - Sets up Anthropic API key
   - Configures model settings
   - Sets service ports

6. **Setup Systemd Services**
   - Creates `gandalf-api.service` (Flask API on port 5000)
   - Creates `gandalf-pipeline.service` (Pipeline Agent on port 8081)
   - Creates `gandalf-ai-agent.service` (Legacy agent on port 8080)
   - Enables services to start on boot

7. **Start Services**
   - Starts Pipeline Agent service
   - Starts Flask API service
   - Verifies services are running

8. **Verification**
   - Checks MySQL is running
   - Checks database exists
   - Checks Python environment
   - Checks services are active
   - Tests API health endpoints

## Prerequisites

- Fresh Ubuntu 24.04 LTS installation
- Root access (or sudo privileges)
- Internet connection
- **Anthropic API Key** (required)

## Usage

### Method 1: Manual Installation

Run the setup script manually on a fresh VM:

```bash
# Clone the repository
cd /var/www/projects
git clone <your-repo-url> gandlf

# Run the setup script with your API key
cd gandlf
sudo bash setup.sh "your-anthropic-api-key-here"
```

The script will:
- Install all dependencies
- Set up the database
- Configure the application
- Start all services
- Display a summary when complete

### Method 2: Cloud-Init (Recommended for VM Automation)

Use the provided cloud-init configuration file:

```bash
# Edit cloud-init-with-setup.yaml and replace the API key placeholder
sed 's/ANTHROPIC_API_KEY_PLACEHOLDER/your-actual-api-key/' \
    cloud-init-with-setup.yaml > custom-cloud-init.yaml

# Launch VM with multipass
multipass launch 24.04 \
    --name gandalf-vm \
    --cpus 2 \
    --memory 4G \
    --disk 40G \
    --cloud-init custom-cloud-init.yaml

# Wait for cloud-init to complete (5-10 minutes)
multipass exec gandalf-vm -- cloud-init status --wait

# Check the setup log
multipass exec gandalf-vm -- tail -100 /var/log/gandalf-setup.log
```

### Method 3: Environment Variable

Pass the API key via environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
sudo -E bash setup.sh
```

## After Setup

### Verify Installation

Check that all services are running:

```bash
# Check service status
systemctl status gandalf-api.service
systemctl status gandalf-pipeline.service

# Test API endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/agent/status

# View logs
journalctl -u gandalf-api.service -f
journalctl -u gandalf-pipeline.service -f
```

### Service Management

```bash
# Start services
sudo systemctl start gandalf-api.service
sudo systemctl start gandalf-pipeline.service

# Stop services
sudo systemctl stop gandalf-api.service
sudo systemctl stop gandalf-pipeline.service

# Restart services
sudo systemctl restart gandalf-api.service
sudo systemctl restart gandalf-pipeline.service

# View service status
sudo systemctl status gandalf-api.service
sudo systemctl status gandalf-pipeline.service

# View service logs
sudo journalctl -u gandalf-api.service -n 50
sudo journalctl -u gandalf-pipeline.service -n 50
```

### Test the Application

Submit a test intent:

```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-25T12:00:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "Add a logout button to the navigation bar"
  }'
```

Expected response: A complete CTC with title, context, definition of done, constraints, and deliverables.

## Configuration

### Location of Files

| Item | Location |
|------|----------|
| Application Directory | `/opt/apps/gandlf` |
| Web Directory (source) | `/var/www/projects/gandlf` |
| Virtual Environment | `/opt/apps/gandlf/venv` |
| Environment Config | `/opt/apps/gandlf/.env` |
| Database Credentials | `/etc/gandalf/db.env` |
| Service Logs | `/var/log/gandlf/` |
| Systemd Services | `/etc/systemd/system/gandalf-*.service` |

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Flask API | 5000 | Main REST API |
| Pipeline Agent | 8081 | Multi-model CTC generation pipeline |
| AI Agent (Legacy) | 8080 | Single-agent service (backward compatibility) |
| MySQL | 3306 | Database (localhost only) |

### Environment Variables

The setup script creates `/opt/apps/gandlf/.env` with:

```bash
ANTHROPIC_API_KEY=<your-key>
GANDALF_ENABLE_HAIKU=true
GANDALF_ENABLE_OPUS=true
GANDALF_DEFAULT_MODEL=sonnet
FLASK_PORT=5000
GANDALF_PIPELINE_PORT=8081
DB_NAME=gandalf_db
DB_USER=gandalf_user
DB_PASS=PQnIQQkNTn90kKF4
DB_HOST=localhost
LOG_LEVEL=INFO
```

You can modify these values after setup by editing the `.env` file and restarting services.

## Troubleshooting

### Setup Script Fails

Check the error message in the output. Common issues:

1. **Not running as root**: Use `sudo bash setup.sh`
2. **No API key provided**: Pass key as argument or set environment variable
3. **Port already in use**: Stop conflicting services
4. **Package installation fails**: Check internet connection and apt sources

### Services Won't Start

Check service logs:

```bash
sudo journalctl -u gandalf-api.service -n 50
sudo journalctl -u gandalf-pipeline.service -n 50
```

Common issues:

1. **Missing Python packages**: Reinstall with `pip install -r requirements.txt`
2. **Invalid API key**: Check `.env` file and update key
3. **Database connection fails**: Check MySQL is running and credentials are correct
4. **Port already in use**: Check for conflicting processes with `lsof -i :5000`

### API Health Check Fails

```bash
# Check if service is running
systemctl status gandalf-api.service

# Check if port is listening
netstat -tlnp | grep 5000

# Check service logs
journalctl -u gandalf-api.service -n 50

# Try manual start for debugging
cd /opt/apps/gandlf
source venv/bin/activate
python3 -m api.app
```

### Pipeline Agent Not Responding

```bash
# Check if service is running
systemctl status gandalf-pipeline.service

# Check service logs
journalctl -u gandalf-pipeline.service -n 50

# Test the endpoint directly
curl http://localhost:8081/health
```

### Database Issues

```bash
# Check MySQL is running
systemctl status mysql

# Test database connection
mysql -u gandalf_user -p gandalf_db

# Check credentials
cat /etc/gandalf/db.env

# Reset database
mysql -e "DROP DATABASE gandalf_db;"
mysql -e "CREATE DATABASE gandalf_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Security Notes

1. **API Key Storage**: The Anthropic API key is stored in `/opt/apps/gandlf/.env` with 0600 permissions (readable only by root)
2. **Database Credentials**: Stored in `/etc/gandalf/db.env` with 0600 permissions
3. **Service User**: Services run as root (consider creating dedicated service user for production)
4. **Firewall**: Consider restricting access to ports 5000, 8080, 8081 to localhost only
5. **HTTPS**: For production, set up reverse proxy (nginx) with SSL/TLS

## Updating the Application

To update GANDALF after setup:

```bash
# Stop services
sudo systemctl stop gandalf-api.service
sudo systemctl stop gandalf-pipeline.service

# Pull latest code
cd /var/www/projects/gandlf
git pull

# Copy to app directory
sudo rsync -a --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' \
    /var/www/projects/gandlf/ /opt/apps/gandlf/

# Update dependencies
cd /opt/apps/gandlf
source venv/bin/activate
pip install -r requirements.txt
pip install -r multi-agent/requirements.txt
deactivate

# Restart services
sudo systemctl start gandalf-pipeline.service
sudo systemctl start gandalf-api.service

# Verify
curl http://localhost:5000/health
```

## Uninstallation

To remove GANDALF completely:

```bash
# Stop and disable services
sudo systemctl stop gandalf-api.service gandalf-pipeline.service
sudo systemctl disable gandalf-api.service gandalf-pipeline.service

# Remove service files
sudo rm /etc/systemd/system/gandalf-*.service
sudo systemctl daemon-reload

# Remove application files
sudo rm -rf /opt/apps/gandlf
sudo rm -rf /var/log/gandlf

# Remove database (optional)
mysql -e "DROP DATABASE gandalf_db;"
mysql -e "DROP USER 'gandalf_user'@'localhost';"

# Remove configuration
sudo rm -rf /etc/gandalf
```

## Additional Resources

- **Quick Start Guide**: `QUICK_START.md`
- **API Documentation**: `QUICK_REFERENCE.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Multi-Agent System**: `multi-agent/README.md`
- **Deployment Guide**: `DEPLOYMENT.md`

## Support

For issues or questions:

1. Check service logs: `journalctl -u gandalf-api.service -f`
2. Review setup log: `/var/log/gandalf-setup.log`
3. Check API status: `curl http://localhost:5000/api/agent/status`
4. Verify configuration: `cat /opt/apps/gandlf/.env`

---

**The VM is ready to play!** 🎮
