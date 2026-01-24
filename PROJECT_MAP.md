# GANDALF Project Map
**Updated:** 2026-01-24 (GANDLF-0008: API integration with multi-agent pipeline)

## Overview
GANDALF is a prompt compiler system that converts unstructured user intents into structured Compiled Task Contracts (CTCs) for AI execution agents. Uses multiple Claude models (Haiku, Sonnet, Opus) orchestrated through a 4-step pipeline for cost-optimized processing.

## Project Structure

```
/var/www/projects/gandlf/
├── api/                    # Flask REST API (Port 5000)
│   ├── __init__.py        # Package initialization
│   ├── app.py             # Main Flask application with 6 endpoints
│   ├── multi_agent_client.py # Orchestrates 4-step pipeline
│   └── efficiency_calculator.py # CTC efficiency metrics
│
├── agents/                 # Agent Instructions & Knowledge Base
│   ├── AGENT_ROLE.md      # Agent mission and principles
│   ├── 01_INTENT_ANALYSIS.md  # Intent analysis instructions
│   ├── 02_GAP_DETECTION.md    # Gap detection instructions
│   └── 03_CTC_GENERATION.md   # CTC generation instructions
│
├── multi-agent/            # Multi-Agent HTTP Services (Port 8081)
│   ├── pipeline_agent_service.py # Flask service for 4-step pipeline
│   ├── pipeline_orchestrator.py  # 4-step workflow orchestrator
│   ├── pipeline_model_router.py  # 4-step model routing logic
│   ├── pipeline_client.py   # HTTP client for pipeline service
│   ├── ai_agent_service.py  # AI agent service (legacy)
│   ├── model_router.py      # Model selection logic
│   ├── start_pipeline_agent.sh # Startup script
│   ├── gandalf-ai-agent.service # Systemd service definition
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment configuration
│   ├── README.md            # Multi-agent documentation
│   └── MULTI_AGENT_ARCHITECTURE.md # Architecture details
│
├── assets/                 # Static Assets
│   └── gandalf-logo.jpeg
│
├── demo/                   # Demo Files & Examples
├── tickets/                # Issue Tracking & Summaries
│
└── Documentation
    ├── README.md
    ├── PROJECT_STRUCTURE.md
    ├── PROJECT_MAP.md (this file)
    ├── TECHNOLOGIES.md
    ├── QUICK_START.md
    ├── DEPLOYMENT.md
    ├── QUICK_REFERENCE.md
    ├── LICENSE
    ├── NOTICE
    └── CLA.md
```

## Data Flow

### Request → Response Pipeline

```
User Client
    │
    ├─ HTTP POST /api/intent
    ├─ JSON: {date, generate_for, user_prompt}
    │
    ▼
┌──────────────────────────────────┐
│ Flask API (app.py)               │
│ - Validates request              │
│ - Generates intent_id            │
│ - Creates MultiAgentClient       │
└──────────────┬───────────────────┘
               │
               ├─ HTTP POST to Pipeline Service
               │
               ▼
       ┌───────────────────────────┐
       │ Pipeline Service (8081)   │
       │ PipelineOrchestrator:     │
       │                           │
       │ Step 1: Lexical Analysis  │
       │   └─ Haiku: Keywords,     │
       │      entities, artifacts  │
       │                           │
       │ Step 2: Semantic Analysis │
       │   └─ Sonnet: Semantic     │
       │      frame building       │
       │                           │
       │ Step 3: Coverage Scoring  │
       │   └─ Haiku: Completeness  │
       │      score, questions     │
       │                           │
       │ Step 4: CTC Generation    │
       │   └─ Opus: Final CTC JSON │
       └───────────┬───────────────┘
               │
               ├─ Claude API Calls
               │
               ▼
       ┌───────────────────────────┐
       │ JSON Response with:       │
       │ - CTC or questions        │
       │ - Telemetry data          │
       │ - Status (completed/      │
       │   needs_clarification)    │
       └───────────┬───────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ Flask API (Response Handler)     │
│ - Calculates efficiency          │
│ - Formats response               │
│ - Returns to client              │
└──────────────┬───────────────────┘
               │
               ▼
        User Client Response
```

