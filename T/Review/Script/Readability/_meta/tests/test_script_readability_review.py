"""Tests for ReadabilityReview model and ScriptReadabilityChecker."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import json

import pytest

from T.Review.Content.Readability import (
    ReadabilityIssue,
    ReadabilityIssueType,
    ReadabilityReview,
    ReadabilitySeverity,
    ScriptReadabilityChecker,
    get_readability_feedback,
    review_content_readability,
    review_content_readability_to_json,
)


class TestReadabilityReviewBasic:
    """Test basic ReadabilityReview functionality."""

    def test_create_basic_review(self):
        """Test creating a basic ReadabilityReview instance."""
        review = ReadabilityReview(
            content_id="script-001",
            script_version="v3",
            overall_score=90,
            pronunciation_score=92,
            pacing_score=90,
            flow_score=88,
            mouthfeel_score=91,
        )

        assert review.content_id == "script-001"
        assert review.script_version == "v3"
        assert review.overall_score == 90
        assert review.pass_threshold == 85
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0
        assert review.high_count == 0
        assert review.pronunciation_score == 92
        assert review.pacing_score == 90
        assert review.flow_score == 88
        assert review.mouthfeel_score == 91
        assert review.reviewer_id == "AI-ReadabilityReviewer-001"
        assert review.reviewed_at is not None
        assert review.confidence_score == 85

    def test_create_failing_review(self):
        """Test creating a review that fails."""
        review = ReadabilityReview(
            content_id="script-002", script_version="v3", overall_score=75  # Below threshold of 85
        )

        assert review.passes is False

    def test_readable_content_passes(self):
        """Test that a readable script passes review."""
        review = ReadabilityReview(
            content_id="script-readable",
            script_version="v3",
            overall_score=95,
            pronunciation_score=98,
            pacing_score=94,
            flow_score=93,
            mouthfeel_score=96,
        )

        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0


class TestReadabilityIssue:
    """Test ReadabilityIssue functionality."""

    def test_create_pronunciation_issue(self):
        """Test creating a pronunciation issue."""
        issue = ReadabilityIssue(
            issue_type=ReadabilityIssueType.PRONUNCIATION,
            severity=ReadabilitySeverity.HIGH,
            line_number=15,
            text="The phenomenon of phosphorescence perplexed physicists",
            suggestion="The glowing effect puzzled scientists",
            explanation="Too many 'ph' and 'p' sounds create a tongue twister",
        )

        assert issue.issue_type == ReadabilityIssueType.PRONUNCIATION
        assert issue.severity == ReadabilitySeverity.HIGH
        assert issue.line_number == 15
        assert issue.confidence == 85

    def test_create_pacing_issue(self):
        """Test creating a pacing issue."""
        issue = ReadabilityIssue(
            issue_type=ReadabilityIssueType.PACING,
            severity=ReadabilitySeverity.MEDIUM,
            line_number=42,
            text="This is a very long sentence...",
            suggestion="Break into shorter sentences",
            explanation="Long sentence makes voiceover difficult",
        )

        assert issue.issue_type == ReadabilityIssueType.PACING
        assert issue.severity == ReadabilitySeverity.MEDIUM

    def test_create_tongue_twister_issue(self):
        """Test creating a tongue twister issue."""
        issue = ReadabilityIssue(
            issue_type=ReadabilityIssueType.TONGUE_TWISTER,
            severity=ReadabilitySeverity.MEDIUM,
            line_number=7,
            text="She sells seashells by the seashore",
            suggestion="Reduce repetition of 's' sound",
            explanation="Multiple 's' sounds create a tongue twister",
        )

        assert issue.issue_type == ReadabilityIssueType.TONGUE_TWISTER
        assert "tongue twister" in issue.explanation.lower()


class TestReadabilityReviewIssueManagement:
    """Test ReadabilityReview issue management."""

    def test_add_issue_updates_counts(self):
        """Test that adding issues updates severity counts."""
        review = ReadabilityReview(content_id="script-001", script_version="v3")

        # Add a high severity issue
        issue1 = ReadabilityIssue(
            issue_type=ReadabilityIssueType.PRONUNCIATION,
            severity=ReadabilitySeverity.HIGH,
            line_number=1,
            text="test",
            suggestion="test",
            explanation="test",
        )
        review.add_issue(issue1)

        assert review.high_count == 1
        assert review.critical_count == 0
        assert len(review.issues) == 1

        # Add a critical issue
        issue2 = ReadabilityIssue(
            issue_type=ReadabilityIssueType.PRONUNCIATION,
            severity=ReadabilitySeverity.CRITICAL,
            line_number=2,
            text="test",
            suggestion="test",
            explanation="test",
        )
        review.add_issue(issue2)

        assert review.critical_count == 1
        assert review.high_count == 1
        assert len(review.issues) == 2
        assert review.passes is False  # Critical issues cause failure

    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        review = ReadabilityReview(content_id="script-001")

        issue_high = ReadabilityIssue(
            issue_type=ReadabilityIssueType.PACING,
            severity=ReadabilitySeverity.HIGH,
            line_number=1,
            text="test",
            suggestion="test",
            explanation="test",
        )

        issue_low = ReadabilityIssue(
            issue_type=ReadabilityIssueType.MOUTHFEEL,
            severity=ReadabilitySeverity.LOW,
            line_number=2,
            text="test",
            suggestion="test",
            explanation="test",
        )

        review.add_issue(issue_high)
        review.add_issue(issue_low)

        high_issues = review.get_issues_by_severity(ReadabilitySeverity.HIGH)
        low_issues = review.get_issues_by_severity(ReadabilitySeverity.LOW)

        assert len(high_issues) == 1
        assert len(low_issues) == 1
        assert high_issues[0].severity == ReadabilitySeverity.HIGH

    def test_get_issues_by_type(self):
        """Test filtering issues by type."""
        review = ReadabilityReview(content_id="script-001")

        issue_pronunciation = ReadabilityIssue(
            issue_type=ReadabilityIssueType.PRONUNCIATION,
            severity=ReadabilitySeverity.HIGH,
            line_number=1,
            text="test",
            suggestion="test",
            explanation="test",
        )

        issue_pacing = ReadabilityIssue(
            issue_type=ReadabilityIssueType.PACING,
            severity=ReadabilitySeverity.MEDIUM,
            line_number=2,
            text="test",
            suggestion="test",
            explanation="test",
        )

        review.add_issue(issue_pronunciation)
        review.add_issue(issue_pacing)

        pronunciation_issues = review.get_issues_by_type(ReadabilityIssueType.PRONUNCIATION)
        pacing_issues = review.get_issues_by_type(ReadabilityIssueType.PACING)

        assert len(pronunciation_issues) == 1
        assert len(pacing_issues) == 1


class TestScriptReadabilityChecker:
    """Test ScriptReadabilityChecker functionality."""

    def test_simple_content_passes(self):
        """Test that a simple, readable script passes."""
        checker = ScriptReadabilityChecker(pass_threshold=85)
        script = "This is a simple script.\nIt has short sentences.\nEasy to read and speak."

        review = checker.review_content(script, "test-001", "v3")

        assert review.passes is True
        assert review.overall_score >= 85
        assert len(review.issues) == 0

    def test_tongue_twister_detected(self):
        """Test detection of tongue twisters."""
        checker = ScriptReadabilityChecker(pass_threshold=85)
        script = "She sells seashells by the seashore, specifically selecting superior specimens."

        review = checker.review_content(script, "test-002", "v3")

        # Should detect tongue twister pattern
        twister_issues = [
            i for i in review.issues if i.issue_type == ReadabilityIssueType.TONGUE_TWISTER
        ]
        assert len(twister_issues) > 0

    def test_long_sentence_detected(self):
        """Test detection of overly long sentences."""
        checker = ScriptReadabilityChecker(pass_threshold=85)
        # Create a sentence with more than 20 words
        script = "This is a very long sentence that goes on and on without any natural pauses or breathing points making it difficult for voiceover."

        review = checker.review_content(script, "test-003", "v3")

        # Should detect pacing issue
        pacing_issues = [i for i in review.issues if i.issue_type == ReadabilityIssueType.PACING]
        assert len(pacing_issues) > 0

    def test_complex_words_detected(self):
        """Test detection of complex words."""
        checker = ScriptReadabilityChecker(pass_threshold=85)
        script = "The methodology employed in the implementation was quintessential."

        review = checker.review_content(script, "test-004", "v3")

        # Should detect complex word issues
        mouthfeel_issues = [
            i for i in review.issues if i.issue_type == ReadabilityIssueType.MOUTHFEEL
        ]
        assert len(mouthfeel_issues) > 0

    def test_skip_stage_directions(self):
        """Test that stage directions are skipped."""
        checker = ScriptReadabilityChecker(pass_threshold=85)
        script = "[Stage direction with complex words]\nINT. Very long location description with many words.\nNormal dialogue line here."

        review = checker.review_content(script, "test-005", "v3")

        # Should not flag stage directions
        assert review.overall_score >= 85

    def test_critical_issue_fails_review(self):
        """Test that critical issues cause review to fail."""
        review = ReadabilityReview(
            content_id="script-critical", script_version="v3", overall_score=90  # Good score but...
        )

        # Add a critical issue
        critical_issue = ReadabilityIssue(
            issue_type=ReadabilityIssueType.PRONUNCIATION,
            severity=ReadabilitySeverity.CRITICAL,
            line_number=1,
            text="test",
            suggestion="test",
            explanation="test",
        )
        review.add_issue(critical_issue)

        # Should fail despite good score
        assert review.passes is False


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_review_content_readability(self):
        """Test the convenience function."""
        script = "This is a simple test script."
        review = review_content_readability(script, "test-001", "v3")

        assert isinstance(review, ReadabilityReview)
        assert review.content_id == "test-001"
        assert review.script_version == "v3"

    def test_review_content_readability_to_json(self):
        """Test JSON conversion."""
        script = "This is a simple test script."
        json_str = review_content_readability_to_json(script, "test-001", "v3")

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["content_id"] == "test-001"
        assert data["script_version"] == "v3"
        assert "overall_score" in data
        assert "issues" in data

    def test_get_readability_feedback(self):
        """Test feedback extraction."""
        script = "She sells seashells by the seashore."
        review = review_content_readability(script, "test-001", "v3")
        feedback = get_readability_feedback(review)

        assert "content_id" in feedback
        assert "passes" in feedback
        assert "overall_score" in feedback
        assert "voiceover_notes" in feedback
        assert "next_action" in feedback


class TestScoreCalculation:
    """Test score calculation logic."""

    def test_pronunciation_score_calculation(self):
        """Test pronunciation score calculation."""
        checker = ScriptReadabilityChecker(pass_threshold=85)
        script = "The strengths of this method remained unclear."

        review = checker.review_content(script, "test-001", "v3")

        # Should have good overall score for one issue
        assert 0 <= review.pronunciation_score <= 100
        assert 0 <= review.overall_score <= 100

    def test_multiple_issues_lower_score(self):
        """Test that multiple issues lower the score."""
        checker = ScriptReadabilityChecker(pass_threshold=85)

        # Content with multiple issues
        script = """Peter Piper picked particularly problematic peppers persistently.
