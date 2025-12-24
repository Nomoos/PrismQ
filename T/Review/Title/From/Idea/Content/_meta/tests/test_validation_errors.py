"""Test input validation and error handling for title review.

This module tests that the review function properly validates inputs
and handles errors gracefully without crashing.
"""

import pytest
from T.Review.Title.From.Idea.Content.src.by_idea_and_content import (
    review_title_by_idea_and_content,
    _sanitize_text_input,
    _validate_text_input,
)


class TestInputValidation:
    """Test input validation logic."""

    def test_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="title_text cannot be empty"):
            review_title_by_idea_and_content("", "valid idea", "valid content text")

    def test_empty_idea_raises_error(self):
        """Test that empty idea raises ValueError."""
        with pytest.raises(ValueError, match="idea_summary cannot be empty"):
            review_title_by_idea_and_content("valid title", "", "valid content text")

    def test_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="content_text cannot be empty"):
            review_title_by_idea_and_content("valid title", "valid idea", "")

    def test_whitespace_only_title_raises_error(self):
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="title_text cannot be empty"):
            review_title_by_idea_and_content("   ", "valid idea", "valid content text")

    def test_title_too_long_raises_error(self):
        """Test that title exceeding max length raises ValueError."""
        long_title = "x" * 201  # MAX_TITLE_LENGTH is 200
        with pytest.raises(ValueError, match="title_text is too long"):
            review_title_by_idea_and_content(long_title, "valid idea", "valid content text")

    def test_idea_too_long_raises_error(self):
        """Test that idea exceeding max length raises ValueError."""
        long_idea = "x" * 5001  # MAX_IDEA_LENGTH is 5000
        with pytest.raises(ValueError, match="idea_summary is too long"):
            review_title_by_idea_and_content("valid title", long_idea, "valid content text")

    def test_content_too_long_raises_error(self):
        """Test that content exceeding max length raises ValueError."""
        long_content = "x" * 100001  # MAX_CONTENT_LENGTH is 100000
        with pytest.raises(ValueError, match="content_text is too long"):
            review_title_by_idea_and_content("valid title", "valid idea", long_content)

    def test_content_too_short_raises_error(self):
        """Test that content shorter than minimum raises ValueError."""
        with pytest.raises(ValueError, match="content_text is too short"):
            review_title_by_idea_and_content("valid title", "valid idea", "short")

    def test_non_string_title_raises_error(self):
        """Test that non-string title raises TypeError."""
        with pytest.raises(TypeError, match="title_text must be a string"):
            review_title_by_idea_and_content(123, "valid idea", "valid content text")

    def test_non_string_idea_raises_error(self):
        """Test that non-string idea raises TypeError."""
        with pytest.raises(TypeError, match="idea_summary must be a string"):
            review_title_by_idea_and_content("valid title", 123, "valid content text")

    def test_non_string_content_raises_error(self):
        """Test that non-string content raises TypeError."""
        with pytest.raises(TypeError, match="content_text must be a string"):
            review_title_by_idea_and_content("valid title", "valid idea", 123)

    def test_none_title_raises_error(self):
        """Test that None title raises TypeError."""
        with pytest.raises(TypeError, match="title_text must be a string"):
            review_title_by_idea_and_content(None, "valid idea", "valid content text")


class TestInputSanitization:
    """Test input sanitization logic."""

    def test_sanitize_removes_null_bytes(self):
        """Test that null bytes are removed during sanitization."""
        text = "hello\x00world"
        sanitized = _sanitize_text_input(text, 100, "test")
        assert "\x00" not in sanitized
        assert sanitized == "helloworld"

    def test_sanitize_normalizes_whitespace(self):
        """Test that excessive whitespace is normalized."""
        text = "hello    world\n\n\ttest"
        sanitized = _sanitize_text_input(text, 100, "test")
        assert sanitized == "hello world test"

    def test_sanitize_strips_leading_trailing_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        text = "   hello world   "
        sanitized = _sanitize_text_input(text, 100, "test")
        assert sanitized == "hello world"

    def test_sanitize_raises_if_too_long_after_cleanup(self):
        """Test that ValueError is raised if text is too long after sanitization."""
        text = "x" * 101
        with pytest.raises(ValueError, match="exceeds maximum length"):
            _sanitize_text_input(text, 100, "test")

    def test_sanitize_non_string_raises_error(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="must be a string"):
            _sanitize_text_input(123, 100, "test")


