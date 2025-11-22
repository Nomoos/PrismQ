"""Consistency Review model for PrismQ AI-powered script consistency validation.

This module defines the ConsistencyReview data model for AI-powered internal
consistency validation of script content. The review checks for character names,
timeline continuity, location consistency, and contradictions throughout the script.

The ConsistencyReview model enables:
- Character name consistency validation
- Timeline alignment checking
- Location/scene continuity verification
- Contradiction detection
- Repeated detail matching
- Feedback for script refinement

Workflow Position:
    Stage 17 (MVP-017): Consistency Review
    Script v3+ → ConsistencyReview (AI Reviewer) → Script Refinement (if fails) → Stage 18
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ConsistencyIssueType(Enum):
    """Types of consistency issues that can be detected."""
    
    CHARACTER_NAME = "character_name"  # Character name inconsistency
    TIMELINE = "timeline"  # Timeline contradiction or sequence error
    LOCATION = "location"  # Location/scene continuity issue
    CONTRADICTION = "contradiction"  # General contradictions in facts or details
    REPEATED_DETAIL = "repeated_detail"  # Details that don't match on repetition
    LORE = "lore"  # Lore or fact alignment issues


class ConsistencySeverity(Enum):
    """Severity levels for consistency issues."""
    
    CRITICAL = "critical"  # Must be fixed - breaks story logic
    HIGH = "high"  # Should be fixed - significant inconsistency
    MEDIUM = "medium"  # Recommended to fix - noticeable issue
    LOW = "low"  # Minor issue - polish


@dataclass
class ConsistencyIssue:
    """Individual consistency issue found in the script."""
    
    issue_type: ConsistencyIssueType
    severity: ConsistencySeverity
    section: str  # Section/scene identifier where issue occurs
    description: str  # What the consistency issue is
    conflicting_sections: List[str] = field(default_factory=list)  # Other sections involved
    suggestion: str = ""  # How to fix it
    impact: str = ""  # Impact on story/narrative
    confidence: int = 85  # 0-100, AI confidence in detection


@dataclass
class ConsistencyReview:
    """AI-powered consistency review with internal continuity validation.
    
    ConsistencyReview provides comprehensive internal consistency validation with:
    - Overall consistency score (0-100%)
    - Categorized issue detection
    - Character name consistency checking
    - Timeline alignment verification
    - Location continuity validation
    - Contradiction detection
    - Suggested fixes with impact analysis
    - Severity-based prioritization
    - Pass/fail determination for workflow progression
    
    The review serves as a quality gate - script must pass consistency review
    before proceeding to Editing Review (Stage 18). If it fails, script returns
    to refinement (Stage 11) with consistency feedback.
    
    Attributes:
        script_id: Identifier of the reviewed script
        script_version: Version of script being reviewed (v3, v4, etc.)
        overall_score: Overall consistency score (0-100)
        pass_threshold: Minimum score required to pass (default 80)
        passes: Whether review passes (score >= threshold)
        
        Issue Tracking:
            issues: List of all detected consistency issues
            critical_count: Number of critical issues
            high_count: Number of high severity issues
            medium_count: Number of medium severity issues
            low_count: Number of low severity issues
            
        Consistency Analysis:
            character_score: Character name consistency score (0-100)
            timeline_score: Timeline continuity score (0-100)
            location_score: Location consistency score (0-100)
            logic_score: Overall logic consistency score (0-100)
            
        Review Metadata:
            reviewer_id: AI reviewer identifier
            reviewed_at: Timestamp of review
            confidence_score: AI confidence in review (0-100)
            
        Feedback:
            summary: Overall assessment summary
            primary_concerns: Main issues to address
            consistent_elements: Story elements that are consistent
            notes: Additional reviewer notes
    
    Example:
        >>> review = ConsistencyReview(
        ...     script_id="script-001",
        ...     script_version="v3",
        ...     overall_score=88,
        ...     character_score=90,
        ...     timeline_score=85,
        ...     location_score=90,
        ...     logic_score=85
        ... )
        >>> review.add_issue(ConsistencyIssue(
        ...     issue_type=ConsistencyIssueType.CHARACTER_NAME,
        ...     severity=ConsistencySeverity.HIGH,
        ...     section="Chapter 3",
        ...     description="Character name changes from 'John' to 'Jon'",
        ...     conflicting_sections=["Chapter 1", "Chapter 3"],
        ...     suggestion="Use consistent spelling 'John' throughout",
        ...     impact="Reader confusion about character identity"
        ... ))
        >>> if review.passes:
        ...     print("Ready for Stage 18: Editing Review")
        ... else:
        ...     print("Return to Stage 11: Script Refinement")
    """
    
    script_id: str
    script_version: str = "v3"
    overall_score: int = 0  # 0-100
    pass_threshold: int = 80  # Minimum score to pass
    max_high_severity_issues: int = 2  # Maximum high severity issues before failing
    passes: bool = True  # Whether review passes
    
    # Issue Tracking
    issues: List[ConsistencyIssue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Consistency Analysis Scores
    character_score: int = 0  # 0-100
    timeline_score: int = 0  # 0-100
    location_score: int = 0  # 0-100
    logic_score: int = 0  # 0-100
    
    # Review Metadata
    reviewer_id: str = "AI-ConsistencyReviewer-001"
    reviewed_at: Optional[str] = None
    confidence_score: int = 85  # 0-100
    
    # Feedback
    summary: str = ""
    primary_concerns: List[str] = field(default_factory=list)
    consistent_elements: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamps and computed fields."""
        if self.reviewed_at is None:
            self.reviewed_at = datetime.now().isoformat()
        
        # Calculate pass/fail status
        self._recalculate_pass_status()
    
    def add_issue(self, issue: ConsistencyIssue) -> None:
        """Add a consistency issue to the review.
        
        Args:
            issue: ConsistencyIssue to add
        """
        self.issues.append(issue)
        
        # Update severity counts
        if issue.severity == ConsistencySeverity.CRITICAL:
            self.critical_count += 1
        elif issue.severity == ConsistencySeverity.HIGH:
            self.high_count += 1
        elif issue.severity == ConsistencySeverity.MEDIUM:
            self.medium_count += 1
        elif issue.severity == ConsistencySeverity.LOW:
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
    
    def get_issues_by_severity(self, severity: ConsistencySeverity) -> List[ConsistencyIssue]:
        """Get all issues of a specific severity.
        
        Args:
            severity: The severity level to filter by
            
        Returns:
            List of issues with the specified severity
        """
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_type(self, issue_type: ConsistencyIssueType) -> List[ConsistencyIssue]:
        """Get all issues of a specific type.
        
        Args:
            issue_type: The issue type to filter by
            
        Returns:
            List of issues with the specified type
        """
        return [issue for issue in self.issues if issue.issue_type == issue_type]
    
    def get_critical_issues(self) -> List[ConsistencyIssue]:
        """Get all critical issues that must be fixed.
        
        Returns:
            List of critical severity issues
        """
        return self.get_issues_by_severity(ConsistencySeverity.CRITICAL)
    
    def get_high_priority_issues(self) -> List[ConsistencyIssue]:
        """Get all high priority issues.
        
        Returns:
            List of critical and high severity issues
        """
        critical = self.get_issues_by_severity(ConsistencySeverity.CRITICAL)
        high = self.get_issues_by_severity(ConsistencySeverity.HIGH)
        return critical + high
    
    def get_character_issues(self) -> List[ConsistencyIssue]:
        """Get all character name consistency issues.
        
        Returns:
            List of character name issues
        """
        return self.get_issues_by_type(ConsistencyIssueType.CHARACTER_NAME)
    
    def get_timeline_issues(self) -> List[ConsistencyIssue]:
        """Get all timeline consistency issues.
        
        Returns:
            List of timeline issues
        """
        return self.get_issues_by_type(ConsistencyIssueType.TIMELINE)
    
    def get_location_issues(self) -> List[ConsistencyIssue]:
        """Get all location consistency issues.
        
        Returns:
            List of location issues
        """
        return self.get_issues_by_type(ConsistencyIssueType.LOCATION)
    
    def get_contradiction_issues(self) -> List[ConsistencyIssue]:
        """Get all contradiction issues.
        
        Returns:
            List of contradiction issues
        """
        return self.get_issues_by_type(ConsistencyIssueType.CONTRADICTION)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ConsistencyReview to dictionary representation.
        
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
    def from_dict(cls, data: Dict[str, Any]) -> "ConsistencyReview":
        """Create ConsistencyReview from dictionary.
        
        Args:
            data: Dictionary containing ConsistencyReview fields
            
        Returns:
            ConsistencyReview instance
        """
        # Convert issues
        issues = []
        for issue_data in data.get("issues", []):
            issue_type = ConsistencyIssueType(issue_data["issue_type"])
            severity = ConsistencySeverity(issue_data["severity"])
            issues.append(ConsistencyIssue(
                issue_type=issue_type,
                severity=severity,
                section=issue_data["section"],
                description=issue_data["description"],
                conflicting_sections=issue_data.get("conflicting_sections", []),
                suggestion=issue_data.get("suggestion", ""),
                impact=issue_data.get("impact", ""),
                confidence=issue_data.get("confidence", 85)
            ))
        
        return cls(
            script_id=data["script_id"],
            script_version=data.get("script_version", "v3"),
            overall_score=data.get("overall_score", 0),
            pass_threshold=data.get("pass_threshold", 80),
            max_high_severity_issues=data.get("max_high_severity_issues", 2),
            passes=data.get("passes", True),
            issues=issues,
            critical_count=data.get("critical_count", 0),
            high_count=data.get("high_count", 0),
            medium_count=data.get("medium_count", 0),
            low_count=data.get("low_count", 0),
            character_score=data.get("character_score", 0),
            timeline_score=data.get("timeline_score", 0),
            location_score=data.get("location_score", 0),
            logic_score=data.get("logic_score", 0),
            reviewer_id=data.get("reviewer_id", "AI-ConsistencyReviewer-001"),
            reviewed_at=data.get("reviewed_at"),
            confidence_score=data.get("confidence_score", 85),
            summary=data.get("summary", ""),
            primary_concerns=data.get("primary_concerns", []),
            consistent_elements=data.get("consistent_elements", []),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {})
        )
    
    def __repr__(self) -> str:
        """String representation of ConsistencyReview."""
        return (
            f"ConsistencyReview(script={self.script_id}, "
            f"version={self.script_version}, "
            f"score={self.overall_score}%, "
            f"passes={'YES' if self.passes else 'NO'}, "
            f"issues={len(self.issues)})"
        )
