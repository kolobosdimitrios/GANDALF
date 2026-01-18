# Multi-Agent Architecture

**Last Updated:** 2026-01-19
**Ticket:** GANDLF-0005

## Overview

The GANDALF system uses multiple Claude models (Haiku, Sonnet, Opus) for different roles to optimize cost and performance. Each model is assigned tasks based on its strengths and cost-effectiveness.

## Model Selection Strategy

### Model Characteristics

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| **Claude Haiku** | Fastest | Lowest | Simple classification, validation, formatting |
| **Claude Sonnet** | Balanced | Medium | Analysis, gap detection, question generation |
| **Claude Opus** | Powerful | Highest | Complex CTC generation, reasoning, synthesis |

### Task-to-Model Mapping

```
┌─────────────────────────────────────────────┐
│ GANDALF Workflow                            │
├─────────────────────────────────────────────┤
│                                             │
│  1. Intent Analysis                         │
│     ├─ Classify intent type → HAIKU        │
│     ├─ Extract keywords → HAIKU            │
│     └─ Clarity scoring → SONNET            │
│                                             │
│  2. Gap Detection                           │
│     ├─ Identify missing info → SONNET      │
│     ├─ Generate questions → SONNET         │
│     └─ Prioritize questions → HAIKU        │
│                                             │
│  3. CTC Generation                          │
│     ├─ Generate CTC structure → OPUS       │
│     ├─ Expand deliverables → OPUS          │
│     ├─ Format validation → HAIKU           │
│     └─ Efficiency calculation → HAIKU      │
│                                             │
└─────────────────────────────────────────────┘
```

## Architecture Components

### 1. Model Router (`model_router.py`)

**Purpose:** Determines which model to use for each task

**Logic:**
- Simple classification/formatting → Haiku
- Analysis/question generation → Sonnet
- Complex reasoning/generation → Opus

**Key Methods:**
- `select_model(task_type: str) -> str`: Returns model name
- `get_model_config(model: str) -> dict`: Returns model parameters

### 2. Multi-Agent Client (`multi_agent_client.py`)

**Purpose:** Manages communication with multiple Claude models

**Key Features:**
- Supports all three Claude models
- Routes tasks to appropriate model
- Handles fallback if primary model unavailable
- Tracks token usage per model

**Key Methods:**
- `analyze_intent(user_intent: str) -> dict`: Uses Haiku + Sonnet
- `detect_gaps(intent_analysis: dict) -> dict`: Uses Sonnet
- `generate_ctc(all_context: dict) -> dict`: Uses Opus + Haiku (validation)

### 3. AI Agent Service (`ai_agent_service.py`)

**Purpose:** HTTP service that processes requests with appropriate model

**Endpoints:**
- `POST /agent` - Main endpoint, accepts model preference
- `GET /health` - Health check
- `GET /models` - List available models

**Request Format:**
```json
{
  "role": "AGENT_ROLE.md content",
  "instructions": "instruction file content",
  "task": "intent_analysis|gap_detection|ctc_generation",
  "model": "haiku|sonnet|opus",  // optional, router decides if not provided
  "payload": { ... }
}
```

## Cost Optimization Strategy

### Token Usage Estimates

**Intent Analysis:**
- Classification (Haiku): ~500 tokens
- Clarity scoring (Sonnet): ~800 tokens
- **Total:** ~1,300 tokens

**Gap Detection:**
- Gap identification (Sonnet): ~1,200 tokens
- Question generation (Sonnet): ~1,000 tokens
- **Total:** ~2,200 tokens

**CTC Generation:**
- Main generation (Opus): ~3,000 tokens
- Validation (Haiku): ~500 tokens
- **Total:** ~3,500 tokens

### Cost Comparison

**Before (All Sonnet):**
- Intent: 1,300 tokens × Sonnet rate
- Gap: 2,200 tokens × Sonnet rate
- CTC: 3,500 tokens × Sonnet rate
- **Total:** ~7,000 tokens at Sonnet pricing

**After (Multi-Agent):**
- Intent: 500 × Haiku + 800 × Sonnet
- Gap: 2,200 × Sonnet
- CTC: 3,000 × Opus + 500 × Haiku
- **Estimated Savings:** 30-40% for simple intents, 10-20% for complex intents

## Implementation Details

### Model Router Logic

```python
def select_model(task_type: str, complexity: str = 'medium') -> str:
    """
    Select appropriate model based on task type and complexity.

    Args:
        task_type: Type of task (classify, analyze, generate, validate)
        complexity: Task complexity (low, medium, high)

    Returns:
        Model name (haiku, sonnet, opus)
    """
    if task_type == 'classify' or task_type == 'validate':
        return 'haiku'  # Fast classification/validation

    if task_type == 'analyze' or task_type == 'detect_gaps':
        return 'sonnet'  # Balanced analysis

    if task_type == 'generate_ctc':
        return 'opus' if complexity == 'high' else 'sonnet'

    return 'sonnet'  # Default to balanced option
```

