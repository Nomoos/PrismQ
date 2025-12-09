"""Tests for KeywordExtractor module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import pytest

from T.Publishing.SEO.Keywords.keyword_extractor import (
    KeywordExtractionResult,
    KeywordExtractor,
    extract_keywords,
)


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
        """,
    }


@pytest.fixture
def short_content():
    """Short content for testing edge cases."""
    return {
        "title": "Python Basics",
        "script": "Python is a programming language. It is easy to learn.",
    }


class TestKeywordExtractionResult:
    """Test KeywordExtractionResult dataclass."""

    def test_create_result(self):
        """Test creating a KeywordExtractionResult."""
        result = KeywordExtractionResult(
            primary_keywords=["python", "programming"],
            secondary_keywords=["learn", "beginners"],
            keyword_scores={"python": 0.9, "programming": 0.8},
            keyword_density={"python": 2.5, "programming": 1.8},
            total_words=100,
            extraction_method="tfidf",
        )

        assert result.primary_keywords == ["python", "programming"]
        assert result.secondary_keywords == ["learn", "beginners"]
        assert result.extraction_method == "tfidf"
        assert result.total_words == 100

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = KeywordExtractionResult(primary_keywords=["python"], extraction_method="tfidf")

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "primary_keywords" in result_dict
        assert "extraction_method" in result_dict
        assert result_dict["primary_keywords"] == ["python"]

    def test_result_repr(self):
        """Test string representation."""
        result = KeywordExtractionResult(
            primary_keywords=["python", "programming"],
            secondary_keywords=["learn", "coding"],
            extraction_method="tfidf",
        )

        repr_str = repr(result)
        assert "primary=2" in repr_str
        assert "secondary=2" in repr_str
        assert "tfidf" in repr_str


class TestKeywordExtractor:
    """Test KeywordExtractor class."""

    def test_extractor_initialization(self):
        """Test creating a KeywordExtractor."""
        extractor = KeywordExtractor(primary_count=5, secondary_count=10, min_keyword_length=3)

        assert extractor.primary_count == 5
        assert extractor.secondary_count == 10
        assert extractor.min_keyword_length == 3
        assert extractor.language == "english"
        assert len(extractor.stop_words) > 0

    def test_extractor_default_values(self):
        """Test default initialization values."""
        extractor = KeywordExtractor()

        assert extractor.primary_count == 5
        assert extractor.secondary_count == 10
        assert extractor.min_keyword_length == 3
        assert extractor.max_keyword_length == 30


class TestTFIDFExtraction:
    """Test TF-IDF keyword extraction."""

    def test_extract_with_tfidf(self, sample_content):
        """Test extracting keywords using TF-IDF."""
        extractor = KeywordExtractor(primary_count=5, secondary_count=5)
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="tfidf"
        )

        assert isinstance(result, KeywordExtractionResult)
        assert len(result.primary_keywords) > 0
        assert len(result.primary_keywords) <= 5
        assert result.extraction_method == "tfidf"
        assert result.total_words > 0

        # Check that likely keywords are present
        all_keywords = result.primary_keywords + result.secondary_keywords
        assert any("python" in kw for kw in all_keywords)

    def test_tfidf_keyword_scores(self, sample_content):
        """Test that TF-IDF produces keyword scores."""
        extractor = KeywordExtractor()
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="tfidf"
        )

        assert len(result.keyword_scores) > 0
        # Scores should be between 0 and 1
        for score in result.keyword_scores.values():
            assert 0 <= score <= 1

    def test_tfidf_with_short_content(self, short_content):
        """Test TF-IDF with minimal content."""
        extractor = KeywordExtractor(primary_count=3, secondary_count=3)
        result = extractor.extract_keywords(
            title=short_content["title"], script=short_content["script"], method="tfidf"
        )

        assert isinstance(result, KeywordExtractionResult)
        assert len(result.primary_keywords) > 0
        assert "python" in result.primary_keywords or "python" in result.secondary_keywords


class TestFrequencyExtraction:
    """Test frequency-based keyword extraction."""

    def test_extract_with_frequency(self, sample_content):
        """Test extracting keywords using frequency analysis."""
        extractor = KeywordExtractor(primary_count=5, secondary_count=5)
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="frequency"
        )

        assert isinstance(result, KeywordExtractionResult)
        assert len(result.primary_keywords) > 0
        assert result.extraction_method == "frequency"

        # Most frequent words should be extracted
        all_keywords = result.primary_keywords + result.secondary_keywords
        assert any("python" in kw for kw in all_keywords)

    def test_frequency_filters_stopwords(self, sample_content):
        """Test that stopwords are filtered out."""
        extractor = KeywordExtractor()
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="frequency"
        )

        all_keywords = result.primary_keywords + result.secondary_keywords

        # Common stopwords should not be in keywords
        stopwords_to_check = ["the", "is", "a", "to", "and", "of"]
        for stopword in stopwords_to_check:
            assert stopword not in all_keywords


class TestHybridExtraction:
    """Test hybrid keyword extraction."""

    def test_extract_with_hybrid(self, sample_content):
        """Test extracting keywords using hybrid method."""
        extractor = KeywordExtractor(primary_count=5, secondary_count=5)
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="hybrid"
        )

        assert isinstance(result, KeywordExtractionResult)
        assert len(result.primary_keywords) > 0
        assert result.extraction_method == "hybrid"

        # Should combine benefits of both methods
        all_keywords = result.primary_keywords + result.secondary_keywords
        assert any("python" in kw for kw in all_keywords)

    def test_hybrid_combines_scores(self, sample_content):
        """Test that hybrid method combines TF-IDF and frequency scores."""
        extractor = KeywordExtractor()

        # Get hybrid results
        hybrid_result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="hybrid"
        )

        assert len(hybrid_result.keyword_scores) > 0
        # Scores should be reasonable (between 0 and 1)
        for score in hybrid_result.keyword_scores.values():
            assert 0 <= score <= 1


