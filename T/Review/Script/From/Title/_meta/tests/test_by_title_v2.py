"""Tests for PrismQ.T.Review.Content.ByTitle v2 module."""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.idea import ContentGenre, Idea
from T.Review.Content.ByTitle import (
    ImprovementComparison,
    compare_reviews,
    extract_improvements_from_review,
    get_next_steps,
    is_ready_to_proceed,
    review_content_by_title,
    review_content_by_title_v2,
)
from T.Review.Content.script_review import ContentLength, ReviewCategory


@pytest.fixture
def sample_idea():
    """Create a sample idea for testing."""
    return Idea(
        title="The Echo",
        concept="A girl hears her own future voice warning her",
        premise="A teenage girl discovers she can hear warnings from her future self through an old radio",
        hook="What if you could hear your own voice... from tomorrow?",
        genre=ContentGenre.HORROR,
        target_audience="Young adults interested in psychological horror",
        target_platforms=["youtube"],
        length_target="90 seconds",
    )


@pytest.fixture
def script_v1():
    """Create a v1 script for testing."""
    return """
    Last night I heard a whisper through my grandmother's old radio.
    At first, I thought it was just static.
    """


@pytest.fixture
def script_v2():
    """Create an improved v2 script for testing."""
    return """
    Last night I heard a whisper through my grandmother's old radio.
    
    At first, I thought it was just static, but then I recognized the voice.
    It was mine. But the words... they were warning me about tomorrow.
    
    "Don't trust him," my own voice said. "The echo knows what's coming."
    
    I'm scared. I'm terrified. Because tomorrow is here, and I don't know
    who to trust anymore. The future voice was right about everything.
    
    Now I understand - the echo isn't just a warning. It's a curse.
    """


@pytest.fixture
def title_v1():
    """Create a v1 title for testing."""
    return "The Voice"


@pytest.fixture
def title_v3():
    """Create an improved v3 title for testing."""
    return "The Voice That Knows Tomorrow - An Echo from the Future"


class TestReviewScriptByTitleV2:
    """Test cases for review_content_by_title_v2 function."""

    def test_basic_v2_review(self, script_v2, title_v3, sample_idea):
        """Test basic v2 script review functionality."""
        review = review_content_by_title_v2(content_text=script_v2, title=title_v3, idea=sample_idea)

        assert review is not None
        assert review.script_title == title_v3
        assert 0 <= review.overall_score <= 100
        assert len(review.category_scores) > 0
        assert review.reviewer_id == "AI-ScriptReviewer-ByTitle-v2-001"

    def test_v2_review_includes_version_metadata(self, script_v2, title_v3, sample_idea):
        """Test that v2 review includes version information in metadata."""
        review = review_content_by_title_v2(
            content_text=script_v2,
            title=title_v3,
            idea=sample_idea,
            script_version="v2",
            title_version="v3",
        )

        assert review.metadata["script_version"] == "v2"
        assert review.metadata["title_version"] == "v3"
        assert review.metadata["review_type"] == "v2_refinement"

    def test_v2_review_with_previous_review(
        self, script_v1, script_v2, title_v1, title_v3, sample_idea
    ):
        """Test v2 review with comparison to v1 review."""
        # Create v1 review
        v1_review = review_content_by_title(script_v1, title_v1, sample_idea)

        # Create v2 review with comparison
        v2_review = review_content_by_title_v2(
            content_text=script_v2, title=title_v3, idea=sample_idea, previous_review=v1_review
        )

        assert v2_review.metadata["has_comparison"] == "true"
        assert "comparisons" in v2_review.metadata
        assert int(v2_review.metadata["comparisons"]) > 0

    def test_v2_review_without_previous_review(self, script_v2, title_v3, sample_idea):
        """Test v2 review without previous review for comparison."""
        review = review_content_by_title_v2(
            content_text=script_v2, title=title_v3, idea=sample_idea, previous_review=None
        )

        assert review.metadata["has_comparison"] == "false"
        assert review is not None

    def test_v2_review_with_custom_versions(self, script_v2, title_v3, sample_idea):
        """Test v2 review with custom version strings."""
        review = review_content_by_title_v2(
            content_text=script_v2,
            title=title_v3,
            idea=sample_idea,
            script_version="v4",
            title_version="v5",
        )

        assert review.metadata["script_version"] == "v4"
        assert review.metadata["title_version"] == "v5"

    def test_v2_review_generates_version_specific_content_id(self, script_v2, title_v3, sample_idea):
        """Test that v2 review generates script ID with version."""
        review = review_content_by_title_v2(
            content_text=script_v2, title=title_v3, idea=sample_idea, script_version="v2"
        )

        assert "-v2" in review.content_id

    def test_v2_review_with_target_length(self, script_v2, title_v3, sample_idea):
        """Test v2 review with target length specified."""
        review = review_content_by_title_v2(
            content_text=script_v2, title=title_v3, idea=sample_idea, target_length_seconds=60
        )

        assert review.optimal_length_seconds == 60
        assert review.current_length_seconds > 0


