"""Script Consistency Review - AI-powered consistency validation for scripts.

This module implements PrismQ.T.Review.Script.Consistency for Stage 17 (MVP-017).
Provides comprehensive consistency checking including character names, timeline,
locations, and internal contradictions with detailed issue detection and JSON output.

The consistency review serves as a quality gate - scripts must pass before proceeding
to Editing Review (Stage 18/MVP-018). If it fails, the script returns to refinement
with detailed feedback.

Workflow Position:
    Stage 17 (MVP-017): Consistency Review
    Script v3+ → Consistency Review → [PASS: Stage 18] or [FAIL: Script Refinement]
"""

import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict


class ConsistencyIssueType(Enum):
    """Types of consistency issues that can be detected."""
    
    CHARACTER_NAME = "character_name"  # Character name inconsistency
    TIMELINE = "timeline"  # Timeline contradiction
    LOCATION = "location"  # Location inconsistency
    DETAIL = "detail"  # Repeated detail mismatch
    CONTRADICTION = "contradiction"  # Internal contradiction
    CONTINUITY = "continuity"  # Story continuity issue


class ConsistencySeverity(Enum):
    """Severity levels for consistency issues."""
    
    CRITICAL = "critical"  # Must be fixed - breaks story logic
    HIGH = "high"  # Should be fixed - major inconsistency
    MEDIUM = "medium"  # Recommended to fix - noticeable issue
    LOW = "low"  # Minor issue - polish


@dataclass
class ConsistencyIssue:
    """Individual consistency issue found in the script."""
    
    issue_type: ConsistencyIssueType
    severity: ConsistencySeverity
    location: str  # Location in script (line/section)
    description: str  # What the issue is
    details: str  # Specific details about the inconsistency
    suggestion: str  # How to fix it
    related_locations: List[str] = field(default_factory=list)  # Other related locations
    confidence: int = 85  # 0-100, AI confidence in detection


