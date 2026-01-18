# GANDALF Quick Start Guide

## What is GANDALF?

GANDALF converts vague user requests into precise, actionable Compiled Task Contracts (CTCs) using an AI agent.

**Example:**
- **User says:** "We need better reporting"
- **GANDALF asks:** What data? What format? Who needs it?
- **User answers:** Sales data, Excel, Managers only
- **GANDALF generates:** Complete CTC with requirements, constraints, deliverables

## How It Works

```
User Request → Flask API → AI Agent (analyzes & generates) → CTC or Questions
```

The AI agent reads instruction files to understand how to analyze intents and generate CTCs.

## Quick Start

### Prerequisites

1. GANDALF VM running (see cloud-init/gandalf-cloud-init.yaml)
2. Python 3.8+ installed
3. AI agent service implemented (see AI_AGENT_IMPLEMENTATION_GUIDE.md)

### Step 1: Implement AI Agent Service

**Required:** You must create an HTTP service in the GANDALF VM that:
- Listens on port 8080
- Accepts requests with instructions and payload
- Calls an LLM (Claude, GPT, etc.)
- Returns JSON following the instruction schemas

See **AI_AGENT_IMPLEMENTATION_GUIDE.md** for complete instructions.

### Step 2: Configure Environment

```bash
# Set AI agent endpoint
export GANDALF_AGENT_ENDPOINT="http://localhost:8080/agent"

# Optional: Flask configuration
export FLASK_PORT=5000
export FLASK_DEBUG=False
```

### Step 3: Start Flask API

```bash
cd /opt/apps/gandlf
python -m api.app
```

The API will start on http://localhost:5000

### Step 4: Test It

**Test health:**
```bash
curl http://localhost:5000/health
```

**Submit a clear intent:**
```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-19T12:00:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "Add a logout button to the navigation bar"
  }'
```

**Expected:** Complete CTC with title, context, DoD, constraints, deliverables

**Submit a vague intent:**
```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-19T12:00:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "We need better reporting"
  }'
```

**Expected:** Clarification questions asking about data type, format, and access

**Submit clarifications:**
```bash
curl -X POST http://localhost:5000/api/intent/clarify \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-19T12:00:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "We need better reporting",
    "clarifications": {
      "data_type": "sales",
      "format": "excel",
      "access": "managers"
    }
  }'
```

**Expected:** Complete CTC incorporating the clarifications

## API Endpoints

### POST /api/intent
Submit user intent, receive CTC or clarification questions

**Request:**
```json
{
  "date": "2024-01-19T12:00:00Z",
  "generate_for": "AI-AGENT",
  "user_prompt": "your request here"
}
```

**Response (Clear Intent):**
```json
{
  "intent_id": "uuid",
  "status": "completed",
  "ctc": {
    "title": "...",
    "context": "...",
    "definition_of_done": [...],
    "constraints": [...],
    "deliverables": [...]
  }
}
```

**Response (Vague Intent):**
```json
{
  "intent_id": "uuid",
  "status": "needs_clarification",
  "clarification_questions": [
    {
      "question": "What type of data?",
      "options": [...],
      "default": "..."
    }
  ]
}
```

### POST /api/intent/clarify
Submit answers to clarification questions

**Request:**
```json
{
  "date": "2024-01-19T12:00:00Z",
  "generate_for": "AI-AGENT",
  "user_prompt": "original request",
  "clarifications": {
    "answer_key_1": "value1",
    "answer_key_2": "value2"
  }
}
```

**Response:** Complete CTC

### GET /api/agent/status
Check if AI agent is available

**Response:**
```json
{
  "status": "ready|error",
  "agent_endpoint": "http://localhost:8080/agent",
  "prompts_dir": "/opt/apps/gandlf/ai_agent_prompts",
  "prompts_loaded": true
}
```

### GET /health
Check API health

**Response:**
```json
{
  "status": "healthy",
  "service": "gandalf-api",
  "timestamp": "2024-01-19T12:00:00Z"
}
```

## Project Structure

```
/opt/apps/gandlf/
├── ai_agent_prompts/          → Instructions for AI agent
│   ├── AGENT_ROLE.md          → Agent mission
│   ├── 01_INTENT_ANALYSIS.md  → How to analyze intents
│   ├── 02_GAP_DETECTION.md    → How to detect gaps
│   └── 03_CTC_GENERATION.md   → How to generate CTCs
├── gandalf_agent/             → AI agent communication
│   ├── agent_client.py        → HTTP client
│   └── ctc_orchestrator.py    → Workflow manager
├── api/
│   └── app.py                 → Flask REST API
└── AI_AGENT_IMPLEMENTATION_GUIDE.md  → Complete implementation guide
```

## Troubleshooting

### "AI Agent communication not yet implemented"

You need to implement the AI agent service first. See AI_AGENT_IMPLEMENTATION_GUIDE.md

### "Connection refused"

The AI agent service is not running. Start it on port 8080.

### "Invalid JSON response"

The AI agent must return ONLY JSON, no markdown code blocks. Check agent implementation.

### "Timeout"

The AI agent must respond within 30 seconds. Optimize LLM inference or increase timeout.

## Next Steps

1. **Implement AI Agent Service** (see AI_AGENT_IMPLEMENTATION_GUIDE.md)
2. Test with demo examples
3. Add database for storing CTCs
4. Create web UI for easier interaction
5. Add authentication and rate limiting

## Documentation

- **AI_AGENT_IMPLEMENTATION_GUIDE.md** - How to implement the AI agent
- **GANDLF-0004_COMPLETION_SUMMARY.md** - Complete implementation summary
- **PROJECT_MAP.md** - Project architecture and components
- **GANDALF.md** - Original specification
- **CompiledOutputSchema.md** - CTC schema

## Support

For issues or questions:
1. Check AI_AGENT_IMPLEMENTATION_GUIDE.md
2. Review PROJECT_MAP.md for architecture
3. Check logs: Flask API logs errors to stdout
4. Verify agent status: `curl http://localhost:5000/api/agent/status`

---

**Ready to start?** Implement the AI agent service following AI_AGENT_IMPLEMENTATION_GUIDE.md
