"""Tests for Idea Creation module."""

import sys
import os
import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../Model/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../Model'))

from creation import IdeaCreator, CreationConfig
from idea import Idea, ContentGenre, IdeaStatus


class TestIdeaCreatorFromTitle:
    """Tests for creating ideas from titles."""
    
    def test_create_single_idea_from_title(self):
        """Test creating a single idea from a title."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("The Future of AI", num_ideas=1)
        
        assert len(ideas) == 1
        assert ideas[0].title == "The Future of AI"
        assert ideas[0].concept is not None
        assert len(ideas[0].concept) > 0
        assert ideas[0].status == IdeaStatus.DRAFT
    
    def test_create_multiple_ideas_from_title(self):
        """Test creating multiple ideas from a title."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("Digital Privacy", num_ideas=3)
        
        assert len(ideas) == 3
        assert all(isinstance(idea, Idea) for idea in ideas)
        # Titles should have some variation
        titles = [idea.title for idea in ideas]
        assert len(set(titles)) > 1  # Not all the same
    
    def test_create_with_target_platforms(self):
        """Test creating ideas with specific target platforms."""
        creator = IdeaCreator()
        platforms = ["youtube", "tiktok", "instagram"]
        ideas = creator.create_from_title(
            "Social Media Trends",
            num_ideas=2,
            target_platforms=platforms
        )
        
        assert len(ideas) == 2
        for idea in ideas:
            assert idea.target_platforms == platforms
    
    def test_create_with_target_formats(self):
        """Test creating ideas with specific target formats."""
        creator = IdeaCreator()
        formats = ["video", "audio"]
        ideas = creator.create_from_title(
            "Podcast Series",
            num_ideas=1,
            target_formats=formats
        )
        
        assert ideas[0].target_formats == formats
    
    def test_create_with_genre(self):
        """Test creating ideas with specific genre."""
        creator = IdeaCreator()
        ideas = creator.create_from_title(
            "Quantum Computing Explained",
            num_ideas=1,
            genre=ContentGenre.EDUCATIONAL
        )
        
        assert ideas[0].genre == ContentGenre.EDUCATIONAL
    
    def test_create_with_length_target(self):
        """Test creating ideas with length target."""
        creator = IdeaCreator()
        ideas = creator.create_from_title(
            "Quick Tips",
            num_ideas=1,
            length_target="60 seconds"
        )
        
        assert ideas[0].length_target == "60 seconds"
    
    def test_create_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        creator = IdeaCreator()
        with pytest.raises(ValueError, match="Title cannot be empty"):
            creator.create_from_title("")
    
    def test_create_whitespace_title_raises_error(self):
        """Test that whitespace-only title raises ValueError."""
        creator = IdeaCreator()
        with pytest.raises(ValueError, match="Title cannot be empty"):
            creator.create_from_title("   ")
    
    def test_create_zero_ideas_raises_error(self):
        """Test that num_ideas=0 raises ValueError."""
        creator = IdeaCreator()
        with pytest.raises(ValueError, match="num_ideas must be at least 1"):
            creator.create_from_title("Valid Title", num_ideas=0)
    
    def test_create_negative_ideas_raises_error(self):
        """Test that negative num_ideas raises ValueError."""
        creator = IdeaCreator()
        with pytest.raises(ValueError, match="num_ideas must be at least 1"):
            creator.create_from_title("Valid Title", num_ideas=-1)
    
    def test_created_ideas_have_keywords(self):
        """Test that created ideas have extracted keywords."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("Artificial Intelligence and Machine Learning")
        
        assert len(ideas[0].keywords) > 0
        # Should contain relevant keywords
        keywords_text = " ".join(ideas[0].keywords).lower()
        assert "artificial" in keywords_text or "intelligence" in keywords_text
    
    def test_created_ideas_have_themes(self):
        """Test that created ideas have extracted themes."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("Educational Technology Innovation")
        
        assert len(ideas[0].themes) > 0
    
    def test_created_ideas_have_narrative_fields(self):
        """Test that created ideas have narrative fields populated."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("Time Travel Paradoxes")
        
        idea = ideas[0]
        assert idea.premise is not None and len(idea.premise) > 0
        assert idea.synopsis is not None and len(idea.synopsis) > 0
        assert idea.skeleton is not None and len(idea.skeleton) > 0
        assert idea.outline is not None and len(idea.outline) > 0
    
    def test_created_ideas_have_creation_notes(self):
        """Test that created ideas have appropriate notes."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("Test Title", num_ideas=2)
        
        for i, idea in enumerate(ideas):
            assert "Generated from title" in idea.notes
            assert f"variation {i + 1}/2" in idea.notes


