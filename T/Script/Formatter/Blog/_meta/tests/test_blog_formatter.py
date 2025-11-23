"""Tests for Blog Formatter module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from T.Script.Formatter.Blog import (
    BlogFormatter,
    BlogFormattedContent,
    BlogMetadata,
    format_blog,
    export_for_platform
)


@pytest.fixture
def sample_short_script():
    """Sample short script for testing."""
    return """This is a story about innovation. Innovation changes the world. 
    We see it everywhere. From technology to art. From science to culture. 
    Innovation drives progress. It creates opportunities. It solves problems. 
    Let's explore this fascinating topic together."""


@pytest.fixture
def sample_medium_script():
    """Sample medium-length script for testing."""
    return """This is a comprehensive story about innovation and how it shapes our world.
    
    Innovation is not just about new technologies. It's about new ways of thinking. 
    It's about challenging assumptions and breaking boundaries. Throughout history, 
    innovation has been the driving force behind human progress.
    
    Consider the industrial revolution. It transformed how we manufacture goods. 
    It changed how we live and work. The same is true for the digital revolution. 
    The internet connected billions of people. It created new industries. It 
    disrupted old ones.
    
    Today, we stand at the threshold of new innovations. Artificial intelligence 
    is reshaping industries. Renewable energy is transforming how we power our world. 
    Biotechnology is revolutionizing healthcare. These innovations will define our future.
    
    But innovation comes with challenges. We must consider ethical implications. 
    We must ensure equitable access. We must balance progress with sustainability. 
    These are the questions we must answer.
    
    The future belongs to those who innovate. Those who dare to dream. Those who 
    are willing to take risks. Innovation is not just about technology. It's about 
    human creativity and determination."""


@pytest.fixture
def sample_long_script():
    """Sample long script for testing (2000+ words)."""
    return """Innovation: The Engine of Human Progress

    Throughout human history, innovation has been the primary driver of progress and 
    transformation. From the earliest stone tools to modern artificial intelligence, 
    our species has consistently demonstrated an remarkable capacity to imagine, create, 
    and implement new solutions to old problems.

    """ + """
    Innovation is fundamentally about problem-solving. Every great innovation starts 
    with a problem that needs solving. Sometimes the problem is obvious. Other times 
    it's subtle. But recognizing the problem is the first step toward innovation.
    
    Consider the invention of the wheel. Someone recognized that moving heavy objects 
    was difficult. They imagined a circular device that could roll. This simple insight 
    changed everything. Transportation became easier. Commerce expanded. Civilizations grew.
    
    Fast forward to the modern era. We face different problems. Climate change threatens 
    our planet. Diseases challenge our health. Inequality divides our societies. But the 
    principles of innovation remain the same. Identify the problem. Imagine solutions. 
    Test and iterate. Scale what works.
    
    """ * 10  # Repeat to make it longer


class TestBlogMetadata:
    """Test BlogMetadata dataclass."""
    
    def test_create_metadata(self):
        """Test creating blog metadata."""
        metadata = BlogMetadata(
            excerpt="This is an excerpt",
            reading_time="5 min read",
            word_count=1000,
            char_count=5000
        )
        
        assert metadata.excerpt == "This is an excerpt"
        assert metadata.reading_time == "5 min read"
        assert metadata.word_count == 1000
        assert metadata.char_count == 5000
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = BlogMetadata(
            excerpt="Test excerpt",
            reading_time="3 min read",
            word_count=500
        )
        
        data = metadata.to_dict()
        
        assert data["excerpt"] == "Test excerpt"
        assert data["reading_time"] == "3 min read"
        assert data["word_count"] == 500


class TestBlogFormattedContent:
    """Test BlogFormattedContent dataclass."""
    
    def test_create_formatted_content(self):
        """Test creating formatted content."""
        metadata = BlogMetadata(reading_time="5 min read")
        content = BlogFormattedContent(
            content_id="test-001",
            title="Test Title",
            formatted_content="# Test Title\n\nContent here",
            metadata=metadata
        )
        
        assert content.content_id == "test-001"
        assert content.title == "Test Title"
        assert content.format_type == "markdown"
        assert content.success is True
    
    def test_formatted_content_to_dict(self):
        """Test converting formatted content to dictionary."""
        metadata = BlogMetadata(reading_time="5 min read")
        content = BlogFormattedContent(
            content_id="test-001",
            title="Test",
            formatted_content="Content",
            metadata=metadata
        )
        
        data = content.to_dict()
        
        assert data["content_id"] == "test-001"
        assert "metadata" in data
        assert data["metadata"]["reading_time"] == "5 min read"


