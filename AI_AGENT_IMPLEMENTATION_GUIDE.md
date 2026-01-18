# AI Agent Implementation Guide

## Overview

The GANDALF CTC generation system delegates all intent analysis, gap detection, and CTC generation to an AI agent running inside the GANDALF VM. This document explains how to implement and integrate the AI agent service.

## Architecture

```
User Request
    ↓
Flask API (/api/intent)
    ↓
CTCOrchestrator
    ↓
AgentClient
    ↓
HTTP Request → AI Agent VM Service
    ↓
AI Agent (reads instruction files)
    ↓
Returns JSON Response
    ↓
Back to User
```

## Components

### 1. Instruction Files (ai_agent_prompts/)

These files contain the instructions the AI agent reads to perform its tasks:

- **AGENT_ROLE.md** - Defines the agent's mission and operating principles
- **01_INTENT_ANALYSIS.md** - Instructions for analyzing user intents
- **02_GAP_DETECTION.md** - Instructions for detecting information gaps
- **03_CTC_GENERATION.md** - Instructions for generating complete CTCs

The agent reads these files to understand what to do with each request.

### 2. Agent Client (gandalf_agent/agent_client.py)

Python service that:
- Loads instruction files
- Formats requests for the AI agent
- Sends HTTP requests to the agent endpoint
- Parses and validates responses

**Key Methods:**
- `analyze_intent(user_intent)` - Send intent for analysis
- `detect_gaps(user_intent, intent_analysis)` - Send for gap detection
- `generate_ctc(...)` - Send for CTC generation

### 3. CTC Orchestrator (gandalf_agent/ctc_orchestrator.py)

Orchestrates the multi-step workflow:
1. Analyze intent via AI agent
2. Detect gaps via AI agent
3. If gaps: return clarification questions
4. If no gaps: generate CTC via AI agent

### 4. Flask API (api/app.py)

REST endpoints:
- `POST /api/intent` - Submit user intent
- `POST /api/intent/clarify` - Submit clarification answers
- `GET /api/agent/status` - Check agent availability

## Implementation Steps

### Step 1: Set Up AI Agent VM Service

You need to implement a service inside the GANDALF VM that:

1. **Listens for HTTP requests** (e.g., on port 8080)
2. **Receives requests** in this format:

```json
{
  "role": "content of AGENT_ROLE.md",
  "instructions": "content of 01_INTENT_ANALYSIS.md (or 02, 03)",
  "task": "intent_analysis|gap_detection|ctc_generation",
  "payload": {
    "user_intent": "Add a logout button",
    "intent_analysis": { ... },  // for gap_detection and ctc_generation
    "gap_detection": { ... },    // for ctc_generation only
    "clarifications": { ... }    // for ctc_generation only (optional)
  }
}
```

3. **Processes the request** by:
   - Reading the role and instructions
   - Understanding the task to perform
   - Analyzing the payload
   - Generating appropriate response

4. **Returns JSON response** following the exact schema in the instruction file

### Step 2: Implement Agent Service (Example)

Here's a conceptual example using Python + Flask:

