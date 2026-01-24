# GANDALF API - Example Usage

This document demonstrates how to use the GANDALF API to convert user intents into Compiled Task Contracts (CTCs).

## Prerequisites

- GANDALF VM is running
- API service is active (port 5000)
- You have network access to the VM

## Example 1: Simple Intent Submission

### Request
```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add user authentication to the app"
  }'
```

### Response
```json
{
  "gandalf_version": "1.0",
  "ctc": {
    "title": "Add user authentication to the app",
    "context": [
      "User request received on 2026-01-19T10:00:00Z",
      "Target executor: claude-code"
    ],
    "definition_of_done": [
      "Implementation completed",
      "Tests passing",
      "Documentation updated"
    ],
    "constraints": [
      "Follow project coding standards",
      "Maintain backward compatibility"
    ],
    "deliverables": [
      "Source code",
      "Tests",
      "Documentation"
    ]
  },
  "clarifications": {
    "asked": [],
    "resolved_by": "default"
  },
  "telemetry": {
    "intent_id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2026-01-19T10:30:00.000000",
    "executor": {
      "name": "claude-code",
      "version": "1.0"
    },
    "elapsed_ms": 0,
    "input_tokens": null,
    "output_tokens": null,
    "user_questions_count": 0,
    "execution_result": "unknown"
  }
}
```

## Example 2: Complex User Prompt

### Request
```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T14:30:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "I need a dashboard that shows real-time metrics. It should have charts, filters, and export functionality. Make it responsive and fast."
  }'
```

### What GANDALF Does
1. Receives the unstructured user prompt
2. Extracts intent: dashboard with real-time metrics
3. Identifies key requirements: charts, filters, export, responsive, performance
4. Generates a structured CTC with clear deliverables
5. Returns JSON that can be fed to an execution agent

## Example 3: Python Client

```python
import requests
from datetime import datetime

class GANDALFClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url

    def health_check(self):
        """Check if API is healthy"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def submit_intent(self, user_prompt, generate_for="claude-code"):
        """Submit a user intent and get CTC"""
        payload = {
            "date": datetime.utcnow().isoformat() + "Z",
            "generate_for": generate_for,
            "user_prompt": user_prompt
        }

        response = requests.post(
            f"{self.base_url}/api/intent",
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API error: {response.status_code} - {response.text}")

# Usage
client = GANDALFClient()

# Check health
health = client.health_check()
print(f"API Status: {health['status']}")

# Submit intent
ctc = client.submit_intent(
    user_prompt="Create a RESTful API for managing blog posts",
    generate_for="claude-code"
)

print(f"Intent ID: {ctc['telemetry']['intent_id']}")
print(f"Task: {ctc['ctc']['title']}")
print(f"Deliverables: {', '.join(ctc['ctc']['deliverables'])}")
```

## Example 4: JavaScript/Node.js Client

```javascript
const axios = require('axios');

class GANDALFClient {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
  }

  async healthCheck() {
    const response = await axios.get(`${this.baseURL}/health`);
    return response.data;
  }

  async submitIntent(userPrompt, generateFor = 'claude-code') {
    const payload = {
      date: new Date().toISOString(),
      generate_for: generateFor,
      user_prompt: userPrompt
    };

    const response = await axios.post(`${this.baseURL}/api/intent`, payload);
    return response.data;
  }
}

// Usage
(async () => {
  const client = new GANDALFClient();

  // Check health
  const health = await client.healthCheck();
  console.log(`API Status: ${health.status}`);

  // Submit intent
  const ctc = await client.submitIntent(
    'Add payment processing with Stripe integration'
  );

  console.log(`Intent ID: ${ctc.telemetry.intent_id}`);
  console.log(`Task: ${ctc.ctc.title}`);
  console.log(`Context: ${ctc.ctc.context.join(', ')}`);
})();
```

## Example 5: Using with Claude Code CLI

Once you have the CTC, you can feed it to Claude Code:

