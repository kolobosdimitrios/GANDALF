"""
Multi-Agent Client

Orchestrates communication with the multi-agent pipeline service.
Coordinates the 4-step CTC generation pipeline:
1. Lexical analysis (Step 1)
2. Semantic analysis (Step 2)
3. Coverage scoring (Step 3)
4. CTC generation (Step 4)
"""

import logging
import os
from typing import Dict, Any, Optional
import sys

# Add multi-agent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'multi-agent'))

from pipeline_orchestrator import PipelineOrchestrator, OrchestrationAction
from pipeline_client import PipelineClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiAgentClient:
    """
    Client that orchestrates the multi-agent pipeline.

    Handles:
    - Intent submission and CTC generation
    - Clarification questions when needed
    - Multi-step orchestration with cost optimization
    """

    def __init__(self, pipeline_endpoint: Optional[str] = None):
        """
        Initialize the multi-agent client.

        Args:
            pipeline_endpoint: Optional pipeline service endpoint
        """
        self.orchestrator = PipelineOrchestrator()
        self.pipeline_client = PipelineClient(endpoint=pipeline_endpoint)
        self.session_state = {}

        logger.info("MultiAgentClient initialized")

    def process_intent(self, user_prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a user intent and generate CTC through the multi-agent pipeline.

        Args:
            user_prompt: User's intent/request
            context: Optional context (project rules, schemas, etc.)

        Returns:
            Dictionary with status, CTC (if complete), or clarification questions
        """
        logger.info(f"Processing intent: {user_prompt[:100]}...")

        context = context or {}
        prior_outputs = {}

        # Execute pipeline steps
        while True:
            # Determine next action
            orchestration_result = self.orchestrator.determine_next_action(
                user_message=user_prompt,
                context=context,
                prior_outputs=prior_outputs,
                user_answers=self.session_state.get('user_answers')
            )

            action = OrchestrationAction(orchestration_result['action'])
            logger.info(f"Orchestration action: {action.value}")

            # Execute action
            if action == OrchestrationAction.RUN_STEP_1:
                result = self._execute_step_1(user_prompt, context)
                prior_outputs['lexical_report'] = result

            elif action == OrchestrationAction.RUN_STEP_2:
                result = self._execute_step_2(
                    user_prompt,
                    prior_outputs.get('lexical_report'),
                    context,
                    self.session_state.get('user_answers')
                )
                prior_outputs['semantic_frame'] = result

            elif action == OrchestrationAction.RUN_STEP_3:
                result = self._execute_step_3(
                    prior_outputs.get('semantic_frame'),
                    context
                )
                prior_outputs['coverage_report'] = result

            elif action == OrchestrationAction.ASK_USER:
                # Return clarification questions to the user
                blocking_questions = orchestration_result.get('user_questions', [])
                logger.info(f"Asking user {len(blocking_questions)} clarification questions")

                return {
                    'status': 'needs_clarification',
                    'intent_analysis': prior_outputs.get('lexical_report'),
                    'gap_detection': prior_outputs.get('semantic_frame'),
                    'clarification_questions': blocking_questions,
                    'efficiency_metrics': {}
                }

            elif action == OrchestrationAction.RUN_STEP_4:
                result = self._execute_step_4(
                    prior_outputs.get('semantic_frame'),
                    prior_outputs.get('coverage_report'),
                    self.session_state.get('user_answers'),
                    context
                )
                prior_outputs['ctc'] = result

                # Return generated CTC
                return {
                    'status': 'ctc_generated',
                    'ctc': result,
                    'intent_analysis': prior_outputs.get('lexical_report'),
                    'gap_detection': prior_outputs.get('semantic_frame'),
                    'efficiency_metrics': {}
                }

            elif action == OrchestrationAction.DONE:
                # CTC already exists
                logger.info("CTC generation complete")

                return {
                    'status': 'ctc_generated',
                    'ctc': prior_outputs.get('ctc'),
                    'intent_analysis': prior_outputs.get('lexical_report'),
                    'gap_detection': prior_outputs.get('semantic_frame'),
                    'efficiency_metrics': {}
                }

            elif action == OrchestrationAction.ERROR:
                logger.error("Orchestration error")

                return {
                    'status': 'error',
                    'error': 'Pipeline orchestration error',
                    'details': orchestration_result.get('status', {})
                }

            else:
                logger.error(f"Unknown orchestration action: {action}")

                return {
                    'status': 'error',
                    'error': 'Unknown orchestration action',
                    'details': str(action)
                }

    def submit_clarifications(
        self,
        user_prompt: str,
        clarifications: Dict[str, str],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Submit user answers to clarification questions and continue CTC generation.

        Args:
            user_prompt: Original user intent
            clarifications: Answers to clarification questions (question_id -> answer)
            context: Optional context

        Returns:
            Dictionary with status and CTC or next clarifications
        """
        logger.info("Submitting clarifications...")

        # Store user answers in session
        self.session_state['user_answers'] = clarifications

        # Continue processing with the answers
        context = context or {}

        # Re-process the intent with the answers
        return self.process_intent(user_prompt, context)

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get the status of the multi-agent pipeline service.

        Returns:
            Status information
        """
        try:
            health = self.pipeline_client.check_health()
            return {
                'status': 'ready',
                'service': 'gandalf-multi-agent-pipeline',
                'details': health
            }
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {
                'status': 'error',
                'service': 'gandalf-multi-agent-pipeline',
                'error': str(e)
            }

    def _execute_step_1(self, user_message: str, context: Dict) -> Dict[str, Any]:
        """Execute Step 1: Lexical Analysis."""
        logger.info("Executing Step 1: Lexical Analysis")

        try:
            result = self.pipeline_client.execute_step_1_lexical(
                user_message=user_message,
                context=context
            )
            logger.info("Step 1 complete")
            return result

        except Exception as e:
            logger.error(f"Step 1 failed: {e}")
            raise

    def _execute_step_2(
        self,
        user_message: str,
        lexical_report: Dict,
        context: Dict,
        user_answers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute Step 2: Semantic Analysis."""
        logger.info("Executing Step 2: Semantic Analysis")

        try:
            result = self.pipeline_client.execute_step_2_semantic(
                user_message=user_message,
                lexical_report=lexical_report,
                context=context,
                user_answers=user_answers
            )
            logger.info("Step 2 complete")
            return result

        except Exception as e:
            logger.error(f"Step 2 failed: {e}")
            raise

    def _execute_step_3(self, semantic_frame: Dict, context: Dict) -> Dict[str, Any]:
        """Execute Step 3: Coverage Scoring & Questions."""
        logger.info("Executing Step 3: Coverage Scoring")

        try:
            result = self.pipeline_client.execute_step_3_coverage(
                semantic_frame=semantic_frame,
                context=context
            )
            logger.info("Step 3 complete")
            return result

        except Exception as e:
            logger.error(f"Step 3 failed: {e}")
            raise

    def _execute_step_4(
        self,
        semantic_frame: Dict,
        coverage_report: Dict,
        user_answers: Optional[Dict] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute Step 4: CTC Generation."""
        logger.info("Executing Step 4: CTC Generation")

        try:
            result = self.pipeline_client.execute_step_4_ctc(
                semantic_frame=semantic_frame,
                coverage_report=coverage_report,
                user_answers=user_answers,
                context=context
            )
            logger.info("Step 4 complete")
            return result

        except Exception as e:
            logger.error(f"Step 4 failed: {e}")
            raise
