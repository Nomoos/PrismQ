"""Script Editing Review - AI-powered editing validation for scripts.

This module implements PrismQ.T.Review.Script.Editing for Stage 18 (MVP-018).
Provides comprehensive editing checks including clarity, flow, redundancy,
structure, and transitions with line-by-line improvement suggestions.

The editing review serves as a quality gate - scripts must pass before proceeding
to Title Readability (Stage 19/MVP-019). If it fails, the script returns to
refinement with detailed feedback.

Workflow Position:
    Stage 18 (MVP-018): Editing Review
    Script v3+ → Editing Review → [PASS: Stage 19] or [FAIL: Script Refinement]
"""

import json
import re
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

# Import EditingReview model classes from local module
from .editing_review import (
    EditingIssue,
    EditingIssueType,
    EditingReview,
    EditingSeverity,
)


class ScriptEditingChecker:
    """AI-powered editing checker for script content.

    Performs comprehensive editing validation including:
    - Clarity and sentence structure
    - Redundancy and repetition
    - Flow and transitions
    - Wordiness and verbose expressions
    - Structural coherence

    Provides line-by-line improvement suggestions with specific rewrites.
    """

    # Scoring penalties (configurable)
    PENALTY_CRITICAL = 15
    PENALTY_HIGH = 10
    PENALTY_MEDIUM = 5
    PENALTY_LOW = 2

    def __init__(self, pass_threshold: int = 85):
        """Initialize the editing checker.

        Args:
            pass_threshold: Minimum score (0-100) required to pass review
        """
        self.pass_threshold = pass_threshold

        # Common wordy phrases and their concise alternatives
        self.wordy_phrases = {
            "in order to": "to",
            "due to the fact that": "because",
            "at this point in time": "now",
            "for the purpose of": "for",
            "in the event that": "if",
            "with regard to": "regarding",
            "in spite of the fact that": "although",
            "by means of": "by",
            "in the near future": "soon",
            "at the present time": "now",
            "in view of the fact that": "because",
            "on the basis of": "based on",
            "in accordance with": "per",
            "for the reason that": "because",
            "in the majority of cases": "usually",
            "make a decision": "decide",
            "give consideration to": "consider",
            "in close proximity": "near",
            "prior to": "before",
            "subsequent to": "after",
            "in conjunction with": "with",
            "a large number of": "many",
            "a small number of": "few",
            "at the conclusion of": "after",
            "during the time that": "while",
            "has the ability to": "can",
            "in a timely manner": "promptly",
            "is able to": "can",
            "it is important to note that": " ",  # Will be cleaned up
            "it should be noted that": " ",  # Will be cleaned up
            "as a matter of fact": "in fact",
            "the fact that": "that",
            "very unique": "unique",
            "completely finished": "finished",
            "absolutely essential": "essential",
            "past history": "history",
            "future plans": "plans",
            "advance warning": "warning",
            "close scrutiny": "scrutiny",
        }

        # Passive voice indicators (simplified)
        self.passive_indicators = [
            (r"\b(was|were|is|are|been|being)\s+\w+ed\b", "Consider active voice"),
            (r"\b(was|were|is|are)\s+\w+en\b", "Consider active voice"),
        ]

        # Weak transitions
        self.weak_transitions = {
            "and then",
            "and so",
            "so anyway",
            "also",
            "plus",
            "in addition",
            "moreover",
            "furthermore",
        }

        # Common redundant pairs
        self.redundant_pairs = [
            "absolutely essential",
            "advance warning",
            "basic fundamentals",
            "close proximity",
            "completely finished",
            "end result",
            "exact same",
            "final outcome",
            "free gift",
            "future plans",
            "past history",
            "personal opinion",
            "prior experience",
            "sudden crisis",
            "true facts",
            "unexpected surprise",
            "very unique",
            "added bonus",
            "actual fact",
        ]

    def review_script(
        self, script_text: str, script_id: str = "script-001", script_version: str = "v3"
    ) -> EditingReview:
        """Review a script for editing quality, clarity, and flow.

        Args:
            script_text: The script text to review
            script_id: Identifier for the script
            script_version: Version of the script (v3, v4, etc.)

        Returns:
            EditingReview object with all detected issues
        """
        review = EditingReview(
            script_id=script_id, script_version=script_version, pass_threshold=self.pass_threshold
        )

        # Split script into lines for line-by-line analysis
        lines = script_text.split("\n")

        # Check each line
        for line_num, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            # Check for wordiness
            self._check_wordiness(line, line_num, review)

            # Check for redundancy
            self._check_redundancy(line, line_num, review)

            # Check for clarity (passive voice, complex structures)
            self._check_clarity(line, line_num, review)

            # Check for weak transitions
            self._check_transitions(line, line_num, review)

        # Check overall flow and structure
        self._check_overall_flow(lines, review)

        # Calculate overall score based on issues
        review.overall_score = self._calculate_score(review)

        # Recalculate pass status after score is set
        review._recalculate_pass_status()

        # Generate summary and feedback
        self._generate_feedback(review)

        return review

    def _preserve_case(self, original: str, replacement: str) -> str:
        """Preserve the case of the original word in the replacement.

        Args:
            original: Original word with case to preserve
            replacement: Replacement word to adjust case

        Returns:
            Replacement word with preserved case
        """
        if not original or not replacement:
            return replacement

        # If original is all uppercase, make replacement uppercase
        if original.isupper():
            return replacement.upper()
        # If original starts with uppercase, capitalize replacement
        elif original[0].isupper():
            return replacement.capitalize()
        # Otherwise, keep replacement lowercase
        else:
            return replacement.lower()

    def _check_wordiness(self, line: str, line_num: int, review: EditingReview) -> None:
        """Check for wordy phrases that can be simplified."""
        line_lower = line.lower()

        for wordy, concise in self.wordy_phrases.items():
            if wordy in line_lower:
                # Find the phrase in the original line (preserve case)
                pattern = re.compile(re.escape(wordy), re.IGNORECASE)
                match = pattern.search(line)

                if match:
                    if concise:
                        suggestion = line.replace(match.group(), concise)
                        explanation = f"Replace wordy phrase '{match.group()}' with '{concise}'"
                    else:
                        suggestion = line.replace(match.group(), "")
                        suggestion = re.sub(r"\s+", " ", suggestion).strip()
                        explanation = f"Remove unnecessary phrase '{match.group()}'"

                    issue = EditingIssue(
                        issue_type=EditingIssueType.WORDINESS,
                        severity=EditingSeverity.MEDIUM,
                        line_number=line_num,
                        text=line.strip(),
                        suggestion=suggestion,
                        explanation=explanation,
                        confidence=85,
                    )
                    review.add_issue(issue)
                    break  # Only flag one wordy phrase per line

    def _check_redundancy(self, line: str, line_num: int, review: EditingReview) -> None:
        """Check for redundant phrases and repetitive content."""
        line_lower = line.lower()

        # Check for redundant pairs
        for redundant in self.redundant_pairs:
            if redundant in line_lower:
                # Suggest removing the redundant part
                parts = redundant.split()
                if len(parts) == 2:
                    # Preserve original case using pattern matching
                    pattern = re.compile(re.escape(redundant), re.IGNORECASE)
                    match = pattern.search(line)
                    if match:
                        # Preserve case of the replacement word
                        replacement = self._preserve_case(match.group(), parts[1])
                        suggestion = line.replace(match.group(), replacement)

                        issue = EditingIssue(
                            issue_type=EditingIssueType.REDUNDANCY,
                            severity=EditingSeverity.HIGH,
                            line_number=line_num,
                            text=line.strip(),
                            suggestion=suggestion,
                            explanation=f"'{redundant}' is redundant; use '{parts[1]}' instead",
                            confidence=90,
                        )
                        review.add_issue(issue)
                        break

        # Check for repeated words (simple check)
        words = re.findall(r"\b\w+\b", line_lower)
        for i in range(len(words) - 1):
            if words[i] == words[i + 1] and len(words[i]) > 3:  # Ignore short words
                issue = EditingIssue(
                    issue_type=EditingIssueType.REDUNDANCY,
                    severity=EditingSeverity.MEDIUM,
                    line_number=line_num,
                    text=line.strip(),
                    suggestion=f"Remove repeated word '{words[i]}'",
                    explanation=f"Word '{words[i]}' appears twice in a row",
                    confidence=95,
                )
                review.add_issue(issue)
                break  # Only flag once per line

    def _check_clarity(self, line: str, line_num: int, review: EditingReview) -> None:
        """Check for clarity issues like passive voice and complex structures."""
        stripped = line.strip()
        if not stripped or len(stripped) < 10:
            return

        # Skip dialogue lines and formatting
        if stripped.startswith(("[", "(", "*", "-", "INT.", "EXT.")):
            return

        # Check for passive voice
        for pattern, suggestion_text in self.passive_indicators:
            matches = list(re.finditer(pattern, line, re.IGNORECASE))
            if matches and len(stripped.split()) > 8:  # Only flag longer sentences
                # Check if this is likely narrative (not dialogue)
                if not any(char in stripped for char in ['"', "'"]):
                    match = matches[0]
                    issue = EditingIssue(
                        issue_type=EditingIssueType.CLARITY,
                        severity=EditingSeverity.MEDIUM,
                        line_number=line_num,
                        text=stripped,
                        suggestion=suggestion_text,
                        explanation="Passive voice can reduce clarity; consider using active voice",
                        confidence=70,
                    )
                    review.add_issue(issue)
                    break  # Only flag once per line

        # Check for overly long sentences
        if len(stripped.split()) > 30:
            issue = EditingIssue(
                issue_type=EditingIssueType.CLARITY,
                severity=EditingSeverity.MEDIUM,
                line_number=line_num,
                text=stripped,
                suggestion="Consider breaking into shorter sentences",
                explanation=f"Long sentence ({len(stripped.split())} words) may be hard to follow",
                confidence=75,
            )
            review.add_issue(issue)

    def _check_transitions(self, line: str, line_num: int, review: EditingReview) -> None:
        """Check for weak or missing transitions."""
        line_lower = line.lower().strip()

        # Check if line starts with a weak transition
        for weak in self.weak_transitions:
            if line_lower.startswith(weak):
                issue = EditingIssue(
                    issue_type=EditingIssueType.TRANSITION,
                    severity=EditingSeverity.LOW,
                    line_number=line_num,
                    text=line.strip(),
                    suggestion=f"Consider a stronger transition than '{weak}'",
                    explanation="Weak transition; consider alternatives like 'However', 'Meanwhile', 'Consequently'",
                    confidence=65,
                )
                review.add_issue(issue)
                break

    def _check_overall_flow(self, lines: List[str], review: EditingReview) -> None:
        """Check overall flow and structure of the script."""
        # Check for very short paragraphs (single line followed by blank)
        non_empty_lines = [(i + 1, line) for i, line in enumerate(lines) if line.strip()]

        if len(non_empty_lines) > 10:
            # Check paragraph variety
            paragraph_lengths = []
            current_para_length = 0

            for i, line in enumerate(lines):
                if line.strip():
                    current_para_length += 1
                else:
                    if current_para_length > 0:
                        paragraph_lengths.append(current_para_length)
                        current_para_length = 0

            if current_para_length > 0:
                paragraph_lengths.append(current_para_length)

            # If all paragraphs are very short or very long, flag as structure issue
            if paragraph_lengths:
                avg_length = sum(paragraph_lengths) / len(paragraph_lengths)
                if avg_length < 1.5 and len(paragraph_lengths) > 5:
                    # Too many single-line paragraphs
                    issue = EditingIssue(
                        issue_type=EditingIssueType.STRUCTURE,
                        severity=EditingSeverity.LOW,
                        line_number=1,
                        text="Overall script structure",
                        suggestion="Consider combining some single-line paragraphs for better flow",
                        explanation="Many single-line paragraphs can make the script feel choppy",
                        confidence=60,
                    )
                    review.add_issue(issue)

    def _calculate_score(self, review: EditingReview) -> int:
        """Calculate overall editing score based on issues.

        Args:
            review: The EditingReview object with detected issues

        Returns:
            Score from 0-100
        """
        # Start with perfect score
        score = 100

        # Deduct points based on severity using class constants
        score -= review.critical_count * self.PENALTY_CRITICAL
        score -= review.high_count * self.PENALTY_HIGH
        score -= review.medium_count * self.PENALTY_MEDIUM
        score -= review.low_count * self.PENALTY_LOW

        # Ensure score doesn't go below 0
        return max(0, score)

    def _generate_feedback(self, review: EditingReview) -> None:
        """Generate summary and feedback for the review.

        Args:
            review: The EditingReview object to populate with feedback
        """
        total_issues = len(review.issues)

        if total_issues == 0:
            review.summary = "Excellent! Script is clear, concise, and well-structured. No editing issues detected."
            review.passes = True
            return

        # Generate summary
        if review.passes:
            review.summary = (
                f"Script passes editing review with {total_issues} minor issue(s) detected."
            )
        else:
            review.summary = f"Script requires revision. {total_issues} editing issue(s) detected, including {review.critical_count} critical issue(s)."

        # Identify primary concerns
        if review.critical_count > 0:
            review.primary_concerns.append(
                f"{review.critical_count} critical clarity issue(s) must be fixed"
            )

        if review.high_count > 0:
            review.primary_concerns.append(
                f"{review.high_count} high-priority issue(s) should be addressed"
            )

        # Categorize issues for quick fixes
        wordiness_count = len(review.get_issues_by_type(EditingIssueType.WORDINESS))
        if wordiness_count > 0:
            review.quick_fixes.append(f"Simplify {wordiness_count} wordy phrase(s)")

        redundancy_count = len(review.get_issues_by_type(EditingIssueType.REDUNDANCY))
        if redundancy_count > 0:
            review.quick_fixes.append(f"Remove {redundancy_count} redundant phrase(s)")

        clarity_count = len(review.get_issues_by_type(EditingIssueType.CLARITY))
        if clarity_count > 0:
            review.quick_fixes.append(f"Improve clarity in {clarity_count} sentence(s)")

        transition_count = len(review.get_issues_by_type(EditingIssueType.TRANSITION))
        if transition_count > 0:
            review.quick_fixes.append(f"Strengthen {transition_count} transition(s)")


