"""Tests for script_improver module.

Tests cover:
- Input validation
- Error handling
- Sanitization
- Score validation
- Edge cases
- Performance considerations
"""

import hashlib
import sys
from pathlib import Path

import pytest

# Add paths for imports
current_file = Path(__file__)
src_dir = current_file.parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

from script_improver import (
    ImprovedScript,
    ScriptImprover,
    ScriptVersion,
    generate_deterministic_id,
    safe_divide,
    sanitize_text,
    validate_score,
    validate_text_input,
    MAX_TEXT_LENGTH,
    MAX_TITLE_LENGTH,
    MIN_TEXT_LENGTH,
    MIN_TITLE_LENGTH,
)


class TestInputValidation:
    """Tests for input validation functions."""

    def test_validate_text_input_valid(self):
        """Test validation passes for valid text."""
        text = "This is a valid script text with enough length"
        validate_text_input(text)  # Should not raise

    def test_validate_text_input_none(self):
        """Test validation fails for None."""
        with pytest.raises(ValueError, match="cannot be None"):
            validate_text_input(None)

    def test_validate_text_input_empty(self):
        """Test validation fails for empty string."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_text_input("")

    def test_validate_text_input_whitespace_only(self):
        """Test validation fails for whitespace-only string."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_text_input("   \n  \t  ")

    def test_validate_text_input_wrong_type(self):
        """Test validation fails for non-string type."""
        with pytest.raises(ValueError, match="must be string"):
            validate_text_input(123)

    def test_validate_text_input_too_short(self):
        """Test validation fails for text below minimum length."""
        with pytest.raises(ValueError, match="too short"):
            validate_text_input("Short", min_length=MIN_TEXT_LENGTH)

    def test_validate_text_input_too_long(self):
        """Test validation fails for text above maximum length."""
        long_text = "x" * (MAX_TEXT_LENGTH + 1)
        with pytest.raises(ValueError, match="too long"):
            validate_text_input(long_text)

    def test_validate_text_input_custom_field_name(self):
        """Test validation uses custom field name in error."""
        with pytest.raises(ValueError, match="my_field"):
            validate_text_input("", field_name="my_field")


class TestScoreValidation:
    """Tests for score validation."""

    def test_validate_score_valid(self):
        """Test validation passes for valid score."""
        validate_score(50)  # Should not raise
        validate_score(0)   # Should not raise
        validate_score(100) # Should not raise

    def test_validate_score_invalid_type(self):
        """Test validation fails for non-numeric type."""
        with pytest.raises(ValueError, match="must be numeric"):
            validate_score("50")

    def test_validate_score_below_range(self):
        """Test validation fails for score below 0."""
        with pytest.raises(ValueError, match="must be 0-100"):
            validate_score(-1)

    def test_validate_score_above_range(self):
        """Test validation fails for score above 100."""
        with pytest.raises(ValueError, match="must be 0-100"):
            validate_score(101)

    def test_validate_score_float(self):
        """Test validation accepts float scores."""
        validate_score(75.5)  # Should not raise


class TestTextSanitization:
    """Tests for text sanitization."""

    def test_sanitize_text_removes_null_bytes(self):
        """Test null bytes are removed."""
        text = "Hello\x00World"
        result = sanitize_text(text)
        assert "\x00" not in result
        assert result == "HelloWorld"

    def test_sanitize_text_strips_whitespace(self):
        """Test leading/trailing whitespace is stripped."""
        text = "  Hello World  \n"
        result = sanitize_text(text)
        assert result == "Hello World"

    def test_sanitize_text_truncates_long_text(self):
        """Test long text is truncated to max length."""
        long_text = "x" * (MAX_TEXT_LENGTH + 100)
        result = sanitize_text(long_text, max_length=MAX_TEXT_LENGTH)
        assert len(result) == MAX_TEXT_LENGTH

    def test_sanitize_text_raises_on_non_string(self):
        """Test raises error for non-string input."""
        with pytest.raises(ValueError, match="must be string"):
            sanitize_text(123)


class TestDeterministicId:
    """Tests for deterministic ID generation."""

    def test_generate_deterministic_id_consistency(self):
        """Test same inputs produce same ID."""
        content = "Test script content"
        title = "Test Title"
        version = "v1"
        
        id1 = generate_deterministic_id(content, title, version)
        id2 = generate_deterministic_id(content, title, version)
        
        assert id1 == id2

    def test_generate_deterministic_id_different_inputs(self):
        """Test different inputs produce different IDs."""
        id1 = generate_deterministic_id("content1", "title1", "v1")
        id2 = generate_deterministic_id("content2", "title1", "v1")
        id3 = generate_deterministic_id("content1", "title2", "v1")
        id4 = generate_deterministic_id("content1", "title1", "v2")
        
        assert id1 != id2
        assert id1 != id3
        assert id1 != id4

    def test_generate_deterministic_id_length(self):
        """Test ID has expected length."""
        id_val = generate_deterministic_id("content", "title", "v1")
        assert len(id_val) == 16  # 16 hex characters


