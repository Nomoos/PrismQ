"""Script Readability Review - AI-powered voiceover readability validation for scripts.

This module implements PrismQ.T.Review.Script.Readability for Stage 20 (MVP-020).
Provides comprehensive readability checking for voiceover suitability including
natural flow, pronunciation, pacing, and spoken-word clarity.

The readability review serves as the final quality gate for scripts - scripts must
pass before proceeding to Expert Review (Stage 21/MVP-021). If it fails, the script
returns to refinement with detailed feedback focused on spoken-word delivery.

Workflow Position:
    Stage 20 (MVP-020): Script Readability Review
    Script v3+ → Readability Review → [PASS: Stage 21] or [FAIL: Script Refinement]
"""

import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ReadabilityIssueType(Enum):
    """Types of readability issues that can be detected."""

    PRONUNCIATION = "pronunciation"  # Hard to pronounce words
    PACING = "pacing"  # Pacing issues for voiceover
    FLOW = "flow"  # Natural flow problems
    MOUTHFEEL = "mouthfeel"  # Difficult to speak aloud
    CLARITY = "clarity"  # Unclear when spoken
    RHYTHM = "rhythm"  # Poor spoken rhythm
    BREATH = "breath"  # Insufficient breathing points
    TONGUE_TWISTER = "tongue_twister"  # Difficult sound combinations


class ReadabilitySeverity(Enum):
    """Severity levels for readability issues."""

    CRITICAL = "critical"  # Must be fixed - impossible to narrate
    HIGH = "high"  # Should be fixed - difficult to narrate
    MEDIUM = "medium"  # Recommended to fix - awkward to narrate
    LOW = "low"  # Minor issue - slight improvement possible


@dataclass
class ReadabilityIssue:
    """Individual readability issue found in the script."""

    issue_type: ReadabilityIssueType
    severity: ReadabilitySeverity
    line_number: int
    text: str  # The problematic text
    suggestion: str  # How to improve it
    explanation: str  # Why this is a readability issue
    confidence: int = 85  # 0-100, AI confidence in detection


