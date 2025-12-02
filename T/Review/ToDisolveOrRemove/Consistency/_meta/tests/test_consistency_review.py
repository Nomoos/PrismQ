"""Tests for ConsistencyReview model."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from T.Review.Consistency import (
    ConsistencyReview,
    ConsistencyIssue,
    ConsistencyIssueType,
    ConsistencySeverity
)


class TestConsistencyReviewBasic:
    """Test basic ConsistencyReview functionality."""
    
    def test_create_basic_review(self):
        """Test creating a basic ConsistencyReview instance."""
        review = ConsistencyReview(
            script_id="script-001",
            script_version="v3",
            overall_score=88,
            character_score=90,
            timeline_score=85,
            location_score=90,
            logic_score=85
        )
        
        assert review.script_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 88
        assert review.pass_threshold == 80
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0
        assert review.high_count == 0
        assert review.character_score == 90
        assert review.timeline_score == 85
        assert review.location_score == 90
        assert review.logic_score == 85
        assert review.reviewer_id == "AI-ConsistencyReviewer-001"
        assert review.reviewed_at is not None
        assert review.confidence_score == 85
    
    def test_create_failing_review(self):
        """Test creating a review that fails."""
        review = ConsistencyReview(
            script_id="script-002",
            script_version="v3",
            overall_score=70  # Below threshold
        )
        
        assert review.passes is False
    
    def test_consistent_script_passes(self):
        """Test that a consistent script passes review."""
        review = ConsistencyReview(
            script_id="script-consistent",
            script_version="v3",
            overall_score=92,
            character_score=95,
            timeline_score=90,
            location_score=92,
            logic_score=90
        )
        
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0


class TestConsistencyIssue:
    """Test ConsistencyIssue functionality."""
    
    def test_create_character_issue(self):
        """Test creating a character name consistency issue."""
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 3",
            description="Character name changes from 'John' to 'Jon'",
            conflicting_sections=["Chapter 1", "Chapter 3"],
            suggestion="Use consistent spelling 'John' throughout",
            impact="Reader confusion about character identity"
        )
        
        assert issue.issue_type == ConsistencyIssueType.CHARACTER_NAME
        assert issue.severity == ConsistencySeverity.HIGH
        assert issue.section == "Chapter 3"
        assert issue.description == "Character name changes from 'John' to 'Jon'"
        assert len(issue.conflicting_sections) == 2
        assert issue.suggestion == "Use consistent spelling 'John' throughout"
        assert issue.confidence == 85
    
    def test_create_timeline_issue(self):
        """Test creating a timeline consistency issue."""
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.CRITICAL,
            section="Act 3",
            description="Character references event that hasn't happened yet",
            conflicting_sections=["Act 2", "Act 3"],
            suggestion="Reorder events or fix reference",
            impact="Timeline contradiction breaks story logic"
        )
        
        assert issue.issue_type == ConsistencyIssueType.TIMELINE
        assert issue.severity == ConsistencySeverity.CRITICAL
    
    def test_create_location_issue(self):
        """Test creating a location consistency issue."""
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.LOCATION,
            severity=ConsistencySeverity.MEDIUM,
            section="Scene 5",
            description="Character suddenly in different location without transition",
            conflicting_sections=["Scene 4", "Scene 5"],
            suggestion="Add transition scene or fix location reference",
            impact="Confusing scene continuity"
        )
        
        assert issue.issue_type == ConsistencyIssueType.LOCATION
        assert issue.severity == ConsistencySeverity.MEDIUM
    
    def test_create_contradiction_issue(self):
        """Test creating a contradiction issue."""
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.CONTRADICTION,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 5",
            description="Character age contradicts earlier statement",
            conflicting_sections=["Chapter 2", "Chapter 5"],
            suggestion="Verify and fix age consistency",
            impact="Character detail contradiction"
        )
        
        assert issue.issue_type == ConsistencyIssueType.CONTRADICTION
        assert issue.severity == ConsistencySeverity.HIGH


class TestConsistencyReviewMethods:
    """Test ConsistencyReview methods."""
    
    def test_add_issue(self):
        """Test adding issues to review."""
        review = ConsistencyReview(
            script_id="script-001",
            overall_score=88
        )
        
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 3",
            description="Character name inconsistency",
            suggestion="Fix name",
            impact="Confusion"
        )
        
        review.add_issue(issue)
        
        assert len(review.issues) == 1
        assert review.high_count == 1
        assert review.critical_count == 0
    
    def test_add_critical_issue_fails_review(self):
        """Test that adding critical issue fails review."""
        review = ConsistencyReview(
            script_id="script-001",
            overall_score=88  # Good score
        )
        
        assert review.passes is True
        
        critical_issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.CRITICAL,
            section="Act 3",
            description="Timeline contradiction",
            suggestion="Fix timeline",
            impact="Story breaks"
        )
        
        review.add_issue(critical_issue)
        
        assert review.passes is False
        assert review.critical_count == 1
    
    def test_multiple_high_severity_fails(self):
        """Test that 2+ high severity issues fail review."""
        review = ConsistencyReview(
            script_id="script-001",
            overall_score=88
        )
        
        assert review.passes is True
        
        # Add 2 high severity issues (default threshold is 2)
        for i in range(2):
            review.add_issue(ConsistencyIssue(
                issue_type=ConsistencyIssueType.CHARACTER_NAME,
                severity=ConsistencySeverity.HIGH,
                section=f"Chapter {i+1}",
                description=f"Issue {i+1}",
                suggestion="Fix it",
                impact="Impact"
            ))
        
        assert review.passes is False
        assert review.high_count == 2
    
    def test_configurable_max_high_severity(self):
        """Test configurable max high severity threshold."""
        # Default threshold is 2
        review = ConsistencyReview(
            script_id="script-001",
            overall_score=88
        )
        
        # Add 1 high severity issue (below default threshold)
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 1",
            description="Issue 1",
            suggestion="Fix it",
            impact="Impact"
        ))
        
        assert review.passes is True  # Still passes with 1 high severity
        
        # Now test with custom threshold of 1
        review2 = ConsistencyReview(
            script_id="script-002",
            overall_score=88,
            max_high_severity_issues=1
        )
        
        # Add 1 high severity issue (at threshold)
        review2.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 1",
            description="Issue 1",
            suggestion="Fix it",
            impact="Impact"
        ))
        
        assert review2.passes is False  # Should fail with threshold of 1
    
    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        review = ConsistencyReview(script_id="script-001")
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 1",
            description="Character name issue",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.MEDIUM,
            section="Chapter 2",
            description="Timeline issue",
            suggestion="Fix",
            impact="Impact"
        ))
        
        high_issues = review.get_issues_by_severity(ConsistencySeverity.HIGH)
        assert len(high_issues) == 1
        assert high_issues[0].issue_type == ConsistencyIssueType.CHARACTER_NAME
        
        medium_issues = review.get_issues_by_severity(ConsistencySeverity.MEDIUM)
        assert len(medium_issues) == 1
        assert medium_issues[0].issue_type == ConsistencyIssueType.TIMELINE
    
    def test_get_issues_by_type(self):
        """Test filtering issues by type."""
        review = ConsistencyReview(script_id="script-001")
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 1",
            description="Issue 1",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.MEDIUM,
            section="Chapter 2",
            description="Issue 2",
            suggestion="Fix",
            impact="Impact"
        ))
        
        character_issues = review.get_issues_by_type(ConsistencyIssueType.CHARACTER_NAME)
        assert len(character_issues) == 2
    
    def test_get_critical_issues(self):
        """Test getting critical issues."""
        review = ConsistencyReview(script_id="script-001")
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.CRITICAL,
            section="Act 3",
            description="Critical timeline issue",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 1",
            description="Character name issue",
            suggestion="Fix",
            impact="Impact"
        ))
        
        critical = review.get_critical_issues()
        assert len(critical) == 1
        assert critical[0].severity == ConsistencySeverity.CRITICAL
    
    def test_get_high_priority_issues(self):
        """Test getting high priority issues."""
        review = ConsistencyReview(script_id="script-001")
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.CRITICAL,
            section="Act 3",
            description="Critical",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 1",
            description="High",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.LOCATION,
            severity=ConsistencySeverity.MEDIUM,
            section="Scene 5",
            description="Medium",
            suggestion="Fix",
            impact="Impact"
        ))
        
        high_priority = review.get_high_priority_issues()
        assert len(high_priority) == 2  # Critical + High
    
    def test_get_character_issues(self):
        """Test getting character issues."""
        review = ConsistencyReview(script_id="script-001")
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 1",
            description="Character",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 2",
            description="Timeline",
            suggestion="Fix",
            impact="Impact"
        ))
        
        character_issues = review.get_character_issues()
        assert len(character_issues) == 1
        assert character_issues[0].issue_type == ConsistencyIssueType.CHARACTER_NAME
    
    def test_get_timeline_issues(self):
        """Test getting timeline issues."""
        review = ConsistencyReview(script_id="script-001")
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.CRITICAL,
            section="Act 2",
            description="Timeline",
            suggestion="Fix",
            impact="Impact"
        ))
        
        timeline_issues = review.get_timeline_issues()
        assert len(timeline_issues) == 1
        assert timeline_issues[0].issue_type == ConsistencyIssueType.TIMELINE
    
    def test_get_location_issues(self):
        """Test getting location issues."""
        review = ConsistencyReview(script_id="script-001")
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.LOCATION,
            severity=ConsistencySeverity.MEDIUM,
            section="Scene 5",
            description="Location",
            suggestion="Fix",
            impact="Impact"
        ))
        
        location_issues = review.get_location_issues()
        assert len(location_issues) == 1
        assert location_issues[0].issue_type == ConsistencyIssueType.LOCATION
    
    def test_get_contradiction_issues(self):
        """Test getting contradiction issues."""
        review = ConsistencyReview(script_id="script-001")
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CONTRADICTION,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 5",
            description="Contradiction",
            suggestion="Fix",
            impact="Impact"
        ))
        
        contradiction_issues = review.get_contradiction_issues()
        assert len(contradiction_issues) == 1
        assert contradiction_issues[0].issue_type == ConsistencyIssueType.CONTRADICTION


class TestInconsistentScript:
    """Test with inconsistent scripts."""
    
    def test_inconsistent_script_fails(self):
        """Test that an inconsistent script fails review."""
        review = ConsistencyReview(
            script_id="script-inconsistent",
            script_version="v3",
            overall_score=65,  # Low score
            character_score=60,
            timeline_score=55,
            location_score=70,
            logic_score=75
        )
        
        # Add multiple issues
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.CRITICAL,
            section="Act 3",
            description="Timeline contradiction",
            conflicting_sections=["Act 2", "Act 3"],
            suggestion="Fix timeline",
            impact="Story logic breaks"
        ))
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 5",
            description="Character name inconsistency",
            conflicting_sections=["Chapter 1", "Chapter 5"],
            suggestion="Use consistent name",
            impact="Character identity confusion"
        ))
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.LOCATION,
            severity=ConsistencySeverity.MEDIUM,
            section="Scene 8",
            description="Location continuity issue",
            conflicting_sections=["Scene 7", "Scene 8"],
            suggestion="Add transition or fix location",
            impact="Scene continuity confusion"
        ))
        
        assert review.passes is False
        assert review.critical_count == 1
        assert review.high_count == 1
        assert len(review.issues) == 3


class TestConsistencyReviewSerialization:
    """Test serialization functionality."""
    
    def test_to_dict(self):
        """Test converting review to dictionary."""
        review = ConsistencyReview(
            script_id="script-001",
            script_version="v3",
            overall_score=88,
            character_score=90,
            timeline_score=85
        )
        
        review.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            section="Chapter 3",
            description="Character name issue",
            suggestion="Fix",
            impact="Impact"
        ))
        
        data = review.to_dict()
        
        assert data["script_id"] == "script-001"
        assert data["script_version"] == "v3"
        assert data["overall_score"] == 88
        assert data["character_score"] == 90
        assert data["timeline_score"] == 85
        assert len(data["issues"]) == 1
        assert data["issues"][0]["issue_type"] == "character_name"
        assert data["issues"][0]["severity"] == "high"
    
    def test_from_dict(self):
        """Test creating review from dictionary."""
        data = {
            "script_id": "script-001",
            "script_version": "v3",
            "overall_score": 88,
            "character_score": 90,
            "timeline_score": 85,
            "location_score": 90,
            "logic_score": 85,
            "issues": [
                {
                    "issue_type": "character_name",
                    "severity": "high",
                    "section": "Chapter 3",
                    "description": "Character name issue",
                    "conflicting_sections": ["Chapter 1", "Chapter 3"],
                    "suggestion": "Fix",
                    "impact": "Impact",
                    "confidence": 85
                }
            ],
            "high_count": 1
        }
        
        review = ConsistencyReview.from_dict(data)
        
        assert review.script_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 88
        assert review.character_score == 90
        assert len(review.issues) == 1
        assert review.issues[0].issue_type == ConsistencyIssueType.CHARACTER_NAME
        assert review.issues[0].severity == ConsistencySeverity.HIGH
    
    def test_round_trip_serialization(self):
        """Test that serialization preserves all data."""
        original = ConsistencyReview(
            script_id="script-001",
            overall_score=85,
            character_score=90,
            timeline_score=85,
            location_score=88,
            logic_score=80
        )
        
        original.add_issue(ConsistencyIssue(
            issue_type=ConsistencyIssueType.LOCATION,
            severity=ConsistencySeverity.MEDIUM,
            section="Scene 5",
            description="Location continuity issue",
            conflicting_sections=["Scene 4", "Scene 5"],
            suggestion="Add transition",
            impact="Confusion"
        ))
        
        # Convert to dict and back
        data = original.to_dict()
        restored = ConsistencyReview.from_dict(data)
        
        assert restored.script_id == original.script_id
        assert restored.overall_score == original.overall_score
        assert restored.character_score == original.character_score
        assert restored.timeline_score == original.timeline_score
        assert len(restored.issues) == len(original.issues)
        assert restored.issues[0].description == original.issues[0].description


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
