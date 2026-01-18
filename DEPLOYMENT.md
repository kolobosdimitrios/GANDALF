# GANDALF Deployment Guide

This guide covers deploying the GANDALF API system using Multipass.

## Prerequisites

- Multipass installed on host system
- Network connectivity
- At least 2GB RAM and 10GB disk space available

## Quick Deploy

### 1. Launch VM with Cloud-Init

```bash
cd /opt/apps/gandlf
multipass launch --name gandalf \
  --cpus 2 \
  --memory 2G \
  --disk 10G \
  --cloud-init cloud-init/gandalf-cloud-init.yaml
```

### 2. Wait for Provisioning

The cloud-init process will:
- Install MySQL, Python, Node.js
- Create database and user
- Set up Python virtual environment
- Install dependencies (Flask, Gunicorn, etc.)
- Configure systemd service
- Start the API automatically

This takes approximately 5-10 minutes.

### 3. Verify Deployment

```bash
# Check VM is running
multipass list

# Access VM
multipass shell gandalf

# Inside VM: Check service status
sudo systemctl status gandalf-api

# Check logs
sudo journalctl -u gandalf-api -n 50

# Test API
curl http://localhost:5000/health
```

### 4. Test from Host

```bash
# Get VM IP
VM_IP=$(multipass info gandalf | grep IPv4 | awk '{print $2}')

# Test health endpoint
curl http://$VM_IP:5000/health

# Submit test intent
curl -X POST http://$VM_IP:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add user authentication"
  }'
```

## Manual Deployment (Without Cloud-Init)

If you need to deploy manually or troubleshoot:

### 1. Create VM

```bash
multipass launch --name gandalf ubuntu:22.04
multipass shell gandalf
```

### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install packages
sudo apt install -y mysql-server python3 python3-venv python3-pip curl git

# Start MySQL
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 3. Setup Database

```bash
# Generate password
DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Create database and user
sudo mysql -e "CREATE DATABASE gandalf CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER 'gandalf'@'localhost' IDENTIFIED BY '${DB_PASS}';"
sudo mysql -e "GRANT ALL PRIVILEGES ON gandalf.* TO 'gandalf'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Save credentials
sudo mkdir -p /etc/gandalf
echo "DB_PASS=${DB_PASS}" | sudo tee /etc/gandalf/db.env
sudo chmod 600 /etc/gandalf/db.env
```

### 4. Setup Application

```bash
# Create directory
sudo mkdir -p /opt/gandalf/api

# Copy application files
# (Assumes files are in /tmp or mounted)
sudo cp -r /path/to/api/* /opt/gandalf/api/

# Create virtual environment
sudo python3 -m venv /opt/gandalf/venv

# Install dependencies
sudo /opt/gandalf/venv/bin/pip install --upgrade pip
sudo /opt/gandalf/venv/bin/pip install flask flask-cors gunicorn mysql-connector-python python-dotenv pydantic
```

### 5. Setup Service

```bash
# Copy service file
sudo cp /opt/apps/gandlf/scripts/gandalf-api.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable gandalf-api
sudo systemctl start gandalf-api

# Check status
sudo systemctl status gandalf-api
```

## Configuration

### Environment Variables

Edit `/etc/systemd/system/gandalf-api.service`:

```ini
[Service]
Environment="FLASK_ENV=production"
Environment="FLASK_PORT=5000"
Environment="FLASK_DEBUG=False"
```

After changes:
```bash
sudo systemctl daemon-reload
sudo systemctl restart gandalf-api
```

### Database Configuration

Database credentials are stored in `/etc/gandalf/db.env`:

```bash
DB_NAME=gandalf
DB_USER=gandalf
DB_HOST=localhost
DB_PORT=3306
DB_PASS=<generated-password>
```

### Logs

Configure log location in service file or startup script:

```bash
ACCESS_LOG="/var/log/gandalf/access.log"
ERROR_LOG="/var/log/gandalf/error.log"
```

Create log directory:
```bash
sudo mkdir -p /var/log/gandalf
sudo chmod 755 /var/log/gandalf
```

## Service Management

### Start/Stop/Restart

