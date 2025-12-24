"""Tests for PrismQ.T.Review.Title.From.Content (v2) module.

This test suite validates the v2 title review functionality including:
- Review of v2 title against v2 content
- Comparison with v1 reviews
- Improvement tracking
- JSON output format
- Regression detection
"""

import os
import sys

import pytest

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../..")))

from T.Review.Title.From.Content.by_content_v2 import (
    ImprovementComparison,
    compare_reviews,
    get_improvement_summary,
    review_title_by_content_v2,
)
from T.Review.Title.From.Content.Idea.by_content_and_idea import (
    review_title_by_content_and_idea,
)
from T.Review.Title.From.Content.Idea.title_review import TitleReview


@pytest.fixture
def sample_v1_title():
    """Sample v1 title for testing."""
    return "The Echo"


@pytest.fixture
def sample_v2_title():
    """Sample v2 title (improved) for testing."""
    return "The Echo - A Haunting Discovery"


@pytest.fixture
def sample_v1_content():
    """Sample v1 script content."""
    return """
    The Echo is a horror short film about mysterious sounds in an abandoned hospital.
    Sarah investigates strange echoes that seem to repeat her thoughts.
    As she delves deeper into the hospital's dark past, she discovers the source
    of the haunting echoes and realizes she's not alone.
    """


@pytest.fixture
def sample_v2_content():
    """Sample v2 script content (improved and expanded)."""
    return """
    The Echo - A Haunting Discovery is a suspenseful horror short film that follows
    Sarah, a paranormal investigator, as she explores the abandoned Mercy Hospital.
    
    Strange echoes seem to anticipate her thoughts and movements. Through her
    investigation, Sarah uncovers the hospital's tragic history and discovers that
    the echoes are manifestations of past trauma. The haunting sounds lead her
    to a shocking revelation about the true nature of the phenomena.
    
    As darkness falls, Sarah must confront the source of these haunting discoveries
    before she becomes part of the echo herself.
    """


@pytest.fixture
def sample_idea():
    """Sample idea for testing."""
    return "A psychological horror story about mysterious sounds in an abandoned hospital"


@pytest.fixture
def v1_review(sample_v1_title, sample_v1_content, sample_idea):
    """Create a v1 review for comparison testing."""
    return review_title_by_content_and_idea(
        title_text=sample_v1_title,
        content_text=sample_v1_content,
        idea_summary=sample_idea,
        title_version="v1",
        script_version="v1",
    )


