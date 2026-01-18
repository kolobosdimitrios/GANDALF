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

- **Multi-Agent System** - Uses Haiku, Sonnet, and Opus models optimally for cost efficiency
- **Intelligent Model Routing** - Automatically selects the best model based on task complexity
- **Token Efficiency** - Minimizes token usage and downstream AI reasoning (30-40% cost savings)
- **Structured Output** - Consistent CTC format for all tasks
- **Intent Extraction** - Automatically identifies user goals and requirements
- **Gap Detection** - Identifies missing information and asks clarifying questions
- **Execution Ready** - Output is directly executable by AI agents
- **Telemetry Tracking** - Captures metrics, costs, and token usage per model

## Architecture

```
┌─────────────┐      HTTP       ┌──────────────┐      HTTP      ┌─────────────────┐
│   User      │ ──────────────> │   Flask API  │ ────────────> │  AI Agent API   │
│  (Human)    │                 │   (Port 5000)│               │   (Port 8080)   │
└─────────────┘                 └──────┬───────┘               └────────┬────────┘
                                       │                                 │
                                       │                    ┌────────────┼────────────┐
                                       │                    │            │            │
                                       v                    v            v            v
                               ┌───────────────┐    ┌──────────┐ ┌──────────┐ ┌──────────┐
                               │    GANDALF    │    │  Haiku   │ │  Sonnet  │ │  Opus    │
                               │    Compiler   │    │ (Simple) │ │ (Medium) │ │(Complex) │
                               └───────┬───────┘    └──────────┘ └──────────┘ └──────────┘
                                       │                    └────────────┬────────────┘
                                       v                                 │
                               ┌───────────────┐                         │
                               │      CTC      │ <───────────────────────┘
                               │   (JSON)      │        Model Router
                               └───────┬───────┘   (Intelligent Selection)
                                       │
                                       v
                               ┌───────────────┐
                               │   MySQL DB    │
                               │  (Telemetry)  │
                               └───────────────┘
```

### Multi-Agent Model Selection

GANDALF uses three Claude models strategically:

- **Haiku** (Fast, Cheap): Intent classification, validation, simple analysis
- **Sonnet** (Balanced): Gap detection, question generation, moderate complexity
- **Opus** (Powerful): Complex CTC generation, technical reasoning, edge cases

This results in **30-40% cost savings** on simple tasks while maintaining quality.

## Quick Start

### Deploy with Multipass

```bash
cd /opt/apps/gandlf
multipass launch --name gandalf \
  --cpus 2 \
  --memory 2G \
  --cloud-init cloud-init/gandalf-cloud-init.yaml
```

### Start AI Agent Service

```bash
# Set up environment
cd /opt/apps/gandlf/multi-agent
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Install dependencies
cd /opt/apps/gandlf
pip install -r requirements.txt

# Start AI Agent Service (in background)
cd /opt/apps/gandlf/multi-agent
./start_ai_agent.sh

# Start Flask API (in another terminal)
cd /opt/apps/gandlf
python -m api.app
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
│   ├── intent_analyzer.py # Intent extraction
│   ├── gap_detector.py    # Gap detection
│   ├── ctc_generator.py   # CTC generation
│   └── README.md          # API documentation
├── multi-agent/           # Multi-Agent System (NEW)
│   ├── model_router.py    # Intelligent model selection
│   ├── ai_agent_service.py # HTTP API for agents
│   ├── pipeline_agent_service.py # Pipeline orchestration
│   ├── test_multi_agent.py # Test suite
│   ├── start_ai_agent.sh  # Startup script
│   ├── .env.example       # Configuration template
│   ├── MULTI_AGENT_ARCHITECTURE.md # Architecture docs
│   └── README.md          # Usage guide
├── gandalf_agent/         # Agent client
│   ├── agent_client.py    # HTTP client
│   └── ctc_orchestrator.py # CTC orchestration
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

### Flask API (Port 5000)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/intent` | Submit user intent, receive CTC |
| GET | `/api/ctc/<id>` | Get CTC by ID (TODO) |
| GET | `/api/intents` | List all intents (TODO) |

### AI Agent API (Port 8080)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/agent` | Execute AI task with model routing |
| GET | `/health` | Health check |
| GET | `/models` | List available models |
| GET | `/telemetry` | Get usage statistics |

## Technology Stack

- **Language:** Python 3.x
- **Framework:** Flask 3.0.2
- **AI Models:** Anthropic Claude (Haiku, Sonnet, Opus)
- **HTTP Client:** httpx 0.28.1
- **WSGI Server:** Gunicorn 21.2.0
- **Database:** MySQL 8.0
- **VM:** Multipass (Ubuntu 22.04+)
- **Process Manager:** systemd

See [TECHNOLOGIES.md](TECHNOLOGIES.md) for complete list.

## Documentation

- **[Multi-Agent Architecture](multi-agent/MULTI_AGENT_ARCHITECTURE.md)** - Model routing and optimization (NEW)
- **[Multi-Agent README](multi-agent/README.md)** - Usage guide for multi-agent system (NEW)
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

## Cost Optimization & Performance

### Multi-Agent System Benefits

The intelligent model routing system provides significant cost savings:

| Task Complexity | Model Used | Cost Reduction |
|----------------|-----------|----------------|
| Simple (classification, validation) | Haiku | **30-40%** |
| Medium (gap detection, questions) | Sonnet | **20-30%** |
| Complex (CTC generation) | Opus | **10-20%** |

**Example:** "Add user authentication"
- Before (all Sonnet): $0.2205
- After (multi-agent): $0.1863
- **Savings: 15.5%**

### Model Selection Logic

The system automatically routes tasks based on:
- Intent complexity (simple/medium/complex)
- Code size analysis
- Technical term density
- Architectural scope

Fallback chain ensures availability: Opus → Sonnet → Haiku

## Metrics & Telemetry

GANDALF tracks:
- Raw user intent
- Generated CTC
- Execution time
- Token usage (per model)
- Cost per request
- Model selection decisions
- Questions asked
- Efficiency percentage

## Roadmap

### Current Version (1.0)
- ✅ Flask REST API
- ✅ Multi-Agent System (Haiku, Sonnet, Opus)
- ✅ Intelligent Model Routing
- ✅ Cost Optimization (30-40% savings)
- ✅ Basic CTC generation
- ✅ Health checks
- ✅ Multipass deployment
- ✅ Telemetry tracking (tokens, cost, latency)
- ✅ Claude API integration

### Upcoming
- [ ] Database integration (MySQL)
- [ ] Advanced intent extraction
- [ ] Clarification system
- [ ] Authentication/authorization
- [ ] Rate limiting
- [ ] Monitoring dashboard
- [ ] Unit & integration tests (expanded)

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

GANDALF is licensed under the Apache License 2.0.

This includes:
- Prompt definitions
- Semantic / lexical pipelines
- CTC schemas
- Orchestration logic
- Documentation

Trademarks and branding are not included in the license.

## Authors

GANDALF Team

## References

- System Prompt: Based on minimal, token-efficient prompt compilation
- Inspired by: Claude Code CLI integration patterns
- Architecture: Follows black-box design principles

---

**Remember:** GANDALF is a prompt compiler, not a consultant. Its purpose is to reduce ambiguity and reasoning cost, not to provide solutions.
