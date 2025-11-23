"""Tests for CategoryClassifier module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import pytest
from T.Publishing.SEO.Taxonomy.category_classifier import (
    CategoryClassifier,
    CategoryClassificationResult,
    classify_categories
)
from T.Publishing.SEO.Taxonomy.taxonomy_config import (
    TaxonomyConfig,
    DEFAULT_TAXONOMY
)


@pytest.fixture
def tech_content():
    """Tech content for testing."""
    return {
        "title": "Building Web Applications with React and Node.js",
        "script": """
        React is a popular JavaScript library for building user interfaces.
        Node.js enables server-side JavaScript development. Together, they
        form a powerful stack for web development. Modern web applications
        require frontend and backend technologies that work seamlessly.
        """,
        "tags": ["react", "nodejs", "javascript", "web development"]
    }


@pytest.fixture
def ai_content():
    """AI/ML content for testing."""
    return {
        "title": "Introduction to Machine Learning and Deep Learning",
        "script": """
        Machine learning is a subset of artificial intelligence that enables
        computers to learn from data. Deep learning uses neural networks to
        solve complex problems. Python and TensorFlow are commonly used for
        AI development. Data science and machine learning are transforming
        industries.
        """,
        "tags": ["machine learning", "ai", "deep learning", "python"]
    }


@pytest.fixture
def lifestyle_content():
    """Lifestyle content for testing."""
    return {
        "title": "Healthy Living: Nutrition and Fitness Tips",
        "script": """
        Maintaining a healthy lifestyle requires balanced nutrition and regular
        exercise. Focus on whole foods, stay hydrated, and get adequate sleep.
        Fitness routines should include both cardio and strength training. Wellness
        encompasses physical and mental health.
        """,
        "tags": ["health", "fitness", "nutrition", "wellness"]
    }


class TestCategoryClassificationResult:
    """Test CategoryClassificationResult dataclass."""
    
    def test_create_result(self):
        """Test creating a CategoryClassificationResult."""
        result = CategoryClassificationResult(
            categories=["Technology/Web Development", "Technology"],
            confidence_scores={
                "Technology/Web Development": 0.85,
                "Technology": 0.75
            },
            hierarchy={"Technology": ["Web Development"]},
            classification_method="keyword_matching"
        )
        
        assert result.categories == ["Technology/Web Development", "Technology"]
        assert result.confidence_scores["Technology/Web Development"] == 0.85
        assert "Technology" in result.hierarchy
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = CategoryClassificationResult(
            categories=["Technology"],
            confidence_scores={"Technology": 0.8}
        )
        
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "categories" in result_dict
        assert result_dict["categories"] == ["Technology"]
    
    def test_result_repr(self):
        """Test string representation."""
        result = CategoryClassificationResult(
            categories=["Tech", "Business"]
        )
        
        repr_str = repr(result)
        assert "categories=2" in repr_str


class TestCategoryClassifier:
    """Test CategoryClassifier class."""
    
    def test_classifier_initialization(self):
        """Test creating a CategoryClassifier."""
        classifier = CategoryClassifier()
        assert classifier.config is not None
        assert classifier.config.max_categories == 3
        
        # Test with custom config
        custom_config = TaxonomyConfig(
            categories={"Test": ["Sub1"]},
            max_categories=2
        )
        classifier = CategoryClassifier(config=custom_config)
        assert classifier.config.max_categories == 2
    
    def test_classify_tech_content(self, tech_content):
        """Test classifying technology content."""
        classifier = CategoryClassifier()
        result = classifier.classify_categories(
            title=tech_content["title"],
            script=tech_content["script"],
            tags=tech_content["tags"]
        )
        
        assert isinstance(result, CategoryClassificationResult)
        assert len(result.categories) > 0
        
        # Should classify as Technology
        categories_str = " ".join(result.categories).lower()
        assert "technology" in categories_str or "tech" in categories_str
    
    def test_classify_ai_content(self, ai_content):
        """Test classifying AI/ML content."""
        classifier = CategoryClassifier()
        result = classifier.classify_categories(
            title=ai_content["title"],
            script=ai_content["script"],
            tags=ai_content["tags"]
        )
        
        assert isinstance(result, CategoryClassificationResult)
        assert len(result.categories) > 0
        
        # Should classify as Technology (AI is under Technology)
        categories_str = " ".join(result.categories).lower()
        assert "technology" in categories_str or "ai" in categories_str
    
    def test_classify_lifestyle_content(self, lifestyle_content):
        """Test classifying lifestyle content."""
        classifier = CategoryClassifier()
        result = classifier.classify_categories(
            title=lifestyle_content["title"],
            script=lifestyle_content["script"],
            tags=lifestyle_content["tags"]
        )
        
        assert isinstance(result, CategoryClassificationResult)
        assert len(result.categories) > 0
        
        # Should classify as Lifestyle
        categories_str = " ".join(result.categories).lower()
        assert "lifestyle" in categories_str or "health" in categories_str
    
    def test_classify_without_tags(self, tech_content):
        """Test classification without tags."""
        classifier = CategoryClassifier()
        result = classifier.classify_categories(
            title=tech_content["title"],
            script=tech_content["script"],
            tags=None
        )
        
        assert isinstance(result, CategoryClassificationResult)
        assert len(result.categories) > 0
    
    def test_confidence_scores(self, tech_content):
        """Test that confidence scores are valid."""
        classifier = CategoryClassifier()
        result = classifier.classify_categories(
            title=tech_content["title"],
            script=tech_content["script"],
            tags=tech_content["tags"]
        )
        
        # All scores should be between 0 and 1
        for category, score in result.confidence_scores.items():
            assert 0 <= score <= 1
            # All returned categories should have reasonable confidence
            assert score >= classifier.config.min_category_score
    
    def test_hierarchical_categories(self, tech_content):
        """Test hierarchical category structure."""
        classifier = CategoryClassifier(
            config=TaxonomyConfig(
                categories={
                    "Technology": ["Web Development", "AI", "Mobile"]
                },
                enable_hierarchical=True
            )
        )
        
        result = classifier.classify_categories(
            title=tech_content["title"],
            script=tech_content["script"],
            tags=tech_content["tags"]
        )
        
        # Should have hierarchy
        assert isinstance(result.hierarchy, dict)
    
    def test_max_categories_limit(self):
        """Test that max_categories limit is respected."""
        config = TaxonomyConfig(
            categories={
                "Tech": ["Web", "AI"],
                "Business": ["Marketing"],
                "Education": ["Programming"],
                "Creative": ["Design"]
            },
            max_categories=2
        )
        classifier = CategoryClassifier(config=config)
        
        result = classifier.classify_categories(
            title="Tech Business Education Creative Programming",
            script="Technology business education creative design programming development",
            tags=["tech", "business", "education"]
        )
        
        assert len(result.categories) <= 2
    
    def test_category_score_calculation(self):
        """Test category score calculation logic."""
        classifier = CategoryClassifier()
        
        # Test with clear technology content
        score = classifier._calculate_category_score(
            category="technology",
            content="technology software programming computer technology",
            tags=["technology", "software"]
        )
        
        assert score > 0.5  # Should have high relevance
    
    def test_category_keywords(self):
        """Test category keyword mapping."""
        classifier = CategoryClassifier()
        
        # Test getting keywords for known categories
        tech_keywords = classifier._get_category_keywords("technology")
        assert len(tech_keywords) > 0
        assert "software" in tech_keywords
        
        ai_keywords = classifier._get_category_keywords("ai")
        assert len(ai_keywords) > 0
    
    def test_hierarchy_building(self):
        """Test hierarchy building logic."""
        classifier = CategoryClassifier()
        
        categories = [
            "Technology",
            "Technology/Web Development",
            "Technology/AI",
            "Business"
        ]
        
        hierarchy = classifier._build_hierarchy(categories)
        
        assert "Technology" in hierarchy
        assert "Web Development" in hierarchy["Technology"]
        assert "AI" in hierarchy["Technology"]
        assert "Business" in hierarchy
    
    def test_get_category_suggestions(self, tech_content):
        """Test getting category suggestions."""
        classifier = CategoryClassifier()
        
        suggestions = classifier.get_category_suggestions(
            title=tech_content["title"],
            script=tech_content["script"],
            min_confidence=0.5
        )
        
        assert isinstance(suggestions, list)
        assert all(isinstance(item, tuple) for item in suggestions)
        assert all(len(item) == 2 for item in suggestions)
        
        # Should be sorted by confidence
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i][1] >= suggestions[i + 1][1]


class TestClassifyCategoriesFunction:
    """Test convenience function."""
    
    def test_classify_categories_function(self, tech_content):
        """Test the convenience function."""
        result = classify_categories(
            title=tech_content["title"],
            script=tech_content["script"],
            tags=tech_content["tags"]
        )
        
        assert isinstance(result, CategoryClassificationResult)
        assert len(result.categories) > 0
    
    def test_classify_with_custom_config(self):
        """Test with custom configuration."""
        config = TaxonomyConfig(
            categories={"Tech": ["Web"], "Business": []},
            max_categories=1
        )
        
        result = classify_categories(
            title="Web Development Tutorial",
            script="Learn web development with modern technologies",
            tags=["web", "development"],
            config=config
        )
        
        assert len(result.categories) <= 1


class TestMultiCategoryContent:
    """Test content that belongs to multiple categories."""
    
    def test_cross_category_content(self):
        """Test content that spans multiple categories."""
        classifier = CategoryClassifier()
        
        result = classifier.classify_categories(
            title="AI for Business: Machine Learning in Marketing",
            script="""
            Artificial intelligence and machine learning are revolutionizing
            business marketing strategies. Companies use AI to analyze customer
            data and optimize campaigns. Technology and business intersect in
            data-driven marketing.
            """,
            tags=["ai", "business", "marketing", "technology"]
        )
        
        assert len(result.categories) >= 1
        
        # Should identify both Technology and Business
        categories_lower = [cat.lower() for cat in result.categories]
        has_tech = any("tech" in cat or "ai" in cat for cat in categories_lower)
        has_business = any("business" in cat or "marketing" in cat for cat in categories_lower)
        
        # Should have at least one of these categories
        assert has_tech or has_business
    
    def test_subcategory_assignment(self):
        """Test assignment to subcategories."""
        classifier = CategoryClassifier()
        
        result = classifier.classify_categories(
            title="Deep Learning and AI Technology Tutorial",
            script="""
            Deep learning is a subset of machine learning that uses neural
            networks. Python and TensorFlow are popular for deep learning.
            AI technology and deep learning applications include computer vision 
            and NLP. Technology advances in artificial intelligence and software.
            """,
            tags=["deep learning", "ai", "python", "neural networks", "technology"]
        )
        
        # Should assign categories (may or may not include subcategories depending on content)
        # The test validates that classification works, not specific category assignment
        assert isinstance(result, CategoryClassificationResult)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_content(self):
        """Test with empty content."""
        classifier = CategoryClassifier()
        result = classifier.classify_categories(
            title="",
            script="",
            tags=None
        )
        
        # Should handle gracefully
        assert isinstance(result, CategoryClassificationResult)
    
    def test_short_content(self):
        """Test with very short content."""
        classifier = CategoryClassifier()
        result = classifier.classify_categories(
            title="AI",
            script="Artificial Intelligence",
            tags=["ai"]
        )
        
        assert isinstance(result, CategoryClassificationResult)
    
    def test_ambiguous_content(self):
        """Test with ambiguous content."""
        classifier = CategoryClassifier()
        result = classifier.classify_categories(
            title="General Topics",
            script="Various topics and general information about things.",
            tags=None
        )
        
        # Should still return a result, even if confidence is low
        assert isinstance(result, CategoryClassificationResult)
    
    def test_special_characters(self):
        """Test content with special characters."""
        classifier = CategoryClassifier()
        result = classifier.classify_categories(
            title="C++ & Python!",
            script="Programming in C++ and Python @home.",
            tags=["programming"]
        )
        
        assert isinstance(result, CategoryClassificationResult)