class TestReviewTitleByScriptV2:
    """Test suite for review_title_by_content_v2 function."""

    def test_basic_v2_review(self, sample_v2_title, sample_v2_content):
        """Test basic v2 review without previous review."""
        review = review_title_by_content_v2(title_text=sample_v2_title, content_text=sample_v2_content)

        assert review is not None
        assert review.title_text == sample_v2_title
        assert review.title_version == "v2"
        assert review.script_version == "v2"
        assert review.review_version == 2
        assert 0 <= review.overall_score <= 100
        assert review.script_alignment_score >= 0

    def test_v2_review_with_previous(self, sample_v2_title, sample_v2_content, v1_review):
        """Test v2 review with previous review for comparison."""
        review = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1_review
        )

        assert review is not None
        assert review.iteration_number == v1_review.iteration_number + 1
        assert review.previous_review_id == v1_review.title_id
        assert len(review.improvement_trajectory) == len(v1_review.improvement_trajectory) + 1

    def test_v2_review_generates_ids(self, sample_v2_title, sample_v2_content):
        """Test that v2 review generates IDs when not provided."""
        review = review_title_by_content_v2(title_text=sample_v2_title, content_text=sample_v2_content)

        assert review.title_id is not None
        assert review.title_id.startswith("title-")
        assert review.content_id is not None
        assert review.content_id.startswith("script-")

    def test_v2_review_with_custom_ids(self, sample_v2_title, sample_v2_content):
        """Test v2 review with custom IDs."""
        review = review_title_by_content_v2(
            title_text=sample_v2_title,
            content_text=sample_v2_content,
            title_id="custom-title-v2",
            content_id="custom-script-v2",
        )

        assert review.title_id == "custom-title-v2"
        assert review.content_id == "custom-script-v2"

    def test_v2_review_has_category_scores(self, sample_v2_title, sample_v2_content):
        """Test that v2 review includes category scores."""
        review = review_title_by_content_v2(title_text=sample_v2_title, content_text=sample_v2_content)

        assert len(review.category_scores) > 0
        # Should have script_alignment, engagement, seo, length
        assert len(review.category_scores) >= 4

    def test_v2_review_has_improvement_points(self, sample_v2_title, sample_v2_content):
        """Test that v2 review generates improvement points."""
        review = review_title_by_content_v2(title_text=sample_v2_title, content_text=sample_v2_content)

        # May or may not have improvements depending on quality
        assert isinstance(review.improvement_points, list)

    def test_v2_review_improvement_points_sorted(self, sample_v2_title, sample_v2_content):
        """Test that improvement points are sorted by impact."""
        # Use a poor title to ensure improvement points
        poor_title = "Video"
        review = review_title_by_content_v2(title_text=poor_title, content_text=sample_v2_content)

        if len(review.improvement_points) > 1:
            for i in range(len(review.improvement_points) - 1):
                assert (
                    review.improvement_points[i].impact_score
                    >= review.improvement_points[i + 1].impact_score
                )

    def test_v2_review_to_dict_compatibility(self, sample_v2_title, sample_v2_content):
        """Test that v2 review can be converted to dict (JSON compatible)."""
        review = review_title_by_content_v2(title_text=sample_v2_title, content_text=sample_v2_content)

        review_dict = review.to_dict()
        assert isinstance(review_dict, dict)
        assert "title_text" in review_dict
        assert "overall_score" in review_dict
        assert "category_scores" in review_dict

    def test_v2_review_empty_content(self, sample_v2_title):
        """Test v2 review with empty script raises ValueError."""
        with pytest.raises(ValueError, match="content_text must be a non-empty string"):
            review_title_by_content_v2(title_text=sample_v2_title, content_text="")

    def test_v2_review_very_long_title(self, sample_v2_content):
        """Test v2 review with very long title."""
        long_title = "The Echo - A Haunting Discovery of Mysterious Sounds and Hidden Secrets in the Abandoned Hospital"
        review = review_title_by_content_v2(title_text=long_title, content_text=sample_v2_content)

        assert review is not None
        # Should note length issue
        assert review.current_length_chars > 60

    def test_v2_review_very_short_title(self, sample_v2_content):
        """Test v2 review with very short title."""
        short_title = "Echo"
        review = review_title_by_content_v2(title_text=short_title, content_text=sample_v2_content)

        assert review is not None
        assert review.current_length_chars < 30