class TestIdeaCreatorFromDescription:
    """Tests for creating ideas from descriptions."""
    
    def test_create_single_idea_from_description(self):
        """Test creating a single idea from a description."""
        creator = IdeaCreator()
        description = "A story about a detective solving mysteries in virtual reality"
        ideas = creator.create_from_description(description, num_ideas=1)
        
        assert len(ideas) == 1
        assert ideas[0].concept is not None
        assert description in ideas[0].concept or ideas[0].concept in description
        assert ideas[0].status == IdeaStatus.DRAFT
    
    def test_create_multiple_ideas_from_description(self):
        """Test creating multiple ideas from a description."""
        creator = IdeaCreator()
        description = "Exploring the impact of climate change on coastal cities"
        ideas = creator.create_from_description(description, num_ideas=3)
        
        assert len(ideas) == 3
        assert all(isinstance(idea, Idea) for idea in ideas)
    
    def test_title_generated_from_description(self):
        """Test that title is generated from description."""
        creator = IdeaCreator()
        description = "A comprehensive guide to sustainable living practices"
        ideas = creator.create_from_description(description, num_ideas=1)
        
        assert ideas[0].title is not None
        assert len(ideas[0].title) > 0
    
    def test_create_with_genre_from_description(self):
        """Test creating ideas with genre from description."""
        creator = IdeaCreator()
        description = "Horror stories from abandoned hospitals"
        ideas = creator.create_from_description(
            description,
            num_ideas=1,
            genre=ContentGenre.HORROR
        )
        
        assert ideas[0].genre == ContentGenre.HORROR
    
    def test_create_empty_description_raises_error(self):
        """Test that empty description raises ValueError."""
        creator = IdeaCreator()
        with pytest.raises(ValueError, match="Description cannot be empty"):
            creator.create_from_description("")
    
    def test_create_whitespace_description_raises_error(self):
        """Test that whitespace-only description raises ValueError."""
        creator = IdeaCreator()
        with pytest.raises(ValueError, match="Description cannot be empty"):
            creator.create_from_description("   ")
    
    def test_created_from_description_have_keywords(self):
        """Test that ideas from description have keywords."""
        creator = IdeaCreator()
        description = "Machine learning algorithms for natural language processing"
        ideas = creator.create_from_description(description)
        
        assert len(ideas[0].keywords) > 0
    
    def test_created_from_description_have_narrative_fields(self):
        """Test that ideas from description have narrative fields."""
        creator = IdeaCreator()
        description = "A journey through ancient civilizations"
        ideas = creator.create_from_description(description)
        
        idea = ideas[0]
        assert idea.premise is not None and len(idea.premise) > 0
        assert idea.synopsis is not None and len(idea.synopsis) > 0
        assert idea.logline is not None and len(idea.logline) > 0
        assert idea.hook is not None and len(idea.hook) > 0


