"""Tests for MetadataGenerator module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import pytest

from T.Publishing.SEO.Keywords.metadata_generator import (
    MetadataGenerator,
    SEOMetadata,
    generate_seo_metadata,
)


@pytest.fixture
def sample_keywords():
    """Sample keywords for testing."""
    return {
        "primary": ["python", "programming", "learn", "beginners", "tutorial"],
        "secondary": ["coding", "development", "software", "language", "easy"],
        "density": {
            "python": 2.8,
            "programming": 2.1,
            "learn": 1.5,
            "beginners": 1.2,
            "tutorial": 1.0,
        },
    }


@pytest.fixture
def sample_content():
    """Sample content for testing."""
    return {
        "title": "How to Learn Python Programming for Beginners",
        "script": """
        Python is a versatile and powerful programming language that's perfect 
        for beginners. Learning Python programming can open up many career 
        opportunities in software development, data science, and automation.
        
        Python's simple syntax makes it easy to learn. The Python programming 
        language has extensive libraries and a supportive community. Many beginners 
        start with Python because of its readability and straightforward approach.
        
        To learn Python effectively, practice coding regularly and work on real 
        projects. Python programming skills are highly valued in the tech industry.
        The best way to master Python is through hands-on experience and consistent
        practice with real-world applications.
        """,
    }


class TestSEOMetadata:
    """Test SEOMetadata dataclass."""

    def test_create_metadata(self, sample_keywords):
        """Test creating SEOMetadata."""
        metadata = SEOMetadata(
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            meta_description="Learn Python programming from scratch.",
            title_tag="Python Programming Tutorial",
            keyword_density=sample_keywords["density"],
        )

        assert len(metadata.primary_keywords) == 5
        assert len(metadata.secondary_keywords) == 5
        assert metadata.meta_description == "Learn Python programming from scratch."
        assert metadata.title_tag == "Python Programming Tutorial"

    def test_metadata_to_dict(self, sample_keywords):
        """Test converting metadata to dictionary."""
        metadata = SEOMetadata(
            primary_keywords=sample_keywords["primary"], meta_description="Test description"
        )

        result_dict = metadata.to_dict()
        assert isinstance(result_dict, dict)
        assert "primary_keywords" in result_dict
        assert "meta_description" in result_dict

    def test_metadata_repr(self, sample_keywords):
        """Test string representation."""
        metadata = SEOMetadata(
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            quality_score=85,
        )

        repr_str = repr(metadata)
        assert "primary=5" in repr_str
        assert "secondary=5" in repr_str
        assert "quality=85" in repr_str


class TestMetadataGenerator:
    """Test MetadataGenerator class."""

    def test_generator_initialization(self):
        """Test creating a MetadataGenerator."""
        generator = MetadataGenerator(brand_name="TestBrand")

        assert generator.brand_name == "TestBrand"
        assert generator.include_brand is True

    def test_generator_without_brand(self):
        """Test generator without brand name."""
        generator = MetadataGenerator()

        assert generator.brand_name is None
        assert generator.include_brand is True


class TestMetaDescriptionGeneration:
    """Test meta description generation."""

    def test_generate_meta_description(self, sample_content, sample_keywords):
        """Test generating meta description."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert len(metadata.meta_description) > 0
        # Should be within character limits (allow some tolerance)
        assert len(metadata.meta_description) >= 100  # Reasonable minimum

    def test_meta_description_contains_keyword(self, sample_content, sample_keywords):
        """Test that meta description contains at least one primary keyword."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        desc_lower = metadata.meta_description.lower()
        # Should contain at least one primary keyword
        has_keyword = any(kw in desc_lower for kw in sample_keywords["primary"][:3])
        assert has_keyword

    def test_meta_description_length_requirements(self, sample_content, sample_keywords):
        """Test that meta description meets length requirements."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        # Should be close to optimal range (150-160)
        desc_len = len(metadata.meta_description)
        assert 120 <= desc_len <= 180  # Allow some flexibility

    def test_meta_description_with_short_content(self, sample_keywords):
        """Test meta description with short content."""
        generator = MetadataGenerator()

        short_title = "Python Tutorial"
        short_script = "Learn Python programming basics. Python is easy to learn and powerful."

        metadata = generator.generate_metadata(
            title=short_title,
            script=short_script,
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert len(metadata.meta_description) > 0
        assert len(metadata.meta_description) <= 180


class TestTitleTagGeneration:
    """Test title tag generation."""

    def test_generate_title_tag(self, sample_content, sample_keywords):
        """Test generating title tag."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert len(metadata.title_tag) > 0
        assert len(metadata.title_tag) <= MetadataGenerator.TITLE_TAG_MAX + 10

    def test_title_tag_with_brand(self, sample_content, sample_keywords):
        """Test title tag includes brand name."""
        generator = MetadataGenerator(brand_name="TestBrand")
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        # Brand should be in title if included
        assert (
            "TestBrand" in metadata.title_tag
            or len(metadata.title_tag) <= MetadataGenerator.TITLE_TAG_MAX
        )

    def test_title_tag_length_limit(self, sample_keywords):
        """Test that title tag respects length limit."""
        generator = MetadataGenerator(brand_name="MyBrand")

        long_title = "This is a very long title that exceeds the recommended character limit for SEO title tags"

        metadata = generator.generate_metadata(
            title=long_title,
            script="Some content here.",
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        # Should be trimmed to fit
        assert len(metadata.title_tag) <= 70  # Allow some flexibility

    def test_title_tag_short_title(self, sample_keywords):
        """Test title tag with short title."""
        generator = MetadataGenerator(brand_name="Brand")

        metadata = generator.generate_metadata(
            title="Python Basics",
            script="Learn Python programming.",
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert len(metadata.title_tag) > 0
        assert "Python" in metadata.title_tag or "python" in metadata.title_tag.lower()


class TestOpenGraphMetadata:
    """Test Open Graph metadata generation."""

    def test_og_title_generation(self, sample_content, sample_keywords):
        """Test Open Graph title generation."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert len(metadata.og_title) > 0
        assert len(metadata.og_title) <= 70

    def test_og_description_generation(self, sample_content, sample_keywords):
        """Test Open Graph description generation."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert len(metadata.og_description) > 0
        assert len(metadata.og_description) <= MetadataGenerator.OG_DESCRIPTION_MAX + 10

    def test_og_description_longer_than_meta(self, sample_content, sample_keywords):
        """Test that OG description can be longer than meta description."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        # OG description can utilize more space
        assert len(metadata.og_description) <= 210  # Max + some tolerance


class TestQualityScore:
    """Test SEO quality score calculation."""

    def test_quality_score_calculation(self, sample_content, sample_keywords):
        """Test that quality score is calculated."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert 0 <= metadata.quality_score <= 100

    def test_quality_score_with_good_metadata(self, sample_content, sample_keywords):
        """Test quality score with well-formed metadata."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
            related_keywords=["advanced", "tutorial", "guide"],
        )

        # Good metadata should score reasonably high
        assert metadata.quality_score >= 50

    def test_quality_score_components(self, sample_content, sample_keywords):
        """Test that quality score considers multiple factors."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        # Score should reflect:
        # - Meta description length
        # - Title tag length
        # - Keyword presence
        # - OG metadata
        assert metadata.quality_score > 0


class TestRecommendations:
    """Test SEO recommendations generation."""

    def test_recommendations_generated(self, sample_content, sample_keywords):
        """Test that recommendations are generated."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert isinstance(metadata.recommendations, list)
        assert len(metadata.recommendations) > 0

    def test_recommendations_for_short_description(self, sample_keywords):
        """Test recommendations when meta description is too short."""
        generator = MetadataGenerator()

        # Very short script will produce short description
        metadata = generator.generate_metadata(
            title="Test",
            script="Short.",
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        # Should recommend improving description length
        rec_text = " ".join(metadata.recommendations).lower()
        assert "description" in rec_text or len(metadata.meta_description) >= 120

    def test_recommendations_for_long_title(self, sample_keywords):
        """Test recommendations when title tag is too long."""
        generator = MetadataGenerator()

        long_title = "This is an extremely long title that will definitely exceed the SEO recommended character limit"

        metadata = generator.generate_metadata(
            title=long_title,
            script="Content here.",
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        # Should have recommendation about title length if it's too long
        if len(metadata.title_tag) > 60:
            rec_text = " ".join(metadata.recommendations).lower()
            assert "title" in rec_text or "truncate" in rec_text

    def test_positive_recommendations(self, sample_content, sample_keywords):
        """Test positive feedback when everything is good."""
        generator = MetadataGenerator()
        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
            related_keywords=["guide", "tutorial", "examples"],
        )

        # Should have recommendations (could be positive or improvement-focused)
        assert len(metadata.recommendations) > 0
        # If quality is very high (95+), should have positive feedback
        if metadata.quality_score >= 95:
            rec_text = " ".join(metadata.recommendations).lower()
            assert (
                "best practice" in rec_text
                or "meets" in rec_text
                or len(metadata.recommendations) == 1
            )


class TestRelatedKeywords:
    """Test related keywords handling."""

    def test_metadata_with_related_keywords(self, sample_content, sample_keywords):
        """Test that related keywords are included in metadata."""
        generator = MetadataGenerator()

        related = ["advanced", "tutorial", "guide", "tips"]

        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
            related_keywords=related,
        )

        assert metadata.related_keywords == related

    def test_metadata_without_related_keywords(self, sample_content, sample_keywords):
        """Test metadata generation without related keywords."""
        generator = MetadataGenerator()

        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert metadata.related_keywords == []


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_keywords(self, sample_content):
        """Test with empty keyword lists."""
        generator = MetadataGenerator()

        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=[],
            secondary_keywords=[],
            keyword_density={},
        )

        assert isinstance(metadata, SEOMetadata)
        assert len(metadata.meta_description) > 0

    def test_very_short_content(self, sample_keywords):
        """Test with very short content."""
        generator = MetadataGenerator()

        metadata = generator.generate_metadata(
            title="Test",
            script="Test content.",
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert isinstance(metadata, SEOMetadata)
        assert len(metadata.meta_description) > 0

    def test_unicode_content(self, sample_keywords):
        """Test with unicode content."""
        generator = MetadataGenerator()

        metadata = generator.generate_metadata(
            title="Python Programming: 编程教程",
            script="Learn Python with examples. Unicode: café, naïve, 日本語",
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert isinstance(metadata, SEOMetadata)
        assert len(metadata.meta_description) > 0


class TestConvenienceFunction:
    """Test convenience function."""

    def test_generate_seo_metadata_function(self, sample_content, sample_keywords):
        """Test the convenience function."""
        metadata = generate_seo_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
            brand_name="TestBrand",
        )

        assert isinstance(metadata, SEOMetadata)
        assert len(metadata.meta_description) > 0
        assert len(metadata.title_tag) > 0
        assert "TestBrand" in metadata.title_tag or len(metadata.title_tag) <= 60

    def test_function_without_brand(self, sample_content, sample_keywords):
        """Test convenience function without brand name."""
        metadata = generate_seo_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
        )

        assert isinstance(metadata, SEOMetadata)
        assert len(metadata.meta_description) > 0


class TestMetadataQuality:
    """Test overall metadata quality."""

    def test_complete_metadata_structure(self, sample_content, sample_keywords):
        """Test that all metadata fields are populated."""
        generator = MetadataGenerator(brand_name="TestBrand")

        metadata = generator.generate_metadata(
            title=sample_content["title"],
            script=sample_content["script"],
            primary_keywords=sample_keywords["primary"],
            secondary_keywords=sample_keywords["secondary"],
            keyword_density=sample_keywords["density"],
            related_keywords=["guide", "tutorial"],
        )

        # All fields should be populated
        assert len(metadata.primary_keywords) > 0
        assert len(metadata.secondary_keywords) > 0
        assert len(metadata.meta_description) > 0
        assert len(metadata.title_tag) > 0
        assert len(metadata.keyword_density) > 0
        assert len(metadata.related_keywords) > 0
        assert len(metadata.og_title) > 0
        assert len(metadata.og_description) > 0
        assert metadata.quality_score > 0
        assert len(metadata.recommendations) > 0
        assert metadata.generation_timestamp != ""
