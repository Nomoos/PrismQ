"""Tests for unified ReviewSeverity enum in PrismQ.T.Review.

These tests verify that the unified ReviewSeverity enum works correctly
and is properly exported from all child review modules.
"""

import pytest
from enum import Enum


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
    
    def test_export_from_grammar(self):
        """Test that ReviewSeverity is exported from Grammar module."""
        from T.Review.Grammar import ReviewSeverity, GrammarSeverity
        from T.Review import ReviewSeverity as ParentReviewSeverity
        
        # Should be the same class
        assert ReviewSeverity is ParentReviewSeverity
        
        # GrammarSeverity should still work (backward compatibility)
        assert GrammarSeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value
    
    def test_export_from_tone(self):
        """Test that ReviewSeverity is exported from Tone module."""
        from T.Review.Tone import ReviewSeverity, ToneSeverity
        from T.Review import ReviewSeverity as ParentReviewSeverity
        
        assert ReviewSeverity is ParentReviewSeverity
        assert ToneSeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value
    
    def test_export_from_content(self):
        """Test that ReviewSeverity is exported from Content module."""
        from T.Review.Content import ReviewSeverity, ContentSeverity
        from T.Review import ReviewSeverity as ParentReviewSeverity
        
        assert ReviewSeverity is ParentReviewSeverity
        assert ContentSeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value
    
    def test_export_from_consistency(self):
        """Test that ReviewSeverity is exported from Consistency module."""
        from T.Review.Consistency import ReviewSeverity, ConsistencySeverity
        from T.Review import ReviewSeverity as ParentReviewSeverity
        
        assert ReviewSeverity is ParentReviewSeverity
        assert ConsistencySeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value
    
    def test_export_from_editing(self):
        """Test that ReviewSeverity is exported from Editing module."""
        from T.Review.Editing import ReviewSeverity, EditingSeverity
        from T.Review import ReviewSeverity as ParentReviewSeverity
        
        assert ReviewSeverity is ParentReviewSeverity
        assert EditingSeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value
    
    def test_export_from_readability(self):
        """Test that ReviewSeverity is exported from Readability module."""
        from T.Review.Readability import ReviewSeverity, ReadabilitySeverity
        from T.Review import ReviewSeverity as ParentReviewSeverity
        
        assert ReviewSeverity is ParentReviewSeverity
        assert ReadabilitySeverity.CRITICAL.value == ReviewSeverity.CRITICAL.value


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility with module-specific severity enums."""
    
    def test_grammar_severity_still_works(self):
        """Test that GrammarSeverity can still be used in GrammarReview."""
        from T.Review.Grammar import GrammarReview, GrammarIssue, GrammarIssueType, GrammarSeverity
        
        issue = GrammarIssue(
            issue_type=GrammarIssueType.SPELLING,
            severity=GrammarSeverity.HIGH,
            line_number=1,
            text="recieve",
            suggestion="receive",
            explanation="Common spelling error"
        )
        
        review = GrammarReview(script_id="test-001", overall_score=90)
        review.add_issue(issue)
        
        assert len(review.issues) == 1
        assert review.high_count == 1
    
    def test_consistency_severity_still_works(self):
        """Test that ConsistencySeverity can still be used in ConsistencyReview."""
        from T.Review.Consistency import (
            ConsistencyReview, ConsistencyIssue, 
            ConsistencyIssueType, ConsistencySeverity
        )
        
        issue = ConsistencyIssue(
            issue_type=ConsistencyIssueType.CHARACTER_NAME,
            severity=ConsistencySeverity.MEDIUM,
            section="Chapter 1",
            description="Name inconsistency"
        )
        
        review = ConsistencyReview(script_id="test-001", overall_score=85)
        review.add_issue(issue)
        
        assert len(review.issues) == 1
        assert review.medium_count == 1
