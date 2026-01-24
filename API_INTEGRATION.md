# API Integration with Multi-Agent Pipeline

## Overview

The GANDALF API has been successfully integrated with the multi-agent pipeline architecture. The API now orchestrates requests through a 4-step CTC generation pipeline instead of using the legacy single-agent approach.

## Architecture

```
API Request → MultiAgentClient → PipelineOrchestrator → Pipeline Steps
                                    ↓
                            Step 1: Lexical Analysis
                            Step 2: Semantic Analysis
                            Step 3: Coverage Scoring
                            Step 4: CTC Generation
```

## Components

### 1. **MultiAgentClient** (`api/multi_agent_client.py`)
Coordinates the multi-agent pipeline execution.

**Key Methods:**
- `process_intent(user_prompt, context)` - Process user intent through the full pipeline
- `submit_clarifications(user_prompt, clarifications)` - Submit answers to clarification questions
- `get_agent_status()` - Check pipeline service health

**Features:**
- Orchestrates all 4 pipeline steps
- Handles clarification question flow
- Manages session state for multi-turn conversations
- Returns standardized responses compatible with existing API contracts

### 2. **PipelineOrchestrator** (`multi-agent/pipeline_orchestrator.py`)
Implements the decision logic for the 4-step pipeline.

**Decision Logic:**
- Step 1 (Lexical): Always runs first if missing
- Step 2 (Semantic): Runs if semantic frame missing or user answers provided
- Step 3 (Coverage): Runs to generate blocking questions
- Step 4 (CTC): Runs when all blocking questions answered
- DONE: When CTC is complete

### 3. **PipelineClient** (`multi-agent/pipeline_client.py`)
HTTP client for communicating with the pipeline agent service.

**Methods:**
- `execute_step_1_lexical()` - Lexical analysis
- `execute_step_2_semantic()` - Semantic analysis
- `execute_step_3_coverage()` - Coverage scoring
- `execute_step_4_ctc()` - CTC generation
- `check_health()` - Health status
- `get_telemetry()` - Usage metrics

## API Endpoints

### 1. Health Check
```bash
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "gandalf-api",
  "timestamp": "2026-01-24T21:18:00"
}
```

### 2. Submit Intent
```bash
POST /api/intent
Content-Type: application/json
```

**Request:**
```json
{
  "date": "2026-01-24T21:18:00Z",
  "generate_for": "AI-AGENT",
  "user_prompt": "Build a REST API for user management"
}
```

**Response (CTC Generated):**
```json
{
  "intent_id": "uuid",
  "date": "2026-01-24T21:18:00Z",
  "generate_for": "AI-AGENT",
  "user_intent": "Build a REST API for user management",
  "status": "completed",
  "ctc": {
    "title": "...",
    "context": [...],
    "definition_of_done": [...],
    "constraints": [...],
    "deliverables": [...]
  },
  "telemetry": {
    "intent_analysis": {...},
    "gap_detection": {...},
    "efficiency": {...},
    "elapsed_ms": 5000
  }
}
```

**Response (Needs Clarification):**
```json
{
  "intent_id": "uuid",
  "date": "2026-01-24T21:18:00Z",
  "generate_for": "AI-AGENT",
  "user_intent": "Build a REST API for user management",
  "status": "needs_clarification",
  "intent_analysis": {...},
  "gap_detection": {...},
  "clarification_questions": [
    {
      "question_id": "q1",
      "question": "What database should be used?",
      "default_if_blank": "PostgreSQL",
      "answer_format": "text"
    }
  ]
}
```

### 3. Submit Clarifications
```bash
POST /api/intent/clarify
Content-Type: application/json
```

**Request:**
```json
{
  "date": "2026-01-24T21:18:00Z",
  "generate_for": "AI-AGENT",
  "user_prompt": "Build a REST API for user management",
  "clarifications": {
    "q1": "PostgreSQL",
    "q2": "JWT authentication"
  }
}
```

**Response:** Same format as Step 2 above

### 4. Agent Status
```bash
GET /api/agent/status
```

**Response:**
```json
{
  "status": "ready",
  "service": "gandalf-multi-agent-pipeline",
  "details": {
    "status": "healthy",
    "service": "GANDALF AI Agent Service",
    "models_enabled": {
      "haiku": true,
      "sonnet": true,
      "opus": true
    },
    "telemetry": {...}
  }
}
```

## Configuration

### Environment Variables

```bash
# Pipeline service endpoint (default: http://localhost:8080)
GANDALF_PIPELINE_ENDPOINT=http://localhost:8080

# Flask settings
FLASK_PORT=5000
FLASK_DEBUG=False
```

## Integration Flow

### 1. Intent Submission Flow

```
1. Client sends intent to /api/intent
2. MultiAgentClient.process_intent() called
3. PipelineOrchestrator.determine_next_action() returns RUN_STEP_1
4. Step 1 (Lexical Analysis) executes via PipelineClient
5. Loop continues with Steps 2, 3, 4...
6. Final CTC returned when complete
```

### 2. Clarification Flow

```
1. Client receives "needs_clarification" response
2. User provides answers for clarification_questions
3. Client sends clarifications to /api/intent/clarify
4. MultiAgentClient.submit_clarifications() stores answers
5. process_intent() resumes from Step 3 with user answers
6. Steps 3 and 4 complete
7. Final CTC returned
```

## Error Handling

The API handles various error scenarios:

- **No JSON**: Returns 400 with "Content-Type must be application/json"
- **Missing fields**: Returns 400 with list of missing fields
- **Invalid date format**: Returns 400 with format specification
- **Pipeline unavailable**: Returns 500 with service error details
- **JSON parse error**: Returns 400 with parsing error

## Telemetry

Each response includes telemetry data:

```json
{
  "telemetry": {
    "intent_analysis": {...},      // From Step 1
    "gap_detection": {...},        // From Step 2
    "efficiency": {                // Calculated by EfficiencyCalculator
      "efficiency_percentage": 85.5,
      "user_chars": 1024,
      "ctc_chars": 150,
      "compression_ratio": 0.15
    },
    "elapsed_ms": 5000
  }
}
```

## Testing

### Test Intent Submission

```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-24T21:18:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "Create a user authentication system"
  }'
```

### Check Service Health

```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/agent/status
```

## Files Changed

1. **api/app.py** - Updated to use MultiAgentClient
2. **api/multi_agent_client.py** - NEW: Orchestrates pipeline
3. **multi-agent/pipeline_client.py** - Updated to use requests instead of httpx

## Backwards Compatibility

The API maintains the same endpoint contracts as before:
- Same `/api/intent` endpoint
- Same `/api/intent/clarify` endpoint
- Same response format
- Same error handling

Existing clients can use the new API without modification.

## Next Steps

1. Start the pipeline agent service: `python3 multi-agent/pipeline_agent_service.py`
2. Start the API: `python3 -m api.app`
3. Test endpoints with provided examples above
4. Monitor logs for any issues
