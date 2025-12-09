"""Tests for ConsistencyReview model and ScriptConsistencyChecker."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import json

import pytest

from T.Review.Content.Consistency import (
    ConsistencyIssue,
    ConsistencyIssueType,
    ConsistencyReview,
    ConsistencySeverity,
    ScriptConsistencyChecker,
    get_consistency_feedback,
    review_content_consistency,
    review_content_consistency_to_json,
)


class TestConsistencyReviewBasic:
    """Test basic ConsistencyReview functionality."""

    def test_create_basic_review(self):
        """Test creating a basic ConsistencyReview instance."""
        review = ConsistencyReview(
            content_id="script-001",
            script_version="v3",
            overall_score=85,
            character_score=90,
            timeline_score=85,
            location_score=80,
            detail_score=85,
        )

        assert review.content_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 85
        assert review.pass_threshold == 80
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0
        assert review.high_count == 0
        assert review.character_score == 90
        assert review.timeline_score == 85
        assert review.location_score == 80
        assert review.detail_score == 85
        assert review.reviewer_id == "AI-ConsistencyReviewer-001"
        assert review.reviewed_at is not None
        assert review.confidence_score == 85

    def test_create_failing_review(self):
        """Test creating a review that fails."""
        review = ConsistencyReview(
            content_id="script-002", script_version="v3", overall_score=75  # Below threshold of 80
        )

        assert review.passes is False

    def test_consistent_content_passes(self):
        """Test that a consistent script passes review."""
        review = ConsistencyReview(
            content_id="script-consistent",
            script_version="v3",
            overall_score=90,
            character_score=95,
            timeline_score=90,
            location_score=88,
            detail_score=90,
        )

        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0


class TestConsistencyIssue:
    """Test ConsistencyIssue functionality."""

    def test_create_character_issue(self):
        """Test creating a character consistency issue."""
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            location="Line 45",
            description="Character name inconsistency",
            details="Character referred to as 'John' in line 10 but 'Johnny' here",
            suggestion="Use consistent name 'John' throughout",
        )

        assert issue.issue_type == ConsistencyIssueType.CHARACTER_NAME
        assert issue.severity == ConsistencySeverity.HIGH
        assert issue.location == "Line 45"
        assert issue.description == "Character name inconsistency"
        assert issue.confidence == 85

    def test_create_timeline_issue(self):
        """Test creating a timeline issue."""
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.CRITICAL,
            location="Act 3",
            description="Timeline contradiction",
            details="Event happens before its prerequisite",
            suggestion="Reorder events to maintain logical sequence",
        )

        assert issue.issue_type == ConsistencyIssueType.TIMELINE
        assert issue.severity == ConsistencySeverity.CRITICAL

    def test_create_location_issue(self):
        """Test creating a location issue."""
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.LOCATION,
            severity=ConsistencySeverity.MEDIUM,
            location="Scene 5",
            description="Location inconsistency",
            details="Character is in two places at once",
            suggestion="Clarify character's location",
        )

        assert issue.issue_type == ConsistencyIssueType.LOCATION
        assert issue.severity == ConsistencySeverity.MEDIUM

    def test_create_contradiction_issue(self):
        """Test creating an internal contradiction issue."""
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.CONTRADICTION,
            severity=ConsistencySeverity.HIGH,
            location="Lines 20-50",
            description="Internal contradiction",
            details="Character stated to be alive but later described as dead",
            suggestion="Resolve the contradiction about character's state",
        )

        assert issue.issue_type == ConsistencyIssueType.CONTRADICTION
        assert issue.severity == ConsistencySeverity.HIGH


class TestConsistencyReviewMethods:
    """Test ConsistencyReview methods."""

    def test_add_issue(self):
        """Test adding issues to review."""
        review = ConsistencyReview(content_id="script-001", overall_score=85)

        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.HIGH,
            location="Line 45",
            description="Character inconsistency",
            details="Name varies",
            suggestion="Use consistent name",
        )

        review.add_issue(issue)

        assert len(review.issues) == 1
        assert review.high_count == 1
        assert review.critical_count == 0

    def test_add_critical_issue_fails_review(self):
        """Test that adding critical issue fails review."""
        review = ConsistencyReview(content_id="script-001", overall_score=85)  # Good score

        assert review.passes is True

        critical_issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.TIMELINE,
            severity=ConsistencySeverity.CRITICAL,
            location="Act 3",
            description="Major timeline error",
            details="Events occur out of logical order",
            suggestion="Reorder timeline",
        )

        review.add_issue(critical_issue)

        assert review.passes is False
        assert review.critical_count == 1

    def test_multiple_high_severity_fails(self):
        """Test that 3+ high severity issues fail review."""
        review = ConsistencyReview(content_id="script-001", overall_score=85)

        assert review.passes is True

        # Add 3 high severity issues
        for i in range(3):
            review.add_issue(
                ConsistencyIssue(
                    issue_type=ConsistencyIssueType.CHARACTER_NAME,
                    severity=ConsistencySeverity.HIGH,
                    location=f"Line {i*10}",
                    description=f"Issue {i+1}",
                    details="Details",
                    suggestion="Fix it",
                )
            )

        assert review.passes is False
        assert review.high_count == 3

    def test_configurable_max_high_severity(self):
        """Test configurable max high severity threshold."""
        # Default threshold is 3
        review = ConsistencyReview(content_id="script-001", overall_score=85)

        # Add 2 high severity issues (below default threshold)
        for i in range(2):
            review.add_issue(
                ConsistencyIssue(
                    issue_type=ConsistencyIssueType.CHARACTER_NAME,
                    severity=ConsistencySeverity.HIGH,
                    location=f"Line {i*10}",
                    description=f"Issue {i+1}",
                    details="Details",
                    suggestion="Fix it",
                )
            )

        assert review.passes is True  # Still passes with 2 high severity

        # Now test with custom threshold of 2
        review2 = ConsistencyReview(
            content_id="script-002", overall_score=85, max_high_severity_issues=2
        )

        # Add 2 high severity issues (at threshold)
        for i in range(2):
            review2.add_issue(
                ConsistencyIssue(
                    issue_type=ConsistencyIssueType.CHARACTER_NAME,
                    severity=ConsistencySeverity.HIGH,
                    location=f"Line {i*10}",
                    description=f"Issue {i+1}",
                    details="Details",
                    suggestion="Fix it",
                )
            )

        assert review2.passes is False  # Should fail with threshold of 2

    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        review = ConsistencyReview(content_id="script-001")

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.CHARACTER_NAME,
                severity=ConsistencySeverity.HIGH,
                location="Line 10",
                description="Character issue",
                details="Details",
                suggestion="Fix",
            )
        )

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.TIMELINE,
                severity=ConsistencySeverity.MEDIUM,
                location="Line 20",
                description="Timeline issue",
                details="Details",
                suggestion="Fix",
            )
        )

        high_issues = review.get_issues_by_severity(ConsistencySeverity.HIGH)
        assert len(high_issues) == 1
        assert high_issues[0].issue_type == ConsistencyIssueType.CHARACTER_NAME

        medium_issues = review.get_issues_by_severity(ConsistencySeverity.MEDIUM)
        assert len(medium_issues) == 1
        assert medium_issues[0].issue_type == ConsistencyIssueType.TIMELINE

    def test_get_issues_by_type(self):
        """Test filtering issues by type."""
        review = ConsistencyReview(content_id="script-001")

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.CHARACTER_NAME,
                severity=ConsistencySeverity.HIGH,
                location="Line 10",
                description="Character 1",
                details="Details",
                suggestion="Fix",
            )
        )

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.CHARACTER_NAME,
                severity=ConsistencySeverity.MEDIUM,
                location="Line 20",
                description="Character 2",
                details="Details",
                suggestion="Fix",
            )
        )

        character_issues = review.get_issues_by_type(ConsistencyIssueType.CHARACTER_NAME)
        assert len(character_issues) == 2

    def test_get_critical_issues(self):
        """Test getting critical issues."""
        review = ConsistencyReview(content_id="script-001")

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.TIMELINE,
                severity=ConsistencySeverity.CRITICAL,
                location="Act 3",
                description="Critical timeline",
                details="Details",
                suggestion="Fix",
            )
        )

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.CHARACTER_NAME,
                severity=ConsistencySeverity.HIGH,
                location="Line 10",
                description="High character",
                details="Details",
                suggestion="Fix",
            )
        )

        critical = review.get_critical_issues()
        assert len(critical) == 1
        assert critical[0].severity == ConsistencySeverity.CRITICAL

    def test_get_high_priority_issues(self):
        """Test getting high priority issues."""
        review = ConsistencyReview(content_id="script-001")

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.TIMELINE,
                severity=ConsistencySeverity.CRITICAL,
                location="Act 3",
                description="Critical",
                details="Details",
                suggestion="Fix",
            )
        )

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.CHARACTER_NAME,
                severity=ConsistencySeverity.HIGH,
                location="Line 10",
                description="High",
                details="Details",
                suggestion="Fix",
            )
        )

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.LOCATION,
                severity=ConsistencySeverity.MEDIUM,
                location="Scene 5",
                description="Medium",
                details="Details",
                suggestion="Fix",
            )
        )

        high_priority = review.get_high_priority_issues()
        assert len(high_priority) == 2  # Critical + High

    def test_get_character_issues(self):
        """Test getting character issues."""
        review = ConsistencyReview(content_id="script-001")

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.CHARACTER_NAME,
                severity=ConsistencySeverity.HIGH,
                location="Line 10",
                description="Character",
                details="Details",
                suggestion="Fix",
            )
        )

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.TIMELINE,
                severity=ConsistencySeverity.HIGH,
                location="Line 20",
                description="Timeline",
                details="Details",
                suggestion="Fix",
            )
        )

        character_issues = review.get_character_issues()
        assert len(character_issues) == 1
        assert character_issues[0].issue_type == ConsistencyIssueType.CHARACTER_NAME

    def test_get_timeline_issues(self):
        """Test getting timeline issues."""
        review = ConsistencyReview(content_id="script-001")

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.TIMELINE,
                severity=ConsistencySeverity.CRITICAL,
                location="Act 2",
                description="Timeline",
                details="Details",
                suggestion="Fix",
            )
        )

        timeline_issues = review.get_timeline_issues()
        assert len(timeline_issues) == 1
        assert timeline_issues[0].issue_type == ConsistencyIssueType.TIMELINE

    def test_get_location_issues(self):
        """Test getting location issues."""
        review = ConsistencyReview(content_id="script-001")

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.LOCATION,
                severity=ConsistencySeverity.HIGH,
                location="Scene 3",
                description="Location",
                details="Details",
                suggestion="Fix",
            )
        )

        location_issues = review.get_location_issues()
        assert len(location_issues) == 1
        assert location_issues[0].issue_type == ConsistencyIssueType.LOCATION

    def test_get_contradiction_issues(self):
        """Test getting contradiction issues."""
        review = ConsistencyReview(content_id="script-001")

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.CONTRADICTION,
                severity=ConsistencySeverity.HIGH,
                location="Lines 20-30",
                description="Contradiction",
                details="Details",
                suggestion="Fix",
            )
        )

        contradiction_issues = review.get_contradiction_issues()
        assert len(contradiction_issues) == 1
        assert contradiction_issues[0].issue_type == ConsistencyIssueType.CONTRADICTION


class TestScriptConsistencyChecker:
    """Test ScriptConsistencyChecker functionality."""

    def test_check_consistent_content(self):
        """Test checking a consistent script."""
        script = """Sarah walked into the library.
