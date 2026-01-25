<div align="center">
  <img src="assets/gandalf-logo.jpeg" alt="GANDALF Logo" width="400"/>
</div>

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
┌─────────────┐
│   User      │
│  (Client)   │
└──────┬──────┘
       │ HTTP POST /api/intent
       ▼
┌──────────────────────────────┐
│  Flask API (Port 5000)       │
│  ├─ MultiAgentClient         │
│  └─ EfficiencyCalculator     │
└──────┬───────────────────────┘
       │ HTTP → Pipeline Service
       ▼
┌──────────────────────────────────────────────┐
│  Pipeline Service (Port 8081)                │
│  ┌─────────────────────────────────────────┐ │
│  │  4-Step CTC Generation Pipeline:       │ │
│  │                                         │ │
│  │  Step 1: Lexical Analysis   → Haiku   │ │
│  │  Step 2: Semantic Analysis  → Sonnet  │ │
│  │  Step 3: Coverage Scoring   → Haiku   │ │
│  │  Step 4: CTC Generation     → Opus    │ │
│  └─────────────────────────────────────────┘ │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Claude API                  │
│  ├─ Haiku (Steps 1,3)       │
│  ├─ Sonnet (Step 2)         │
│  └─ Opus (Step 4)           │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  CTC JSON Response           │
│  (with telemetry)            │
└──────────────────────────────┘
```

### 4-Step Pipeline Strategy

GANDALF uses a multi-step, multi-model approach for cost-optimized CTC generation:

| Step | Name | Model | Purpose | Cost Benefit |
|------|------|-------|---------|--------------|
| 1 | Lexical Analysis | Haiku | Extract keywords, entities | Fast & cheap |
| 2 | Semantic Analysis | Sonnet | Build semantic frame | Balanced |
| 3 | Coverage Scoring | Haiku | Score completeness, generate Q&A | Fast & cheap |
| 4 | CTC Generation | Opus | Final CTC generation | Best quality |

**Result: 41.4% cost savings** compared to all-Opus approach while maintaining quality.

## Quick Start

> **🚀 Automated Setup Available!** For production deployment, see [`setup/`](setup/) directory for automated installation scripts and cloud-init configuration.

### Option 1: Automated Setup (Recommended)

```bash
# Run the automated setup script
cd /var/www/projects/gandlf/setup
sudo bash setup.sh "your-anthropic-api-key"

# Verify installation
bash verify_setup.sh
```

See [`setup/README.md`](setup/README.md) for detailed setup instructions, cloud-init configuration, and troubleshooting.

### Option 2: Manual Setup

```bash
cd /var/www/projects/gandlf

# Install dependencies
pip3 install -r requirements.txt
cd multi-agent && pip3 install -r requirements.txt

# Configure environment
cd multi-agent
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 2. Start the Services

**Terminal 1: Start Pipeline Service**
```bash
cd /var/www/projects/gandlf/multi-agent
./start_pipeline_agent.sh
# Service runs on port 8081
```

**Terminal 2: Start Flask API**
```bash
cd /var/www/projects/gandlf
python3 -m api.app
# API runs on port 5000
```

### 3. Test the System

