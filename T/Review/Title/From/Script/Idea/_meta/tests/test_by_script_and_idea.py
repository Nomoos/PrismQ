"""Tests for title review function - review_title_by_script_and_idea."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest

from T.Review.Title.ByScriptAndIdea import (
    AlignmentAnalysis,
    TitleReview,
    TitleReviewCategory,
    review_title_by_script_and_idea,
)
from T.Review.Title.ByScriptAndIdea.by_script_and_idea import (
    analyze_engagement,
    analyze_seo,
    analyze_title_idea_alignment,
    analyze_title_script_alignment,
    extract_keywords,
    generate_improvement_points,
)


class TestExtractKeywords:
    """Test keyword extraction functionality."""

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        text = "The haunting echo in the abandoned house revealed dark secrets"
        keywords = extract_keywords(text, max_keywords=5)

        assert len(keywords) <= 5
        assert isinstance(keywords, list)
        assert "haunting" in keywords or "echo" in keywords

    def test_extract_keywords_filters_stopwords(self):
        """Test that stopwords are filtered."""
        text = "the and or but in on at"
        keywords = extract_keywords(text)

        assert len(keywords) == 0  # All stopwords

    def test_extract_keywords_empty_text(self):
        """Test with empty text."""
        keywords = extract_keywords("")
        assert keywords == []

    def test_extract_keywords_frequency_sorting(self):
        """Test that keywords are sorted by frequency."""
        text = "echo echo echo sound sound mystery"
        keywords = extract_keywords(text, max_keywords=3)

        assert keywords[0] == "echo"  # Most frequent
        assert "sound" in keywords


class TestAnalyzeTitleScriptAlignment:
    """Test title-script alignment analysis."""

    def test_high_alignment(self):
        """Test title with high script alignment."""
        title = "The Haunting Echo"
        script = """
        In the abandoned house, an echo haunts every room.
        The haunting sound reveals dark secrets of the past.
        Every echo brings them closer to the truth.
        """

        analysis = analyze_title_script_alignment(title, script)

        assert isinstance(analysis, AlignmentAnalysis)
        assert analysis.score >= 50  # Good alignment with 100% keyword match
        assert "haunting" in analysis.matches or "echo" in analysis.matches
        assert len(analysis.key_elements) > 0

    def test_low_alignment(self):
        """Test title with low script alignment."""
        title = "Space Adventure Mission"
        script = """
        In the abandoned house, an echo haunts every room.
        The haunting sound reveals dark secrets of the past.
        """

        analysis = analyze_title_script_alignment(title, script)

        assert analysis.score < 50
        assert len(analysis.mismatches) > 0

    def test_with_script_summary(self):
        """Test alignment analysis with script summary."""
        title = "The Echo"
        script = "A long script about many things that happen in various places."
        summary = "Story about mysterious echoes in a house"

        analysis = analyze_title_script_alignment(title, script, summary)

        # Should get bonus for appearing in summary
        assert analysis.score > 0

    def test_empty_title(self):
        """Test with empty title."""
        analysis = analyze_title_script_alignment("", "some script text")
        assert analysis.score == 0


class TestAnalyzeTitleIdeaAlignment:
    """Test title-idea alignment analysis."""

    def test_high_alignment(self):
        """Test title with high idea alignment."""
        title = "The Haunting Echo"
        idea_summary = "Horror story about mysterious echoes that haunt"
        idea_intent = "Create suspense through auditory elements"

        analysis = analyze_title_idea_alignment(title, idea_summary, idea_intent)

        assert isinstance(analysis, AlignmentAnalysis)
        assert analysis.score >= 30  # Reasonable alignment with partial matches
        assert len(analysis.matches) > 0

    def test_intent_bonus(self):
        """Test that intent matching provides bonus."""
        title = "The Echo Mystery"
        idea_summary = "Story about something"
        idea_intent = "Create mystery using echo as central element"

        analysis = analyze_title_idea_alignment(title, idea_summary, idea_intent)

        # Should get bonus for matching intent keywords
        assert analysis.score >= 20  # Has intent bonus even with low base score

    def test_no_intent(self):
        """Test without intent provided."""
        title = "The Echo"
        idea_summary = "Story about echoes"

        analysis = analyze_title_idea_alignment(title, idea_summary, None)

        assert analysis.score > 0


class TestAnalyzeEngagement:
    """Test engagement analysis."""

    def test_high_engagement_title(self):
        """Test title with high engagement potential."""
        title = "The Shocking Mystery: What Haunts the House?"

        result = analyze_engagement(title)

        assert result["engagement_score"] > 50
        assert result["curiosity_score"] > 50
        assert result["has_question"] is True

    def test_low_engagement_title(self):
        """Test simple title with lower engagement."""
        title = "A House"

        result = analyze_engagement(title)

        assert result["engagement_score"] >= 0
        assert result["has_question"] is False

    def test_number_in_title(self):
        """Test title with number."""
        title = "5 Secrets of the House"

        result = analyze_engagement(title)

        assert result["has_number"] is True
        assert result["clickthrough_potential"] > 50

    def test_misleading_words(self):
        """Test that misleading words reduce expectation accuracy."""
        title = "The Ultimate Best Perfect House"

        result = analyze_engagement(title)

        assert result["expectation_accuracy"] < 85


class TestAnalyzeSeo:
    """Test SEO analysis."""

    def test_seo_with_keywords(self):
        """Test SEO analysis with good keywords."""
        title = "How to Find the Echo: A Mystery Guide"
        script_keywords = ["echo", "mystery", "find", "guide", "house"]

        result = analyze_seo(title, script_keywords)

        assert result["seo_score"] > 0
        assert result["keyword_relevance"] > 0

    def test_optimal_length(self):
        """Test title with optimal length."""
        title = "A" * 60  # 60 characters - optimal range
        script_keywords = []

        result = analyze_seo(title, script_keywords)

        assert result["length_score"] == 100

    def test_suggested_keywords(self):
        """Test that suggested keywords are provided."""
        title = "The House"
        script_keywords = ["mystery", "echo", "haunting", "secret"]

        result = analyze_seo(title, script_keywords)

        assert "suggested_keywords" in result
        assert len(result["suggested_keywords"]) >= 0


class TestGenerateImprovementPoints:
    """Test improvement point generation."""

    def test_low_script_alignment_improvement(self):
        """Test improvement for low script alignment."""
        script_alignment = AlignmentAnalysis(
            score=60,
            matches=["echo"],
            mismatches=["mystery", "ghost"],
            key_elements=["house", "sound", "darkness"],
            reasoning="Weak alignment",
        )
        idea_alignment = AlignmentAnalysis(
            score=80, matches=["echo"], mismatches=[], key_elements=["echo"], reasoning="Good"
        )
        engagement_data = {
            "engagement_score": 70,
            "curiosity_score": 70,
            "clickthrough_potential": 70,
            "expectation_accuracy": 70,
            "has_question": False,
            "has_number": False,
            "engagement_words": 1,
        }
        seo_data = {
            "seo_score": 70,
            "keyword_relevance": 70,
            "length_score": 85,
            "suggested_keywords": ["house"],
        }

        improvements = generate_improvement_points(
            "The Echo Mystery Ghost", script_alignment, idea_alignment, engagement_data, seo_data
        )

        assert len(improvements) > 0
        # Should have script alignment improvement
        assert any(imp.category == TitleReviewCategory.SCRIPT_ALIGNMENT for imp in improvements)

    def test_low_engagement_improvement(self):
        """Test improvement for low engagement."""
        script_alignment = AlignmentAnalysis(
            score=80, matches=[], mismatches=[], key_elements=[], reasoning=""
        )
        idea_alignment = AlignmentAnalysis(
            score=80, matches=[], mismatches=[], key_elements=[], reasoning=""
        )
        engagement_data = {
            "engagement_score": 50,  # Low
            "curiosity_score": 50,
            "clickthrough_potential": 50,
            "expectation_accuracy": 70,
            "has_question": False,
            "has_number": False,
            "engagement_words": 0,
        }
        seo_data = {
            "seo_score": 80,
            "keyword_relevance": 80,
            "length_score": 85,
            "suggested_keywords": [],
        }

        improvements = generate_improvement_points(
            "Title", script_alignment, idea_alignment, engagement_data, seo_data
        )

        assert any(imp.category == TitleReviewCategory.ENGAGEMENT for imp in improvements)

    def test_sorted_by_impact(self):
        """Test that improvements are sorted by impact score."""
        script_alignment = AlignmentAnalysis(
            score=60, matches=[], mismatches=["test"], key_elements=["key"], reasoning=""
        )
        idea_alignment = AlignmentAnalysis(
            score=60, matches=[], mismatches=[], key_elements=[], reasoning=""
        )
        engagement_data = {
            "engagement_score": 50,
            "curiosity_score": 50,
            "clickthrough_potential": 50,
            "expectation_accuracy": 70,
            "has_question": False,
            "has_number": False,
            "engagement_words": 0,
        }
        seo_data = {
            "seo_score": 60,
            "keyword_relevance": 60,
            "length_score": 85,
            "suggested_keywords": ["test"],
        }

        improvements = generate_improvement_points(
            "Title", script_alignment, idea_alignment, engagement_data, seo_data
        )

        # Check that impact scores are descending
        for i in range(len(improvements) - 1):
            assert improvements[i].impact_score >= improvements[i + 1].impact_score


class TestReviewTitleByScriptAndIdea:
    """Test the main review function."""

    def test_basic_review(self):
        """Test basic title review."""
        title = "The Haunting Echo"
        script = """
        In the old abandoned house, strange echoes fill the air.
        Every sound seems to repeat, haunting the visitors.
        What secrets do these echoes hold?
        """
        idea = "Horror story about mysterious echoes in a haunted house"

        review = review_title_by_script_and_idea(
            title_text=title, script_text=script, idea_summary=idea
        )

        assert isinstance(review, TitleReview)
        assert review.title_text == title
        assert review.overall_score >= 0
        assert review.overall_score <= 100
        assert review.script_alignment_score >= 0
        assert review.idea_alignment_score >= 0
        assert len(review.category_scores) > 0
        assert len(review.improvement_points) >= 0

    def test_review_with_all_parameters(self):
        """Test review with all optional parameters."""
        review = review_title_by_script_and_idea(
            title_text="The Echo Mystery",
            script_text="A story about echoes and mysteries in a house",
            idea_summary="Mystery story with echoes",
            title_id="title-001",
            script_id="script-001",
            idea_id="idea-001",
            script_summary="Echoes reveal mysteries",
            idea_intent="Create suspense through sound",
            target_audience="Mystery enthusiasts",
            title_version="v1",
            script_version="v1",
        )

        assert review.title_id == "title-001"
        assert review.script_id == "script-001"
        assert review.idea_id == "idea-001"
        assert review.title_version == "v1"
        assert review.script_version == "v1"
        assert review.target_audience == "Mystery enthusiasts"

    def test_review_generates_ids(self):
        """Test that review generates IDs if not provided."""
        review = review_title_by_script_and_idea(
            title_text="Title", script_text="Script", idea_summary="Idea"
        )

        assert review.title_id is not None
        assert review.script_id is not None
        assert review.idea_id is not None
        assert review.title_id.startswith("title-")

    def test_high_quality_title(self):
        """Test review of high-quality title."""
        title = "The Echoing Shadows: Mystery in the Haunted House"
        script = """
        Shadows dance in the haunted house as echoes fill the corridors.
        Each echo brings a new mystery to solve. The house holds secrets
        that only the shadows and echoes can reveal. This mystery deepens
        with every haunting sound that bounces off the walls.
        """
        idea = "Mystery horror about echoes and shadows revealing secrets in a haunted house"

        review = review_title_by_script_and_idea(
            title_text=title,
            script_text=script,
            idea_summary=idea,
            idea_intent="Create atmospheric mystery using sound and light",
        )

        # Should score well with good alignment
        assert review.overall_score >= 65
        assert review.script_alignment_score >= 65
        assert review.idea_alignment_score >= 60

    def test_poor_quality_title(self):
        """Test review of poorly aligned title."""
        title = "Space Adventure Mission"
        script = """
        In the haunted house, echoes reveal dark secrets.
        The mystery deepens as shadows move in the darkness.
        """
        idea = "Horror mystery about echoes and shadows"

        review = review_title_by_script_and_idea(
            title_text=title, script_text=script, idea_summary=idea
        )

        # Should score poorly with bad alignment
        assert review.overall_score < 60
        assert review.needs_major_revision is True
        assert len(review.improvement_points) > 0

    def test_review_has_category_scores(self):
        """Test that review includes all major categories."""
        review = review_title_by_script_and_idea(
            title_text="The Echo",
            script_text="A story about echoes",
            idea_summary="Story about echoes",
        )

        categories = [cs.category for cs in review.category_scores]

        assert TitleReviewCategory.SCRIPT_ALIGNMENT in categories
        assert TitleReviewCategory.IDEA_ALIGNMENT in categories
        assert TitleReviewCategory.ENGAGEMENT in categories
        assert TitleReviewCategory.SEO_OPTIMIZATION in categories

    def test_review_improvement_points_prioritized(self):
        """Test that improvement points are prioritized."""
        review = review_title_by_script_and_idea(
            title_text="A Story",
            script_text="This is a long story about completely different things",
            idea_summary="Different concept entirely",
        )

        if len(review.improvement_points) > 1:
            # Should be sorted by impact score
            for i in range(len(review.improvement_points) - 1):
                assert (
                    review.improvement_points[i].impact_score
                    >= review.improvement_points[i + 1].impact_score
                )

    def test_review_to_dict_compatibility(self):
        """Test that review can be converted to dict (JSON compatible)."""
        review = review_title_by_script_and_idea(
            title_text="The Echo", script_text="Story about echoes", idea_summary="Echo story"
        )

        # Should be able to convert to dict without errors
        data = review.to_dict()
        assert isinstance(data, dict)
        assert data["title_text"] == "The Echo"
        assert "overall_score" in data
        assert "category_scores" in data
        assert "improvement_points" in data

    def test_empty_script(self):
        """Test handling of empty script."""
        review = review_title_by_script_and_idea(
            title_text="The Echo", script_text="", idea_summary="Story about echoes"
        )

        assert isinstance(review, TitleReview)
        assert review.script_alignment_score >= 0

    def test_very_long_title(self):
        """Test handling of very long title."""
        long_title = "A" * 150
        review = review_title_by_script_and_idea(
            title_text=long_title, script_text="Some script", idea_summary="Some idea"
        )

        # Should have improvement point about length
        assert any(imp.category == TitleReviewCategory.CLARITY for imp in review.improvement_points)

    def test_very_short_title(self):
        """Test handling of very short title."""
        short_title = "A"
        review = review_title_by_script_and_idea(
            title_text=short_title, script_text="Some script", idea_summary="Some idea"
        )

        # Should have improvement point about length
        assert any(imp.category == TitleReviewCategory.CLARITY for imp in review.improvement_points)


class TestWorkflowIntegration:
    """Test workflow integration scenarios."""

    def test_review_ready_for_improvement(self):
        """Test that review is ready for improvement stage."""
        review = review_title_by_script_and_idea(
            title_text="The Echo Mystery",
            script_text="A mysterious echo haunts the house",
            idea_summary="Mystery about haunting echoes",
        )

        # Review should be complete and ready
        assert review.is_ready_for_improvement() is True

    def test_iterative_improvement_tracking(self):
        """Test that review tracks iteration number."""
        review = review_title_by_script_and_idea(
            title_text="The Echo", script_text="Echo story", idea_summary="Echo idea"
        )

        assert review.iteration_number == 1
        assert len(review.improvement_trajectory) == 1
        assert review.improvement_trajectory[0] == review.overall_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
