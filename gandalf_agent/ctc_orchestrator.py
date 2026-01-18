"""
CTC Orchestration

Orchestrates the multi-step process of converting user intents to CTCs
using the AI agent for all analysis and generation.
"""

import logging
from typing import Dict, Any, Optional
from .agent_client import AgentClient

logger = logging.getLogger(__name__)


class CTCOrchestrator:
    """
    Orchestrates the CTC generation workflow using the AI agent.

    Workflow:
    1. User submits intent
    2. AI agent analyzes intent
    3. AI agent detects gaps
    4. If gaps exist, ask clarification questions
    5. User answers questions (optional step)
    6. AI agent generates CTC with all context
    """

    def __init__(self, agent_client: Optional[AgentClient] = None):
        """
        Initialize the orchestrator.

        Args:
            agent_client: AgentClient instance (creates default if not provided)
        """
        self.agent = agent_client or AgentClient()
        logger.info("CTCOrchestrator initialized")

    def process_intent(
        self,
        user_intent: str,
        clarifications: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user intent through the complete GANDALF pipeline.

        Args:
            user_intent: The user's natural language request
            clarifications: Answers to clarification questions (if this is a followup)

        Returns:
            Either:
            - Clarification request if gaps detected
            - Complete CTC if ready for implementation
        """
        logger.info(f"Processing intent: {user_intent[:100]}...")

        # Step 1: Ask AI agent to analyze intent
        logger.info("Step 1: Intent analysis via AI agent")
        try:
            intent_analysis = self.agent.analyze_intent(user_intent)
            logger.info(f"Intent classified as: {intent_analysis.get('intent_type')}")
            logger.debug(f"Intent analysis: {intent_analysis}")
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {
                'status': 'error',
                'error': f'Intent analysis failed: {str(e)}',
                'details': 'The AI agent could not analyze the intent. Please check agent connectivity.'
            }

        # Step 2: Ask AI agent to detect gaps
        logger.info("Step 2: Gap detection via AI agent")
        try:
            gap_detection = self.agent.detect_gaps(user_intent, intent_analysis)
            logger.info(f"Needs clarification: {gap_detection.get('needs_clarification')}")
            logger.debug(f"Gap detection: {gap_detection}")
        except Exception as e:
            logger.error(f"Gap detection failed: {e}")
            return {
                'status': 'error',
                'error': f'Gap detection failed: {str(e)}',
                'details': 'The AI agent could not detect gaps. Please check agent connectivity.'
            }

        # Step 3: Check if clarification is needed
        if gap_detection.get('needs_clarification', False) and not clarifications:
            logger.info("Clarification needed - returning questions to user")
            return {
                'status': 'needs_clarification',
                'intent_analysis': intent_analysis,
                'gap_detection': gap_detection,
                'clarification_questions': gap_detection.get('clarification_questions', [])
            }

        # Step 4: Ask AI agent to generate CTC
        logger.info("Step 3: CTC generation via AI agent")
        try:
            ctc_result = self.agent.generate_ctc(
                user_intent,
                intent_analysis,
                gap_detection,
                clarifications
            )
            logger.info("CTC generated successfully")
            logger.debug(f"CTC: {ctc_result}")
        except Exception as e:
            logger.error(f"CTC generation failed: {e}")
            return {
                'status': 'error',
                'error': f'CTC generation failed: {str(e)}',
                'details': 'The AI agent could not generate the CTC. Please check agent connectivity.'
            }

        # Return complete CTC
        return {
            'status': 'ctc_generated',
            'intent_analysis': intent_analysis,
            'gap_detection': gap_detection,
            'ctc': ctc_result.get('ctc'),
            'efficiency_metrics': ctc_result.get('efficiency_metrics')
        }

    def submit_clarifications(
        self,
        user_intent: str,
        clarifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit clarification answers and continue CTC generation.

        This is called after the user answers clarification questions.

        Args:
            user_intent: The original user intent
            clarifications: User's answers to the clarification questions

        Returns:
            Complete CTC
        """
        logger.info("Processing intent with clarifications")
        return self.process_intent(user_intent, clarifications)

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Check if the AI agent is available and responding.

        Returns:
            Status information about the agent
        """
        try:
            # Try to load prompts to verify setup
            agent_role = self.agent._load_prompt_file('AGENT_ROLE.md')

            return {
                'status': 'ready',
                'agent_endpoint': self.agent.agent_endpoint,
                'prompts_dir': str(self.agent.prompts_dir),
                'prompts_loaded': True,
                'note': 'AI agent communication needs to be implemented in agent_client.py'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'agent_endpoint': self.agent.agent_endpoint,
                'prompts_dir': str(self.agent.prompts_dir)
            }