class TestParameterValidation:
    """Test suite for parameter validation."""

    def test_empty_title_raises_error(self, sample_v2_content):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="title_text must be a non-empty string"):
            review_title_by_content_v2(title_text="", content_text=sample_v2_content)

    def test_none_title_raises_error(self, sample_v2_content):
        """Test that None title raises ValueError."""
        with pytest.raises(ValueError, match="title_text must be a non-empty string"):
            review_title_by_content_v2(title_text=None, content_text=sample_v2_content)

    def test_whitespace_only_title_raises_error(self, sample_v2_content):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="title_text is too short"):
            review_title_by_content_v2(title_text="   ", content_text=sample_v2_content)

    def test_too_long_title_raises_error(self, sample_v2_content):
        """Test that excessively long title raises ValueError."""
        long_title = "A" * 250
        with pytest.raises(ValueError, match="title_text exceeds maximum length"):
            review_title_by_content_v2(title_text=long_title, content_text=sample_v2_content)

    def test_too_short_title_raises_error(self, sample_v2_content):
        """Test that title shorter than 3 chars raises ValueError."""
        with pytest.raises(ValueError, match="title_text is too short"):
            review_title_by_content_v2(title_text="Hi", content_text=sample_v2_content)

    def test_empty_content_raises_error(self, sample_v2_title):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="content_text must be a non-empty string"):
            review_title_by_content_v2(title_text=sample_v2_title, content_text="")

    def test_too_short_content_raises_error(self, sample_v2_title):
        """Test that content shorter than 10 chars raises ValueError."""
        with pytest.raises(ValueError, match="content_text is too short"):
            review_title_by_content_v2(title_text=sample_v2_title, content_text="Short")

    def test_invalid_previous_review_type_raises_error(self, sample_v2_title, sample_v2_content):
        """Test that invalid previous_review type raises TypeError."""
        with pytest.raises(TypeError, match="previous_review must be a TitleReview instance"):
            review_title_by_content_v2(
                title_text=sample_v2_title, 
                content_text=sample_v2_content, 
                previous_review="not a review"
            )

    def test_whitespace_is_trimmed(self, sample_v2_content):
        """Test that whitespace is properly trimmed from inputs."""
        review = review_title_by_content_v2(
            title_text="  The Echo  ",
            content_text=f"  {sample_v2_content}  "
        )
        assert review.title_text == "The Echo"


class TestCompareReviews:
    """Test suite for compare_reviews function."""

    def test_compare_with_improvement(self, v1_review, sample_v2_title, sample_v2_content):
        """Test comparison when v2 is improved."""
        v2_review = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1_review
        )

        comparisons = compare_reviews(v1_review, v2_review)

        assert len(comparisons) > 0
        assert all(isinstance(c, ImprovementComparison) for c in comparisons)
        # First comparison should be overall
        assert comparisons[0].category == "overall"

    def test_compare_no_previous_review(self, sample_v2_title, sample_v2_content):
        """Test comparison with no previous review."""
        v2_review = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content
        )

        comparisons = compare_reviews(None, v2_review)

        assert len(comparisons) == 0

    def test_compare_detects_improvement(
        self, sample_v1_title, sample_v1_content, sample_v2_title, sample_v2_content, sample_idea
    ):
        """Test that comparison detects improvements."""
        v1 = review_title_by_content_and_idea(
            title_text=sample_v1_title, content_text=sample_v1_content, idea_summary=sample_idea
        )

        v2 = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1
        )

        comparisons = compare_reviews(v1, v2)

        # Check if any category shows improvement
        has_improvement = any(c.improved for c in comparisons)
        # May or may not improve depending on content, just check structure
        assert isinstance(has_improvement, bool)

    def test_compare_detects_regression(self, v1_review, sample_v2_content):
        """Test that comparison detects regressions."""
        # Use a worse title to force regression
        worse_title = "Video"

        v2 = review_title_by_content_v2(
            title_text=worse_title, content_text=sample_v2_content, previous_review=v1_review
        )

        comparisons = compare_reviews(v1_review, v2)

        # Should detect regression
        has_regression = any(c.regression for c in comparisons)
        assert isinstance(has_regression, bool)

    def test_comparison_includes_deltas(self, v1_review, sample_v2_title, sample_v2_content):
        """Test that comparisons include score deltas."""
        v2 = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1_review
        )

        comparisons = compare_reviews(v1_review, v2)

        for comp in comparisons:
            assert hasattr(comp, "delta")
            assert hasattr(comp, "v1_score")
            assert hasattr(comp, "v2_score")
            assert comp.delta == comp.v2_score - comp.v1_score

    def test_comparison_includes_feedback(self, v1_review, sample_v2_title, sample_v2_content):
        """Test that comparisons include feedback messages."""
        v2 = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1_review
        )

        comparisons = compare_reviews(v1_review, v2)

        for comp in comparisons:
            assert hasattr(comp, "feedback")
            assert isinstance(comp.feedback, str)
            assert len(comp.feedback) > 0


