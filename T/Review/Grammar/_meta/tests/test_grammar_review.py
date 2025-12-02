"""Basic tests for GrammarReview model."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))

import pytest
from T.Review.Grammar import (
    GrammarReview,
    GrammarIssue,
    GrammarIssueType,
    GrammarSeverity
)


class TestGrammarReviewBasic:
    """Test basic GrammarReview functionality."""
    
    def test_create_basic_review(self):
        """Test creating a basic GrammarReview instance."""
        review = GrammarReview(
            script_id="script-001",
            script_version="v3",
            overall_score=92
        )
        
        assert review.script_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 92
        assert review.pass_threshold == 85
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0
        assert review.high_count == 0
        assert review.reviewer_id == "AI-GrammarReviewer-001"
        assert review.reviewed_at is not None
        assert review.confidence_score == 90
    
    def test_create_failing_review(self):
        """Test creating a review that fails."""
        review = GrammarReview(
            script_id="script-002",
            script_version="v3",
            overall_score=70  # Below threshold
        )
        
        assert review.passes is False


class TestGrammarIssue:
    """Test GrammarIssue functionality."""
    
    def test_create_grammar_issue(self):
        """Test creating a grammar issue."""
        issue = GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.HIGH,
            line_number=15,
            text="recieve",
            suggestion="receive",
            explanation="Common spelling error"
        )
        
        assert issue.issue_type == GrammarIssueType.SPELLING
        assert issue.severity == GrammarSeverity.HIGH
        assert issue.line_number == 15
        assert issue.text == "recieve"
        assert issue.suggestion == "receive"
        assert issue.confidence == 85


class TestGrammarReviewMethods:
    """Test GrammarReview methods."""
    
    def test_add_issue(self):
        """Test adding issues to review."""
        review = GrammarReview(
            script_id="script-001",
            overall_score=92
        )
        
        issue = GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.HIGH,
            line_number=15,
            text="recieve",
            suggestion="receive",
            explanation="Common spelling error"
        )
        
        review.add_issue(issue)
        
        assert len(review.issues) == 1
        assert review.high_count == 1
        assert review.critical_count == 0
    
    def test_add_critical_issue_fails_review(self):
        """Test that adding critical issue fails review."""
        review = GrammarReview(
            script_id="script-001",
            overall_score=92  # Good score
        )
        
        assert review.passes is True
        
        critical_issue = GrammarIssue(
            issue_type=GrammarIssueType.GRAMMAR,
            severity=GrammarSeverity.CRITICAL,
            line_number=10,
            text="They was running",
            suggestion="They were running",
            explanation="Subject-verb agreement error"
        )
        
        review.add_issue(critical_issue)
        
        assert review.passes is False
        assert review.critical_count == 1
    
    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        review = GrammarReview(script_id="script-001")
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.HIGH,
            line_number=15,
            text="recieve",
            suggestion="receive",
            explanation="Spelling error"
        ))
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.PUNCTUATION,
            severity=GrammarSeverity.MEDIUM,
            line_number=20,
            text="Hello",
            suggestion="Hello.",
            explanation="Missing period"
        ))
        
        high_issues = review.get_issues_by_severity(GrammarSeverity.HIGH)
        assert len(high_issues) == 1
        assert high_issues[0].issue_type == GrammarIssueType.SPELLING
        
        medium_issues = review.get_issues_by_severity(GrammarSeverity.MEDIUM)
        assert len(medium_issues) == 1
        assert medium_issues[0].issue_type == GrammarIssueType.PUNCTUATION
    
    def test_get_issues_by_type(self):
        """Test filtering issues by type."""
        review = GrammarReview(script_id="script-001")
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.HIGH,
            line_number=15,
            text="recieve",
            suggestion="receive",
            explanation="Spelling error"
        ))
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.MEDIUM,
            line_number=25,
            text="occured",
            suggestion="occurred",
            explanation="Spelling error"
        ))
        
        spelling_issues = review.get_issues_by_type(GrammarIssueType.SPELLING)
        assert len(spelling_issues) == 2
    
    def test_get_critical_issues(self):
        """Test getting critical issues."""
        review = GrammarReview(script_id="script-001")
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.GRAMMAR,
            severity=GrammarSeverity.CRITICAL,
            line_number=10,
            text="They was",
            suggestion="They were",
            explanation="Critical error"
        ))
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.HIGH,
            line_number=15,
            text="recieve",
            suggestion="receive",
            explanation="Spelling error"
        ))
        
        critical = review.get_critical_issues()
        assert len(critical) == 1
        assert critical[0].severity == GrammarSeverity.CRITICAL
    
    def test_get_high_priority_issues(self):
        """Test getting high priority issues."""
        review = GrammarReview(script_id="script-001")
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.GRAMMAR,
            severity=GrammarSeverity.CRITICAL,
            line_number=10,
            text="They was",
            suggestion="They were",
            explanation="Critical error"
        ))
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.HIGH,
            line_number=15,
            text="recieve",
            suggestion="receive",
            explanation="Spelling error"
        ))
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.PUNCTUATION,
            severity=GrammarSeverity.MEDIUM,
            line_number=20,
            text="Hello",
            suggestion="Hello.",
            explanation="Missing period"
        ))
        
        high_priority = review.get_high_priority_issues()
        assert len(high_priority) == 2  # Critical + High


class TestGrammarReviewSerialization:
    """Test serialization functionality."""
    
    def test_to_dict(self):
        """Test converting review to dictionary."""
        review = GrammarReview(
            script_id="script-001",
            script_version="v3",
            overall_score=92
        )
        
        review.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.HIGH,
            line_number=15,
            text="recieve",
            suggestion="receive",
            explanation="Spelling error"
        ))
        
        data = review.to_dict()
        
        assert data["script_id"] == "script-001"
        assert data["script_version"] == "v3"
        assert data["overall_score"] == 92
        assert len(data["issues"]) == 1
        assert data["issues"][0]["issue_type"] == "spelling"
        assert data["issues"][0]["severity"] == "high"
    
    def test_from_dict(self):
        """Test creating review from dictionary."""
        data = {
            "script_id": "script-001",
            "script_version": "v3",
            "overall_score": 92,
            "issues": [
                {
                    "issue_type": "spelling",
                    "severity": "high",
                    "line_number": 15,
                    "text": "recieve",
                    "suggestion": "receive",
                    "explanation": "Spelling error",
                    "confidence": 85
                }
            ],
            "high_count": 1
        }
        
        review = GrammarReview.from_dict(data)
        
        assert review.script_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 92
        assert len(review.issues) == 1
        assert review.issues[0].issue_type == GrammarIssueType.SPELLING
        assert review.issues[0].severity == GrammarSeverity.HIGH
    
    def test_round_trip_serialization(self):
        """Test that serialization preserves all data."""
        original = GrammarReview(
            script_id="script-001",
            overall_score=88
        )
        
        original.add_issue(GrammarIssue(
            issue_type=GrammarIssueType.PUNCTUATION,
            severity=GrammarSeverity.MEDIUM,
            line_number=10,
            text="Hello",
            suggestion="Hello.",
            explanation="Missing period"
        ))
        
        # Convert to dict and back
        data = original.to_dict()
        restored = GrammarReview.from_dict(data)
        
        assert restored.script_id == original.script_id
        assert restored.overall_score == original.overall_score
        assert len(restored.issues) == len(original.issues)
        assert restored.issues[0].text == original.issues[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
