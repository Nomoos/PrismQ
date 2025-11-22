"""Tests for ContentReview model."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from T.Review.Content import (
    ContentReview,
    ContentIssue,
    ContentIssueType,
    ContentSeverity
)


class TestContentReviewBasic:
    """Test basic ContentReview functionality."""
    
    def test_create_basic_review(self):
        """Test creating a basic ContentReview instance."""
        review = ContentReview(
            script_id="script-001",
            script_version="v3",
            overall_score=85,
            logic_score=90,
            plot_score=85,
            character_score=80,
            pacing_score=85
        )
        
        assert review.script_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 85
        assert review.pass_threshold == 75
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0
        assert review.high_count == 0
        assert review.logic_score == 90
        assert review.plot_score == 85
        assert review.character_score == 80
        assert review.pacing_score == 85
        assert review.reviewer_id == "AI-ContentReviewer-001"
        assert review.reviewed_at is not None
        assert review.confidence_score == 85
    
    def test_create_failing_review(self):
        """Test creating a review that fails."""
        review = ContentReview(
            script_id="script-002",
            script_version="v3",
            overall_score=70  # Below threshold
        )
        
        assert review.passes is False
    
    def test_coherent_script_passes(self):
        """Test that a coherent script passes review."""
        review = ContentReview(
            script_id="script-coherent",
            script_version="v3",
            overall_score=88,
            logic_score=90,
            plot_score=88,
            character_score=85,
            pacing_score=90
        )
        
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0


class TestContentIssue:
    """Test ContentIssue functionality."""
    
    def test_create_content_issue(self):
        """Test creating a content issue."""
        issue = ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.HIGH,
            section="Act 2, Scene 3",
            description="Character motivation unclear",
            suggestion="Add dialogue explaining decision",
            impact="Reader confusion about protagonist's choices"
        )
        
        assert issue.issue_type == ContentIssueType.LOGIC_GAP
        assert issue.severity == ContentSeverity.HIGH
        assert issue.section == "Act 2, Scene 3"
        assert issue.description == "Character motivation unclear"
        assert issue.suggestion == "Add dialogue explaining decision"
        assert issue.confidence == 85
    
    def test_create_plot_issue(self):
        """Test creating a plot issue."""
        issue = ContentIssue(
            issue_type=ContentIssueType.PLOT_ISSUE,
            severity=ContentSeverity.CRITICAL,
            section="Act 3",
            description="Plot hole: Character knows information they couldn't have",
            suggestion="Add scene showing how character learned the information",
            impact="Breaks suspension of disbelief"
        )
        
        assert issue.issue_type == ContentIssueType.PLOT_ISSUE
        assert issue.severity == ContentSeverity.CRITICAL
    
    def test_create_pacing_issue(self):
        """Test creating a pacing issue."""
        issue = ContentIssue(
            issue_type=ContentIssueType.PACING,
            severity=ContentSeverity.MEDIUM,
            section="Act 1",
            description="Opening is too slow, takes too long to hook reader",
            suggestion="Start with action or intrigue, move exposition later",
            impact="May lose reader interest in first pages"
        )
        
        assert issue.issue_type == ContentIssueType.PACING
        assert issue.severity == ContentSeverity.MEDIUM


class TestContentReviewMethods:
    """Test ContentReview methods."""
    
    def test_add_issue(self):
        """Test adding issues to review."""
        review = ContentReview(
            script_id="script-001",
            overall_score=85
        )
        
        issue = ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.HIGH,
            section="Act 2",
            description="Logic gap",
            suggestion="Fix logic",
            impact="Confusion"
        )
        
        review.add_issue(issue)
        
        assert len(review.issues) == 1
        assert review.high_count == 1
        assert review.critical_count == 0
    
    def test_add_critical_issue_fails_review(self):
        """Test that adding critical issue fails review."""
        review = ContentReview(
            script_id="script-001",
            overall_score=85  # Good score
        )
        
        assert review.passes is True
        
        critical_issue = ContentIssue(
            issue_type=ContentIssueType.PLOT_ISSUE,
            severity=ContentSeverity.CRITICAL,
            section="Act 3",
            description="Major plot hole",
            suggestion="Rewrite scene",
            impact="Story breaks down"
        )
        
        review.add_issue(critical_issue)
        
        assert review.passes is False
        assert review.critical_count == 1
    
    def test_multiple_high_severity_fails(self):
        """Test that 3+ high severity issues fail review."""
        review = ContentReview(
            script_id="script-001",
            overall_score=85
        )
        
        assert review.passes is True
        
        # Add 3 high severity issues
        for i in range(3):
            review.add_issue(ContentIssue(
                issue_type=ContentIssueType.LOGIC_GAP,
                severity=ContentSeverity.HIGH,
                section=f"Act {i+1}",
                description=f"Issue {i+1}",
                suggestion="Fix it",
                impact="Impact"
            ))
        
        assert review.passes is False
        assert review.high_count == 3
    
    def test_configurable_max_high_severity(self):
        """Test configurable max high severity threshold."""
        # Default threshold is 3
        review = ContentReview(
            script_id="script-001",
            overall_score=85
        )
        
        # Add 2 high severity issues (below default threshold)
        for i in range(2):
            review.add_issue(ContentIssue(
                issue_type=ContentIssueType.LOGIC_GAP,
                severity=ContentSeverity.HIGH,
                section=f"Act {i+1}",
                description=f"Issue {i+1}",
                suggestion="Fix it",
                impact="Impact"
            ))
        
        assert review.passes is True  # Still passes with 2 high severity
        
        # Now test with custom threshold of 2
        review2 = ContentReview(
            script_id="script-002",
            overall_score=85,
            max_high_severity_issues=2
        )
        
        # Add 2 high severity issues (at threshold)
        for i in range(2):
            review2.add_issue(ContentIssue(
                issue_type=ContentIssueType.LOGIC_GAP,
                severity=ContentSeverity.HIGH,
                section=f"Act {i+1}",
                description=f"Issue {i+1}",
                suggestion="Fix it",
                impact="Impact"
            ))
        
        assert review2.passes is False  # Should fail with threshold of 2
    
    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        review = ContentReview(script_id="script-001")
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.HIGH,
            section="Act 1",
            description="Logic gap",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.PACING,
            severity=ContentSeverity.MEDIUM,
            section="Act 2",
            description="Pacing issue",
            suggestion="Speed up",
            impact="Impact"
        ))
        
        high_issues = review.get_issues_by_severity(ContentSeverity.HIGH)
        assert len(high_issues) == 1
        assert high_issues[0].issue_type == ContentIssueType.LOGIC_GAP
        
        medium_issues = review.get_issues_by_severity(ContentSeverity.MEDIUM)
        assert len(medium_issues) == 1
        assert medium_issues[0].issue_type == ContentIssueType.PACING
    
    def test_get_issues_by_type(self):
        """Test filtering issues by type."""
        review = ContentReview(script_id="script-001")
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.HIGH,
            section="Act 1",
            description="Logic gap 1",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.MEDIUM,
            section="Act 2",
            description="Logic gap 2",
            suggestion="Fix",
            impact="Impact"
        ))
        
        logic_issues = review.get_issues_by_type(ContentIssueType.LOGIC_GAP)
        assert len(logic_issues) == 2
    
    def test_get_critical_issues(self):
        """Test getting critical issues."""
        review = ContentReview(script_id="script-001")
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.PLOT_ISSUE,
            severity=ContentSeverity.CRITICAL,
            section="Act 3",
            description="Plot hole",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.HIGH,
            section="Act 2",
            description="Logic gap",
            suggestion="Fix",
            impact="Impact"
        ))
        
        critical = review.get_critical_issues()
        assert len(critical) == 1
        assert critical[0].severity == ContentSeverity.CRITICAL
    
    def test_get_high_priority_issues(self):
        """Test getting high priority issues."""
        review = ContentReview(script_id="script-001")
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.PLOT_ISSUE,
            severity=ContentSeverity.CRITICAL,
            section="Act 3",
            description="Critical",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.HIGH,
            section="Act 2",
            description="High",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.PACING,
            severity=ContentSeverity.MEDIUM,
            section="Act 1",
            description="Medium",
            suggestion="Fix",
            impact="Impact"
        ))
        
        high_priority = review.get_high_priority_issues()
        assert len(high_priority) == 2  # Critical + High
    
    def test_get_logic_issues(self):
        """Test getting logic issues."""
        review = ContentReview(script_id="script-001")
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.HIGH,
            section="Act 1",
            description="Logic",
            suggestion="Fix",
            impact="Impact"
        ))
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.PLOT_ISSUE,
            severity=ContentSeverity.HIGH,
            section="Act 2",
            description="Plot",
            suggestion="Fix",
            impact="Impact"
        ))
        
        logic_issues = review.get_logic_issues()
        assert len(logic_issues) == 1
        assert logic_issues[0].issue_type == ContentIssueType.LOGIC_GAP
    
    def test_get_plot_issues(self):
        """Test getting plot issues."""
        review = ContentReview(script_id="script-001")
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.PLOT_ISSUE,
            severity=ContentSeverity.CRITICAL,
            section="Act 2",
            description="Plot",
            suggestion="Fix",
            impact="Impact"
        ))
        
        plot_issues = review.get_plot_issues()
        assert len(plot_issues) == 1
        assert plot_issues[0].issue_type == ContentIssueType.PLOT_ISSUE
    
    def test_get_character_issues(self):
        """Test getting character issues."""
        review = ContentReview(script_id="script-001")
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.CHARACTER_MOTIVATION,
            severity=ContentSeverity.HIGH,
            section="Act 2",
            description="Character",
            suggestion="Fix",
            impact="Impact"
        ))
        
        character_issues = review.get_character_issues()
        assert len(character_issues) == 1
        assert character_issues[0].issue_type == ContentIssueType.CHARACTER_MOTIVATION
    
    def test_get_pacing_issues(self):
        """Test getting pacing issues."""
        review = ContentReview(script_id="script-001")
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.PACING,
            severity=ContentSeverity.MEDIUM,
            section="Act 1",
            description="Pacing",
            suggestion="Fix",
            impact="Impact"
        ))
        
        pacing_issues = review.get_pacing_issues()
        assert len(pacing_issues) == 1
        assert pacing_issues[0].issue_type == ContentIssueType.PACING


class TestIncoherentScript:
    """Test with incoherent scripts."""
    
    def test_incoherent_script_fails(self):
        """Test that an incoherent script fails review."""
        review = ContentReview(
            script_id="script-incoherent",
            script_version="v3",
            overall_score=60,  # Low score
            logic_score=50,
            plot_score=55,
            character_score=65,
            pacing_score=70
        )
        
        # Add multiple issues
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.PLOT_ISSUE,
            severity=ContentSeverity.CRITICAL,
            section="Act 2",
            description="Major plot hole",
            suggestion="Rewrite section",
            impact="Story doesn't make sense"
        ))
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.HIGH,
            section="Act 1",
            description="Logic gap",
            suggestion="Add explanation",
            impact="Confusion"
        ))
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.CHARACTER_MOTIVATION,
            severity=ContentSeverity.HIGH,
            section="Act 3",
            description="Character acts inconsistently",
            suggestion="Clarify motivation",
            impact="Character feels unrealistic"
        ))
        
        assert review.passes is False
        assert review.critical_count == 1
        assert review.high_count == 2
        assert len(review.issues) == 3


class TestContentReviewSerialization:
    """Test serialization functionality."""
    
    def test_to_dict(self):
        """Test converting review to dictionary."""
        review = ContentReview(
            script_id="script-001",
            script_version="v3",
            overall_score=85,
            logic_score=90,
            plot_score=85
        )
        
        review.add_issue(ContentIssue(
            issue_type=ContentIssueType.LOGIC_GAP,
            severity=ContentSeverity.HIGH,
            section="Act 2",
            description="Logic gap",
            suggestion="Fix",
            impact="Impact"
        ))
        
        data = review.to_dict()
        
        assert data["script_id"] == "script-001"
        assert data["script_version"] == "v3"
        assert data["overall_score"] == 85
        assert data["logic_score"] == 90
        assert data["plot_score"] == 85
        assert len(data["issues"]) == 1
        assert data["issues"][0]["issue_type"] == "logic_gap"
        assert data["issues"][0]["severity"] == "high"
    
    def test_from_dict(self):
        """Test creating review from dictionary."""
        data = {
            "script_id": "script-001",
            "script_version": "v3",
            "overall_score": 85,
            "logic_score": 90,
            "plot_score": 85,
            "character_score": 80,
            "pacing_score": 85,
            "issues": [
                {
                    "issue_type": "logic_gap",
                    "severity": "high",
                    "section": "Act 2",
                    "description": "Logic gap",
                    "suggestion": "Fix",
                    "impact": "Impact",
                    "confidence": 85
                }
            ],
            "high_count": 1
        }
        
        review = ContentReview.from_dict(data)
        
        assert review.script_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 85
        assert review.logic_score == 90
        assert len(review.issues) == 1
        assert review.issues[0].issue_type == ContentIssueType.LOGIC_GAP
        assert review.issues[0].severity == ContentSeverity.HIGH
    
    def test_round_trip_serialization(self):
        """Test that serialization preserves all data."""
        original = ContentReview(
            script_id="script-001",
            overall_score=80,
            logic_score=85,
            plot_score=80,
            character_score=75,
            pacing_score=80
        )
        
        original.add_issue(ContentIssue(
            issue_type=ContentIssueType.PACING,
            severity=ContentSeverity.MEDIUM,
            section="Act 1",
            description="Pacing issue",
            suggestion="Speed up",
            impact="Impact"
        ))
        
        # Convert to dict and back
        data = original.to_dict()
        restored = ContentReview.from_dict(data)
        
        assert restored.script_id == original.script_id
        assert restored.overall_score == original.overall_score
        assert restored.logic_score == original.logic_score
        assert restored.plot_score == original.plot_score
        assert len(restored.issues) == len(original.issues)
        assert restored.issues[0].description == original.issues[0].description


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
