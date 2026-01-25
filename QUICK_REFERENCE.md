# GANDALF Web Project - Quick Reference Card

## Quick Start

### Prerequisites
- Python 3.12+
- Dependencies installed: `pip3 install -r requirements.txt`
- Virtual environment set up: `python3 -m venv venv`

### Manual Start

```bash
# Activate environment
source /var/www/projects/gandlf/venv/bin/activate

# Run Flask directly (dev)
python3 -m api.app

# Using gunicorn (production)
gunicorn --workers 4 --bind 0.0.0.0:7000 api.app:app
```

## Systemd Service (Production)

### Setup

```bash
# Copy service file
sudo cp /var/www/projects/gandlf/scripts/gandalf-web.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable gandalf-web.service
sudo systemctl start gandalf-web.service
```

### Service Management

```bash
# Status
sudo systemctl status gandalf-web.service

# Start/Stop/Restart
sudo systemctl start gandalf-web.service
sudo systemctl stop gandalf-web.service
sudo systemctl restart gandalf-web.service

# View logs
sudo journalctl -u gandalf-web.service -f
sudo journalctl -u gandalf-web.service -n 50
```

## Test

```bash
# Health check (port 7000 for web project)
curl http://localhost:7000/health

# Submit intent
curl -X POST http://localhost:7000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-25T10:00:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "Add user authentication"
  }'

# Check agent status
curl http://localhost:7000/api/agent/status
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check - API status |
| GET | `/api/agent/status` | AI agent connectivity check |
| POST | `/api/intent` | Submit intent, receive CTC or clarifications |
| POST | `/api/intent/clarify` | Submit clarification answers |
| GET | `/api/intents` | List submitted intents |
| GET | `/api/ctc/<id>` | Get specific CTC |

## Required Payload

```json
{
  "date": "2026-01-25T10:00:00Z",
  "generate_for": "AI-AGENT",
  "user_prompt": "Your request here"
}
```

## Project Structure

```
/var/www/projects/gandlf/
├── api/
│   ├── app.py                      # Main Flask app
│   ├── efficiency_calculator.py    # Metrics
│   ├── multi_agent_client.py       # AI integration
│   └── README.md
├── scripts/
│   ├── start_web.sh               # Startup script
│   └── gandalf-web.service        # systemd service
├── multi-agent/                   # AI agent code
├── requirements.txt               # Dependencies
└── QUICK_REFERENCE.md            # This file
```

## Troubleshooting

```bash
# Check if running
curl http://localhost:7000/health

# View service logs
sudo journalctl -u gandalf-web.service -n 50

# Check if port is in use
sudo lsof -i :7000

# Restart service
sudo systemctl restart gandalf-web.service

# Check virtual environment
ls -la /var/www/projects/gandlf/venv/bin/python3
```

## Documentation

- Full README: `/var/www/projects/gandlf/README.md`
- API Docs: `/var/www/projects/gandlf/api/README.md`
- Deployment: `/var/www/projects/gandlf/DEPLOYMENT.md`
- System Services: `/opt/apps/gandlf/SYSTEMD_SETUP.md`

## Quick Links

- **Web Service Port**: 7000
- **App Service Port**: 5000
- **AI Agent Port**: 8080
- **Logs**: `/var/log/gandlf/`
- **Service Config**: `/etc/systemd/system/gandalf-web.service`
