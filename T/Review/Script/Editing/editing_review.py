"""Editing Review model for PrismQ AI-powered script editing validation.

This module defines the EditingReview data model for AI-powered editing and
clarity validation of script content. The review checks for clarity, flow,
redundancy, and structural coherence.

The EditingReview model enables:
- Sentence clarity and rewrite suggestions
- Structural paragraph improvements
- Redundancy detection and removal
- Transition quality checking
- Flow and readability optimization
- Feedback for script refinement

Workflow Position:
    Stage 18 (MVP-018): Editing Review
    Script v3+ → EditingReview (AI Reviewer) → Script Refinement (if fails) → Stage 19
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class EditingIssueType(Enum):
    """Types of editing issues that can be detected."""
    
    CLARITY = "clarity"  # Unclear or confusing sentences
    REDUNDANCY = "redundancy"  # Repeated or unnecessary content
    FLOW = "flow"  # Poor transitions or flow
    STRUCTURE = "structure"  # Structural paragraph issues
    WORDINESS = "wordiness"  # Overly wordy or verbose
    TRANSITION = "transition"  # Weak or missing transitions
    COHERENCE = "coherence"  # Logical inconsistency within text


class EditingSeverity(Enum):
    """Severity levels for editing issues."""
    
    CRITICAL = "critical"  # Must be fixed for clarity
    HIGH = "high"  # Should be fixed for flow
    MEDIUM = "medium"  # Recommended to fix
    LOW = "low"  # Minor improvement


@dataclass
class EditingIssue:
    """Individual editing issue found in the script."""
    
    issue_type: EditingIssueType
    severity: EditingSeverity
    line_number: int
    text: str  # The problematic text
    suggestion: str  # Suggested improvement
    explanation: str  # Why this needs editing
    confidence: int = 85  # 0-100, AI confidence in detection


@dataclass
class EditingReview:
    """AI-powered editing review with clarity and flow improvements.
    
    EditingReview provides comprehensive editing validation with:
    - Overall clarity and flow score (0-100%)
    - Categorized issue detection
    - Line-by-line improvement suggestions
    - Rewrite suggestions with explanations
    - Severity-based prioritization
    - Pass/fail determination for workflow progression
    
    The review serves as a quality gate - script must pass editing review
    before proceeding to Title Readability (Stage 19). If it fails, script
    returns to refinement (Stage 11) with editing feedback.
    
    Attributes:
        script_id: Identifier of the reviewed script
        script_version: Version of script being reviewed (v3, v4, etc.)
        overall_score: Overall editing quality score (0-100)
        pass_threshold: Minimum score required to pass (default 85)
        passes: Whether review passes (score >= threshold)
        
        Issue Tracking:
            issues: List of all detected editing issues
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
        >>> review = EditingReview(
        ...     script_id="script-001",
        ...     script_version="v3",
        ...     overall_score=92
        ... )
        >>> review.add_issue(EditingIssue(
        ...     issue_type=EditingIssueType.CLARITY,
        ...     severity=EditingSeverity.HIGH,
        ...     line_number=15,
        ...     text="The thing was done by him very quickly",
        ...     suggestion="He completed it quickly",
        ...     explanation="Passive voice reduces clarity"
        ... ))
        >>> if review.passes:
        ...     print("Ready for Stage 19: Title Readability")
        ... else:
        ...     print("Return to Stage 11: Script Refinement")
    """
    
    script_id: str
    script_version: str = "v3"
    overall_score: int = 0  # 0-100
    pass_threshold: int = 85  # Minimum score to pass
    passes: bool = True  # Whether review passes
    
    # Issue Tracking
    issues: List[EditingIssue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Review Metadata
    reviewer_id: str = "AI-EditingReviewer-001"
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
    
    def add_issue(self, issue: EditingIssue) -> None:
        """Add an editing issue to the review.
        
        Args:
            issue: EditingIssue to add
        """
        self.issues.append(issue)
        
        # Update severity counts
        if issue.severity == EditingSeverity.CRITICAL:
            self.critical_count += 1
        elif issue.severity == EditingSeverity.HIGH:
            self.high_count += 1
        elif issue.severity == EditingSeverity.MEDIUM:
            self.medium_count += 1
        elif issue.severity == EditingSeverity.LOW:
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
    
    def get_issues_by_severity(self, severity: EditingSeverity) -> List[EditingIssue]:
        """Get all issues of a specific severity.
        
        Args:
            severity: The severity level to filter by
            
        Returns:
            List of issues with the specified severity
        """
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_type(self, issue_type: EditingIssueType) -> List[EditingIssue]:
        """Get all issues of a specific type.
        
        Args:
            issue_type: The issue type to filter by
            
        Returns:
            List of issues with the specified type
        """
        return [issue for issue in self.issues if issue.issue_type == issue_type]
    
    def get_critical_issues(self) -> List[EditingIssue]:
        """Get all critical issues that must be fixed.
        
        Returns:
            List of critical severity issues
        """
        return self.get_issues_by_severity(EditingSeverity.CRITICAL)
    
    def get_high_priority_issues(self) -> List[EditingIssue]:
        """Get all high priority issues.
        
        Returns:
            List of critical and high severity issues
        """
        critical = self.get_issues_by_severity(EditingSeverity.CRITICAL)
        high = self.get_issues_by_severity(EditingSeverity.HIGH)
        return critical + high
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert EditingReview to dictionary representation.
        
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
    def from_dict(cls, data: Dict[str, Any]) -> "EditingReview":
        """Create EditingReview from dictionary.
        
        Args:
            data: Dictionary containing EditingReview fields
            
        Returns:
            EditingReview instance
        """
        # Extract and convert issues
        issues_data = data.pop("issues", [])
        issues = [
            EditingIssue(
                issue_type=EditingIssueType(issue["issue_type"]),
                severity=EditingSeverity(issue["severity"]),
                line_number=issue["line_number"],
                text=issue["text"],
                suggestion=issue["suggestion"],
                explanation=issue["explanation"],
                confidence=issue.get("confidence", 85)
            )
            for issue in issues_data
        ]
        
        # Create review without issues
        review = cls(**data)
        
        # Add issues
        review.issues = issues
        
        return review
