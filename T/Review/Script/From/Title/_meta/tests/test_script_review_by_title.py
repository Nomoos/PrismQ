"""Tests for PrismQ.T.Review.Content.ByTitle module."""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.idea import ContentGenre, Idea
from T.Review.Content.ByTitle import AlignmentScore, review_content_by_title
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
def sample_content():
    """Create a sample script for testing."""
    return """
    Last night I heard a whisper through my grandmother's old radio.
    
    At first, I thought it was just static, but then I recognized the voice.
    It was mine. But the words... they were warning me about tomorrow.
    
    "Don't trust him," my own voice said. "The echo knows what's coming."
    
    I'm scared. I'm terrified. Because tomorrow is here, and I don't know
    who to trust anymore. The future voice was right about everything.
    
    Now I understand - the echo isn't just a warning. It's a curse.
    """


class TestReviewScriptByTitle:
    """Test cases for review_content_by_title function."""

    def test_basic_review(self, sample_content, sample_idea):
        """Test basic script review functionality."""
        title = "The Voice That Knows Tomorrow"
        review = review_content_by_title(sample_content, title, sample_idea)

        assert review is not None
        assert review.script_title == title
        assert 0 <= review.overall_score <= 100
        assert len(review.category_scores) > 0
        assert review.reviewer_id == "AI-ScriptReviewer-ByTitle-001"

    def test_review_with_strong_alignment(self, sample_idea):
        """Test review with strong title-script alignment."""
        title = "The Echo"
        script = """
        The echo came at midnight. An echo of my own voice,
        warning me about tomorrow. The echo knows the future.
        The echo is my only hope. The echo, the echo, the echo...
        """

        review = review_content_by_title(script, title, sample_idea)

        # Should have good alignment since "echo" appears multiple times
        assert review.overall_score >= 60
        title_score = int(review.metadata.get("title_alignment_score", "0"))
        assert title_score >= 60

    def test_review_with_poor_alignment(self, sample_idea):
        """Test review with poor title-script alignment."""
        title = "Quantum Mechanics of Space Travel"
        script = """
        Once upon a time, there was a little dog who loved to play.
        He would run in the park every day and chase butterflies.
        """

        review = review_content_by_title(script, title, sample_idea)

        # Should have lower score due to poor alignment
        assert review.overall_score < 80
        assert review.needs_major_revision == (review.overall_score < 60)

    def test_review_with_custom_content_id(self, sample_content, sample_idea):
        """Test review with custom script ID."""
        title = "The Voice That Knows Tomorrow"
        custom_id = "my-custom-script-123"

        review = review_content_by_title(sample_content, title, sample_idea, content_id=custom_id)

        assert review.content_id == custom_id

    def test_review_generates_default_content_id(self, sample_content, sample_idea):
        """Test that default script ID is generated."""
        title = "The Voice That Knows Tomorrow"

        review = review_content_by_title(sample_content, title, sample_idea)

        assert review.content_id is not None
        assert "script-" in review.content_id
        assert "the-echo" in review.content_id.lower()

    def test_review_with_target_length(self, sample_content, sample_idea):
        """Test review with target length specified."""
        title = "The Voice That Knows Tomorrow"

        # Note: sample_idea has length_target="90 seconds" which takes priority
        review = review_content_by_title(sample_content, title, sample_idea, target_length_seconds=60)

        # Idea's length_target takes priority, so we get YOUTUBE_SHORT_EXTENDED
        assert review.target_length == ContentLength.YOUTUBE_SHORT_EXTENDED
        assert review.is_youtube_short == True
        assert review.optimal_length_seconds == 60

    def test_review_estimates_content_length(self, sample_content, sample_idea):
        """Test that script length is estimated."""
        title = "The Voice That Knows Tomorrow"

        review = review_content_by_title(sample_content, title, sample_idea)

        assert review.current_length_seconds is not None
        assert review.current_length_seconds > 0


class TestAlignmentAnalysis:
    """Test cases for title and idea alignment analysis."""

    def test_title_alignment_strong(self, sample_idea):
        """Test strong title alignment detection."""
        title = "The Echo Voice"
        script = """
        The echo of a voice called out to me. An echo from tomorrow.
        The voice was familiar - it was my own echo, repeating warnings.
        Echo, echo, echo... the voice wouldn't stop.
        """

        review = review_content_by_title(script, title, sample_idea)
        title_score = int(review.metadata.get("title_alignment_score", "0"))

        assert title_score >= 70
        assert len(review.strengths) > 0

    def test_title_alignment_weak(self, sample_idea):
        """Test weak title alignment detection."""
        title = "Mysterious Quantum Entanglement"
        script = """
        Once there was a person who liked to walk in the park.
        They enjoyed the sunshine and the fresh air very much.
        """

        review = review_content_by_title(script, title, sample_idea)
        title_score = int(review.metadata.get("title_alignment_score", "0"))

        assert title_score < 60
        assert len(review.improvement_points) > 0

    def test_idea_alignment_with_concept(self, sample_idea):
        """Test idea alignment based on concept."""
        title = "The Future Voice"
        script = """
        I heard a voice warning me. It was my own voice from the future.
        The voice knows what will happen tomorrow and tries to warn me.
        """

        review = review_content_by_title(script, title, sample_idea)
        idea_score = int(review.metadata.get("idea_alignment_score", "0"))

        # Should have decent idea alignment
        assert idea_score >= 60

    def test_idea_alignment_with_genre(self, sample_idea):
        """Test genre consistency checking."""
        title = "The Horror Within"
        script = """
        Fear gripped me as the dark shadow approached. Terror filled
        my heart. The nightmare was real, and I was scared beyond belief.
        """

        review = review_content_by_title(script, title, sample_idea)

        # Horror genre words should boost alignment
        assert review.overall_score > 0