### Clarification Flow

```
If gaps detected:

1. API returns: {"status": "needs_clarification", "questions": [...]}
2. User submits: POST /api/intent/clarify with answers
3. API resumes pipeline with user context
4. Pipeline generates final CTC
5. API returns: {"status": "completed", "ctc": {...}}
```

## API Endpoints

### Primary Endpoints (Flask API - Port 5000)

#### 1. `GET /health`
Health check endpoint
- **Response:** `{"status": "healthy", "service": "gandalf-api", "timestamp": "ISO-8601"}`
- **Purpose:** Verify API is running
- **File:** api/app.py:41

#### 2. `POST /api/intent`
Submit user intent and receive CTC or clarification questions
- **Request:**
  ```json
  {
    "date": "2026-01-24T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add user authentication to the app"
  }
  ```
- **Response (Clear Intent):**
  ```json
  {
    "status": "completed",
    "intent_id": "uuid",
    "ctc": {
      "title": "Add user authentication",
      "context": [...],
      "definition_of_done": [...],
      "constraints": [...],
      "deliverables": [...]
    },
    "telemetry": {...},
    "efficiency": "85.2%"
  }
  ```
- **Response (Needs Clarification):**
  ```json
  {
    "status": "needs_clarification",
    "intent_id": "uuid",
    "questions": ["What type of auth?", "JWT or session?"],
    "telemetry": {...}
  }
  ```
- **File:** api/app.py

#### 3. `POST /api/intent/clarify`
Submit clarification answers to continue CTC generation
- **Request:**
  ```json
  {
    "intent_id": "uuid",
    "user_prompt": "Add user authentication to the app",
    "clarifications": {
      "question_1": "JWT tokens",
      "question_2": "Stateless auth"
    }
  }
  ```
- **Response:** Complete CTC in GANDALF format
- **File:** api/app.py

#### 4. `GET /api/agent/status`
Check pipeline service availability and configuration
- **Response:**
  ```json
  {
    "status": "ready",
    "pipeline_endpoint": "http://localhost:8081",
    "services": {
      "pipeline": "running",
      "model_router": "healthy"
    },
    "models": ["haiku", "sonnet", "opus"],
    "timestamp": "ISO-8601"
  }
  ```
- **File:** api/app.py

#### 5. `GET /api/ctc/<intent_id>`
Retrieve CTC by intent ID
- **Response:** Complete CTC JSON or 404 error
- **Note:** Database integration in progress
- **File:** api/app.py

#### 6. `GET /api/intents`
List all intents with pagination
- **Query Parameters:** `page=1`, `limit=10`
- **Response:** List of intents with metadata
- **Note:** Database integration in progress
- **File:** api/app.py

## Key Components

### API Layer (`api/`)

#### Main Application (`api/app.py`)
- **Purpose:** Flask REST API server for GANDALF
- **Port:** 5000
- **Key Endpoints:** 6 endpoints (health, intent, clarify, status, ctc, intents)
- **Dependencies:** Flask, flask-cors, MultiAgentClient
- **Status:** ✅ Production-ready

#### MultiAgentClient (`api/multi_agent_client.py`)
- **Purpose:** Orchestrates the 4-step pipeline
- **Key Methods:**
  - `process_intent(user_intent)` - Submit intent to pipeline
  - `submit_clarifications(intent_id, clarifications)` - Continue with answers
  - `get_agent_status()` - Check pipeline health
- **Pipeline Steps:** Lexical → Semantic → Coverage → CTC
- **Status:** ✅ Fully integrated

#### EfficiencyCalculator (`api/efficiency_calculator.py`)
- **Purpose:** Calculates CTC generation efficiency metrics
- **Metrics:** Token usage, cost, quality score
- **Output:** Efficiency percentage (0-100%)
- **Status:** ✅ Active

### Multi-Agent Services (`multi-agent/`)

#### Pipeline Service (`pipeline_agent_service.py`)
- **Purpose:** 4-step CTC generation pipeline
- **Port:** 8081
- **Architecture:** Flask-based HTTP service
- **Models Used:** Haiku, Sonnet, Opus (intelligent routing)
- **Status:** ✅ Running

