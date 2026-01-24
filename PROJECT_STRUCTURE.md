# GANDALF Project Structure - v3.0

## Project Overview
Multi-agent architecture for GANDALF using Claude AI models with 4-step CTC generation pipeline. The system converts unstructured user intents into Compiled Task Contracts (CTCs) through intelligent model routing and orchestration.

## Directory Structure

```
/var/www/projects/gandlf/
├── .git/                          # Git repository
├── agents/                         # Agent Instructions & Knowledge Base
│   ├── AGENT_ROLE.md             # Agent's mission & operating principles
│   ├── 01_INTENT_ANALYSIS.md     # Intent analysis task instructions
│   ├── 02_GAP_DETECTION.md       # Gap detection task instructions
│   └── 03_CTC_GENERATION.md      # CTC generation task instructions
│
├── multi-agent/                    # Multi-Agent HTTP Services (PRIMARY)
│   ├── ai_agent_service.py       # Flask service for AI agent processing
│   ├── pipeline_agent_service.py # Flask service for 4-step pipeline
│   ├── model_router.py           # Model selection logic (Haiku/Sonnet/Opus)
│   ├── pipeline_model_router.py  # 4-step pipeline model routing
│   ├── pipeline_orchestrator.py  # 4-step pipeline orchestrator
│   ├── pipeline_client.py        # HTTP client for pipeline service
│   ├── start_ai_agent.sh         # Startup script for AI agent
│   ├── start_pipeline_agent.sh   # Startup script for pipeline agent
│   ├── gandalf-ai-agent.service  # Systemd service definition
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variables template
│   ├── test_multi_agent.py       # Multi-agent testing
│   ├── test_pipeline.py          # Pipeline testing
│   ├── README.md                 # Multi-agent documentation
│   ├── MULTI_AGENT_ARCHITECTURE.md    # Architecture details
│   ├── MULTI_MODEL_PIPELINE.md        # 4-step pipeline documentation
│   ├── QUICK_START.md                 # Quick start guide
│   └── QUICK_START_PIPELINE.md        # Pipeline quick start
│
├── api/                            # Flask REST API (Python)
│   ├── __init__.py               # Package initialization
│   ├── app.py                    # Main Flask application with endpoints
│   ├── multi_agent_client.py     # Client for multi-agent pipeline
│   ├── efficiency_calculator.py  # CTC efficiency metrics
│   └── README.md                 # API documentation
│
├── assets/                         # Static Assets
│   └── gandalf-logo.jpeg
│
├── demo/                           # Demo Files & Examples
│   └── [demo files]
│
├── tickets/                        # Issue Tracking & Summaries
│   └── [ticket files]
│
└── Documentation Files
    ├── README.md                  # Main project documentation
    ├── PROJECT_STRUCTURE.md       # This file
    ├── PROJECT_MAP.md             # Architecture & data flow
    ├── TECHNOLOGIES.md            # Tech stack details
    ├── QUICK_REFERENCE.md         # Quick reference guide
    ├── DEPLOYMENT.md              # Deployment guide
    ├── QUICK_START.md             # Quick start guide
    ├── LICENSE
    ├── NOTICE
    └── CLA.md

```

## Key Components

### 1. **agents/** - Agent Knowledge Base (Consolidated)
The consolidated agent instructions for GANDALF:
- **AGENT_ROLE.md** - Defines the agent's mission, principles, and operating context
- **01_INTENT_ANALYSIS.md** - Instructions for analyzing user intents and extracting information
- **02_GAP_DETECTION.md** - Instructions for detecting gaps in user requirements
- **03_CTC_GENERATION.md** - Instructions for generating Complete Test Cases (CTCs)

### 2. **multi-agent/** - Multi-Agent HTTP Services (Backend)
HTTP services for running the multi-agent CTC generation pipeline:
- **ai_agent_service.py** - Flask service with Claude model integration
- **pipeline_agent_service.py** - Advanced 4-step pipeline orchestration
- **model_router.py** - Intelligent model selection (Haiku/Sonnet/Opus)
- **pipeline_model_router.py** - 4-step pipeline model routing
- **pipeline_orchestrator.py** - Complex 4-step workflow orchestration
- **pipeline_client.py** - HTTP client for pipeline service
- Startup scripts and systemd service definitions
- Comprehensive testing and documentation

