# GANDALF REST API

REST API for the GANDALF prompt compiler system. Converts unstructured user intents into structured Compiled Task Contracts (CTCs).

## Quick Start

### Start the API (Development)
```bash
cd /opt/apps/gandlf
source venv/bin/activate
python api/app.py
```

### Start the API (Production)
```bash
sudo systemctl start gandalf-api
```

## API Endpoints

### Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "gandalf-api",
  "timestamp": "2026-01-19T10:30:00.000000"
}
```

### Submit User Intent
```bash
POST /api/intent
Content-Type: application/json
```

**Request Body:**
```json
{
  "date": "2026-01-19T10:00:00Z",
  "generate_for": "claude-code",
  "user_prompt": "Add user authentication to the app"
}
```

**Required Fields:**
- `date` (string): ISO-8601 formatted timestamp
- `generate_for` (string): Target AI agent identifier
- `user_prompt` (string): Raw user intent

**Response:**
```json
{
  "gandalf_version": "1.0",
  "ctc": {
    "title": "Add user authentication to the app",
    "context": [
      "User request received on 2026-01-19T10:00:00Z",
      "Target executor: claude-code"
    ],
    "definition_of_done": [
      "Implementation completed",
      "Tests passing",
      "Documentation updated"
    ],
    "constraints": [
      "Follow project coding standards",
      "Maintain backward compatibility"
    ],
    "deliverables": [
      "Source code",
      "Tests",
      "Documentation"
    ]
  },
  "clarifications": {
    "asked": [],
    "resolved_by": "default"
  },
  "telemetry": {
    "intent_id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2026-01-19T10:30:00.000000",
    "executor": {
      "name": "claude-code",
      "version": "1.0"
    },
    "elapsed_ms": 0,
    "input_tokens": null,
    "output_tokens": null,
    "user_questions_count": 0,
    "execution_result": "unknown"
  }
}
```

### Get CTC by ID
```bash
GET /api/ctc/<intent_id>
```

**Status:** Not yet implemented (501)

### List All Intents
```bash
GET /api/intents?page=1&limit=20
```

**Status:** Not yet implemented (501)

## Testing

### Manual Testing
```bash
# Health check
curl http://localhost:5000/health

# Submit intent
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add user authentication to the app"
  }'
```

### Automated Testing
```bash
# Run test script
python scripts/test_api.py
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields",
  "missing": ["date", "user_prompt"]
}
```

### 400 Invalid Date Format
```json
{
  "error": "Invalid date format. Use ISO-8601 format"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Error details..."
}
```

## Configuration

Environment variables (set in systemd service or shell):

```bash
FLASK_ENV=production      # production or development
FLASK_PORT=5000          # Port to listen on
FLASK_DEBUG=False        # Enable debug mode
```

## Logs

- Access log: `/var/log/gandalf/access.log`
- Error log: `/var/log/gandalf/error.log`
- System journal: `journalctl -u gandalf-api`

## Service Management

```bash
# Start
sudo systemctl start gandalf-api

# Stop
sudo systemctl stop gandalf-api

# Restart
sudo systemctl restart gandalf-api

# Status
sudo systemctl status gandalf-api

# View logs
sudo journalctl -u gandalf-api -f
```

## Development

### Project Structure
```
api/
├── __init__.py    # Package initialization
├── app.py         # Main Flask application
└── README.md      # This file
```

### Adding New Endpoints

1. Define route in `app.py`
2. Add docstring with description
3. Implement validation
4. Return JSON response
5. Update this README

### Code Style

- Follow PEP 8
- Use descriptive names
- Add docstrings to functions
- Comment the WHY, not the WHAT
- Keep functions small (one job)

## TODO

- [ ] Implement actual GANDALF prompt compilation logic
- [ ] Add database integration (MySQL)
- [ ] Implement GET /api/ctc/<intent_id>
- [ ] Implement GET /api/intents with pagination
- [ ] Add authentication (API keys or JWT)
- [ ] Add rate limiting
- [ ] Add input sanitization
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Add request/response logging
- [ ] Add metrics endpoint
- [ ] Add OpenAPI/Swagger documentation

## References

- Main docs: `/opt/apps/gandlf/PROJECT_MAP.md`
- Tech stack: `/opt/apps/gandlf/TECHNOLOGIES.md`
- System prompt: `/var/www/projects/gandlf/GANDALF.md`
- CTC schema: `/var/www/projects/gandlf/CompiledOutputSchema.md`