def review_script_editing(
    script_text: str,
    script_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 85,
) -> EditingReview:
    """Convenience function to review script editing quality.

    Args:
        script_text: The script text to review
        script_id: Identifier for the script
        script_version: Version of the script
        pass_threshold: Minimum score required to pass

    Returns:
        EditingReview object with all detected issues

    Example:
        >>> script = "In order to make a decision, we need to give consideration to all options."
        >>> review = review_script_editing(script)
        >>> print(f"Score: {review.overall_score}")
        >>> print(f"Passes: {review.passes}")
        >>> for issue in review.issues:
        ...     print(f"Line {issue.line_number}: {issue.explanation}")
    """
    checker = ScriptEditingChecker(pass_threshold=pass_threshold)
    return checker.review_script(script_text, script_id, script_version)


def review_script_editing_to_json(
    script_text: str,
    script_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 85,
) -> str:
    """Review script editing and return results as JSON string.

    Args:
        script_text: The script text to review
        script_id: Identifier for the script
        script_version: Version of the script
        pass_threshold: Minimum score required to pass

    Returns:
        JSON string containing the editing review results

    Example:
        >>> script = "In order to walk, I was walking down the street."
        >>> json_result = review_script_editing_to_json(script)
        >>> import json
        >>> result = json.loads(json_result)
        >>> print(result['overall_score'])
        >>> print(result['passes'])
    """
    review = review_script_editing(script_text, script_id, script_version, pass_threshold)
    return json.dumps(review.to_dict(), indent=2)