class TestImprovementComparison:
    """Test cases for improvement comparison functionality."""

    def test_compare_reviews_basic(self, script_v1, script_v2, title_v1, title_v3, sample_idea):
        """Test basic review comparison."""
        v1_review = review_content_by_title(script_v1, title_v1, sample_idea)
        v2_review = review_content_by_title(script_v2, title_v3, sample_idea)

        comparisons = compare_reviews(v1_review, v2_review)

        assert len(comparisons) > 0
        assert all(isinstance(c, ImprovementComparison) for c in comparisons)

    def test_compare_reviews_with_none(self, script_v2, title_v3, sample_idea):
        """Test comparison with None as v1 review."""
        v2_review = review_content_by_title(script_v2, title_v3, sample_idea)

        comparisons = compare_reviews(None, v2_review)

        assert len(comparisons) == 0

    def test_improvement_comparison_structure(
        self, script_v1, script_v2, title_v1, title_v3, sample_idea
    ):
        """Test that improvement comparisons have expected structure."""
        v1_review = review_content_by_title(script_v1, title_v1, sample_idea)
        v2_review = review_content_by_title(script_v2, title_v3, sample_idea)

        comparisons = compare_reviews(v1_review, v2_review)

        for comp in comparisons:
            assert hasattr(comp, "category")
            assert hasattr(comp, "v1_score")
            assert hasattr(comp, "v2_score")
            assert hasattr(comp, "delta")
            assert hasattr(comp, "improved")
            assert hasattr(comp, "regression")
            assert hasattr(comp, "maintained")
            assert hasattr(comp, "feedback")
            assert isinstance(comp.feedback, str)

    def test_improvement_detection(self, script_v1, script_v2, title_v1, title_v3, sample_idea):
        """Test detection of improvements."""
        v1_review = review_content_by_title(script_v1, title_v1, sample_idea)
        v2_review = review_content_by_title(script_v2, title_v3, sample_idea)

        comparisons = compare_reviews(v1_review, v2_review)

        # At least overall score should be compared
        overall_comp = next((c for c in comparisons if c.category == "overall"), None)
        assert overall_comp is not None
        assert overall_comp.delta == v2_review.overall_score - v1_review.overall_score

    def test_regression_detection(self, sample_idea):
        """Test detection of regressions."""
        # Create reviews where v2 is worse
        good_content = (
            """
        Amazing story with echo and voice and future warning.
        Terror and fear grip the character as the echo reveals secrets.
        The voice echoes through time bringing warnings from tomorrow.
        Discover the truth as the echo grows louder and more urgent.
        """
            * 3
        )

        poor_content = "Short."

        v1_review = review_content_by_title(good_content, "The Echo Voice", sample_idea)
        v2_review = review_content_by_title(poor_content, "Title", sample_idea)

        comparisons = compare_reviews(v1_review, v2_review)

        # Should detect some regressions
        regressions = [c for c in comparisons if c.regression]
        assert len(regressions) > 0

    def test_maintained_score_detection(self, script_v2, title_v3, sample_idea):
        """Test detection of maintained scores."""
        v1_review = review_content_by_title(script_v2, title_v3, sample_idea)
        v2_review = review_content_by_title(script_v2, title_v3, sample_idea)

        comparisons = compare_reviews(v1_review, v2_review)

        # All scores should be maintained (same script/title)
        maintained = [c for c in comparisons if c.maintained]
        assert len(maintained) > 0