```bash
sudo systemctl start gandalf-api
sudo systemctl stop gandalf-api
sudo systemctl restart gandalf-api
```

### Enable/Disable Auto-Start

```bash
sudo systemctl enable gandalf-api   # Start on boot
sudo systemctl disable gandalf-api  # Don't start on boot
```

### View Status

```bash
sudo systemctl status gandalf-api
```

### View Logs

```bash
# System journal (live)
sudo journalctl -u gandalf-api -f

# Last 100 lines
sudo journalctl -u gandalf-api -n 100

# Access log
sudo tail -f /var/log/gandalf/access.log

# Error log
sudo tail -f /var/log/gandalf/error.log
```

## Networking

### Port Configuration

Default port: 5000

To change:
1. Edit environment variable in service file
2. Reload and restart service

### Firewall

If using UFW:
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

### External Access

To access from outside VM:

```bash
# Get VM IP
multipass info gandalf | grep IPv4

# Access from host
curl http://<VM-IP>:5000/health
```

## Updating

### Update Application Code

```bash
# Copy new files
sudo cp -r /path/to/new/api/* /opt/gandalf/api/

# Restart service
sudo systemctl restart gandalf-api
```

### Update Dependencies

```bash
# Activate venv
source /opt/gandalf/venv/bin/activate

# Update packages
pip install --upgrade flask flask-cors gunicorn

# Restart service
sudo systemctl restart gandalf-api
```

### Update Database Schema

```bash
# Apply migrations (when implemented)
source /opt/gandalf/venv/bin/activate
python /opt/gandalf/scripts/migrate.py
```

## Monitoring

### Health Checks

```bash
# Manual check
curl http://localhost:5000/health

# Automated monitoring (cron)
*/5 * * * * curl -f http://localhost:5000/health || echo "GANDALF API down" | mail -s "Alert" admin@example.com
```

### Resource Usage

```bash
# Check CPU and memory
top -p $(pgrep -f "gunicorn.*gandalf")

# Check disk space
df -h /opt/gandalf
df -h /var/log/gandalf
```

## Backup

### Database Backup

```bash
# Create backup
mysqldump -u gandalf -p gandalf > gandalf_backup_$(date +%Y%m%d).sql

# Restore backup
mysql -u gandalf -p gandalf < gandalf_backup_20260119.sql
```

### Application Backup

```bash
# Backup application
tar -czf gandalf_app_$(date +%Y%m%d).tar.gz /opt/gandalf

# Restore application
tar -xzf gandalf_app_20260119.tar.gz -C /
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u gandalf-api -n 50

# Check if port is in use
sudo lsof -i :5000

# Verify Python environment
source /opt/gandalf/venv/bin/activate
python -c "import flask; print(flask.__version__)"
```

### API Returns Errors

```bash
# Check error log
sudo tail -f /var/log/gandalf/error.log

# Verify database connection
mysql -u gandalf -p -h localhost gandalf -e "SELECT 1"

# Test API manually
python /opt/gandalf/api/app.py
```

### High Memory Usage

```bash
# Check worker count
ps aux | grep gunicorn | wc -l

# Reduce workers in service file
# Change: --workers 4 to --workers 2
sudo systemctl restart gandalf-api
```

## Production Checklist

- [ ] Database password is secure and backed up
- [ ] FLASK_DEBUG is set to False
- [ ] Logs are rotating (logrotate)
- [ ] Monitoring is configured
- [ ] Backups are automated
- [ ] Firewall rules are configured
- [ ] SSL/TLS is configured (if exposing externally)
- [ ] Rate limiting is configured
- [ ] Authentication is configured

## Next Steps

1. Test API with `/opt/apps/gandlf/scripts/test_api.py`
2. Review examples in `EXAMPLE_USAGE.md`
3. Configure monitoring
4. Set up backups
5. Implement database schema
6. Add authentication

## References

- Cloud-init config: `/opt/apps/gandlf/cloud-init/gandalf-cloud-init.yaml`
- Service file: `/opt/apps/gandlf/scripts/gandalf-api.service`
- API docs: `/opt/apps/gandlf/api/README.md`
- Project map: `/opt/apps/gandlf/PROJECT_MAP.md`