def get_editing_feedback(review: EditingReview) -> Dict[str, Any]:
    """Get formatted feedback from an editing review for script refinement.

    Args:
        review: EditingReview object

    Returns:
        Dictionary with structured feedback for script writers

    Example:
        >>> review = review_script_editing(script_text)
        >>> feedback = get_editing_feedback(review)
        >>> if not feedback['passes']:
        ...     print("Script needs revision:")
        ...     for issue in feedback['critical_issues']:
        ...         print(f"  Line {issue['line']}: {issue['explanation']}")
    """
    return {
        "script_id": review.script_id,
        "script_version": review.script_version,
        "passes": review.passes,
        "overall_score": review.overall_score,
        "threshold": review.pass_threshold,
        "summary": review.summary,
        "total_issues": len(review.issues),
        "critical_issues": [
            {
                "line": issue.line_number,
                "type": issue.issue_type.value,
                "text": issue.text,
                "suggestion": issue.suggestion,
                "explanation": issue.explanation,
            }
            for issue in review.get_critical_issues()
        ],
        "high_priority_issues": [
            {
                "line": issue.line_number,
                "type": issue.issue_type.value,
                "text": issue.text,
                "suggestion": issue.suggestion,
                "explanation": issue.explanation,
            }
            for issue in review.get_issues_by_severity(EditingSeverity.HIGH)
        ],
        "primary_concerns": review.primary_concerns,
        "quick_fixes": review.quick_fixes,
        "next_action": (
            "Proceed to Stage 19 (Title Readability)"
            if review.passes
            else "Return to Script Refinement (Stage 11)"
        ),
    }


