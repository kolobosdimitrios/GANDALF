# STEP 2: Gap Detection & Coverage Scoring

## Goal
Score completeness of the semantic_frame and identify minimal blocking questions needed to proceed deterministically to CTC generation.

---

## Coverage Scoring

### Scoring Weights (sum to 100)
- Goal + DoD clarity: 15%
- Deliverables + naming: 15%
- Constraints + non-goals: 15%
- Target environment: 10%
- Toolchain: 10%
- Idempotency: 10%
- Verification: 10%
- Security/secrets: 10%
- Determinism/version pinning: 5%

### Completeness Per Slot
- **0.0** - Missing
- **0.5** - Partial
- **1.0** - Complete

### Output Schema
```json
{
  "coverage_report": {
    "score_total": 0,
    "blocking": true,
    "slot_scores": [
      {
        "slot": "string",
        "weight": 0,
        "completeness": 0.0,
        "notes": "string"
      }
    ],
    "blocking_questions": [
      {
        "question_id": "Q1",
        "slot": "string",
        "question": "string",
        "why": "string",
        "default_if_blank": "string",
        "answer_format": "string"
      }
    ],
    "non_blocking_questions": [
      {
        "question_id": "N1",
        "slot": "string",
        "question": "string",
        "why": "string",
        "default_if_blank": "string",
        "answer_format": "string"
      }
    ],
    "defaults_applied": ["string"]
  }
}
```

---

## Blocking Rules

Set `blocking: true` if ANY of these are incomplete without safe default:
- execution_entrypoint.only_command_user_runs
- vm_provider + provisioning
- deliverables (must include setuph.sh and cloud-init yaml)
- secrets_policy
- database.type
- claude_code_cli.install_method OR documented single default
- verification list (must be non-empty)

If safe defaults exist:
- Include in defaults_applied array
- Do NOT block
- Set blocking: false

---

## Question Rules

For blocking_questions:
- Must be the minimal set to remove blocking=true
- Use multiple choice whenever possible
- Each question must be answerable in one line
- Do not add new questions

For non_blocking_questions:
- Helpful but not required
- Applied with defaults if unanswered
- Keep list short

---

## Orchestration Logic

Based on coverage_report, take action:

1. **If score < threshold**: action = ASK_USER with blocking_questions
2. **If score >= threshold**: action = RUN_STEP_3 (CTC Generation prep)
3. **If user answers provided**: action = RE_SCORE (update coverage with answers)

---

## User Question Packaging

When preparing questions for the user:
- Only include blocking_questions
- Format as compact structured questions
- Always include default_if_blank
- Never add "why" unless specifically requested

### Packaged Output Schema
```json
{
  "questions_to_user": [
    {
      "question_id": "Q1",
      "question": "string",
      "default_if_blank": "string",
      "answer_format": "string"
    }
  ]
}
```

---

## Input to Gap Detection
- semantic_frame: object
- context: object (optional)
- user_answers: object (optional)

---

## Summary
After Gap Detection, you have:
1. **Coverage Score** - Completeness assessment (0-100)
2. **Blocking Status** - Can proceed or need user input
3. **Questions (if needed)** - Minimal set to resolve blocking issues
4. **Defaults Applied** - What was assumed automatically

If no blocking questions: proceed to STEP 3.
If blocking questions exist: return them to user, wait for answers.
