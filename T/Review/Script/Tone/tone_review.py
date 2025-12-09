"""Tone Review model for PrismQ AI-powered script tone validation.

This module defines the ToneReview data model for AI-powered tone and
style validation of script content. The review checks emotional intensity,
style alignment, voice consistency, and tone appropriateness.

The ToneReview model enables:
- Emotional intensity evaluation
- Style alignment checking (dark, suspense, dramatic, etc.)
- Voice and POV consistency validation
- Tone appropriateness for content type
- Audience-specific tone tuning
- Feedback for script refinement

Workflow Position:
    Stage 15 (MVP-015): Tone Review
    Script v3+ (Grammar Passed) → ToneReview (AI Reviewer) → Script Refinement (if fails) → Stage 16
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ToneIssueType(Enum):
    """Types of tone issues that can be detected."""

    EMOTIONAL_INTENSITY = "emotional_intensity"  # Intensity mismatch
    STYLE_ALIGNMENT = "style_alignment"  # Style inconsistency
    VOICE_CONSISTENCY = "voice_consistency"  # Voice/POV issues
    TONE_APPROPRIATENESS = "tone_appropriateness"  # Inappropriate tone
    AUDIENCE_MISMATCH = "audience_mismatch"  # Not suitable for target audience
    TONAL_SHIFT = "tonal_shift"  # Unexpected tone changes
    MOOD_INCONSISTENCY = "mood_inconsistency"  # Mood doesn't match intent


class ToneSeverity(Enum):
    """Severity levels for tone issues."""

    CRITICAL = "critical"  # Must be fixed
    HIGH = "high"  # Should be fixed
    MEDIUM = "medium"  # Recommended to fix
    LOW = "low"  # Minor issue


@dataclass
class ToneIssue:
    """Individual tone issue found in the script."""

    issue_type: ToneIssueType
    severity: ToneSeverity
    line_number: int
    text: str  # The problematic text
    suggestion: str  # Suggested improvement
    explanation: str  # Why this is an issue
    confidence: int = 85  # 0-100, AI confidence in detection


@dataclass
class ToneReview:
    """AI-powered tone review with style and voice consistency validation.

    ToneReview provides comprehensive tone and style validation with:
    - Overall tone appropriateness score (0-100%)
    - Categorized issue detection
    - Line-by-line tone identification
    - Suggested improvements with explanations
    - Severity-based prioritization
    - Pass/fail determination for workflow progression

    The review serves as a quality gate - script must pass both grammar review
    (Stage 14) and tone review before proceeding to next stage (Stage 16).
    If it fails, script returns to refinement (Stage 11) with tone feedback.

    Attributes:
        script_id: Identifier of the reviewed script
        script_version: Version of script being reviewed (v3, v4, etc.)
        overall_score: Overall tone appropriateness score (0-100)
        pass_threshold: Minimum score required to pass (default 80)
        passes: Whether review passes (score >= threshold)

        Tone Metrics:
            emotional_intensity_score: Emotional intensity appropriateness (0-100)
            style_alignment_score: Style consistency score (0-100)
            voice_consistency_score: Voice/POV consistency (0-100)
            audience_fit_score: Audience appropriateness (0-100)

        Issue Tracking:
            issues: List of all detected tone issues
            critical_count: Number of critical issues
            high_count: Number of high severity issues
            medium_count: Number of medium severity issues
            low_count: Number of low severity issues

        Review Metadata:
            reviewer_id: AI reviewer identifier
            reviewed_at: Timestamp of review
            confidence_score: AI confidence in review (0-100)
            target_tone: Expected tone style (e.g., "dark", "suspense")
            target_audience: Target audience description

        Feedback:
            summary: Overall assessment summary
            primary_concerns: Main issues to address
            strengths: What works well
            recommendations: Specific improvements
            notes: Additional reviewer notes

    Example:
        >>> review = ToneReview(
        ...     script_id="script-001",
        ...     script_version="v3",
        ...     overall_score=88,
        ...     target_tone="dark suspense",
        ...     target_audience="US female 14-29"
        ... )
        >>> review.add_issue(ToneIssue(
        ...     issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
        ...     severity=ToneSeverity.MEDIUM,
        ...     line_number=42,
        ...     text="This is really fun and exciting!",
        ...     suggestion="This unsettling discovery changed everything.",
        ...     explanation="Too upbeat for dark suspense tone"
        ... ))
        >>> if review.passes:
        ...     print("Ready for Stage 16")
        ... else:
        ...     print("Return to Stage 11: Script Refinement")
    """

    script_id: str
    script_version: str = "v3"
    overall_score: int = 0  # 0-100
    pass_threshold: int = (
        80  # Minimum score to pass (lower than Grammar's 85 due to subjective nature)
    )
    passes: bool = True  # Whether review passes

    # Tone Metrics
    emotional_intensity_score: int = 0  # 0-100
    style_alignment_score: int = 0  # 0-100
    voice_consistency_score: int = 0  # 0-100
    audience_fit_score: int = 0  # 0-100

    # Issue Tracking
    issues: List[ToneIssue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Review Metadata
    reviewer_id: str = "AI-ToneReviewer-001"
    reviewed_at: Optional[str] = None
    confidence_score: int = 85  # 0-100
    target_tone: str = ""  # Expected tone (e.g., "dark suspense")
    target_audience: str = ""  # Target audience description

    # Feedback
    summary: str = ""
    primary_concerns: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize timestamps and computed fields."""
        if self.reviewed_at is None:
            self.reviewed_at = datetime.now().isoformat()

        # Calculate pass/fail status
        self._recalculate_pass_status()

    def add_issue(self, issue: ToneIssue) -> None:
        """Add a tone issue to the review.

        Args:
            issue: ToneIssue to add
        """
        self.issues.append(issue)

        # Update severity counts
        if issue.severity == ToneSeverity.CRITICAL:
            self.critical_count += 1
        elif issue.severity == ToneSeverity.HIGH:
            self.high_count += 1
        elif issue.severity == ToneSeverity.MEDIUM:
            self.medium_count += 1
        elif issue.severity == ToneSeverity.LOW:
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

    def get_issues_by_severity(self, severity: ToneSeverity) -> List[ToneIssue]:
        """Get all issues of a specific severity.

        Args:
            severity: The severity level to filter by

        Returns:
            List of issues with the specified severity
        """
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_type(self, issue_type: ToneIssueType) -> List[ToneIssue]:
        """Get all issues of a specific type.

        Args:
            issue_type: The issue type to filter by

        Returns:
            List of issues with the specified type
        """
        return [issue for issue in self.issues if issue.issue_type == issue_type]

    def get_critical_issues(self) -> List[ToneIssue]:
        """Get all critical issues that must be fixed.

        Returns:
            List of critical severity issues
        """
        return self.get_issues_by_severity(ToneSeverity.CRITICAL)

    def get_high_priority_issues(self) -> List[ToneIssue]:
        """Get all high priority issues.

        Returns:
            List of critical and high severity issues
        """
        critical = self.get_issues_by_severity(ToneSeverity.CRITICAL)
        high = self.get_issues_by_severity(ToneSeverity.HIGH)
        return critical + high

    def to_dict(self) -> Dict[str, Any]:
        """Convert ToneReview to dictionary representation.

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
    def from_dict(cls, data: Dict[str, Any]) -> "ToneReview":
        """Create ToneReview from dictionary.

        Args:
            data: Dictionary containing ToneReview fields

        Returns:
            ToneReview instance

        Note:
            Explicit parameter passing ensures type safety and clear data mapping,
            following the same pattern as GrammarReview for consistency.
        """
        # Convert issues
        issues = []
        for issue_data in data.get("issues", []):
            issue_type = ToneIssueType(issue_data["issue_type"])
            severity = ToneSeverity(issue_data["severity"])
            issues.append(
                ToneIssue(
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
            pass_threshold=data.get("pass_threshold", 80),
            passes=data.get("passes", True),
            emotional_intensity_score=data.get("emotional_intensity_score", 0),
            style_alignment_score=data.get("style_alignment_score", 0),
            voice_consistency_score=data.get("voice_consistency_score", 0),
            audience_fit_score=data.get("audience_fit_score", 0),
            issues=issues,
            critical_count=data.get("critical_count", 0),
            high_count=data.get("high_count", 0),
            medium_count=data.get("medium_count", 0),
            low_count=data.get("low_count", 0),
            reviewer_id=data.get("reviewer_id", "AI-ToneReviewer-001"),
            reviewed_at=data.get("reviewed_at"),
            confidence_score=data.get("confidence_score", 85),
            target_tone=data.get("target_tone", ""),
            target_audience=data.get("target_audience", ""),
            summary=data.get("summary", ""),
            primary_concerns=data.get("primary_concerns", []),
            strengths=data.get("strengths", []),
            recommendations=data.get("recommendations", []),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """String representation of ToneReview."""
        return (
            f"ToneReview(script={self.script_id}, "
            f"version={self.script_version}, "
            f"score={self.overall_score}%, "
            f"passes={'YES' if self.passes else 'NO'}, "
            f"issues={len(self.issues)})"
        )
