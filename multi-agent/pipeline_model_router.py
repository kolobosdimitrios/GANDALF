"""
Pipeline Model Router

Routes the 4-step GANDALF pipeline to optimal Claude models:
1. Lexical Analysis -> Haiku (cheapest)
2. Semantic Analysis -> Sonnet (cheap/medium)
3. Coverage Scoring -> Haiku or algorithmic (cheapest)
4. CTC Generation -> Opus (best reasoning)

This follows the Orchestrator.md cost optimization strategy.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ClaudeModel(Enum):
    """Available Claude models"""
    HAIKU = "claude-3-5-haiku-20241022"
    SONNET = "claude-3-5-sonnet-20241022"
    OPUS = "claude-opus-4-5-20250929"


class PipelineStep(Enum):
    """4-step GANDALF pipeline"""
    LEXICAL_ANALYSIS = "lexical_analysis"      # Step 1
    SEMANTIC_ANALYSIS = "semantic_analysis"    # Step 2
    COVERAGE_SCORING = "coverage_scoring"      # Step 3
    CTC_GENERATION = "ctc_generation"          # Step 4


class PipelineModelRouter:
    """
    Routes pipeline steps to optimal Claude models.

    Cost optimization strategy (from Orchestrator.md):
    - Step 1 (Lexical): cheapest model (Haiku)
    - Step 2 (Semantic): cheap/medium model (Sonnet)
    - Step 3 (Coverage): algorithmic if possible; otherwise cheapest (Haiku)
    - Step 4 (CTC): best reasoning model ONLY after questions resolved (Opus)
    """

    # Routing rules per Orchestrator.md
    ROUTING_RULES = {
        PipelineStep.LEXICAL_ANALYSIS: ClaudeModel.HAIKU,
        PipelineStep.SEMANTIC_ANALYSIS: ClaudeModel.SONNET,
        PipelineStep.COVERAGE_SCORING: ClaudeModel.HAIKU,
        PipelineStep.CTC_GENERATION: ClaudeModel.OPUS,
    }

    # Fallback chain
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
            "temperature": 0.2,  # Lower for structured extraction
            "cost_per_1k_input": 0.00025,
            "cost_per_1k_output": 0.00125,
        },
        ClaudeModel.SONNET: {
            "max_tokens": 4000,
            "timeout": 30,
            "temperature": 0.4,  # Medium for analysis
            "cost_per_1k_input": 0.003,
            "cost_per_1k_output": 0.015,
        },
        ClaudeModel.OPUS: {
            "max_tokens": 8000,
            "timeout": 60,
            "temperature": 0.6,  # Higher for creative CTC generation
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
        Initialize the pipeline model router.

        Args:
            enable_haiku: Allow using Haiku for fast tasks
            enable_opus: Allow using Opus for CTC generation
            force_model: Force all steps to use this model (for testing)
            default_model: Default model if routing fails
        """
        self.enable_haiku = enable_haiku
        self.enable_opus = enable_opus
        self.force_model = force_model
        self.default_model = self._parse_model(default_model)

        logger.info("PipelineModelRouter initialized:")
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

    def select_model_for_step(
        self,
        step: str,
        complexity: Optional[str] = None,
        prefer_model: Optional[str] = None
    ) -> ClaudeModel:
        """
        Select the appropriate model for a pipeline step.

        Args:
            step: Pipeline step (use PipelineStep enum values)
            complexity: Task complexity (not used for step 1-3, only for step 4)
            prefer_model: User preference (optional override)

        Returns:
            ClaudeModel to use for this step
        """
        # If force_model is set, always use it (for testing)
        if self.force_model:
            logger.info(f"Force model active: {self.force_model}")
            return self._parse_model(self.force_model)

        # If user specifies preference, respect it
        if prefer_model:
            logger.info(f"User preference: {prefer_model}")
            return self._parse_model(prefer_model)

        # Parse step
        try:
            step_enum = PipelineStep(step)
        except ValueError:
            logger.warning(f"Unknown step: {step}, using default model")
            return self.default_model

        # Get model from routing rules
        selected_model = self.ROUTING_RULES.get(step_enum, ClaudeModel.SONNET)

        # Check if selected model is enabled
        if selected_model == ClaudeModel.HAIKU and not self.enable_haiku:
            logger.info("Haiku disabled, using fallback")
            selected_model = self.FALLBACK_CHAIN[ClaudeModel.HAIKU]

        if selected_model == ClaudeModel.OPUS and not self.enable_opus:
            logger.info("Opus disabled, using fallback")
            selected_model = self.FALLBACK_CHAIN[ClaudeModel.OPUS]

        logger.info(f"Selected model for {step}: {selected_model.value}")
        return selected_model

    def get_model_config(self, model: ClaudeModel) -> Dict[str, Any]:
        """
        Get configuration for a specific model.

        Args:
            model: ClaudeModel enum

        Returns:
            Dictionary with model configuration
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

    def get_pipeline_plan(self) -> Dict[str, ClaudeModel]:
        """
        Get the complete model plan for the GANDALF pipeline.

        Returns:
            Dictionary mapping pipeline steps to models
        """
        plan = {
            "step_1_lexical": self.select_model_for_step("lexical_analysis"),
            "step_2_semantic": self.select_model_for_step("semantic_analysis"),
            "step_3_coverage": self.select_model_for_step("coverage_scoring"),
            "step_4_ctc": self.select_model_for_step("ctc_generation"),
        }

        logger.info("Pipeline model plan:")
        for step, model in plan.items():
            logger.info(f"  {step}: {model.value}")

        return plan

    def estimate_pipeline_cost(
        self,
        tokens_per_step: Dict[str, Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Estimate total cost for a complete pipeline run.

        Args:
            tokens_per_step: Dict mapping step name to {"input": int, "output": int}

        Returns:
            Cost breakdown by step and total
        """
        plan = self.get_pipeline_plan()
        cost_breakdown = {}
        total_cost = 0.0

        for step_name, model in plan.items():
            step_key = step_name.replace("step_", "").split("_", 1)[1]  # Extract step name
            tokens = tokens_per_step.get(step_key, {"input": 0, "output": 0})

            cost = self.estimate_cost(
                model,
                tokens["input"],
                tokens["output"]
            )

            cost_breakdown[step_name] = {
                "model": model.value,
                "tokens": tokens,
                "cost_usd": cost
            }
            total_cost += cost

        return {
            "breakdown": cost_breakdown,
            "total_cost_usd": round(total_cost, 6)
        }

    def __repr__(self) -> str:
        return (
            f"PipelineModelRouter(haiku={self.enable_haiku}, opus={self.enable_opus}, "
            f"force={self.force_model}, default={self.default_model.value})"
        )
