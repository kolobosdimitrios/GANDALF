"""
Pipeline AI Agent Service

HTTP service for the 4-step GANDALF pipeline using multi-model optimization.

Pipeline Steps:
1. Lexical Analysis (Haiku) - Extract structure without interpretation
2. Semantic Analysis (Sonnet) - Build semantic frame
3. Coverage Scoring (Haiku) - Score completeness, generate questions
4. CTC Generation (Opus) - Generate final CTC after questions resolved
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify
from anthropic import Anthropic
from pipeline_model_router import PipelineModelRouter, ClaudeModel, PipelineStep

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Anthropic client
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
if not anthropic_api_key:
    logger.error("ANTHROPIC_API_KEY environment variable not set!")
    raise ValueError("ANTHROPIC_API_KEY is required")

anthropic_client = Anthropic(api_key=anthropic_api_key)

# Initialize pipeline model router
model_router = PipelineModelRouter(
    enable_haiku=os.getenv('GANDALF_ENABLE_HAIKU', 'true').lower() == 'true',
    enable_opus=os.getenv('GANDALF_ENABLE_OPUS', 'true').lower() == 'true',
    force_model=os.getenv('GANDALF_FORCE_MODEL'),
    default_model=os.getenv('GANDALF_DEFAULT_MODEL', 'sonnet')
)

# Path to instruction files
PROMPTS_DIR = Path(__file__).parent.parent / "ai_agent_prompts"
if not PROMPTS_DIR.exists():
    # Fallback to current directory structure
    PROMPTS_DIR = Path("/opt/apps/gandlf")

# Telemetry tracking
telemetry = {
    "requests_total": 0,
    "pipeline_runs": 0,
    "steps_completed": {
        "lexical": 0,
        "semantic": 0,
        "coverage": 0,
        "ctc": 0
    },
    "requests_by_model": {"haiku": 0, "sonnet": 0, "opus": 0},
    "tokens_by_model": {
        "haiku": {"input": 0, "output": 0},
        "sonnet": {"input": 0, "output": 0},
        "opus": {"input": 0, "output": 0}
    },
    "cost_by_model": {"haiku": 0.0, "sonnet": 0.0, "opus": 0.0},
    "errors_total": 0,
    "start_time": datetime.utcnow().isoformat()
}


def track_usage(model: ClaudeModel, input_tokens: int, output_tokens: int, cost: float):
    """Track model usage for telemetry."""
    model_name = model.name.lower()
    telemetry["requests_by_model"][model_name] += 1
    telemetry["tokens_by_model"][model_name]["input"] += input_tokens
    telemetry["tokens_by_model"][model_name]["output"] += output_tokens
    telemetry["cost_by_model"][model_name] += cost


def load_instruction_file(filename: str) -> str:
    """Load instruction file content."""
    try:
        file_path = PROMPTS_DIR / filename
        if not file_path.exists():
            logger.error(f"Instruction file not found: {file_path}")
            raise FileNotFoundError(f"Instruction file not found: {filename}")

        with open(file_path, 'r') as f:
            content = f.read()

        logger.debug(f"Loaded instruction file: {filename}")
        return content

    except Exception as e:
        logger.error(f"Error loading instruction file {filename}: {e}")
        raise


def call_claude_api(
    model: ClaudeModel,
    system_prompt: str,
    user_message: str,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None
) -> Dict[str, Any]:
    """
    Call Claude API with specified model.

    Args:
        model: ClaudeModel to use
        system_prompt: System prompt (instructions)
        user_message: User message (task payload)
        max_tokens: Max tokens for response
        temperature: Temperature setting

    Returns:
        Dictionary with response content and usage statistics
    """
    # Get model configuration
    config = model_router.get_model_config(model)

    # Use provided values or defaults from config
    max_tokens = max_tokens or config["max_tokens"]
    temperature = temperature if temperature is not None else config["temperature"]

    logger.info(f"Calling Claude API with model: {model.value}")
    logger.debug(f"Max tokens: {max_tokens}, Temperature: {temperature}")

    try:
        response = anthropic_client.messages.create(
            model=model.value,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        # Extract response content
        content = response.content[0].text if response.content else ""

        # Get token usage
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Calculate cost
        cost = model_router.estimate_cost(model, input_tokens, output_tokens)

        # Track usage
        track_usage(model, input_tokens, output_tokens, cost)

        logger.info(f"API call successful:")
        logger.info(f"  Input tokens: {input_tokens}")
        logger.info(f"  Output tokens: {output_tokens}")
        logger.info(f"  Cost: ${cost:.6f}")

        return {
            "content": content,
            "model": model.value,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost
        }

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        telemetry["errors_total"] += 1

        # Try fallback model
        fallback_model = model_router.get_fallback_model(model)
        if fallback_model != model:
            logger.info(f"Trying fallback model: {fallback_model.value}")
            return call_claude_api(
                fallback_model,
                system_prompt,
                user_message,
                max_tokens,
                temperature
            )

        raise


def parse_json_response(content: str) -> Dict[str, Any]:
    """Parse JSON response, handling markdown code blocks."""
    content = content.strip()

    # Remove markdown code blocks if present
    if content.startswith("```"):
        lines = content.split('\n')
        start_idx = 0
        end_idx = len(lines)

        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                if start_idx == 0:
                    start_idx = i + 1
                else:
                    end_idx = i
                    break

        content = '\n'.join(lines[start_idx:end_idx])

    return json.loads(content)


def execute_step_1_lexical(user_message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute Step 1: Lexical Analysis (Haiku).

    Extract structure from user message without deep interpretation.
    """
    logger.info("=== Step 1: Lexical Analysis ===")

    # Load instruction file
    instructions = load_instruction_file("LexicalAnalysis.md")

    # Select model
    model = model_router.select_model_for_step("lexical_analysis")

    # Build user message
    payload = {
        "user_message": user_message,
        "context": context or {}
    }

    user_msg = f"""
Perform lexical analysis on the user message.

Input:
{json.dumps(payload, indent=2)}

Return ONLY valid JSON following the schema in the instructions.
Do NOT include markdown code blocks or explanatory text.
"""

    # Call Claude API
    api_response = call_claude_api(
        model=model,
        system_prompt=instructions,
        user_message=user_msg
    )

    # Parse response
    result = parse_json_response(api_response["content"])

    # Add telemetry
    result["_telemetry"] = {
        "model_used": api_response["model"],
        "input_tokens": api_response["input_tokens"],
        "output_tokens": api_response["output_tokens"],
        "cost_usd": api_response["cost_usd"],
        "step": "lexical_analysis"
    }

    telemetry["steps_completed"]["lexical"] += 1
    return result


