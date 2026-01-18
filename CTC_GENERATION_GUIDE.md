# GANDALF CTC Generation Guide

Quick reference for using the GANDALF CTC generation system.

## Quick Start

### 1. Start the API Server
```bash
cd /opt/apps/gandlf
python3 -m api.app
```

### 2. Submit a User Intent
```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-19T10:00:00Z",
    "generate_for": "claude-code",
    "user_prompt": "Your task description here"
  }'
```

## Response Types

### Type 1: CTC Generated (Clear Intent)
When the user intent is clear enough, you get a complete CTC:

```json
{
  "gandalf_version": "1.0",
  "ctc": {
    "title": "Add FAQ section to landing page",
    "context": [
      "Landing page exists and needs an FAQ section"
    ],
    "definition_of_done": [
      "Landing page includes an FAQ section with at least 3 Q&A items",
      "FAQ section is placed below the main content",
      "The new section renders correctly with existing styles"
    ],
    "constraints": [
      "Do not change other sections of the page"
    ],
    "deliverables": [
      "Updated landing page file(s)"
    ]
  },
  "clarifications": {
    "asked": [],
    "resolved_by": "default"
  },
  "telemetry": {
    "intent_id": "uuid-here",
    "created_at": "2026-01-19T10:00:00.000000",
    "elapsed_ms": 15,
    "efficiency": {
      "efficiency_percentage": 0.0,
      "user_chars": 78,
      "ctc_chars": 360,
      "compression_ratio": 4.62
    }
  }
}
```

### Type 2: Clarification Needed (Vague Intent)
When the intent is too vague, you get clarification questions:

```json
{
  "gandalf_version": "1.0",
  "requires_clarification": true,
  "clarifications": {
    "asked": [
      {
        "question": "Which format should the report be exported in?",
        "options": [
          "A: CSV",
          "B: PDF",
          "C: XLSX"
        ],
        "default_option": "A"
      }
    ],
    "resolved_by": null
  },
  "telemetry": {
    "intent_id": "uuid-here",
    "user_questions_count": 1,
    "execution_result": "pending_clarification"
  }
}
```

## Understanding the CTC Structure

### Title
- **Format**: Clear verb + concrete object
- **Example**: "Add dark mode toggle"
- **Avoid**: Vague verbs (improve, optimize, handle)

### Context (Max 2 bullets)
- What exists now or what triggered the task
- Delta-only information (no background stories)
- Task-specific context

### Definition of Done (3-7 items)
- Observable, verifiable outcomes
- Must be objectively testable
- No vague terms ("clean", "robust", "proper")

### Constraints (Max 5)
- Only task-specific hard limits
- Out-of-scope items when helpful
- Implementation restrictions

### Deliverables (Max 5)
- Concrete artifacts only
- No descriptions or explanations
- Just file/output names

## Testing Your Implementation

### Run the Test Suite
```bash
cd /opt/apps/gandlf
python3 scripts/test_ctc_generation.py
```

### Test Individual Prompts
```python
from api.ctc_generator import CTCGenerator

generator = CTCGenerator()
result = generator.generate(
    user_prompt="Add user authentication to the app",
    intent_id="test-001",
    date="2026-01-19T10:00:00Z",
    generate_for="claude-code"
)

print(result['ctc']['title'])
```

## Common Patterns

### Software Features
```
Input: "Add a filter to the activity log for date ranges."
Output CTC:
  Title: "Add date range filter to activity log"
  Context: "Activity log exists and needs date range filtering"
  DoD: 3 items (inputs, filtering works, can clear)
  Deliverables: UI update, filtering logic
```

### Bug Reports
```
Input: "The login page shows a 500 error when users reset their password."
Output CTC:
  Title: "Fix 500 error on password reset"
  Context: "Password reset flow triggers a 500 error on login page"
  DoD: 3 items (error gone, can login with new password, no errors in logs)
  Deliverables: Fix to password reset handler
```

### Vague Requests (Needs Clarification)
```
Input: "Make the app faster."
Output: Clarification about which area (page load, search, upload)

Input: "Export the monthly sales report."
Output: Clarification about format (CSV, PDF, XLSX)
```