She sells seashells specifically by the seashore.
This is a very long sentence that goes on and on and on without any natural pauses or breathing points whatsoever making it extremely difficult for any voiceover artist to deliver smoothly.
The methodology employed in the implementation of the aforementioned functionality was quintessential."""

        review = checker.review_content(script, "test-001", "v3")

        # Should have lower score due to multiple issues
        assert len(review.issues) > 0
        assert review.overall_score < 100


class TestSerializationDeserialization:
    """Test serialization and deserialization."""

    def test_to_dict_and_from_dict(self):
        """Test converting to dict and back."""
        review1 = ReadabilityReview(content_id="script-001", script_version="v3", overall_score=90)

        issue = ReadabilityIssue(
            issue_type=ReadabilityIssueType.PACING,
            severity=ReadabilitySeverity.HIGH,
            line_number=1,
            text="test text",
            suggestion="test suggestion",
            explanation="test explanation",
        )
        review1.add_issue(issue)

        # Convert to dict
        data = review1.to_dict()

        # Convert back
        review2 = ReadabilityReview.from_dict(data)

        assert review2.content_id == review1.content_id
        assert review2.script_version == review1.script_version
        assert review2.overall_score == review1.overall_score
        assert len(review2.issues) == len(review1.issues)
        assert review2.issues[0].issue_type == review1.issues[0].issue_type


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
