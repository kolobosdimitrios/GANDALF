"""
Intent Analyzer Module
Classifies user intents and extracts key information
"""
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Classification of user intent types"""
    SOFTWARE_FEATURE = "software_feature"
    BUG_REPORT = "bug_report"
    BUSINESS_NEED = "business_need"
    NON_TECHNICAL = "non_technical"
    CONFIGURATION = "configuration"
    ANALYSIS = "analysis"


class IntentClarity(Enum):
    """How clear/specific the user intent is"""
    CLEAR = "clear"           # Can proceed immediately
    VAGUE = "vague"           # Needs clarification
    INCOMPLETE = "incomplete"  # Missing critical info


@dataclass
class IntentAnalysis:
    """Result of analyzing a user intent"""
    intent_type: IntentType
    clarity: IntentClarity
    action_verb: Optional[str]
    target_object: Optional[str]
    has_scope: bool
    has_constraints: bool
    has_success_criteria: bool
    complexity: int  # 1-5 scale
    confidence: float  # 0.0-1.0


class IntentAnalyzer:
    """
    Analyzes user prompts to extract intent, detect gaps, and classify clarity
    """

    # Keywords for intent classification
    SOFTWARE_KEYWORDS = [
        'add', 'create', 'implement', 'build', 'develop', 'code',
        'function', 'feature', 'endpoint', 'api', 'database', 'ui',
        'button', 'form', 'page', 'component', 'service', 'module'
    ]

    BUG_KEYWORDS = [
        'fix', 'bug', 'error', 'broken', 'not working', 'fails', 'crash',
        'issue', 'problem', 'doesn\'t work', 'incorrect', '500', '404'
    ]

    BUSINESS_KEYWORDS = [
        'improve', 'increase', 'reduce', 'optimize', 'better', 'more',
        'revenue', 'users', 'retention', 'conversion', 'growth', 'metrics'
    ]

    VAGUE_VERBS = [
        'improve', 'optimize', 'handle', 'manage', 'process', 'deal with',
        'make better', 'enhance', 'upgrade', 'modernize'
    ]

    CLEAR_VERBS = [
        'add', 'remove', 'create', 'delete', 'update', 'fix', 'implement',
        'configure', 'set up', 'install', 'deploy', 'test', 'validate',
        'export', 'upload', 'download', 'save', 'load', 'import'
    ]

    def analyze(self, user_prompt: str) -> IntentAnalysis:
        """
        Analyze user prompt and classify intent

        Args:
            user_prompt: Raw user input

        Returns:
            IntentAnalysis with classification results
        """
        prompt_lower = user_prompt.lower()

        # Classify intent type
        intent_type = self._classify_type(prompt_lower)

        # Extract action and target
        action_verb, target_object = self._extract_action_target(user_prompt)

        # Check for key elements
        has_scope = self._has_scope(user_prompt)
        has_constraints = self._has_constraints(user_prompt)
        has_success_criteria = self._has_success_criteria(user_prompt)

        # Determine clarity
        clarity = self._determine_clarity(
            prompt_lower,
            action_verb,
            target_object,
            has_scope
        )

        # Calculate complexity (1-5)
        complexity = self._estimate_complexity(user_prompt, intent_type)

        # Calculate confidence
        confidence = self._calculate_confidence(
            action_verb,
            target_object,
            clarity,
            intent_type
        )

        return IntentAnalysis(
            intent_type=intent_type,
            clarity=clarity,
            action_verb=action_verb,
            target_object=target_object,
            has_scope=has_scope,
            has_constraints=has_constraints,
            has_success_criteria=has_success_criteria,
            complexity=complexity,
            confidence=confidence
        )

    def _classify_type(self, prompt_lower: str) -> IntentType:
        """Classify the type of user intent"""
        # Count keyword matches
        software_score = sum(1 for kw in self.SOFTWARE_KEYWORDS if kw in prompt_lower)
        bug_score = sum(1 for kw in self.BUG_KEYWORDS if kw in prompt_lower)
        business_score = sum(1 for kw in self.BUSINESS_KEYWORDS if kw in prompt_lower)

        # Bug reports have highest priority
        if bug_score > 0:
            return IntentType.BUG_REPORT

        # Software features
        if software_score > business_score:
            return IntentType.SOFTWARE_FEATURE

        # Business needs (often vague)
        if business_score > 0:
            return IntentType.BUSINESS_NEED

        # Check for non-technical requests
        non_tech_patterns = [
            'write', 'draft', 'create.*document', 'create.*email',
            'summarize', 'list', 'policy', 'checklist', 'note', 'schedule'
        ]
        if any(re.search(pattern, prompt_lower) for pattern in non_tech_patterns):
            # But exclude software-related writing
            if software_score == 0:
                return IntentType.NON_TECHNICAL

        # Default to software feature
        return IntentType.SOFTWARE_FEATURE

    def _extract_action_target(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract the main action verb and target object"""
        prompt_lower = prompt.lower()
        words = prompt.split()

        action = None
        target = None

        # Check for multi-word verbs first (e.g., "set up")
        multi_word_verbs = ['set up', 'make better', 'deal with']
        for verb in multi_word_verbs:
            if verb in prompt_lower:
                action = verb
                # Get words after the multi-word verb
                verb_idx = prompt_lower.index(verb) + len(verb)
                remaining = prompt[verb_idx:].strip()
                target_words = remaining.split()[:3]
                target = ' '.join(target_words) if target_words else None
                return action, target

        # Find single-word action verb
        for i, word in enumerate(words[:5]):  # Check first 5 words
            word_lower = word.lower().strip('.,!?')
            if word_lower in self.CLEAR_VERBS or word_lower in self.VAGUE_VERBS:
                action = word_lower
                # Get next 2-3 words as potential target
                target_words = words[i + 1:i + 4]
                target = ' '.join(target_words) if target_words else None
                break

        # For bug reports without explicit verbs, infer "fix" as action
        if not action:
            bug_indicators = ['error', '500', '404', 'fails', 'broken', 'not working', 'doesn\'t', 'nothing']
            if any(indicator in prompt_lower for indicator in bug_indicators):
                action = 'fix'
                # Target is the problem description
                target_words = words[:4]
                target = ' '.join(target_words)

        return action, target

    def _has_scope(self, prompt: str) -> bool:
        """Check if prompt defines clear scope"""
        scope_indicators = [
            'in', 'on', 'to', 'for', 'within',
            'page', 'section', 'app', 'feature', 'module'
        ]
        return any(indicator in prompt.lower() for indicator in scope_indicators)

    def _has_constraints(self, prompt: str) -> bool:
        """Check if prompt specifies constraints"""
        constraint_indicators = [
            'without', 'don\'t', 'only', 'must', 'should',
            'avoid', 'exclude', 'no', 'not'
        ]
        return any(indicator in prompt.lower() for indicator in constraint_indicators)

    def _has_success_criteria(self, prompt: str) -> bool:
        """Check if prompt includes success criteria"""
        criteria_indicators = [
            'when', 'should', 'must', 'will', 'can',
            'able to', 'allows', 'enables'
        ]
        return any(indicator in prompt.lower() for indicator in criteria_indicators)

    def _determine_clarity(
        self,
        prompt_lower: str,
        action_verb: Optional[str],
        target_object: Optional[str],
        has_scope: bool
    ) -> IntentClarity:
        """Determine if the intent is clear enough to proceed"""
        # Clear if has specific action + target + scope
        if action_verb and target_object and has_scope:
            if action_verb not in self.VAGUE_VERBS:
                return IntentClarity.CLEAR

        # Vague if using vague verbs or missing specifics
        if action_verb in self.VAGUE_VERBS:
            return IntentClarity.VAGUE

        # Check for very short/ambiguous prompts
        if len(prompt_lower.split()) < 4:
            return IntentClarity.INCOMPLETE

        # Has action but vague target
        if action_verb and not target_object:
            return IntentClarity.VAGUE

        # Default to vague if missing key elements
        if not action_verb or not target_object:
            return IntentClarity.INCOMPLETE

        return IntentClarity.CLEAR

    def _estimate_complexity(self, prompt: str, intent_type: IntentType) -> int:
        """Estimate task complexity on 1-5 scale"""
        complexity = 2  # Default

        # Count indicators of complexity
        if 'multiple' in prompt.lower() or 'several' in prompt.lower():
            complexity += 1

        if 'integrate' in prompt.lower() or 'system' in prompt.lower():
            complexity += 1

        if intent_type == IntentType.SOFTWARE_FEATURE:
            complexity += 1

        if len(prompt.split()) > 20:  # Long description = more complex
            complexity += 1

        return min(5, max(1, complexity))

    def _calculate_confidence(
        self,
        action_verb: Optional[str],
        target_object: Optional[str],
        clarity: IntentClarity,
        intent_type: IntentType
    ) -> float:
        """Calculate confidence score 0.0-1.0"""
        confidence = 0.5

        # Boost for having action and target
        if action_verb:
            confidence += 0.2
        if target_object:
            confidence += 0.2

        # Adjust based on clarity
        if clarity == IntentClarity.CLEAR:
            confidence += 0.1
        elif clarity == IntentClarity.INCOMPLETE:
            confidence -= 0.2

        # Certain intent types are more reliable
        if intent_type in [IntentType.BUG_REPORT, IntentType.SOFTWARE_FEATURE]:
            confidence += 0.1

        return min(1.0, max(0.0, confidence))
