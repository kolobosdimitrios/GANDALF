# GANDALF - Requirements Inference & Prompt Normalization System

**G**enerative **A**gent for **N**ormalizing **D**irectives **A**nd **L**everaging **F**ormalization

GANDALF is an invisible prompt-compiler agent that converts unstructured human messages into minimal, deterministic, AI-optimized task prompts (Compiled Task Contracts or CTCs).

## What is GANDALF?

GANDALF sits between human users and execution-oriented AI agents (like Claude Code CLI). It:

1. **Receives** unstructured user intents
2. **Extracts** requirements and context
3. **Normalizes** into structured format
4. **Generates** executable task contracts (CTCs)
5. **Returns** optimized prompts ready for AI execution

## Key Features

- **Token Efficiency** - Minimizes token usage and downstream AI reasoning
- **Structured Output** - Consistent CTC format for all tasks
- **Intent Extraction** - Automatically identifies user goals and requirements
- **Gap Detection** - Identifies missing information and asks clarifying questions
- **Execution Ready** - Output is directly executable by AI agents
- **Telemetry Tracking** - Captures metrics for optimization

## Architecture

```
┌─────────────┐      HTTP       ┌──────────────┐
│   User      │ ──────────────> │   Flask API  │
│  (Human)    │                 │   (Port 5000)│
└─────────────┘                 └──────┬───────┘
                                       │
                                       v
                               ┌───────────────┐
                               │    GANDALF    │
                               │    Compiler   │
                               └───────┬───────┘
                                       │
                                       v
                               ┌───────────────┐
                               │      CTC      │
                               │   (JSON)      │
                               └───────┬───────┘
                                       │
                                       v
                               ┌───────────────┐
                               │   MySQL DB    │
                               │  (Telemetry)  │
                               └───────────────┘
```

## Quick Start

### Deploy with Multipass

```bash
cd /opt/apps/gandlf
multipass launch --name gandalf \
  --cpus 2 \
  --memory 2G \
  --cloud-init cloud-init/gandalf-cloud-init.yaml
```

### Test the API

```bash
# Get VM IP
VM_IP=$(multipass info gandalf | grep IPv4 | awk '{print $2}')

# Health check
curl http://$VM_IP:5000/health

# Submit intent
curl -X POST http://$VM_IP:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add user authentication to the app"
  }'
```

## CTC Format (Compiled Task Contract)

```json
{
  "gandalf_version": "1.0",
  "ctc": {
    "title": "Add user authentication",
    "context": ["Existing app needs auth", "Using JWT tokens"],
    "definition_of_done": [
      "User registration endpoint working",
      "Login endpoint returns JWT",
      "Protected routes verify tokens"
    ],
    "constraints": [
      "Use bcrypt for passwords",
      "JWT expires in 24 hours"
    ],
    "deliverables": [
      "Auth endpoints",
      "Middleware",
      "Tests"
    ]
  },
  "clarifications": {
    "asked": [],
    "resolved_by": "default"
  },
  "telemetry": {
    "intent_id": "uuid",
    "created_at": "ISO-8601",
    "executor": {"name": "claude-code", "version": "1.0"},
    "elapsed_ms": 0,
    "input_tokens": null,
    "output_tokens": null,
    "user_questions_count": 0,
    "execution_result": "unknown"
  }
}
```

## Project Structure

```
/opt/apps/gandlf/
├── api/                    # Flask REST API
│   ├── app.py             # Main application
│   └── README.md          # API documentation
├── cloud-init/            # VM provisioning
│   └── gandalf-cloud-init.yaml
├── scripts/               # Utility scripts
│   ├── start_api.sh       # API startup
│   ├── test_api.py        # Test suite
│   └── gandalf-api.service # Systemd service
├── requirements.txt       # Python dependencies
├── PROJECT_MAP.md         # Architecture overview
├── TECHNOLOGIES.md        # Tech stack details
├── DEPLOYMENT.md          # Deployment guide
├── EXAMPLE_USAGE.md       # Usage examples
└── README.md              # This file
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/intent` | Submit user intent, receive CTC |
| GET | `/api/ctc/<id>` | Get CTC by ID (TODO) |
| GET | `/api/intents` | List all intents (TODO) |