### Non-Technical Requests
```
Input: "Write a short thank-you note for new subscribers."
Output CTC:
  Title: "Draft thank-you note for new subscribers"
  Context: "New subscribers need a short thank-you note"
  DoD: 3 items (includes greeting, thanks subscriber, under 60 words)
  Constraints: "Use friendly, professional tone"
  Deliverables: "Thank-you note text"
```

## Intent Classification

The system automatically classifies intents into:

1. **SOFTWARE_FEATURE** - Adding/modifying functionality
2. **BUG_REPORT** - Fixing broken behavior
3. **BUSINESS_NEED** - High-level business goals (usually needs clarification)
4. **NON_TECHNICAL** - Content creation, documentation, non-code tasks

## Gap Detection

The system detects these types of missing information:

| Gap Type | Example | Action |
|----------|---------|--------|
| MISSING_FORMAT | "Export report" | Ask: CSV/PDF/XLSX? |
| MISSING_PLATFORM | "iOS bug sometimes" | Ask: Which iOS version? |
| MISSING_SCOPE | "Add button" | Ask: Where to add? |
| VAGUE_ACTION | "Improve performance" | Ask: Which area? |
| MISSING_TARGET | Unclear what to act on | Ask for clarification |

## Efficiency Metrics

Each response includes efficiency metrics:

```json
"efficiency": {
  "efficiency_percentage": 0.0,    // % saved (negative = expanded)
  "user_chars": 78,                 // Input character count
  "ctc_chars": 360,                 // Output character count
  "compression_ratio": 4.62         // Output/Input ratio
}
```

**Note**: Negative efficiency is expected and correct per GANDALF spec. The goal is clarity and completeness, not compression.

## Best Practices

### For Clear CTCs
✅ Be specific: "Add FAQ section to landing page"
✅ Include scope: "...to landing page"
✅ Mention constraints: "without changing header"
✅ Define success: "when daily errors exceed 2%"

### For Avoiding Clarifications
✅ Specify format: "Export as CSV"
✅ Specify location: "Add button in settings"
✅ Specify platform: "Fix on iOS 16+"
✅ Be concrete: "Add 3 Q&A items" not "Add FAQ"

### What Triggers Clarifications
❌ "Export report" → needs format
❌ "Make faster" → needs area
❌ "Better reporting" → needs type
❌ "Improve onboarding" → needs stage
❌ "Upload images" → needs formats

## API Integration

### Python
```python
import requests

response = requests.post(
    'http://localhost:5000/api/intent',
    json={
        'date': '2026-01-19T10:00:00Z',
        'generate_for': 'claude-code',
        'user_prompt': 'Your task here'
    }
)

ctc = response.json()
if ctc.get('requires_clarification'):
    # Handle clarification
    questions = ctc['clarifications']['asked']
else:
    # Use CTC
    title = ctc['ctc']['title']
```

### JavaScript
```javascript
const response = await fetch('http://localhost:5000/api/intent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    date: new Date().toISOString(),
    generate_for: 'claude-code',
    user_prompt: 'Your task here'
  })
});

const ctc = await response.json();
```

## Troubleshooting

### Issue: Getting clarifications for clear tasks
**Solution**: Make your prompt more specific. Include:
- Format (for exports/uploads)
- Location (for UI changes)
- Scope boundaries
- Success criteria

### Issue: CTC too generic
**Solution**: Provide more context in your input:
- What exists now
- What specifically needs to change
- Any constraints or requirements

### Issue: Wrong intent classification
**Solution**: Use clearer action verbs:
- "Fix" for bugs
- "Add" for new features
- "Update" for modifications
- "Create" for new content

## Module Reference

- **IntentAnalyzer** - Classifies user intent
- **GapDetector** - Finds missing information
- **ClarificationGenerator** - Creates questions
- **CTCGenerator** - Orchestrates CTC creation
- **EfficiencyCalculator** - Computes metrics

## Support

For issues or questions:
1. Check the test suite: `scripts/test_ctc_generation.py`
2. Review examples: `Gandalf_Demo_Intents_and_Outputs.md`
3. Read spec: `GANDALF.md`
4. See implementation: `IMPLEMENTATION_SUMMARY.md`

---

**Version**: 1.0
**Last Updated**: 2026-01-19
**Status**: Production Ready
