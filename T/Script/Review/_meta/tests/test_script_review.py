"""Tests for ScriptReview model."""

import pytest
from datetime import datetime
from T.Script.Review import (
    ScriptReview,
    ReviewCategory,
    ContentLength,
    ImprovementPoint,
    CategoryScore
)


class TestScriptReviewBasic:
    """Test basic ScriptReview functionality."""
    
    def test_create_basic_review(self):
        """Test creating a basic ScriptReview instance."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Test Script",
            overall_score=75
        )
        
        assert review.script_id == "script-001"
        assert review.script_title == "Test Script"
        assert review.overall_score == 75
        assert review.category_scores == []
        assert review.improvement_points == []
        assert review.target_audience == ""
        assert review.audience_alignment_score == 0
        assert review.target_length == ContentLength.VARIABLE
        assert review.current_length_seconds is None
        assert review.optimal_length_seconds is None
        assert review.is_youtube_short is False
        assert review.hook_strength_score == 0
        assert review.retention_score == 0
        assert review.viral_potential_score == 0
        assert review.reviewer_id == "AI-ScriptReviewer-001"
        assert review.review_version == 1
        assert review.reviewed_at is not None
        assert review.confidence_score == 85
        assert review.needs_major_revision is False
        assert review.iteration_number == 1
        assert review.previous_review_id is None
        assert review.improvement_trajectory == [75]
        assert review.strengths == []
        assert review.primary_concern == ""
        assert review.quick_wins == []
        assert review.notes == ""
        assert review.metadata == {}
    
    def test_create_youtube_short_review(self):
        """Test creating a review for YouTube short."""
        review = ScriptReview(
            script_id="short-001",
            script_title="Horror Short",
            overall_score=72,
            target_audience="Horror fans 18-35",
            audience_alignment_score=85,
            target_length=ContentLength.YOUTUBE_SHORT_EXTENDED,
            current_length_seconds=145,
            optimal_length_seconds=90,
            is_youtube_short=True,
            hook_strength_score=95,
            retention_score=68,
            viral_potential_score=78,
            needs_major_revision=False
        )
        
        assert review.script_id == "short-001"
        assert review.script_title == "Horror Short"
        assert review.overall_score == 72
        assert review.target_audience == "Horror fans 18-35"
        assert review.audience_alignment_score == 85
        assert review.target_length == ContentLength.YOUTUBE_SHORT_EXTENDED
        assert review.current_length_seconds == 145
        assert review.optimal_length_seconds == 90
        assert review.is_youtube_short is True
        assert review.hook_strength_score == 95
        assert review.retention_score == 68
        assert review.viral_potential_score == 78
        assert review.needs_major_revision is False


class TestCategoryScore:
    """Test CategoryScore functionality."""
    
    def test_create_category_score(self):
        """Test creating CategoryScore."""
        score = CategoryScore(
            category=ReviewCategory.ENGAGEMENT,
            score=85,
            reasoning="Strong hook, weak middle",
            strengths=["Great opening", "Emotional impact"],
            weaknesses=["Mid-section drag", "Predictable"]
        )
        
        assert score.category == ReviewCategory.ENGAGEMENT
        assert score.score == 85
        assert score.reasoning == "Strong hook, weak middle"
        assert len(score.strengths) == 2
        assert len(score.weaknesses) == 2


class TestImprovementPoint:
    """Test ImprovementPoint functionality."""
    
    def test_create_improvement_point(self):
        """Test creating ImprovementPoint."""
        point = ImprovementPoint(
            category=ReviewCategory.PACING,
            title="Reduce middle section",
            description="Cut 30-40 seconds",
            priority="high",
            impact_score=25,
            specific_example="Investigation sequence too long",
            suggested_fix="Focus on 2-3 key moments"
        )
        
        assert point.category == ReviewCategory.PACING
        assert point.title == "Reduce middle section"
        assert point.description == "Cut 30-40 seconds"
        assert point.priority == "high"
        assert point.impact_score == 25
        assert point.specific_example == "Investigation sequence too long"
        assert point.suggested_fix == "Focus on 2-3 key moments"


class TestScriptReviewMethods:
    """Test ScriptReview methods."""
    
    def test_get_category_score(self):
        """Test getting score for specific category."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=75
        )
        
        # Add category scores
        review.category_scores.append(CategoryScore(
            category=ReviewCategory.ENGAGEMENT,
            score=80,
            reasoning="Good"
        ))
        review.category_scores.append(CategoryScore(
            category=ReviewCategory.PACING,
            score=70,
            reasoning="Needs work"
        ))
        
        # Get specific category
        engagement = review.get_category_score(ReviewCategory.ENGAGEMENT)
        assert engagement is not None
        assert engagement.score == 80
        
        pacing = review.get_category_score(ReviewCategory.PACING)
        assert pacing is not None
        assert pacing.score == 70
        
        # Non-existent category
        clarity = review.get_category_score(ReviewCategory.CLARITY)
        assert clarity is None
    
    def test_get_high_priority_improvements(self):
        """Test getting high-priority improvements."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=75
        )
        
        # Add improvements with different priorities
        review.improvement_points.append(ImprovementPoint(
            category=ReviewCategory.PACING,
            title="High priority 1",
            description="Important",
            priority="high",
            impact_score=25
        ))
        review.improvement_points.append(ImprovementPoint(
            category=ReviewCategory.CLARITY,
            title="Medium priority",
            description="Moderate",
            priority="medium",
            impact_score=15
        ))
        review.improvement_points.append(ImprovementPoint(
            category=ReviewCategory.STRUCTURE,
            title="High priority 2",
            description="Critical",
            priority="high",
            impact_score=30
        ))
        review.improvement_points.append(ImprovementPoint(
            category=ReviewCategory.IMPACT,
            title="Low priority",
            description="Nice to have",
            priority="low",
            impact_score=5
        ))
        
        # Get high-priority only
        high_priority = review.get_high_priority_improvements()
        
        assert len(high_priority) == 2
        # Should be sorted by impact score (descending)
        assert high_priority[0].title == "High priority 2"
        assert high_priority[0].impact_score == 30
        assert high_priority[1].title == "High priority 1"
        assert high_priority[1].impact_score == 25
    
    def test_get_youtube_short_readiness(self):
        """Test YouTube short readiness calculation."""
        review = ScriptReview(
            script_id="short-001",
            script_title="Test Short",
            overall_score=75,
            is_youtube_short=True,
            target_length=ContentLength.YOUTUBE_SHORT,
            current_length_seconds=55,
            hook_strength_score=85,
            retention_score=75,
            viral_potential_score=70
        )
        
        readiness = review.get_youtube_short_readiness()
        
        assert "ready" in readiness
        assert "readiness_score" in readiness
        assert "length_compliant" in readiness
        assert "length_feedback" in readiness
        assert readiness["length_compliant"] is True  # 55s <= 60s
        assert readiness["hook_strength"] == 85
        assert readiness["retention_score"] == 75
        assert readiness["viral_potential"] == 70
    
    def test_youtube_short_readiness_not_configured(self):
        """Test readiness when not configured for YouTube shorts."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Regular Script",
            overall_score=75,
            is_youtube_short=False
        )
        
        readiness = review.get_youtube_short_readiness()
        
        assert readiness["ready"] is False
        assert "Not configured" in readiness["reason"]


