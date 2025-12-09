"""Tests for Idea summary and translation functionality."""

import os
import sys

import pytest

# Add parent directories to path for imports
current_dir = os.path.dirname(__file__)
model_dir = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.insert(0, model_dir)
sys.path.insert(0, os.path.join(model_dir, "src"))

from src.idea import ContentGenre, Idea, IdeaStatus


class TestIdeaSummary:
    """Tests for Idea summary generation."""

    def test_generate_basic_summary(self):
        """Test generating a basic summary."""
        idea = Idea(title="Test Idea", concept="Test concept for validation")

        summary = idea.generate_summary()

        assert summary is not None
        assert "Title: Test Idea" in summary
        assert "Concept: Test concept" in summary

    def test_summary_includes_premise(self):
        """Test that summary includes premise if available."""
        idea = Idea(
            title="Test Idea",
            concept="Test concept",
            premise="This is a detailed premise for the idea",
        )

        summary = idea.generate_summary()

        assert "Premise:" in summary
        assert "detailed premise" in summary

    def test_summary_includes_logline(self):
        """Test that summary includes logline if available."""
        idea = Idea(
            title="Test Idea", concept="Test concept", logline="An exciting one-sentence hook"
        )

        summary = idea.generate_summary()

        assert "Logline:" in summary
        assert "one-sentence hook" in summary

    def test_summary_includes_synopsis(self):
        """Test that summary includes synopsis if available."""
        idea = Idea(
            title="Test Idea",
            concept="Test concept",
            synopsis="A comprehensive synopsis of the idea",
        )

        summary = idea.generate_summary()

        assert "Synopsis:" in summary
        assert "comprehensive synopsis" in summary

    def test_summary_includes_genre(self):
        """Test that summary includes genre."""
        idea = Idea(title="Test Idea", concept="Test concept", genre=ContentGenre.HORROR)

        summary = idea.generate_summary()

        assert "Genre: horror" in summary

    def test_summary_includes_platforms(self):
        """Test that summary includes target platforms."""
        idea = Idea(
            title="Test Idea",
            concept="Test concept",
            target_platforms=["youtube", "tiktok", "instagram"],
        )

        summary = idea.generate_summary()

        assert "Platforms:" in summary
        assert "youtube" in summary

    def test_summary_includes_formats(self):
        """Test that summary includes target formats."""
        idea = Idea(
            title="Test Idea", concept="Test concept", target_formats=["text", "audio", "video"]
        )

        summary = idea.generate_summary()

        assert "Formats:" in summary
        assert "text" in summary
        assert "audio" in summary
        assert "video" in summary

    def test_summary_respects_max_length(self):
        """Test that summary respects max_length parameter."""
        idea = Idea(
            title="Test Idea",
            concept="Test concept",
            premise="This is a very long premise " * 20,
            synopsis="This is a very long synopsis " * 30,
        )

        summary = idea.generate_summary(max_length=100)

        assert len(summary) <= 150  # Allow some buffer for truncation logic
        assert "..." in summary or summary.endswith("\n")

    def test_summary_with_complete_idea(self):
        """Test summary with all fields populated."""
        idea = Idea(
            title="The Echo",
            concept="A girl hears her own voice from the future",
            premise="A teenage girl starts hearing a voice identical to her own",
            logline="A girl discovers she can hear her own future thoughts",
            synopsis="An exploration of time paradoxes through horror",
            genre=ContentGenre.HORROR,
            target_platforms=["youtube", "tiktok"],
            target_formats=["video", "audio"],
        )

        summary = idea.generate_summary()

        # Should include key information
        assert "The Echo" in summary
        assert "future" in summary.lower()
        assert "horror" in summary

    def test_summary_empty_optional_fields(self):
        """Test summary with only required fields."""
        idea = Idea(title="Minimal Idea", concept="Minimal concept")

        summary = idea.generate_summary()

        # Should still generate valid summary
        assert "Minimal Idea" in summary
        assert "Minimal concept" in summary
        assert len(summary) > 0


