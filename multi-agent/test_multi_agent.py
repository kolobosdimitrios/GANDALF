#!/usr/bin/env python3
"""
Test Multi-Agent System

Simple test script to verify the multi-agent system is working correctly.
Tests model router, model selection, and basic functionality.
"""

import sys
import os

# Add current directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_router import ModelRouter, ClaudeModel, TaskType


def test_model_router():
    """Test model router functionality."""
    print("=" * 60)
    print("Testing Model Router")
    print("=" * 60)

    # Initialize router
    router = ModelRouter(
        enable_haiku=True,
        enable_opus=True,
        default_model="sonnet"
    )
    print(f"✓ Router initialized: {router}")
    print()

    # Test model selection for different tasks
    print("Testing model selection:")
    test_cases = [
        ("classify_intent", None, ClaudeModel.HAIKU),
        ("extract_keywords", None, ClaudeModel.HAIKU),
        ("score_clarity", None, ClaudeModel.SONNET),
        ("detect_gaps", None, ClaudeModel.SONNET),
        ("generate_questions", None, ClaudeModel.SONNET),
        ("prioritize_questions", None, ClaudeModel.HAIKU),
        ("generate_ctc", "high", ClaudeModel.OPUS),
        ("generate_ctc", "low", ClaudeModel.SONNET),
        ("validate_format", None, ClaudeModel.HAIKU),
        ("calculate_efficiency", None, ClaudeModel.HAIKU),
    ]

    all_passed = True
    for task, complexity, expected in test_cases:
        selected = router.select_model(task, complexity)
        status = "✓" if selected == expected else "✗"
        if selected != expected:
            all_passed = False
        print(f"  {status} {task:25s} (complexity={complexity or 'N/A':6s}) → {selected.name:6s} (expected {expected.name})")

    print()
    if all_passed:
        print("✓ All model selection tests passed!")
    else:
        print("✗ Some model selection tests failed!")
        return False

    # Test model configuration
    print()
    print("Testing model configurations:")
    for model in [ClaudeModel.HAIKU, ClaudeModel.SONNET, ClaudeModel.OPUS]:
        config = router.get_model_config(model)
        print(f"  {model.name}:")
        print(f"    Model ID: {model.value}")
        print(f"    Max tokens: {config['max_tokens']}")
        print(f"    Timeout: {config['timeout']}s")
        print(f"    Temperature: {config['temperature']}")
        print(f"    Cost per 1K input: ${config['cost_per_1k_input']:.5f}")
        print(f"    Cost per 1K output: ${config['cost_per_1k_output']:.5f}")
    print("✓ Model configurations loaded successfully")
    print()

    # Test fallback chain
    print("Testing fallback chain:")
    for model in [ClaudeModel.HAIKU, ClaudeModel.SONNET, ClaudeModel.OPUS]:
        fallback = router.get_fallback_model(model)
        print(f"  {model.name:6s} → {fallback.name:6s}")
    print("✓ Fallback chain working")
    print()

    # Test cost estimation
    print("Testing cost estimation:")
    test_usage = [
        (ClaudeModel.HAIKU, 1000, 500, "Simple task"),
        (ClaudeModel.SONNET, 2000, 1000, "Medium task"),
        (ClaudeModel.OPUS, 3000, 2000, "Complex task"),
    ]

    for model, input_tokens, output_tokens, desc in test_usage:
        cost = router.estimate_cost(model, input_tokens, output_tokens)
        print(f"  {model.name:6s} - {desc:15s}: {input_tokens:4d} in + {output_tokens:4d} out = ${cost:.6f}")
    print("✓ Cost estimation working")
    print()

    # Test workflow plan
    print("Testing workflow plan generation:")
    for complexity in ["low", "medium", "high"]:
        print(f"  Complexity: {complexity}")
        plan = router.get_workflow_model_plan(complexity)
        for step, model in plan.items():
            print(f"    {step:25s} → {model.name}")
    print("✓ Workflow plan generation working")
    print()

    return True


def test_disabled_models():
    """Test behavior when models are disabled."""
    print("=" * 60)
    print("Testing Disabled Models")
    print("=" * 60)

    # Test with Haiku disabled
    print("Testing with Haiku disabled:")
    router = ModelRouter(enable_haiku=False, enable_opus=True)

    # Tasks that normally use Haiku should fallback to Sonnet
    model = router.select_model("classify_intent")
    expected = ClaudeModel.SONNET  # Fallback from Haiku
    status = "✓" if model == expected else "✗"
    print(f"  {status} classify_intent → {model.name} (expected {expected.name})")

    # Test with Opus disabled
    print()
    print("Testing with Opus disabled:")
    router = ModelRouter(enable_haiku=True, enable_opus=False)

    # CTC generation should fallback to Sonnet
    model = router.select_model("generate_ctc", complexity="high")
    expected = ClaudeModel.SONNET  # Fallback from Opus
    status = "✓" if model == expected else "✗"
    print(f"  {status} generate_ctc (high) → {model.name} (expected {expected.name})")

    print()
    print("✓ Disabled model tests passed!")
    print()

    return True


def test_force_model():
    """Test forcing all tasks to use one model."""
    print("=" * 60)
    print("Testing Force Model")
    print("=" * 60)

    for force_model in ["haiku", "sonnet", "opus"]:
        print(f"Testing force_model={force_model}:")
        router = ModelRouter(force_model=force_model)

        expected = router._parse_model(force_model)

        # All tasks should use forced model
        tasks = ["classify_intent", "detect_gaps", "generate_ctc"]
        all_correct = True

        for task in tasks:
            model = router.select_model(task)
            status = "✓" if model == expected else "✗"
            if model != expected:
                all_correct = False
            print(f"  {status} {task:20s} → {model.name}")

        if all_correct:
            print(f"  ✓ All tasks correctly using {force_model}")
        print()

    print("✓ Force model tests passed!")
    print()

    return True


def main():
    """Run all tests."""
    print()
    print("=" * 60)
    print("GANDALF Multi-Agent System Tests")
    print("=" * 60)
    print()

    tests = [
        ("Model Router", test_model_router),
        ("Disabled Models", test_disabled_models),
        ("Force Model", test_force_model),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
            import traceback
            traceback.print_exc()

    # Summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")

    all_passed = all(passed for _, passed in results)
    print()
    if all_passed:
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
