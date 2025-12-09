"""Tests for unified ReviewSeverity enum in PrismQ.T.Review.

These tests verify that the unified ReviewSeverity enum works correctly
and is properly exported from all child review modules.
"""

from enum import Enum

import pytest


class TestReviewSeverityEnum:
    """Tests for the unified ReviewSeverity enum."""

    def test_import_from_parent_module(self):
        """Test that ReviewSeverity can be imported from T.Review."""
        from T.Review import ReviewSeverity

        assert issubclass(ReviewSeverity, Enum)

    def test_severity_values(self):
        """Test that ReviewSeverity has the expected values."""
        from T.Review import ReviewSeverity

        assert ReviewSeverity.CRITICAL.value == "critical"
        assert ReviewSeverity.HIGH.value == "high"
        assert ReviewSeverity.MEDIUM.value == "medium"
        assert ReviewSeverity.LOW.value == "low"

    def test_severity_has_four_levels(self):
        """Test that ReviewSeverity has exactly four levels."""
        from T.Review import ReviewSeverity

        assert len(ReviewSeverity) == 4


class TestReviewSeverityExports:
    """Tests for ReviewSeverity exports from child modules."""

    def test_export_from_script_grammar(self):
        """Test that GrammarSeverity is exported from Script.Grammar module."""
        from T.Review import ReviewSeverity
        from T.Review.Script.Grammar import GrammarSeverity

        # GrammarSeverity should have same values as ReviewSeverity
        assert GrammarSeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value

    def test_export_from_script_tone(self):
        """Test that ToneSeverity is exported from Script.Tone module."""
        from T.Review import ReviewSeverity
        from T.Review.Script.Tone import ToneSeverity

        assert ToneSeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value

    def test_export_from_script_content(self):
        """Test that ContentSeverity is exported from Script.Content module."""
        from T.Review import ReviewSeverity
        from T.Review.Script.Content import ContentSeverity

        assert ContentSeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value

    def test_export_from_script_consistency(self):
        """Test that ConsistencySeverity is exported from Script.Consistency module."""
        from T.Review import ReviewSeverity
        from T.Review.Script.Consistency import ConsistencySeverity

        assert ConsistencySeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value

    def test_export_from_script_editing(self):
        """Test that EditingSeverity is exported from Script.Editing module."""
        from T.Review import ReviewSeverity
        from T.Review.Script.Editing import EditingSeverity

        assert EditingSeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value

    def test_export_from_title_readability(self):
        """Test that ReadabilitySeverity is exported from Title.Readability module."""
        from T.Review import ReviewSeverity
        from T.Review.Title.Readability import ReadabilitySeverity

        assert ReadabilitySeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with module-specific severity enums."""

    def test_grammar_severity_still_works(self):
        """Test that GrammarSeverity can still be used in GrammarReview."""
        from T.Review.Script.Grammar import (
            GrammarIssue,
            GrammarIssueType,
            GrammarReview,
            GrammarSeverity,
        )

        issue = GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.HIGH,
            line_number=1,
            text="recieve",
            suggestion="receive",
            explanation="Common spelling error",
        )

        review = GrammarReview(script_id="test-001", overall_score=90)
        review.add_issue(issue)

        assert len(review.issues) == 1
        assert review.high_count == 1

    def test_consistency_severity_still_works(self):
        """Test that ConsistencySeverity can still be used in ConsistencyReview."""
        from T.Review.Script.Consistency import (
            ConsistencyIssue,
            ConsistencyIssueType,
            ConsistencyReview,
            ConsistencySeverity,
        )

        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.MEDIUM,
            location="Chapter 1",
            description="Name inconsistency",
            details="Character named differently",
            suggestion="Use consistent name",
        )

        review = ConsistencyReview(script_id="test-001", overall_score=85)
        review.add_issue(issue)

        assert len(review.issues) == 1
        assert review.medium_count == 1
