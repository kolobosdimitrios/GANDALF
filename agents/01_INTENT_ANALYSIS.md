# STEP 1: Intent Analysis & Semantic Framing

## Goal
Extract and validate user intent, then build a structured SemanticFrame for CTC generation.

---

## Substep 1A: Lexical Analysis

Extract structure from the user message without deep interpretation.

### Output Schema
```json
{
  "lexical_report": {
    "language": "en" | "el" | "mixed" | "unknown",
    "keywords": ["string"],
    "intent_verbs": ["string"],
    "entities": [
      {
        "type": "tool" | "os" | "version" | "file" | "path" | "service" | "db" | "constraint" | "project" | "other",
        "value": "string",
        "confidence": 0.0,
        "evidence": "short excerpt from user_message"
      }
    ],
    "artifacts": [
      {
        "kind": "file" | "directory" | "script" | "yaml" | "config" | "unknown",
        "name": "string",
        "confidence": 0.0,
        "evidence": "short excerpt"
      }
    ],
    "constraints": [
      {
        "rule": "string",
        "confidence": 0.0,
        "evidence": "short excerpt"
      }
    ],
    "ambiguities": [
      {
        "item": "string",
        "reason": "string",
        "suggested_disambiguations": ["string"]
      }
    ],
    "warnings": ["string"]
  }
}
```

### Lexical Analysis Rules
- Do not invent facts
- Keep evidence short (max 12 words)
- Prefer fewer, higher-signal keywords
- If no ambiguity, ambiguities must be []
- Output JSON only, no markdown

---

## Substep 1B: Intent Extraction

Identify from the user message:
- **What the user wants to change**
- **What exists already** (if stated)
- **The expected outcome**

Do not infer implementation details unless explicitly stated.

---

## Substep 1C: Semantic Frame Construction

Convert intent + lexical_report into a structured SemanticFrame.

### Output Schema
```json
{
  "semantic_frame": {
    "goal": "string (≤250 chars)",
    "scope": {
      "in_scope": ["string"],
      "out_of_scope": ["string"]
    },
    "target_environment": {
      "host_os": "macos" | "linux" | "windows" | "unknown",
      "vm_os": "ubuntu-lts" | "unknown",
      "vm_image_preference": "24.04" | "22.04" | "unknown",
      "architecture": "arm64" | "amd64" | "unknown"
    },
    "toolchain": {
      "vm_provider": "multipass" | "unknown",
      "provisioning": "cloud-init" | "unknown",
      "database": {
        "type": "postgresql" | "mysql" | "sqlite" | "unknown",
        "exposure": "localhost_only" | "host_only" | "lan" | "unknown"
      },
      "python": {
        "venv_path": "string",
        "requirements_source": "requirements.txt" | "inline" | "unknown"
      },
      "claude_code_cli": {
        "install_method": "official_installer" | "npm" | "unknown",
        "version_pin": "string|unknown",
        "standalone_on_path": true
      }
    },
    "deliverables": [
      {
        "path": "string",
        "purpose": "string"
      }
    ],
    "definition_of_done": ["string"],
    "execution_entrypoint": {
      "only_command_user_runs": "setuph.sh"
    },
    "idempotency": ["string"],
    "verification": ["string"],
    "security": {
      "secrets_policy": "generated_once_not_committed",
      "host_secrets_dir": ".secrets/",
      "vm_secrets_dir": "/etc/gandalf/",
      "network_exposure_policy": "do_not_expose_by_default"
    },
    "constraints": ["string"],
    "assumptions": ["string"],
    "open_questions": [
      {
        "slot": "string",
        "question": "string",
        "why": "string",
        "default_if_blank": "string",
        "answer_format": "string"
      }
    ]
  }
}
```

### Semantic Frame Rules
- Fill slots with explicit values when stated by the user
- If the user did not specify, apply safe defaults and record in assumptions
- Only put items in open_questions if they materially affect correctness
- Keep goal concise (≤250 chars)
- Output JSON only, no markdown

### Input to Semantic Analysis
- user_message: string
- lexical_report: object
- context: object (optional)
- user_answers: object (optional)

---

## Summary
After Intent Analysis, you have:
1. **Lexical Report** - Raw structure from user message
2. **Semantic Frame** - Structured context for next steps
3. **Open Questions** - Identified gaps that may need user input

Pass these to STEP 2: Gap Detection.