### Multi-Step Workflow Example

**User Intent:** "Add user authentication"

**Step 1: Intent Analysis**
1. **Haiku** classifies intent → "software_feature"
2. **Haiku** extracts keywords → ["authentication", "user", "security"]
3. **Sonnet** scores clarity → 3/5 (needs details)

**Step 2: Gap Detection**
1. **Sonnet** identifies gaps → [auth_method, session_management, password_policy]
2. **Sonnet** generates questions → 3 structured questions
3. **Haiku** prioritizes questions → marks 2 as blocking

**Step 3: User Clarifies**
User answers questions with clarifications

**Step 4: CTC Generation**
1. **Opus** generates complete CTC → Full structure with all sections
2. **Haiku** validates format → Checks JSON schema compliance
3. **Haiku** calculates efficiency → Compression ratio, token counts

## Fallback Strategy

If primary model unavailable:
1. **Haiku fallback:** Use Sonnet
2. **Sonnet fallback:** Use Opus (if critical) or Haiku (if non-critical)
3. **Opus fallback:** Use Sonnet + post-processing

## Configuration

### Environment Variables

```bash
# Model API Keys
ANTHROPIC_API_KEY=your-api-key-here

# Model Selection
GANDALF_DEFAULT_MODEL=sonnet          # Default if router doesn't decide
GANDALF_ENABLE_HAIKU=true            # Enable Haiku for fast tasks
GANDALF_ENABLE_OPUS=true             # Enable Opus for complex tasks
GANDALF_FORCE_MODEL=                 # Force all tasks to one model (testing)

# Cost Controls
GANDALF_MAX_TOKENS_HAIKU=2000
GANDALF_MAX_TOKENS_SONNET=4000
GANDALF_MAX_TOKENS_OPUS=8000
GANDALF_DAILY_BUDGET_USD=50.00

# Performance
GANDALF_TIMEOUT_HAIKU=10             # seconds
GANDALF_TIMEOUT_SONNET=30            # seconds
GANDALF_TIMEOUT_OPUS=60              # seconds
```

## Telemetry

Track per model:
- Request count
- Token usage (input/output)
- Cost (estimated)
- Latency (response time)
- Error rate

**Metrics JSON:**
```json
{
  "model_usage": {
    "haiku": {
      "requests": 2,
      "input_tokens": 450,
      "output_tokens": 550,
      "cost_usd": 0.0003,
      "avg_latency_ms": 245
    },
    "sonnet": {
      "requests": 2,
      "input_tokens": 1800,
      "output_tokens": 1400,
      "cost_usd": 0.018,
      "avg_latency_ms": 1340
    },
    "opus": {
      "requests": 1,
      "input_tokens": 2400,
      "output_tokens": 3600,
      "cost_usd": 0.243,
      "avg_latency_ms": 4820
    }
  },
  "total_cost_usd": 0.2613,
  "total_requests": 5,
  "workflow_duration_ms": 6890
}
```

## Benefits

1. **Cost Reduction:** 30-40% savings on simple intents
2. **Performance:** Faster response for classification/validation
3. **Quality:** Opus for complex CTC generation ensures high quality
4. **Scalability:** Can handle more requests within same budget
5. **Flexibility:** Easy to adjust model selection strategy

## Testing Strategy

1. **Unit Tests:** Test model router logic with various task types
2. **Integration Tests:** Test full workflow with all three models
3. **Cost Tests:** Validate actual cost savings vs single-model approach
4. **Performance Tests:** Measure latency improvements for simple tasks
5. **Quality Tests:** Ensure CTC quality doesn't degrade with Haiku/Sonnet

## Migration Path

**Phase 1:** Implement multi-agent infrastructure
- Build model router
- Create multi-agent client
- Update AI agent service

**Phase 2:** Enable Haiku for simple tasks
- Intent classification
- Format validation
- Keyword extraction

**Phase 3:** Enable Opus for complex generation
- CTC generation
- Complex reasoning
- Multi-step synthesis

**Phase 4:** Optimize and tune
- Adjust model selection thresholds
- Monitor cost/quality metrics
- Fine-tune prompt strategies per model

## Future Enhancements

1. **Dynamic Model Selection:** Use ML to learn optimal model selection
2. **Cost Budgeting:** Enforce daily/monthly cost limits
3. **Quality Feedback Loop:** Track CTC acceptance rate per model
4. **Caching:** Cache Haiku classifications to reduce duplicate requests
5. **Batch Processing:** Group similar tasks for efficiency