The library was quiet and peaceful.
Sarah found a book and sat down to read.
After an hour, Sarah left the library."""

        checker = ScriptConsistencyChecker(pass_threshold=80)
        review = checker.review_content(script, "test-001", "v3")

        assert review.content_id == "test-001"
        assert review.script_version == "v3"
        assert review.passes is True
        assert review.overall_score >= 80

    def test_detect_character_name_inconsistency(self):
        """Test detecting character name inconsistencies."""
        script = """John walked into the room.
He looked around nervously.
Johnny picked up the book.
John left the building."""

        checker = ScriptConsistencyChecker(pass_threshold=80)
        review = checker.review_content(script, "test-002", "v3")

        character_issues = review.get_character_issues()
        assert len(character_issues) > 0
        assert any(
            "John" in issue.details and "Johnny" in issue.details for issue in character_issues
        )

    def test_track_characters(self):
        """Test character tracking."""
        script = """Alice met Bob at the park.
They talked for hours.
Alice enjoyed the conversation."""

        checker = ScriptConsistencyChecker(pass_threshold=80)
        review = checker.review_content(script, "test-003", "v3")

        assert "Alice" in review.characters_found
        assert "Bob" in review.characters_found

    def test_empty_content(self):
        """Test with empty script."""
        script = ""

        checker = ScriptConsistencyChecker(pass_threshold=80)
        review = checker.review_content(script, "test-004", "v3")

        assert review.overall_score >= 0
        assert len(review.issues) == 0


class TestConsistencyReviewSerialization:
    """Test serialization functionality."""

    def test_to_dict(self):
        """Test converting review to dictionary."""
        review = ConsistencyReview(
            content_id="script-001",
            script_version="v3",
            overall_score=85,
            character_score=90,
            timeline_score=85,
        )

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.CHARACTER_NAME,
                severity=ConsistencySeverity.HIGH,
                location="Line 10",
                description="Character inconsistency",
                details="Name varies",
                suggestion="Fix",
            )
        )

        data = review.to_dict()

        assert data["content_id"] == "script-001"
        assert data["script_version"] == "v3"
        assert data["overall_score"] == 85
        assert data["character_score"] == 90
        assert data["timeline_score"] == 85
        assert len(data["issues"]) == 1
        assert data["issues"][0]["issue_type"] == "character_name"
        assert data["issues"][0]["severity"] == "high"

    def test_from_dict(self):
        """Test creating review from dictionary."""
        data = {
            "content_id": "script-001",
            "script_version": "v3",
            "overall_score": 85,
            "character_score": 90,
            "timeline_score": 85,
            "location_score": 80,
            "detail_score": 85,
            "issues": [
                {
                    "issue_type": "character_name",
                    "severity": "high",
                    "location": "Line 10",
                    "description": "Character inconsistency",
                    "details": "Name varies",
                    "suggestion": "Fix",
                    "related_locations": [],
                    "confidence": 85,
                }
            ],
            "high_count": 1,
            "characters_found": ["Alice", "Bob"],
            "locations_found": ["park", "library"],
        }

        review = ConsistencyReview.from_dict(data)

        assert review.content_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 85
        assert review.character_score == 90
        assert len(review.issues) == 1
        assert review.issues[0].issue_type == ConsistencyIssueType.CHARACTER_NAME
        assert review.issues[0].severity == ConsistencySeverity.HIGH
        assert "Alice" in review.characters_found
        assert "Bob" in review.characters_found

    def test_round_trip_serialization(self):
        """Test that serialization preserves all data."""
        original = ConsistencyReview(
            content_id="script-001",
            overall_score=80,
            character_score=85,
            timeline_score=80,
            location_score=75,
            detail_score=80,
        )

        original.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.LOCATION,
                severity=ConsistencySeverity.MEDIUM,
                location="Scene 5",
                description="Location issue",
                details="Location unclear",
                suggestion="Clarify",
            )
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = ConsistencyReview.from_dict(data)

        assert restored.content_id == original.content_id
        assert restored.overall_score == original.overall_score
        assert restored.character_score == original.character_score
        assert restored.timeline_score == original.timeline_score
        assert len(restored.issues) == len(original.issues)
        assert restored.issues[0].description == original.issues[0].description


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_review_content_consistency(self):
        """Test review_content_consistency function."""
        script = """Emma walked through the forest.