```python
# ai_agent_service.py (runs inside GANDALF VM)
from flask import Flask, request, jsonify
import anthropic  # or any LLM provider

app = Flask(__name__)
client = anthropic.Anthropic(api_key="your-key")

@app.route('/agent', methods=['POST'])
def process_request():
    data = request.json

    # Extract components
    role = data['role']
    instructions = data['instructions']
    task = data['task']
    payload = data['payload']

    # Build prompt for AI
    prompt = f"""
{role}

{instructions}

Now perform the task with this input:
{json.dumps(payload, indent=2)}

Return ONLY valid JSON following the schema in the instructions.
"""

    # Call AI model
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    # Parse JSON response
    result = json.loads(response.content[0].text)

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Step 3: Configure Agent Endpoint

Set the environment variable to point to your AI agent:

```bash
export GANDALF_AGENT_ENDPOINT="http://localhost:8080/agent"
```

Or modify `agent_client.py`:

```python
self.agent_endpoint = "http://your-vm-ip:8080/agent"
```

### Step 4: Complete the AgentClient Implementation

In `gandalf_agent/agent_client.py`, uncomment and implement the HTTP request:

```python
def _send_to_agent(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    # ... existing code ...

    import requests

    response = requests.post(
        self.agent_endpoint,
        json=agent_request,
        timeout=30
    )
    response.raise_for_status()
    return response.json()
```

### Step 5: Test the Integration

1. **Start the AI agent service** in the VM:
   ```bash
   python ai_agent_service.py
   ```

2. **Start the Flask API**:
   ```bash
   cd /opt/apps/gandlf
   python -m api.app
   ```

3. **Test with curl**:
   ```bash
   curl -X POST http://localhost:5000/api/intent \
     -H "Content-Type: application/json" \
     -d '{
       "date": "2024-01-19T12:00:00Z",
       "generate_for": "AI-AGENT",
       "user_prompt": "Add a logout button to the navigation bar"
     }'
   ```

## Request/Response Examples

### Example 1: Clear Intent → CTC Generated

**Request:**
```json
{
  "date": "2024-01-19T12:00:00Z",
  "generate_for": "AI-AGENT",
  "user_prompt": "Add a logout button to the top navigation bar"
}
```

**Response:**
```json
{
  "intent_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "ctc": {
    "title": "Add Logout Button to Navigation Bar",
    "context": "Users need a clear way to log out...",
    "definition_of_done": [
      "Logout button visible in navigation",
      "Clicking button clears session",
      "User redirected to login page"
    ],
    "constraints": ["Use existing auth system", ...],
    "deliverables": ["Modified navigation component", ...],
    "implementation_hints": ["Add button to NavigationBar.js", ...]
  },
  "telemetry": {
    "intent_analysis": { "intent_type": "software_feature", ... },
    "gap_detection": { "needs_clarification": false, ... },
    "efficiency": { "compression_ratio": 7.44, ... }
  }
}
```

### Example 2: Vague Intent → Clarification Needed

**Request:**
```json
{
  "date": "2024-01-19T12:00:00Z",
  "generate_for": "AI-AGENT",
  "user_prompt": "We need better reporting"
}
```

**Response:**
```json
{
  "intent_id": "123e4567-e89b-12d3-a456-426614174001",
  "status": "needs_clarification",
  "intent_analysis": {
    "intent_type": "business_need",
    "clarity_score": 1
  },
  "clarification_questions": [
    {
      "question": "What type of data do you want to report on?",
      "why": "Determines database queries needed",
      "options": [
        {"label": "Sales & Revenue", "value": "sales", "description": "..."},
        {"label": "User Activity", "value": "user_activity", "description": "..."}
      ],
      "default": "user_activity"
    },
    {
      "question": "What format do you need?",
      "options": [...]
    }
  ]
}
```

### Example 3: Submitting Clarifications

**Request:**
```json
{
  "date": "2024-01-19T12:00:00Z",
  "generate_for": "AI-AGENT",
  "user_prompt": "We need better reporting",
  "clarifications": {
    "data_type": "user_activity",
    "format": "excel"
  }
}
```

**Response:**
```json
{
  "status": "completed",
  "ctc": { ... complete CTC with clarifications incorporated ... }
}
```

## AI Agent Requirements

The AI agent service MUST:

1. **Read and follow instructions** from the markdown files exactly
2. **Return valid JSON** matching the schema in each instruction file
3. **Handle errors gracefully** and return error responses
4. **Process requests within 30 seconds** (timeout limit)
5. **Be stateless** - each request is independent

## Testing the Agent

Use the test script to validate your AI agent implementation:

```bash
cd /opt/apps/gandlf
python scripts/test_ctc_generation.py
```

This will test against the demo and validation examples.

## Troubleshooting

### Agent Not Responding
- Check if agent service is running: `curl http://localhost:8080/agent`
- Check logs in the agent service
- Verify GANDALF_AGENT_ENDPOINT is set correctly

### Invalid JSON Response
- Agent must return ONLY JSON, no markdown code blocks
- Validate JSON schema matches instruction file
- Check for trailing commas or syntax errors

### Timeout Errors
- Agent must respond within 30 seconds
- Optimize AI model inference
- Consider caching for common patterns

### Wrong Classification
- Review instruction files for clarity
- Check examples in instruction files
- Verify agent is reading full instructions

## Next Steps

1. Implement the AI agent service in the GANDALF VM
2. Configure the agent endpoint
3. Test with the demo examples
4. Integrate with your frontend
5. Add database persistence for CTCs

## Files Modified

- `/opt/apps/gandlf/ai_agent_prompts/` - Instruction files
- `/opt/apps/gandlf/gandalf_agent/` - Agent client and orchestrator
- `/opt/apps/gandlf/api/app.py` - Flask API integration

## Configuration

Environment variables:
- `GANDALF_AGENT_ENDPOINT` - URL of the AI agent service (default: http://localhost:8080/agent)
- `FLASK_PORT` - Port for Flask API (default: 5000)
- `FLASK_DEBUG` - Enable debug mode (default: False)