```bash
# Get CTC from GANDALF
CTC=$(curl -s -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Add user authentication"
  }' | jq -r '.ctc | "# Task: \(.title)\n\n## Context\n\(.context | map("- " + .) | join("\n"))\n\n## Definition of Done\n\(.definition_of_done | map("- [ ] " + .) | join("\n"))\n\n## Constraints\n\(.constraints | map("- " + .) | join("\n"))\n\n## Deliverables\n\(.deliverables | map("- " + .) | join("\n"))"')

# Pass to Claude Code
echo "$CTC" | claude-code
```

## Example 6: Error Handling

### Missing Required Fields
```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T10:00:00Z",
    "generate_for": "claude-code"
  }'
```

Response:
```json
{
  "error": "Missing required fields",
  "missing": ["user_prompt"]
}
```

### Invalid Date Format
```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "not-a-date",
    "generate_for": "claude-code",
    "user_prompt": "Test"
  }'
```

Response:
```json
{
  "error": "Invalid date format. Use ISO-8601 format"
}
```

## Example 7: Batch Processing

Process multiple intents:

```python
import requests
from datetime import datetime

intents = [
    "Add user authentication",
    "Create admin dashboard",
    "Implement email notifications",
    "Add payment processing"
]

base_url = "http://localhost:5000"

for intent in intents:
    payload = {
        "date": datetime.utcnow().isoformat() + "Z",
        "generate_for": "claude-code",
        "user_prompt": intent
    }

    response = requests.post(f"{base_url}/api/intent", json=payload)

    if response.status_code == 200:
        ctc = response.json()
        print(f"✓ Processed: {ctc['ctc']['title']}")
        print(f"  Intent ID: {ctc['telemetry']['intent_id']}")
    else:
        print(f"✗ Failed: {intent}")
```

## Testing the API

### Quick Health Check
```bash
curl http://localhost:5000/health
```

### Run Test Suite
```bash
cd /opt/apps/gandlf
source venv/bin/activate
python scripts/test_api.py
```

## Integration Patterns

### 1. CLI Wrapper
```bash
#!/bin/bash
# gandalf-submit.sh
USER_PROMPT="$1"

curl -s -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d "{
    \"date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"generate_for\": \"claude-code\",
    \"user_prompt\": \"$USER_PROMPT\"
  }" | jq '.'
```

Usage:
```bash
./gandalf-submit.sh "Add user authentication to the app"
```

### 2. CI/CD Integration
```yaml
# .github/workflows/gandalf.yml
name: Generate CTC
on: [push]
jobs:
  generate-ctc:
    runs-on: ubuntu-latest
    steps:
      - name: Generate CTC from commit message
        run: |
          curl -X POST http://gandalf-server:5000/api/intent \
            -H "Content-Type: application/json" \
            -d "{
              \"date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
              \"generate_for\": \"github-actions\",
              \"user_prompt\": \"${{ github.event.head_commit.message }}\"
            }"
```

## Next Steps

1. Review the generated CTC
2. Validate it meets your requirements
3. Pass to execution agent (Claude Code, etc.)
4. Monitor execution through telemetry
5. Store results in database for analysis

## Troubleshooting

### API Not Responding
```bash
# Check if service is running
sudo systemctl status gandalf-api

# Check logs
sudo journalctl -u gandalf-api -n 50

# Restart service
sudo systemctl restart gandalf-api
```

### Connection Refused
- Verify VM is running: `multipass list`
- Check firewall rules
- Verify port 5000 is open
- Check API is bound to correct interface

### Invalid Response
- Check request format matches examples
- Verify Content-Type is application/json
- Ensure date is ISO-8601 format
- Check API logs for errors

## References

- API Documentation: `/opt/apps/gandlf/api/README.md`
- Project Map: `/opt/apps/gandlf/PROJECT_MAP.md`
- Technologies: `/opt/apps/gandlf/TECHNOLOGIES.md`
