"""
AI Agent Client

Handles communication with the AI agent running in the GANDALF VM.
The agent reads instruction files and processes requests according to GANDALF rules.
"""

import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import httpx

logger = logging.getLogger(__name__)


class AgentClient:
    """
    Client for communicating with the GANDALF AI Agent.

    The AI agent reads instruction files from ai_agent_prompts/ and processes
    requests according to GANDALF methodology.
    """

    def __init__(self, prompts_dir: str = None, agent_endpoint: str = None):
        """
        Initialize the agent client.

        Args:
            prompts_dir: Directory containing AI agent prompt files
            agent_endpoint: URL endpoint for the AI agent (e.g., http://localhost:8080/agent)
        """
        if prompts_dir is None:
            base_dir = Path(__file__).parent.parent
            prompts_dir = base_dir / "ai_agent_prompts"

        self.prompts_dir = Path(prompts_dir)
        self.agent_endpoint = agent_endpoint or os.getenv('GANDALF_AGENT_ENDPOINT', 'http://localhost:8080/agent')

        # Verify prompts directory exists
        if not self.prompts_dir.exists():
            raise ValueError(f"Prompts directory not found: {self.prompts_dir}")

        logger.info(f"AgentClient initialized with prompts_dir: {self.prompts_dir}")
        logger.info(f"Agent endpoint: {self.agent_endpoint}")

    def _load_prompt_file(self, filename: str) -> str:
        """Load an instruction file for the AI agent."""
        filepath = self.prompts_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Prompt file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def _send_to_agent(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to the AI agent and get response.

        This method handles the actual communication with the AI agent VM.
        The agent will read the corresponding instruction file and process the request.

        Args:
            task_type: Type of task (intent_analysis, gap_detection, ctc_generation)
            payload: Request data to send to the agent

        Returns:
            Agent's response as a dictionary
        """
        # Load the instruction file for this task type
        instruction_files = {
            'intent_analysis': '01_INTENT_ANALYSIS.md',
            'gap_detection': '02_GAP_DETECTION.md',
            'ctc_generation': '03_CTC_GENERATION.md'
        }

        if task_type not in instruction_files:
            raise ValueError(f"Unknown task type: {task_type}")

        instruction_file = instruction_files[task_type]
        instructions = self._load_prompt_file(instruction_file)

        # Also load the agent role definition
        role_definition = self._load_prompt_file('AGENT_ROLE.md')

        # Prepare the request for the AI agent
        agent_request = {
            'role': role_definition,
            'instructions': instructions,
            'task': task_type,
            'payload': payload
        }

        logger.info(f"Sending {task_type} request to AI agent")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

        try:
            # Send HTTP request to AI agent service
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    self.agent_endpoint,
                    json=agent_request
                )
                response.raise_for_status()
                result = response.json()

            logger.info(f"AI agent response received")
            logger.debug(f"Response: {json.dumps(result, indent=2)[:500]}...")

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from AI agent: {e.response.status_code}")
            logger.error(f"Response: {e.response.text[:500]}")
            raise ConnectionError(
                f"AI Agent returned error {e.response.status_code}: {e.response.text[:200]}"
            )

        except httpx.TimeoutException as e:
            logger.error(f"Timeout communicating with AI agent: {e}")
            raise TimeoutError(
                f"AI Agent did not respond within timeout period"
            )

        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to AI agent at {self.agent_endpoint}: {e}")
            raise ConnectionError(
                f"Cannot connect to AI Agent at {self.agent_endpoint}. "
                f"Ensure the AI agent service is running."
            )

        except Exception as e:
            logger.error(f"Error communicating with AI agent: {e}")
            raise

    def analyze_intent(self, user_intent: str) -> Dict[str, Any]:
        """
        Ask the AI agent to analyze a user intent.

        Args:
            user_intent: The user's natural language request

        Returns:
            Intent analysis result with classification and metadata
        """
        payload = {
            'user_intent': user_intent
        }

        return self._send_to_agent('intent_analysis', payload)

    def detect_gaps(
        self,
        user_intent: str,
        intent_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ask the AI agent to detect information gaps.

        Args:
            user_intent: The user's original request
            intent_analysis: Result from analyze_intent()

        Returns:
            Gap detection result with questions and assumptions
        """
        payload = {
            'user_intent': user_intent,
            'intent_analysis': intent_analysis
        }

        return self._send_to_agent('gap_detection', payload)

    def generate_ctc(
        self,
        user_intent: str,
        intent_analysis: Dict[str, Any],
        gap_detection: Dict[str, Any],
        clarifications: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ask the AI agent to generate a complete CTC.

        Args:
            user_intent: The user's original request
            intent_analysis: Result from analyze_intent()
            gap_detection: Result from detect_gaps()
            clarifications: User's answers to clarification questions (if any)

        Returns:
            Complete CTC following GANDALF schema
        """
        payload = {
            'user_intent': user_intent,
            'intent_analysis': intent_analysis,
            'gap_detection': gap_detection,
            'clarifications': clarifications or {}
        }

        return self._send_to_agent('ctc_generation', payload)