def execute_step_2_semantic(
    user_message: str,
    lexical_report: Dict,
    context: Optional[Dict] = None,
    user_answers: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Execute Step 2: Semantic Analysis (Sonnet).

    Convert lexical structure into semantic frame.
    """
    logger.info("=== Step 2: Semantic Analysis ===")

    # Load instruction file
    instructions = load_instruction_file("Semantic_Analysis.md")

    # Select model
    model = model_router.select_model_for_step("semantic_analysis")

    # Build user message
    payload = {
        "user_message": user_message,
        "lexical_report": lexical_report,
        "context": context or {},
        "user_answers": user_answers or {}
    }

    user_msg = f"""
Perform semantic analysis to build a semantic frame.

Input:
{json.dumps(payload, indent=2)}

Return ONLY valid JSON following the schema in the instructions.
Do NOT include markdown code blocks or explanatory text.
"""

    # Call Claude API
    api_response = call_claude_api(
        model=model,
        system_prompt=instructions,
        user_message=user_msg
    )

    # Parse response
    result = parse_json_response(api_response["content"])

    # Add telemetry
    result["_telemetry"] = {
        "model_used": api_response["model"],
        "input_tokens": api_response["input_tokens"],
        "output_tokens": api_response["output_tokens"],
        "cost_usd": api_response["cost_usd"],
        "step": "semantic_analysis"
    }

    telemetry["steps_completed"]["semantic"] += 1
    return result


def execute_step_3_coverage(
    semantic_frame: Dict,
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Execute Step 3: Coverage Scoring & Questions (Haiku).

    Score completeness and generate minimal blocking questions.
    """
    logger.info("=== Step 3: Coverage Scoring ===")

    # Load instruction file
    instructions = load_instruction_file("Coverage_Scoring_and_Questions.md")

    # Select model
    model = model_router.select_model_for_step("coverage_scoring")

    # Build user message
    payload = {
        "semantic_frame": semantic_frame,
        "context": context or {}
    }

    user_msg = f"""
Perform coverage scoring and generate questions if needed.

Input:
{json.dumps(payload, indent=2)}

Return ONLY valid JSON following the schema in the instructions.
Do NOT include markdown code blocks or explanatory text.
"""

    # Call Claude API
    api_response = call_claude_api(
        model=model,
        system_prompt=instructions,
        user_message=user_msg
    )

    # Parse response
    result = parse_json_response(api_response["content"])

    # Add telemetry
    result["_telemetry"] = {
        "model_used": api_response["model"],
        "input_tokens": api_response["input_tokens"],
        "output_tokens": api_response["output_tokens"],
        "cost_usd": api_response["cost_usd"],
        "step": "coverage_scoring"
    }

    telemetry["steps_completed"]["coverage"] += 1
    return result


def execute_step_4_ctc(
    semantic_frame: Dict,
    coverage_report: Dict,
    user_answers: Optional[Dict] = None,
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Execute Step 4: CTC Generation (Opus).

    Generate final Compiled Task Contract.
    """
    logger.info("=== Step 4: CTC Generation ===")

    # Load instruction file
    instructions = load_instruction_file("CTC_Generator.md")

    # Select model (always Opus for CTC generation)
    model = model_router.select_model_for_step("ctc_generation")

    # Build user message with schema
    compiled_output_schema = load_instruction_file("CompiledOutputSchema.md")

    payload = {
        "semantic_frame": semantic_frame,
        "coverage_report": coverage_report,
        "user_answers": user_answers or {},
        "context": {
            **(context or {}),
            "compiled_output_schema": compiled_output_schema
        }
    }

    user_msg = f"""
Generate the Compiled Task Contract (CTC).

Input:
{json.dumps(payload, indent=2)}

Return ONLY valid JSON following the schema in the instructions.
Do NOT include markdown code blocks or explanatory text.
"""

    # Call Claude API
    api_response = call_claude_api(
        model=model,
        system_prompt=instructions,
        user_message=user_msg
    )

    # Parse response
    result = parse_json_response(api_response["content"])

    # Add telemetry
    result["_telemetry"] = {
        "model_used": api_response["model"],
        "input_tokens": api_response["input_tokens"],
        "output_tokens": api_response["output_tokens"],
        "cost_usd": api_response["cost_usd"],
        "step": "ctc_generation"
    }

    telemetry["steps_completed"]["ctc"] += 1
    return result


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "GANDALF Pipeline AI Agent Service",
        "models_enabled": {
            "haiku": model_router.enable_haiku,
            "sonnet": True,
            "opus": model_router.enable_opus
        },
        "pipeline_plan": {
            step: model.value
            for step, model in model_router.get_pipeline_plan().items()
        },
        "telemetry": telemetry
    })


@app.route('/pipeline/step1', methods=['POST'])
def step1_lexical():
    """Execute Step 1: Lexical Analysis."""
    try:
        data = request.json
        if not data or "user_message" not in data:
            return jsonify({"error": "user_message is required"}), 400

        result = execute_step_1_lexical(
            user_message=data["user_message"],
            context=data.get("context")
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Step 1 error: {e}", exc_info=True)
        telemetry["errors_total"] += 1
        return jsonify({"error": str(e)}), 500


@app.route('/pipeline/step2', methods=['POST'])
def step2_semantic():
    """Execute Step 2: Semantic Analysis."""
    try:
        data = request.json
        if not data or "user_message" not in data or "lexical_report" not in data:
            return jsonify({"error": "user_message and lexical_report are required"}), 400

        result = execute_step_2_semantic(
            user_message=data["user_message"],
            lexical_report=data["lexical_report"],
            context=data.get("context"),
            user_answers=data.get("user_answers")
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Step 2 error: {e}", exc_info=True)
        telemetry["errors_total"] += 1
        return jsonify({"error": str(e)}), 500


@app.route('/pipeline/step3', methods=['POST'])
def step3_coverage():
    """Execute Step 3: Coverage Scoring."""
    try:
        data = request.json
        if not data or "semantic_frame" not in data:
            return jsonify({"error": "semantic_frame is required"}), 400

        result = execute_step_3_coverage(
            semantic_frame=data["semantic_frame"],
            context=data.get("context")
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Step 3 error: {e}", exc_info=True)
        telemetry["errors_total"] += 1
        return jsonify({"error": str(e)}), 500


@app.route('/pipeline/step4', methods=['POST'])
def step4_ctc():
    """Execute Step 4: CTC Generation."""
    try:
        data = request.json
        required = ["semantic_frame", "coverage_report"]
        missing = [f for f in required if f not in data]

        if missing:
            return jsonify({"error": f"Missing required fields: {missing}"}), 400

        result = execute_step_4_ctc(
            semantic_frame=data["semantic_frame"],
            coverage_report=data["coverage_report"],
            user_answers=data.get("user_answers"),
            context=data.get("context")
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Step 4 error: {e}", exc_info=True)
        telemetry["errors_total"] += 1
        return jsonify({"error": str(e)}), 500


@app.route('/telemetry', methods=['GET'])
def get_telemetry():
    """Get telemetry data."""
    total_cost = sum(telemetry["cost_by_model"].values())
    total_tokens = {
        "input": sum(m["input"] for m in telemetry["tokens_by_model"].values()),
        "output": sum(m["output"] for m in telemetry["tokens_by_model"].values())
    }

    return jsonify({
        "telemetry": telemetry,
        "summary": {
            "total_requests": telemetry["requests_total"],
            "pipeline_runs": telemetry["pipeline_runs"],
            "total_cost_usd": round(total_cost, 6),
            "total_tokens": total_tokens,
            "total_errors": telemetry["errors_total"],
            "uptime": datetime.utcnow().isoformat()
        }
    })


@app.route('/telemetry/reset', methods=['POST'])
def reset_telemetry():
    """Reset telemetry data."""
    global telemetry
    telemetry = {
        "requests_total": 0,
        "pipeline_runs": 0,
        "steps_completed": {
            "lexical": 0,
            "semantic": 0,
            "coverage": 0,
            "ctc": 0
        },
        "requests_by_model": {"haiku": 0, "sonnet": 0, "opus": 0},
        "tokens_by_model": {
            "haiku": {"input": 0, "output": 0},
            "sonnet": {"input": 0, "output": 0},
            "opus": {"input": 0, "output": 0}
        },
        "cost_by_model": {"haiku": 0.0, "sonnet": 0.0, "opus": 0.0},
        "errors_total": 0,
        "start_time": datetime.utcnow().isoformat()
    }

    return jsonify({"status": "telemetry reset"})


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("GANDALF Pipeline AI Agent Service Starting")
    logger.info("=" * 60)
    logger.info(f"Model Router: {model_router}")
    logger.info(f"Pipeline Plan: {model_router.get_pipeline_plan()}")
    logger.info("=" * 60)

    port = int(os.getenv('GANDALF_AGENT_PORT', 8080))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