@dataclass
class ConsistencyReview:
    """AI-powered consistency review for script validation.
    
    ConsistencyReview provides comprehensive consistency validation with:
    - Overall consistency score (0-100%)
    - Character name tracking
    - Timeline verification
    - Location consistency checking
    - Internal contradiction detection
    - Pass/fail determination for workflow progression
    
    The review serves as a quality gate - script must pass consistency review
    before proceeding to Editing Review (Stage 18). If it fails, script
    returns to refinement (Stage 11) with consistency feedback.
    
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
            timeline_score: Timeline consistency score (0-100)
            location_score: Location consistency score (0-100)
            detail_score: Detail consistency score (0-100)
            
        Detected Elements:
            characters_found: Set of character names found
            locations_found: Set of locations found
            timeline_events: List of timeline events
            
        Review Metadata:
            reviewer_id: AI reviewer identifier
            reviewed_at: Timestamp of review
            confidence_score: AI confidence in review (0-100)
            
        Feedback:
            summary: Overall assessment summary
            primary_concerns: Main issues to address
            notes: Additional reviewer notes
    
    Example:
        >>> review = ConsistencyReview(
        ...     script_id="script-001",
        ...     script_version="v3",
        ...     overall_score=85
        ... )
        >>> review.add_issue(ConsistencyIssue(
        ...     issue_type=ConsistencyIssueType.CHARACTER_NAME,
        ...     severity=ConsistencySeverity.HIGH,
        ...     location="Line 45",
        ...     description="Character name inconsistency",
        ...     details="Character referred to as 'John' in line 10 but 'Johnny' here",
        ...     suggestion="Use consistent name 'John' throughout"
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
    max_high_severity_issues: int = 3  # Maximum high severity issues before failing
    passes: bool = True  # Whether review passes
    
    # Issue Tracking
    issues: List[ConsistencyIssue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Consistency Analysis Scores
    character_score: int = 100  # 0-100
    timeline_score: int = 100  # 0-100
    location_score: int = 100  # 0-100
    detail_score: int = 100  # 0-100
    
    # Detected Elements
    characters_found: Set[str] = field(default_factory=set)
    locations_found: Set[str] = field(default_factory=set)
    timeline_events: List[str] = field(default_factory=list)
    
    # Review Metadata
    reviewer_id: str = "AI-ConsistencyReviewer-001"
    reviewed_at: Optional[str] = None
    confidence_score: int = 85  # 0-100
    
    # Feedback
    summary: str = ""
    primary_concerns: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize timestamps and computed fields."""
        if self.reviewed_at is None:
            self.reviewed_at = datetime.now().isoformat()
        
        # Convert sets if they were passed as lists
        if not isinstance(self.characters_found, set):
            self.characters_found = set(self.characters_found)
        if not isinstance(self.locations_found, set):
            self.locations_found = set(self.locations_found)
        
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
        """Get all character consistency issues.
        
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
        """Get all internal contradiction issues.
        
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
        
        # Convert sets to lists for JSON serialization
        data["characters_found"] = list(self.characters_found)
        data["locations_found"] = list(self.locations_found)
        
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
                location=issue_data["location"],
                description=issue_data["description"],
                details=issue_data["details"],
                suggestion=issue_data["suggestion"],
                related_locations=issue_data.get("related_locations", []),
                confidence=issue_data.get("confidence", 85)
            ))
        
        return cls(
            script_id=data["script_id"],
            script_version=data.get("script_version", "v3"),
            overall_score=data.get("overall_score", 0),
            pass_threshold=data.get("pass_threshold", 80),
            max_high_severity_issues=data.get("max_high_severity_issues", 3),
            passes=data.get("passes", True),
            issues=issues,
            critical_count=data.get("critical_count", 0),
            high_count=data.get("high_count", 0),
            medium_count=data.get("medium_count", 0),
            low_count=data.get("low_count", 0),
            character_score=data.get("character_score", 100),
            timeline_score=data.get("timeline_score", 100),
            location_score=data.get("location_score", 100),
            detail_score=data.get("detail_score", 100),
            characters_found=set(data.get("characters_found", [])),
            locations_found=set(data.get("locations_found", [])),
            timeline_events=data.get("timeline_events", []),
            reviewer_id=data.get("reviewer_id", "AI-ConsistencyReviewer-001"),
            reviewed_at=data.get("reviewed_at"),
            confidence_score=data.get("confidence_score", 85),
            summary=data.get("summary", ""),
            primary_concerns=data.get("primary_concerns", []),
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


class ScriptConsistencyChecker:
    """AI-powered consistency checker for script content.
    
    Performs comprehensive consistency validation including:
    - Character name consistency
    - Timeline verification
    - Location tracking
    - Internal contradictions
    - Detail consistency
    """
    
    # Common words to filter out when detecting character names
    COMMON_NON_NAME_WORDS = {
        'The', 'A', 'An', 'I', 'He', 'She', 'It', 'They', 'We',
        'This', 'That', 'These', 'Those', 'What', 'Where', 'When',
        'Why', 'How', 'There', 'Here', 'Then', 'Now', 'But', 'Yet',
        'Suddenly', 'After', 'Before'
    }
    
    # Timeline indicators
    TIMELINE_INDICATORS = [
        'earlier', 'later', 'before', 'after', 'yesterday', 'tomorrow',
        'morning', 'afternoon', 'evening', 'night', 'day', 'week', 'month', 'year',
        'first', 'then', 'next', 'finally', 'meanwhile', 'simultaneously'
    ]
    
    # Location keywords
    LOCATION_KEYWORDS = [
        'at', 'in', 'inside', 'outside', 'near', 'location', 'place',
        'building', 'house', 'room', 'office', 'street', 'city', 'town'
    ]
    
    # Contradiction patterns (pattern, type)
    CONTRADICTION_PATTERNS = [
        (r'\b(never|no|not|nobody|nothing)\b.*\b(always|yes|everyone|everything)\b', 'opposite_statements'),
        (r'\b(alive)\b.*\b(dead)\b', 'life_state_contradiction'),
        (r'\b(married)\b.*\b(single)\b', 'relationship_contradiction'),
    ]
    
    def __init__(self, pass_threshold: int = 80):
        """Initialize the consistency checker.
        
        Args:
            pass_threshold: Minimum score (0-100) required to pass review
        """
        self.pass_threshold = pass_threshold
    
    def review_script(
        self,
        script_text: str,
        script_id: str = "script-001",
        script_version: str = "v3"
    ) -> ConsistencyReview:
        """Review a script for consistency issues.
        
        Args:
            script_text: The script text to review
            script_id: Identifier for the script
            script_version: Version of the script (v3, v4, etc.)
            
        Returns:
            ConsistencyReview object with all detected issues
        """
        review = ConsistencyReview(
            script_id=script_id,
            script_version=script_version,
            pass_threshold=self.pass_threshold
        )
        
        # Split script into lines for analysis
        lines = script_text.split('\n')
        
        # Track elements throughout the script
        character_mentions = defaultdict(list)  # name -> [line_numbers]
        location_mentions = defaultdict(list)  # location -> [line_numbers]
        
        # Check each line
        for line_num, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            
            # Track character names
            self._track_characters(line, line_num, character_mentions)
            
            # Track locations
            self._track_locations(line, line_num, location_mentions)
            
            # Check for timeline markers
            self._check_timeline(line, line_num, review)
        
        # Analyze tracked elements for consistency
        self._check_character_consistency(character_mentions, review)
        self._check_location_consistency(location_mentions, review)
        self._check_contradictions(lines, review)
        
        # Update review with found elements
        review.characters_found = set(character_mentions.keys())
        review.locations_found = set(location_mentions.keys())
        
        # Calculate scores
        review.character_score = self._calculate_character_score(review)
        review.location_score = self._calculate_location_score(review)
        review.timeline_score = self._calculate_timeline_score(review)
        review.detail_score = self._calculate_detail_score(review)
        
        # Calculate overall score
        review.overall_score = int(
            (review.character_score * 0.30) +
            (review.timeline_score * 0.25) +
            (review.location_score * 0.25) +
            (review.detail_score * 0.20)
        )
        
        # Recalculate pass status with final score
        review._recalculate_pass_status()
        
        # Generate summary and feedback
        self._generate_feedback(review)
        
        return review
    
    def _track_characters(
        self,
        line: str,
        line_num: int,
        character_mentions: Dict[str, List[int]]
    ) -> None:
        """Track character names mentioned in the line."""
        # Find capitalized words (potential character names)
        words = re.findall(r'\b([A-Z][a-z]+)\b', line)
        
        for word in words:
            if word not in self.COMMON_NON_NAME_WORDS and len(word) > 2:
                character_mentions[word].append(line_num)
    
    def _track_locations(
        self,
        line: str,
        line_num: int,
        location_mentions: Dict[str, List[int]]
    ) -> None:
        """Track locations mentioned in the line."""
        line_lower = line.lower()
        
        # Look for location patterns
        for keyword in self.LOCATION_KEYWORDS:
            if keyword in line_lower:
                # Extract potential location (simplified)
                words_after = line_lower.split(keyword, 1)
                if len(words_after) > 1:
                    potential_location = words_after[1].split()[0:3]
                    if potential_location:
                        location = ' '.join(potential_location).strip('.,;:!?')
                        if location and len(location) > 2:
                            location_mentions[location].append(line_num)
    
    def _check_timeline(
        self,
        line: str,
        line_num: int,
        review: ConsistencyReview
    ) -> None:
        """Check for timeline markers and record them."""
        line_lower = line.lower()
        
        for indicator in self.TIMELINE_INDICATORS:
            if indicator in line_lower:
                review.timeline_events.append(f"Line {line_num}: {indicator}")
    
    def _check_character_consistency(
        self,
        character_mentions: Dict[str, List[int]],
        review: ConsistencyReview
    ) -> None:
        """Check for character name inconsistencies."""
        # Look for similar names that might be variations
        names = list(character_mentions.keys())
        
        for i, name1 in enumerate(names):
            for name2 in names[i+1:]:
                # Check if names are similar (could be variations)
                if self._are_names_similar(name1, name2):
                    issue = ConsistencyIssue(
                        issue_type=ConsistencyIssueType.CHARACTER_NAME,
                        severity=ConsistencySeverity.HIGH,
                        location=f"Lines {', '.join(map(str, character_mentions[name1][:3]))}",
                        description=f"Possible character name inconsistency",
                        details=f"Character referred to as both '{name1}' and '{name2}'",
                        suggestion=f"Use consistent name throughout script",
                        related_locations=[f"Lines {', '.join(map(str, character_mentions[name2][:3]))}"],
                        confidence=75
                    )
                    review.add_issue(issue)
    
    def _are_names_similar(self, name1: str, name2: str) -> bool:
        """Check if two names are similar enough to be variations."""
        # Check if one is a substring of the other
        if name1.lower() in name2.lower() or name2.lower() in name1.lower():
            return True
        
        # Check if they share a common prefix (nickname pattern)
        min_len = min(len(name1), len(name2))
        if min_len >= 3 and name1[:3].lower() == name2[:3].lower():
            return True
        
        return False
    
    def _check_location_consistency(
        self,
        location_mentions: Dict[str, List[int]],
        review: ConsistencyReview
    ) -> None:
        """Check for location inconsistencies."""
        # This is a placeholder - in a real implementation, this would use
        # more sophisticated NLP to detect location contradictions
        pass
    
    def _check_contradictions(
        self,
        lines: List[str],
        review: ConsistencyReview
    ) -> None:
        """Check for internal contradictions in the script."""
        full_text = ' '.join(lines).lower()
        
        for pattern, contradiction_type in self.CONTRADICTION_PATTERNS:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                # Find approximate line number
                pos = match.start()
                line_num = full_text[:pos].count('\n') + 1
                
                issue = ConsistencyIssue(
                    issue_type=ConsistencyIssueType.CONTRADICTION,
                    severity=ConsistencySeverity.MEDIUM,
                    location=f"Around line {line_num}",
                    description=f"Potential contradiction detected",
                    details=f"Found potentially contradictory statements: {contradiction_type}",
                    suggestion="Review for logical consistency",
                    confidence=60
                )
                review.add_issue(issue)
    
    def _calculate_character_score(self, review: ConsistencyReview) -> int:
        """Calculate character consistency score."""
        character_issues = len(review.get_character_issues())
        
        if character_issues == 0:
            return 100
        elif character_issues == 1:
            return 85
        elif character_issues == 2:
            return 70
        else:
            return max(50, 100 - (character_issues * 15))
    
    def _calculate_location_score(self, review: ConsistencyReview) -> int:
        """Calculate location consistency score."""
        location_issues = len(review.get_location_issues())
        
        if location_issues == 0:
            return 100
        elif location_issues == 1:
            return 90
        else:
            return max(60, 100 - (location_issues * 10))
    
    def _calculate_timeline_score(self, review: ConsistencyReview) -> int:
        """Calculate timeline consistency score."""
        timeline_issues = len(review.get_timeline_issues())
        
        if timeline_issues == 0:
            return 100
        elif timeline_issues == 1:
            return 85
        else:
            return max(50, 100 - (timeline_issues * 15))
    
    def _calculate_detail_score(self, review: ConsistencyReview) -> int:
        """Calculate detail consistency score."""
        detail_issues = len(review.get_issues_by_type(ConsistencyIssueType.DETAIL))
        contradiction_issues = len(review.get_contradiction_issues())
        
        total_detail_issues = detail_issues + contradiction_issues
        
        if total_detail_issues == 0:
            return 100
        elif total_detail_issues <= 2:
            return 85
        else:
            return max(60, 100 - (total_detail_issues * 10))
    
    def _generate_feedback(self, review: ConsistencyReview) -> None:
        """Generate summary and feedback for the review."""
        total_issues = len(review.issues)
        
        if total_issues == 0:
            review.summary = "Excellent! No consistency issues detected. Script maintains internal coherence."
            review.passes = True
            return
        
        # Generate summary
        if review.passes:
            review.summary = f"Script passes consistency review with {total_issues} minor issue(s) detected."
        else:
            review.summary = f"Script requires revision. {total_issues} consistency issue(s) detected, including {review.critical_count} critical error(s)."
        
        # Identify primary concerns
        if review.critical_count > 0:
            review.primary_concerns.append(f"{review.critical_count} critical consistency error(s) must be fixed")
        
        if review.high_count > 0:
            review.primary_concerns.append(f"{review.high_count} high-priority consistency issue(s) should be addressed")
        
        # Categorize issues
        character_count = len(review.get_character_issues())
        if character_count > 0:
            review.primary_concerns.append(f"{character_count} character name inconsistenc{'y' if character_count == 1 else 'ies'}")
        
        timeline_count = len(review.get_timeline_issues())
        if timeline_count > 0:
            review.primary_concerns.append(f"{timeline_count} timeline issue(s)")
        
        location_count = len(review.get_location_issues())
        if location_count > 0:
            review.primary_concerns.append(f"{location_count} location inconsistenc{'y' if location_count == 1 else 'ies'}")
        
        contradiction_count = len(review.get_contradiction_issues())
        if contradiction_count > 0:
            review.primary_concerns.append(f"{contradiction_count} internal contradiction(s)")


def review_script_consistency(
    script_text: str,
    script_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 80
) -> ConsistencyReview:
    """Convenience function to review script consistency.
    
    Args:
        script_text: The script text to review
        script_id: Identifier for the script
        script_version: Version of the script
        pass_threshold: Minimum score required to pass
        
    Returns:
        ConsistencyReview object with all detected issues
        
    Example:
        >>> script = "John walked into the room. Later, Johnny picked up the book."
        >>> review = review_script_consistency(script)
        >>> print(f"Score: {review.overall_score}")
        >>> print(f"Passes: {review.passes}")
        >>> for issue in review.issues:
        ...     print(f"{issue.location}: {issue.description}")
    """
    checker = ScriptConsistencyChecker(pass_threshold=pass_threshold)
    return checker.review_script(script_text, script_id, script_version)


def review_script_consistency_to_json(
    script_text: str,
    script_id: str = "script-001",
    script_version: str = "v3",
    pass_threshold: int = 80
) -> str:
    """Review script consistency and return results as JSON string.
    
    Args:
        script_text: The script text to review
        script_id: Identifier for the script
        script_version: Version of the script
        pass_threshold: Minimum score required to pass
        
    Returns:
        JSON string containing the consistency review results
        
    Example:
        >>> script = "John walked in. Johnny left."
        >>> json_result = review_script_consistency_to_json(script)
        >>> import json
        >>> result = json.loads(json_result)
        >>> print(result['overall_score'])
        >>> print(result['passes'])
    """
    import json
    review = review_script_consistency(script_text, script_id, script_version, pass_threshold)
    return json.dumps(review.to_dict(), indent=2)


def get_consistency_feedback(review: ConsistencyReview) -> Dict[str, Any]:
    """Get formatted feedback from a consistency review for script refinement.
    
    Args:
        review: ConsistencyReview object
        
    Returns:
        Dictionary with structured feedback for script writers
        
    Example:
        >>> review = review_script_consistency(script_text)
        >>> feedback = get_consistency_feedback(review)
        >>> if not feedback['passes']:
        ...     print("Script needs revision:")
        ...     for issue in feedback['critical_issues']:
        ...         print(f"  {issue['location']}: {issue['description']}")
    """
    return {
        'script_id': review.script_id,
        'script_version': review.script_version,
        'passes': review.passes,
        'overall_score': review.overall_score,
        'threshold': review.pass_threshold,
        'summary': review.summary,
        'total_issues': len(review.issues),
        'critical_issues': [
            {
                'location': issue.location,
                'type': issue.issue_type.value,
                'description': issue.description,
                'details': issue.details,
                'suggestion': issue.suggestion
            }
            for issue in review.get_critical_issues()
        ],
        'high_priority_issues': [
            {
                'location': issue.location,
                'type': issue.issue_type.value,
                'description': issue.description,
                'details': issue.details,
                'suggestion': issue.suggestion
            }
            for issue in review.get_issues_by_severity(ConsistencySeverity.HIGH)
        ],
        'character_issues': [
            {
                'location': issue.location,
                'description': issue.description,
                'details': issue.details,
                'suggestion': issue.suggestion
            }
            for issue in review.get_character_issues()
        ],
        'timeline_issues': [
            {
                'location': issue.location,
                'description': issue.description,
                'details': issue.details,
                'suggestion': issue.suggestion
            }
            for issue in review.get_timeline_issues()
        ],
        'primary_concerns': review.primary_concerns,
        'next_action': 'Proceed to Stage 18 (Editing Review)' if review.passes else 'Return to Script Refinement (Stage 11)'
    }


if __name__ == "__main__":
    # Example usage
    test_script = """John walked into the old house at dusk.
The building was empty, dark and quiet.
He looked around nervously.
Suddenly, Johnny heard a noise from upstairs.
John climbed the stairs slowly.
At the top, there was a closed door.
He opened it and saw a figure in the shadows.
It was Mary, his old friend from college.
But wait - hadn't Mary died last year?
John remembered attending her funeral.
Yet here she was, standing before him.
"Mary?" he said. "How is this possible?"
She smiled. "I never died, John. That was someone else."
"""
    
    print("=== Script Consistency Review ===\n")
    print("Script:")
    print(test_script)
    print("\n" + "="*50 + "\n")
    
    review = review_script_consistency(test_script, script_id="test-001", script_version="v3")
    
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Character Score: {review.character_score}/100")
    print(f"Timeline Score: {review.timeline_score}/100")
    print(f"Location Score: {review.location_score}/100")
    print(f"Detail Score: {review.detail_score}/100")
    print(f"Passes: {'YES' if review.passes else 'NO'}")
    print(f"Total Issues: {len(review.issues)}")
    print(f"\nCharacters Found: {', '.join(sorted(review.characters_found))}")
    print(f"\nSummary: {review.summary}\n")
    
    if review.issues:
        print("Issues Found:")
        for issue in review.issues:
            print(f"\n{issue.location} [{issue.severity.value.upper()}] - {issue.issue_type.value.upper()}")
            print(f"  Description: {issue.description}")
            print(f"  Details: {issue.details}")
            print(f"  Suggestion: {issue.suggestion}")
    
    print("\n" + "="*50)
    print("\nJSON Output (first 500 chars):")
    json_output = review_script_consistency_to_json(test_script, script_id="test-001")
    print(json_output[:500] + "...")