class TestComparisonMetadata:
    """Test cases for comparison metadata in reviews."""

    def test_improvements_count_in_metadata(
        self, script_v1, script_v2, title_v1, title_v3, sample_idea
    ):
        """Test that improvements count is tracked in metadata."""
        v1_review = review_content_by_title(script_v1, title_v1, sample_idea)
        v2_review = review_content_by_title_v2(
            script_v2, title_v3, sample_idea, previous_review=v1_review
        )

        assert "improvements_count" in v2_review.metadata
        assert "regressions_count" in v2_review.metadata

    def test_improvement_summary_in_metadata(
        self, script_v1, script_v2, title_v1, title_v3, sample_idea
    ):
        """Test that improvement summary is included in metadata."""
        v1_review = review_content_by_title(script_v1, title_v1, sample_idea)
        v2_review = review_content_by_title_v2(
            script_v2, title_v3, sample_idea, previous_review=v1_review
        )

        # Should have improvement summary if there are changes
        if (
            int(v2_review.metadata.get("improvements_count", "0")) > 0
            or int(v2_review.metadata.get("regressions_count", "0")) > 0
        ):
            assert "improvement_summary" in v2_review.metadata

    def test_regression_warnings_in_improvement_points(self, sample_idea):
        """Test that regressions are added as improvement points."""
        good_content = (
            """
        Echo voice future warning discover tomorrow.
        Terror fear horror nightmare shadow scared dark.
        """
            * 10
        )

        poor_content = "Test."

        v1_review = review_content_by_title(good_content, "The Echo Voice Future", sample_idea)
        v2_review = review_content_by_title_v2(
            poor_content, "Title", sample_idea, previous_review=v1_review
        )

        # Should have regression warnings as high-priority improvements
        high_priority = [p for p in v2_review.improvement_points if p.priority == "high"]
        regression_warnings = [p for p in high_priority if "regression" in p.title.lower()]

        if int(v2_review.metadata.get("regressions_count", "0")) > 0:
            assert len(regression_warnings) > 0


class TestHelperFunctions:
    """Test cases for helper functions."""

    def test_extract_improvements_from_review(self, script_v2, title_v3, sample_idea):
        """Test extraction of improvements from review."""
        review = review_content_by_title_v2(script_v2, title_v3, sample_idea)

        improvements = extract_improvements_from_review(review)

        assert isinstance(improvements, list)
        # Should extract only high-priority improvements
        for imp in improvements:
            assert isinstance(imp, str)
            assert "impact:" in imp or len(imp) > 0

    def test_is_ready_to_proceed_with_high_score(self, sample_idea):
        """Test ready to proceed check with high score."""
        good_content = (
            """
        The echo of my voice came through the radio, warning me about tomorrow.
        It was a voice from the future, my future self speaking to me now.
        Terror gripped me as I realized the echo knows everything that will happen.
        The voice that knows tomorrow is both a blessing and a curse.
        Fear filled my heart but hope remained as I listened to the warnings.
        """
            * 3
        )

        title = "The Voice That Knows Tomorrow"

        review = review_content_by_title_v2(good_content, title, sample_idea)

        # Should be ready if score is high enough
        ready = is_ready_to_proceed(review, threshold=60)
        assert isinstance(ready, bool)

    def test_is_ready_to_proceed_with_low_score(self, sample_idea):
        """Test ready to proceed check with low score."""
        poor_content = "Short."
        title = "Random Title"

        review = review_content_by_title_v2(poor_content, title, sample_idea)

        ready = is_ready_to_proceed(review, threshold=80)
        assert ready == False

    def test_get_next_steps_basic(self, script_v2, title_v3, sample_idea):
        """Test generation of next steps."""
        review = review_content_by_title_v2(script_v2, title_v3, sample_idea)

        steps = get_next_steps(review)

        assert isinstance(steps, list)
        assert len(steps) > 0
        assert all(isinstance(s, str) for s in steps)

    def test_get_next_steps_for_high_quality_content(self, sample_idea):
        """Test next steps for high-quality script."""
        excellent_content = (
            """
        The echo of my voice came through the radio, warning me about tomorrow.
        It was a voice from the future, my future self speaking to me now.
        Terror gripped me as I realized the echo knows everything that will happen.
        The voice that knows tomorrow is both a blessing and a curse.
        Fear filled my heart but hope remained as I listened to the warnings.
        I discovered the truth about my future through this haunting echo.
        The mystery unfolded as each warning became reality.
        """
            * 3
        )

        title = "The Voice That Knows Tomorrow - An Echo from the Future"

        review = review_content_by_title_v2(excellent_content, title, sample_idea)
        steps = get_next_steps(review)

        # Should suggest proceeding if quality is high
        if review.overall_score >= 80:
            assert any("proceed" in step.lower() for step in steps)

    def test_get_next_steps_for_poor_quality_content(self, sample_idea):
        """Test next steps for poor-quality script."""
        poor_content = "Test."
        title = "Title"

        review = review_content_by_title_v2(poor_content, title, sample_idea)
        steps = get_next_steps(review)

        # Should suggest improvements
        assert any("revision" in step.lower() or "improve" in step.lower() for step in steps)