## Technology Stack

- **Language:** Python 3.x
- **Framework:** Flask 3.0.2
- **WSGI Server:** Gunicorn 21.2.0
- **Database:** MySQL 8.0
- **VM:** Multipass (Ubuntu 22.04+)
- **Process Manager:** systemd

See [TECHNOLOGIES.md](TECHNOLOGIES.md) for complete list.

## Documentation

- **[API Documentation](api/README.md)** - Endpoint details and examples
- **[Project Map](PROJECT_MAP.md)** - Architecture and data flow
- **[Deployment Guide](DEPLOYMENT.md)** - Setup and deployment
- **[Example Usage](EXAMPLE_USAGE.md)** - Usage examples and patterns
- **[Technologies](TECHNOLOGIES.md)** - Complete tech stack
- **[GANDALF System Prompt](../../../var/www/projects/gandlf/GANDALF.md)** - Core rules and behavior

## Development

### Local Setup

```bash
# Clone repository
cd /opt/apps/gandlf

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python api/app.py
```

### Running Tests

```bash
source venv/bin/activate
python scripts/test_api.py
```

## Use Cases

### 1. CLI Integration
Convert vague commands into structured tasks:
```bash
$ gandalf "make the app faster"
→ CTC: Optimize application performance
  - Profile current bottlenecks
  - Implement caching layer
  - Optimize database queries
```

### 2. CI/CD Pipeline
Auto-generate tasks from commit messages:
```yaml
- name: Generate CTC
  run: curl -X POST $GANDALF_API/intent ...
```

### 3. AI Agent Orchestration
Feed structured tasks to execution agents:
```python
ctc = gandalf.submit_intent(user_input)
claude_code.execute(ctc)
```

## Core Principles

1. **AI-Unaware Behavior** - System feels like a simple helper
2. **No Internal Leakage** - Only shows clarifying questions and final CTC
3. **Delta-Only Thinking** - Output only task-specific information
4. **Token Efficiency First** - Minimize verbosity and reasoning space

## Metrics & Telemetry

GANDALF tracks:
- Raw user intent
- Generated CTC
- Execution time
- Token usage
- Questions asked
- Efficiency percentage

## Roadmap

### Current Version (1.0)
- ✅ Flask REST API
- ✅ Basic CTC generation
- ✅ Health checks
- ✅ Multipass deployment

### Upcoming
- [ ] Database integration (MySQL)
- [ ] Advanced intent extraction
- [ ] Clarification system
- [ ] Authentication/authorization
- [ ] Rate limiting
- [ ] Monitoring dashboard
- [ ] Claude API integration
- [ ] Unit & integration tests

## Contributing

### Code Style
- Follow PEP 8
- Use descriptive names
- Comment the WHY, not the WHAT
- Keep functions small (one job)
- Add docstrings

### Before Committing
- [ ] Code is readable by junior developer
- [ ] Functions are small (one job)
- [ ] Tests exist
- [ ] Documentation updated
- [ ] PROJECT_MAP.md updated

## Service Management

```bash
# Start service
sudo systemctl start gandalf-api

# Check status
sudo systemctl status gandalf-api

# View logs
sudo journalctl -u gandalf-api -f

# Restart service
sudo systemctl restart gandalf-api
```

## Troubleshooting

### API Not Responding
```bash
sudo systemctl status gandalf-api
sudo journalctl -u gandalf-api -n 50
```

### Database Connection Issues
```bash
mysql -u gandalf -p
sudo cat /etc/gandalf/db.env
```

### See [DEPLOYMENT.md](DEPLOYMENT.md) for complete troubleshooting guide

## License

[Add license information]

## Authors

GANDALF Team

## References

- System Prompt: Based on minimal, token-efficient prompt compilation
- Inspired by: Claude Code CLI integration patterns
- Architecture: Follows black-box design principles

---

**Remember:** GANDALF is a prompt compiler, not a consultant. Its purpose is to reduce ambiguity and reasoning cost, not to provide solutions.
