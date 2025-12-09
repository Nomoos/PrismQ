"""Content Grammar Review - AI-powered grammar validation for scripts.

This module implements PrismQ.T.Review.Content.Grammar for Stage 14 (MVP-014).
Provides comprehensive grammar, punctuation, spelling, syntax, and tense checking
for script content with line-by-line error detection and JSON output.

The grammar review serves as a quality gate - scripts must pass before proceeding
to Tone Review (Stage 15/MVP-015). If it fails, the script returns to refinement
with detailed feedback.

Workflow Position:
    Stage 14 (MVP-014): Grammar Review
    Content v3+ → Grammar Review → [PASS: Stage 15] or [FAIL: Content Refinement]
"""

import json
import re
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

# Import the GrammarReview model from local module
from .grammar_review import (
    GrammarIssue,
    GrammarIssueType,
    GrammarReview,
    GrammarSeverity,
)


class ScriptGrammarChecker:
    """AI-powered grammar checker for script content.

    Performs comprehensive grammar validation including:
    - Grammar and syntax errors
    - Punctuation issues
    - Spelling mistakes
    - Tense consistency
    - Subject-verb agreement
    - Capitalization errors

    Provides line-by-line error detection with specific corrections.
    """

    def __init__(self, pass_threshold: int = 85):
        """Initialize the grammar checker.

        Args:
            pass_threshold: Minimum score (0-100) required to pass review
        """
        self.pass_threshold = pass_threshold

        # Common spelling errors (could be expanded with AI/NLP library)
        self.common_spelling_errors = {
            "recieve": "receive",
            "occured": "occurred",
            "seperate": "separate",
            "definately": "definitely",
            "wierd": "weird",
            "untill": "until",
            "thier": "their",
            "teh": "the",
            "adn": "and",
            "taht": "that",
            "hte": "the",
            "nad": "and",
            "tehir": "their",
            "wich": "which",
            "whcih": "which",
            "recieved": "received",
            "begining": "beginning",
            "goverment": "government",
            "collegue": "colleague",
            "accomodate": "accommodate",
            "occassion": "occasion",
            "recomend": "recommend",
            "succesful": "successful",
            "neccessary": "necessary",
            "mispell": "misspell",
            "pronounciation": "pronunciation",
            "existance": "existence",
            "arguement": "argument",
            "miniscule": "minuscule",
            "embarass": "embarrass",
            "harrass": "harass",
            "perseverence": "perseverance",
            "priviledge": "privilege",
            "occurence": "occurrence",
            "beleive": "believe",
            "foriegn": "foreign",
            "freind": "friend",
            "guage": "gauge",
            "heighth": "height",
            "liason": "liaison",
            "maintainance": "maintenance",
            "noticable": "noticeable",
            "pasttime": "pastime",
            "rythm": "rhythm",
            "supercede": "supersede",
            "tendancy": "tendency",
            "vaccuum": "vacuum",
        }

        # Common grammar patterns
        self.subject_verb_errors = [
            (
                r"\b(I|you|we|they)\s+was\b",
                "were",
                'Subject-verb agreement: plural subjects take "were"',
            ),
            (
                r"\b(he|she|it)\s+were\b",
                "was",
                'Subject-verb agreement: singular subjects take "was"',
            ),
            (
                r"\b(I|you|we|they)\s+has\b",
                "have",
                'Subject-verb agreement: plural subjects take "have"',
            ),
            (
                r"\b(he|she|it)\s+have\b",
                "has",
                'Subject-verb agreement: singular subjects take "has"',
            ),
            (
                r"\b(I|you|we|they)\s+is\b",
                "are",
                'Subject-verb agreement: plural subjects take "are"',
            ),
            (r"\b(he|she|it)\s+are\b", "is", 'Subject-verb agreement: singular subjects take "is"'),
        ]

        # Tense mixing patterns (simplified detection)
        self.tense_patterns = {
            "past": [r"\b(walked|ran|said|went|came|saw|did|had|was|were)\b"],
            "present": [
                r"\b(walk|walks|run|runs|say|says|go|goes|come|comes|see|sees|do|does|is|are)\b"
            ],
        }

    def review_content(
        self, content_text: str, content_id: str = "script-001", script_version: str = "v3"
    ) -> GrammarReview:
        """Review a script for grammar, punctuation, spelling, syntax, and tense.

        Args:
            content_text: The script text to review
            content_id: Identifier for the script
            script_version: Version of the script (v3, v4, etc.)

        Returns:
            GrammarReview object with all detected issues
        """
        review = GrammarReview(
            content_id=content_id, script_version=script_version, pass_threshold=self.pass_threshold
        )

        # Split script into lines for line-by-line analysis
        lines = content_text.split("\n")

        # Check each line
        for line_num, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            # Check spelling
            self._check_spelling(line, line_num, review)

            # Check grammar (subject-verb agreement)
            self._check_grammar(line, line_num, review)

            # Check punctuation
            self._check_punctuation(line, line_num, review)

            # Check capitalization
            self._check_capitalization(line, line_num, review)

        # Check overall tense consistency
        self._check_tense_consistency(content_text, lines, review)

        # Calculate overall score based on issues
        review.overall_score = self._calculate_score(review)

        # Generate summary and feedback
        self._generate_feedback(review)

        return review

    def _check_spelling(self, line: str, line_num: int, review: GrammarReview) -> None:
        """Check for spelling errors in a line."""
        words = re.findall(r"\b\w+\b", line.lower())

        for word in words:
            if word in self.common_spelling_errors:
                correct_word = self.common_spelling_errors[word]

                # Find the word in the original line (preserve case)
                pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
                match = pattern.search(line)

                if match:
                    original_word = match.group()
                    # Preserve original capitalization
                    if original_word[0].isupper():
                        correct_word = correct_word.capitalize()

                    issue = GrammarIssue(
                        issue_type=GrammarIssueType.SPELLING,
                        severity=GrammarSeverity.HIGH,
                        line_number=line_num,
                        text=original_word,
                        suggestion=correct_word,
                        explanation=f"Spelling error: '{original_word}' should be '{correct_word}'",
                        confidence=95,
                    )
                    review.add_issue(issue)

    def _check_grammar(self, line: str, line_num: int, review: GrammarReview) -> None:
        """Check for grammar errors (subject-verb agreement)."""
        for pattern, correct_verb, explanation in self.subject_verb_errors:
            matches = re.finditer(pattern, line, re.IGNORECASE)

            for match in matches:
                error_text = match.group()
                # Extract subject and verb
                words = error_text.split()
                if len(words) >= 2:
                    subject = words[0]
                    wrong_verb = " ".join(words[1:])
                    suggested_text = f"{subject} {correct_verb}"

                    issue = GrammarIssue(
                        issue_type=GrammarIssueType.AGREEMENT,
                        severity=GrammarSeverity.CRITICAL,
                        line_number=line_num,
                        text=error_text,
                        suggestion=suggested_text,
                        explanation=explanation,
                        confidence=90,
                    )
                    review.add_issue(issue)

    def _check_punctuation(self, line: str, line_num: int, review: GrammarReview) -> None:
        """Check for punctuation errors."""
        stripped = line.strip()
        if not stripped:
            return

        # Skip lines that are clearly dialogue or action descriptions
        if stripped.startswith(("[", "(", "*", "-")):
            return

        # Check if sentence ends with proper punctuation
        if len(stripped) > 10 and not re.search(r"[.!?:]$", stripped):
            # Only flag if it looks like a complete sentence (has subject and verb patterns)
            if re.search(
                r"\b(I|you|he|she|it|we|they|the|a|an)\b.*\b(is|are|was|were|has|have|do|does|did)\b",
                stripped,
                re.IGNORECASE,
            ):
                issue = GrammarIssue(
                    issue_type=GrammarIssueType.PUNCTUATION,
                    severity=GrammarSeverity.MEDIUM,
                    line_number=line_num,
                    text=stripped,
                    suggestion=stripped + ".",
                    explanation="Sentence should end with proper punctuation",
                    confidence=75,
                )
                review.add_issue(issue)

        # Check for double spaces
        if "  " in line:
            issue = GrammarIssue(
                issue_type=GrammarIssueType.PUNCTUATION,
                severity=GrammarSeverity.LOW,
                line_number=line_num,
                text=line,
                suggestion=re.sub(r"\s+", " ", line),
                explanation="Remove extra spaces",
                confidence=100,
            )
            review.add_issue(issue)

    def _check_capitalization(self, line: str, line_num: int, review: GrammarReview) -> None:
        """Check for capitalization errors."""
        stripped = line.strip()
        if not stripped:
            return

        # Skip special formatting lines
        if stripped.startswith(("[", "(", "*", "-")):
            return

        # Check if sentence starts with lowercase letter
        if stripped[0].islower() and stripped[0].isalpha():
            issue = GrammarIssue(
                issue_type=GrammarIssueType.CAPITALIZATION,
                severity=GrammarSeverity.MEDIUM,
                line_number=line_num,
                text=stripped,
                suggestion=stripped[0].upper() + stripped[1:],
                explanation="Sentence should start with a capital letter",
                confidence=85,
            )
            review.add_issue(issue)

    def _check_tense_consistency(
        self, content_text: str, lines: List[str], review: GrammarReview
    ) -> None:
        """Check for tense consistency throughout the script."""
        # Count tense markers
        past_count = 0
        present_count = 0

        for pattern in self.tense_patterns["past"]:
            past_count += len(re.findall(pattern, content_text, re.IGNORECASE))

        for pattern in self.tense_patterns["present"]:
            present_count += len(re.findall(pattern, content_text, re.IGNORECASE))

        # Determine primary tense
        if past_count > present_count * 2:
            primary_tense = "past"
            inconsistent_patterns = self.tense_patterns["present"]
            tense_name = "present"
        elif present_count > past_count * 2:
            primary_tense = "present"
            inconsistent_patterns = self.tense_patterns["past"]
            tense_name = "past"
        else:
            # Mixed tense is acceptable in scripts (dialogue vs narration)
            return

        # Flag lines with inconsistent tense (only if very clear)
        for line_num, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            for pattern in inconsistent_patterns:
                if re.search(pattern, line, re.IGNORECASE) and len(line.split()) > 5:
                    # Only flag if the line has mostly the inconsistent tense
                    inconsistent_matches = len(re.findall(pattern, line, re.IGNORECASE))
                    if inconsistent_matches >= 2:
                        issue = GrammarIssue(
                            issue_type=GrammarIssueType.TENSE,
                            severity=GrammarSeverity.MEDIUM,
                            line_number=line_num,
                            text=line.strip(),
                            suggestion=f"Consider using {primary_tense} tense consistently",
                            explanation=f"Content primarily uses {primary_tense} tense, but this line uses {tense_name} tense",
                            confidence=60,
                        )
                        review.add_issue(issue)
                        break  # Only flag once per line

    def _calculate_score(self, review: GrammarReview) -> int:
        """Calculate overall grammar score based on issues.

        Args:
            review: The GrammarReview object with detected issues

        Returns:
            Score from 0-100
        """
        # Start with perfect score
        score = 100

        # Deduct points based on severity
        score -= review.critical_count * 15  # Critical: -15 points each
        score -= review.high_count * 8  # High: -8 points each
        score -= review.medium_count * 4  # Medium: -4 points each
        score -= review.low_count * 1  # Low: -1 point each

        # Ensure score doesn't go below 0
        return max(0, score)

    def _generate_feedback(self, review: GrammarReview) -> None:
        """Generate summary and feedback for the review.

        Args:
            review: The GrammarReview object to populate with feedback
        """
        total_issues = len(review.issues)

        if total_issues == 0:
            review.summary = "Excellent! No grammar issues detected. Content is technically correct."
            review.passes = True
            return

        # Generate summary
        if review.passes:
            review.summary = (
                f"Content passes grammar review with {total_issues} minor issue(s) detected."
            )
        else:
            review.summary = f"Content requires revision. {total_issues} grammar issue(s) detected, including {review.critical_count} critical error(s)."

        # Identify primary concerns
        if review.critical_count > 0:
            review.primary_concerns.append(
                f"{review.critical_count} critical grammar error(s) must be fixed"
            )

        if review.high_count > 0:
            review.primary_concerns.append(
                f"{review.high_count} high-priority issue(s) should be addressed"
            )

        # Categorize issues for quick fixes
        spelling_count = len(review.get_issues_by_type(GrammarIssueType.SPELLING))
        if spelling_count > 0:
            review.quick_fixes.append(f"Fix {spelling_count} spelling error(s)")

        punctuation_count = len(review.get_issues_by_type(GrammarIssueType.PUNCTUATION))
        if punctuation_count > 0:
            review.quick_fixes.append(f"Correct {punctuation_count} punctuation issue(s)")

        capitalization_count = len(review.get_issues_by_type(GrammarIssueType.CAPITALIZATION))
        if capitalization_count > 0:
            review.quick_fixes.append(f"Fix {capitalization_count} capitalization error(s)")


