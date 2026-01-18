"""
Gap Detector Module
Identifies missing information and classifies as blocking or non-blocking
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from .intent_analyzer import IntentAnalysis, IntentType, IntentClarity


class GapType(Enum):
    """Types of information gaps"""
    MISSING_SCOPE = "missing_scope"
    MISSING_PLATFORM = "missing_platform"
    MISSING_FORMAT = "missing_format"
    MISSING_TARGET = "missing_target"
    MISSING_CRITERIA = "missing_criteria"
    VAGUE_ACTION = "vague_action"
    MISSING_CONTEXT = "missing_context"
    AMBIGUOUS_INTENT = "ambiguous_intent"


class GapSeverity(Enum):
    """How critical the gap is"""
    BLOCKING = "blocking"      # Must ask user
    NON_BLOCKING = "non_blocking"  # Can proceed with defaults


@dataclass
class Gap:
    """Represents a detected information gap"""
    gap_type: GapType
    severity: GapSeverity
    description: str
    suggested_default: Optional[str] = None


@dataclass
class GapAnalysis:
    """Result of gap detection"""
    has_blocking_gaps: bool
    blocking_gaps: List[Gap]
    non_blocking_gaps: List[Gap]
    can_proceed: bool


class GapDetector:
    """
    Detects missing information in user intents
    Classifies gaps as blocking (must ask) or non-blocking (use defaults)
    """

    def detect_gaps(self, user_prompt: str, intent_analysis: IntentAnalysis) -> GapAnalysis:
        """
        Detect information gaps in user prompt

        Args:
            user_prompt: Raw user input
            intent_analysis: Result from IntentAnalyzer

        Returns:
            GapAnalysis with detected gaps
        """
        gaps = []

        # Check clarity-based gaps
        if intent_analysis.clarity == IntentClarity.INCOMPLETE:
            gaps.extend(self._detect_incomplete_gaps(user_prompt, intent_analysis))
        elif intent_analysis.clarity == IntentClarity.VAGUE:
            gaps.extend(self._detect_vague_gaps(user_prompt, intent_analysis))

        # Check intent-type specific gaps
        if intent_analysis.intent_type == IntentType.SOFTWARE_FEATURE:
            gaps.extend(self._detect_feature_gaps(user_prompt))
        elif intent_analysis.intent_type == IntentType.BUG_REPORT:
            gaps.extend(self._detect_bug_gaps(user_prompt))
        elif intent_analysis.intent_type == IntentType.BUSINESS_NEED:
            gaps.extend(self._detect_business_gaps(user_prompt))
        elif intent_analysis.intent_type == IntentType.NON_TECHNICAL:
            gaps.extend(self._detect_non_tech_gaps(user_prompt))

        # Separate blocking from non-blocking
        blocking_gaps = [g for g in gaps if g.severity == GapSeverity.BLOCKING]
        non_blocking_gaps = [g for g in gaps if g.severity == GapSeverity.NON_BLOCKING]

        # Limit to max 3 blocking gaps (per GANDALF rules)
        blocking_gaps = blocking_gaps[:3]

        has_blocking = len(blocking_gaps) > 0
        can_proceed = not has_blocking

        return GapAnalysis(
            has_blocking_gaps=has_blocking,
            blocking_gaps=blocking_gaps,
            non_blocking_gaps=non_blocking_gaps,
            can_proceed=can_proceed
        )

    def _detect_incomplete_gaps(
        self,
        prompt: str,
        analysis: IntentAnalysis
    ) -> List[Gap]:
        """Detect gaps when intent is incomplete"""
        gaps = []

        # Don't flag as incomplete if it's an export/upload/format-specific task
        # These will be handled by feature-specific gap detection
        prompt_lower = prompt.lower()
        is_format_task = any(word in prompt_lower for word in ['export', 'upload', 'download', 'save'])

        # Missing action
        if not analysis.action_verb and not is_format_task:
            gaps.append(Gap(
                gap_type=GapType.VAGUE_ACTION,
                severity=GapSeverity.BLOCKING,
                description="What action should be taken?"
            ))

        # Missing target
        if not analysis.target_object and not is_format_task:
            gaps.append(Gap(
                gap_type=GapType.MISSING_TARGET,
                severity=GapSeverity.BLOCKING,
                description="What is the target of this action?"
            ))

        # Missing scope - skip for format tasks, they have specific scope needs
        if not analysis.has_scope and not is_format_task:
            gaps.append(Gap(
                gap_type=GapType.MISSING_SCOPE,
                severity=GapSeverity.BLOCKING,
                description="Where should this be implemented?"
            ))

        return gaps

    def _detect_vague_gaps(
        self,
        prompt: str,
        analysis: IntentAnalysis
    ) -> List[Gap]:
        """Detect gaps when intent is vague"""
        gaps = []
        prompt_lower = prompt.lower()

        # Vague improvement requests - but not if it's a specific setup/config task
        has_specific_action = any(word in prompt_lower for word in [
            'set up', 'configure', 'add', 'create', 'fix', 'update', 'when', 'alert'
        ])

        if any(word in prompt_lower for word in ['better', 'improve', 'optimize']):
            # Only flag as vague if no specific action or target
            if not has_specific_action and not analysis.has_scope:
                gaps.append(Gap(
                    gap_type=GapType.VAGUE_ACTION,
                    severity=GapSeverity.BLOCKING,
                    description="What specific aspect needs improvement?"
                ))

        # Missing specifics - only non-blocking
        if not analysis.has_success_criteria and not has_specific_action:
            gaps.append(Gap(
                gap_type=GapType.MISSING_CRITERIA,
                severity=GapSeverity.NON_BLOCKING,
                description="Success criteria not explicitly defined",
                suggested_default="Standard implementation criteria"
            ))

        return gaps

    def _detect_feature_gaps(self, prompt: str) -> List[Gap]:
        """Detect gaps specific to software feature requests"""
        gaps = []
        prompt_lower = prompt.lower()

        # Check for format/export requests - but not if it's a bug report about export
        is_export_bug = any(word in prompt_lower for word in ['nothing', 'not working', 'doesn\'t work', 'broken', 'fails'])

        if any(word in prompt_lower for word in ['export', 'download', 'save']) and not is_export_bug:
            if not any(fmt in prompt_lower for fmt in ['csv', 'pdf', 'json', 'xlsx', 'xml']):
                gaps.append(Gap(
                    gap_type=GapType.MISSING_FORMAT,
                    severity=GapSeverity.BLOCKING,
                    description="Which format should be used?",
                    suggested_default="CSV"
                ))

        # Check for upload requests
        if 'upload' in prompt_lower:
            if not any(fmt in prompt_lower for fmt in ['jpg', 'png', 'gif', 'pdf', 'image']):
                gaps.append(Gap(
                    gap_type=GapType.MISSING_FORMAT,
                    severity=GapSeverity.BLOCKING,
                    description="Which file formats should be supported?",
                    suggested_default="JPG and PNG"
                ))

        # Check for UI placement
        if any(word in prompt_lower for word in ['button', 'link', 'toggle']):
            if not any(loc in prompt_lower for loc in ['in', 'on', 'above', 'below', 'settings']):
                gaps.append(Gap(
                    gap_type=GapType.MISSING_SCOPE,
                    severity=GapSeverity.BLOCKING,
                    description="Where should the UI element be placed?",
                    suggested_default="In settings menu"
                ))

        return gaps

    def _detect_bug_gaps(self, prompt: str) -> List[Gap]:
        """Detect gaps specific to bug reports"""
        gaps = []
        prompt_lower = prompt.lower()

        # Check if bug is intermittent/platform-specific
        is_intermittent = any(word in prompt_lower for word in ['sometimes', 'occasionally', 'intermittent'])

        # Check for iOS/Android version needs
        if 'ios' in prompt_lower:
            if not any(ver in prompt_lower for ver in ['version', 'ios 1', 'ios 2', '+', 'all']):
                # Ask if intermittent or no specific version mentioned
                if is_intermittent:
                    gaps.append(Gap(
                        gap_type=GapType.MISSING_PLATFORM,
                        severity=GapSeverity.BLOCKING,
                        description="Which version/platform is affected?",
                        suggested_default="All supported versions"
                    ))

        if 'android' in prompt_lower:
            if not any(ver in prompt_lower for ver in ['version', 'android 1', '+', 'all']):
                if is_intermittent:
                    gaps.append(Gap(
                        gap_type=GapType.MISSING_PLATFORM,
                        severity=GapSeverity.BLOCKING,
                        description="Which version/platform is affected?",
                        suggested_default="All supported versions"
                    ))

        # Check for environment specification - only for deployment-related issues
        if 'release' in prompt_lower or 'deploy' in prompt_lower:
            if not any(env in prompt_lower for env in ['production', 'staging', 'dev']):
                if not has_specific_error:
                    gaps.append(Gap(
                        gap_type=GapType.MISSING_PLATFORM,
                        severity=GapSeverity.BLOCKING,
                        description="Which environment is affected?",
                        suggested_default="Production"
                    ))

        return gaps

    def _detect_business_gaps(self, prompt: str) -> List[Gap]:
        """Detect gaps specific to business needs"""
        gaps = []
        prompt_lower = prompt.lower()

        # Business goals are almost always vague initially
        if any(word in prompt_lower for word in ['increase', 'improve', 'better', 'more']):
            gaps.append(Gap(
                gap_type=GapType.VAGUE_ACTION,
                severity=GapSeverity.BLOCKING,
                description="What specific metric or area should be targeted?"
            ))

        # Check for dashboard/reporting requests
        if any(word in prompt_lower for word in ['dashboard', 'report', 'metric']):
            if not any(spec in prompt_lower for spec in ['revenue', 'user', 'sales', 'activity']):
                gaps.append(Gap(
                    gap_type=GapType.MISSING_SCOPE,
                    severity=GapSeverity.BLOCKING,
                    description="What type of metrics/data should be included?",
                    suggested_default="Key performance metrics"
                ))

        return gaps

    def _detect_non_tech_gaps(self, prompt: str) -> List[Gap]:
        """Detect gaps specific to non-technical requests"""
        gaps = []
        prompt_lower = prompt.lower()

        # Check for content that needs to be provided
        if 'summarize' in prompt_lower or 'review' in prompt_lower:
            if 'transcript' not in prompt_lower and 'document' not in prompt_lower:
                gaps.append(Gap(
                    gap_type=GapType.MISSING_CONTEXT,
                    severity=GapSeverity.BLOCKING,
                    description="Please provide the content to process"
                ))

        # Check for schedule/team requests
        if 'schedule' in prompt_lower and 'team' in prompt_lower:
            if not any(num in prompt for num in ['2', '3', '4', '5', '6', '7', '8', '9']):
                gaps.append(Gap(
                    gap_type=GapType.MISSING_SCOPE,
                    severity=GapSeverity.BLOCKING,
                    description="How many people should be included?",
                    suggested_default="5 members"
                ))

        return gaps
