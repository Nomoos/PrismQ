"""Tests for TagGenerator module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import pytest
from T.Publishing.SEO.Taxonomy.tag_generator import (
    TagGenerator,
    TagGenerationResult,
    generate_tags
)
from T.Publishing.SEO.Taxonomy.taxonomy_config import (
    TaxonomyConfig,
    DEFAULT_TAXONOMY
)


@pytest.fixture
def sample_content():
    """Sample content for testing."""
    return {
        "title": "Introduction to Machine Learning and AI",
        "script": """
        Machine learning is a subset of artificial intelligence that enables 
        computers to learn from data. Python is the most popular programming 
        language for machine learning due to its extensive libraries like 
        scikit-learn and TensorFlow.
        
        AI and machine learning are transforming industries from healthcare 
        to finance. Deep learning, a subset of machine learning, uses neural 
        networks to solve complex problems. Data science professionals use 
        these technologies to build predictive models.
        """,
        "keywords": ["machine learning", "AI", "python", "data science"]
    }


@pytest.fixture
def tech_content():
    """Tech-focused content for testing."""
    return {
        "title": "Building Modern Web Applications with React and Node.js",
        "script": """
        React is a popular JavaScript library for building user interfaces.
        Combined with Node.js for the backend, developers can create full-stack 
        web applications using JavaScript throughout. This modern web development 
        approach enables rapid development and scalable applications.
        """,
        "keywords": ["react", "nodejs", "javascript", "web development"]
    }


class TestTagGenerationResult:
    """Test TagGenerationResult dataclass."""
    
    def test_create_result(self):
        """Test creating a TagGenerationResult."""
        result = TagGenerationResult(
            tags=["python", "programming", "ai"],
            relevance_scores={"python": 0.9, "programming": 0.85, "ai": 0.88},
            source_breakdown={"keywords": 2, "content": 1},
            duplicates_removed=3,
            generation_method="semantic"
        )
        
        assert result.tags == ["python", "programming", "ai"]
        assert result.relevance_scores["python"] == 0.9
        assert result.duplicates_removed == 3
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = TagGenerationResult(
            tags=["test"],
            relevance_scores={"test": 0.8}
        )
        
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "tags" in result_dict
        assert result_dict["tags"] == ["test"]
    
    def test_result_repr(self):
        """Test string representation."""
        result = TagGenerationResult(
            tags=["a", "b", "c"],
            duplicates_removed=2
        )
        
        repr_str = repr(result)
        assert "tags=3" in repr_str
        assert "duplicates_removed=2" in repr_str


class TestTagGenerator:
    """Test TagGenerator class."""
    
    def test_generator_initialization(self):
        """Test creating a TagGenerator."""
        generator = TagGenerator()
        assert generator.config is not None
        assert generator.config.max_tags == 10
        
        # Test with custom config
        custom_config = TaxonomyConfig(
            categories={"Test": ["Sub1"]},
            max_tags=5
        )
        generator = TagGenerator(config=custom_config)
        assert generator.config.max_tags == 5
    
    def test_generate_tags_basic(self, sample_content):
        """Test basic tag generation."""
        generator = TagGenerator()
        result = generator.generate_tags(
            title=sample_content["title"],
            script=sample_content["script"],
            base_keywords=sample_content["keywords"]
        )
        
        assert isinstance(result, TagGenerationResult)
        assert len(result.tags) > 0
        assert len(result.tags) <= generator.config.max_tags
        assert all(isinstance(tag, str) for tag in result.tags)
    
    def test_generate_tags_with_keywords(self, sample_content):
        """Test tag generation with keywords."""
        generator = TagGenerator()
        result = generator.generate_tags(
            title=sample_content["title"],
            script=sample_content["script"],
            base_keywords=sample_content["keywords"]
        )
        
        # Check that some keywords appear in tags
        tags_lower = [tag.lower() for tag in result.tags]
        assert any("machine learning" in tag or "machine" in tags_lower for tag in tags_lower)
    
    def test_generate_tags_without_keywords(self, sample_content):
        """Test tag generation without keywords."""
        generator = TagGenerator()
        result = generator.generate_tags(
            title=sample_content["title"],
            script=sample_content["script"],
            base_keywords=None
        )
        
        assert isinstance(result, TagGenerationResult)
        assert len(result.tags) > 0
    
    def test_relevance_scores(self, sample_content):
        """Test that relevance scores are valid."""
        generator = TagGenerator()
        result = generator.generate_tags(
            title=sample_content["title"],
            script=sample_content["script"],
            base_keywords=sample_content["keywords"]
        )
        
        # All scores should be between 0 and 1
        for tag, score in result.relevance_scores.items():
            assert 0 <= score <= 1
            # All returned tags should meet min_relevance threshold
            assert score >= generator.config.min_relevance
    
    def test_deduplication(self):
        """Test that similar tags are deduplicated."""
        generator = TagGenerator()
        
        # Content with similar/duplicate terms
        result = generator.generate_tags(
            title="Programming in Python and Python Programming",
            script="Learn Python programming. Python is great for programming.",
            base_keywords=["python", "programming", "python programming"]
        )
        
        # Check that we don't have too many similar tags
        tags_lower = [tag.lower() for tag in result.tags]
        
        # Should have deduplicated similar terms
        # Count variations of "python" and "programming"
        python_count = sum(1 for tag in tags_lower if "python" in tag)
        programming_count = sum(1 for tag in tags_lower if "programming" in tag)
        
        # Should not have excessive duplicates
        assert python_count <= 2
        assert programming_count <= 2
    
    def test_tag_validation(self):
        """Test tag validation logic."""
        generator = TagGenerator()
        
        # Test valid tags
        assert generator._is_valid_tag("python")
        assert generator._is_valid_tag("machine learning")
        assert generator._is_valid_tag("ai")
        
        # Test invalid tags
        assert not generator._is_valid_tag("")  # Empty
        assert not generator._is_valid_tag("a")  # Too short
        assert not generator._is_valid_tag("the")  # Stop word
        assert not generator._is_valid_tag("x" * 35)  # Too long
    
    def test_normalize_tag(self):
        """Test tag normalization."""
        generator = TagGenerator()
        
        assert generator._normalize_tag("Python") == "python"
        assert generator._normalize_tag("Machine Learning") == "machine learning"
        assert generator._normalize_tag("  AI  ") == "ai"
        assert generator._normalize_tag("Web-Dev") == "web-dev"
        assert generator._normalize_tag("C++") == "c"  # Special chars removed
    
    def test_source_breakdown(self, sample_content):
        """Test source breakdown tracking."""
        generator = TagGenerator()
        result = generator.generate_tags(
            title=sample_content["title"],
            script=sample_content["script"],
            base_keywords=sample_content["keywords"]
        )
        
        assert "keywords" in result.source_breakdown
        assert "content" in result.source_breakdown
        assert "semantic" in result.source_breakdown
        
        # Should have some tags from keywords
        assert result.source_breakdown["keywords"] > 0
    
    def test_max_tags_limit(self):
        """Test that max_tags limit is respected."""
        config = TaxonomyConfig(
            categories={"Test": []},
            max_tags=5
        )
        generator = TagGenerator(config=config)
        
        result = generator.generate_tags(
            title="Python Programming JavaScript Web Development AI Machine Learning Data Science",
            script="Python JavaScript programming coding development software engineering",
            base_keywords=["python", "javascript", "ai", "data", "ml"]
        )
        
        assert len(result.tags) <= 5


class TestGenerateTagsFunction:
    """Test convenience function."""
    
    def test_generate_tags_function(self, sample_content):
        """Test the convenience function."""
        result = generate_tags(
            title=sample_content["title"],
            script=sample_content["script"],
            keywords=sample_content["keywords"]
        )
        
        assert isinstance(result, TagGenerationResult)
        assert len(result.tags) > 0
    
    def test_generate_tags_with_custom_config(self):
        """Test with custom configuration."""
        config = TaxonomyConfig(
            categories={"Tech": []},
            min_relevance=0.8,
            max_tags=3
        )
        
        result = generate_tags(
            title="Python Programming",
            script="Learn Python programming basics",
            keywords=["python"],
            config=config
        )
        
        assert len(result.tags) <= 3
        assert all(score >= 0.8 for score in result.relevance_scores.values())


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_content(self):
        """Test with empty content."""
        generator = TagGenerator()
        result = generator.generate_tags(
            title="",
            script="",
            base_keywords=None
        )
        
        # Should handle gracefully
        assert isinstance(result, TagGenerationResult)
    
    def test_short_content(self):
        """Test with very short content."""
        generator = TagGenerator()
        result = generator.generate_tags(
            title="AI",
            script="Artificial Intelligence",
            base_keywords=["ai"]
        )
        
        assert isinstance(result, TagGenerationResult)
        assert len(result.tags) > 0
    
    def test_special_characters(self):
        """Test content with special characters."""
        generator = TagGenerator()
        result = generator.generate_tags(
            title="C++ & Python!",
            script="Learn C++ and Python programming @home.",
            base_keywords=None
        )
        
        assert isinstance(result, TagGenerationResult)
        # Should handle special characters gracefully
    
    def test_unicode_content(self):
        """Test content with unicode characters."""
        generator = TagGenerator()
        result = generator.generate_tags(
            title="Programmation Python",
            script="Apprendre Python et développement",
            base_keywords=None
        )
        
        assert isinstance(result, TagGenerationResult)