def review_content_grammar(
    content_text: str,
    content_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 85,
) -> GrammarReview:
    """Convenience function to review script grammar.

    Args:
        content_text: The script text to review
        content_id: Identifier for the script
        script_version: Version of the script
        pass_threshold: Minimum score required to pass

    Returns:
        GrammarReview object with all detected issues

    Example:
        >>> script = "I was walking down the street. He were running fast."
        >>> review = review_content_grammar(script)
        >>> print(f"Score: {review.overall_score}")
        >>> print(f"Passes: {review.passes}")
        >>> for issue in review.issues:
        ...     print(f"Line {issue.line_number}: {issue.explanation}")
    """
    checker = ScriptGrammarChecker(pass_threshold=pass_threshold)
    return checker.review_content(content_text, content_id, script_version)


def review_content_grammar_to_json(
    content_text: str,
    content_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 85,
) -> str:
    """Review script grammar and return results as JSON string.

    Args:
        content_text: The script text to review
        content_id: Identifier for the script
        script_version: Version of the script
        pass_threshold: Minimum score required to pass

    Returns:
        JSON string containing the grammar review results

    Example:
        >>> script = "I was walking. He were running."
        >>> json_result = review_content_grammar_to_json(script)
        >>> import json
        >>> result = json.loads(json_result)
        >>> print(result['overall_score'])
        >>> print(result['passes'])
    """
    review = review_content_grammar(content_text, content_id, script_version, pass_threshold)
    return json.dumps(review.to_dict(), indent=2)


