# GANDALF API - Quick Reference Card

## Deploy

```bash
multipass launch --name gandalf \
  --cloud-init /opt/apps/gandlf/cloud-init/gandalf-cloud-init.yaml
```

## Test

```bash
# Health check
curl http://localhost:5000/health

# Submit intent
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add user authentication"
  }'
```

## Service Management

```bash
# Status
sudo systemctl status gandalf-api

# Start/Stop/Restart
sudo systemctl start gandalf-api
sudo systemctl stop gandalf-api
sudo systemctl restart gandalf-api

# Logs
sudo journalctl -u gandalf-api -f
sudo tail -f /var/log/gandalf/error.log
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/intent` | Submit intent, get CTC |

## Required Payload

```json
{
  "date": "ISO-8601 timestamp",
  "generate_for": "target-ai-agent",
  "user_prompt": "user's request"
}
```

## Files

```
/opt/apps/gandlf/
├── api/app.py              # Main Flask app
├── scripts/
│   ├── start_api.sh        # Startup script
│   ├── test_api.py         # Test suite
│   └── gandalf-api.service # systemd service
├── requirements.txt        # Dependencies
└── README.md               # Full documentation
```

## Troubleshooting

```bash
# Check if running
curl http://localhost:5000/health

# View errors
sudo journalctl -u gandalf-api -n 50

# Restart service
sudo systemctl restart gandalf-api
```

## Documentation

- Main README: `/opt/apps/gandlf/README.md`
- API Docs: `/opt/apps/gandlf/api/README.md`
- Deployment: `/opt/apps/gandlf/DEPLOYMENT.md`
- Examples: `/opt/apps/gandlf/EXAMPLE_USAGE.md`

## Quick Links

- Port: 5000
- Logs: `/var/log/gandalf/`
- Config: `/etc/systemd/system/gandalf-api.service`
