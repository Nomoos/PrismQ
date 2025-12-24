"""Tests for validation and error handling in Title Improvement module."""

import pytest
from pathlib import Path
import sys

# Add parent directories to path for imports
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir / "../../src"))
sys.path.insert(0, str(test_dir / "../../../../Idea/Model/src"))
sys.path.insert(0, str(test_dir / "../../../../Review/Title/ByScriptAndIdea"))
sys.path.insert(0, str(test_dir / "../../../../Review/Content"))

from title_improver import (
    TitleImprover,
    TitleImprovementError,
    ValidationError,
    ImprovementError,
    validate_version_number,
    extract_version_number,
    validate_version_progression,
    validate_text_length,
    MIN_TITLE_LENGTH,
    MAX_TITLE_LENGTH,
    MIN_CONTENT_LENGTH,
    MAX_CONTENT_LENGTH,
)

from title_review import TitleReview, TitleReviewCategory, TitleImprovementPoint
from script_review import ScriptReview, ReviewCategory, ImprovementPoint, ContentLength


class TestValidationHelpers:
    """Tests for validation helper functions."""

    def test_validate_version_number_valid(self):
        """Test version number validation with valid inputs."""
        # Should not raise
        validate_version_number("v1")
        validate_version_number("v2")
        validate_version_number("v10")
        validate_version_number("v999")

    def test_validate_version_number_invalid_format(self):
        """Test version number validation with invalid formats."""
        with pytest.raises(ValidationError, match="must be in format"):
            validate_version_number("1")
        
        with pytest.raises(ValidationError, match="must be in format"):
            validate_version_number("version1")
        
        with pytest.raises(ValidationError, match="must be in format"):
            validate_version_number("v")
        
        with pytest.raises(ValidationError, match="must be in format"):
            validate_version_number("v1.0")

    def test_validate_version_number_empty(self):
        """Test version number validation with empty input."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_version_number("")
        
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_version_number(None)

    def test_extract_version_number(self):
        """Test extracting numeric part from version string."""
        assert extract_version_number("v1") == 1
        assert extract_version_number("v2") == 2
        assert extract_version_number("v10") == 10
        assert extract_version_number("v999") == 999

    def test_extract_version_number_invalid(self):
        """Test extracting from invalid version string."""
        with pytest.raises(ValidationError):
            extract_version_number("invalid")

    def test_validate_version_progression_valid(self):
        """Test version progression validation with valid progressions."""
        # Should not raise
        validate_version_progression("v1", "v2")
        validate_version_progression("v2", "v3")
        validate_version_progression("v1", "v10")

    def test_validate_version_progression_invalid(self):
        """Test version progression validation with invalid progressions."""
        with pytest.raises(ValidationError, match="must be greater than"):
            validate_version_progression("v2", "v1")
        
        with pytest.raises(ValidationError, match="must be greater than"):
            validate_version_progression("v2", "v2")
        
        with pytest.raises(ValidationError, match="must be greater than"):
            validate_version_progression("v10", "v5")

    def test_validate_text_length_valid(self):
        """Test text length validation with valid inputs."""
        # Should not raise
        validate_text_length("A" * 50, "test", 10, 100)
        validate_text_length("Test title", "title", MIN_TITLE_LENGTH, MAX_TITLE_LENGTH)

    def test_validate_text_length_too_short(self):
        """Test text length validation with too short input."""
        with pytest.raises(ValidationError, match="too short"):
            validate_text_length("short", "test", 10, 100)

    def test_validate_text_length_too_long(self):
        """Test text length validation with too long input."""
        with pytest.raises(ValidationError, match="too long"):
            validate_text_length("A" * 150, "test", 10, 100)

    def test_validate_text_length_empty(self):
        """Test text length validation with empty/whitespace input."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_text_length("", "test", 10, 100)
        
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_text_length("   ", "test", 10, 100)