class TestContentScoring:
    """Test cases for content quality scoring."""

    def test_engagement_score_with_strong_opening(self, sample_idea):
        """Test engagement scoring with strong opening."""
        title = "The Question"
        script = """
        What if you could see the future? Imagine knowing every decision
        before you make it. Last night, everything changed suddenly!
        """

        review = review_content_by_title(script, title, sample_idea)

        # Should have good engagement due to questions and strong words
        engagement = review.get_category_score(ReviewCategory.ENGAGEMENT)
        assert engagement is not None
        assert engagement.score >= 70

    def test_pacing_score(self, sample_idea):
        """Test pacing score calculation."""
        title = "Well Paced Story"
        script = """
        First paragraph with about one hundred to two hundred characters 
        that establishes the setting and introduces our main character here.
        
        Second paragraph continues the story with similar length, maintaining
        good pacing and keeping the reader engaged with the narrative flow.
        
        Third paragraph wraps up with appropriate length and good structure
        to provide satisfying conclusion without dragging on too long here.
        """

        review = review_content_by_title(script, title, sample_idea)

        pacing = review.get_category_score(ReviewCategory.PACING)
        assert pacing is not None
        assert pacing.score >= 60

    def test_clarity_score(self, sample_idea):
        """Test clarity scoring based on sentence structure."""
        title = "Clear Story"
        script = """
        This is clear. This makes sense. The story flows well.
        Each sentence is concise. The meaning is obvious. Good clarity here.
        """

        review = review_content_by_title(script, title, sample_idea)

        clarity = review.get_category_score(ReviewCategory.CLARITY)
        assert clarity is not None
        assert clarity.score >= 60

    def test_impact_score_with_emotional_content(self, sample_idea):
        """Test impact scoring with emotional words."""
        title = "Emotional Journey"
        script = """
        I was shocked and amazed by the discovery. Fear gripped my heart
        as I realized the truth. Hope faded, replaced by terror and pain.
        But then joy returned, and I felt grateful and proud of my journey.
        """

        review = review_content_by_title(script, title, sample_idea)

        impact = review.get_category_score(ReviewCategory.IMPACT)
        assert impact is not None
        assert impact.score >= 70


class TestImprovementGeneration:
    """Test cases for improvement point generation."""

    def test_generates_improvements_for_low_scores(self, sample_idea):
        """Test that improvements are generated for low scores."""
        title = "Quantum Physics"
        script = "Short text."

        review = review_content_by_title(script, title, sample_idea)

        assert len(review.improvement_points) > 0
        assert review.needs_major_revision == True

    def test_improvement_points_have_impact_scores(self, sample_idea):
        """Test that improvement points include impact scores."""
        title = "Test Title"
        script = "Very short script that needs improvement overall here."

        review = review_content_by_title(script, title, sample_idea)

        for improvement in review.improvement_points:
            assert improvement.impact_score > 0
            assert improvement.priority in ["high", "medium", "low"]
            assert improvement.suggested_fix != ""

    def test_improvements_sorted_by_impact(self, sample_idea):
        """Test that improvements are sorted by impact score."""
        title = "Poor Content"
        script = "Needs work."

        review = review_content_by_title(script, title, sample_idea)

        if len(review.improvement_points) > 1:
            for i in range(len(review.improvement_points) - 1):
                assert (
                    review.improvement_points[i].impact_score
                    >= review.improvement_points[i + 1].impact_score
                )

    def test_quick_wins_identified(self, sample_idea):
        """Test that quick wins are identified."""
        title = "Needs Improvement"
        script = "Short script."

        review = review_content_by_title(script, title, sample_idea)

        # Should have some quick wins if there are high-impact improvements
        if any(imp.impact_score >= 15 for imp in review.improvement_points[:3]):
            assert len(review.quick_wins) > 0