class TestJSONOutput:
    """Test cases for JSON format output."""

    def test_v2_review_can_be_converted_to_dict(self, script_v2, title_v3, sample_idea):
        """Test that v2 review can be converted to dictionary."""
        review = review_content_by_title_v2(script_v2, title_v3, sample_idea)

        review_dict = review.to_dict()

        assert isinstance(review_dict, dict)
        assert "content_id" in review_dict
        assert "overall_score" in review_dict
        assert "category_scores" in review_dict
        assert "improvement_points" in review_dict
        assert "metadata" in review_dict

    def test_v2_json_output_includes_version_info(self, script_v2, title_v3, sample_idea):
        """Test that JSON output includes version information."""
        review = review_content_by_title_v2(
            script_v2, title_v3, sample_idea, script_version="v2", title_version="v3"
        )

        review_dict = review.to_dict()

        assert review_dict["metadata"]["script_version"] == "v2"
        assert review_dict["metadata"]["title_version"] == "v3"
        assert review_dict["metadata"]["review_type"] == "v2_refinement"

    def test_v2_json_output_includes_comparison_data(
        self, script_v1, script_v2, title_v1, title_v3, sample_idea
    ):
        """Test that JSON output includes comparison data when available."""
        v1_review = review_content_by_title(script_v1, title_v1, sample_idea)
        v2_review = review_content_by_title_v2(
            script_v2, title_v3, sample_idea, previous_review=v1_review
        )

        review_dict = v2_review.to_dict()

        assert review_dict["metadata"]["has_comparison"] == "true"
        assert "comparisons" in review_dict["metadata"]


class TestEdgeCases:
    """Test cases for edge cases and error handling."""

    def test_v2_review_handles_empty_content(self, title_v3, sample_idea):
        """Test v2 review handling of empty script."""
        review = review_content_by_title_v2("", title_v3, sample_idea)

        assert review is not None
        assert review.needs_major_revision == True

    def test_v2_review_handles_very_long_content(self, title_v3, sample_idea):
        """Test v2 review handling of very long script."""
        long_content = "This is a test sentence. " * 1000

        review = review_content_by_title_v2(long_content, title_v3, sample_idea)

        assert review is not None
        assert review.current_length_seconds > 100

    def test_v2_review_with_minimal_idea(self):
        """Test v2 review with minimal idea object."""
        idea = Idea(title="Minimal", concept="", genre=ContentGenre.HORROR)

        review = review_content_by_title_v2("Test script.", "Title", idea)

        assert review is not None
        assert review.overall_score >= 0

    def test_v2_review_handles_special_characters(self, sample_idea):
        """Test v2 review handling of special characters."""
        script = """
        Test with special chars: @#$%^&*()
        Unicode: café, naïve, Zürich
        Symbols: © ® ™ € £ ¥
        """
        title = "Special @#$ Characters!"

        review = review_content_by_title_v2(script, title, sample_idea)

        assert review is not None
        assert review.overall_score >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
