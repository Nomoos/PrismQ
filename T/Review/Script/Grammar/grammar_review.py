"""Grammar Review model for PrismQ AI-powered script grammar validation.

This module defines the GrammarReview data model for AI-powered grammar and
syntax validation of script content. The review checks for technical correctness
before deeper content and style reviews.

The GrammarReview model enables:
- Grammar and syntax error detection
- Punctuation and spelling validation
- Tense and person consistency checking
- Sentence structure evaluation
- Feedback for script refinement

Workflow Position:
    Stage 14 (MVP-014): Grammar Review
    Script v3+ → GrammarReview (AI Reviewer) → Script Refinement (if fails) → Stage 15
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class GrammarIssueType(Enum):
    """Types of grammar issues that can be detected."""

    GRAMMAR = "grammar"  # General grammar errors
    PUNCTUATION = "punctuation"  # Punctuation errors
    SPELLING = "spelling"  # Spelling mistakes
    SYNTAX = "syntax"  # Sentence structure issues
    TENSE = "tense"  # Tense inconsistency
    AGREEMENT = "agreement"  # Subject-verb agreement
    CAPITALIZATION = "capitalization"  # Capitalization errors


class GrammarSeverity(Enum):
    """Severity levels for grammar issues."""

    CRITICAL = "critical"  # Must be fixed
    HIGH = "high"  # Should be fixed
    MEDIUM = "medium"  # Recommended to fix
    LOW = "low"  # Minor issue


@dataclass
class GrammarIssue:
    """Individual grammar issue found in the script."""

    issue_type: GrammarIssueType
    severity: GrammarSeverity
    line_number: int
    text: str  # The problematic text
    suggestion: str  # Suggested correction
    explanation: str  # Why this is an issue
    confidence: int = 85  # 0-100, AI confidence in detection


@dataclass
class GrammarReview:
    """AI-powered grammar review with error detection and suggestions.

    GrammarReview provides comprehensive grammar and syntax validation with:
    - Overall correctness score (0-100%)
    - Categorized issue detection
    - Line-by-line error identification
    - Suggested corrections with explanations
    - Severity-based prioritization
    - Pass/fail determination for workflow progression

    The review serves as a quality gate - script must pass grammar review
    before proceeding to Tone Review (Stage 15). If it fails, script returns
    to refinement (Stage 11) with grammar feedback.

    Attributes:
        script_id: Identifier of the reviewed script
        script_version: Version of script being reviewed (v3, v4, etc.)
        overall_score: Overall grammar correctness score (0-100)
        pass_threshold: Minimum score required to pass (default 85)
        passes: Whether review passes (score >= threshold)

        Issue Tracking:
            issues: List of all detected grammar issues
            critical_count: Number of critical issues
            high_count: Number of high severity issues
            medium_count: Number of medium severity issues
            low_count: Number of low severity issues

        Review Metadata:
            reviewer_id: AI reviewer identifier
            reviewed_at: Timestamp of review
            confidence_score: AI confidence in review (0-100)

        Feedback:
            summary: Overall assessment summary
            primary_concerns: Main issues to address
            quick_fixes: Easy improvements
            notes: Additional reviewer notes

    Example:
        >>> review = GrammarReview(
        ...     script_id="script-001",
        ...     script_version="v3",
        ...     overall_score=92
        ... )
        >>> review.add_issue(GrammarIssue(
        ...     issue_type=GrammarIssueType.SPELLING,
        ...     severity=GrammarSeverity.HIGH,
        ...     line_number=15,
        ...     text="recieve",
        ...     suggestion="receive",
        ...     explanation="Common spelling error"
        ... ))
        >>> if review.passes:
        ...     print("Ready for Stage 15: Tone Review")
        ... else:
        ...     print("Return to Stage 11: Script Refinement")
    """

    script_id: str
    script_version: str = "v3"
    overall_score: int = 0  # 0-100
    pass_threshold: int = 85  # Minimum score to pass
    passes: bool = True  # Whether review passes

    # Issue Tracking
    issues: List[GrammarIssue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Review Metadata
    reviewer_id: str = "AI-GrammarReviewer-001"
    reviewed_at: Optional[str] = None
    confidence_score: int = 90  # 0-100

    # Feedback
    summary: str = ""
    primary_concerns: List[str] = field(default_factory=list)
    quick_fixes: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps and computed fields."""
        if self.reviewed_at is None:
            self.reviewed_at = datetime.now().isoformat()

        # Calculate pass/fail status
        self._recalculate_pass_status()

    def add_issue(self, issue: GrammarIssue) -> None:
        """Add a grammar issue to the review.

        Args:
            issue: GrammarIssue to add
        """
        self.issues.append(issue)

        # Update severity counts
        if issue.severity == GrammarSeverity.CRITICAL:
            self.critical_count += 1
        elif issue.severity == GrammarSeverity.HIGH:
            self.high_count += 1
        elif issue.severity == GrammarSeverity.MEDIUM:
            self.medium_count += 1
        elif issue.severity == GrammarSeverity.LOW:
            self.low_count += 1

        # Recalculate pass status
        self._recalculate_pass_status()

    def _recalculate_pass_status(self) -> None:
        """Recalculate pass/fail status based on issues."""
        # Fail if any critical issues
        if self.critical_count > 0:
            self.passes = False
        else:
            self.passes = self.overall_score >= self.pass_threshold

    def get_issues_by_severity(self, severity: GrammarSeverity) -> List[GrammarIssue]:
        """Get all issues of a specific severity.

        Args:
            severity: The severity level to filter by

        Returns:
            List of issues with the specified severity
        """
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_type(self, issue_type: GrammarIssueType) -> List[GrammarIssue]:
        """Get all issues of a specific type.

        Args:
            issue_type: The issue type to filter by

        Returns:
            List of issues with the specified type
        """
        return [issue for issue in self.issues if issue.issue_type == issue_type]

    def get_critical_issues(self) -> List[GrammarIssue]:
        """Get all critical issues that must be fixed.

        Returns:
            List of critical severity issues
        """
        return self.get_issues_by_severity(GrammarSeverity.CRITICAL)

    def get_high_priority_issues(self) -> List[GrammarIssue]:
        """Get all high priority issues.

        Returns:
            List of critical and high severity issues
        """
        critical = self.get_issues_by_severity(GrammarSeverity.CRITICAL)
        high = self.get_issues_by_severity(GrammarSeverity.HIGH)
        return critical + high

    def to_dict(self) -> Dict[str, Any]:
        """Convert GrammarReview to dictionary representation.

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
    def from_dict(cls, data: Dict[str, Any]) -> "GrammarReview":
        """Create GrammarReview from dictionary.

        Args:
            data: Dictionary containing GrammarReview fields

        Returns:
            GrammarReview instance
        """
        # Convert issues
        issues = []
        for issue_data in data.get("issues", []):
            issue_type = GrammarIssueType(issue_data["issue_type"])
            severity = GrammarSeverity(issue_data["severity"])
            issues.append(
                GrammarIssue(
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
            reviewer_id=data.get("reviewer_id", "AI-GrammarReviewer-001"),
            reviewed_at=data.get("reviewed_at"),
            confidence_score=data.get("confidence_score", 90),
            summary=data.get("summary", ""),
            primary_concerns=data.get("primary_concerns", []),
            quick_fixes=data.get("quick_fixes", []),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """String representation of GrammarReview."""
        return (
            f"GrammarReview(script={self.script_id}, "
            f"version={self.script_version}, "
            f"score={self.overall_score}%, "
            f"passes={'YES' if self.passes else 'NO'}, "
            f"issues={len(self.issues)})"
        )