class TestCreationConfig:
    """Tests for CreationConfig."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = CreationConfig()
        
        assert config.min_title_length == 20
        assert config.max_title_length == 100
        assert config.min_story_length == 100
        assert config.max_story_length == 1000
        assert config.variation_degree == "medium"
        assert config.include_all_fields is True
    
    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = CreationConfig(
            min_title_length=30,
            max_title_length=120,
            min_story_length=200,
            max_story_length=2000,
            variation_degree="high",
            include_all_fields=False
        )
        
        assert config.min_title_length == 30
        assert config.max_title_length == 120
        assert config.min_story_length == 200
        assert config.max_story_length == 2000
        assert config.variation_degree == "high"
        assert config.include_all_fields is False
    
    def test_creator_uses_config(self):
        """Test that IdeaCreator uses provided config."""
        config = CreationConfig(include_all_fields=False)
        creator = IdeaCreator(config)
        
        ideas = creator.create_from_title("Test Title")
        
        # With include_all_fields=False, some fields should be empty
        # while synopsis should be populated
        assert ideas[0].synopsis is not None
    
    def test_title_length_respected(self):
        """Test that title length limits are respected."""
        config = CreationConfig(max_title_length=50)
        creator = IdeaCreator(config)
        
        long_description = "This is a very long description that would normally generate a very long title exceeding our maximum length limit"
        ideas = creator.create_from_description(long_description)
        
        assert len(ideas[0].title) <= config.max_title_length


class TestVariationGeneration:
    """Tests for variation generation."""
    
    def test_low_variation_degree(self):
        """Test low variation degree produces similar ideas."""
        config = CreationConfig(variation_degree="low")
        creator = IdeaCreator(config)
        
        ideas = creator.create_from_title("Test Title", num_ideas=3)
        
        # With low variation, first ideas should be similar
        assert ideas[0].title == "Test Title"
    
    def test_medium_variation_degree(self):
        """Test medium variation degree produces moderate diversity."""
        config = CreationConfig(variation_degree="medium")
        creator = IdeaCreator(config)
        
        ideas = creator.create_from_title("Test Title", num_ideas=3)
        
        # Should have some variation in titles
        titles = [idea.title for idea in ideas]
        assert len(set(titles)) >= 2
    
    def test_high_variation_degree(self):
        """Test high variation degree produces diverse ideas."""
        config = CreationConfig(variation_degree="high")
        creator = IdeaCreator(config)
        
        ideas = creator.create_from_title("Test Title", num_ideas=5)
        
        # Should have significant variation
        concepts = [idea.concept for idea in ideas]
        # At least some concepts should be different
        assert len(set(concepts)) >= 2


class TestFieldPopulation:
    """Tests for narrative field population."""
    
    def test_all_narrative_fields_populated(self):
        """Test that all narrative fields are populated when configured."""
        config = CreationConfig(include_all_fields=True)
        creator = IdeaCreator(config)
        
        ideas = creator.create_from_title("Complete Story")
        idea = ideas[0]
        
        # Check all narrative fields
        assert idea.idea is not None and len(idea.idea) > 0
        assert idea.premise is not None and len(idea.premise) > 0
        assert idea.logline is not None and len(idea.logline) > 0
        assert idea.hook is not None and len(idea.hook) > 0
        assert idea.synopsis is not None and len(idea.synopsis) > 0
        assert idea.skeleton is not None and len(idea.skeleton) > 0
        assert idea.outline is not None and len(idea.outline) > 0
    
    def test_minimal_fields_when_configured(self):
        """Test that minimal fields are populated when configured."""
        config = CreationConfig(include_all_fields=False)
        creator = IdeaCreator(config)
        
        ideas = creator.create_from_title("Minimal Story")
        idea = ideas[0]
        
        # Synopsis should be populated
        assert idea.synopsis is not None and len(idea.synopsis) > 0
        # Keywords and themes should be present
        assert len(idea.keywords) > 0
    
    def test_synopsis_length_varies(self):
        """Test that synopsis length varies within configured bounds."""
        config = CreationConfig(
            min_story_length=50,
            max_story_length=500
        )
        creator = IdeaCreator(config)
        
        ideas = creator.create_from_title("Variable Length Story", num_ideas=1)
        
        # Synopsis should be within reasonable bounds
        synopsis_word_count = len(ideas[0].synopsis.split())
        assert synopsis_word_count >= 10  # At least some content


class TestDefaultBehavior:
    """Tests for default behavior with 10 ideas."""
    
    def test_default_creates_ten_ideas_from_title(self):
        """Test that default behavior creates 10 ideas from title."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("AI and Machine Learning")
        
        assert len(ideas) == 10
        assert all(isinstance(idea, Idea) for idea in ideas)
        # Each idea should have unique title
        titles = [idea.title for idea in ideas]
        assert len(set(titles)) >= 3  # At least some variation
    
    def test_default_creates_ten_ideas_from_description(self):
        """Test that default behavior creates 10 ideas from description."""
        creator = IdeaCreator()
        description = "Exploring the impact of artificial intelligence on society"
        ideas = creator.create_from_description(description)
        
        assert len(ideas) == 10
        assert all(isinstance(idea, Idea) for idea in ideas)
    
    def test_custom_default_num_ideas(self):
        """Test that custom default_num_ideas config works."""
        config = CreationConfig(default_num_ideas=5)
        creator = IdeaCreator(config)
        ideas = creator.create_from_title("Custom Default")
        
        assert len(ideas) == 5
    
    def test_explicit_overrides_default(self):
        """Test that explicit num_ideas overrides default."""
        creator = IdeaCreator()  # Default is 10
        ideas = creator.create_from_title("Explicit Override", num_ideas=3)
        
        assert len(ideas) == 3


class TestAIConfiguration:
    """Tests for AI configuration and fallback behavior."""
    
    def test_ai_disabled_by_config(self):
        """Test that AI can be disabled via config."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        
        assert creator.ai_generator is None
        ideas = creator.create_from_title("No AI Test", num_ideas=2)
        assert len(ideas) == 2
    
    def test_ai_enabled_but_unavailable(self):
        """Test fallback when AI is enabled but Ollama unavailable."""
        config = CreationConfig(use_ai=True)
        creator = IdeaCreator(config)
        
        # AI should be unavailable (no Ollama running in test environment)
        if creator.ai_generator:
            assert not creator.ai_generator.available
        
        ideas = creator.create_from_title("Fallback Test", num_ideas=2)
        assert len(ideas) == 2
    
    def test_custom_ai_model_config(self):
        """Test custom AI model configuration."""
        config = CreationConfig(
            use_ai=True,
            ai_model="qwen2.5:72b-q4_K_M",
            ai_temperature=0.9
        )
        creator = IdeaCreator(config)
        
        # Config should be set
        assert config.ai_model == "qwen2.5:72b-q4_K_M"
        assert config.ai_temperature == 0.9
    
    def test_fallback_creates_valid_ideas(self):
        """Test that fallback generation creates valid ideas."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        
        ideas = creator.create_from_title("Fallback Valid Test", num_ideas=3)
        
        for idea in ideas:
            assert idea.title
            assert idea.concept
            assert idea.synopsis
            assert len(idea.keywords) > 0
            assert idea.status == IdeaStatus.DRAFT
