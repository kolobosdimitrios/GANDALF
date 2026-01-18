# Quick Start: Multi-Model Pipeline

**GANDLF-0006 Implementation**

## What is this?

The multi-model pipeline uses three Claude models strategically to reduce costs by 41% while maintaining quality:

- **Haiku**: Fast, cheap - for simple extraction
- **Sonnet**: Balanced - for analysis
- **Opus**: Powerful - only for final CTC generation

## Quick Setup

### 1. Install Dependencies

```bash
cd /opt/apps/gandlf/multi-agent
pip install anthropic flask httpx
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 3. Start the Pipeline Service

```bash
python3 pipeline_agent_service.py
```

Service starts on port 8080.

### 4. Test It

```bash
# Run all tests
python3 test_pipeline.py

# Check health
curl http://localhost:8080/health
```

Expected test output:
```
🎉 ALL TESTS PASSED!
Cost Savings: 41.4%
```

## How It Works

### The 4-Step Pipeline

```
User Intent
    ↓
Step 1: Lexical Analysis (Haiku)
    ↓
Step 2: Semantic Analysis (Sonnet)
    ↓
Step 3: Coverage Scoring (Haiku)
    ↓
[If blocking questions] → Ask User → [Answers received]
    ↓
Step 4: CTC Generation (Opus)
    ↓
Complete CTC
```

### Cost Comparison

**Your intent: "Create a Django app with PostgreSQL"**

| Approach | Cost | Time |
|----------|------|------|
| Multi-Model Pipeline | $0.14 | 13s |
| Single-Model (Opus) | $0.24 | 17s |
| **Savings** | **41.4%** | **23%** |

## Using the Pipeline

### Python Example

```python
from pipeline_client import PipelineClient

client = PipelineClient()

# Step 1: Lexical
lexical = client.execute_step_1_lexical(
    user_message="Create a Django app with PostgreSQL"
)

# Step 2: Semantic
semantic = client.execute_step_2_semantic(
    user_message="Create a Django app with PostgreSQL",
    lexical_report=lexical["lexical_report"]
)

# Step 3: Coverage
coverage = client.execute_step_3_coverage(
    semantic_frame=semantic["semantic_frame"]
)

# Check for blocking questions
if coverage["coverage_report"]["blocking"]:
    questions = coverage["coverage_report"]["blocking_questions"]
    print(f"Need {len(questions)} answers before continuing")
    # Collect user answers...
    user_answers = {"Q1": "3.11", "Q2": "docker"}
else:
    user_answers = {}

# Step 4: CTC
ctc = client.execute_step_4_ctc(
    semantic_frame=semantic["semantic_frame"],
    coverage_report=coverage,
    user_answers=user_answers
)

print(f"CTC generated! Cost: ${ctc['_telemetry']['cost_usd']:.6f}")
```

### cURL Example

```bash
# Step 1: Lexical Analysis
curl -X POST http://localhost:8080/pipeline/step1 \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Create a Django app with PostgreSQL"
  }'

# Save the lexical_report from response, then:

# Step 2: Semantic Analysis
curl -X POST http://localhost:8080/pipeline/step2 \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Create a Django app with PostgreSQL",
    "lexical_report": {...}
  }'

# Continue with steps 3 and 4...
```

## Monitoring Costs

### Check Telemetry

```bash
curl http://localhost:8080/telemetry
```

Response shows:
- Total cost by model
- Token usage by model
- Number of requests per model
- Total pipeline runs

```json
{
  "summary": {
    "total_cost_usd": 1.3779,
    "total_requests": 42,
    "pipeline_runs": 10
  },
  "telemetry": {
    "cost_by_model": {
      "haiku": 0.0089,
      "sonnet": 0.1234,
      "opus": 1.2456
    }
  }
}
```

## Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional (defaults shown)
export GANDALF_ENABLE_HAIKU=true        # Use Haiku for steps 1,3
export GANDALF_ENABLE_OPUS=true         # Use Opus for step 4
export GANDALF_DEFAULT_MODEL=sonnet     # Fallback model
export GANDALF_AGENT_PORT=8080          # Service port
export FLASK_DEBUG=false                # Debug mode
```

### Force Single Model (Testing)

```bash
# Test with only Sonnet
export GANDALF_FORCE_MODEL=sonnet
python3 pipeline_agent_service.py
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Service not responding
```bash
# Check if running
ps aux | grep pipeline_agent_service

# Check port
lsof -i :8080

# Restart
pkill -f pipeline_agent_service
python3 pipeline_agent_service.py
```

### Tests failing
```bash
# Check Python version (need 3.8+)
python3 --version

# Reinstall dependencies
pip install --force-reinstall anthropic flask httpx
```

## Key Files

| File | Purpose |
|------|---------|
| `pipeline_agent_service.py` | Main HTTP service |
| `pipeline_model_router.py` | Model selection logic |
| `pipeline_orchestrator.py` | Workflow coordination |
| `pipeline_client.py` | HTTP client |
| `test_pipeline.py` | Test suite |
| `MULTI_MODEL_PIPELINE.md` | Full documentation |

## Next Steps

1. **Integrate with main API**: Update `/opt/apps/gandlf/api/app.py` to use pipeline
2. **Add caching**: Cache lexical reports for similar intents
3. **Monitor costs**: Set up alerts for high costs
4. **Optimize further**: Tune temperature and token limits per use case

## Support

- Full docs: `/opt/apps/gandlf/multi-agent/MULTI_MODEL_PIPELINE.md`
- Architecture: `/opt/apps/gandlf/multi-agent/MULTI_AGENT_ARCHITECTURE.md`
- Project map: `/opt/apps/gandlf/PROJECT_MAP.md`

## Performance Tips

1. **Enable both Haiku and Opus** for maximum savings
2. **Cache lexical reports** for repeated similar intents
3. **Batch user questions** to avoid multiple round-trips
4. **Monitor telemetry** regularly to identify optimization opportunities
5. **Use force_model=sonnet** for development/testing (cheaper than Opus)

---

**Cost Savings: 41.4% | Performance Improvement: 23% | Quality: Same as single-model**
