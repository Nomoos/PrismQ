"""Tests for Title Generation from Idea module."""

import sys
import os
import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../Idea/Model/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../Idea/Model'))

from title_generator import (
    TitleGenerator,
    TitleVariant,
    TitleConfig,
    generate_titles_from_idea
)
from idea import Idea, ContentGenre, IdeaStatus


class TestTitleGenerator:
    """Tests for TitleGenerator class."""
    
    def test_generate_default_variants(self):
        """Test generating default number of title variants."""
        idea = Idea(
            title="The Future of AI",
            concept="An exploration of artificial intelligence trends",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea)
        
        assert len(variants) == 5  # Default is 5
        assert all(isinstance(v, TitleVariant) for v in variants)
        assert all(len(v.text) > 0 for v in variants)
    
    def test_generate_three_variants(self):
        """Test generating exactly 3 variants."""
        idea = Idea(
            title="Digital Privacy",
            concept="Understanding online privacy concerns",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)
        
        assert len(variants) == 3
        # Check different styles
        styles = [v.style for v in variants]
        assert len(set(styles)) == 3  # All different styles
    
    def test_generate_five_variants(self):
        """Test generating 5 variants with different styles."""
        idea = Idea(
            title="Machine Learning Basics",
            concept="Introduction to machine learning concepts",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=5)
        
        assert len(variants) == 5
        styles = [v.style for v in variants]
        expected_styles = {'direct', 'question', 'how-to', 'curiosity', 'authoritative'}
        assert set(styles) == expected_styles
    
    def test_generate_from_concept_only(self):
        """Test generating titles when only concept is provided."""
        idea = Idea(
            title="",
            concept="A comprehensive exploration of quantum computing and its implications for modern technology",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)
        
        assert len(variants) == 3
        assert all(len(v.text) > 0 for v in variants)
        # Should extract title from concept
        assert all("quantum" in v.text.lower() or "computing" in v.text.lower() for v in variants[:1])
    
    def test_variant_length_constraints(self):
        """Test that variants respect length constraints."""
        config = TitleConfig(
            min_length=20,
            max_length=80,
            num_variants=4
        )
        
        idea = Idea(
            title="A Very Long Title About The Future of Technology and Innovation in the Modern World",
            concept="Technology trends",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator(config)
        variants = generator.generate_from_idea(idea)
        
        for variant in variants:
            assert len(variant.text) <= config.max_length
            assert variant.length == len(variant.text)
    
    def test_keyword_extraction(self):
        """Test keyword extraction from idea."""
        idea = Idea(
            title="Machine Learning for Healthcare",
            concept="Applying ML techniques to medical diagnosis",
            keywords=["machine-learning", "healthcare", "diagnosis"],
            themes=["technology", "medicine"],
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)
        
        # Check that variants have keywords
        for variant in variants:
            assert len(variant.keywords) > 0
            assert any(kw in variant.keywords for kw in ["machine-learning", "healthcare"])
    
    def test_educational_genre_variant(self):
        """Test variant generation for educational genre."""
        idea = Idea(
            title="Quantum Computing",
            concept="Understanding quantum computers",
            genre=ContentGenre.EDUCATIONAL,
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=4)
        
        # Should include educational-style variants
        texts = [v.text for v in variants]
        assert any("Guide" in text or "Understanding" in text or "How to" in text 
                  for text in texts)
    
    def test_entertainment_genre_variant(self):
        """Test variant generation for entertainment genre."""
        idea = Idea(
            title="Space Exploration",
            concept="The exciting world of space travel",
            genre=ContentGenre.ENTERTAINMENT,
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=4)
        
        # Should include engaging variants
        texts = [v.text for v in variants]
        assert any("Fascinating" in text or "World" in text or "Secrets" in text 
                  for text in texts)
    
    def test_variant_scores(self):
        """Test that variants have quality scores."""
        idea = Idea(
            title="Artificial Intelligence",
            concept="AI technology overview",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)
        
        for variant in variants:
            assert 0.0 <= variant.score <= 1.0
            assert variant.score > 0.5  # Should have reasonable scores
    
    def test_variant_to_dict(self):
        """Test converting variant to dictionary."""
        variant = TitleVariant(
            text="Test Title",
            style="direct",
            length=10,
            keywords=["test", "title"],
            score=0.85
        )
        
        result = variant.to_dict()
        
        assert result["text"] == "Test Title"
        assert result["style"] == "direct"
        assert result["length"] == 10
        assert result["keywords"] == ["test", "title"]
        assert result["score"] == 0.85
    
    def test_invalid_idea(self):
        """Test error handling with invalid idea."""
        generator = TitleGenerator()
        
        with pytest.raises(ValueError, match="Idea cannot be None"):
            generator.generate_from_idea(None)
    
    def test_empty_idea(self):
        """Test error handling with empty idea."""
        idea = Idea(
            title="",
            concept="",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        
        with pytest.raises(ValueError, match="must have at least a title or concept"):
            generator.generate_from_idea(idea)
    
    def test_invalid_num_variants(self):
        """Test error handling with invalid number of variants."""
        idea = Idea(
            title="Test Title",
            concept="Test concept",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        
        # Too few variants
        with pytest.raises(ValueError, match="must be between 3 and 5"):
            generator.generate_from_idea(idea, num_variants=2)
        
        # Too many variants
        with pytest.raises(ValueError, match="must be between 3 and 5"):
            generator.generate_from_idea(idea, num_variants=6)
    
    def test_custom_config(self):
        """Test using custom configuration."""
        config = TitleConfig(
            num_variants=4,
            min_length=30,
            max_length=60,
            focus="engagement"
        )
        
        idea = Idea(
            title="Tech Trends",
            concept="Latest technology trends",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator(config)
        variants = generator.generate_from_idea(idea)
        
        assert len(variants) == 4
        for variant in variants:
            assert len(variant.text) <= config.max_length


class TestConvenienceFunction:
    """Tests for convenience function."""
    
    def test_generate_titles_from_idea(self):
        """Test convenience function for title generation."""
        idea = Idea(
            title="Cloud Computing",
            concept="Understanding cloud services",
            status=IdeaStatus.DRAFT
        )
        
        variants = generate_titles_from_idea(idea, num_variants=3)
        
        assert len(variants) == 3
        assert all(isinstance(v, TitleVariant) for v in variants)
    
    def test_with_custom_config(self):
        """Test convenience function with custom config."""
        config = TitleConfig(
            num_variants=4,
            max_length=70
        )
        
        idea = Idea(
            title="Blockchain Technology",
            concept="Decentralized systems",
            status=IdeaStatus.DRAFT
        )
        
        variants = generate_titles_from_idea(idea, num_variants=4, config=config)
        
        assert len(variants) == 4
        for variant in variants:
            assert len(variant.text) <= 70


class TestVariantStyles:
    """Tests for specific variant generation strategies."""
    
    def test_direct_variant(self):
        """Test direct variant generation."""
        idea = Idea(
            title="Cybersecurity Best Practices",
            concept="Security guidelines",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=5)
        
        # Direct variant should be first
        direct = variants[0]
        assert direct.style == "direct"
        assert "Cybersecurity" in direct.text or "Best Practices" in direct.text
    
    def test_question_variant(self):
        """Test question variant generation."""
        idea = Idea(
            title="Future of Work",
            concept="Workplace trends",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=5)
        
        # Find question variant
        question = next(v for v in variants if v.style == "question")
        assert question.text.endswith("?")
        assert any(word in question.text for word in ["What", "How", "Why"])
    
    def test_howto_variant(self):
        """Test how-to variant generation."""
        idea = Idea(
            title="Data Science",
            concept="Learning data science",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=5)
        
        # Find how-to variant
        howto = next(v for v in variants if v.style == "how-to")
        assert "How to" in howto.text or "Master" in howto.text
    
    def test_curiosity_variant(self):
        """Test curiosity variant generation."""
        idea = Idea(
            title="Neural Networks",
            concept="Deep learning systems",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=5)
        
        # Find curiosity variant
        curiosity = next(v for v in variants if v.style == "curiosity")
        assert any(word in curiosity.text for word in 
                  ["Hidden", "Secret", "Truth", "Guide", "Complete", "Fascinating"])
    
    def test_authoritative_variant(self):
        """Test authoritative variant generation."""
        idea = Idea(
            title="Project Management",
            concept="Managing projects effectively",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=5)
        
        # Find authoritative variant
        auth = next(v for v in variants if v.style == "authoritative")
        assert any(word in auth.text for word in 
                  ["Analysis", "Comprehensive", "Expert", "Essential", "Guide"])


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    def test_very_short_title(self):
        """Test with very short title."""
        idea = Idea(
            title="AI",
            concept="Artificial Intelligence overview",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)
        
        assert len(variants) == 3
        # Variants should expand the short title
        assert all(len(v.text) >= 2 for v in variants)
    
    def test_title_with_special_characters(self):
        """Test title with special characters."""
        idea = Idea(
            title="AI & ML: The Future?",
            concept="AI and ML trends",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)
        
        assert len(variants) == 3
        assert all(len(v.text) > 0 for v in variants)
    
    def test_unicode_title(self):
        """Test title with unicode characters."""
        idea = Idea(
            title="Technology & Innovation",
            concept="Tech trends",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)
        
        assert len(variants) == 3
        assert all(len(v.text) > 0 for v in variants)
    
    def test_long_concept(self):
        """Test with very long concept."""
        idea = Idea(
            title="",
            concept="""This is a very long concept that goes into great detail about 
            multiple topics including technology, innovation, future trends, and 
            various other aspects that might be relevant to content creation and 
            publishing in the modern digital age.""",
            status=IdeaStatus.DRAFT
        )
        
        generator = TitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)
        
        assert len(variants) == 3
        # Should extract reasonable titles from long concept
        assert all(len(v.text) < 150 for v in variants)