class TestTitleImproverValidation:
    """Tests for TitleImprover input validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.improver = TitleImprover()
        
        # Valid inputs
        self.valid_title = "The Mystery House with Echo"
        self.valid_content = "A" * 100  # Valid length content
        
        # Create minimal valid reviews
        self.valid_title_review = TitleReview(
            title_id="test-001",
            title_text=self.valid_title,
            title_version="v1",
            overall_score=70,
            script_alignment_score=70,
            idea_alignment_score=70,
            engagement_score=70,
            content_id="content-001",
            current_length_chars=len(self.valid_title),
            optimal_length_chars=60,
        )
        self.valid_title_review.improvement_points = []
        
        self.valid_script_review = ScriptReview(
            content_id="content-001",
            script_title=self.valid_title,
            overall_score=70,
            target_audience="Test",
            audience_alignment_score=70,
            target_length=ContentLength.SHORT_FORM,
            current_length_seconds=120,
        )
        self.valid_script_review.improvement_points = []

    def test_validation_empty_title(self):
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError, match="original_title"):
            self.improver.improve_title(
                original_title="",
                content_text=self.valid_content,
                title_review=self.valid_title_review,
                script_review=self.valid_script_review,
            )

    def test_validation_title_too_short(self):
        """Test that too short title is rejected."""
        with pytest.raises(ValidationError, match="too short"):
            self.improver.improve_title(
                original_title="Test",  # Too short
                content_text=self.valid_content,
                title_review=self.valid_title_review,
                script_review=self.valid_script_review,
            )

    def test_validation_title_too_long(self):
        """Test that too long title is rejected."""
        with pytest.raises(ValidationError, match="too long"):
            self.improver.improve_title(
                original_title="A" * 300,  # Too long
                content_text=self.valid_content,
                title_review=self.valid_title_review,
                script_review=self.valid_script_review,
            )

    def test_validation_empty_content(self):
        """Test that empty content is rejected."""
        with pytest.raises(ValidationError, match="content_text"):
            self.improver.improve_title(
                original_title=self.valid_title,
                content_text="",
                title_review=self.valid_title_review,
                script_review=self.valid_script_review,
            )

    def test_validation_content_too_short(self):
        """Test that too short content is rejected."""
        with pytest.raises(ValidationError, match="too short"):
            self.improver.improve_title(
                original_title=self.valid_title,
                content_text="Short",  # Too short
                title_review=self.valid_title_review,
                script_review=self.valid_script_review,
            )

    def test_validation_missing_title_review(self):
        """Test that missing title review is rejected."""
        with pytest.raises(ValidationError, match="title_review is required"):
            self.improver.improve_title(
                original_title=self.valid_title,
                content_text=self.valid_content,
                title_review=None,
                script_review=self.valid_script_review,
            )

    def test_validation_missing_script_review(self):
        """Test that missing script review is rejected."""
        with pytest.raises(ValidationError, match="script_review is required"):
            self.improver.improve_title(
                original_title=self.valid_title,
                content_text=self.valid_content,
                title_review=self.valid_title_review,
                script_review=None,
            )

    def test_validation_invalid_version_format(self):
        """Test that invalid version format is rejected."""
        with pytest.raises(ValidationError, match="must be in format"):
            self.improver.improve_title(
                original_title=self.valid_title,
                content_text=self.valid_content,
                title_review=self.valid_title_review,
                script_review=self.valid_script_review,
                original_version_number="1",  # Invalid format
                new_version_number="v2",
            )

    def test_validation_invalid_version_progression(self):
        """Test that invalid version progression is rejected."""
        with pytest.raises(ValidationError, match="must be greater than"):
            self.improver.improve_title(
                original_title=self.valid_title,
                content_text=self.valid_content,
                title_review=self.valid_title_review,
                script_review=self.valid_script_review,
                original_version_number="v2",
                new_version_number="v1",  # Going backwards
            )

    def test_validation_same_version(self):
        """Test that same version for original and new is rejected."""
        with pytest.raises(ValidationError, match="must be greater than"):
            self.improver.improve_title(
                original_title=self.valid_title,
                content_text=self.valid_content,
                title_review=self.valid_title_review,
                script_review=self.valid_script_review,
                original_version_number="v1",
                new_version_number="v1",  # Same version
            )


class TestTitleImproverErrorHandling:
    """Tests for error handling during improvement process."""

    def setup_method(self):
        """Set up test fixtures."""
        self.improver = TitleImprover()

    def test_malformed_review_object(self):
        """Test handling of malformed review object."""
        # Create object without required fields
        class BadReview:
            pass
        
        bad_review = BadReview()
        
        with pytest.raises(ValidationError, match="missing required field"):
            self.improver.improve_title(
                original_title="Test Title Long Enough",
                content_text="A" * 100,
                title_review=bad_review,
                script_review=bad_review,
            )

    def test_graceful_degradation(self):
        """Test that improvement continues even if some strategies fail."""
        # Create valid but minimal reviews
        title_review = TitleReview(
            title_id="test-001",
            title_text="Test Title",
            title_version="v1",
            overall_score=50,
            script_alignment_score=50,
            idea_alignment_score=50,
            engagement_score=50,
            content_id="content-001",
            current_length_chars=10,
            optimal_length_chars=60,
        )
        title_review.improvement_points = []
        
        script_review = ScriptReview(
            content_id="content-001",
            script_title="Test Title",
            overall_score=50,
            target_audience="Test",
            audience_alignment_score=50,
            target_length=ContentLength.SHORT_FORM,
            current_length_seconds=120,
        )
        script_review.improvement_points = []
        
        # Should complete without raising, even with minimal data
        result = self.improver.improve_title(
            original_title="Test Title Long Enough",
            content_text="A" * 100,
            title_review=title_review,
            script_review=script_review,
        )
        
        assert result is not None
        assert result.new_version.text is not None


class TestExceptionHierarchy:
    """Tests for custom exception types."""

    def test_title_improvement_error_base(self):
        """Test that TitleImprovementError is base exception."""
        err = TitleImprovementError("test")
        assert isinstance(err, Exception)

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from TitleImprovementError."""
        err = ValidationError("test")
        assert isinstance(err, TitleImprovementError)
        assert isinstance(err, Exception)

    def test_improvement_error_inheritance(self):
        """Test that ImprovementError inherits from TitleImprovementError."""
        err = ImprovementError("test")
        assert isinstance(err, TitleImprovementError)
        assert isinstance(err, Exception)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
