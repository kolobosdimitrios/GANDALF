"""
AI Agent Service

HTTP service that processes GANDALF requests using multiple Claude models.
This service runs in the GANDALF VM and handles:
- Intent analysis
- Gap detection
- CTC generation

It uses different Claude models (Haiku, Sonnet, Opus) based on task complexity
to optimize cost and performance.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from flask import Flask, request, jsonify, Response
from anthropic import Anthropic
from model_router import ModelRouter, ClaudeModel

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

# Initialize model router
model_router = ModelRouter(
    enable_haiku=os.getenv('GANDALF_ENABLE_HAIKU', 'true').lower() == 'true',
    enable_opus=os.getenv('GANDALF_ENABLE_OPUS', 'true').lower() == 'true',
    force_model=os.getenv('GANDALF_FORCE_MODEL'),
    default_model=os.getenv('GANDALF_DEFAULT_MODEL', 'sonnet')
)

# Telemetry tracking
telemetry = {
    "requests_total": 0,
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
        system_prompt: System prompt (role + instructions)
        user_message: User message (task + payload)
        max_tokens: Max tokens for response (uses model default if not provided)
        temperature: Temperature (uses model default if not provided)

    Returns:
        Dictionary with response content and usage statistics
    """
    # Get model configuration
    config = model_router.get_model_config(model)

    # Use provided values or defaults from config
    max_tokens = max_tokens or config["max_tokens"]
    temperature = temperature or config["temperature"]

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


def process_agent_request(
    role: str,
    instructions: str,
    task: str,
    payload: Dict[str, Any],
    prefer_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process an agent request with the appropriate model.

    Args:
        role: Agent role definition (AGENT_ROLE.md content)
        instructions: Task-specific instructions (01_*, 02_*, 03_* content)
        task: Task type (intent_analysis, gap_detection, ctc_generation)
        payload: Task payload (user intent, context, etc.)
        prefer_model: User preference for model (optional)

    Returns:
        Agent response as dictionary
    """
    logger.info(f"Processing task: {task}")

    # Select appropriate model
    model = model_router.select_model(
        task_type=task,
        complexity=payload.get('complexity', 'medium'),
        prefer_model=prefer_model
    )

    # Build system prompt (role + instructions)
    system_prompt = f"{role}\n\n{instructions}"

    # Build user message (task description + payload)
    user_message = f"""
Now perform the task: {task}

Input data:
{json.dumps(payload, indent=2)}

IMPORTANT:
- Return ONLY valid JSON following the schema in the instructions
- Do NOT include markdown code blocks (no ```json)
- Do NOT include explanatory text before or after the JSON
- Ensure all required fields are present
"""

    # Call Claude API
    api_response = call_claude_api(
        model=model,
        system_prompt=system_prompt,
        user_message=user_message
    )

    # Parse JSON response
    try:
        # Extract JSON from response (in case there's extra text)
        content = api_response["content"].strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            # Find the actual JSON content
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

        result = json.loads(content)

        # Add telemetry to response
        result["_telemetry"] = {
            "model_used": api_response["model"],
            "input_tokens": api_response["input_tokens"],
            "output_tokens": api_response["output_tokens"],
            "cost_usd": api_response["cost_usd"],
            "task_type": task
        }

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.error(f"Response content: {api_response['content'][:500]}")
        raise ValueError(f"AI agent returned invalid JSON: {str(e)}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "GANDALF AI Agent Service",
        "models_enabled": {
            "haiku": model_router.enable_haiku,
            "sonnet": True,  # Always available
            "opus": model_router.enable_opus
        },
        "telemetry": telemetry
    })


@app.route('/models', methods=['GET'])
def list_models():
    """List available models and their configurations."""
    models_info = {}

    for model in [ClaudeModel.HAIKU, ClaudeModel.SONNET, ClaudeModel.OPUS]:
        config = model_router.get_model_config(model)
        models_info[model.name.lower()] = {
            "model_id": model.value,
            "enabled": (
                True if model == ClaudeModel.SONNET
                else model_router.enable_haiku if model == ClaudeModel.HAIKU
                else model_router.enable_opus
            ),
            "config": config
        }

    return jsonify({
        "models": models_info,
        "default_model": model_router.default_model.name.lower(),
        "force_model": model_router.force_model
    })


@app.route('/agent', methods=['POST'])
def agent_endpoint():
    """
    Main agent endpoint.

    Accepts requests with role, instructions, task, and payload.
    Routes to appropriate Claude model and returns JSON response.
    """
    try:
        telemetry["requests_total"] += 1

        # Parse request
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required_fields = ["role", "instructions", "task", "payload"]
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400

        # Extract fields
        role = data["role"]
        instructions = data["instructions"]
        task = data["task"]
        payload = data["payload"]
        prefer_model = data.get("model")  # Optional model preference

        # Process request
        result = process_agent_request(
            role=role,
            instructions=instructions,
            task=task,
            payload=payload,
            prefer_model=prefer_model
        )

        return jsonify(result)

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        telemetry["errors_total"] += 1
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.route('/telemetry', methods=['GET'])
def get_telemetry():
    """Get telemetry data."""
    # Calculate total cost
    total_cost = sum(telemetry["cost_by_model"].values())

    # Calculate total tokens
    total_tokens = {
        "input": sum(m["input"] for m in telemetry["tokens_by_model"].values()),
        "output": sum(m["output"] for m in telemetry["tokens_by_model"].values())
    }

    return jsonify({
        "telemetry": telemetry,
        "summary": {
            "total_requests": telemetry["requests_total"],
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
    logger.info("GANDALF AI Agent Service Starting")
    logger.info("=" * 60)
    logger.info(f"Model Router: {model_router}")
    logger.info("=" * 60)

    # Get port from environment or default to 8080
    port = int(os.getenv('GANDALF_AGENT_PORT', 8080))

    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
