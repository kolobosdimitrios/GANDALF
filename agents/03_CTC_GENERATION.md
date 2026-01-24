# STEP 3: CTC Generation

## Goal
Generate a deterministic Compiled Task Contract (CTC) ready for execution without additional clarification.

---

## Input Requirements
The CTC generator requires:
- **semantic_frame** (from STEP 1)
- **coverage_report** (from STEP 2)
- **user_answers** (if clarifications were asked)
- **compiled_output_schema** (from context - REQUIRED)
- **context** with project constraints (optional)

---

## Output Schema

The CTC MUST match the compiled_output_schema exactly:

```json
{
  "gandalf_version": "1.0",
  "ctc": {
    "title": "...",
    "context": ["..."],
    "definition_of_done": ["...", "..."],
    "constraints": ["..."],
    "deliverables": ["..."]
  },
  "clarifications": {
    "asked": [
      {
        "question": "...",
        "options": ["A: ...", "B: ...", "C: ..."],
        "default_option": "A"
      }
    ],
    "resolved_by": "user|default"
  },
  "telemetry": {
    "intent_id": "uuid",
    "created_at": "ISO-8601",
    "executor": { "name": "claude-code", "version": "..." },
    "elapsed_ms": 0,
    "input_tokens": null,
    "output_tokens": null,
    "user_questions_count": 0,
    "execution_result": "unknown"
  }
}
```

---

## CTC Section Rules

### Title
- **Format**: Clear verb + concrete object
- **Example**: "Add dark mode toggle"
- **Avoid**: Vague verbs (improve, optimize, handle)
- **Length**: One concise sentence

### Context (Maximum 2 bullets)
- What exists now or what triggered the task
- Delta-only information (no background stories)
- Only task-specific context needed for understanding

### Definition of Done (3-7 checkboxes)
- Observable, verifiable outcomes
- Must be objectively testable
- No vague terms ("clean", "robust", "proper")
- Each item must be checkable

### Constraints (Maximum 5 bullets)
- Only task-specific hard limits or exclusions
- Out-of-scope items when helpful for scope clarity
- Implementation restrictions that affect solution path

### Deliverables (Maximum 5 bullets)
- Concrete artifacts only (files, code, tests, docs)
- No descriptions or explanations
- Just names/paths

---

## Determinism Rules
- Use exact filenames and paths (no variables)
- Include explicit non-goals to prevent scope creep
- Include idempotency requirements as acceptance criteria
- Include verification commands/checks as acceptance criteria
- Single explicit Claude Code CLI prompt artifact inside CTC

---

## Safety Rules
- Do NOT include secrets in CTC content
- Define WHERE they are generated/stored instead
- Do NOT expose services publicly unless explicitly specified
- Include security constraints from semantic_frame

---

## Generation Algorithm

1. **Extract from semantic_frame**
   - goal → title
   - in_scope → incorporated into title/context
   - out_of_scope → constraints
   - deliverables → deliverables section
   - definition_of_done → definition_of_done section
   - constraints → constraints section

2. **Validate against compiled_output_schema**
   - Each field present and type-correct
   - Array lengths within bounds
   - No extra fields

3. **Apply user answers**
   - Incorporate clarifications where they affect CTC content
   - Set resolved_by = "user" if answers provided
   - Set resolved_by = "default" if defaults used

4. **Generate telemetry**
   - intent_id: UUID from session
   - created_at: ISO-8601 timestamp
   - executor: From context or "claude-code"
   - elapsed_ms: Time spent
   - input_tokens/output_tokens: If tracked (nullable)
   - user_questions_count: Count of questions asked
   - execution_result: "unknown" (filled after execution)

---

## Error Handling

If compiled_output_schema is missing:
```json
{
  "error": {
    "code": "MISSING_SCHEMA",
    "message": "compiled_output_schema not provided in context"
  }
}
```

If semantic_frame is incomplete:
```json
{
  "error": {
    "code": "INCOMPLETE_FRAME",
    "message": "semantic_frame missing required slots: [list]"
  }
}
```

---

## Common CTC Patterns

### Software Feature
```
Title: Add date range filter to activity log
Context: Activity log exists and needs date range filtering
DoD:
  - Filter UI component added
  - Filtering logic implemented
  - Can clear filters to show all
Constraints: Use existing date picker library
Deliverables: Updated activity log component, filtering logic
```

### Bug Report
```
Title: Fix 500 error on password reset
Context: Password reset flow triggers 500 error
DoD:
  - Error no longer occurs
  - Can login with newly reset password
  - No error logs from handler
Constraints: Do not change authentication system
Deliverables: Password reset handler fix
```

### Clarification Needed Case
```
Title: Export monthly sales report
Clarifications:
  - Question: "What format?"
    Options: [CSV, PDF, XLSX]
    Default: CSV
DoD: (from resolved clarifications)
Deliverables: (from resolved clarifications)
```

---

## Output Rules
- Output JSON only, no markdown
- No extra keys beyond schema
- No comments or explanations
- Result must be valid, parseable JSON

---

## Summary
CTC is ready for execution when:
1. All fields match compiled_output_schema
2. Title + context + DoD are clear and specific
3. Deliverables are concrete artifacts
4. Constraints prevent scope creep
5. Telemetry is complete
6. No vague language present

Pass CTC to execution agent with confidence.