class TestSecurityIssues:
    """Test handling of potential security issues."""

    def test_null_bytes_handled_safely(self):
        """Test that null bytes in input are handled safely."""
        # Should not crash, null bytes should be removed
        review = review_title_by_idea_and_content(
            "title\x00test",
            "idea\x00test",
            "content text\x00with null bytes that should be removed"
        )
        assert review is not None
        assert "\x00" not in review.title_text

    def test_unicode_characters_handled(self):
        """Test that Unicode characters are handled correctly."""
        review = review_title_by_idea_and_content(
            "The Mystery of 神秘",
            "A story about ancient artifacts 🏺",
            "Deep in the jungle, explorers find ancient treasures with mysterious symbols 象形文字"
        )
        assert review is not None
        assert review.overall_score >= 0

    def test_special_characters_handled(self):
        """Test that special characters don't cause issues."""
        review = review_title_by_idea_and_content(
            "Title with special chars: <>&\"'",
            "Idea with symbols: @#$%^&*()",
            "Content with various characters: !@#$%^&*(){}[]|\\:;<>?,./~`"
        )
        assert review is not None
        assert review.overall_score >= 0

    def test_newlines_and_tabs_handled(self):
        """Test that newlines and tabs don't break processing."""
        review = review_title_by_idea_and_content(
            "Title\nwith\nnewlines",
            "Idea\twith\ttabs",
            "Content\n\twith\n\tmixed\n\twhitespace characters everywhere"
        )
        assert review is not None
        assert review.overall_score >= 0


class TestErrorRecovery:
    """Test that errors are handled gracefully without crashing."""

    def test_valid_inputs_return_review(self):
        """Test that valid inputs return a review object."""
        review = review_title_by_idea_and_content(
            "The Haunted Mansion",
            "A horror story about a haunted house",
            "Deep in the forest stands an old mansion. Local legends speak of strange sounds and ghostly apparitions."
        )
        assert review is not None
        assert review.overall_score >= 0
        assert review.overall_score <= 100
        assert review.title_id.startswith("title-")
        assert review.idea_id.startswith("idea-")
        assert review.content_id.startswith("content-")

    def test_minimal_valid_content(self):
        """Test that minimal valid content works."""
        review = review_title_by_idea_and_content(
            "T",
            "I",
            "Content xx"  # Exactly 10 chars minimum
        )
        assert review is not None
        assert review.overall_score >= 0

    def test_maximum_valid_lengths(self):
        """Test that maximum valid lengths work."""
        review = review_title_by_idea_and_content(
            "x" * 200,  # MAX_TITLE_LENGTH
            "y" * 5000,  # MAX_IDEA_LENGTH
            "z" * 1000  # Well within MAX_CONTENT_LENGTH
        )
        assert review is not None
        assert review.overall_score >= 0


class TestIdempotency:
    """Test that same inputs produce same IDs (idempotency)."""

    def test_same_inputs_produce_same_ids(self):
        """Test that identical inputs produce identical IDs."""
        review1 = review_title_by_idea_and_content(
            "Consistent Title",
            "Consistent Idea",
            "Consistent content that should produce the same ID every time"
        )
        review2 = review_title_by_idea_and_content(
            "Consistent Title",
            "Consistent Idea",
            "Consistent content that should produce the same ID every time"
        )
        
        assert review1.title_id == review2.title_id
        assert review1.idea_id == review2.idea_id
        assert review1.content_id == review2.content_id

    def test_different_inputs_produce_different_ids(self):
        """Test that different inputs produce different IDs."""
        review1 = review_title_by_idea_and_content(
            "Title One",
            "Idea One",
            "Content one with specific text"
        )
        review2 = review_title_by_idea_and_content(
            "Title Two",
            "Idea Two",
            "Content two with different text"
        )
        
        assert review1.title_id != review2.title_id
        assert review1.idea_id != review2.idea_id
        assert review1.content_id != review2.content_id

    def test_whitespace_normalized_produces_same_id(self):
        """Test that whitespace differences are normalized for ID generation."""
        review1 = review_title_by_idea_and_content(
            "Title  with   spaces",
            "Idea  with   spaces",
            "Content  with   extra   spaces"
        )
        review2 = review_title_by_idea_and_content(
            "Title with spaces",
            "Idea with spaces",
            "Content with extra spaces"
        )
        
        # After sanitization, these should produce the same IDs
        assert review1.title_id == review2.title_id
        assert review1.idea_id == review2.idea_id
        assert review1.content_id == review2.content_id
