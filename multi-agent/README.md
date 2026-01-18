# Multi-Agent System

**Ticket:** GANDLF-0005
**Last Updated:** 2026-01-19

## Overview

The GANDALF multi-agent system uses different Claude models (Haiku, Sonnet, Opus) for different tasks to optimize cost and performance:

- **Haiku**: Fast, cheap - classification, validation, formatting
- **Sonnet**: Balanced - analysis, gap detection, question generation
- **Opus**: Powerful, expensive - complex CTC generation and reasoning

## Architecture

```
User Intent
    ↓
Flask API
    ↓
CTCOrchestrator
    ↓
AgentClient (HTTP)
    ↓
AI Agent Service (multi-agent/)
    ↓
ModelRouter → Selects appropriate model
    ↓
Claude API (Haiku/Sonnet/Opus)
    ↓
Response → User
```

## Components

### 1. Model Router (`model_router.py`)
- Determines which model to use for each task
- Handles fallback if primary model unavailable
- Tracks cost and token usage

### 2. AI Agent Service (`ai_agent_service.py`)
- HTTP service listening on port 8080
- Receives requests from AgentClient
- Routes to appropriate Claude model
- Returns JSON responses

### 3. Updated AgentClient (`../gandalf_agent/agent_client.py`)
- HTTP communication enabled (using httpx)
- Sends requests to AI Agent Service
- Handles errors and timeouts

## Installation

### 1. Install Dependencies

```bash
cd /opt/apps/gandlf
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create `.env` file or export variables:

```bash
# Required: Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Optional: Model configuration
export GANDALF_ENABLE_HAIKU=true          # Enable Haiku for fast tasks
export GANDALF_ENABLE_OPUS=true           # Enable Opus for complex tasks
export GANDALF_DEFAULT_MODEL=sonnet       # Default model
export GANDALF_FORCE_MODEL=                # Force all tasks to one model (testing)

# Optional: Agent endpoint
export GANDALF_AGENT_ENDPOINT=http://localhost:8080/agent
export GANDALF_AGENT_PORT=8080

# Optional: Flask API
export FLASK_PORT=5000
export FLASK_DEBUG=False
```

### 3. Start the AI Agent Service

```bash
cd /opt/apps/gandlf/multi-agent
python ai_agent_service.py
```

The service will start on port 8080 (configurable via `GANDALF_AGENT_PORT`).

### 4. Start the Flask API

In another terminal:

```bash
cd /opt/apps/gandlf
python -m api.app
```

The API will start on port 5000 (configurable via `FLASK_PORT`).

## Usage

### Submit an Intent

```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T12:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add a logout button to the navigation bar"
  }'
```

### Check Agent Status

```bash
curl http://localhost:5000/api/agent/status
```

### Check AI Service Health

```bash
curl http://localhost:8080/health
```

### List Available Models

```bash
curl http://localhost:8080/models
```

### View Telemetry

```bash
curl http://localhost:8080/telemetry
```

## Model Selection Logic

The `ModelRouter` automatically selects models based on task type:

| Task | Model | Reason |
|------|-------|--------|
| Classify intent | Haiku | Simple classification |
| Extract keywords | Haiku | Fast extraction |
| Score clarity | Sonnet | Nuanced analysis |
| Detect gaps | Sonnet | Context understanding |
| Generate questions | Sonnet | Good at formulation |
| Prioritize questions | Haiku | Simple ranking |
| **Generate CTC** | **Opus** | **Complex reasoning** |
| Validate format | Haiku | Schema checking |
| Calculate efficiency | Haiku | Simple math |

## Cost Optimization

### Expected Savings

- **Simple intents** (clear requirements): 30-40% cost reduction
- **Medium intents** (some gaps): 20-30% cost reduction
- **Complex intents** (major gaps): 10-20% cost reduction

### Example Cost Breakdown

**User Intent:** "Add user authentication"

| Step | Model | Input Tokens | Output Tokens | Cost |
|------|-------|--------------|---------------|------|
| Classify | Haiku | 200 | 100 | $0.0001 |
| Score clarity | Sonnet | 400 | 200 | $0.0042 |
| Detect gaps | Sonnet | 600 | 400 | $0.0078 |
| Generate questions | Sonnet | 500 | 300 | $0.0060 |
| Generate CTC | Opus | 1200 | 2000 | $0.1680 |
| Validate | Haiku | 400 | 50 | $0.0002 |
| **Total** | - | **3300** | **3050** | **$0.1863** |

**Comparison** (all Sonnet): $0.2205 → **Savings: 15.5%**

## Configuration Options

### Force Specific Model (Testing)

Test with only one model:

```bash
# Test everything with Haiku (fast, cheap)
export GANDALF_FORCE_MODEL=haiku
python ai_agent_service.py

