"""Comprehensive tests for Title Readability Review (MVP-019).

This test suite validates the implementation of the title readability review,
ensuring it correctly evaluates titles based on voiceover suitability, clarity,
length, engagement, rhythm, and mouthfeel.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import json
from datetime import datetime

import pytest

from T.Review.Title.Readability import (
    ReadabilityIssue,
    ReadabilityIssueType,
    ReadabilitySeverity,
    TitleReadabilityReview,
)


class TestTitleReadabilityReviewModel:
    """Test the TitleReadabilityReview data model."""

    def test_create_basic_review(self):
        """Test creating a basic readability review."""
        review = TitleReadabilityReview(
            title_id="title-001",
            title_text="The Echo Mystery",
            title_version="v3",
            overall_score=90,
        )

        assert review.title_id == "title-001"
        assert review.title_text == "The Echo Mystery"
        assert review.title_version == "v3"
        assert review.overall_score == 90
        assert review.pass_threshold == 85
        assert review.passes is True
        assert len(review.issues) == 0
        assert review.critical_count == 0
        assert review.high_count == 0
        assert review.medium_count == 0
        assert review.low_count == 0

        print("✓ Can create basic TitleReadabilityReview")

    def test_review_with_timestamp(self):
        """Test that review includes timestamp."""
        review = TitleReadabilityReview(
            title_id="title-002",
            title_text="Dark Secrets Revealed",
            title_version="v4",
            overall_score=88,
        )

        assert review.reviewed_at is not None
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(review.reviewed_at)

        print("✓ Review includes timestamp")

    def test_review_passes_with_high_score(self):
        """Test review passes when score >= threshold."""
        review = TitleReadabilityReview(
            title_id="title-003",
            title_text="Mystery Unveiled",
            title_version="v3",
            overall_score=85,
        )

        assert review.passes is True
        assert review.overall_score >= review.pass_threshold

        print("✓ Review passes with score >= threshold")

    def test_review_fails_with_low_score(self):
        """Test review fails when score < threshold."""
        review = TitleReadabilityReview(
            title_id="title-004", title_text="Test Title", title_version="v3", overall_score=75
        )

        assert review.passes is False
        assert review.overall_score < review.pass_threshold

        print("✓ Review fails with score < threshold")


class TestReadabilityIssue:
    """Test the ReadabilityIssue model."""

    def test_create_readability_issue(self):
        """Test creating a readability issue."""
        issue = ReadabilityIssue(
            issue_type=ReadabilityIssueType.MOUTHFEEL,
            severity=ReadabilitySeverity.HIGH,
            text="Dark Cryptographic Secrets",
            suggestion="Hidden Digital Secrets",
            explanation="Multiple consonant clusters make it hard to say aloud",
            confidence=90,
        )

        assert issue.issue_type == ReadabilityIssueType.MOUTHFEEL
        assert issue.severity == ReadabilitySeverity.HIGH
        assert issue.text == "Dark Cryptographic Secrets"
        assert issue.suggestion == "Hidden Digital Secrets"
        assert "consonant clusters" in issue.explanation
        assert issue.confidence == 90

        print("✓ Can create ReadabilityIssue")

    def test_issue_types(self):
        """Test all issue types are available."""
        issue_types = [
            ReadabilityIssueType.CLARITY,
            ReadabilityIssueType.LENGTH,
            ReadabilityIssueType.ENGAGEMENT,
            ReadabilityIssueType.VOICEOVER_FLOW,
            ReadabilityIssueType.RHYTHM,
            ReadabilityIssueType.MOUTHFEEL,
            ReadabilityIssueType.PRONUNCIATION,
            ReadabilityIssueType.LISTENING_CLARITY,
        ]

        for issue_type in issue_types:
            issue = ReadabilityIssue(
                issue_type=issue_type,
                severity=ReadabilitySeverity.MEDIUM,
                text="Sample text",
                suggestion="Improved text",
                explanation="Sample explanation",
            )
            assert issue.issue_type == issue_type

        print("✓ All issue types are available")

    def test_severity_levels(self):
        """Test all severity levels are available."""
        severity_levels = [
            ReadabilitySeverity.CRITICAL,
            ReadabilitySeverity.HIGH,
            ReadabilitySeverity.MEDIUM,
            ReadabilitySeverity.LOW,
        ]

        for severity in severity_levels:
            issue = ReadabilityIssue(
                issue_type=ReadabilityIssueType.CLARITY,
                severity=severity,
                text="Test",
                suggestion="Better",
                explanation="Reason",
            )
            assert issue.severity == severity

        print("✓ All severity levels are available")


class TestAddingIssues:
    """Test adding issues to reviews."""

    def test_add_single_issue(self):
        """Test adding a single issue."""
        review = TitleReadabilityReview(
            title_id="title-005", title_text="Test Title", title_version="v3", overall_score=90
        )

        issue = ReadabilityIssue(
            issue_type=ReadabilityIssueType.VOICEOVER_FLOW,
            severity=ReadabilitySeverity.MEDIUM,
            text="Test Title",
            suggestion="Better Title",
            explanation="Flow could be improved",
        )

        review.add_issue(issue)

        assert len(review.issues) == 1
        assert review.medium_count == 1
        assert review.issues[0] == issue

        print("✓ Can add single issue")

    def test_add_critical_issue_fails_review(self):
        """Test that adding a critical issue fails the review."""
        review = TitleReadabilityReview(
            title_id="title-006",
            title_text="Critical Issue Title",
            title_version="v3",
            overall_score=90,
        )

        assert review.passes is True

        issue = ReadabilityIssue(
            issue_type=ReadabilityIssueType.LISTENING_CLARITY,
            severity=ReadabilitySeverity.CRITICAL,
            text="Critical Issue Title",
            suggestion="Clear Title",
            explanation="Completely unclear when listened to",
        )

        review.add_issue(issue)

        assert review.passes is False
        assert review.critical_count == 1
        assert len(review.get_critical_issues()) == 1

        print("✓ Critical issue fails review")

    def test_add_multiple_issues(self):
        """Test adding multiple issues with different severities."""
        review = TitleReadabilityReview(
            title_id="title-007",
            title_text="Multiple Issues Title",
            title_version="v3",
            overall_score=88,
        )

        issues = [
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.CLARITY,
                severity=ReadabilitySeverity.HIGH,
                text="Part 1",
                suggestion="Better Part 1",
                explanation="Unclear",
            ),
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.MOUTHFEEL,
                severity=ReadabilitySeverity.MEDIUM,
                text="Part 2",
                suggestion="Better Part 2",
                explanation="Hard to say",
            ),
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.RHYTHM,
                severity=ReadabilitySeverity.LOW,
                text="Part 3",
                suggestion="Better Part 3",
                explanation="Minor rhythm issue",
            ),
        ]

        for issue in issues:
            review.add_issue(issue)

        assert len(review.issues) == 3
        assert review.high_count == 1
        assert review.medium_count == 1
        assert review.low_count == 1
        assert review.critical_count == 0

        print("✓ Can add multiple issues")


class TestIssueFiltering:
    """Test filtering issues by various criteria."""

    def test_get_issues_by_severity(self):
        """Test filtering issues by severity."""
        review = TitleReadabilityReview(
            title_id="title-008", title_text="Filter Test", title_version="v3", overall_score=85
        )

        # Add issues with different severities
        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.CLARITY,
                severity=ReadabilitySeverity.HIGH,
                text="High 1",
                suggestion="Fix",
                explanation="Reason",
            )
        )
        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.LENGTH,
                severity=ReadabilitySeverity.HIGH,
                text="High 2",
                suggestion="Fix",
                explanation="Reason",
            )
        )
        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.RHYTHM,
                severity=ReadabilitySeverity.LOW,
                text="Low 1",
                suggestion="Fix",
                explanation="Reason",
            )
        )

        high_issues = review.get_issues_by_severity(ReadabilitySeverity.HIGH)
        low_issues = review.get_issues_by_severity(ReadabilitySeverity.LOW)

        assert len(high_issues) == 2
        assert len(low_issues) == 1
        assert all(issue.severity == ReadabilitySeverity.HIGH for issue in high_issues)
        assert all(issue.severity == ReadabilitySeverity.LOW for issue in low_issues)

        print("✓ Can filter issues by severity")

    def test_get_issues_by_type(self):
        """Test filtering issues by type."""
        review = TitleReadabilityReview(
            title_id="title-009",
            title_text="Type Filter Test",
            title_version="v3",
            overall_score=86,
        )

        # Add issues with different types
        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.MOUTHFEEL,
                severity=ReadabilitySeverity.MEDIUM,
                text="Mouthfeel 1",
                suggestion="Fix",
                explanation="Reason",
            )
        )
        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.MOUTHFEEL,
                severity=ReadabilitySeverity.HIGH,
                text="Mouthfeel 2",
                suggestion="Fix",
                explanation="Reason",
            )
        )
        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.RHYTHM,
                severity=ReadabilitySeverity.LOW,
                text="Rhythm 1",
                suggestion="Fix",
                explanation="Reason",
            )
        )

        mouthfeel_issues = review.get_issues_by_type(ReadabilityIssueType.MOUTHFEEL)
        rhythm_issues = review.get_issues_by_type(ReadabilityIssueType.RHYTHM)

        assert len(mouthfeel_issues) == 2
        assert len(rhythm_issues) == 1
        assert all(issue.issue_type == ReadabilityIssueType.MOUTHFEEL for issue in mouthfeel_issues)

        print("✓ Can filter issues by type")

    def test_get_high_priority_issues(self):
        """Test getting high priority (critical + high) issues."""
        review = TitleReadabilityReview(
            title_id="title-010", title_text="Priority Test", title_version="v3", overall_score=95
        )

        # Add issues with different severities
        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.CLARITY,
                severity=ReadabilitySeverity.CRITICAL,
                text="Critical",
                suggestion="Fix",
                explanation="Reason",
            )
        )
        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.LENGTH,
                severity=ReadabilitySeverity.HIGH,
                text="High",
                suggestion="Fix",
                explanation="Reason",
            )
        )
        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.RHYTHM,
                severity=ReadabilitySeverity.MEDIUM,
                text="Medium",
                suggestion="Fix",
                explanation="Reason",
            )
        )

        high_priority = review.get_high_priority_issues()

        assert len(high_priority) == 2
        assert any(issue.severity == ReadabilitySeverity.CRITICAL for issue in high_priority)
        assert any(issue.severity == ReadabilitySeverity.HIGH for issue in high_priority)

        print("✓ Can get high priority issues")


class TestSerialization:
    """Test serialization and deserialization."""

    def test_to_dict(self):
        """Test converting review to dictionary."""
        review = TitleReadabilityReview(
            title_id="title-011",
            title_text="Serialization Test",
            title_version="v3",
            overall_score=87,
        )

        review.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.VOICEOVER_FLOW,
                severity=ReadabilitySeverity.MEDIUM,
                text="Test",
                suggestion="Better",
                explanation="Flow issue",
            )
        )

        data = review.to_dict()

        assert isinstance(data, dict)
        assert data["title_id"] == "title-011"
        assert data["title_text"] == "Serialization Test"
        assert data["overall_score"] == 87
        assert len(data["issues"]) == 1
        assert data["issues"][0]["issue_type"] == "voiceover_flow"
        assert data["issues"][0]["severity"] == "medium"

        print("✓ Can convert to dict")

    def test_from_dict(self):
        """Test creating review from dictionary."""
        data = {
            "title_id": "title-012",
            "title_text": "From Dict Test",
            "title_version": "v4",
            "overall_score": 89,
            "pass_threshold": 85,
            "passes": True,
            "issues": [
                {
                    "issue_type": "mouthfeel",
                    "severity": "high",
                    "text": "Test Text",
                    "suggestion": "Better Text",
                    "explanation": "Reason",
                    "confidence": 90,
                }
            ],
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "reviewer_id": "AI-ReadabilityReviewer-001",
            "reviewed_at": "2024-01-01T00:00:00",
            "confidence_score": 90,
            "summary": "",
            "voiceover_notes": [],
            "quick_fixes": [],
            "notes": "",
            "metadata": {},
        }

        review = TitleReadabilityReview.from_dict(data)

        assert review.title_id == "title-012"
        assert review.title_text == "From Dict Test"
        assert review.overall_score == 89
        assert len(review.issues) == 1
        assert review.issues[0].issue_type == ReadabilityIssueType.MOUTHFEEL
        assert review.issues[0].severity == ReadabilitySeverity.HIGH

        print("✓ Can create from dict")

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization are consistent."""
        original = TitleReadabilityReview(
            title_id="title-013", title_text="Roundtrip Test", title_version="v3", overall_score=92
        )

        original.add_issue(
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.RHYTHM,
                severity=ReadabilitySeverity.LOW,
                text="Test",
                suggestion="Better",
                explanation="Minor rhythm",
            )
        )

        # Serialize and deserialize
        data = original.to_dict()
        restored = TitleReadabilityReview.from_dict(data)

        assert restored.title_id == original.title_id
        assert restored.title_text == original.title_text
        assert restored.overall_score == original.overall_score
        assert len(restored.issues) == len(original.issues)
        assert restored.issues[0].issue_type == original.issues[0].issue_type

        print("✓ Roundtrip serialization works")