@dataclass
class ReadabilityReview:
    """AI-powered readability review for voiceover suitability.

    ReadabilityReview provides comprehensive voiceover readability validation with:
    - Overall readability score (0-100%)
    - Natural flow assessment
    - Pronunciation difficulty detection
    - Pacing and rhythm analysis
    - Mouthfeel and ease-of-speaking evaluation
    - Pass/fail determination for workflow progression

    The review serves as the final script quality gate - script must pass readability
    review before proceeding to Expert Review (Stage 21). If it fails, script
    returns to refinement (Stage 11) with voiceover-focused feedback.

    Attributes:
        script_id: Identifier of the reviewed script
        script_version: Version of script being reviewed (v3, v4, etc.)
        overall_score: Overall readability score (0-100)
        pass_threshold: Minimum score required to pass (default 85)
        passes: Whether review passes (score >= threshold)

        Issue Tracking:
            issues: List of all detected readability issues
            critical_count: Number of critical issues
            high_count: Number of high severity issues
            medium_count: Number of medium severity issues
            low_count: Number of low severity issues

        Readability Scores:
            pronunciation_score: Pronunciation ease score (0-100)
            pacing_score: Pacing quality score (0-100)
            flow_score: Natural flow score (0-100)
            mouthfeel_score: Ease of speaking score (0-100)

        Review Metadata:
            reviewer_id: AI reviewer identifier
            reviewed_at: Timestamp of review
            confidence_score: AI confidence in review (0-100)

        Feedback:
            summary: Overall assessment summary
            primary_concerns: Main issues to address
            voiceover_notes: Specific notes for voiceover delivery
            notes: Additional reviewer notes

    Example:
        >>> review = ReadabilityReview(
        ...     script_id="script-001",
        ...     script_version="v3",
        ...     overall_score=90
        ... )
        >>> review.add_issue(ReadabilityIssue(
        ...     issue_type=ReadabilityIssueType.PRONUNCIATION,
        ...     severity=ReadabilitySeverity.HIGH,
        ...     line_number=15,
        ...     text="The phenomenon of phosphorescence perplexed physicists",
        ...     suggestion="The glowing effect puzzled scientists",
        ...     explanation="Too many 'ph' and 'p' sounds create a tongue twister"
        ... ))
        >>> if review.passes:
        ...     print("Ready for Stage 21: Expert Review")
        ... else:
        ...     print("Return to Stage 11: Script Refinement")
    """

    script_id: str
    script_version: str = "v3"
    overall_score: int = 0  # 0-100
    pass_threshold: int = 85  # Minimum score to pass
    passes: bool = True  # Whether review passes

    # Issue Tracking
    issues: List[ReadabilityIssue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Readability Scores
    pronunciation_score: int = 100  # 0-100
    pacing_score: int = 100  # 0-100
    flow_score: int = 100  # 0-100
    mouthfeel_score: int = 100  # 0-100

    # Review Metadata
    reviewer_id: str = "AI-ReadabilityReviewer-001"
    reviewed_at: Optional[str] = None
    confidence_score: int = 85  # 0-100

    # Feedback
    summary: str = ""
    primary_concerns: List[str] = field(default_factory=list)
    voiceover_notes: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps and computed fields."""
        if self.reviewed_at is None:
            self.reviewed_at = datetime.now().isoformat()

        # Calculate pass/fail status
        self._recalculate_pass_status()

    def add_issue(self, issue: ReadabilityIssue) -> None:
        """Add a readability issue to the review.

        Args:
            issue: ReadabilityIssue to add
        """
        self.issues.append(issue)

        # Update severity counts
        if issue.severity == ReadabilitySeverity.CRITICAL:
            self.critical_count += 1
        elif issue.severity == ReadabilitySeverity.HIGH:
            self.high_count += 1
        elif issue.severity == ReadabilitySeverity.MEDIUM:
            self.medium_count += 1
        elif issue.severity == ReadabilitySeverity.LOW:
            self.low_count += 1

        # Recalculate pass status
        self._recalculate_pass_status()

    def _recalculate_pass_status(self) -> None:
        """Recalculate pass/fail status based on issues and scores."""
        # Fail if any critical issues
        if self.critical_count > 0:
            self.passes = False
        else:
            self.passes = self.overall_score >= self.pass_threshold

    def get_issues_by_severity(self, severity: ReadabilitySeverity) -> List[ReadabilityIssue]:
        """Get all issues of a specific severity.

        Args:
            severity: The severity level to filter by

        Returns:
            List of issues with the specified severity
        """
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_type(self, issue_type: ReadabilityIssueType) -> List[ReadabilityIssue]:
        """Get all issues of a specific type.

        Args:
            issue_type: The issue type to filter by

        Returns:
            List of issues with the specified type
        """
        return [issue for issue in self.issues if issue.issue_type == issue_type]

    def get_critical_issues(self) -> List[ReadabilityIssue]:
        """Get all critical issues that must be fixed.

        Returns:
            List of critical severity issues
        """
        return self.get_issues_by_severity(ReadabilitySeverity.CRITICAL)

    def get_high_priority_issues(self) -> List[ReadabilityIssue]:
        """Get all high priority issues.

        Returns:
            List of critical and high severity issues
        """
        critical = self.get_issues_by_severity(ReadabilitySeverity.CRITICAL)
        high = self.get_issues_by_severity(ReadabilitySeverity.HIGH)
        return critical + high

    def to_dict(self) -> Dict[str, Any]:
        """Convert ReadabilityReview to dictionary representation.

        Returns:
            Dictionary containing all fields with Enums converted to strings
        """
        data = asdict(self)

        # Convert issues
        data["issues"] = [
            {
                **asdict(issue),
                "issue_type": issue.issue_type.value,
                "severity": issue.severity.value,
            }
            for issue in self.issues
        ]

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReadabilityReview":
        """Create ReadabilityReview from dictionary.

        Args:
            data: Dictionary containing ReadabilityReview fields

        Returns:
            ReadabilityReview instance
        """
        # Convert issues
        issues = []
        for issue_data in data.get("issues", []):
            issue_type = ReadabilityIssueType(issue_data["issue_type"])
            severity = ReadabilitySeverity(issue_data["severity"])
            issues.append(
                ReadabilityIssue(
                    issue_type=issue_type,
                    severity=severity,
                    line_number=issue_data["line_number"],
                    text=issue_data["text"],
                    suggestion=issue_data["suggestion"],
                    explanation=issue_data["explanation"],
                    confidence=issue_data.get("confidence", 85),
                )
            )

        return cls(
            script_id=data["script_id"],
            script_version=data.get("script_version", "v3"),
            overall_score=data.get("overall_score", 0),
            pass_threshold=data.get("pass_threshold", 85),
            passes=data.get("passes", True),
            issues=issues,
            critical_count=data.get("critical_count", 0),
            high_count=data.get("high_count", 0),
            medium_count=data.get("medium_count", 0),
            low_count=data.get("low_count", 0),
            pronunciation_score=data.get("pronunciation_score", 100),
            pacing_score=data.get("pacing_score", 100),
            flow_score=data.get("flow_score", 100),
            mouthfeel_score=data.get("mouthfeel_score", 100),
            reviewer_id=data.get("reviewer_id", "AI-ReadabilityReviewer-001"),
            reviewed_at=data.get("reviewed_at"),
            confidence_score=data.get("confidence_score", 85),
            summary=data.get("summary", ""),
            primary_concerns=data.get("primary_concerns", []),
            voiceover_notes=data.get("voiceover_notes", []),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """String representation of ReadabilityReview."""
        return (
            f"ReadabilityReview(script={self.script_id}, "
            f"version={self.script_version}, "
            f"score={self.overall_score}%, "
            f"passes={'YES' if self.passes else 'NO'}, "
            f"issues={len(self.issues)})"
        )


class ScriptReadabilityChecker:
    """AI-powered readability checker for script voiceover suitability.

    Performs comprehensive readability validation including:
    - Pronunciation difficulty detection
    - Pacing and rhythm analysis
    - Natural flow assessment
    - Mouthfeel (ease of speaking) evaluation
    - Breath point identification
    - Tongue twister detection
    """

    # Scoring penalties
    PENALTY_CRITICAL = 20
    PENALTY_HIGH = 12
    PENALTY_MEDIUM = 6
    PENALTY_LOW = 2

    # Difficult consonant clusters
    DIFFICULT_CLUSTERS = [
        r"\b\w*sths\w*\b",  # sixths, lengths
        r"\b\w*[bcdfghjklmnpqrstvwxz]{4,}\w*\b",  # 4+ consonants in a row
        r"\b\w*ngths\w*\b",  # strengths, lengths
    ]

    # Tongue twister patterns (alliteration with difficult sounds)
    TONGUE_TWISTER_PATTERNS = [
        (r"\b([pP]\w+\s+){3,}", "p"),  # Peter Piper picked...
        (r"\b([sS]\w+\s+){3,}", "s"),  # She sells seashells...
        (r"\b([tT]\w+\s+){3,}", "t"),  # Toy boat, toy boat...
        (r"\b([fF]\w+\s+){3,}", "f"),  # Freshly fried fish...
        (r"\b([bB]\w+\s+){3,}", "b"),  # Big black bug...
    ]

    # Complex/formal words that are hard to speak naturally
    COMPLEX_WORDS = {
        "phenomenon": "effect",
        "phosphorescence": "glow",
        "methodology": "method",
        "functionality": "function",
        "implementation": "setup",
        "aforementioned": "mentioned",
        "subsequently": "then",
        "nevertheless": "however",
        "notwithstanding": "despite",
        "contemporaneous": "current",
        "unequivocally": "clearly",
        "indubitably": "certainly",
        "quintessential": "perfect",
        "particularly": "especially",
        "specifically": "exactly",
    }

    # Long sentence thresholds for voiceover
    MAX_WORDS_PER_BREATH = 15  # Maximum comfortable words in one breath
    LONG_SENTENCE_WORDS = 20  # Flag sentences longer than this

    def __init__(self, pass_threshold: int = 85):
        """Initialize the readability checker.

        Args:
            pass_threshold: Minimum score (0-100) required to pass review
        """
        self.pass_threshold = pass_threshold

    def review_script(
        self, script_text: str, script_id: str = "script-001", script_version: str = "v3"
    ) -> ReadabilityReview:
        """Review a script for voiceover readability.

        Args:
            script_text: The script text to review
            script_id: Identifier for the script
            script_version: Version of the script (v3, v4, etc.)

        Returns:
            ReadabilityReview object with all detected issues
        """
        review = ReadabilityReview(
            script_id=script_id, script_version=script_version, pass_threshold=self.pass_threshold
        )

        # Split script into lines for line-by-line analysis
        lines = script_text.split("\n")

        # Check each line
        for line_num, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            # Skip stage directions and formatting
            if line.strip().startswith(("[", "(", "*", "INT.", "EXT.")):
                continue

            # Check for pronunciation difficulties
            self._check_pronunciation(line, line_num, review)

            # Check for tongue twisters
            self._check_tongue_twisters(line, line_num, review)

            # Check for pacing issues (sentence length)
            self._check_pacing(line, line_num, review)

            # Check for breath points
            self._check_breath_points(line, line_num, review)

            # Check for complex words
            self._check_complex_words(line, line_num, review)

        # Calculate scores
        review.pronunciation_score = self._calculate_pronunciation_score(review)
        review.pacing_score = self._calculate_pacing_score(review)
        review.flow_score = self._calculate_flow_score(review)
        review.mouthfeel_score = self._calculate_mouthfeel_score(review)

        # Calculate overall score
        review.overall_score = int(
            (review.pronunciation_score * 0.30)
            + (review.pacing_score * 0.25)
            + (review.flow_score * 0.25)
            + (review.mouthfeel_score * 0.20)
        )

        # Recalculate pass status with final score
        review._recalculate_pass_status()

        # Generate summary and feedback
        self._generate_feedback(review)

        return review

    def _check_pronunciation(self, line: str, line_num: int, review: ReadabilityReview) -> None:
        """Check for difficult pronunciation patterns."""
        for pattern in self.DIFFICULT_CLUSTERS:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                word = match.group()
                issue = ReadabilityIssue(
                    issue_type=ReadabilityIssueType.PRONUNCIATION,
                    severity=ReadabilitySeverity.HIGH,
                    line_number=line_num,
                    text=line.strip(),
                    suggestion=f"Consider simplifying or replacing '{word}' with easier pronunciation",
                    explanation=f"Word '{word}' has a difficult consonant cluster that's hard to pronounce clearly",
                    confidence=80,
                )
                review.add_issue(issue)

    def _check_tongue_twisters(self, line: str, line_num: int, review: ReadabilityReview) -> None:
        """Check for tongue twister patterns (alliteration with difficult sounds)."""
        for pattern, sound in self.TONGUE_TWISTER_PATTERNS:
            if re.search(pattern, line):
                issue = ReadabilityIssue(
                    issue_type=ReadabilityIssueType.TONGUE_TWISTER,
                    severity=ReadabilitySeverity.MEDIUM,
                    line_number=line_num,
                    text=line.strip(),
                    suggestion=f"Reduce repetition of '{sound}' sound for easier voiceover delivery",
                    explanation=f"Multiple words starting with '{sound}' create a tongue twister effect",
                    confidence=75,
                )
                review.add_issue(issue)
                break  # Only flag once per line

    def _check_pacing(self, line: str, line_num: int, review: ReadabilityReview) -> None:
        """Check for pacing issues based on sentence length."""
        stripped = line.strip()
        if not stripped:
            return

        # Count words
        words = stripped.split()
        word_count = len(words)

        # Check for overly long sentences
        if word_count > self.LONG_SENTENCE_WORDS:
            # Count commas for breath points
            comma_count = stripped.count(",")

            # If no commas in a long sentence, it's harder to narrate
            if comma_count == 0:
                severity = ReadabilitySeverity.HIGH
                explanation = f"Long sentence ({word_count} words) with no breathing pauses makes voiceover difficult"
            else:
                severity = ReadabilitySeverity.MEDIUM
                explanation = (
                    f"Long sentence ({word_count} words) - consider breaking into shorter segments"
                )

            issue = ReadabilityIssue(
                issue_type=ReadabilityIssueType.PACING,
                severity=severity,
                line_number=line_num,
                text=stripped,
                suggestion="Break into shorter sentences or add natural pauses",
                explanation=explanation,
                confidence=85,
            )
            review.add_issue(issue)

    def _check_breath_points(self, line: str, line_num: int, review: ReadabilityReview) -> None:
        """Check for adequate breathing points in the script."""
        stripped = line.strip()
        if not stripped:
            return

        # Split by natural breath points (periods, commas, etc.)
        segments = re.split(r"[.,;:!?—]", stripped)

        for segment in segments:
            words = segment.strip().split()
            if len(words) > self.MAX_WORDS_PER_BREATH:
                issue = ReadabilityIssue(
                    issue_type=ReadabilityIssueType.BREATH,
                    severity=ReadabilitySeverity.MEDIUM,
                    line_number=line_num,
                    text=stripped,
                    suggestion=f"Add a natural pause or comma after {self.MAX_WORDS_PER_BREATH} words",
                    explanation=f"Segment has {len(words)} words without a breath point (comfortable max is {self.MAX_WORDS_PER_BREATH})",
                    confidence=80,
                )
                review.add_issue(issue)
                break  # Only flag once per line

    def _check_complex_words(self, line: str, line_num: int, review: ReadabilityReview) -> None:
        """Check for complex words that are hard to speak naturally."""
        line_lower = line.lower()

        for complex_word, simple_word in self.COMPLEX_WORDS.items():
            if complex_word in line_lower:
                issue = ReadabilityIssue(
                    issue_type=ReadabilityIssueType.MOUTHFEEL,
                    severity=ReadabilitySeverity.LOW,
                    line_number=line_num,
                    text=line.strip(),
                    suggestion=f"Consider replacing '{complex_word}' with '{simple_word}' for easier voiceover",
                    explanation=f"Word '{complex_word}' is complex and formal; simpler alternatives flow better in narration",
                    confidence=70,
                )
                review.add_issue(issue)
                break  # Only flag one complex word per line

    def _calculate_pronunciation_score(self, review: ReadabilityReview) -> int:
        """Calculate pronunciation ease score."""
        pronunciation_issues = len(
            [i for i in review.issues if i.issue_type == ReadabilityIssueType.PRONUNCIATION]
        )

        if pronunciation_issues == 0:
            return 100
        elif pronunciation_issues == 1:
            return 85
        elif pronunciation_issues == 2:
            return 70
        else:
            return max(50, 100 - (pronunciation_issues * 12))

    def _calculate_pacing_score(self, review: ReadabilityReview) -> int:
        """Calculate pacing quality score."""
        pacing_issues = len(
            [
                i
                for i in review.issues
                if i.issue_type in [ReadabilityIssueType.PACING, ReadabilityIssueType.BREATH]
            ]
        )

        if pacing_issues == 0:
            return 100
        elif pacing_issues <= 2:
            return 85
        else:
            return max(60, 100 - (pacing_issues * 8))

    def _calculate_flow_score(self, review: ReadabilityReview) -> int:
        """Calculate natural flow score."""
        flow_issues = len(
            [
                i
                for i in review.issues
                if i.issue_type in [ReadabilityIssueType.FLOW, ReadabilityIssueType.TONGUE_TWISTER]
            ]
        )

        if flow_issues == 0:
            return 100
        elif flow_issues <= 2:
            return 88
        else:
            return max(65, 100 - (flow_issues * 10))

    def _calculate_mouthfeel_score(self, review: ReadabilityReview) -> int:
        """Calculate ease of speaking (mouthfeel) score."""
        mouthfeel_issues = len(
            [i for i in review.issues if i.issue_type == ReadabilityIssueType.MOUTHFEEL]
        )

        if mouthfeel_issues == 0:
            return 100
        elif mouthfeel_issues <= 3:
            return 90
        else:
            return max(70, 100 - (mouthfeel_issues * 5))

    def _generate_feedback(self, review: ReadabilityReview) -> None:
        """Generate summary and feedback for the review."""
        total_issues = len(review.issues)

        if total_issues == 0:
            review.summary = "Excellent! Script is perfectly suited for voiceover. Natural flow, easy pronunciation, and good pacing throughout."
            review.passes = True
            return

        # Generate summary
        if review.passes:
            review.summary = f"Script passes readability review with {total_issues} minor issue(s) detected. Ready for voiceover with minimal adjustments."
        else:
            review.summary = f"Script requires revision for voiceover suitability. {total_issues} readability issue(s) detected, including {review.critical_count} critical issue(s)."

        # Identify primary concerns
        if review.critical_count > 0:
            review.primary_concerns.append(
                f"{review.critical_count} critical voiceover issue(s) must be fixed"
            )

        if review.high_count > 0:
            review.primary_concerns.append(
                f"{review.high_count} high-priority pronunciation/pacing issue(s)"
            )

        # Categorize issues for voiceover notes
        pronunciation_count = len(
            [i for i in review.issues if i.issue_type == ReadabilityIssueType.PRONUNCIATION]
        )
        if pronunciation_count > 0:
            review.voiceover_notes.append(
                f"{pronunciation_count} pronunciation difficult{'y' if pronunciation_count == 1 else 'ies'}"
            )

        pacing_count = len(
            [i for i in review.issues if i.issue_type == ReadabilityIssueType.PACING]
        )
        if pacing_count > 0:
            review.voiceover_notes.append(f"{pacing_count} pacing issue(s)")

        breath_count = len(
            [i for i in review.issues if i.issue_type == ReadabilityIssueType.BREATH]
        )
        if breath_count > 0:
            review.voiceover_notes.append(f"{breath_count} breathing point(s) needed")

        twister_count = len(
            [i for i in review.issues if i.issue_type == ReadabilityIssueType.TONGUE_TWISTER]
        )
        if twister_count > 0:
            review.voiceover_notes.append(f"{twister_count} tongue twister(s) detected")


def review_script_readability(
    script_text: str,
    script_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 85,
) -> ReadabilityReview:
    """Convenience function to review script readability for voiceover.

    Args:
        script_text: The script text to review
        script_id: Identifier for the script
        script_version: Version of the script
        pass_threshold: Minimum score required to pass

    Returns:
        ReadabilityReview object with all detected issues

    Example:
        >>> script = "Peter Piper picked a peck of particularly problematic peppers."
        >>> review = review_script_readability(script)
        >>> print(f"Score: {review.overall_score}")
        >>> print(f"Passes: {review.passes}")
        >>> for issue in review.issues:
        ...     print(f"Line {issue.line_number}: {issue.explanation}")
    """
    checker = ScriptReadabilityChecker(pass_threshold=pass_threshold)
    return checker.review_script(script_text, script_id, script_version)


def review_script_readability_to_json(
    script_text: str,
    script_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 85,
) -> str:
    """Review script readability and return results as JSON string.

    Args:
        script_text: The script text to review
        script_id: Identifier for the script
        script_version: Version of the script
        pass_threshold: Minimum score required to pass

    Returns:
        JSON string containing the readability review results

    Example:
        >>> script = "The phenomenon of phosphorescence perplexed physicists."
        >>> json_result = review_script_readability_to_json(script)
        >>> import json
        >>> result = json.loads(json_result)
        >>> print(result['overall_score'])
        >>> print(result['passes'])
    """
    import json

    review = review_script_readability(script_text, script_id, script_version, pass_threshold)
    return json.dumps(review.to_dict(), indent=2)


def get_readability_feedback(review: ReadabilityReview) -> Dict[str, Any]:
    """Get formatted feedback from a readability review for script refinement.

    Args:
        review: ReadabilityReview object

    Returns:
        Dictionary with structured feedback for script writers

    Example:
        >>> review = review_script_readability(script_text)
        >>> feedback = get_readability_feedback(review)
        >>> if not feedback['passes']:
        ...     print("Script needs voiceover revision:")
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
            for issue in review.get_issues_by_severity(ReadabilitySeverity.HIGH)
        ],
        "pronunciation_score": review.pronunciation_score,
        "pacing_score": review.pacing_score,
        "flow_score": review.flow_score,
        "mouthfeel_score": review.mouthfeel_score,
        "primary_concerns": review.primary_concerns,
        "voiceover_notes": review.voiceover_notes,
        "next_action": (
            "Proceed to Stage 21 (Expert Review)"
            if review.passes
            else "Return to Script Refinement (Stage 11)"
        ),
    }