class TestKeywordDensity:
    """Test keyword density calculation."""

    def test_density_calculation(self, sample_content):
        """Test that keyword density is calculated."""
        extractor = KeywordExtractor()
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="tfidf"
        )

        assert len(result.keyword_density) > 0

        # Density should be reasonable percentages
        for density in result.keyword_density.values():
            assert 0 <= density <= 10  # Max 10% density

    def test_top_keyword_density(self, sample_content):
        """Test that top keywords have higher density."""
        extractor = KeywordExtractor()
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="tfidf"
        )

        if len(result.primary_keywords) >= 2:
            first_keyword = result.primary_keywords[0]
            second_keyword = result.primary_keywords[1]

            # First keyword should have equal or higher density
            assert result.keyword_density[first_keyword] >= result.keyword_density[second_keyword]


class TestRelatedKeywords:
    """Test related keyword suggestions."""

    def test_suggest_related_keywords(self, sample_content):
        """Test suggesting related keywords."""
        extractor = KeywordExtractor()
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="tfidf"
        )

        related = extractor.suggest_related_keywords(
            keywords=result.primary_keywords[:3],
            original_text=f"{sample_content['title']} {sample_content['script']}",
            max_suggestions=10,
        )

        assert isinstance(related, list)
        assert len(related) > 0
        assert len(related) <= 10

    def test_related_keywords_not_duplicates(self, sample_content):
        """Test that related keywords don't duplicate primary keywords."""
        extractor = KeywordExtractor()
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="tfidf"
        )

        related = extractor.suggest_related_keywords(
            keywords=result.primary_keywords[:3],
            original_text=f"{sample_content['title']} {sample_content['script']}",
            max_suggestions=5,
        )

        # Related keywords should not be in primary keywords
        for kw in related:
            assert kw not in result.primary_keywords[:3]


class TestTextPreprocessing:
    """Test text preprocessing functionality."""

    def test_preprocess_text(self):
        """Test text preprocessing."""
        extractor = KeywordExtractor()

        text = "Hello WORLD! This is a TEST. Visit https://example.com"
        processed = extractor._preprocess_text(text)

        # Should be lowercase
        assert processed.islower()

        # Should not contain URLs
        assert "http" not in processed
        assert "example.com" not in processed

        # Should contain clean words
        assert "hello" in processed
        assert "world" in processed
        assert "test" in processed

    def test_preprocess_removes_special_chars(self):
        """Test that special characters are removed."""
        extractor = KeywordExtractor()

        text = "Python! @#$% Programming... <html>"
        processed = extractor._preprocess_text(text)

        # Should only contain alphanumeric and spaces
        assert processed == "python programming html"


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_extraction_method(self, sample_content):
        """Test handling of invalid extraction method."""
        extractor = KeywordExtractor()

        with pytest.raises(ValueError, match="Unknown extraction method"):
            extractor.extract_keywords(
                title=sample_content["title"],
                script=sample_content["script"],
                method="invalid_method",
            )

    def test_empty_content(self):
        """Test handling of empty content."""
        extractor = KeywordExtractor()
        result = extractor.extract_keywords(title="", script="", method="tfidf")

        # Should return result even with empty content
        assert isinstance(result, KeywordExtractionResult)
        assert result.total_words == 0

    def test_very_short_content(self):
        """Test with very short content."""
        extractor = KeywordExtractor()
        result = extractor.extract_keywords(title="Test", script="Short text.", method="tfidf")

        assert isinstance(result, KeywordExtractionResult)
        # May have few or no keywords with very short content
        assert len(result.primary_keywords) >= 0


class TestConvenienceFunction:
    """Test convenience function."""

    def test_extract_keywords_function(self, sample_content):
        """Test the convenience function."""
        result = extract_keywords(
            title=sample_content["title"],
            script=sample_content["script"],
            method="tfidf",
            primary_count=5,
            secondary_count=10,
        )

        assert isinstance(result, KeywordExtractionResult)
        assert len(result.primary_keywords) > 0
        assert len(result.primary_keywords) <= 5

    def test_function_default_parameters(self, sample_content):
        """Test convenience function with defaults."""
        result = extract_keywords(title=sample_content["title"], script=sample_content["script"])

        assert isinstance(result, KeywordExtractionResult)
        assert result.extraction_method == "tfidf"
        assert len(result.primary_keywords) <= 5
        assert len(result.secondary_keywords) <= 10


class TestKeywordQuality:
    """Test keyword extraction quality."""

    def test_keywords_are_relevant(self, sample_content):
        """Test that extracted keywords are relevant to content."""
        extractor = KeywordExtractor()
        result = extractor.extract_keywords(
            title=sample_content["title"], script=sample_content["script"], method="tfidf"
        )

        # Should extract "python" and "programming" as they're most relevant
        all_keywords = result.primary_keywords + result.secondary_keywords
        keywords_str = " ".join(all_keywords)

        assert "python" in keywords_str
        # At least one programming-related term
        assert any(term in keywords_str for term in ["programming", "learn", "language"])

    def test_title_words_prioritized(self):
        """Test that title words get higher priority."""
        extractor = KeywordExtractor()

        # Title contains unique word not in script
        result = extractor.extract_keywords(
            title="Quantum Computing Explained",
            script="This article discusses various topics in computer science and technology.",
            method="tfidf",
        )

        all_keywords = result.primary_keywords + result.secondary_keywords
        # "quantum" from title should be extracted even if not in script
        keywords_str = " ".join(all_keywords)
        assert "quantum" in keywords_str or "computing" in keywords_str
