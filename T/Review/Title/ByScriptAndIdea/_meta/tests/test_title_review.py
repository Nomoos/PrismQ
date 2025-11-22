"""Tests for TitleReview model."""

import pytest
from datetime import datetime
from T.Review.Title.ByScriptAndIdea import (
    TitleReview,
    TitleReviewCategory,
    TitleImprovementPoint,
    TitleCategoryScore
)


class TestTitleReviewBasic:
    """Test basic TitleReview functionality."""
    
    def test_create_basic_review(self):
        """Test creating a basic TitleReview instance."""
        review = TitleReview(
            title_id="title-001",
            title_text="The Echo - A Haunting Discovery",
            overall_score=75
        )
        
        assert review.title_id == "title-001"
        assert review.title_text == "The Echo - A Haunting Discovery"
        assert review.title_version == "v1"
        assert review.overall_score == 75
        assert review.category_scores == []
        assert review.improvement_points == []
        assert review.script_id == ""
        assert review.script_alignment_score == 0
        assert review.idea_id == ""
        assert review.idea_alignment_score == 0
        assert review.engagement_score == 0
        assert review.clickthrough_potential == 0
        assert review.seo_score == 0
        assert review.current_length_chars == len("The Echo - A Haunting Discovery")
        assert review.optimal_length_chars == 60
        assert review.reviewer_id == "AI-TitleReviewer-001"
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
    
    def test_create_complete_review(self):
        """Test creating a complete review with all context."""
        review = TitleReview(
            title_id="title-001",
            title_text="The Echo - A Haunting Discovery",
            title_version="v1",
            overall_score=78,
            script_id="script-001",
            script_title="The Echo",
            script_summary="A horror short about mysterious echoes",
            script_version="v1",
            script_alignment_score=85,
            key_script_elements=["echo", "haunting", "discovery", "mystery"],
            idea_id="idea-001",
            idea_summary="Horror story about sounds that repeat",
            idea_intent="Create suspense through auditory elements",
            idea_alignment_score=82,
            target_audience="Horror enthusiasts aged 18-35",
            engagement_score=75,
            clickthrough_potential=72,
            curiosity_score=80,
            expectation_accuracy=76,
            seo_score=68,
            keyword_relevance=70,
            suggested_keywords=["echo", "horror", "haunting"],
            length_score=85
        )
        
        assert review.title_id == "title-001"
        assert review.title_text == "The Echo - A Haunting Discovery"
        assert review.overall_score == 78
        assert review.script_id == "script-001"
        assert review.script_alignment_score == 85
        assert review.idea_id == "idea-001"
        assert review.idea_alignment_score == 82
        assert review.engagement_score == 75
        assert review.clickthrough_potential == 72
        assert review.curiosity_score == 80
        assert review.expectation_accuracy == 76
        assert review.seo_score == 68
        assert len(review.key_script_elements) == 4
        assert "echo" in review.key_script_elements


class TestTitleCategoryScore:
    """Test TitleCategoryScore functionality."""
    
    def test_create_category_score(self):
        """Test creating TitleCategoryScore."""
        score = TitleCategoryScore(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            score=85,
            reasoning="Title accurately reflects script content",
            strengths=["Mentions key element 'echo'", "Indicates genre"],
            weaknesses=["Could be more specific", "Generic subtitle"]
        )
        
        assert score.category == TitleReviewCategory.SCRIPT_ALIGNMENT
        assert score.score == 85
        assert score.reasoning == "Title accurately reflects script content"
        assert len(score.strengths) == 2
        assert len(score.weaknesses) == 2
    
    def test_all_review_categories(self):
        """Test all title review categories exist."""
        categories = [
            TitleReviewCategory.SCRIPT_ALIGNMENT,
            TitleReviewCategory.IDEA_ALIGNMENT,
            TitleReviewCategory.ENGAGEMENT,
            TitleReviewCategory.EXPECTATION_SETTING,
            TitleReviewCategory.CLARITY,
            TitleReviewCategory.SEO_OPTIMIZATION,
            TitleReviewCategory.AUDIENCE_FIT,
            TitleReviewCategory.LENGTH
        ]
        
        assert len(categories) == 8
        for cat in categories:
            assert isinstance(cat, TitleReviewCategory)


class TestTitleImprovementPoint:
    """Test TitleImprovementPoint functionality."""
    
    def test_create_improvement_point(self):
        """Test creating TitleImprovementPoint."""
        improvement = TitleImprovementPoint(
            category=TitleReviewCategory.ENGAGEMENT,
            title="Add emotional hook",
            description="Title lacks emotional engagement element",
            priority="high",
            impact_score=25,
            specific_example="Current: 'The Echo' → Suggested: 'The Echo - A Haunting Discovery'",
            suggested_fix="Add subtitle that hints at emotional journey"
        )
        
        assert improvement.category == TitleReviewCategory.ENGAGEMENT
        assert improvement.title == "Add emotional hook"
        assert improvement.priority == "high"
        assert improvement.impact_score == 25
        assert "emotional" in improvement.description