if __name__ == "__main__":
    # Example usage
    test_script = """Peter Piper picked a peck of particularly problematic peppers from the phosphorescent patch.
The phenomenon of phosphorescence perplexed physicists persistently pursuing explanations.
This is a very long sentence that goes on and on without any natural pauses or breathing points making it extremely difficult for a voiceover artist to deliver smoothly and naturally.
Subsequently, the methodology employed in the implementation of the aforementioned functionality was unequivocally quintessential.
Short line here.
She sells seashells by the seashore, specifically selecting superior specimens.
The strengths of the sixth method remained unclear."""

    print("=== Script Readability Review for Voiceover ===\n")
    print("Script:")
    print(test_script)
    print("\n" + "=" * 50 + "\n")

    review = review_script_readability(test_script, script_id="test-001", script_version="v3")

    print(f"Overall Score: {review.overall_score}/100")
    print(f"Pronunciation Score: {review.pronunciation_score}/100")
    print(f"Pacing Score: {review.pacing_score}/100")
    print(f"Flow Score: {review.flow_score}/100")
    print(f"Mouthfeel Score: {review.mouthfeel_score}/100")
    print(f"Passes: {'YES' if review.passes else 'NO'}")
    print(f"Total Issues: {len(review.issues)}")
    print(f"\nSummary: {review.summary}\n")

    if review.voiceover_notes:
        print("Voiceover Notes:")
        for note in review.voiceover_notes:
            print(f"  - {note}")
        print()

    if review.issues:
        print("Issues Found:")
        for issue in review.issues:
            print(
                f"\nLine {issue.line_number} [{issue.severity.value.upper()}] - {issue.issue_type.value.upper()}"
            )
            print(f"  Text: '{issue.text[:80]}...'")
            print(f"  Suggestion: {issue.suggestion}")
            print(f"  Explanation: {issue.explanation}")

    print("\n" + "=" * 50)
    print("\nJSON Output (first 800 chars):")
    json_output = review_script_readability_to_json(test_script, script_id="test-001")
    print(json_output[:800] + "...")