def get_grammar_feedback(review: GrammarReview) -> Dict[str, Any]:
    """Get formatted feedback from a grammar review for script refinement.

    Args:
        review: GrammarReview object

    Returns:
        Dictionary with structured feedback for script writers

    Example:
        >>> review = review_content_grammar(content_text)
        >>> feedback = get_grammar_feedback(review)
        >>> if not feedback['passes']:
        ...     print("Content needs revision:")
        ...     for issue in feedback['critical_issues']:
        ...         print(f"  Line {issue['line']}: {issue['explanation']}")
    """
    return {
        "content_id": review.content_id,
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
            for issue in review.get_issues_by_severity(GrammarSeverity.HIGH)
        ],
        "primary_concerns": review.primary_concerns,
        "quick_fixes": review.quick_fixes,
        "next_action": (
            "Proceed to Stage 15 (Tone Review)"
            if review.passes
            else "Return to Content Refinement (Stage 11)"
        ),
    }


if __name__ == "__main__":
    # Example usage
    test_content = """I was walking down the street when I saw him.
He were running very fast toward the old building.
The sun was setting, and shadows grow longer.
I recieved a message on my phone.
it was important but I couldn't read it clearly"""

    print("=== Content Grammar Review ===\n")
    print("Content:")
    print(test_content)
    print("\n" + "=" * 50 + "\n")

    review = review_content_grammar(test_content, content_id="test-001", script_version="v3")

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
            print(f"  Text: '{issue.text}'")
            print(f"  Suggestion: '{issue.suggestion}'")
            print(f"  Explanation: {issue.explanation}")

    print("\n" + "=" * 50)
    print("\nJSON Output:")
    print(review_content_grammar_to_json(test_content, content_id="test-001"))
