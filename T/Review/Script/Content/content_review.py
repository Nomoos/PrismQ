"""Content Review model for PrismQ AI-powered script content validation.

This module defines the ContentReview data model for AI-powered narrative
and content validation of script content. The review checks for story logic,
plot coherence, character motivation, and pacing.

The ContentReview model enables:
- Logic gap detection
- Plot issue identification
- Character motivation analysis
- Pacing evaluation
- Narrative coherence verification
- Feedback for script refinement

Workflow Position:
    Stage 16 (MVP-016): Content Review
    Script v3+ → ContentReview (AI Reviewer) → Script Refinement (if fails) → Stage 17
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ContentIssueType(Enum):
    """Types of content issues that can be detected."""

    LOGIC_GAP = "logic_gap"  # Missing or unclear logic
    PLOT_ISSUE = "plot_issue"  # Plot holes or inconsistencies
    CHARACTER_MOTIVATION = "character_motivation"  # Unclear or inconsistent motivation
    PACING = "pacing"  # Pacing problems (too slow/fast)
    NARRATIVE_COHERENCE = "narrative_coherence"  # Story doesn't flow well
    SCENE_ORDERING = "scene_ordering"  # Scene sequence issues
    STRUCTURAL = "structural"  # Overall structural problems


class ContentSeverity(Enum):
    """Severity levels for content issues."""

    CRITICAL = "critical"  # Must be fixed - breaks story
    HIGH = "high"  # Should be fixed - major impact
    MEDIUM = "medium"  # Recommended to fix - moderate impact
    LOW = "low"  # Minor issue - polish


@dataclass
class ContentIssue:
    """Individual content issue found in the script."""

    issue_type: ContentIssueType
    severity: ContentSeverity
    section: str  # Section/scene identifier
    description: str  # What the issue is
    suggestion: str  # How to fix it
    impact: str  # Impact on story/narrative
    confidence: int = 85  # 0-100, AI confidence in detection


@dataclass
class ContentReview:
    """AI-powered content review with narrative analysis and suggestions.

    ContentReview provides comprehensive narrative and content validation with:
    - Overall narrative coherence score (0-100%)
    - Categorized issue detection
    - Logic gap identification
    - Plot issue detection
    - Character motivation analysis
    - Pacing evaluation
    - Suggested improvements with impact analysis
    - Severity-based prioritization
    - Pass/fail determination for workflow progression

    The review serves as a quality gate - script must pass content review
    before proceeding to Consistency Review (Stage 17). If it fails, script
    returns to refinement (Stage 11) with content feedback.

    Attributes:
        script_id: Identifier of the reviewed script
        script_version: Version of script being reviewed (v3, v4, etc.)
        overall_score: Overall narrative coherence score (0-100)
        pass_threshold: Minimum score required to pass (default 75)
        passes: Whether review passes (score >= threshold)

        Issue Tracking:
            issues: List of all detected content issues
            critical_count: Number of critical issues
            high_count: Number of high severity issues
            medium_count: Number of medium severity issues
            low_count: Number of low severity issues

        Content Analysis:
            logic_score: Logic consistency score (0-100)
            plot_score: Plot coherence score (0-100)
            character_score: Character motivation score (0-100)
            pacing_score: Pacing quality score (0-100)

        Review Metadata:
            reviewer_id: AI reviewer identifier
            reviewed_at: Timestamp of review
            confidence_score: AI confidence in review (0-100)

        Feedback:
            summary: Overall assessment summary
            primary_concerns: Main issues to address
            strengths: Story strengths identified
            notes: Additional reviewer notes

    Example:
        >>> review = ContentReview(
        ...     script_id="script-001",
        ...     script_version="v3",
        ...     overall_score=85,
        ...     logic_score=90,
        ...     plot_score=85,
        ...     character_score=80,
        ...     pacing_score=85
        ... )
        >>> review.add_issue(ContentIssue(
        ...     issue_type=ContentIssueType.LOGIC_GAP,
        ...     severity=ContentSeverity.HIGH,
        ...     section="Act 2, Scene 3",
        ...     description="Character's motivation unclear",
        ...     suggestion="Add dialogue explaining decision",
        ...     impact="Reader confusion about protagonist's choices"
        ... ))
        >>> if review.passes:
        ...     print("Ready for Stage 17: Consistency Review")
        ... else:
        ...     print("Return to Stage 11: Script Refinement")
    """

    script_id: str
    script_version: str = "v3"
    overall_score: int = 0  # 0-100
    pass_threshold: int = 75  # Minimum score to pass
    max_high_severity_issues: int = 3  # Maximum high severity issues before failing
    passes: bool = True  # Whether review passes

    # Issue Tracking
    issues: List[ContentIssue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Content Analysis Scores
    logic_score: int = 0  # 0-100
    plot_score: int = 0  # 0-100
    character_score: int = 0  # 0-100
    pacing_score: int = 0  # 0-100

    # Review Metadata
    reviewer_id: str = "AI-ContentReviewer-001"
    reviewed_at: Optional[str] = None
    confidence_score: int = 85  # 0-100

    # Feedback
    summary: str = ""
    primary_concerns: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps and computed fields."""
        if self.reviewed_at is None:
            self.reviewed_at = datetime.now().isoformat()

        # Calculate pass/fail status
        self._recalculate_pass_status()

    def add_issue(self, issue: ContentIssue) -> None:
        """Add a content issue to the review.

        Args:
            issue: ContentIssue to add
        """
        self.issues.append(issue)

        # Update severity counts
        if issue.severity == ContentSeverity.CRITICAL:
            self.critical_count += 1
        elif issue.severity == ContentSeverity.HIGH:
            self.high_count += 1
        elif issue.severity == ContentSeverity.MEDIUM:
            self.medium_count += 1
        elif issue.severity == ContentSeverity.LOW:
            self.low_count += 1

        # Recalculate pass status
        self._recalculate_pass_status()

    def _recalculate_pass_status(self) -> None:
        """Recalculate pass/fail status based on issues and scores."""
        # Fail if any critical issues
        if self.critical_count > 0:
            self.passes = False
        # Fail if too many high severity issues
        elif self.high_count >= self.max_high_severity_issues:
            self.passes = False
        else:
            self.passes = self.overall_score >= self.pass_threshold

    def get_issues_by_severity(self, severity: ContentSeverity) -> List[ContentIssue]:
        """Get all issues of a specific severity.

        Args:
            severity: The severity level to filter by

        Returns:
            List of issues with the specified severity
        """
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_type(self, issue_type: ContentIssueType) -> List[ContentIssue]:
        """Get all issues of a specific type.

        Args:
            issue_type: The issue type to filter by

        Returns:
            List of issues with the specified type
        """
        return [issue for issue in self.issues if issue.issue_type == issue_type]

    def get_critical_issues(self) -> List[ContentIssue]:
        """Get all critical issues that must be fixed.

        Returns:
            List of critical severity issues
        """
        return self.get_issues_by_severity(ContentSeverity.CRITICAL)

    def get_high_priority_issues(self) -> List[ContentIssue]:
        """Get all high priority issues.

        Returns:
            List of critical and high severity issues
        """
        critical = self.get_issues_by_severity(ContentSeverity.CRITICAL)
        high = self.get_issues_by_severity(ContentSeverity.HIGH)
        return critical + high

    def get_logic_issues(self) -> List[ContentIssue]:
        """Get all logic-related issues.

        Returns:
            List of logic gap issues
        """
        return self.get_issues_by_type(ContentIssueType.LOGIC_GAP)

    def get_plot_issues(self) -> List[ContentIssue]:
        """Get all plot-related issues.

        Returns:
            List of plot issues
        """
        return self.get_issues_by_type(ContentIssueType.PLOT_ISSUE)

    def get_character_issues(self) -> List[ContentIssue]:
        """Get all character motivation issues.

        Returns:
            List of character motivation issues
        """
        return self.get_issues_by_type(ContentIssueType.CHARACTER_MOTIVATION)

    def get_pacing_issues(self) -> List[ContentIssue]:
        """Get all pacing issues.

        Returns:
            List of pacing issues
        """
        return self.get_issues_by_type(ContentIssueType.PACING)

    def to_dict(self) -> Dict[str, Any]:
        """Convert ContentReview to dictionary representation.

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
    def from_dict(cls, data: Dict[str, Any]) -> "ContentReview":
        """Create ContentReview from dictionary.

        Args:
            data: Dictionary containing ContentReview fields

        Returns:
            ContentReview instance
        """
        # Convert issues
        issues = []
        for issue_data in data.get("issues", []):
            issue_type = ContentIssueType(issue_data["issue_type"])
            severity = ContentSeverity(issue_data["severity"])
            issues.append(
                ContentIssue(
                    issue_type=issue_type,
                    severity=severity,
                    section=issue_data["section"],
                    description=issue_data["description"],
                    suggestion=issue_data["suggestion"],
                    impact=issue_data["impact"],
                    confidence=issue_data.get("confidence", 85),
                )
            )

        return cls(
            script_id=data["script_id"],
            script_version=data.get("script_version", "v3"),
            overall_score=data.get("overall_score", 0),
            pass_threshold=data.get("pass_threshold", 75),
            max_high_severity_issues=data.get("max_high_severity_issues", 3),
            passes=data.get("passes", True),
            issues=issues,
            critical_count=data.get("critical_count", 0),
            high_count=data.get("high_count", 0),
            medium_count=data.get("medium_count", 0),
            low_count=data.get("low_count", 0),
            logic_score=data.get("logic_score", 0),
            plot_score=data.get("plot_score", 0),
            character_score=data.get("character_score", 0),
            pacing_score=data.get("pacing_score", 0),
            reviewer_id=data.get("reviewer_id", "AI-ContentReviewer-001"),
            reviewed_at=data.get("reviewed_at"),
            confidence_score=data.get("confidence_score", 85),
            summary=data.get("summary", ""),
            primary_concerns=data.get("primary_concerns", []),
            strengths=data.get("strengths", []),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """String representation of ContentReview."""
        return (
            f"ContentReview(script={self.script_id}, "
            f"version={self.script_version}, "
            f"score={self.overall_score}%, "
            f"passes={'YES' if self.passes else 'NO'}, "
            f"issues={len(self.issues)})"
        )