# Test everything with Opus (high quality)
export GANDALF_FORCE_MODEL=opus
python ai_agent_service.py
```

### Disable Expensive Models

Reduce cost by disabling Opus:

```bash
export GANDALF_ENABLE_OPUS=false
```

Now complex CTC generation will use Sonnet instead of Opus.

### Custom Model Preference

You can specify model preference in API request:

```json
{
  "date": "2026-01-19T12:00:00Z",
  "generate_for": "claude-code",
  "user_prompt": "Add user authentication",
  "model_preference": "opus"
}
```

## Telemetry

The AI agent service tracks:

- Request count per model
- Token usage (input/output) per model
- Cost per model
- Error rate
- Latency per model

View telemetry:

```bash
curl http://localhost:8080/telemetry
```

Reset telemetry:

```bash
curl -X POST http://localhost:8080/telemetry/reset
```

## Troubleshooting

### "Cannot connect to AI Agent"

**Problem:** AgentClient can't reach AI Agent Service

**Solution:**
1. Check if AI Agent Service is running: `curl http://localhost:8080/health`
2. Check `GANDALF_AGENT_ENDPOINT` is correct
3. Check firewall/network settings

### "ANTHROPIC_API_KEY not set"

**Problem:** AI Agent Service can't call Claude API

**Solution:**
1. Get API key from https://console.anthropic.com
2. Export: `export ANTHROPIC_API_KEY=your-key`
3. Restart AI Agent Service

### "Invalid JSON response"

**Problem:** Claude returned malformed JSON

**Solution:**
1. Check instruction files in `ai_agent_prompts/`
2. Ensure examples show valid JSON only
3. Review system prompt in AI Agent Service

### "Timeout errors"

**Problem:** Requests taking too long

**Solution:**
1. Check model timeout settings in `model_router.py`
2. Increase timeout in `agent_client.py` (currently 60s)
3. Use faster model (Haiku instead of Opus) for testing

### High costs

**Problem:** Spending too much on API calls

**Solution:**
1. Disable Opus: `export GANDALF_ENABLE_OPUS=false`
2. Use Haiku for testing: `export GANDALF_FORCE_MODEL=haiku`
3. Check telemetry to identify expensive tasks
4. Cache common intents (future enhancement)

## Testing

### Test Model Router

```python
from model_router import ModelRouter, TaskType

router = ModelRouter()

# Test model selection
model = router.select_model("classify_intent")
print(f"Model for classification: {model.value}")

# Test workflow plan
plan = router.get_workflow_model_plan(intent_complexity="medium")
for step, model in plan.items():
    print(f"{step}: {model.value}")

# Test cost estimation
cost = router.estimate_cost(model, input_tokens=1000, output_tokens=500)
print(f"Estimated cost: ${cost:.6f}")
```

### Test AI Agent Service

```bash
# Health check
curl http://localhost:8080/health

# List models
curl http://localhost:8080/models

# Test intent analysis
curl -X POST http://localhost:8080/agent \
  -H "Content-Type: application/json" \
  -d @test_intent_request.json
```

### End-to-End Test

```bash
cd /opt/apps/gandlf/scripts
python test_ctc_generation.py
```

## Files

```
/opt/apps/gandlf/multi-agent/
├── README.md                      → This file
├── MULTI_AGENT_ARCHITECTURE.md   → Architecture design document
├── model_router.py                → Model selection logic
├── ai_agent_service.py            → HTTP service with multi-model support
├── requirements.txt               → Python dependencies
└── .env.example                   → Example environment variables
```

## Next Steps

1. **Production Deployment:**
   - Use gunicorn for AI Agent Service
   - Set up systemd service
   - Configure nginx reverse proxy
   - Enable HTTPS

2. **Monitoring:**
   - Set up cost alerts
   - Track model performance metrics
   - Monitor error rates per model

3. **Optimization:**
   - Implement response caching
   - Add request batching
   - Fine-tune model selection thresholds

4. **Features:**
   - User feedback on CTC quality
   - A/B testing different models
   - Dynamic model selection based on performance

## References

- Architecture: `MULTI_AGENT_ARCHITECTURE.md`
- Main API: `/opt/apps/gandlf/api/app.py`
- Agent Client: `/opt/apps/gandlf/gandalf_agent/agent_client.py`
- Instruction Files: `/opt/apps/gandlf/ai_agent_prompts/`
- Anthropic Docs: https://docs.anthropic.com/