```bash
# Health check
curl http://localhost:5000/health

# Submit intent
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-24T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add user authentication to the app"
  }'

# Get pipeline status
curl http://localhost:5000/api/agent/status
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
/var/www/projects/gandlf/
├── api/                    # Flask REST API (Python)
│   ├── __init__.py        # Package initialization
│   ├── app.py             # Main Flask application (6 endpoints)
│   ├── multi_agent_client.py # Multi-agent orchestrator
│   ├── efficiency_calculator.py # CTC efficiency metrics
│   └── README.md          # API documentation
├── multi-agent/           # Multi-Agent HTTP Services
│   ├── pipeline_agent_service.py # 4-step pipeline service
│   ├── pipeline_orchestrator.py  # Pipeline orchestration
│   ├── pipeline_model_router.py  # 4-step model routing
│   ├── pipeline_client.py # Pipeline HTTP client
│   ├── ai_agent_service.py # AI agent service
│   ├── model_router.py    # Model selection logic
│   ├── start_pipeline_agent.sh # Pipeline startup
│   ├── start_ai_agent.sh  # AI agent startup
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example       # Configuration template
│   ├── README.md          # Multi-agent docs
│   └── MULTI_AGENT_ARCHITECTURE.md # Architecture details
├── agents/                # Agent Instructions & KB
│   ├── AGENT_ROLE.md      # Agent mission & principles
│   ├── 01_INTENT_ANALYSIS.md # Intent analysis instructions
│   ├── 02_GAP_DETECTION.md # Gap detection instructions
│   └── 03_CTC_GENERATION.md # CTC generation instructions
├── assets/                # Static Assets
│   └── gandalf-logo.jpeg
├── demo/                  # Demo Files & Examples
├── tickets/               # Issue Tracking & Summaries
├── requirements.txt       # Python dependencies
├── PROJECT_STRUCTURE.md   # Directory structure (this detailed)
├── PROJECT_MAP.md         # Architecture & data flow
├── TECHNOLOGIES.md        # Tech stack details
├── DEPLOYMENT.md          # Deployment guide
├── QUICK_START.md         # Quick start guide
├── QUICK_REFERENCE.md     # Quick reference
├── README.md              # This file
├── LICENSE
├── NOTICE
└── CLA.md
```

## API Endpoints

### Flask API (Port 5000) - Primary Interface

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check, service status |
| POST | `/api/intent` | Submit user intent, receive CTC or clarifications |
| POST | `/api/intent/clarify` | Submit clarification answers, continue CTC generation |
| GET | `/api/ctc/<intent_id>` | Retrieve CTC by ID |
| GET | `/api/intents` | List all intents with pagination |
| GET | `/api/agent/status` | Check pipeline service status |

### Backend Services

**Pipeline Service (Port 8081):**
- Internal 4-step orchestration
- Model routing (Haiku → Sonnet → Haiku → Opus)
- Telemetry tracking

**AI Agent Service (Port 8080):**
- Legacy single-agent service
- Available for compatibility

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

### 🚀 Setup & Deployment
- **[Setup Directory](setup/)** - Automated setup scripts and cloud-init configuration (NEW)
- **[Setup Guide](setup/SETUP_GUIDE.md)** - Comprehensive setup guide with troubleshooting (NEW)
- **[Deployment Guide](DEPLOYMENT.md)** - Manual setup and deployment

### 🏗️ Architecture & Usage
- **[Multi-Agent Architecture](multi-agent/MULTI_AGENT_ARCHITECTURE.md)** - Model routing and optimization
- **[Multi-Agent README](multi-agent/README.md)** - Usage guide for multi-agent system
- **[API Documentation](api/README.md)** - Endpoint details and examples
- **[Project Map](PROJECT_MAP.md)** - Architecture and data flow
- **[Example Usage](EXAMPLE_USAGE.md)** - Usage examples and patterns

### 📚 Reference
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

### Current Version (1.0) - Released
- ✅ Flask REST API (6 endpoints)
- ✅ Multi-Agent System (Haiku, Sonnet, Opus)
- ✅ 4-Step CTC Generation Pipeline
- ✅ Intelligent Model Routing (41.4% cost savings)
- ✅ Health checks & agent status endpoints
- ✅ Clarification system (ask → answer → generate)
- ✅ Telemetry tracking (tokens, cost, latency, efficiency)
- ✅ Claude API integration
- ✅ MultiAgentClient orchestrator
- ✅ Efficiency calculator

### In Development
- [ ] Database integration (MySQL) for CTC storage
- [ ] Advanced intent extraction features
- [ ] Authentication & authorization
- [ ] Rate limiting
- [ ] Monitoring dashboard
- [ ] Extended unit & integration tests

### Future
- [ ] Web UI for intent submission
- [ ] CTC versioning & history
- [ ] User feedback mechanism
- [ ] Advanced analytics

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