class TestScriptReviewSerialization:
    """Test serialization and deserialization."""
    
    def test_to_dict(self):
        """Test converting ScriptReview to dictionary."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Test",
            overall_score=75,
            target_length=ContentLength.YOUTUBE_SHORT,
            is_youtube_short=True
        )
        
        # Add category score
        review.category_scores.append(CategoryScore(
            category=ReviewCategory.ENGAGEMENT,
            score=80,
            reasoning="Good"
        ))
        
        # Add improvement point
        review.improvement_points.append(ImprovementPoint(
            category=ReviewCategory.PACING,
            title="Fix pacing",
            description="Improve timing",
            priority="high",
            impact_score=20
        ))
        
        data = review.to_dict()
        
        assert isinstance(data, dict)
        assert data["script_id"] == "script-001"
        assert data["script_title"] == "Test"
        assert data["overall_score"] == 75
        assert data["target_length"] == "youtube_short"  # Enum to string
        assert data["is_youtube_short"] is True
        
        # Check category scores converted
        assert len(data["category_scores"]) == 1
        assert data["category_scores"][0]["category"] == "engagement"
        
        # Check improvement points converted
        assert len(data["improvement_points"]) == 1
        assert data["improvement_points"][0]["category"] == "pacing"
    
    def test_from_dict(self):
        """Test creating ScriptReview from dictionary."""
        data = {
            "script_id": "script-001",
            "script_title": "Test",
            "overall_score": 75,
            "target_length": "youtube_short_extended",
            "is_youtube_short": True,
            "category_scores": [
                {
                    "category": "engagement",
                    "score": 80,
                    "reasoning": "Good",
                    "strengths": ["Hook"],
                    "weaknesses": ["Middle"]
                }
            ],
            "improvement_points": [
                {
                    "category": "pacing",
                    "title": "Fix pacing",
                    "description": "Improve",
                    "priority": "high",
                    "impact_score": 20,
                    "specific_example": "Example",
                    "suggested_fix": "Fix"
                }
            ]
        }
        
        review = ScriptReview.from_dict(data)
        
        assert review.script_id == "script-001"
        assert review.script_title == "Test"
        assert review.overall_score == 75
        assert review.target_length == ContentLength.YOUTUBE_SHORT_EXTENDED
        assert review.is_youtube_short is True
        
        # Check category scores
        assert len(review.category_scores) == 1
        assert review.category_scores[0].category == ReviewCategory.ENGAGEMENT
        assert review.category_scores[0].score == 80
        
        # Check improvement points
        assert len(review.improvement_points) == 1
        assert review.improvement_points[0].category == ReviewCategory.PACING
        assert review.improvement_points[0].impact_score == 20
    
    def test_roundtrip_serialization(self):
        """Test that to_dict -> from_dict preserves data."""
        original = ScriptReview(
            script_id="script-001",
            script_title="Test Script",
            overall_score=80,
            target_audience="Test audience",
            audience_alignment_score=85,
            target_length=ContentLength.YOUTUBE_SHORT,
            current_length_seconds=55,
            optimal_length_seconds=50,
            is_youtube_short=True,
            hook_strength_score=90,
            retention_score=85,
            viral_potential_score=80,
            reviewer_id="AI-Test-001",
            review_version=2,
            confidence_score=90,
            needs_major_revision=False,
            iteration_number=2,
            previous_review_id="review-000",
            improvement_trajectory=[70, 80],
            strengths=["Strong hook"],
            primary_concern="Pacing",
            quick_wins=["Cut intro"],
            notes="Test notes"
        )
        
        # Roundtrip
        data = original.to_dict()
        restored = ScriptReview.from_dict(data)
        
        # Compare fields
        assert restored.script_id == original.script_id
        assert restored.script_title == original.script_title
        assert restored.overall_score == original.overall_score
        assert restored.target_audience == original.target_audience
        assert restored.audience_alignment_score == original.audience_alignment_score
        assert restored.target_length == original.target_length
        assert restored.current_length_seconds == original.current_length_seconds
        assert restored.optimal_length_seconds == original.optimal_length_seconds
        assert restored.is_youtube_short == original.is_youtube_short
        assert restored.hook_strength_score == original.hook_strength_score
        assert restored.retention_score == original.retention_score
        assert restored.viral_potential_score == original.viral_potential_score
        assert restored.reviewer_id == original.reviewer_id
        assert restored.review_version == original.review_version
        assert restored.confidence_score == original.confidence_score
        assert restored.needs_major_revision == original.needs_major_revision
        assert restored.iteration_number == original.iteration_number
        assert restored.previous_review_id == original.previous_review_id
        assert restored.improvement_trajectory == original.improvement_trajectory
        assert restored.strengths == original.strengths
        assert restored.primary_concern == original.primary_concern
        assert restored.quick_wins == original.quick_wins
        assert restored.notes == original.notes


class TestScriptReviewRepresentation:
    """Test string representation."""
    
    def test_repr(self):
        """Test __repr__ method."""
        review = ScriptReview(
            script_id="script-001",
            script_title="Test Script",
            overall_score=75,
            iteration_number=2
        )
        
        review.improvement_points.append(ImprovementPoint(
            category=ReviewCategory.PACING,
            title="Test",
            description="Test",
            priority="high",
            impact_score=20
        ))
        
        repr_str = repr(review)
        
        assert "ScriptReview(" in repr_str
        assert "script='Test Script'" in repr_str
        assert "score=75%" in repr_str
        assert "iteration=2" in repr_str
        assert "improvements=1" in repr_str