### 3. **api/** - Flask REST API Layer (PRIMARY)
Python Flask API for client integration:
- **app.py** - Main REST API endpoints (6 endpoints)
- **multi_agent_client.py** - Orchestrates 4-step pipeline
- **efficiency_calculator.py** - CTC efficiency metrics
- Integrated with multi-agent backend
- CORS enabled for all routes

### 4. **demo/** & **tickets/**
Demo implementations and project tracking documents.

## Removed Components
- **gandalf_agent/** ❌ REMOVED (replaced by multi-agent system)
- Old documentation files in agents/ ❌ REMOVED (consolidated into 4 main files)
- PHP API layer ❌ REMOVED (replaced by Python Flask API)

## Multi-Agent Architecture

```
Request Flow (4-Step Pipeline):

┌─────────────────────────────────────────────────────┐
│ Flask API (/api/intent)                             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │ MultiAgentClient      │
       │ (Orchestrator)        │
       └───────────┬───────────┘
                   │
    ┌──────────────┴──────────────┐
    │    Pipeline Orchestrator    │
    │                             │
    │  Step 1: Lexical Analysis   │──> Haiku (fast, cheap)
    │  Step 2: Semantic Analysis  │──> Sonnet (balanced)
    │  Step 3: Coverage Scoring   │──> Haiku (fast, cheap)
    │  Step 4: CTC Generation     │──> Opus (powerful)
    │                             │
    └──────────────┬──────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Claude API          │
        │  (Selected Model)    │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  CTC JSON Response   │
        │  (with telemetry)    │
        └──────────────────────┘
```

### Model Selection Strategy
- **Haiku** (Fast, Cost-effective): Intent analysis, validation, coverage scoring
- **Sonnet** (Balanced): Semantic analysis, gap detection, question generation
- **Opus** (Powerful): Complex CTC generation, deep reasoning, edge cases
- **Cost Savings**: 41.4% compared to all-Opus approach

## Configuration

### Environment Variables
Location: `multi-agent/.env`

```bash
# Claude API
ANTHROPIC_API_KEY=your_key_here    # Anthropic API key (required)

# Service Ports
GANDALF_AGENT_PORT=8080            # AI agent service port
GANDALF_PIPELINE_PORT=8081         # Pipeline service port
GANDALF_FLASK_PORT=5000            # Flask API port

# Model Configuration
GANDALF_ENABLE_HAIKU=true          # Enable Haiku model
GANDALF_ENABLE_SONNET=true         # Enable Sonnet model
GANDALF_ENABLE_OPUS=true           # Enable Opus model
GANDALF_DEFAULT_MODEL=sonnet       # Default model selection
GANDALF_FORCE_MODEL=               # Force all tasks to one model (testing)

# Token Limits
GANDALF_MAX_TOKENS_HAIKU=2000      # Haiku max tokens
GANDALF_MAX_TOKENS_SONNET=4000     # Sonnet max tokens
GANDALF_MAX_TOKENS_OPUS=8000       # Opus max tokens

# API Configuration
GANDALF_PIPELINE_ENDPOINT=http://localhost:8080  # Pipeline service URL
```

## Running the Services

### 1. Start Multi-Agent Backend
```bash
cd /var/www/projects/gandlf/multi-agent
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
./start_pipeline_agent.sh  # Starts pipeline on port 8081
```

### 2. Start Flask API
```bash
cd /var/www/projects/gandlf
python3 -m api.app  # Starts API on port 5000
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
    "user_prompt": "Add user authentication"
  }'
```

## API Endpoints

### Available Endpoints (Flask API - Port 5000)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/api/intent` | Submit user intent, get CTC or clarifications |
| POST | `/api/intent/clarify` | Submit clarification answers |
| GET | `/api/ctc/<intent_id>` | Retrieve CTC by ID |
| GET | `/api/intents` | List all intents |
| GET | `/api/agent/status` | Check pipeline status |

## Project Status
✅ Multi-agent architecture (Haiku, Sonnet, Opus)
✅ 4-step CTC generation pipeline
✅ Flask REST API fully integrated
✅ Intelligent model routing (41.4% cost savings)
✅ Consolidated agent instructions
✅ Production-ready services
✅ Telemetry & efficiency tracking
✅ Removed redundant components

## Next Steps
- [ ] MySQL database integration for CTC storage
- [ ] Advanced intent analysis features
- [ ] Monitoring and metrics dashboard
- [ ] Rate limiting and authentication
- [ ] Extended test coverage

---
**Last Updated:** 2026-01-24
**Version:** 3.0
**Ticket:** GANDLF-0008