#### Pipeline Orchestrator (`pipeline_orchestrator.py`)
- **Purpose:** Manages 4-step workflow execution
- **Steps:**
  1. **Lexical Analysis** (Haiku) - Keyword extraction
  2. **Semantic Analysis** (Sonnet) - Semantic frame
  3. **Coverage Scoring** (Haiku) - Completeness assessment
  4. **CTC Generation** (Opus) - Final CTC JSON
- **Status:** ✅ Operational

#### Pipeline Client (`pipeline_client.py`)
- **Purpose:** HTTP client for pipeline service communication
- **Transport:** HTTP POST requests
- **Error Handling:** Retry logic, fallback chain
- **Status:** ✅ Updated to use requests library

#### Pipeline Model Router (`pipeline_model_router.py`)
- **Purpose:** Intelligent model selection for each step
- **Logic:** Routes each step to optimal model
- **Cost Optimization:** 41.4% savings vs. all-Opus
- **Status:** ✅ Optimized

### Agent Instructions (`agents/`)

These consolidated markdown files guide Claude during CTC generation:

#### AGENT_ROLE.md
- Defines agent mission and operating principles
- Specifies output standards (valid JSON, no assumptions)
- Lists core responsibilities

#### 01_INTENT_ANALYSIS.md
- Instructions for analyzing user intents
- Classification criteria (software feature, bug fix, business need, non-technical)
- Clarity scoring (1-5 scale)
- Output schema with examples

#### 02_GAP_DETECTION.md
- Instructions for detecting missing information
- Gap categories (technical, scope, context, quality)
- Severity classification (blocking, important, nice-to-have)
- Clarification question generation rules (max 3 questions)

#### 03_CTC_GENERATION.md
- Instructions for generating complete CTCs
- GANDALF schema compliance requirements
- Section-by-section generation guidance
- Examples for different intent types

### CTC Structure
Based on CompiledOutputSchema.md:
```json
{
  "gandalf_version": "1.0",
  "ctc": {
    "title": "...",
    "context": [...],
    "definition_of_done": [...],
    "constraints": [...],
    "deliverables": [...]
  },
  "clarifications": {...},
  "telemetry": {...}
}
```

### Startup Process (VM Boot)
1. Multipass VM starts with cloud-init.yaml
2. MySQL installed and configured
3. Python venv created with dependencies
4. API directory structure created
5. systemd service `gandalf-api.service` enabled
6. Gunicorn starts Flask app on port 5000
7. Health check verifies API is running

## Environment Variables

### Flask API
- `FLASK_ENV` - production/development
- `FLASK_PORT` - API port (default: 5000)
- `FLASK_DEBUG` - Debug mode (default: False)

