"""
Test Pipeline

Tests the 4-step GANDALF pipeline with multi-model optimization.

Tests:
1. Model router selection logic
2. Individual pipeline steps
3. Full pipeline orchestration
4. Cost estimation
"""

import sys
import json
import logging
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, '/opt/apps/gandlf/multi-agent')

from pipeline_model_router import PipelineModelRouter, PipelineStep, ClaudeModel
from pipeline_orchestrator import PipelineOrchestrator, OrchestrationAction

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_model_router():
    """Test model router selection logic."""
    logger.info("=" * 60)
    logger.info("TEST 1: Model Router Selection Logic")
    logger.info("=" * 60)

    router = PipelineModelRouter()

    # Test each step gets the correct model
    tests = [
        ("lexical_analysis", ClaudeModel.HAIKU),
        ("semantic_analysis", ClaudeModel.SONNET),
        ("coverage_scoring", ClaudeModel.HAIKU),
        ("ctc_generation", ClaudeModel.OPUS),
    ]

    all_passed = True
    for step, expected_model in tests:
        selected_model = router.select_model_for_step(step)
        passed = selected_model == expected_model

        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {step} -> {selected_model.value} (expected: {expected_model.value})")

        if not passed:
            all_passed = False

    logger.info("")
    logger.info(f"Model Router Test: {'PASSED' if all_passed else 'FAILED'}")
    logger.info("")
    return all_passed


def test_pipeline_plan():
    """Test getting the full pipeline plan."""
    logger.info("=" * 60)
    logger.info("TEST 2: Pipeline Plan")
    logger.info("=" * 60)

    router = PipelineModelRouter()
    plan = router.get_pipeline_plan()

    logger.info("Pipeline Model Plan:")
    for step, model in plan.items():
        logger.info(f"  {step}: {model.value}")

    logger.info("")
    return True


def test_cost_estimation():
    """Test cost estimation for pipeline."""
    logger.info("=" * 60)
    logger.info("TEST 3: Cost Estimation")
    logger.info("=" * 60)

    router = PipelineModelRouter()

    # Simulate token counts for each step
    tokens_per_step = {
        "lexical": {"input": 500, "output": 200},     # Haiku
        "semantic": {"input": 800, "output": 600},    # Sonnet
        "coverage": {"input": 600, "output": 300},    # Haiku
        "ctc": {"input": 1000, "output": 1500},       # Opus
    }

    cost_estimate = router.estimate_pipeline_cost(tokens_per_step)

    logger.info("Cost Breakdown:")
    for step_name, details in cost_estimate["breakdown"].items():
        logger.info(f"  {step_name}:")
        logger.info(f"    Model: {details['model']}")
        logger.info(f"    Tokens: {details['tokens']}")
        logger.info(f"    Cost: ${details['cost_usd']:.6f}")

    logger.info(f"\nTotal Estimated Cost: ${cost_estimate['total_cost_usd']:.6f}")
    logger.info("")

    # Compare with single-model approach (all Opus)
    single_model_cost = 0.0
    for step_key, tokens in tokens_per_step.items():
        single_model_cost += router.estimate_cost(
            ClaudeModel.OPUS,
            tokens["input"],
            tokens["output"]
        )

    logger.info(f"Cost if using ONLY Opus: ${single_model_cost:.6f}")
    savings = ((single_model_cost - cost_estimate['total_cost_usd']) / single_model_cost) * 100
    logger.info(f"Cost Savings: {savings:.1f}%")
    logger.info("")

    return True


def test_orchestrator_step1():
    """Test orchestrator determines Step 1 when starting."""
    logger.info("=" * 60)
    logger.info("TEST 4: Orchestrator - Initial State (Step 1)")
    logger.info("=" * 60)

    orchestrator = PipelineOrchestrator()

    decision = orchestrator.determine_next_action(
        user_message="Create a Django app with PostgreSQL",
        context={},
        prior_outputs={},
        user_answers={}
    )

    expected_action = OrchestrationAction.RUN_STEP_1.value
    actual_action = decision["action"]
    passed = actual_action == expected_action

    status = "✓ PASS" if passed else "✗ FAIL"
    logger.info(f"{status}: Action is {actual_action} (expected: {expected_action})")
    logger.info(f"Status: {json.dumps(decision['status'], indent=2)}")
    logger.info("")

    return passed


def test_orchestrator_step2():
    """Test orchestrator determines Step 2 after Step 1."""
    logger.info("=" * 60)
    logger.info("TEST 5: Orchestrator - After Step 1 (Step 2)")
    logger.info("=" * 60)

    orchestrator = PipelineOrchestrator()

    # Simulate having lexical report
    prior_outputs = {
        "lexical_report": {
            "language": "en",
            "keywords": ["django", "postgresql"],
            "intent_verbs": ["create"],
            "entities": []
        }
    }

    decision = orchestrator.determine_next_action(
        user_message="Create a Django app with PostgreSQL",
        context={},
        prior_outputs=prior_outputs,
        user_answers={}
    )

    expected_action = OrchestrationAction.RUN_STEP_2.value
    actual_action = decision["action"]
    passed = actual_action == expected_action

    status = "✓ PASS" if passed else "✗ FAIL"
    logger.info(f"{status}: Action is {actual_action} (expected: {expected_action})")
    logger.info(f"Status: {json.dumps(decision['status'], indent=2)}")
    logger.info("")

    return passed


