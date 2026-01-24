# GANDALF Project Structure - Cleaned v2.0

## Project Overview
Multi-agent architecture for GANDALF using Claude AI models with hierarchical task processing.

## Directory Structure

```
gandlf/
├── .git/                          # Git repository
├── agents/                         # Agent Instructions & Knowledge Base
│   ├── AGENT_ROLE.md             # Agent's mission & operating principles
│   ├── 01_INTENT_ANALYSIS.md     # Intent analysis task instructions
│   ├── 02_GAP_DETECTION.md       # Gap detection task instructions
│   └── 03_CTC_GENERATION.md      # CTC generation task instructions
│
├── multi-agent/                    # Multi-Agent HTTP Services (PRIMARY)
│   ├── ai_agent_service.py       # Flask service for AI agent processing
│   ├── pipeline_agent_service.py # Flask service for pipeline orchestration
│   ├── model_router.py           # Model selection & routing logic
│   ├── pipeline_model_router.py  # Pipeline-specific model routing
│   ├── pipeline_orchestrator.py  # Pipeline execution orchestrator
│   ├── pipeline_client.py        # Client for pipeline service
│   ├── start_ai_agent.sh         # Startup script for AI agent
│   ├── start_pipeline_agent.sh   # Startup script for pipeline agent
│   ├── gandalf-ai-agent.service  # Systemd service definition
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variables template
│   ├── test_multi_agent.py       # Multi-agent testing
│   ├── test_pipeline.py          # Pipeline testing
│   ├── README.md                 # Multi-agent documentation
│   ├── MULTI_AGENT_ARCHITECTURE.md    # Architecture details
│   ├── MULTI_MODEL_PIPELINE.md        # Pipeline documentation
│   ├── QUICK_START.md                 # Quick start guide
│   └── QUICK_START_PIPELINE.md        # Pipeline quick start
│
├── api/                            # API Integration Layer
│   ├── config.php
│   └── agent_request.php
│
├── assets/                         # Static Assets
│   └── gandalf-logo.jpeg
│
├── demo/                           # Demo Files
│   └── [demo files]
│
├── tickets/                        # Issue Tracking
│   └── [ticket files]
│
└── [Documentation Files]
    ├── README.md
    ├── LICENSE
    ├── NOTICE
    └── CLA.md

```

## Key Components

### 1. **agents/** - Agent Knowledge Base
The consolidated agent instructions for GANDALF:
- **AGENT_ROLE.md** - Defines the agent's mission, principles, and operating context
- **01_INTENT_ANALYSIS.md** - Instructions for analyzing user intents and extracting information
- **02_GAP_DETECTION.md** - Instructions for detecting gaps in user requirements
- **03_CTC_GENERATION.md** - Instructions for generating Complete Test Cases (CTCs)

### 2. **multi-agent/** - Production Services (ACTIVE)
HTTP services for running GANDALF agents:
- **ai_agent_service.py** - Main Flask service that processes requests using Claude models
- **pipeline_agent_service.py** - Advanced pipeline orchestration service
- **model_router.py** - Intelligent model selection (Haiku/Sonnet/Opus)
- **pipeline_orchestrator.py** - Complex workflow orchestration
- Startup scripts for both services
- Comprehensive testing and documentation

### 3. **api/** - REST API Layer
Integration layer for web applications:
- PHP endpoints for agent requests
- Configuration management

### 4. **demo/** & **tickets/**
Demo implementations and project tracking.

## Removed Components
- **gandalf_agent/** ❌ REMOVED (redundant single-agent implementation)
- Old documentation files in agents/ ❌ REMOVED (consolidated into 4 main files)

## Multi-Agent Architecture

```
Request Flow:
┌─────────────┐
│ Web/API     │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│ multi-agent/ai_agent*    │
│ (Request Handler)        │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ model_router.py          │
│ (Select: Haiku/Sonnet/   │
│  Opus based on task)     │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Claude API               │
│ (Process with selected   │
│  model)                  │
└──────────────────────────┘
```

### Model Selection Strategy
- **Haiku** - Intent analysis, gap detection (fast, cost-effective)
- **Sonnet** - Standard CTC generation (balanced)
- **Opus** - Complex analysis, edge cases (highest quality)

## Configuration

Environment variables in `multi-agent/.env`:
```
ANTHROPIC_API_KEY=          # Claude API key
GANDALF_AGENT_PORT=8080     # AI agent service port
GANDALF_PIPELINE_PORT=8081  # Pipeline service port
GANDALF_ENABLE_HAIKU=true   # Enable Haiku model
GANDALF_ENABLE_OPUS=true    # Enable Opus model
GANDALF_DEFAULT_MODEL=sonnet
```

## Running the Services

### AI Agent Service
```bash
cd /var/www/projects/gandlf/multi-agent
./start_ai_agent.sh
```

### Pipeline Agent Service
```bash
cd /var/www/projects/gandlf/multi-agent
./start_pipeline_agent.sh
```

## Project Status
✅ Clean multi-agent architecture
✅ Consolidated agent instructions
✅ Production-ready services
✅ Removed redundant components
✅ Ready for deployment

---
**Last Updated:** 2026-01-24
