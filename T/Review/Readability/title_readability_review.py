"""Title Readability Review model for PrismQ AI-powered voiceover validation.

This module defines the TitleReadabilityReview data model for AI-powered
readability validation of title content focused on voiceover suitability.
The review checks for clarity, length, engagement, and spoken-word flow.

The TitleReadabilityReview model enables:
- Voiceover flow assessment
- Natural rhythm and pacing evaluation
- Hard-to-read sentence detection
- Mouthfeel analysis (ease of speaking aloud)
- Clarity when listened to (not just read)
- Dramatic pause and delivery adjustments

Workflow Position:
    Stage 19 (MVP-019): Title Readability Review
    Title (vN) + Script (vN) → TitleReadabilityReview (AI Reviewer) → {
        PASS: Ready for finalization
        FAIL: Return to Title Refinement
    }
    
Dependencies:
    - MVP-018 (Editing Review) must pass before this stage
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ReadabilityIssueType(Enum):
    """Types of readability issues that can be detected for voiceover."""
    
    CLARITY = "clarity"  # Unclear when spoken aloud
    LENGTH = "length"  # Too long or too short for voiceover
    ENGAGEMENT = "engagement"  # Not engaging when heard
    VOICEOVER_FLOW = "voiceover_flow"  # Poor flow when spoken
    RHYTHM = "rhythm"  # Poor rhythm or pacing
    MOUTHFEEL = "mouthfeel"  # Difficult to say aloud
    PRONUNCIATION = "pronunciation"  # Hard to pronounce words
    LISTENING_CLARITY = "listening_clarity"  # Unclear when listened to


class ReadabilitySeverity(Enum):
    """Severity levels for readability issues."""
    
    CRITICAL = "critical"  # Must be fixed for voiceover
    HIGH = "high"  # Should be fixed for quality
    MEDIUM = "medium"  # Recommended to fix
    LOW = "low"  # Minor improvement


@dataclass
class ReadabilityIssue:
    """Individual readability issue found in the title."""
    
    issue_type: ReadabilityIssueType
    severity: ReadabilitySeverity
    text: str  # The problematic text
    suggestion: str  # Suggested improvement
    explanation: str  # Why this needs fixing for voiceover
    confidence: int = 85  # 0-100, AI confidence in detection


@dataclass
class TitleReadabilityReview:
    """AI-powered readability review for voiceover suitability.
    
    TitleReadabilityReview provides comprehensive voiceover validation with:
    - Overall readability score for spoken-word (0-100%)
    - Voiceover flow assessment
    - Natural rhythm and pacing evaluation
    - Mouthfeel and pronunciation checking
    - Listening clarity validation
    - Pass/fail determination for workflow progression
    
    This is the FINAL review stage for titles - if this passes, the title
    is ready for finalization. If it fails, the title returns to refinement
    with voiceover-specific feedback.
    
    Attributes:
        title_id: Identifier of the reviewed title
        title_text: The actual title text being reviewed
        title_version: Version of title being reviewed (v3, v4, etc.)
        overall_score: Overall readability score (0-100)
        pass_threshold: Minimum score required to pass (default 85)
        passes: Whether review passes (score >= threshold)
        
        Issue Tracking:
            issues: List of all detected readability issues
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
            voiceover_notes: Notes specific to voiceover delivery
            quick_fixes: Easy improvements
            notes: Additional reviewer notes
    
    Example:
        >>> review = TitleReadabilityReview(
        ...     title_id="title-001",
        ...     title_text="The Echo Mystery: Dark Secrets",
        ...     title_version="v3",
        ...     overall_score=92
        ... )
        >>> review.add_issue(ReadabilityIssue(
        ...     issue_type=ReadabilityIssueType.MOUTHFEEL,
        ...     severity=ReadabilitySeverity.HIGH,
        ...     text="Dark Secrets",
        ...     suggestion="Hidden Secrets",
        ...     explanation="'Dark Secrets' creates awkward mouth position"
        ... ))
        >>> if review.passes:
        ...     print("Ready for Finalization")
        ... else:
        ...     print("Return to Title Refinement")
    """
    
    title_id: str
    title_text: str
    title_version: str = "v3"
    overall_score: int = 0  # 0-100
    pass_threshold: int = 85  # Minimum score to pass
    passes: bool = True  # Whether review passes
    
    # Issue Tracking
    issues: List[ReadabilityIssue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Review Metadata
    reviewer_id: str = "AI-ReadabilityReviewer-001"
    reviewed_at: Optional[str] = None
    confidence_score: int = 90  # 0-100
    
    # Feedback
    summary: str = ""
    voiceover_notes: List[str] = field(default_factory=list)
    quick_fixes: List[str] = field(default_factory=list)
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
        """Recalculate pass/fail status based on issues."""
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
        """Convert TitleReadabilityReview to dictionary representation.
        
        Returns:
            Dictionary containing all fields with Enums converted to strings
        """
        data = asdict(self)
        
        # Convert issues
        data["issues"] = [
            {
                **asdict(issue),
                "issue_type": issue.issue_type.value,
                "severity": issue.severity.value
            }
            for issue in self.issues
        ]
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TitleReadabilityReview":
        """Create TitleReadabilityReview from dictionary.
        
        Args:
            data: Dictionary containing TitleReadabilityReview fields
            
        Returns:
            TitleReadabilityReview instance
        """
        # Extract issues data
        issues_data = data.pop("issues", [])
        
        # Reset counts to 0 since we'll recalculate them
        data["critical_count"] = 0
        data["high_count"] = 0
        data["medium_count"] = 0
        data["low_count"] = 0
        
        # Create review without issues
        review = cls(**data)
        
        # Add issues using add_issue to properly update counts
        for issue_data in issues_data:
            issue = ReadabilityIssue(
                issue_type=ReadabilityIssueType(issue_data["issue_type"]),
                severity=ReadabilitySeverity(issue_data["severity"]),
                text=issue_data["text"],
                suggestion=issue_data["suggestion"],
                explanation=issue_data["explanation"],
                confidence=issue_data.get("confidence", 85)
            )
            review.add_issue(issue)
        
        return review