class TestSafeDivide:
    """Tests for safe division utility."""

    def test_safe_divide_normal(self):
        """Test normal division works."""
        result = safe_divide(10, 2)
        assert result == 5.0

    def test_safe_divide_by_zero(self):
        """Test division by zero returns default."""
        result = safe_divide(10, 0, default=0.0)
        assert result == 0.0

    def test_safe_divide_custom_default(self):
        """Test custom default is used."""
        result = safe_divide(10, 0, default=-1.0)
        assert result == -1.0

    def test_safe_divide_type_error(self):
        """Test type error returns default."""
        result = safe_divide("10", 2, default=0.0)
        assert result == 0.0


class MockReview:
    """Mock review object for testing."""
    
    def __init__(self, score=70, points=None):
        self.overall_score = score
        self.improvement_points = points or []


class MockImprovementPoint:
    """Mock improvement point."""
    
    def __init__(self, title, description, priority, impact_score, suggested_fix, category="STRUCTURE"):
        self.title = title
        self.description = description
        self.priority = priority
        self.impact_score = impact_score
        self.suggested_fix = suggested_fix
        self.category = category


class TestScriptImprover:
    """Tests for ScriptImprover class."""

    @pytest.fixture
    def improver(self):
        """Create ScriptImprover instance."""
        return ScriptImprover()

    @pytest.fixture
    def valid_review(self):
        """Create valid mock review."""
        points = [
            MockImprovementPoint(
                title="Improve opening",
                description="The opening hook needs work",
                priority="high",
                impact_score=80,
                suggested_fix="Add compelling hook",
                category="STRUCTURE"
            ),
            MockImprovementPoint(
                title="Strengthen conclusion",
                description="The ending needs more impact",
                priority="medium",
                impact_score=60,
                suggested_fix="Add memorable closing",
                category="CONTENT"
            ),
        ]
        return MockReview(score=65, points=points)

    def test_improve_content_valid_input(self, improver, valid_review):
        """Test content improvement with valid inputs."""
        original = "This is a test script. " * 10  # Make it long enough
        title = "Test Title About Scripts"
        
        result = improver.improve_content(
            original_content=original,
            title_text=title,
            script_review=valid_review,
            original_version_number="v1",
            new_version_number="v2",
        )
        
        assert isinstance(result, ImprovedScript)
        assert result.original_version.version_number == "v1"
        assert result.new_version.version_number == "v2"
        assert len(result.new_version.text) > 0

    def test_improve_content_empty_content(self, improver, valid_review):
        """Test improvement fails with empty content."""
        with pytest.raises(ValueError, match="cannot be empty"):
            improver.improve_content(
                original_content="",
                title_text="Test Title",
                script_review=valid_review,
            )

    def test_improve_content_empty_title(self, improver, valid_review):
        """Test improvement fails with empty title."""
        with pytest.raises(ValueError, match="cannot be empty"):
            improver.improve_content(
                original_content="Test script content that is long enough",
                title_text="",
                script_review=valid_review,
            )

    def test_improve_content_none_review(self, improver):
        """Test improvement fails with None review."""
        with pytest.raises(ValueError, match="required"):
            improver.improve_content(
                original_content="Test script content that is long enough",
                title_text="Test Title",
                script_review=None,
            )

    def test_improve_content_too_short(self, improver, valid_review):
        """Test improvement fails with too-short content."""
        with pytest.raises(ValueError, match="too short"):
            improver.improve_content(
                original_content="Short",
                title_text="Test Title",
                script_review=valid_review,
            )

    def test_improve_content_invalid_version(self, improver, valid_review):
        """Test improvement fails with invalid version number."""
        with pytest.raises(ValueError, match="version_number"):
            improver.improve_content(
                original_content="Test script content that is long enough",
                title_text="Test Title",
                script_review=valid_review,
                original_version_number="",
            )

    def test_improve_content_sanitizes_input(self, improver, valid_review):
        """Test content improvement sanitizes inputs."""
        original = "Script with null\x00byte. " * 10
        title = "  Title with whitespace  "
        
        result = improver.improve_content(
            original_content=original,
            title_text=title,
            script_review=valid_review,
        )
        
        # Check null bytes removed
        assert "\x00" not in result.new_version.text
        # Original is sanitized internally

    def test_improve_content_handles_long_text(self, improver, valid_review):
        """Test improvement handles large text without crashing."""
        # Create large but valid text (under limit)
        large_script = "This is a sentence. " * 2000  # ~40k chars
        
        result = improver.improve_content(
            original_content=large_script,
            title_text="Test Title",
            script_review=valid_review,
        )
        
        assert isinstance(result, ImprovedScript)

    def test_extract_improvements_empty(self, improver):
        """Test extracting improvements from empty review."""
        review = MockReview(score=70, points=[])
        improvements = improver._extract_improvements(review)
        assert improvements == []

    def test_extract_improvements_sorts_by_priority(self, improver):
        """Test improvements are sorted by priority and impact."""
        points = [
            MockImprovementPoint("Low priority", "desc", "low", 50, "fix"),
            MockImprovementPoint("High priority", "desc", "high", 80, "fix"),
            MockImprovementPoint("Medium priority", "desc", "medium", 60, "fix"),
        ]
        review = MockReview(score=70, points=points)
        
        improvements = improver._extract_improvements(review)
        
        # High priority should be first
        assert improvements[0]["priority"] == "high"
        assert improvements[1]["priority"] == "medium"
        assert improvements[2]["priority"] == "low"