class TestTitleReviewMethods:
    """Test TitleReview methods."""
    
    def setup_method(self):
        """Set up test review instance."""
        self.review = TitleReview(
            title_id="title-001",
            title_text="The Echo",
            overall_score=70,
            script_alignment_score=75,
            idea_alignment_score=80,
            engagement_score=72,
            clickthrough_potential=68,
            curiosity_score=75,
            expectation_accuracy=70,
            current_length_chars=8,
            optimal_length_chars=60
        )
        
        # Add category scores
        self.review.category_scores.append(TitleCategoryScore(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            score=75,
            reasoning="Good alignment with script",
            strengths=["Clear", "Concise"],
            weaknesses=["Too simple"]
        ))
        
        self.review.category_scores.append(TitleCategoryScore(
            category=TitleReviewCategory.ENGAGEMENT,
            score=65,
            reasoning="Needs more engagement",
            strengths=["Memorable"],
            weaknesses=["Lacks hook", "Not intriguing"]
        ))
        
        # Add improvement points
        self.review.improvement_points.append(TitleImprovementPoint(
            category=TitleReviewCategory.ENGAGEMENT,
            title="Add emotional element",
            description="Include emotional hook",
            priority="high",
            impact_score=25
        ))
        
        self.review.improvement_points.append(TitleImprovementPoint(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            title="Reference key scene",
            description="Mention discovery element",
            priority="high",
            impact_score=20
        ))
        
        self.review.improvement_points.append(TitleImprovementPoint(
            category=TitleReviewCategory.LENGTH,
            title="Expand title length",
            description="Add subtitle for context",
            priority="medium",
            impact_score=15
        ))
    
    def test_get_category_score(self):
        """Test retrieving specific category score."""
        script_score = self.review.get_category_score(TitleReviewCategory.SCRIPT_ALIGNMENT)
        assert script_score is not None
        assert script_score.score == 75
        assert script_score.category == TitleReviewCategory.SCRIPT_ALIGNMENT
        
        # Test non-existent category
        seo_score = self.review.get_category_score(TitleReviewCategory.SEO_OPTIMIZATION)
        assert seo_score is None
    
    def test_get_high_priority_improvements(self):
        """Test getting high-priority improvements."""
        high_priority = self.review.get_high_priority_improvements()
        
        assert len(high_priority) == 2
        # Should be sorted by impact score descending
        assert high_priority[0].impact_score == 25
        assert high_priority[1].impact_score == 20
        assert all(imp.priority == "high" for imp in high_priority)
    
    def test_get_alignment_summary(self):
        """Test alignment summary calculation."""
        summary = self.review.get_alignment_summary()
        
        assert summary["script_alignment"] == 75
        assert summary["idea_alignment"] == 80
        assert summary["average_alignment"] == 77  # (75 + 80) / 2
        assert summary["alignment_status"] == "good"  # >= 70
        assert summary["needs_improvement"] is False  # >= 70
        assert "key_issues" in summary
    
    def test_get_alignment_summary_poor(self):
        """Test alignment summary with poor scores."""
        review = TitleReview(
            title_id="title-002",
            title_text="Test Title",
            script_alignment_score=55,
            idea_alignment_score=50
        )
        
        summary = review.get_alignment_summary()
        assert summary["average_alignment"] == 52  # (55 + 50) / 2
        assert summary["alignment_status"] == "poor"  # < 60
        assert summary["needs_improvement"] is True  # < 70
    
    def test_get_engagement_summary(self):
        """Test engagement summary calculation."""
        summary = self.review.get_engagement_summary()
        
        assert "composite_score" in summary
        assert summary["engagement"] == 72
        assert summary["clickthrough_potential"] == 68
        assert summary["curiosity"] == 75
        assert summary["expectation_accuracy"] == 70
        assert "ready_for_publication" in summary
        assert "recommendations" in summary
        assert len(summary["recommendations"]) <= 3
    
    def test_get_length_assessment(self):
        """Test length assessment."""
        assessment = self.review.get_length_assessment()
        
        assert assessment["current_length"] == 8
        assert assessment["optimal_length"] == 60
        assert assessment["difference"] == -52  # 8 - 60
        assert assessment["status"] == "too_short"
        assert "too short" in assessment["feedback"]
    
    def test_get_length_assessment_optimal(self):
        """Test length assessment with optimal length."""
        review = TitleReview(
            title_id="title-003",
            title_text="A" * 60,  # Exactly 60 characters
            current_length_chars=60,
            optimal_length_chars=60,
            length_score=100
        )
        
        assessment = review.get_length_assessment()
        assert assessment["status"] == "optimal"
        assert "appropriate" in assessment["feedback"]
    
    def test_is_ready_for_improvement(self):
        """Test readiness check for improvement stage."""
        assert self.review.is_ready_for_improvement() is True
        
        # Test with incomplete review
        incomplete_review = TitleReview(
            title_id="title-004",
            title_text="Test"
        )
        assert incomplete_review.is_ready_for_improvement() is False


