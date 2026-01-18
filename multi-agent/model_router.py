"""
Model Router

Determines which Claude model to use for each task based on complexity and cost optimization.

Model Selection Strategy:
- Haiku: Fast, cheap - for classification, validation, formatting
- Sonnet: Balanced - for analysis, gap detection, question generation
- Opus: Powerful, expensive - for complex CTC generation and reasoning
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ClaudeModel(Enum):
    """Available Claude models"""
    HAIKU = "claude-3-5-haiku-20241022"
    SONNET = "claude-3-5-sonnet-20241022"
    OPUS = "claude-opus-4-5-20251101"


class TaskType(Enum):
    """Types of tasks in GANDALF workflow"""
    CLASSIFY_INTENT = "classify_intent"
    EXTRACT_KEYWORDS = "extract_keywords"
    SCORE_CLARITY = "score_clarity"
    DETECT_GAPS = "detect_gaps"
    GENERATE_QUESTIONS = "generate_questions"
    PRIORITIZE_QUESTIONS = "prioritize_questions"
    GENERATE_CTC = "generate_ctc"
    VALIDATE_FORMAT = "validate_format"
    CALCULATE_EFFICIENCY = "calculate_efficiency"


class ComplexityLevel(Enum):
    """Complexity levels for tasks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModelRouter:
    """
    Routes tasks to the appropriate Claude model based on task type and complexity.

    Purpose:
    - Optimize cost by using cheaper models for simple tasks
    - Ensure quality by using powerful models for complex tasks
    - Provide flexibility for override and fallback
    """

    # Model routing rules: task_type -> model
    ROUTING_RULES = {
        TaskType.CLASSIFY_INTENT: ClaudeModel.HAIKU,
        TaskType.EXTRACT_KEYWORDS: ClaudeModel.HAIKU,
        TaskType.SCORE_CLARITY: ClaudeModel.SONNET,
        TaskType.DETECT_GAPS: ClaudeModel.SONNET,
        TaskType.GENERATE_QUESTIONS: ClaudeModel.SONNET,
        TaskType.PRIORITIZE_QUESTIONS: ClaudeModel.HAIKU,
        TaskType.GENERATE_CTC: ClaudeModel.OPUS,
        TaskType.VALIDATE_FORMAT: ClaudeModel.HAIKU,
        TaskType.CALCULATE_EFFICIENCY: ClaudeModel.HAIKU,
    }

    # Fallback chain: if primary unavailable, use fallback
    FALLBACK_CHAIN = {
        ClaudeModel.HAIKU: ClaudeModel.SONNET,
        ClaudeModel.SONNET: ClaudeModel.OPUS,
        ClaudeModel.OPUS: ClaudeModel.SONNET,
    }

    # Model configurations
    MODEL_CONFIGS = {
        ClaudeModel.HAIKU: {
            "max_tokens": 2000,
            "timeout": 10,
            "temperature": 0.3,
            "cost_per_1k_input": 0.00025,  # USD
            "cost_per_1k_output": 0.00125,
        },
        ClaudeModel.SONNET: {
            "max_tokens": 4000,
            "timeout": 30,
            "temperature": 0.5,
            "cost_per_1k_input": 0.003,
            "cost_per_1k_output": 0.015,
        },
        ClaudeModel.OPUS: {
            "max_tokens": 8000,
            "timeout": 60,
            "temperature": 0.7,
            "cost_per_1k_input": 0.015,
            "cost_per_1k_output": 0.075,
        },
    }

    def __init__(
        self,
        enable_haiku: bool = True,
        enable_opus: bool = True,
        force_model: Optional[str] = None,
        default_model: str = "sonnet"
    ):
        """
        Initialize the model router.

        Args:
            enable_haiku: Allow using Haiku for fast tasks
            enable_opus: Allow using Opus for complex tasks
            force_model: Force all tasks to use this model (for testing)
            default_model: Default model if routing fails (haiku|sonnet|opus)
        """
        self.enable_haiku = enable_haiku
        self.enable_opus = enable_opus
        self.force_model = force_model
        self.default_model = self._parse_model(default_model)

        logger.info(f"ModelRouter initialized:")
        logger.info(f"  Haiku enabled: {enable_haiku}")
        logger.info(f"  Opus enabled: {enable_opus}")
        logger.info(f"  Force model: {force_model or 'None'}")
        logger.info(f"  Default model: {default_model}")

    def _parse_model(self, model_str: str) -> ClaudeModel:
        """Parse model string to ClaudeModel enum."""
        model_map = {
            "haiku": ClaudeModel.HAIKU,
            "sonnet": ClaudeModel.SONNET,
            "opus": ClaudeModel.OPUS,
        }
        return model_map.get(model_str.lower(), ClaudeModel.SONNET)

    def select_model(
        self,
        task_type: str,
        complexity: Optional[str] = None,
        prefer_model: Optional[str] = None
    ) -> ClaudeModel:
        """
        Select the appropriate model for a task.

        Args:
            task_type: Type of task (use TaskType enum values)
            complexity: Task complexity (low|medium|high)
            prefer_model: User preference for model (optional override)

        Returns:
            ClaudeModel to use for this task
        """
        # If force_model is set, always use it (for testing)
        if self.force_model:
            logger.info(f"Force model active: {self.force_model}")
            return self._parse_model(self.force_model)

        # If user specifies preference, respect it
        if prefer_model:
            logger.info(f"User preference: {prefer_model}")
            return self._parse_model(prefer_model)

        # Parse task type
        try:
            task_enum = TaskType(task_type)
        except ValueError:
            logger.warning(f"Unknown task type: {task_type}, using default model")
            return self.default_model

        # Get model from routing rules
        selected_model = self.ROUTING_RULES.get(task_enum, ClaudeModel.SONNET)

        # Check if selected model is enabled
        if selected_model == ClaudeModel.HAIKU and not self.enable_haiku:
            logger.info("Haiku disabled, using fallback")
            selected_model = self.FALLBACK_CHAIN[ClaudeModel.HAIKU]

        if selected_model == ClaudeModel.OPUS and not self.enable_opus:
            logger.info("Opus disabled, using fallback")
            selected_model = self.FALLBACK_CHAIN[ClaudeModel.OPUS]

        # For CTC generation, consider complexity
        if task_enum == TaskType.GENERATE_CTC and complexity:
            complexity_enum = ComplexityLevel(complexity) if isinstance(complexity, str) else complexity

            if complexity_enum == ComplexityLevel.LOW:
                # Simple CTCs can use Sonnet
                if self.enable_opus:
                    selected_model = ClaudeModel.SONNET
                    logger.info("Low complexity CTC, using Sonnet instead of Opus")

            elif complexity_enum == ComplexityLevel.HIGH:
                # Complex CTCs need Opus
                if self.enable_opus:
                    selected_model = ClaudeModel.OPUS
                    logger.info("High complexity CTC, using Opus")
                else:
                    selected_model = ClaudeModel.SONNET
                    logger.info("Opus disabled, using Sonnet for complex CTC")

        logger.info(f"Selected model for {task_type}: {selected_model.value}")
        return selected_model

    def get_model_config(self, model: ClaudeModel) -> Dict[str, Any]:
        """
        Get configuration for a specific model.

        Args:
            model: ClaudeModel enum

        Returns:
            Dictionary with model configuration (max_tokens, timeout, etc.)
        """
        return self.MODEL_CONFIGS[model].copy()

    def get_fallback_model(self, model: ClaudeModel) -> ClaudeModel:
        """
        Get fallback model if primary is unavailable.

        Args:
            model: Primary model that failed

        Returns:
            Fallback model to try
        """
        fallback = self.FALLBACK_CHAIN.get(model, ClaudeModel.SONNET)
        logger.info(f"Fallback for {model.value}: {fallback.value}")
        return fallback

    def estimate_cost(
        self,
        model: ClaudeModel,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Estimate cost for a request.

        Args:
            model: Model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        config = self.MODEL_CONFIGS[model]
        input_cost = (input_tokens / 1000) * config["cost_per_1k_input"]
        output_cost = (output_tokens / 1000) * config["cost_per_1k_output"]
        total_cost = input_cost + output_cost

        logger.debug(f"Cost estimate for {model.value}:")
        logger.debug(f"  Input: {input_tokens} tokens = ${input_cost:.6f}")
        logger.debug(f"  Output: {output_tokens} tokens = ${output_cost:.6f}")
        logger.debug(f"  Total: ${total_cost:.6f}")

        return total_cost

    def get_workflow_model_plan(self, intent_complexity: str = "medium") -> Dict[str, ClaudeModel]:
        """
        Get the complete model plan for a GANDALF workflow.

        Args:
            intent_complexity: Complexity of the user intent (low|medium|high)

        Returns:
            Dictionary mapping workflow steps to models
        """
        complexity_enum = ComplexityLevel(intent_complexity)

        plan = {
            "classify_intent": self.select_model("classify_intent"),
            "extract_keywords": self.select_model("extract_keywords"),
            "score_clarity": self.select_model("score_clarity"),
            "detect_gaps": self.select_model("detect_gaps"),
            "generate_questions": self.select_model("generate_questions"),
            "prioritize_questions": self.select_model("prioritize_questions"),
            "generate_ctc": self.select_model("generate_ctc", complexity=intent_complexity),
            "validate_format": self.select_model("validate_format"),
            "calculate_efficiency": self.select_model("calculate_efficiency"),
        }

        logger.info(f"Workflow model plan (complexity={intent_complexity}):")
        for step, model in plan.items():
            logger.info(f"  {step}: {model.value}")

        return plan

    def __repr__(self) -> str:
        return (
            f"ModelRouter(haiku={self.enable_haiku}, opus={self.enable_opus}, "
            f"force={self.force_model}, default={self.default_model.value})"
        )
