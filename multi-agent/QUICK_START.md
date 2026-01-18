# Multi-Agent System Quick Start

**5-Minute Setup Guide for GANDALF Multi-Agent System**

## Prerequisites

- Python 3.x installed
- Anthropic API key ([Get one here](https://console.anthropic.com))

## Setup (2 minutes)

### 1. Configure Environment

```bash
cd /opt/apps/gandlf/multi-agent

# Copy example env file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or vim, or any editor
```

Add this line:
```
ANTHROPIC_API_KEY=your-actual-api-key-here
```

### 2. Install Dependencies

```bash
cd /opt/apps/gandlf
pip install -r requirements.txt
```

## Start System (1 minute)

### Terminal 1: Start AI Agent Service

```bash
cd /opt/apps/gandlf/multi-agent
./start_ai_agent.sh
```

Wait for: "Running on http://0.0.0.0:8080"

### Terminal 2: Start Flask API

```bash
cd /opt/apps/gandlf
python -m api.app
```

Wait for: "Running on http://127.0.0.1:5000"

## Test System (2 minutes)

### 1. Check Health

```bash
# AI Agent Service
curl http://localhost:8080/health

# Flask API
curl http://localhost:5000/health
```

### 2. Test Model Router

```bash
python3 multi-agent/test_multi_agent.py
```

Expected: ✅ ALL TESTS PASSED

### 3. Submit Test Intent

```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T12:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add a logout button"
  }'
```

Expected: JSON response with CTC or clarification questions

### 4. Check Telemetry

```bash
curl http://localhost:8080/telemetry
```

Expected: Usage statistics showing which models were used

## Common Commands

### View Available Models

```bash
curl http://localhost:8080/models
```

### View Agent Status

```bash
curl http://localhost:5000/api/agent/status
```

### Reset Telemetry

```bash
curl -X POST http://localhost:8080/telemetry/reset
```

## Configuration Options

Edit `.env` file to customize:

```bash
# Disable expensive Opus model (saves costs)
GANDALF_ENABLE_OPUS=false

# Force all tasks to use Haiku (fastest, cheapest)
GANDALF_FORCE_MODEL=haiku

# Force all tasks to use Opus (highest quality)
GANDALF_FORCE_MODEL=opus

# Change default model
GANDALF_DEFAULT_MODEL=sonnet
```

After changing `.env`, restart the AI Agent Service.

## Troubleshooting

### "Cannot connect to AI Agent"
- Check if service is running: `curl http://localhost:8080/health`
- Check logs in Terminal 1

### "ANTHROPIC_API_KEY not set"
- Edit `.env` file and add your API key
- Restart AI Agent Service

### "Port already in use"
- Kill existing process: `lsof -ti:8080 | xargs kill`
- Or change port in `.env`: `GANDALF_AGENT_PORT=8081`

### Tests fail
- Check dependencies: `pip install -r requirements.txt`
- Check Python version: `python3 --version` (should be 3.8+)

## What Each Model Does

| Task | Model | Why |
|------|-------|-----|
| Classify intent | Haiku | Fast classification |
| Extract keywords | Haiku | Simple extraction |
| Score clarity | Sonnet | Nuanced analysis |
| Detect gaps | Sonnet | Context understanding |
| Generate questions | Sonnet | Good formulation |
| **Generate CTC** | **Opus** | **Complex reasoning** |
| Validate format | Haiku | Schema checking |

## Cost Comparison

**Example: "Add user authentication"**

| Approach | Cost per Intent | Speed |
|----------|-----------------|-------|
| All Sonnet | $0.22 | Medium |
| **Multi-Agent** | **$0.18** | Fast for simple, slow for complex |
| All Haiku | $0.05 | Fast but lower quality |
| All Opus | $0.45 | Slow but highest quality |

**Savings: 15-40%** depending on intent complexity

## Next Steps

1. Read full documentation: `multi-agent/README.md`
2. Review architecture: `multi-agent/MULTI_AGENT_ARCHITECTURE.md`
3. Set up systemd service for production (see README)
4. Configure monitoring and alerts

## Quick Reference

```bash
# Start everything
cd /opt/apps/gandlf/multi-agent && ./start_ai_agent.sh &
cd /opt/apps/gandlf && python -m api.app &

# Stop everything
pkill -f ai_agent_service
pkill -f "api.app"

# View logs
tail -f /var/log/gandalf/ai-agent-error.log

# Test system
python3 multi-agent/test_multi_agent.py
curl http://localhost:5000/health
```

## Support

- Full README: `/opt/apps/gandlf/multi-agent/README.md`
- Architecture: `/opt/apps/gandlf/multi-agent/MULTI_AGENT_ARCHITECTURE.md`
- Project Map: `/opt/apps/gandlf/PROJECT_MAP.md`
- Completion Summary: `/opt/apps/gandlf/GANDLF-0005_COMPLETION_SUMMARY.md`

---

**You're ready to go!** 🚀

The system will automatically select the best model for each task and optimize costs.
