# Multi-Agent API Integration Test Guide

## Quick Start

### Prerequisites
- Pipeline agent service running on `http://localhost:8080`
- API service running on `http://localhost:5000`
- Python 3.12+
- Dependencies installed

### Start Services

```bash
# Terminal 1: Start pipeline agent service
cd /var/www/projects/gandlf/multi-agent
python3 pipeline_agent_service.py

# Terminal 2: Start API service
cd /var/www/projects/gandlf
python3 -m api.app
```

## Test Cases

### 1. Health Check
Verify API and pipeline services are running.

```bash
# API health
curl -s http://localhost:5000/health | jq .

# Pipeline agent health
curl -s http://localhost:8080/health | jq .
```

**Expected:** Both return `"status": "healthy"`

### 2. Intent Submission - Simple Request

```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-24T21:18:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "Create a simple Hello World web application"
  }' | jq .
```

**Expected:** Response with `"status": "completed"` and generated CTC

### 3. Intent Submission - Complex Request (May Need Clarification)

```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-24T21:18:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "Build a payment processing system"
  }' | jq .
```

**Expected:** Might return `"status": "needs_clarification"` with clarification questions

### 4. Submit Clarifications

If the previous request returned clarification questions, use those question IDs:

```bash
curl -X POST http://localhost:5000/api/intent/clarify \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-24T21:18:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "Build a payment processing system",
    "clarifications": {
      "q1": "Stripe and PayPal",
      "q2": "Python with FastAPI",
      "q3": "PostgreSQL"
    }
  }' | jq .
```

**Expected:** Response with `"status": "completed"` and complete CTC

### 5. Agent Status

```bash
curl -s http://localhost:5000/api/agent/status | jq .
```

**Expected:** Status should show all components ready

## Validation Checklist

- [ ] API health check returns "healthy"
- [ ] Pipeline service health check returns "healthy"
- [ ] Simple intent returns completed CTC
- [ ] Complex intent returns clarification questions or CTC
- [ ] Clarification submission returns completed CTC
- [ ] Agent status endpoint shows all ready
- [ ] Telemetry data is present in responses
- [ ] No error messages in logs

## Troubleshooting

### Pipeline Service Not Responding

```bash
# Check if service is running
ps aux | grep pipeline_agent_service

# Check port 8080 is listening
netstat -tulpn | grep 8080

# Test connectivity
curl -v http://localhost:8080/health
```

### Import Errors

```bash
# Verify MultiAgentClient imports
cd /var/www/projects/gandlf
python3 -c "from api.multi_agent_client import MultiAgentClient; print('OK')"

# Verify app imports
python3 -c "from api.app import app; print('OK')"
```

### API Not Starting

```bash
# Check syntax
python3 -m py_compile api/app.py

# Check dependencies
python3 -c "import flask; import flask_cors; print('OK')"
```

## Performance Baseline

Typical response times:
- Simple intent (lexical only): 500-1000ms
- Complex intent with clarifications: 1000-2000ms
- Clarification submission: 1000-2000ms
- Final CTC generation: 2000-5000ms

## Error Response Examples

### Missing Fields
```json
{
  "error": "Missing required fields",
  "missing": ["date", "generate_for"]
}
```

### Invalid Date Format
```json
{
  "error": "Invalid date format. Use ISO-8601 format"
}
```

### Service Unavailable
```json
{
  "error": "Internal server error",
  "message": "Pipeline service unavailable"
}
```

## Telemetry Analysis

Check the telemetry in responses:

```bash
curl -s http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-24T21:18:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "Test message"
  }' | jq '.telemetry'
```

Key metrics:
- `elapsed_ms`: Total processing time
- `efficiency_percentage`: CTC compression ratio
- `user_chars` / `ctc_chars`: Character counts