class TestVoiceoverSpecificFeatures:
    """Test voiceover-specific features."""

    def test_voiceover_notes(self):
        """Test voiceover_notes field."""
        review = TitleReadabilityReview(
            title_id="title-014", title_text="Voiceover Test", title_version="v3", overall_score=88
        )

        review.voiceover_notes.append("Add dramatic pause after 'Mystery'")
        review.voiceover_notes.append("Emphasize 'revealed' for impact")

        assert len(review.voiceover_notes) == 2
        assert "dramatic pause" in review.voiceover_notes[0]

        print("✓ Voiceover notes work correctly")

    def test_voiceover_issue_types(self):
        """Test voiceover-specific issue types."""
        review = TitleReadabilityReview(
            title_id="title-015",
            title_text="Voiceover Issue Test",
            title_version="v3",
            overall_score=85,
        )

        # Add voiceover-specific issues
        voiceover_issues = [
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.VOICEOVER_FLOW,
                severity=ReadabilitySeverity.MEDIUM,
                text="Test",
                suggestion="Better",
                explanation="Poor voiceover flow",
            ),
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.MOUTHFEEL,
                severity=ReadabilitySeverity.HIGH,
                text="Test",
                suggestion="Better",
                explanation="Difficult to say aloud",
            ),
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.PRONUNCIATION,
                severity=ReadabilitySeverity.MEDIUM,
                text="Test",
                suggestion="Better",
                explanation="Hard to pronounce",
            ),
            ReadabilityIssue(
                issue_type=ReadabilityIssueType.LISTENING_CLARITY,
                severity=ReadabilitySeverity.HIGH,
                text="Test",
                suggestion="Better",
                explanation="Unclear when listened to",
            ),
        ]

        for issue in voiceover_issues:
            review.add_issue(issue)

        assert len(review.issues) == 4

        # Verify voiceover-specific types are present
        issue_types = [issue.issue_type for issue in review.issues]
        assert ReadabilityIssueType.VOICEOVER_FLOW in issue_types
        assert ReadabilityIssueType.MOUTHFEEL in issue_types
        assert ReadabilityIssueType.PRONUNCIATION in issue_types
        assert ReadabilityIssueType.LISTENING_CLARITY in issue_types

        print("✓ Voiceover-specific issue types work")


class TestWorkflowIntegration:
    """Test workflow integration scenarios."""

    def test_passes_ready_for_finalization(self):
        """Test that passing review indicates ready for finalization."""
        review = TitleReadabilityReview(
            title_id="title-016",
            title_text="Perfect Voiceover Title",
            title_version="v3",
            overall_score=95,
        )

        assert review.passes is True
        assert review.critical_count == 0

        print("✓ Passing review ready for finalization")

    def test_fails_returns_to_refinement(self):
        """Test that failing review returns to refinement."""
        review = TitleReadabilityReview(
            title_id="title-017",
            title_text="Needs Work Title",
            title_version="v3",
            overall_score=80,
        )

        assert review.passes is False

        print("✓ Failing review returns to refinement")

    def test_metadata_tracking(self):
        """Test metadata tracking for workflow."""
        review = TitleReadabilityReview(
            title_id="title-018", title_text="Metadata Test", title_version="v3", overall_score=90
        )

        review.metadata["content_id"] = "script-123"
        review.metadata["script_version"] = "v3"
        review.metadata["workflow_stage"] = "MVP-019"

        assert review.metadata["content_id"] == "script-123"
        assert review.metadata["workflow_stage"] == "MVP-019"

        print("✓ Metadata tracking works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
