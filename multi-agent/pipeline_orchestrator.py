"""
Pipeline Orchestrator

Implements the orchestration logic from Orchestrator.md.

Coordinates the 4-step CTC generation pipeline:
1. Lexical analysis
2. Semantic analysis
3. Coverage scoring + question generation
4. CTC generation

Decision logic:
- If lexical_report missing -> RUN_STEP_1
- Else if semantic_frame missing OR user_answers changed -> RUN_STEP_2
- Else if coverage_report missing OR semantic_frame updated -> RUN_STEP_3
- Else if blocking_questions not empty AND user_answers missing -> ASK_USER
- Else if blocking_questions empty OR answered -> RUN_STEP_4
- If CTC exists and user didn't change requirements -> DONE
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class OrchestrationAction(Enum):
    """Possible orchestration actions."""
    RUN_STEP_1 = "RUN_STEP_1"
    RUN_STEP_2 = "RUN_STEP_2"
    RUN_STEP_3 = "RUN_STEP_3"
    ASK_USER = "ASK_USER"
    RUN_STEP_4 = "RUN_STEP_4"
    DONE = "DONE"
    ERROR = "ERROR"


class PipelineOrchestrator:
    """
    Orchestrates the 4-step GANDALF pipeline.

    Follows the decision logic from Orchestrator.md to minimize cost
    by routing to the cheapest appropriate model for each step.
    """

    def __init__(self):
        """Initialize the orchestrator."""
        logger.info("PipelineOrchestrator initialized")

    def determine_next_action(
        self,
        user_message: str,
        context: Optional[Dict] = None,
        prior_outputs: Optional[Dict] = None,
        user_answers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Determine the next action in the pipeline.

        Args:
            user_message: User's intent/request
            context: Optional context (project rules, schemas, etc.)
            prior_outputs: Optional prior outputs (lexical_report, semantic_frame, etc.)
            user_answers: Optional user answers to blocking questions

        Returns:
            Orchestration decision with action, routing, and payload
        """
        logger.info("Determining next action...")

        # Initialize
        prior_outputs = prior_outputs or {}
        context = context or {}
        user_answers = user_answers or {}

        # Extract prior outputs
        lexical_report = prior_outputs.get("lexical_report")
        semantic_frame = prior_outputs.get("semantic_frame")
        coverage_report = prior_outputs.get("coverage_report")
        ctc = prior_outputs.get("ctc")

        # Decision logic per Orchestrator.md

        # 1) If lexical_report missing -> RUN_STEP_1
        if not lexical_report:
            return self._build_response(
                action=OrchestrationAction.RUN_STEP_1,
                inputs_needed={"need_lexical_report": True},
                next_step_payload={
                    "user_message": user_message,
                    "context": context
                },
                status={
                    "blocking": False,
                    "score_total": None,
                    "notes": ["Starting pipeline: running lexical analysis"]
                }
            )

        # 2) If semantic_frame missing OR user_answers changed relevant slots -> RUN_STEP_2
        if not semantic_frame or (user_answers and self._semantic_affected_by_answers(semantic_frame, user_answers)):
            return self._build_response(
                action=OrchestrationAction.RUN_STEP_2,
                inputs_needed={
                    "need_lexical_report": False,
                    "need_semantic_frame": True
                },
                next_step_payload={
                    "user_message": user_message,
                    "lexical_report": lexical_report,
                    "context": context,
                    "user_answers": user_answers
                },
                status={
                    "blocking": False,
                    "score_total": None,
                    "notes": ["Running semantic analysis"]
                }
            )

        # 3) If coverage_report missing OR semantic_frame updated -> RUN_STEP_3
        if not coverage_report:
            return self._build_response(
                action=OrchestrationAction.RUN_STEP_3,
                inputs_needed={
                    "need_lexical_report": False,
                    "need_semantic_frame": False,
                    "need_coverage_report": True
                },
                next_step_payload={
                    "semantic_frame": semantic_frame,
                    "context": context
                },
                status={
                    "blocking": False,
                    "score_total": None,
                    "notes": ["Running coverage scoring"]
                }
            )

        # 4) If coverage_report.blocking_questions not empty AND user_answers missing -> ASK_USER
        blocking_questions = coverage_report.get("coverage_report", {}).get("blocking_questions", [])
        blocking = coverage_report.get("coverage_report", {}).get("blocking", False)

        if blocking and blocking_questions and not self._all_questions_answered(blocking_questions, user_answers):
            return self._build_response(
                action=OrchestrationAction.ASK_USER,
                inputs_needed={
                    "need_user_answers": True
                },
                user_questions=blocking_questions,
                status={
                    "blocking": True,
                    "score_total": coverage_report.get("coverage_report", {}).get("score_total"),
                    "notes": ["Blocking questions need answers before CTC generation"]
                }
            )

        # 5) If coverage_report.blocking_questions empty OR answered -> RUN_STEP_4
        if not blocking or self._all_questions_answered(blocking_questions, user_answers):
            return self._build_response(
                action=OrchestrationAction.RUN_STEP_4,
                inputs_needed={
                    "need_lexical_report": False,
                    "need_semantic_frame": False,
                    "need_coverage_report": False,
                    "need_user_answers": False
                },
                next_step_payload={
                    "semantic_frame": semantic_frame,
                    "coverage_report": coverage_report,
                    "user_answers": user_answers,
                    "context": context
                },
                status={
                    "blocking": False,
                    "score_total": coverage_report.get("coverage_report", {}).get("score_total"),
                    "notes": ["Running CTC generation with Opus model"]
                }
            )

        # 6) If CTC exists and user didn't change requirements -> DONE
        if ctc:
            return self._build_response(
                action=OrchestrationAction.DONE,
                inputs_needed={},
                status={
                    "blocking": False,
                    "score_total": coverage_report.get("coverage_report", {}).get("score_total") if coverage_report else 100,
                    "notes": ["CTC generation complete"]
                }
            )

        # Fallback: should not reach here
        return self._build_response(
            action=OrchestrationAction.ERROR,
            inputs_needed={},
            status={
                "blocking": True,
                "score_total": None,
                "notes": ["Unexpected state in orchestration logic"]
            }
        )

    def _build_response(
        self,
        action: OrchestrationAction,
        inputs_needed: Dict[str, bool],
        next_step_payload: Optional[Dict] = None,
        user_questions: Optional[List[Dict]] = None,
        status: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Build standardized orchestration response."""
        return {
            "action": action.value,
            "model_routing": {
                "step_1_model": "cheapest",
                "step_2_model": "cheap_or_mid",
                "step_3_model": "none_or_cheapest",
                "step_4_model": "best_reasoning"
            },
            "inputs_needed": inputs_needed,
            "next_step_payload": next_step_payload or {},
            "user_questions": user_questions or [],
            "status": status or {}
        }

    def _semantic_affected_by_answers(self, semantic_frame: Dict, user_answers: Dict) -> bool:
        """
        Check if user answers affect slots in semantic frame.

        Returns True if answers reference slots in the semantic frame.
        """
        # Check if any question IDs in user_answers correspond to open_questions
        open_questions = semantic_frame.get("semantic_frame", {}).get("open_questions", [])
        answered_slots = {q["slot"] for q in open_questions if q.get("slot") in user_answers}

        return len(answered_slots) > 0

    def _all_questions_answered(self, blocking_questions: List[Dict], user_answers: Dict) -> bool:
        """
        Check if all blocking questions have been answered.

        Args:
            blocking_questions: List of blocking questions from coverage report
            user_answers: Dictionary of question_id -> answer

        Returns:
            True if all blocking questions have answers
        """
        if not blocking_questions:
            return True

        for question in blocking_questions:
            question_id = question.get("question_id")
            if question_id not in user_answers or not user_answers[question_id]:
                # Question not answered or answer is empty
                return False

        return True

    def package_user_questions(self, coverage_report: Dict) -> List[Dict[str, Any]]:
        """
        Package blocking questions for user using User_Question_Packager logic.

        Args:
            coverage_report: Coverage report with blocking_questions

        Returns:
            List of questions formatted for user
        """
        blocking_questions = coverage_report.get("coverage_report", {}).get("blocking_questions", [])

        # Format per User_Question_Packager.md
        questions_to_user = []
        for q in blocking_questions:
            questions_to_user.append({
                "question_id": q.get("question_id"),
                "question": q.get("question"),
                "default_if_blank": q.get("default_if_blank", ""),
                "answer_format": q.get("answer_format", "text")
            })

        return questions_to_user

    def validate_user_answers(
        self,
        user_answers: Dict[str, str],
        blocking_questions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Validate user answers against blocking questions.

        Args:
            user_answers: Dictionary of question_id -> answer
            blocking_questions: List of blocking questions

        Returns:
            Validation result with is_valid and missing_answers
        """
        missing_answers = []

        for question in blocking_questions:
            question_id = question.get("question_id")
            answer = user_answers.get(question_id, "").strip()

            # Check if answer is missing and no default exists
            if not answer:
                default = question.get("default_if_blank", "").strip()
                if not default:
                    missing_answers.append({
                        "question_id": question_id,
                        "question": question.get("question"),
                        "reason": "No answer provided and no default available"
                    })

        return {
            "is_valid": len(missing_answers) == 0,
            "missing_answers": missing_answers
        }

    def __repr__(self) -> str:
        return "PipelineOrchestrator(4-step workflow with cost optimization)"