def test_orchestrator_step3():
    """Test orchestrator determines Step 3 after Step 2."""
    logger.info("=" * 60)
    logger.info("TEST 6: Orchestrator - After Step 2 (Step 3)")
    logger.info("=" * 60)

    orchestrator = PipelineOrchestrator()

    # Simulate having lexical report and semantic frame
    prior_outputs = {
        "lexical_report": {
            "language": "en",
            "keywords": ["django", "postgresql"]
        },
        "semantic_frame": {
            "goal": "Create Django application with PostgreSQL database",
            "scope": {"in_scope": ["Django setup"], "out_of_scope": []},
            "target_environment": {"host_os": "linux"}
        }
    }

    decision = orchestrator.determine_next_action(
        user_message="Create a Django app with PostgreSQL",
        context={},
        prior_outputs=prior_outputs,
        user_answers={}
    )

    expected_action = OrchestrationAction.RUN_STEP_3.value
    actual_action = decision["action"]
    passed = actual_action == expected_action

    status = "✓ PASS" if passed else "✗ FAIL"
    logger.info(f"{status}: Action is {actual_action} (expected: {expected_action})")
    logger.info(f"Status: {json.dumps(decision['status'], indent=2)}")
    logger.info("")

    return passed


def test_orchestrator_ask_user():
    """Test orchestrator asks user when blocking questions exist."""
    logger.info("=" * 60)
    logger.info("TEST 7: Orchestrator - Blocking Questions (ASK_USER)")
    logger.info("=" * 60)

    orchestrator = PipelineOrchestrator()

    # Simulate having all prior steps with blocking questions
    prior_outputs = {
        "lexical_report": {"language": "en"},
        "semantic_frame": {"goal": "Create Django app"},
        "coverage_report": {
            "coverage_report": {
                "score_total": 65,
                "blocking": True,
                "blocking_questions": [
                    {
                        "question_id": "Q1",
                        "question": "Which Python version?",
                        "default_if_blank": "3.11",
                        "answer_format": "text"
                    }
                ]
            }
        }
    }

    decision = orchestrator.determine_next_action(
        user_message="Create a Django app",
        context={},
        prior_outputs=prior_outputs,
        user_answers={}
    )

    expected_action = OrchestrationAction.ASK_USER.value
    actual_action = decision["action"]
    passed = actual_action == expected_action

    status = "✓ PASS" if passed else "✗ FAIL"
    logger.info(f"{status}: Action is {actual_action} (expected: {expected_action})")
    logger.info(f"Questions: {len(decision['user_questions'])} question(s)")
    logger.info(f"Status: {json.dumps(decision['status'], indent=2)}")
    logger.info("")

    return passed


def test_orchestrator_step4():
    """Test orchestrator proceeds to Step 4 after questions answered."""
    logger.info("=" * 60)
    logger.info("TEST 8: Orchestrator - Questions Answered (Step 4)")
    logger.info("=" * 60)

    orchestrator = PipelineOrchestrator()

    # Simulate having all prior steps with questions answered
    prior_outputs = {
        "lexical_report": {"language": "en"},
        "semantic_frame": {"goal": "Create Django app"},
        "coverage_report": {
            "coverage_report": {
                "score_total": 95,
                "blocking": False,
                "blocking_questions": []
            }
        }
    }

    decision = orchestrator.determine_next_action(
        user_message="Create a Django app",
        context={},
        prior_outputs=prior_outputs,
        user_answers={"Q1": "3.11"}
    )

    expected_action = OrchestrationAction.RUN_STEP_4.value
    actual_action = decision["action"]
    passed = actual_action == expected_action

    status = "✓ PASS" if passed else "✗ FAIL"
    logger.info(f"{status}: Action is {actual_action} (expected: {expected_action})")
    logger.info(f"Status: {json.dumps(decision['status'], indent=2)}")
    logger.info("")

    return passed


def test_fallback():
    """Test fallback model selection."""
    logger.info("=" * 60)
    logger.info("TEST 9: Model Fallback")
    logger.info("=" * 60)

    router = PipelineModelRouter()

    fallback_tests = [
        (ClaudeModel.HAIKU, ClaudeModel.SONNET),
        (ClaudeModel.SONNET, ClaudeModel.OPUS),
        (ClaudeModel.OPUS, ClaudeModel.SONNET),
    ]

    all_passed = True
    for model, expected_fallback in fallback_tests:
        fallback = router.get_fallback_model(model)
        passed = fallback == expected_fallback

        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {model.value} -> {fallback.value} (expected: {expected_fallback.value})")

        if not passed:
            all_passed = False

    logger.info("")
    logger.info(f"Fallback Test: {'PASSED' if all_passed else 'FAILED'}")
    logger.info("")
    return all_passed


def run_all_tests():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("GANDALF MULTI-MODEL PIPELINE TESTS")
    logger.info("=" * 60)
    logger.info("")

    tests = [
        ("Model Router Selection", test_model_router),
        ("Pipeline Plan", test_pipeline_plan),
        ("Cost Estimation", test_cost_estimation),
        ("Orchestrator Step 1", test_orchestrator_step1),
        ("Orchestrator Step 2", test_orchestrator_step2),
        ("Orchestrator Step 3", test_orchestrator_step3),
        ("Orchestrator ASK_USER", test_orchestrator_ask_user),
        ("Orchestrator Step 4", test_orchestrator_step4),
        ("Model Fallback", test_fallback),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed

    for test_name, passed_flag in results:
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("")
    logger.info(f"Total: {total} tests")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info("")

    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED!")
    else:
        logger.error(f"❌ {failed} TEST(S) FAILED")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