class TestTitleReviewSerialization:
    """Test TitleReview serialization."""
    
    def test_to_dict(self):
        """Test converting review to dictionary."""
        review = TitleReview(
            title_id="title-001",
            title_text="The Echo",
            overall_score=75,
            script_alignment_score=80,
            idea_alignment_score=85
        )
        
        review.category_scores.append(TitleCategoryScore(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            score=80,
            reasoning="Good alignment"
        ))
        
        review.improvement_points.append(TitleImprovementPoint(
            category=TitleReviewCategory.ENGAGEMENT,
            title="Improve engagement",
            description="Add hook",
            priority="high",
            impact_score=20
        ))
        
        data = review.to_dict()
        
        assert isinstance(data, dict)
        assert data["title_id"] == "title-001"
        assert data["title_text"] == "The Echo"
        assert data["overall_score"] == 75
        assert len(data["category_scores"]) == 1
        assert data["category_scores"][0]["category"] == "script_alignment"
        assert len(data["improvement_points"]) == 1
        assert data["improvement_points"][0]["category"] == "engagement"
    
    def test_from_dict(self):
        """Test creating review from dictionary."""
        data = {
            "title_id": "title-001",
            "title_text": "The Echo",
            "title_version": "v1",
            "overall_score": 75,
            "script_id": "script-001",
            "script_alignment_score": 80,
            "idea_id": "idea-001",
            "idea_alignment_score": 85,
            "category_scores": [
                {
                    "category": "script_alignment",
                    "score": 80,
                    "reasoning": "Good alignment",
                    "strengths": ["Clear"],
                    "weaknesses": ["Simple"]
                }
            ],
            "improvement_points": [
                {
                    "category": "engagement",
                    "title": "Add hook",
                    "description": "Include emotional element",
                    "priority": "high",
                    "impact_score": 20,
                    "specific_example": "",
                    "suggested_fix": ""
                }
            ]
        }
        
        review = TitleReview.from_dict(data)
        
        assert review.title_id == "title-001"
        assert review.title_text == "The Echo"
        assert review.overall_score == 75
        assert len(review.category_scores) == 1
        assert review.category_scores[0].category == TitleReviewCategory.SCRIPT_ALIGNMENT
        assert len(review.improvement_points) == 1
        assert review.improvement_points[0].category == TitleReviewCategory.ENGAGEMENT
    
    def test_round_trip_serialization(self):
        """Test that to_dict -> from_dict preserves data."""
        original = TitleReview(
            title_id="title-001",
            title_text="The Echo - A Haunting Discovery",
            overall_score=78,
            script_id="script-001",
            script_alignment_score=85,
            idea_id="idea-001",
            idea_alignment_score=82
        )
        
        original.category_scores.append(TitleCategoryScore(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            score=85,
            reasoning="Strong alignment",
            strengths=["Accurate", "Clear"],
            weaknesses=["Generic"]
        ))
        
        data = original.to_dict()
        restored = TitleReview.from_dict(data)
        
        assert restored.title_id == original.title_id
        assert restored.title_text == original.title_text
        assert restored.overall_score == original.overall_score
        assert len(restored.category_scores) == len(original.category_scores)


class TestTitleReviewRepr:
    """Test TitleReview string representation."""
    
    def test_repr(self):
        """Test __repr__ method."""
        review = TitleReview(
            title_id="title-001",
            title_text="The Echo",
            overall_score=78,
            iteration_number=2,
            script_alignment_score=85,
            idea_alignment_score=82
        )
        
        repr_str = repr(review)
        assert "TitleReview" in repr_str
        assert "The Echo" in repr_str
        assert "78%" in repr_str
        assert "iteration=2" in repr_str
        assert "script_align=85%" in repr_str
        assert "idea_align=82%" in repr_str


class TestTitleReviewEdgeCases:
    """Test edge cases and validation."""
    
    def test_empty_title_text(self):
        """Test review with empty title text."""
        review = TitleReview(
            title_id="title-001",
            title_text=""
        )
        assert review.current_length_chars == 0
    
    def test_very_long_title(self):
        """Test review with very long title."""
        long_title = "A" * 200
        review = TitleReview(
            title_id="title-001",
            title_text=long_title
        )
        assert review.current_length_chars == 200
        
        assessment = review.get_length_assessment()
        assert assessment["status"] == "too_long"
    
    def test_multiple_iterations(self):
        """Test improvement trajectory tracking."""
        review = TitleReview(
            title_id="title-001",
            title_text="Test Title",
            overall_score=60
        )
        
        assert review.improvement_trajectory == [60]
        assert review.iteration_number == 1
    
    def test_confidence_score_ranges(self):
        """Test confidence scores within valid range."""
        review = TitleReview(
            title_id="title-001",
            title_text="Test",
            confidence_score=100
        )
        assert 0 <= review.confidence_score <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