class TestIdeaTranslation:
    """Tests for Idea Czech translation."""

    def test_translate_basic_summary(self):
        """Test translating a basic summary to Czech."""
        idea = Idea(title="Test Idea", concept="Test concept")

        czech = idea.translate_summary_to_czech()

        assert czech is not None
        assert "Název:" in czech  # Czech for "Title:"
        assert "Koncept:" in czech  # Czech for "Concept:"

    def test_translate_with_premise(self):
        """Test translation includes premise."""
        idea = Idea(title="Test Idea", concept="Test concept", premise="A detailed premise")

        czech = idea.translate_summary_to_czech()

        assert "Premisa:" in czech

    def test_translate_with_logline(self):
        """Test translation includes logline."""
        idea = Idea(title="Test Idea", concept="Test concept", logline="A compelling logline")

        czech = idea.translate_summary_to_czech()

        assert "Logline:" in czech

    def test_translate_genre(self):
        """Test genre is translated."""
        idea = Idea(title="Test Idea", concept="Test concept", genre=ContentGenre.HORROR)

        czech = idea.translate_summary_to_czech()

        assert "Žánr:" in czech  # Czech for "Genre:"
        assert "horor" in czech  # Czech for "horror"

    def test_translate_educational_genre(self):
        """Test educational genre translation."""
        idea = Idea(title="Test Idea", concept="Test concept", genre=ContentGenre.EDUCATIONAL)

        czech = idea.translate_summary_to_czech()

        assert "vzdělávací" in czech

    def test_translate_technology_genre(self):
        """Test technology genre translation."""
        idea = Idea(title="Test Idea", concept="Test concept", genre=ContentGenre.TECHNOLOGY)

        czech = idea.translate_summary_to_czech()

        assert "technologie" in czech

    def test_translate_platforms(self):
        """Test platforms are translated."""
        idea = Idea(
            title="Test Idea", concept="Test concept", target_platforms=["youtube", "tiktok"]
        )

        czech = idea.translate_summary_to_czech()

        assert "Platformy:" in czech

    def test_translate_formats(self):
        """Test formats are translated."""
        idea = Idea(title="Test Idea", concept="Test concept", target_formats=["text", "video"])

        czech = idea.translate_summary_to_czech()

        assert "Formáty:" in czech

    def test_translate_with_custom_summary(self):
        """Test translation with custom pre-generated summary."""
        idea = Idea(title="Test Idea", concept="Test concept")

        custom_summary = "Title: Custom\nConcept: Custom concept\nGenre: horror"
        czech = idea.translate_summary_to_czech(summary=custom_summary)

        assert "Název:" in czech
        assert "Koncept:" in czech
        assert "Žánr:" in czech
        assert "horor" in czech

    def test_translation_note_included(self):
        """Test that translation includes note about production usage."""
        idea = Idea(title="Test Idea", concept="Test concept")

        czech = idea.translate_summary_to_czech()

        # Should include note about using StoryTranslation model
        assert "Poznámka:" in czech or "StoryTranslation" in czech

    def test_translate_complete_idea(self):
        """Test translation of complete idea."""
        idea = Idea(
            title="The Echo",
            concept="Time travel horror story",
            premise="A girl hears her future self",
            logline="Hear your future, change your fate",
            synopsis="A psychological thriller about time",
            genre=ContentGenre.HORROR,
            target_platforms=["youtube", "tiktok"],
            target_formats=["video", "audio"],
        )

        czech = idea.translate_summary_to_czech()

        # Should have Czech headings
        assert "Název:" in czech
        assert "Koncept:" in czech
        assert "Premisa:" in czech
        assert "Žánr:" in czech
        assert "horor" in czech


class TestSummaryAndTranslationIntegration:
    """Tests for integrated summary and translation workflow."""

    def test_generate_and_translate_workflow(self):
        """Test complete workflow: generate summary then translate."""
        idea = Idea(
            title="AI Revolution",
            concept="The impact of AI on society",
            premise="AI is transforming every aspect of modern life",
            genre=ContentGenre.TECHNOLOGY,
            target_platforms=["youtube", "medium"],
            target_formats=["video", "text"],
        )

        # Generate summary
        summary = idea.generate_summary(max_length=300)
        assert summary is not None
        assert len(summary) > 0

        # Translate to Czech
        czech = idea.translate_summary_to_czech(summary=summary)
        assert czech is not None
        assert "Název:" in czech
        assert "technologie" in czech

    def test_direct_translate_workflow(self):
        """Test direct translation without pre-generating summary."""
        idea = Idea(
            title="Digital Privacy",
            concept="Protecting privacy in digital age",
            genre=ContentGenre.EDUCATIONAL,
        )

        # Translate directly (will generate summary internally)
        czech = idea.translate_summary_to_czech()

        assert czech is not None
        assert "Název:" in czech
        assert "Koncept:" in czech
        assert "vzdělávací" in czech

    def test_multiple_translations_same_idea(self):
        """Test generating multiple translations of same idea."""
        idea = Idea(
            title="Climate Change",
            concept="Understanding climate science",
            premise="A detailed exploration of climate science and its implications for the future",
            synopsis="This comprehensive look at climate change examines the science, impacts, and solutions",
            genre=ContentGenre.DOCUMENTARY,
        )

        # Generate multiple summaries with different lengths
        short_summary = idea.generate_summary(max_length=100)
        long_summary = idea.generate_summary(max_length=500)

        # Translate both
        czech_short = idea.translate_summary_to_czech(summary=short_summary)
        czech_long = idea.translate_summary_to_czech(summary=long_summary)

        # Czech translations should have different lengths
        assert len(czech_short) <= len(czech_long)
        assert "Název:" in czech_short
        assert "Název:" in czech_long
