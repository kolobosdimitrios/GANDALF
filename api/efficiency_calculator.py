"""
Efficiency Calculator Module
Calculates conversion efficiency from user intent to CTC
"""
import json
from typing import Dict, Tuple


class EfficiencyCalculator:
    """
    Calculates efficiency percentage for intent → CTC conversion
    As defined in GANDALF spec:
    Efficiency % = max(0, min(100, 100 * (1 - (CTC_chars / max(1, user_chars)))))
    """

    @staticmethod
    def calculate_character_efficiency(user_prompt: str, ctc_data: Dict) -> float:
        """
        Calculate efficiency based on character count

        Args:
            user_prompt: Original user input
            ctc_data: Generated CTC dictionary

        Returns:
            Efficiency percentage (0-100)
        """
        user_chars = len(user_prompt)

        # Convert CTC to comparable text format (just the core CTC, not metadata)
        ctc_text = EfficiencyCalculator._ctc_to_text(ctc_data)
        ctc_chars = len(ctc_text)

        # Apply formula
        efficiency = 100 * (1 - (ctc_chars / max(1, user_chars)))

        # Clamp to 0-100 range
        return max(0.0, min(100.0, efficiency))

    @staticmethod
    def calculate_token_efficiency(
        user_prompt_tokens: int,
        ctc_tokens: int
    ) -> float:
        """
        Calculate efficiency based on token count (optional)

        Args:
            user_prompt_tokens: Token count of user input
            ctc_tokens: Token count of generated CTC

        Returns:
            Efficiency percentage (0-100)
        """
        if user_prompt_tokens <= 0:
            return 0.0

        # Apply formula
        efficiency = 100 * (1 - (ctc_tokens / user_prompt_tokens))

        # Clamp to 0-100 range
        return max(0.0, min(100.0, efficiency))

    @staticmethod
    def _ctc_to_text(ctc_data: Dict) -> str:
        """
        Convert CTC to text representation for character counting
        Only counts the actual CTC content, not metadata/telemetry

        Args:
            ctc_data: CTC dictionary

        Returns:
            Text representation of CTC
        """
        if 'ctc' not in ctc_data:
            # If it's a clarification request, count the clarifications
            return EfficiencyCalculator._clarifications_to_text(ctc_data)

        ctc = ctc_data['ctc']
        parts = []

        # Title
        if 'title' in ctc:
            parts.append(f"# Task: {ctc['title']}")

        # Context
        if 'context' in ctc:
            parts.append("\n## Context")
            for item in ctc['context']:
                parts.append(f"- {item}")

        # Definition of Done
        if 'definition_of_done' in ctc:
            parts.append("\n## Definition of Done")
            for item in ctc['definition_of_done']:
                parts.append(f"- [ ] {item}")

        # Constraints
        if 'constraints' in ctc and ctc['constraints']:
            parts.append("\n## Constraints")
            for item in ctc['constraints']:
                parts.append(f"- {item}")

        # Deliverables
        if 'deliverables' in ctc:
            parts.append("\n## Deliverables")
            for item in ctc['deliverables']:
                parts.append(f"- {item}")

        return '\n'.join(parts)

    @staticmethod
    def _clarifications_to_text(ctc_data: Dict) -> str:
        """Convert clarification request to text for counting"""
        if 'clarifications' not in ctc_data:
            return ""

        clarifications = ctc_data['clarifications']
        if 'asked' not in clarifications:
            return ""

        parts = ["Before proceeding, clarification is needed:"]

        for i, clarification in enumerate(clarifications['asked'], 1):
            parts.append(f"\n{i}) {clarification['question']}")
            for option in clarification['options']:
                parts.append(f"   - {option}")

        return '\n'.join(parts)

    @staticmethod
    def calculate_with_metadata(user_prompt: str, ctc_data: Dict) -> Dict[str, float]:
        """
        Calculate efficiency and return with metadata

        Args:
            user_prompt: Original user input
            ctc_data: Generated CTC

        Returns:
            Dictionary with efficiency metrics and metadata
        """
        char_efficiency = EfficiencyCalculator.calculate_character_efficiency(
            user_prompt,
            ctc_data
        )

        user_chars = len(user_prompt)
        ctc_text = EfficiencyCalculator._ctc_to_text(ctc_data)
        ctc_chars = len(ctc_text)

        return {
            "efficiency_percentage": round(char_efficiency, 2),
            "user_chars": user_chars,
            "ctc_chars": ctc_chars,
            "compression_ratio": round(ctc_chars / max(1, user_chars), 2)
        }
