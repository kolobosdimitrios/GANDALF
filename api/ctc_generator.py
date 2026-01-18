"""
CTC Generator Module
Generates Compiled Task Contracts following GANDALF rules
"""
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .intent_analyzer import IntentAnalysis, IntentAnalyzer, IntentType
from .gap_detector import GapDetector, GapAnalysis
from .clarification_generator import ClarificationGenerator, Clarification


class CTCGenerator:
    """
    Main CTC generation engine
    Follows GANDALF specification for creating minimal, deterministic task prompts
    """

    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.gap_detector = GapDetector()
        self.clarification_generator = ClarificationGenerator()

    def generate(
        self,
        user_prompt: str,
        intent_id: str,
        date: str,
        generate_for: str
    ) -> Dict:
        """
        Generate a CTC from user prompt

        Args:
            user_prompt: Raw user intent
            intent_id: Unique identifier
            date: ISO-8601 timestamp
            generate_for: Target executor (e.g., "claude-code")

        Returns:
            Complete GANDALF-format CTC or clarification request
        """
        # Step 1: Analyze intent
        intent_analysis = self.intent_analyzer.analyze(user_prompt)

        # Step 2: Detect gaps
        gap_analysis = self.gap_detector.detect_gaps(user_prompt, intent_analysis)

        # Step 3: If blocking gaps exist, generate clarifications
        if gap_analysis.has_blocking_gaps:
            return self._generate_clarification_response(
                user_prompt,
                intent_analysis,
                gap_analysis,
                intent_id,
                date,
                generate_for
            )

        # Step 4: Generate CTC
        return self._generate_ctc_response(
            user_prompt,
            intent_analysis,
            gap_analysis,
            intent_id,
            date,
            generate_for
        )

    def _generate_clarification_response(
        self,
        user_prompt: str,
        intent_analysis: IntentAnalysis,
        gap_analysis: GapAnalysis,
        intent_id: str,
        date: str,
        generate_for: str
    ) -> Dict:
        """Generate a response requesting clarifications"""
        clarifications = self.clarification_generator.generate_clarifications(
            user_prompt,
            intent_analysis,
            gap_analysis
        )

        # Format clarifications for output
        clarification_data = self.clarification_generator.format_for_output(clarifications)

        # Return minimal structure with clarifications
        return {
            "gandalf_version": "1.0",
            "requires_clarification": True,
            "clarifications": clarification_data,
            "telemetry": {
                "intent_id": intent_id,
                "created_at": datetime.utcnow().isoformat(),
                "executor": {
                    "name": generate_for,
                    "version": "1.0"
                },
                "elapsed_ms": 0,
                "input_tokens": None,
                "output_tokens": None,
                "user_questions_count": len(clarifications),
                "execution_result": "pending_clarification"
            }
        }

    def _generate_ctc_response(
        self,
        user_prompt: str,
        intent_analysis: IntentAnalysis,
        gap_analysis: GapAnalysis,
        intent_id: str,
        date: str,
        generate_for: str
    ) -> Dict:
        """Generate complete CTC response"""
        # Generate each CTC component
        title = self._generate_title(user_prompt, intent_analysis)
        context = self._generate_context(user_prompt, intent_analysis)
        definition_of_done = self._generate_definition_of_done(user_prompt, intent_analysis)
        constraints = self._generate_constraints(user_prompt, intent_analysis)
        deliverables = self._generate_deliverables(user_prompt, intent_analysis)

        return {
            "gandalf_version": "1.0",
            "ctc": {
                "title": title,
                "context": context,
                "definition_of_done": definition_of_done,
                "constraints": constraints,
                "deliverables": deliverables
            },
            "clarifications": {
                "asked": [],
                "resolved_by": "default"
            },
            "telemetry": {
                "intent_id": intent_id,
                "created_at": datetime.utcnow().isoformat(),
                "executor": {
                    "name": generate_for,
                    "version": "1.0"
                },
                "elapsed_ms": 0,
                "input_tokens": None,
                "output_tokens": None,
                "user_questions_count": 0,
                "execution_result": "unknown"
            }
        }

    def _generate_title(self, user_prompt: str, analysis: IntentAnalysis) -> str:
        """
        Generate task title
        Rule: Clear verb + concrete object
        Avoid vague verbs (improve, handle, optimize)
        """
        # Try to extract action + target
        action = analysis.action_verb
        target = analysis.target_object

        if action and target:
            # Clean up the target (remove articles, limit length)
            target_clean = self._clean_target(target)

            # Map vague verbs to specific ones
            action_mapped = self._map_to_clear_verb(action, user_prompt, analysis)

            return f"{action_mapped.capitalize()} {target_clean}"

        # Fallback: extract from prompt
        return self._extract_title_from_prompt(user_prompt)

    def _clean_target(self, target: str) -> str:
        """Clean up target object for title"""
        # Remove articles
        target = re.sub(r'\b(a|an|the)\b', '', target, flags=re.IGNORECASE)
        # Remove extra whitespace
        target = ' '.join(target.split())
        # Limit length
        if len(target) > 40:
            target = target[:37] + "..."
        return target.strip()

    def _map_to_clear_verb(self, verb: str, prompt: str, analysis: IntentAnalysis) -> str:
        """Map vague verbs to clear, specific ones"""
        prompt_lower = prompt.lower()

        verb_map = {
            'improve': 'optimize' if 'performance' in prompt_lower else 'enhance',
            'handle': 'process',
            'manage': 'configure',
            'deal with': 'process',
            'make better': 'improve'
        }

        return verb_map.get(verb, verb)

    def _extract_title_from_prompt(self, prompt: str) -> str:
        """Extract title from prompt when action/target unclear"""
        # Remove leading/trailing whitespace
        prompt = prompt.strip()

        # Take first sentence
        first_sentence = prompt.split('.')[0]

        # Capitalize first letter
        if first_sentence:
            first_sentence = first_sentence[0].upper() + first_sentence[1:]

        # Limit length
        if len(first_sentence) > 50:
            return first_sentence[:47] + "..."

        return first_sentence

    def _generate_context(self, user_prompt: str, analysis: IntentAnalysis) -> List[str]:
        """
        Generate context bullets
        Rule: Max 2 bullets, no background stories, only delta information
        """
        context = []
        prompt_lower = user_prompt.lower()

        # First bullet: What exists or what triggered the task
        if analysis.intent_type == IntentType.BUG_REPORT:
            # Bug context
            context.append(self._extract_bug_context(user_prompt))
        elif analysis.intent_type == IntentType.SOFTWARE_FEATURE:
            # Feature context
            context.append(self._extract_feature_context(user_prompt))
        elif analysis.intent_type == IntentType.NON_TECHNICAL:
            # Non-technical context
            context.append(self._extract_non_tech_context(user_prompt))
        else:
            # Generic context
            context.append(self._extract_generic_context(user_prompt))

        # Second bullet: Only if strictly necessary
        if analysis.complexity > 3 and analysis.has_constraints:
            constraint_summary = self._extract_key_constraint(user_prompt)
            if constraint_summary:
                context.append(constraint_summary)

        # Ensure max 2 bullets
        return context[:2]

    def _extract_bug_context(self, prompt: str) -> str:
        """Extract context for bug reports"""
        # Look for error or problem description
        prompt_lower = prompt.lower()

        if 'fails' in prompt_lower or 'error' in prompt_lower:
            return "Error reported in current system behavior"
        elif 'not working' in prompt_lower or 'broken' in prompt_lower:
            return "Functionality is not working as expected"
        else:
            return "Bug fix required in existing feature"

    def _extract_feature_context(self, prompt: str) -> str:
        """Extract context for feature requests"""
        prompt_lower = prompt.lower()

        # Check what exists
        if 'add' in prompt_lower or 'create' in prompt_lower:
            if 'page' in prompt_lower:
                return "Existing page needs new feature"
            elif 'app' in prompt_lower:
                return "Application needs new functionality"
            else:
                return "New feature required"
        elif 'update' in prompt_lower or 'change' in prompt_lower:
            return "Existing feature needs modification"
        else:
            return "Feature enhancement requested"

    def _extract_non_tech_context(self, prompt: str) -> str:
        """Extract context for non-technical requests"""
        prompt_lower = prompt.lower()

        if 'email' in prompt_lower or 'note' in prompt_lower:
            return "Text content needs to be created"
        elif 'document' in prompt_lower or 'policy' in prompt_lower:
            return "Document creation requested"
        elif 'checklist' in prompt_lower or 'schedule' in prompt_lower:
            return "Structured list needs to be created"
        else:
            return "Content creation requested"

    def _extract_generic_context(self, prompt: str) -> str:
        """Generic context extraction"""
        return "Task requested based on user requirements"

    def _extract_key_constraint(self, prompt: str) -> Optional[str]:
        """Extract a key constraint if it changes implementation"""
        prompt_lower = prompt.lower()

        if 'without changing' in prompt_lower or 'don\'t change' in prompt_lower:
            return "Existing functionality must remain unchanged"
        elif 'only' in prompt_lower:
            # Extract what "only" applies to
            return None  # Too complex for now
        else:
            return None

    def _generate_definition_of_done(
        self,
        user_prompt: str,
        analysis: IntentAnalysis
    ) -> List[str]:
        """
        Generate Definition of Done checkboxes
        Rule: 3-7 checkboxes, objectively verifiable, no vague terms
        """
        dod = []
        prompt_lower = user_prompt.lower()

        # Base on intent type
        if analysis.intent_type == IntentType.BUG_REPORT:
            dod.extend(self._generate_bug_dod(user_prompt))
        elif analysis.intent_type == IntentType.SOFTWARE_FEATURE:
            dod.extend(self._generate_feature_dod(user_prompt, analysis))
        elif analysis.intent_type == IntentType.NON_TECHNICAL:
            dod.extend(self._generate_non_tech_dod(user_prompt))
        else:
            dod.extend(self._generate_generic_dod(user_prompt))

        # Add common verification items
        if analysis.intent_type == IntentType.SOFTWARE_FEATURE:
            dod.append("Implementation tested and verified")

        # Ensure 3-7 items
        if len(dod) < 3:
            dod.append("Changes documented")
        if len(dod) < 3:
            dod.append("No new errors introduced")

        return dod[:7]

    def _generate_bug_dod(self, prompt: str) -> List[str]:
        """Generate DoD for bug fixes"""
        dod = []
        prompt_lower = prompt.lower()

        # Specific to the bug
        if '500 error' in prompt_lower or 'error' in prompt_lower:
            dod.append("Error no longer occurs")
            dod.append("Error logs show no related errors")
        elif 'blank screen' in prompt_lower or 'nothing' in prompt_lower:
            dod.append("Expected content displays correctly")
        else:
            dod.append("Reported issue is resolved")

        # Verification
        dod.append("Fix verified in affected scenarios")
        dod.append("No regression in related functionality")

        return dod

    def _generate_feature_dod(self, prompt: str, analysis: IntentAnalysis) -> List[str]:
        """Generate DoD for features"""
        dod = []
        prompt_lower = prompt.lower()

        # Extract specific requirements
        if 'toggle' in prompt_lower or 'button' in prompt_lower:
            dod.append(f"UI element is visible and accessible")
            dod.append("Clicking the element triggers expected behavior")

        if 'filter' in prompt_lower:
            dod.append("Filter correctly narrows results")
            dod.append("Filter can be cleared")

        if 'export' in prompt_lower:
            dod.append("Export generates file with correct data")
            dod.append("Downloaded file is in specified format")

        if 'upload' in prompt_lower:
            dod.append("File upload accepts specified formats")
            dod.append("Uploaded files are processed correctly")

        if 'email' in prompt_lower and 'send' not in prompt_lower:
            dod.append("Email template includes all required elements")

        # Persistence for settings/preferences
        if 'settings' in prompt_lower or 'toggle' in prompt_lower:
            dod.append("User selection persists across sessions")

        # Generic feature completion
        if not dod:
            dod.append("Feature is implemented as described")
            dod.append("Feature works in all specified scenarios")

        return dod

    def _generate_non_tech_dod(self, prompt: str) -> List[str]:
        """Generate DoD for non-technical tasks"""
        dod = []
        prompt_lower = prompt.lower()

        if 'email' in prompt_lower or 'note' in prompt_lower:
            dod.append("Message includes a greeting")
            dod.append("Message conveys intended information")
            if 'short' in prompt_lower or 'brief' in prompt_lower:
                dod.append("Message is concise (under 100 words)")

        if 'checklist' in prompt_lower or 'list' in prompt_lower:
            dod.append("List includes all required items")
            dod.append("Items are formatted as bullet points")

        if 'policy' in prompt_lower or 'document' in prompt_lower:
            dod.append("Document includes all required sections")
            dod.append("Content follows appropriate tone")

        if 'schedule' in prompt_lower:
            dod.append("Schedule covers specified time period")
            dod.append("All required participants are included")

        return dod

    def _generate_generic_dod(self, prompt: str) -> List[str]:
        """Generic DoD generation"""
        return [
            "Requirements from user prompt are met",
            "Output is complete and functional",
            "Result has been verified"
        ]

    def _generate_constraints(self, user_prompt: str, analysis: IntentAnalysis) -> List[str]:
        """
        Generate constraints
        Rule: Max 5 bullets, only task-specific hard limits
        """
        constraints = []
        prompt_lower = user_prompt.lower()

        # Extract explicit constraints
        if 'without' in prompt_lower or 'don\'t' in prompt_lower:
            # Extract what not to change
            if 'without changing' in prompt_lower:
                constraints.append("Do not modify existing functionality")
            elif 'don\'t change' in prompt_lower:
                constraints.append("Preserve current behavior in other areas")

        # Scope constraints
        if 'only' in prompt_lower:
            constraints.append("Limit changes to specified scope only")

        # Type-specific constraints
        if analysis.intent_type == IntentType.SOFTWARE_FEATURE:
            if 'settings' in prompt_lower or 'ui' in prompt_lower:
                constraints.append("Do not change non-UI functionality")

        if analysis.intent_type == IntentType.BUG_REPORT:
            constraints.append("Do not introduce new issues")

        if analysis.intent_type == IntentType.NON_TECHNICAL:
            if 'tone' in prompt_lower or 'professional' in prompt_lower:
                constraints.append("Use professional tone")
            elif 'friendly' in prompt_lower:
                constraints.append("Use friendly, conversational tone")

        # Add style constraint for short content
        if any(word in prompt_lower for word in ['short', 'brief', 'concise', 'one page']):
            if 'page' in prompt_lower:
                constraints.append("Content must fit on one page")
            else:
                constraints.append("Keep content brief and concise")

        # Max 5 constraints
        return constraints[:5]

    def _generate_deliverables(self, user_prompt: str, analysis: IntentAnalysis) -> List[str]:
        """
        Generate deliverables list
        Rule: Max 5 bullets, artifacts only, no descriptions
        """
        deliverables = []
        prompt_lower = user_prompt.lower()

        # Type-specific deliverables
        if analysis.intent_type == IntentType.SOFTWARE_FEATURE:
            # Code deliverables
            if 'ui' in prompt_lower or 'page' in prompt_lower or 'component' in prompt_lower:
                deliverables.append("Updated UI component(s)")
            if 'api' in prompt_lower or 'endpoint' in prompt_lower:
                deliverables.append("API endpoint implementation")
            if 'database' in prompt_lower:
                deliverables.append("Database schema changes")

            # Default code deliverable
            if not deliverables:
                deliverables.append("Source code implementation")

            # Tests if complex
            if analysis.complexity > 2:
                deliverables.append("Unit tests")

        elif analysis.intent_type == IntentType.BUG_REPORT:
            deliverables.append("Bug fix implementation")
            if analysis.complexity > 2:
                deliverables.append("Test case for the fix")

        elif analysis.intent_type == IntentType.NON_TECHNICAL:
            # Content deliverables
            if 'email' in prompt_lower:
                deliverables.append("Email template" if 'template' in prompt_lower else "Email text")
            elif 'document' in prompt_lower or 'policy' in prompt_lower:
                deliverables.append("Document file")
            elif 'checklist' in prompt_lower or 'list' in prompt_lower:
                deliverables.append("Checklist document")
            elif 'schedule' in prompt_lower:
                deliverables.append("Schedule template")
            else:
                deliverables.append("Written content")

        else:
            # Generic deliverables
            deliverables.append("Implementation artifacts")

        # Max 5 deliverables
        return deliverables[:5]