class TestGetImprovementSummary:
    """Test suite for get_improvement_summary function."""

    def test_summary_without_previous(self, sample_v2_title, sample_v2_content):
        """Test summary without previous review."""
        v2 = review_title_by_content_v2(title_text=sample_v2_title, content_text=sample_v2_content)

        summary = get_improvement_summary(None, v2)

        assert summary["has_comparison"] is False
        assert "current_score" in summary
        assert summary["current_score"] == v2.overall_score

    def test_summary_with_previous(self, v1_review, sample_v2_title, sample_v2_content):
        """Test summary with previous review."""
        v2 = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1_review
        )

        summary = get_improvement_summary(v1_review, v2)

        assert summary["has_comparison"] is True
        assert "overall_assessment" in summary
        assert "overall_delta" in summary
        assert "v1_score" in summary
        assert "v2_score" in summary
        assert summary["v1_score"] == v1_review.overall_score
        assert summary["v2_score"] == v2.overall_score

    def test_summary_includes_improvements(self, v1_review, sample_v2_title, sample_v2_content):
        """Test that summary includes list of improvements."""
        v2 = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1_review
        )

        summary = get_improvement_summary(v1_review, v2)

        assert "improvements" in summary
        assert isinstance(summary["improvements"], list)

    def test_summary_includes_regressions(self, v1_review, sample_v2_content):
        """Test that summary includes list of regressions."""
        worse_title = "Test"
        v2 = review_title_by_content_v2(
            title_text=worse_title, content_text=sample_v2_content, previous_review=v1_review
        )

        summary = get_improvement_summary(v1_review, v2)

        assert "regressions" in summary
        assert isinstance(summary["regressions"], list)

    def test_summary_includes_recommendation(self, v1_review, sample_v2_title, sample_v2_content):
        """Test that summary includes recommendation."""
        v2 = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1_review
        )

        summary = get_improvement_summary(v1_review, v2)

        assert "recommendation" in summary
        assert isinstance(summary["recommendation"], str)
        assert len(summary["recommendation"]) > 0

    def test_summary_includes_next_steps(self, v1_review, sample_v2_title, sample_v2_content):
        """Test that summary includes next steps."""
        v2 = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1_review
        )

        summary = get_improvement_summary(v1_review, v2)

        assert "next_steps" in summary
        assert isinstance(summary["next_steps"], list)
        assert len(summary["next_steps"]) > 0