### Multi-Agent System (GANDLF-0005)
- `ANTHROPIC_API_KEY` - **Required** - Anthropic API key for Claude models
- `GANDALF_AGENT_ENDPOINT` - AI agent service URL (default: http://localhost:8080/agent)
- `GANDALF_AGENT_PORT` - AI agent service port (default: 8080)
- `GANDALF_ENABLE_HAIKU` - Enable Haiku model (default: true)
- `GANDALF_ENABLE_OPUS` - Enable Opus model (default: true)
- `GANDALF_DEFAULT_MODEL` - Default model: haiku|sonnet|opus (default: sonnet)
- `GANDALF_FORCE_MODEL` - Force all tasks to one model (for testing, default: empty)
- `GANDALF_MAX_TOKENS_HAIKU` - Max tokens for Haiku (default: 2000)
- `GANDALF_MAX_TOKENS_SONNET` - Max tokens for Sonnet (default: 4000)
- `GANDALF_MAX_TOKENS_OPUS` - Max tokens for Opus (default: 8000)

### Database
- Database credentials stored in `/etc/gandalf/db.env` (TODO)

## Database (TODO)
- **Host:** localhost
- **Database:** gandalf
- **User:** gandalf
- **Tables:** (to be defined)
  - intents - Store user intents
  - ctcs - Store generated CTCs
  - telemetry - Execution metrics

## Deployment

### VM Provisioning
```bash
multipass launch --name gandalf --cloud-init cloud-init/gandalf-cloud-init.yaml
```

### Service Management
```bash
systemctl status gandalf-api
systemctl start gandalf-api
systemctl stop gandalf-api
systemctl restart gandalf-api
```

### Logs
- Access log: `/var/log/gandalf/access.log`
- Error log: `/var/log/gandalf/error.log`
- System log: `journalctl -u gandalf-api`

## Testing

### Health Check
```bash
curl http://localhost:5000/health
```

### Submit Intent
```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add user authentication to the app"
  }'
```

## Implementation Status

### Completed (GANDLF-0008) - API Integration with Multi-Agent Pipeline
- ✅ Flask REST API (6 endpoints, fully functional)
- ✅ MultiAgentClient for orchestrating 4-step pipeline
- ✅ Integration with pipeline service (port 8081)
- ✅ Clarification system (ask → answer → generate)
- ✅ Agent status endpoint
- ✅ Efficiency calculator with telemetry
- ✅ Error handling and validation
- ✅ CORS enabled for all routes
- ✅ Updated PROJECT_STRUCTURE.md, README.md, PROJECT_MAP.md

### Completed (GANDLF-0006) - 4-Step Multi-Model Pipeline
- ✅ Pipeline orchestrator with 4-step workflow
- ✅ Pipeline model router (intelligent routing)
- ✅ Pipeline client with HTTP communication
- ✅ Cost optimization (41.4% savings vs. all-Opus)
- ✅ Step-wise model selection (Haiku→Sonnet→Haiku→Opus)
- ✅ Telemetry tracking per step
- ✅ Fallback chain for model unavailability
- ✅ Test suite (test_pipeline.py)
- ✅ Comprehensive documentation (MULTI_MODEL_PIPELINE.md)
- ✅ Startup scripts and service definitions

### Completed (GANDLF-0005) - Multi-Agent System
- ✅ ModelRouter for intelligent model selection
- ✅ AI Agent Service with multi-model support
- ✅ HTTP communication (using requests library)
- ✅ Telemetry tracking per model
- ✅ Configuration via environment variables
- ✅ Test suite for model router
- ✅ Comprehensive documentation
- ✅ Startup scripts and systemd service files

### Completed (GANDLF-0004) - AI Agent Based Implementation
- ✅ Consolidated agent instructions (4 files)
- ✅ Agent communication module
- ✅ Workflow orchestration
- ✅ Clarification question workflow
- ✅ Comprehensive documentation

## Architecture Overview

### System Components

```
┌─────────────────────────────────────┐
│ Flask API (Port 5000)               │
│ - 6 HTTP endpoints                  │
│ - Request validation                │
│ - Response formatting               │
└─────────────┬───────────────────────┘
              │ HTTP POST
              ▼
┌─────────────────────────────────────┐
│ MultiAgentClient (api/)             │
│ - Orchestrates 4-step pipeline      │
│ - Manages session state             │
│ - Handles clarifications            │
└─────────────┬───────────────────────┘
              │ HTTP POST
              ▼
┌─────────────────────────────────────┐
│ Pipeline Service (Port 8081)        │
│ - PipelineOrchestrator              │
│ - 4-step workflow execution         │
│ - PipelineModelRouter               │
└─────────────┬───────────────────────┘
              │ Claude API calls
              ▼
┌─────────────────────────────────────┐
│ Claude Models                       │
│ ├─ Haiku (Steps 1, 3)              │
│ ├─ Sonnet (Step 2)                 │
│ └─ Opus (Step 4)                   │
└─────────────────────────────────────┘
```

### Data Flow (Detailed)

1. **User** submits intent via Flask API
2. **Flask API** validates request, generates intent_id
3. **MultiAgentClient** sends intent to Pipeline Service
4. **Pipeline Service** orchestrates 4 steps:
   - **Step 1:** Lexical analysis (Haiku)
   - **Step 2:** Semantic analysis (Sonnet)
   - **Step 3:** Coverage scoring (Haiku)
   - **Step 4:** CTC generation (Opus)
5. **Claude API** processes with selected model
6. **Pipeline** returns CTC or clarification questions
7. **Flask API** formats response with telemetry
8. **User** receives CTC or questions
9. (Optional) **User** submits clarifications
10. **Pipeline** resumes with user context
11. **Flask API** returns complete CTC

## Starting the System

### Prerequisites
```bash
# Install dependencies
cd /var/www/projects/gandlf
pip3 install -r requirements.txt
cd multi-agent
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Start Services

**Terminal 1: Pipeline Service**
```bash
cd /var/www/projects/gandlf/multi-agent
./start_pipeline_agent.sh
# Service runs on port 8081
```

**Terminal 2: Flask API**
```bash
cd /var/www/projects/gandlf
python3 -m api.app
# API runs on port 5000
```

### Test the System

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

# Check pipeline status
curl http://localhost:5000/api/agent/status
```

## Environment Variables

### API Configuration
```bash
GANDALF_PIPELINE_ENDPOINT=http://localhost:8081  # Pipeline service URL
FLASK_ENV=production                             # Flask environment
FLASK_DEBUG=False                                # Disable debug mode
```

### Pipeline Configuration
```bash
ANTHROPIC_API_KEY=                    # Required: Anthropic API key
GANDALF_AGENT_PORT=8080              # AI agent service port
GANDALF_PIPELINE_PORT=8081           # Pipeline service port
GANDALF_ENABLE_HAIKU=true            # Enable Haiku model
GANDALF_ENABLE_SONNET=true           # Enable Sonnet model
GANDALF_ENABLE_OPUS=true             # Enable Opus model
GANDALF_DEFAULT_MODEL=sonnet         # Default model selection
GANDALF_FORCE_MODEL=                 # Force one model (testing)
GANDALF_MAX_TOKENS_HAIKU=2000        # Haiku max tokens
GANDALF_MAX_TOKENS_SONNET=4000       # Sonnet max tokens
GANDALF_MAX_TOKENS_OPUS=8000         # Opus max tokens
```

## CTC Structure

Based on GANDALF schema:
```json
{
  "gandalf_version": "1.0",
  "ctc": {
    "title": "...",
    "context": ["..."],
    "definition_of_done": ["..."],
    "constraints": ["..."],
    "deliverables": ["..."]
  },
  "clarifications": {
    "asked": ["..."],
    "resolved_by": "default|user"
  },
  "telemetry": {
    "intent_id": "uuid",
    "created_at": "ISO-8601",
    "executor": {"name": "claude-code", "version": "1.0"},
    "elapsed_ms": 0,
    "input_tokens": null,
    "output_tokens": null,
    "user_questions_count": 0,
    "execution_result": "unknown",
    "efficiency": "85.2%"
  }
}
```

## Next Steps (TODOs)

### High Priority
1. **Database Integration** - Store intents and CTCs in MySQL
2. **GET /api/ctc/<id>** - Retrieve CTCs from database
3. **GET /api/intents** - List intents with pagination
4. **Authentication/Authorization** - Secure API endpoints
5. **Rate Limiting** - Prevent abuse

### Medium Priority
6. **Monitoring Dashboard** - Visual metrics and telemetry
7. **Extended Testing** - Unit and integration tests
8. **Error Recovery** - Enhanced error handling and retries
9. **Performance Optimization** - Caching and optimization
10. **Documentation** - API usage examples and guides

### Low Priority
11. **Web UI** - Browser-based intent submission
12. **CTC Versioning** - Track CTC history
13. **User Feedback** - CTC quality rating system
14. **Advanced Analytics** - Cost and efficiency analysis

## References

- **GANDALF System Prompt:** GANDALF.md
- **CTC Schema:** CompiledOutputSchema.md
- **Multi-Agent Architecture:** multi-agent/MULTI_AGENT_ARCHITECTURE.md
- **Pipeline Documentation:** multi-agent/MULTI_MODEL_PIPELINE.md
- **API Documentation:** api/README.md