class TestBlogFormatter:
    """Test BlogFormatter class."""
    
    def test_formatter_initialization(self):
        """Test initializing the formatter."""
        formatter = BlogFormatter()
        
        assert formatter is not None
        assert formatter.READING_SPEED_WPM == 225
    
    def test_format_short_blog(self, sample_short_script):
        """Test formatting a short blog post."""
        formatter = BlogFormatter()
        
        result = formatter.format_blog(
            script=sample_short_script,
            title="Innovation Story",
            content_id="test-001"
        )
        
        assert result.success is True
        assert result.title == "Innovation Story"
        assert len(result.errors) == 0
        assert "# Innovation Story" in result.formatted_content
        assert result.metadata.word_count > 0
    
    def test_format_medium_blog(self, sample_medium_script):
        """Test formatting a medium-length blog post."""
        formatter = BlogFormatter()
        
        result = formatter.format_blog(
            script=sample_medium_script,
            title="Innovation and Progress",
            content_id="test-002",
            format_type="markdown"
        )
        
        assert result.success is True
        assert result.metadata.word_count > 100
        assert result.metadata.paragraph_count > 3
        assert result.metadata.reading_time is not None
        assert "min read" in result.metadata.reading_time
    
    def test_format_with_html(self, sample_medium_script):
        """Test formatting as HTML."""
        formatter = BlogFormatter()
        
        result = formatter.format_blog(
            script=sample_medium_script,
            title="HTML Test",
            content_id="test-003",
            format_type="html"
        )
        
        assert result.success is True
        assert result.format_type == "html"
        assert "<h1>HTML Test</h1>" in result.formatted_content
        assert "<p>" in result.formatted_content
        assert "</p>" in result.formatted_content
    
    def test_format_with_cta(self, sample_medium_script):
        """Test formatting with CTA sections."""
        formatter = BlogFormatter()
        
        cta_text = "Subscribe to our newsletter for more insights!"
        
        result = formatter.format_blog(
            script=sample_medium_script,
            title="CTA Test",
            content_id="test-004",
            cta_text=cta_text
        )
        
        assert result.success is True
        assert cta_text in result.formatted_content
    
    def test_reading_time_calculation(self):
        """Test reading time calculation."""
        formatter = BlogFormatter()
        
        # Test various word counts
        assert formatter._calculate_reading_time(225) == "1 min read"
        assert formatter._calculate_reading_time(450) == "2 min read"
        assert formatter._calculate_reading_time(675) == "3 min read"
        assert formatter._calculate_reading_time(1125) == "5 min read"
    
    def test_excerpt_generation(self, sample_medium_script):
        """Test excerpt generation."""
        formatter = BlogFormatter()
        
        result = formatter.format_blog(
            script=sample_medium_script,
            title="Excerpt Test",
            content_id="test-005"
        )
        
        assert len(result.metadata.excerpt) > 0
        assert len(result.metadata.excerpt) <= 200
    
    def test_paragraph_formatting(self, sample_medium_script):
        """Test paragraph formatting with sentence limits."""
        formatter = BlogFormatter()
        
        result = formatter.format_blog(
            script=sample_medium_script,
            title="Paragraph Test",
            content_id="test-006"
        )
        
        # Check that content is formatted with proper paragraphs
        assert result.metadata.paragraph_count > 0
    
    def test_heading_hierarchy(self, sample_medium_script):
        """Test heading hierarchy (H1, H2, H3)."""
        formatter = BlogFormatter()
        
        result = formatter.format_blog(
            script=sample_medium_script,
            title="Heading Test",
            content_id="test-007",
            format_type="markdown"
        )
        
        # Check for H1 (title)
        assert "# Heading Test" in result.formatted_content
        
        # Check for H2 (sections)
        assert "## " in result.formatted_content


