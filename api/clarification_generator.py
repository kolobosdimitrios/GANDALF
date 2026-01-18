"""
Clarification Generator Module
Generates clarifying questions for blocking gaps
"""
from typing import List, Dict, Optional
from dataclasses import dataclass

from .gap_detector import Gap, GapType, GapAnalysis
from .intent_analyzer import IntentAnalysis, IntentType


@dataclass
class ClarificationOption:
    """A single clarification option"""
    label: str
    description: str


@dataclass
class Clarification:
    """A clarification question with options"""
    question: str
    options: Dict[str, str]  # "A": "option text", "B": "option text", "C": "option text"
    default_option: str  # "A", "B", or "C"


class ClarificationGenerator:
    """
    Generates structured clarification questions for blocking gaps
    Following GANDALF format: max 3 questions, 3 options each with default
    """

    def generate_clarifications(
        self,
        user_prompt: str,
        intent_analysis: IntentAnalysis,
        gap_analysis: GapAnalysis
    ) -> List[Clarification]:
        """
        Generate clarification questions for blocking gaps

        Args:
            user_prompt: Original user input
            intent_analysis: Intent analysis result
            gap_analysis: Gap analysis result

        Returns:
            List of clarification questions (max 3)
        """
        if not gap_analysis.has_blocking_gaps:
            return []

        clarifications = []

        # Process each blocking gap (max 3)
        for gap in gap_analysis.blocking_gaps[:3]:
            clarification = self._generate_clarification_for_gap(
                gap,
                user_prompt,
                intent_analysis
            )
            if clarification:
                clarifications.append(clarification)

        return clarifications

    def _generate_clarification_for_gap(
        self,
        gap: Gap,
        user_prompt: str,
        intent_analysis: IntentAnalysis
    ) -> Optional[Clarification]:
        """Generate a clarification question for a specific gap"""
        gap_type = gap.gap_type
        intent_type = intent_analysis.intent_type

        # Route to specific generator based on gap type
        if gap_type == GapType.MISSING_FORMAT:
            return self._generate_format_clarification(user_prompt)
        elif gap_type == GapType.MISSING_PLATFORM:
            return self._generate_platform_clarification(user_prompt, intent_type)
        elif gap_type == GapType.MISSING_SCOPE:
            return self._generate_scope_clarification(user_prompt, intent_type)
        elif gap_type == GapType.VAGUE_ACTION:
            return self._generate_action_clarification(user_prompt, intent_type)
        elif gap_type == GapType.MISSING_TARGET:
            return self._generate_target_clarification(user_prompt, intent_type)
        elif gap_type == GapType.MISSING_CONTEXT:
            return self._generate_context_clarification(user_prompt)

        # Fallback generic question
        return Clarification(
            question=gap.description,
            options={
                "A": gap.suggested_default if gap.suggested_default else "Option A",
                "B": "Option B",
                "C": "Option C"
            },
            default_option="A"
        )

    def _generate_format_clarification(self, prompt: str) -> Clarification:
        """Generate clarification for file format"""
        prompt_lower = prompt.lower()

        if 'upload' in prompt_lower or 'photo' in prompt_lower or 'image' in prompt_lower:
            return Clarification(
                question="What image formats should be supported?",
                options={
                    "A": "JPG and PNG",
                    "B": "JPG, PNG, and GIF",
                    "C": "All common image formats"
                },
                default_option="A"
            )
        else:
            # Export format
            return Clarification(
                question="Which format should the report be exported in?",
                options={
                    "A": "CSV",
                    "B": "PDF",
                    "C": "XLSX"
                },
                default_option="A"
            )

    def _generate_platform_clarification(
        self,
        prompt: str,
        intent_type: IntentType
    ) -> Clarification:
        """Generate clarification for platform/environment"""
        prompt_lower = prompt.lower()

        if 'ios' in prompt_lower or 'android' in prompt_lower:
            # Mobile platform version
            if 'ios' in prompt_lower:
                return Clarification(
                    question="Which iOS version is affected?",
                    options={
                        "A": "iOS 16+",
                        "B": "iOS 15",
                        "C": "All supported iOS versions"
                    },
                    default_option="C"
                )
            else:
                return Clarification(
                    question="Which Android version is affected?",
                    options={
                        "A": "Android 12+",
                        "B": "Android 11",
                        "C": "All supported Android versions"
                    },
                    default_option="C"
                )
        else:
            # Environment
            return Clarification(
                question="Which search environment is affected?",
                options={
                    "A": "Production",
                    "B": "Staging",
                    "C": "Both production and staging"
                },
                default_option="A"
            )

    def _generate_scope_clarification(
        self,
        prompt: str,
        intent_type: IntentType
    ) -> Clarification:
        """Generate clarification for scope/location"""
        prompt_lower = prompt.lower()

        # UI element placement
        if any(word in prompt_lower for word in ['button', 'toggle', 'control']):
            return Clarification(
                question="Where should the export be triggered?",
                options={
                    "A": "Export button above the table",
                    "B": "Export option in row actions",
                    "C": "Export from a settings menu"
                },
                default_option="A"
            )

        # Reporting/metrics
        if any(word in prompt_lower for word in ['report', 'dashboard', 'metric']):
            if intent_type == IntentType.BUSINESS_NEED:
                return Clarification(
                    question="What type of reporting is needed first?",
                    options={
                        "A": "Revenue and sales metrics",
                        "B": "User activity metrics",
                        "C": "Operational KPIs"
                    },
                    default_option="A"
                )
            else:
                return Clarification(
                    question="Which dashboard should be prioritized?",
                    options={
                        "A": "Executive overview",
                        "B": "Sales performance",
                        "C": "Customer success metrics"
                    },
                    default_option="A"
                )

        # Team size
        if 'team' in prompt_lower and 'schedule' in prompt_lower:
            return Clarification(
                question="How many team members should be included in the schedule?",
                options={
                    "A": "3 members",
                    "B": "5 members",
                    "C": "7 members"
                },
                default_option="B"
            )

        # Generic scope
        return Clarification(
            question="What is the scope of this change?",
            options={
                "A": "Single page/component",
                "B": "Multiple related components",
                "C": "System-wide change"
            },
            default_option="A"
        )

    def _generate_action_clarification(
        self,
        prompt: str,
        intent_type: IntentType
    ) -> Clarification:
        """Generate clarification for vague actions"""
        prompt_lower = prompt.lower()

        # Performance improvements
        if any(word in prompt_lower for word in ['faster', 'speed', 'performance']):
            return Clarification(
                question="Which area should be prioritized for speed improvements?",
                options={
                    "A": "Page load time",
                    "B": "Search results response time",
                    "C": "File upload performance"
                },
                default_option="A"
            )

        # Onboarding improvements
        if 'onboarding' in prompt_lower:
            return Clarification(
                question="Which onboarding stage needs improvement first?",
                options={
                    "A": "Signup flow",
                    "B": "First-use tutorial",
                    "C": "Email onboarding sequence"
                },
                default_option="A"
            )

        # Retention improvements
        if 'retention' in prompt_lower:
            return Clarification(
                question="What retention metric should be targeted?",
                options={
                    "A": "30-day active users",
                    "B": "Weekly active users",
                    "C": "7-day return rate"
                },
                default_option="A"
            )

        # Support ticket reduction
        if 'support' in prompt_lower and 'ticket' in prompt_lower:
            return Clarification(
                question="Which support ticket category should be addressed first?",
                options={
                    "A": "Billing issues",
                    "B": "Login/access issues",
                    "C": "Feature usage questions"
                },
                default_option="B"
            )

        # Generic improvement
        return Clarification(
            question="What specific aspect needs improvement?",
            options={
                "A": "User interface",
                "B": "Performance",
                "C": "Functionality"
            },
            default_option="A"
        )

    def _generate_target_clarification(
        self,
        prompt: str,
        intent_type: IntentType
    ) -> Clarification:
        """Generate clarification for missing target"""
        return Clarification(
            question="What is the target of this action?",
            options={
                "A": "User interface element",
                "B": "Backend service",
                "C": "Data/content"
            },
            default_option="A"
        )

    def _generate_context_clarification(self, prompt: str) -> Clarification:
        """Generate clarification for missing context"""
        return Clarification(
            question="Please provide the meeting transcript to summarize.",
            options={
                "A": "Paste the transcript here",
                "B": "Upload a file",
                "C": "Provide a link"
            },
            default_option="A"
        )

    def format_for_output(self, clarifications: List[Clarification]) -> Dict:
        """
        Format clarifications for GANDALF JSON output

        Returns dict in format:
        {
            "asked": [
                {
                    "question": "...",
                    "options": ["A: ...", "B: ...", "C: ..."],
                    "default_option": "A"
                }
            ],
            "resolved_by": None (will be set when answered)
        }
        """
        asked = []
        for clarification in clarifications:
            asked.append({
                "question": clarification.question,
                "options": [
                    f"{key}: {value}"
                    for key, value in clarification.options.items()
                ],
                "default_option": clarification.default_option
            })

        return {
            "asked": asked,
            "resolved_by": None  # Will be "user" or "default" when resolved
        }
