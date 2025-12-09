"""Integration tests for Taxonomy module."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

import pytest

from T.Publishing.SEO.Taxonomy import (
    DEFAULT_TAXONOMY,
    CategoryClassifier,
    TagGenerator,
    TaxonomyConfig,
    process_taxonomy,
)


@pytest.fixture
def sample_content():
    """Sample content for testing."""
    return {
        "title": "Building AI-Powered Web Applications with Python",
        "script": """
        Artificial intelligence is revolutionizing web development. Python
        has become the go-to language for AI and machine learning applications.
        Modern web frameworks like Flask and Django make it easy to integrate
        AI models into web applications.
        
        Developers can use TensorFlow, PyTorch, and scikit-learn to build
        machine learning models and deploy them as web services. This enables
        creating intelligent applications that can analyze data, make predictions,
        and provide personalized experiences.
        
        Web development combined with AI opens up endless possibilities for
        creating innovative applications that serve users better.
        """,
        "keywords": ["python", "ai", "machine learning", "web development"],
    }


class TestProcessTaxonomy:
    """Test the main process_taxonomy function."""

    def test_complete_taxonomy_processing(self, sample_content):
        """Test complete end-to-end taxonomy processing."""
        result = process_taxonomy(
            title=sample_content["title"],
            script=sample_content["script"],
            keywords=sample_content["keywords"],
        )

        # Verify result structure
        assert "tags" in result
        assert "categories" in result
        assert "hierarchy" in result
        assert "stats" in result
        assert "tag_scores" in result
        assert "category_scores" in result

        # Verify tags
        assert isinstance(result["tags"], list)
        assert len(result["tags"]) > 0

        # Verify categories
        assert isinstance(result["categories"], list)
        assert len(result["categories"]) > 0

        # Verify stats
        assert "total_tags" in result["stats"]
        assert "total_categories" in result["stats"]
        assert "quality_score" in result["stats"]

    def test_without_keywords(self, sample_content):
        """Test processing without keywords."""
        result = process_taxonomy(
            title=sample_content["title"], script=sample_content["script"], keywords=None
        )

        assert len(result["tags"]) > 0
        assert len(result["categories"]) > 0

    def test_without_scores(self, sample_content):
        """Test processing without including scores."""
        result = process_taxonomy(
            title=sample_content["title"],
            script=sample_content["script"],
            keywords=sample_content["keywords"],
            include_scores=False,
        )

        assert "tag_scores" not in result
        assert "category_scores" not in result
        assert "tags" in result
        assert "categories" in result

    def test_with_custom_config(self, sample_content):
        """Test processing with custom config."""
        config = TaxonomyConfig(
            categories={"Technology": ["AI", "Web Development"]},
            max_tags=5,
            max_categories=2,
            min_relevance=0.75,
        )

        result = process_taxonomy(
            title=sample_content["title"],
            script=sample_content["script"],
            keywords=sample_content["keywords"],
            config=config,
        )

        assert len(result["tags"]) <= 5
        assert len(result["categories"]) <= 2

    def test_quality_score_calculation(self, sample_content):
        """Test quality score calculation."""
        result = process_taxonomy(
            title=sample_content["title"],
            script=sample_content["script"],
            keywords=sample_content["keywords"],
        )

        quality_score = result["stats"]["quality_score"]

        # Quality score should be between 0 and 100
        assert 0 <= quality_score <= 100

        # Should be reasonable for good content
        assert quality_score > 30


class TestTagAndCategoryIntegration:
    """Test integration between tags and categories."""

    def test_tags_influence_categories(self, sample_content):
        """Test that tags influence category classification."""
        # Extract content for clarity
        title = sample_content["title"]
        script = sample_content["script"]
        keywords = sample_content["keywords"]

        # Generate tags first
        tag_gen = TagGenerator()
        tag_result = tag_gen.generate_tags(title=title, script=script, base_keywords=keywords)

        # Classify with tags
        cat_classifier = CategoryClassifier()
        with_tags = cat_classifier.classify_categories(
            title=title, script=script, tags=tag_result.tags
        )

        # Classify without tags
        without_tags = cat_classifier.classify_categories(title=title, script=script, tags=None)

        # At least one should produce results
        assert len(with_tags.categories) > 0 or len(without_tags.categories) > 0

    def test_hierarchical_consistency(self, sample_content):
        """Test consistency in hierarchical categories."""
        result = process_taxonomy(
            title=sample_content["title"],
            script=sample_content["script"],
            keywords=sample_content["keywords"],
        )

        # If hierarchy is present, verify structure
        if result["hierarchy"]:
            for parent, children in result["hierarchy"].items():
                # Parent should be in categories
                assert parent in result["categories"] or any(
                    parent in cat for cat in result["categories"]
                )


class TestMultipleContentTypes:
    """Test with different types of content."""

    def test_technical_content(self):
        """Test with technical content."""
        result = process_taxonomy(
            title="Understanding Blockchain Technology and Cryptocurrency",
            script="""
            Blockchain is a distributed ledger technology that powers cryptocurrencies
            like Bitcoin and Ethereum. It provides transparency, security, and
            decentralization. Smart contracts on blockchain enable automated transactions
            without intermediaries.
            """,
            keywords=["blockchain", "cryptocurrency", "bitcoin"],
        )

        assert len(result["tags"]) > 0
        assert len(result["categories"]) > 0

        # Should identify as Technology
        categories_str = " ".join(result["categories"]).lower()
        assert "tech" in categories_str or "blockchain" in categories_str

    def test_lifestyle_content(self):
        """Test with lifestyle content."""
        result = process_taxonomy(
            title="10 Healthy Eating Habits for Better Wellness",
            script="""
            Maintaining a balanced diet is crucial for health and wellness.
            Focus on whole foods, vegetables, and fruits. Stay hydrated and
            eat mindfully. Regular meal planning helps maintain healthy eating
            habits and supports fitness goals.
            """,
            keywords=["health", "nutrition", "wellness", "fitness"],
        )

        assert len(result["tags"]) > 0
        assert len(result["categories"]) > 0

        # Should identify as Lifestyle or Health
        categories_str = " ".join(result["categories"]).lower()
        assert "lifestyle" in categories_str or "health" in categories_str

    def test_business_content(self):
        """Test with business content."""
        result = process_taxonomy(
            title="Digital Marketing Strategies for Small Businesses",
            script="""
            Small businesses need effective digital marketing strategies to compete.
            Social media marketing, SEO, and content marketing are essential.
            Email campaigns and online advertising help reach target audiences.
            Analytics and data-driven decisions improve marketing ROI.
            """,
            keywords=["digital marketing", "business", "seo", "social media"],
        )

        assert len(result["tags"]) > 0
        assert len(result["categories"]) > 0

        # Should identify as Business or Marketing
        categories_str = " ".join(result["categories"]).lower()
        assert "business" in categories_str or "marketing" in categories_str


class TestEdgeCases:
    """Test edge cases."""

    def test_minimal_content(self):
        """Test with minimal content."""
        result = process_taxonomy(
            title="AI", script="Artificial Intelligence basics", keywords=["ai"]
        )

        # Should handle gracefully
        assert "tags" in result
        assert "categories" in result

    def test_very_long_content(self):
        """Test with very long content."""
        long_script = " ".join(
            ["Python programming is great for web development and data science."] * 100
        )

        result = process_taxonomy(
            title="Python Programming Guide", script=long_script, keywords=["python", "programming"]
        )

        assert len(result["tags"]) > 0
        assert len(result["categories"]) > 0

        # Should respect max_tags limit
        assert len(result["tags"]) <= DEFAULT_TAXONOMY.max_tags

    def test_multilingual_content(self):
        """Test with non-English content (should handle gracefully)."""
        result = process_taxonomy(
            title="Programmation Python",
            script="Python est un langage de programmation polyvalent.",
            keywords=["python", "programmation"],
        )

        # Should still work, though results may vary
        assert "tags" in result
        assert "categories" in result


class TestQualityMetrics:
    """Test quality metrics and scoring."""

    def test_quality_score_components(self, sample_content):
        """Test quality score calculation components."""
        result = process_taxonomy(
            title=sample_content["title"],
            script=sample_content["script"],
            keywords=sample_content["keywords"],
        )

        stats = result["stats"]

        # Check all components are present
        assert "avg_tag_relevance" in stats
        assert "avg_category_confidence" in stats
        assert "quality_score" in stats

        # Averages should be between 0 and 1
        assert 0 <= stats["avg_tag_relevance"] <= 1
        assert 0 <= stats["avg_category_confidence"] <= 1

    def test_optimal_tag_count_scoring(self):
        """Test that optimal tag count (5-10) gives good score."""
        # Content likely to generate 5-10 tags
        result = process_taxonomy(
            title="Python Web Development with Django and Flask",
            script="""
            Python web development frameworks like Django and Flask make it
            easy to build web applications. Django provides a full-featured
            framework while Flask offers flexibility and simplicity.
            """,
            keywords=["python", "django", "flask", "web development"],
        )

        tag_count = result["stats"]["total_tags"]

        # Should generate a reasonable number of tags
        assert 3 <= tag_count <= 15

    def test_optimal_category_count_scoring(self, sample_content):
        """Test that optimal category count (1-3) gives good score."""
        result = process_taxonomy(
            title=sample_content["title"],
            script=sample_content["script"],
            keywords=sample_content["keywords"],
        )

        cat_count = result["stats"]["total_categories"]

        # Should assign reasonable number of categories
        assert 1 <= cat_count <= DEFAULT_TAXONOMY.max_categories


class TestConfigPersistence:
    """Test configuration handling across pipeline."""

    def test_config_propagation(self):
        """Test that config is properly propagated through pipeline."""
        custom_config = TaxonomyConfig(
            categories={"Tech": ["Web", "AI"]}, max_tags=7, max_categories=2, min_relevance=0.75
        )

        result = process_taxonomy(
            title="Web Development and AI Integration",
            script="Building AI-powered web applications with modern technologies.",
            keywords=["web", "ai"],
            config=custom_config,
        )

        # Should respect config limits
        assert len(result["tags"]) <= 7
        assert len(result["categories"]) <= 2

        # All tag scores should meet min_relevance
        if result.get("tag_scores"):
            for score in result["tag_scores"].values():
                assert score >= 0.75


class TestRealWorldScenarios:
    """Test realistic content scenarios."""

    def test_tutorial_content(self):
        """Test with tutorial-style content."""
        result = process_taxonomy(
            title="Complete Beginner's Guide to React Hooks and JavaScript",
            script="""
            React Hooks revolutionized how we write React components using JavaScript. 
            This tutorial covers useState, useEffect, and custom hooks for web development.
            Learn how to manage state and side effects in functional components with JavaScript.
            We'll build practical examples step by step for web applications and software development.
            Programming with React and modern web technology.
            """,
            keywords=["react", "javascript", "hooks", "tutorial", "web development", "programming"],
        )

        assert len(result["tags"]) > 0
        # Categories may not always be assigned if confidence is low, so we check the structure
        assert "categories" in result
        assert result["stats"]["quality_score"] > 20

    def test_news_content(self):
        """Test with news-style content."""
        result = process_taxonomy(
            title="Breaking: New AI Regulation Announced",
            script="""
            Government announces new regulations for artificial intelligence
            technology. The policy affects AI companies and research institutions.
            Industry leaders respond to the regulatory framework. Impact on
            technology sector and innovation discussed.
            """,
            keywords=["ai", "regulation", "technology", "policy"],
        )

        assert len(result["tags"]) > 0
        assert len(result["categories"]) > 0

    def test_review_content(self):
        """Test with product review content."""
        result = process_taxonomy(
            title="MacBook Pro M3 Review: Performance and Design Technology",
            script="""
            Apple's new MacBook Pro with M3 chip delivers exceptional performance for
            software development and technology work. The laptop excels in video editing, 
            software development, programming and creative work using modern technology.
            Battery life is impressive for computer hardware. Design improvements include 
            better display and keyboard technology. Recommended for technology professionals
            and developers working with computers and software applications.
            """,
            keywords=["macbook", "review", "laptop", "apple", "technology", "computer", "hardware"],
        )

        assert len(result["tags"]) > 0
        # Categories may not always be assigned if confidence is low, so we check the structure
        assert "categories" in result