if __name__ == "__main__":
    # Example usage
    test_script = """In order to understand the situation, we need to give consideration to all the facts.
The decision was made by the committee at this point in time.
Due to the fact that the weather was bad, the event was cancelled cancelled.
In close proximity to the building, there is a very unique statue.
And then we walked down the street and then we saw the building and so we entered.
The hero makes a decision to fight the villain in spite of the fact that he is outnumbered.
"""

    print("=== Script Editing Review ===\n")
    print("Script:")
    print(test_script)
    print("\n" + "=" * 50 + "\n")

    review = review_script_editing(test_script, script_id="test-001", script_version="v3")

    print(f"Overall Score: {review.overall_score}/100")
    print(f"Passes: {'YES' if review.passes else 'NO'}")
    print(f"Total Issues: {len(review.issues)}")
    print(f"\nSummary: {review.summary}\n")

    if review.issues:
        print("Issues Found:")
        for issue in review.issues:
            print(
                f"\nLine {issue.line_number} [{issue.severity.value.upper()}] - {issue.issue_type.value.upper()}"
            )
            print(f"  Text: '{issue.text[:60]}...'")
            print(f"  Suggestion: '{issue.suggestion[:60]}...'")
            print(f"  Explanation: {issue.explanation}")

    print("\n" + "=" * 50)
    print("\nJSON Output:")
    print(review_script_editing_to_json(test_script, script_id="test-001"))