class TestPlatformSpecific:
    """Test platform-specific formatting."""
    
    def test_medium_format(self, sample_medium_script):
        """Test Medium-specific formatting."""
        result = export_for_platform(
            script=sample_medium_script,
            title="Medium Test",
            content_id="test-101",
            platform="medium",
            format_type="markdown"
        )
        
        assert result.success is True
        assert result.platform == "medium"
        # Check for Medium-specific elements
        assert "Import this to Medium" in result.formatted_content or "---" in result.formatted_content
    
    def test_wordpress_format(self, sample_medium_script):
        """Test WordPress-specific formatting."""
        result = export_for_platform(
            script=sample_medium_script,
            title="WordPress Test",
            content_id="test-102",
            platform="wordpress",
            format_type="html"
        )
        
        assert result.success is True
        assert result.platform == "wordpress"
        # Check for WordPress-specific elements
        assert "WordPress" in result.formatted_content or "wp:" in result.formatted_content
    
    def test_ghost_format(self, sample_medium_script):
        """Test Ghost-specific formatting."""
        result = export_for_platform(
            script=sample_medium_script,
            title="Ghost Test",
            content_id="test-103",
            platform="ghost",
            format_type="markdown"
        )
        
        assert result.success is True
        assert result.platform == "ghost"
        # Check for Ghost-specific elements (frontmatter)
        assert "---" in result.formatted_content or "title:" in result.formatted_content
    
    def test_generic_format(self, sample_medium_script):
        """Test generic platform formatting."""
        result = export_for_platform(
            script=sample_medium_script,
            title="Generic Test",
            content_id="test-104",
            platform="generic",
            format_type="markdown"
        )
        
        assert result.success is True
        assert result.platform == "generic"


class TestConvenienceFunction:
    """Test convenience function."""
    
    def test_format_blog_function(self, sample_short_script):
        """Test format_blog convenience function."""
        result = format_blog(
            script=sample_short_script,
            title="Function Test",
            content_id="test-201"
        )
        
        assert result.success is True
        assert result.title == "Function Test"
        assert result.content_id == "test-201"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_script(self):
        """Test formatting empty script."""
        formatter = BlogFormatter()
        
        result = formatter.format_blog(
            script="",
            title="Empty Test",
            content_id="test-301"
        )
        
        # Should handle gracefully
        assert result.content_id == "test-301"
    
    def test_very_short_script(self):
        """Test with very short script."""
        formatter = BlogFormatter()
        
        result = formatter.format_blog(
            script="Innovation.",
            title="Short Test",
            content_id="test-302"
        )
        
        assert result.success is True
        assert result.metadata.word_count >= 1
    
    def test_invalid_format_type(self):
        """Test with invalid format type."""
        formatter = BlogFormatter()
        
        result = formatter.format_blog(
            script="Test content",
            title="Invalid Format",
            content_id="test-303",
            format_type="invalid"
        )
        
        assert result.success is False
        assert len(result.errors) > 0
    
    def test_special_characters(self):
        """Test with special characters in content."""
        formatter = BlogFormatter()
        
        script = "Test with <html> & special 'quotes' and \"more quotes\""
        
        result = formatter.format_blog(
            script=script,
            title="Special Chars",
            content_id="test-304",
            format_type="html"
        )
        
        assert result.success is True
        # HTML should be escaped
        assert "&lt;" in result.formatted_content or "<html>" not in result.formatted_content


class TestScriptLengthVariations:
    """Test with various script lengths as per acceptance criteria."""
    
    def test_500_word_script(self):
        """Test with ~500 word script."""
        script = " ".join(["word"] * 500)
        
        formatter = BlogFormatter()
        result = formatter.format_blog(
            script=script,
            title="500 Words",
            content_id="test-401"
        )
        
        assert result.success is True
        assert 450 <= result.metadata.word_count <= 550
        assert "2 min read" in result.metadata.reading_time or "3 min read" in result.metadata.reading_time
    
    def test_1000_word_script(self):
        """Test with ~1000 word script."""
        script = " ".join(["word"] * 1000)
        
        formatter = BlogFormatter()
        result = formatter.format_blog(
            script=script,
            title="1000 Words",
            content_id="test-402"
        )
        
        assert result.success is True
        assert 950 <= result.metadata.word_count <= 1050
        assert "4 min read" in result.metadata.reading_time or "5 min read" in result.metadata.reading_time
    
    def test_2000_word_script(self):
        """Test with ~2000 word script."""
        script = " ".join(["word"] * 2000)
        
        formatter = BlogFormatter()
        result = formatter.format_blog(
            script=script,
            title="2000 Words",
            content_id="test-403"
        )
        
        assert result.success is True
        assert 1950 <= result.metadata.word_count <= 2050
        assert "9 min read" in result.metadata.reading_time or "8 min read" in result.metadata.reading_time


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
