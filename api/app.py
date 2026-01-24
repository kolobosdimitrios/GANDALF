"""
GANDALF REST API
Provides endpoints for user intent submission and CTC generation
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import os
import logging
from typing import Dict, Any
import time

# Import GANDALF modules - Multi-agent system
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .multi_agent_client import MultiAgentClient
from .efficiency_calculator import EfficiencyCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize multi-agent client
multi_agent_client = MultiAgentClient(
    pipeline_endpoint=os.getenv('GANDALF_PIPELINE_ENDPOINT', 'http://localhost:8080')
)

# Initialize efficiency calculator
efficiency_calculator = EfficiencyCalculator()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    Returns server status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'gandalf-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# User intent submission endpoint
@app.route('/api/intent', methods=['POST'])
def submit_intent():
    """
    Accept user intent and generate CTC

    Required fields:
    - date: ISO-8601 timestamp
    - generate_for: Target AI agent (e.g., "AI-AGENT")
    - user_prompt: The raw user intent

    Returns:
    - Generated CTC in GANDALF format
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400

        data = request.get_json()

        # Validate required fields
        required_fields = ['date', 'generate_for', 'user_prompt']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400

        # Extract data
        date = data['date']
        generate_for = data['generate_for']
        user_prompt = data['user_prompt']

        # Validate date format
        try:
            datetime.fromisoformat(date.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use ISO-8601 format'
            }), 400

        # Generate intent ID
        intent_id = str(uuid.uuid4())

        logger.info(f"Processing intent {intent_id} for {generate_for}")
        logger.info(f"User prompt: {user_prompt[:100]}...")

        # Measure start time
        start_time = time.time()

        # Generate CTC using GANDALF logic
        ctc = generate_ctc(user_prompt, intent_id, date, generate_for)

        # Calculate elapsed time
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Update telemetry with actual elapsed time
        if 'telemetry' in ctc:
            ctc['telemetry']['elapsed_ms'] = elapsed_ms

        # Calculate and add efficiency metrics
        efficiency_data = efficiency_calculator.calculate_with_metadata(user_prompt, ctc)
        if 'telemetry' in ctc:
            ctc['telemetry']['efficiency'] = efficiency_data

        logger.info(f"Intent {intent_id} processed in {elapsed_ms}ms")
        logger.info(f"Efficiency: {efficiency_data['efficiency_percentage']}%")

        return jsonify(ctc), 200

    except Exception as e:
        logger.error(f"Error processing intent: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


def generate_ctc(user_prompt: str, intent_id: str, date: str, generate_for: str) -> Dict[str, Any]:
    """
    Generate a Compiled Task Contract from user prompt using GANDALF Multi-Agent Pipeline

    The multi-agent pipeline will:
    1. Analyze the intent (lexical analysis)
    2. Analyze semantics and detect gaps
    3. Score coverage and generate blocking questions if needed
    4. Generate complete CTC when ready

    Args:
        user_prompt: Raw user intent
        intent_id: Unique identifier for this intent
        date: Timestamp
        generate_for: Target AI agent

    Returns:
        CTC in GANDALF format OR clarification request
    """
    # Use MultiAgentClient which orchestrates the 4-step pipeline
    result = multi_agent_client.process_intent(user_prompt)

    # Add metadata to the result
    if result['status'] == 'ctc_generated':
        # Wrap in standard GANDALF output format
        return {
            'intent_id': intent_id,
            'date': date,
            'generate_for': generate_for,
            'user_intent': user_prompt,
            'status': 'completed',
            'ctc': result['ctc'],
            'telemetry': {
                'intent_analysis': result.get('intent_analysis'),
                'gap_detection': result.get('gap_detection'),
                'efficiency': result.get('efficiency_metrics')
            }
        }
    elif result['status'] == 'needs_clarification':
        # Return clarification request
        return {
            'intent_id': intent_id,
            'date': date,
            'generate_for': generate_for,
            'user_intent': user_prompt,
            'status': 'needs_clarification',
            'intent_analysis': result['intent_analysis'],
            'gap_detection': result['gap_detection'],
            'clarification_questions': result['clarification_questions']
        }
    elif result['status'] == 'error':
        # Return error
        return {
            'intent_id': intent_id,
            'date': date,
            'generate_for': generate_for,
            'user_intent': user_prompt,
            'status': 'error',
            'error': result['error'],
            'details': result.get('details')
        }
    else:
        # Unknown status
        return {
            'intent_id': intent_id,
            'date': date,
            'generate_for': generate_for,
            'user_intent': user_prompt,
            'status': 'error',
            'error': 'Unknown result status',
            'details': str(result)
        }


# Get CTC by ID endpoint
@app.route('/api/ctc/<intent_id>', methods=['GET'])
def get_ctc(intent_id: str):
    """
    Retrieve a previously generated CTC by intent ID

    Args:
        intent_id: UUID of the intent

    Returns:
        CTC data or 404 if not found
    """
    # TODO: Implement database lookup
    return jsonify({
        'error': 'Not implemented yet',
        'message': 'Database integration pending'
    }), 501


# Submit clarifications endpoint
@app.route('/api/intent/clarify', methods=['POST'])
def submit_clarifications():
    """
    Submit clarification answers to continue CTC generation

    Required fields:
    - date: ISO-8601 timestamp
    - generate_for: Target AI agent
    - user_prompt: The original user intent
    - clarifications: Object with answers to clarification questions

    Returns:
    - Generated CTC in GANDALF format
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400

        data = request.get_json()

        # Validate required fields
        required_fields = ['date', 'generate_for', 'user_prompt', 'clarifications']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400

        # Extract data
        date = data['date']
        generate_for = data['generate_for']
        user_prompt = data['user_prompt']
        clarifications = data['clarifications']

        # Generate intent ID
        intent_id = str(uuid.uuid4())

        logger.info(f"Processing clarifications for {generate_for}")
        logger.info(f"Original prompt: {user_prompt[:100]}...")

        # Measure start time
        start_time = time.time()

        # Submit clarifications to multi-agent client
        result = multi_agent_client.submit_clarifications(user_prompt, clarifications)

        # Calculate elapsed time
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Format response (same as submit_intent)
        if result['status'] == 'ctc_generated':
            response = {
                'intent_id': intent_id,
                'date': date,
                'generate_for': generate_for,
                'user_intent': user_prompt,
                'status': 'completed',
                'ctc': result['ctc'],
                'telemetry': {
                    'intent_analysis': result.get('intent_analysis'),
                    'gap_detection': result.get('gap_detection'),
                    'efficiency': result.get('efficiency_metrics'),
                    'elapsed_ms': elapsed_ms
                }
            }
        else:
            response = {
                'intent_id': intent_id,
                'date': date,
                'generate_for': generate_for,
                'user_intent': user_prompt,
                'status': result['status'],
                'error': result.get('error'),
                'details': result.get('details')
            }

        logger.info(f"Clarifications processed in {elapsed_ms}ms")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error processing clarifications: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


# Agent status endpoint
@app.route('/api/agent/status', methods=['GET'])
def agent_status():
    """
    Check multi-agent pipeline status and readiness

    Returns:
        Agent status information
    """
    try:
        status = multi_agent_client.get_agent_status()
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error checking agent status: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# List all intents endpoint
@app.route('/api/intents', methods=['GET'])
def list_intents():
    """
    List all user intents with pagination

    Query params:
    - page: Page number (default: 1)
    - limit: Items per page (default: 20)

    Returns:
        List of intents
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    # TODO: Implement database query with pagination
    return jsonify({
        'error': 'Not implemented yet',
        'message': 'Database integration pending'
    }), 501


if __name__ == '__main__':
    # Development server
    # In production, use gunicorn or uwsgi
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting GANDALF API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
