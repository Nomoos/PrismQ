"""Performance tests for title review.

These tests ensure that the review function performs within acceptable time limits.
"""

import pytest
from T.Review.Title.From.Idea.Content.src.by_idea_and_content import (
    review_title_by_idea_and_content,
)


class TestPerformance:
    """Test performance characteristics of the review function."""

    @pytest.mark.timeout(1)
    def test_normal_content_completes_quickly(self):
        """Test that normal-sized content completes within 1 second."""
        content = "This is a normal sized content. " * 100  # About 3KB
        review = review_title_by_idea_and_content(
            "Test Title for Performance",
            "Test idea for performance evaluation",
            content
        )
        assert review is not None
        assert review.overall_score >= 0

    @pytest.mark.timeout(5)
    def test_large_content_completes_reasonably(self):
        """Test that large content (50KB) completes within 5 seconds."""
        # Create ~50KB content
        content = "This is a large content section with many words. " * 1000
        review = review_title_by_idea_and_content(
            "Test Title for Large Content Performance",
            "Test idea for large content performance evaluation",
            content
        )
        assert review is not None
        assert review.overall_score >= 0

    @pytest.mark.timeout(2)
    def test_multiple_reviews_perform_well(self):
        """Test that multiple reviews complete within reasonable time."""
        for i in range(10):
            review = review_title_by_idea_and_content(
                f"Test Title {i}",
                f"Test idea number {i}",
                f"Test content for iteration {i} with some additional text to make it realistic"
            )
            assert review is not None

    @pytest.mark.timeout(1)
    def test_long_title_performs_well(self):
        """Test that maximum length title doesn't slow processing."""
        long_title = "Very long title " * 12  # Near max length
        review = review_title_by_idea_and_content(
            long_title[:200],  # Ensure within limit
            "Test idea",
            "Test content for performance with long title evaluation"
        )
        assert review is not None

    @pytest.mark.timeout(2)
    def test_long_idea_performs_well(self):
        """Test that maximum length idea doesn't slow processing."""
        long_idea = "Very detailed idea summary " * 180  # Near max length
        review = review_title_by_idea_and_content(
            "Test Title",
            long_idea[:5000],  # Ensure within limit
            "Test content for performance with long idea evaluation"
        )
        assert review is not None

    @pytest.mark.timeout(3)
    def test_complex_content_with_many_keywords(self):
        """Test content with many unique words for keyword extraction."""
        # Content with many unique words to stress keyword extraction
        words = [f"keyword{i}" for i in range(200)]
        content = " ".join(words) + " with additional context and description"
        review = review_title_by_idea_and_content(
            "Title with many keyword1 keyword2 keyword3",
            "Idea about keyword5 keyword10 keyword20",
            content
        )
        assert review is not None