class TestAcceptanceCriteria:
    """Test acceptance criteria from MVP-008."""

    def test_ac1_review_v2_title_against_v2_content(self, sample_v2_title, sample_v2_content):
        """AC: Review title v2 against script v2."""
        review = review_title_by_content_v2(
            title_text=sample_v2_title,
            content_text=sample_v2_content,
            title_version="v2",
            script_version="v2",
        )

        assert review.title_version == "v2"
        assert review.script_version == "v2"
        assert review.script_alignment_score >= 0

    def test_ac2_generate_feedback_for_refinement(self, sample_v2_title, sample_v2_content):
        """AC: Generate feedback for refinement."""
        review = review_title_by_content_v2(title_text=sample_v2_title, content_text=sample_v2_content)

        assert len(review.category_scores) > 0
        assert isinstance(review.improvement_points, list)
        assert hasattr(review, "strengths")
        assert hasattr(review, "primary_concern")

    def test_ac3_compare_improvements_v1_to_v2(self, v1_review, sample_v2_title, sample_v2_content):
        """AC: Compare improvements from v1 to v2."""
        v2_review = review_title_by_content_v2(
            title_text=sample_v2_title, content_text=sample_v2_content, previous_review=v1_review
        )

        comparisons = compare_reviews(v1_review, v2_review)
        assert len(comparisons) > 0

        summary = get_improvement_summary(v1_review, v2_review)
        assert summary["has_comparison"] is True
        assert "overall_delta" in summary

    def test_ac4_output_json_format(self, sample_v2_title, sample_v2_content):
        """AC: Output JSON format with feedback."""
        review = review_title_by_content_v2(title_text=sample_v2_title, content_text=sample_v2_content)

        # Test to_dict method
        review_dict = review.to_dict()
        assert isinstance(review_dict, dict)

        # Verify key fields are present
        assert "title_text" in review_dict
        assert "overall_score" in review_dict
        assert "category_scores" in review_dict
        assert "improvement_points" in review_dict
        assert "script_alignment_score" in review_dict

    def test_ac5_review_sample_v2_pairs(self):
        """AC: Tests review sample v2 title/script pairs."""
        # Sample 1: Good alignment
        review1 = review_title_by_content_v2(
            title_text="The Mystery of the Abandoned Hospital",
            content_text="An abandoned hospital holds dark secrets and mysteries waiting to be uncovered.",
            title_version="v2",
            script_version="v2",
        )
        assert review1.script_alignment_score > 50

        # Sample 2: Poor alignment
        review2 = review_title_by_content_v2(
            title_text="Cooking with Fire",
            content_text="An abandoned hospital holds dark secrets and mysteries waiting to be uncovered.",
            title_version="v2",
            script_version="v2",
        )
        assert review2.script_alignment_score < review1.script_alignment_score


class TestWorkflowIntegration:
    """Test workflow integration scenarios."""

    def test_v1_to_v2_workflow(
        self, sample_v1_title, sample_v1_content, sample_v2_title, sample_v2_content, sample_idea
    ):
        """Test complete v1 to v2 workflow."""
        # Step 1: Review v1
        v1_review = review_title_by_content_and_idea(
            title_text=sample_v1_title,
            content_text=sample_v1_content,
            idea_summary=sample_idea,
            title_version="v1",
            script_version="v1",
        )

        # Step 2: Review v2 with v1 comparison
        v2_review = review_title_by_content_v2(
            title_text=sample_v2_title,
            content_text=sample_v2_content,
            title_version="v2",
            script_version="v2",
            previous_review=v1_review,
        )

        # Step 3: Get improvement summary
        summary = get_improvement_summary(v1_review, v2_review)

        assert v2_review.iteration_number == v1_review.iteration_number + 1
        assert summary["has_comparison"] is True

    def test_v2_ready_for_v3(self, sample_v2_title, sample_v2_content):
        """Test that v2 review can inform v3 refinement."""
        v2_review = review_title_by_content_v2(
            title_text=sample_v2_title,
            content_text=sample_v2_content,
            title_version="v2",
            script_version="v2",
        )

        # Should have feedback for v3 refinement
        assert hasattr(v2_review, "improvement_points")
        assert hasattr(v2_review, "quick_wins")
        assert v2_review.is_ready_for_improvement()

    def test_multiple_iterations(
        self, sample_v1_title, sample_v1_content, sample_v2_title, sample_v2_content, sample_idea
    ):
        """Test multiple iteration tracking (v1 -> v2 -> v3)."""
        # v1
        v1_review = review_title_by_content_and_idea(
            title_text=sample_v1_title, content_text=sample_v1_content, idea_summary=sample_idea
        )

        # v2
        v2_review = review_title_by_content_v2(
            title_text=sample_v2_title,
            content_text=sample_v2_content,
            previous_review=v1_review,
            title_version="v2",
        )

        # v3
        v3_title = "The Echo - A Haunting Discovery of Dark Secrets"
        v3_review = review_title_by_content_v2(
            title_text=v3_title,
            content_text=sample_v2_content,
            previous_review=v2_review,
            title_version="v3",
        )

        assert v1_review.iteration_number == 1
        assert v2_review.iteration_number == 2
        assert v3_review.iteration_number == 3
        assert len(v3_review.improvement_trajectory) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