class TestTargetLengthDetermination:
    """Test cases for target length determination."""

    def test_determines_youtube_short_from_idea_length_target(self):
        """Test YouTube short detection from idea's length_target."""
        idea = Idea(
            title="Short Video",
            concept="Quick content",
            genre=ContentGenre.EDUCATIONAL,
            length_target="60 seconds",
        )

        review = review_content_by_title("Test script here.", "Title", idea)

        assert review.target_length in [
            ContentLength.YOUTUBE_SHORT,
            ContentLength.YOUTUBE_SHORT_EXTENDED,
        ]

    def test_determines_youtube_short_from_target_seconds(self):
        """Test YouTube short detection from target_length_seconds."""
        idea = Idea(title="Video", concept="Content", genre=ContentGenre.EDUCATIONAL)

        review = review_content_by_title("Test script.", "Title", idea, target_length_seconds=45)

        assert review.target_length == ContentLength.YOUTUBE_SHORT
        assert review.is_youtube_short == True

    def test_determines_short_form_for_longer_content(self):
        """Test short form detection for longer content."""
        idea = Idea(
            title="Longer Video",
            concept="Extended content",
            genre=ContentGenre.EDUCATIONAL,
            length_target="3 minutes",
        )

        review = review_content_by_title("Test script content.", "Title", idea)

        assert review.target_length == ContentLength.SHORT_FORM

    def test_determines_from_platform(self):
        """Test length determination from target platforms."""
        idea = Idea(
            title="TikTok Video",
            concept="Viral content",
            genre=ContentGenre.EDUCATIONAL,
            target_platforms=["tiktok"],
        )

        review = review_content_by_title("Test script.", "Title", idea)

        assert review.target_length == ContentLength.YOUTUBE_SHORT


class TestMetadataAndTracking:
    """Test cases for metadata and tracking features."""

    def test_includes_alignment_scores_in_metadata(self, sample_content, sample_idea):
        """Test that alignment scores are included in metadata."""
        title = "The Voice"
        review = review_content_by_title(sample_content, title, sample_idea)

        assert "title_alignment_score" in review.metadata
        assert "idea_alignment_score" in review.metadata
        assert "idea_genre" in review.metadata
        assert "idea_version" in review.metadata

    def test_tracks_strengths_from_alignment(self, sample_idea):
        """Test that strengths are tracked from alignment analysis."""
        title = "The Echo Voice"
        script = """
        The echo of voices filled the room. Echo after echo, voice after voice.
        The echo and the voice became one, echoing through the voice of time.
        """

        review = review_content_by_title(script, title, sample_idea)

        assert len(review.strengths) > 0

    def test_identifies_primary_concern(self, sample_idea):
        """Test that primary concern is identified."""
        title = "Random Title"
        script = "Short."

        review = review_content_by_title(script, title, sample_idea)

        assert review.primary_concern != ""
        assert len(review.primary_concern) > 10


class TestEdgeCases:
    """Test cases for edge cases and error handling."""

    def test_handles_empty_content(self, sample_idea):
        """Test handling of empty script."""
        title = "Title"
        script = ""

        review = review_content_by_title(script, title, sample_idea)

        assert review is not None
        assert review.needs_major_revision == True

    def test_handles_very_long_content(self, sample_idea):
        """Test handling of very long script."""
        title = "Long Story"
        script = "This is a test sentence. " * 1000

        review = review_content_by_title(script, title, sample_idea)

        assert review is not None
        assert review.current_length_seconds > 100

    def test_handles_minimal_idea(self):
        """Test handling of minimal idea object."""
        idea = Idea(title="Minimal", concept="", genre=ContentGenre.HORROR)

        review = review_content_by_title("Test script.", "Title", idea)

        assert review is not None
        assert review.overall_score >= 0

    def test_handles_special_characters_in_text(self, sample_idea):
        """Test handling of special characters."""
        title = "Special @#$ Characters!"
        script = """
        Test with special chars: @#$%^&*()
        Unicode: café, naïve, Zürich
        Symbols: © ® ™ € £ ¥
        """

        review = review_content_by_title(script, title, sample_idea)

        assert review is not None
        assert review.overall_score >= 0


class TestJSONOutput:
    """Test cases for JSON format output."""

    def test_review_can_be_converted_to_dict(self, sample_content, sample_idea):
        """Test that review can be converted to dictionary."""
        title = "The Voice"
        review = review_content_by_title(sample_content, title, sample_idea)

        review_dict = review.to_dict()

        assert isinstance(review_dict, dict)
        assert "content_id" in review_dict
        assert "overall_score" in review_dict
        assert "category_scores" in review_dict
        assert "improvement_points" in review_dict

    def test_json_output_has_required_fields(self, sample_content, sample_idea):
        """Test that JSON output has all required fields."""
        title = "The Voice"
        review = review_content_by_title(sample_content, title, sample_idea)

        review_dict = review.to_dict()

        # Check required fields from acceptance criteria
        assert review_dict["overall_score"] is not None
        assert isinstance(review_dict["category_scores"], list)
        assert isinstance(review_dict["improvement_points"], list)
        assert isinstance(review_dict["metadata"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