class TestScriptVersion:
    """Tests for ScriptVersion dataclass."""

    def test_script_version_creation(self):
        """Test creating a script version."""
        version = ScriptVersion(
            version_number="v1",
            text="Test script content",
            review_score=75,
        )
        
        assert version.version_number == "v1"
        assert version.text == "Test script content"
        assert version.review_score == 75

    def test_script_version_to_dict(self):
        """Test converting script version to dict."""
        version = ScriptVersion(
            version_number="v1",
            text="Short",
            review_score=75,
        )
        
        result = version.to_dict()
        
        assert result["version_number"] == "v1"
        assert "text" in result
        assert result["review_score"] == 75

    def test_script_version_to_dict_truncates_long_text(self):
        """Test dict representation truncates long text."""
        long_text = "x" * 1000
        version = ScriptVersion(
            version_number="v1",
            text=long_text,
        )
        
        result = version.to_dict()
        
        # Text should be truncated in preview
        assert len(result["text"]) <= 503  # 500 + "..."
        assert result["full_text_length"] == 1000


class TestImprovedScript:
    """Tests for ImprovedScript dataclass."""

    def test_improved_script_creation(self):
        """Test creating an improved script."""
        original = ScriptVersion("v1", "Original text")
        improved = ScriptVersion("v2", "Improved text")
        
        result = ImprovedScript(
            new_version=improved,
            original_version=original,
            rationale="Made improvements",
        )
        
        assert result.new_version == improved
        assert result.original_version == original
        assert result.rationale == "Made improvements"

    def test_improved_script_to_dict(self):
        """Test converting improved script to dict."""
        original = ScriptVersion("v1", "Original text")
        improved = ScriptVersion("v2", "Improved text")
        
        result = ImprovedScript(
            new_version=improved,
            original_version=original,
            rationale="Made improvements",
        )
        
        dict_result = result.to_dict()
        
        assert "new_version" in dict_result
        assert "original_version" in dict_result
        assert dict_result["rationale"] == "Made improvements"


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    @pytest.fixture
    def improver(self):
        return ScriptImprover()

    def test_improve_content_special_characters(self, improver):
        """Test improvement handles special characters."""
        review = MockReview(score=70, points=[])
        
        script = "Script with special chars: àéîöü ñ 中文 émojis 😀🎉"
        title = "Title with émojis 🎬"
        
        result = improver.improve_content(
            original_content=script,
            title_text=title,
            script_review=review,
        )
        
        assert isinstance(result, ImprovedScript)

    def test_improve_content_unicode(self, improver):
        """Test improvement handles unicode properly."""
        review = MockReview(score=70, points=[])
        
        script = "Script with unicode: ™ © ® € £ ¥"
        title = "Unicode Title ™"
        
        result = improver.improve_content(
            original_content=script,
            title_text=title,
            script_review=review,
        )
        
        assert isinstance(result, ImprovedScript)

    def test_improve_content_multiline(self, improver):
        """Test improvement handles multiline content."""
        review = MockReview(score=70, points=[])
        
        script = """This is line one.
        This is line two.
        
        This is after a blank line.
        """
        title = "Multiline Test"
        
        result = improver.improve_content(
            original_content=script,
            title_text=title,
            script_review=review,
        )
        
        assert isinstance(result, ImprovedScript)
        # Structure should be cleaned
        assert "\n\n\n" not in result.new_version.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