The trees were tall and ancient.
Emma found a clearing and rested."""

        review = review_content_consistency(script, "test-001", "v3", 80)

        assert review.content_id == "test-001"
        assert review.script_version == "v3"
        assert review.overall_score >= 0
        assert review.passes is not None

    def test_review_content_consistency_to_json(self):
        """Test review_content_consistency_to_json function."""
        script = "Alice met Bob. They talked."

        json_result = review_content_consistency_to_json(script, "test-002", "v3", 80)

        assert json_result is not None
        data = json.loads(json_result)
        assert data["content_id"] == "test-002"
        assert data["script_version"] == "v3"
        assert "overall_score" in data
        assert "passes" in data

    def test_get_consistency_feedback(self):
        """Test get_consistency_feedback function."""
        review = ConsistencyReview(content_id="script-001", overall_score=85, passes=True)

        review.add_issue(
            ConsistencyIssue(
                issue_type=ConsistencyIssueType.CHARACTER_NAME,
                severity=ConsistencySeverity.HIGH,
                location="Line 10",
                description="Character issue",
                details="Name varies",
                suggestion="Fix",
            )
        )

        feedback = get_consistency_feedback(review)

        assert feedback["content_id"] == "script-001"
        assert feedback["passes"] is True
        assert feedback["overall_score"] == 85
        assert "next_action" in feedback
        assert len(feedback["high_priority_issues"]) == 1
        assert len(feedback["character_issues"]) == 1


class TestInconsistentScript:
    """Test with inconsistent scripts."""

    def test_inconsistent_content_with_multiple_issues(self):
        """Test that a script with multiple issues gets proper review."""
        script = """John walked into the house.
Johnny picked up the phone.
John left the building.
Later, Johnny came back."""

        review = review_content_consistency(script, "test-001", "v3", 80)

        # Should have character name issues
        character_issues = review.get_character_issues()
        assert len(character_issues) > 0

        # Check that characters were tracked
        assert len(review.characters_found) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
