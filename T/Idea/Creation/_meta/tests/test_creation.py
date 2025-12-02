"""Tests for Idea Creation module.

Note: Most tests require AI (Ollama) to be running. Tests that don't require AI
are marked accordingly. Without Ollama, idea generation returns empty lists.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../Model/src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../Model'))

from creation import IdeaCreator, CreationConfig
from idea import Idea, ContentGenre, IdeaStatus


# Marker for tests that require AI (Ollama) to be running
requires_ai = pytest.mark.skipif(
    True,  # Skip by default since Ollama is not available in CI
    reason="Requires Ollama AI to be running"
)


class TestIdeaCreatorValidation:
    """Tests for input validation (don't require AI)."""
    
    def test_create_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        with pytest.raises(ValueError, match="Title cannot be empty"):
            creator.create_from_title("")
    
    def test_create_whitespace_title_raises_error(self):
        """Test that whitespace-only title raises ValueError."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        with pytest.raises(ValueError, match="Title cannot be empty"):
            creator.create_from_title("   ")
    
    def test_create_zero_ideas_raises_error(self):
        """Test that num_ideas=0 raises ValueError."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        with pytest.raises(ValueError, match="num_ideas must be at least 1"):
            creator.create_from_title("Valid Title", num_ideas=0)
    
    def test_create_negative_ideas_raises_error(self):
        """Test that negative num_ideas raises ValueError."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        with pytest.raises(ValueError, match="num_ideas must be at least 1"):
            creator.create_from_title("Valid Title", num_ideas=-1)
    
    def test_create_empty_description_raises_error(self):
        """Test that empty description raises ValueError."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        with pytest.raises(ValueError, match="Description cannot be empty"):
            creator.create_from_description("")
    
    def test_create_whitespace_description_raises_error(self):
        """Test that whitespace-only description raises ValueError."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        with pytest.raises(ValueError, match="Description cannot be empty"):
            creator.create_from_description("   ")


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
        assert config.use_ai is True
        assert config.default_num_ideas == 10
        assert config.prompt_template is None
    
    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = CreationConfig(
            min_title_length=30,
            max_title_length=120,
            min_story_length=200,
            max_story_length=2000,
            variation_degree="high",
            include_all_fields=False,
            use_ai=False,
            default_num_ideas=5,
            prompt_template="Custom template"
        )
        
        assert config.min_title_length == 30
        assert config.max_title_length == 120
        assert config.min_story_length == 200
        assert config.max_story_length == 2000
        assert config.variation_degree == "high"
        assert config.include_all_fields is False
        assert config.use_ai is False
        assert config.default_num_ideas == 5
        assert config.prompt_template == "Custom template"
    
    def test_prompt_template_config(self):
        """Test that custom prompt template can be configured."""
        custom_template = "Custom template for {num_ideas} ideas about {input}"
        config = CreationConfig(
            use_ai=True,
            prompt_template=custom_template
        )
        assert config.prompt_template == custom_template


class TestAIConfiguration:
    """Tests for AI configuration behavior (no fallback - AI required)."""
    
    def test_ai_disabled_returns_empty_list(self):
        """Test that disabling AI returns empty list."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        
        assert creator.ai_generator is None
        ideas = creator.create_from_title("No AI Test", num_ideas=2)
        assert len(ideas) == 0  # Empty list when AI disabled
    
    def test_ai_enabled_but_unavailable_returns_empty_list(self):
        """Test that unavailable AI returns empty list with error logged."""
        config = CreationConfig(use_ai=True)
        creator = IdeaCreator(config)
        
        # AI should be unavailable (no Ollama running in test environment)
        # The ai_generator should be None because Ollama is not running
        assert creator.ai_generator is None
        
        ideas = creator.create_from_title("AI Unavailable Test", num_ideas=2)
        assert len(ideas) == 0  # Empty list when AI unavailable
    
    def test_custom_ai_model_config(self):
        """Test custom AI model configuration."""
        config = CreationConfig(
            use_ai=True,
            ai_model="qwen2.5:72b-q4_K_M",
            ai_temperature=0.9
        )
        
        # Config should be set
        assert config.ai_model == "qwen2.5:72b-q4_K_M"
        assert config.ai_temperature == 0.9
    
    def test_description_no_ai_returns_empty_list(self):
        """Test that without AI, empty list is returned for descriptions."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        
        ideas = creator.create_from_description("Test description", num_ideas=3)
        assert len(ideas) == 0  # Empty list when no AI


class TestIdeaCreatorWithMockedAI:
    """Tests using mocked AI generator."""
    
    def test_create_ideas_from_ai_data(self):
        """Test converting AI response to Idea objects."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        
        # Mock AI response data
        ai_ideas = [
            {
                'title': 'Test Idea 1',
                'concept': 'A great concept',
                'premise': 'The premise of the story',
                'logline': 'A compelling logline',
                'hook': 'An attention-grabbing hook',
                'synopsis': 'A detailed synopsis',
                'skeleton': '1. Point 1\n2. Point 2',
                'outline': 'Detailed outline here',
                'keywords': ['test', 'idea', 'creation'],
                'themes': ['innovation', 'technology']
            },
            {
                'title': 'Test Idea 2',
                'concept': 'Another concept',
                'premise': 'Another premise',
                'logline': 'Another logline',
                'hook': 'Another hook',
                'synopsis': 'Another synopsis',
                'skeleton': '1. A\n2. B',
                'outline': 'Another outline',
                'keywords': ['test2'],
                'themes': ['theme2']
            }
        ]
        
        # Call the internal method directly
        ideas = creator._create_ideas_from_ai_data(
            ai_ideas=ai_ideas,
            target_platforms=['youtube'],
            target_formats=['video'],
            genre=ContentGenre.EDUCATIONAL,
            length_target='10 minutes',
            source_type='title',
            source='Test Title'
        )
        
        assert len(ideas) == 2
        
        # Check first idea
        assert ideas[0].title == 'Test Idea 1'
        assert ideas[0].concept == 'A great concept'
        assert ideas[0].premise == 'The premise of the story'
        assert ideas[0].logline == 'A compelling logline'
        assert ideas[0].hook == 'An attention-grabbing hook'
        assert ideas[0].synopsis == 'A detailed synopsis'
        assert ideas[0].target_platforms == ['youtube']
        assert ideas[0].target_formats == ['video']
        assert ideas[0].genre == ContentGenre.EDUCATIONAL
        assert ideas[0].length_target == '10 minutes'
        assert ideas[0].keywords == ['test', 'idea', 'creation']
        assert ideas[0].themes == ['innovation', 'technology']
        assert ideas[0].status == IdeaStatus.DRAFT
        assert 'AI-generated' in ideas[0].notes
        
        # Check second idea
        assert ideas[1].title == 'Test Idea 2'
        assert ideas[1].concept == 'Another concept'
    
    def test_create_ideas_with_default_values(self):
        """Test AI data conversion with missing fields uses defaults."""
        config = CreationConfig(use_ai=False)
        creator = IdeaCreator(config)
        
        # Minimal AI response
        ai_ideas = [
            {'title': 'Minimal Idea'}
        ]
        
        ideas = creator._create_ideas_from_ai_data(
            ai_ideas=ai_ideas,
            source_type='title',
            source='Test'
        )
        
        assert len(ideas) == 1
        assert ideas[0].title == 'Minimal Idea'
        assert ideas[0].concept == ''  # Default empty
        assert ideas[0].target_platforms == ['youtube', 'medium']  # Default
        assert ideas[0].target_formats == ['text', 'video']  # Default
        assert ideas[0].genre == ContentGenre.OTHER  # Default
        assert ideas[0].length_target == 'variable'  # Default


# Tests that require AI (marked as skip in CI)
@requires_ai
class TestIdeaCreatorFromTitle:
    """Tests for creating ideas from titles (requires AI)."""
    
    def test_create_single_idea_from_title(self):
        """Test creating a single idea from a title."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("The Future of AI", num_ideas=1)
        
        assert len(ideas) == 1
        assert ideas[0].title is not None
        assert ideas[0].concept is not None
        assert len(ideas[0].concept) > 0
        assert ideas[0].status == IdeaStatus.DRAFT
    
    def test_create_multiple_ideas_from_title(self):
        """Test creating multiple ideas from a title."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("Digital Privacy", num_ideas=3)
        
        assert len(ideas) == 3
        assert all(isinstance(idea, Idea) for idea in ideas)
    
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


@requires_ai
class TestIdeaCreatorFromDescription:
    """Tests for creating ideas from descriptions (requires AI)."""
    
    def test_create_single_idea_from_description(self):
        """Test creating a single idea from a description."""
        creator = IdeaCreator()
        description = "A story about a detective solving mysteries in virtual reality"
        ideas = creator.create_from_description(description, num_ideas=1)
        
        assert len(ideas) == 1
        assert ideas[0].concept is not None
        assert ideas[0].status == IdeaStatus.DRAFT
    
    def test_create_multiple_ideas_from_description(self):
        """Test creating multiple ideas from a description."""
        creator = IdeaCreator()
        description = "Exploring the impact of climate change on coastal cities"
        ideas = creator.create_from_description(description, num_ideas=3)
        
        assert len(ideas) == 3
        assert all(isinstance(idea, Idea) for idea in ideas)


@requires_ai  
class TestDefaultBehavior:
    """Tests for default behavior with 10 ideas (requires AI)."""
    
    def test_default_creates_ten_ideas_from_title(self):
        """Test that default behavior creates 10 ideas from title."""
        creator = IdeaCreator()
        ideas = creator.create_from_title("AI and Machine Learning")
        
        assert len(ideas) == 10
        assert all(isinstance(idea, Idea) for idea in ideas)
    
    def test_default_creates_ten_ideas_from_description(self):
        """Test that default behavior creates 10 ideas from description."""
        creator = IdeaCreator()
        description = "Exploring the impact of artificial intelligence on society"
        ideas = creator.create_from_description(description)
        
        assert len(ideas) == 10
        assert all(isinstance(idea, Idea) for idea in ideas)


class TestAIGeneratorIdeaText:
    """Tests for AI generator's idea_text field generation."""
    
    def test_validate_idea_dict_creates_idea_text(self):
        """Test that _validate_idea_dict generates idea_text from other fields."""
        from ai_generator import AIIdeaGenerator
        
        generator = AIIdeaGenerator()
        
        # Test with missing idea_text
        idea = {
            'title': 'Test Title',
            'hook': 'An engaging hook that captures attention immediately.',
            'premise': 'This is a detailed premise that explains the story setup.',
            'concept': 'The underlying concept that drives the narrative.',
        }
        
        validated = generator._validate_idea_dict(idea)
        
        # Should have idea_text field now
        assert 'idea_text' in validated
        # idea_text should be at least MIN_IDEA_TEXT_LENGTH characters
        assert len(validated['idea_text']) >= generator.MIN_IDEA_TEXT_LENGTH
    
    def test_generate_idea_text_meets_minimum_length(self):
        """Test that _generate_idea_text always produces at least MIN_IDEA_TEXT_LENGTH characters."""
        from ai_generator import AIIdeaGenerator
        
        generator = AIIdeaGenerator()
        
        # Test with minimal content
        idea = {
            'title': 'A Short Title',
            'hook': 'Hook',
            'premise': 'Premise',
            'concept': 'Concept',
        }
        
        text = generator._generate_idea_text(idea)
        assert len(text) >= generator.MIN_IDEA_TEXT_LENGTH
    
    def test_generate_idea_text_uses_available_fields(self):
        """Test that _generate_idea_text combines available fields."""
        from ai_generator import AIIdeaGenerator
        
        generator = AIIdeaGenerator()
        
        idea = {
            'title': 'The Story of Tomorrow',
            'hook': 'What if everything you knew was wrong?',
            'premise': 'A young scientist discovers a hidden truth.',
            'concept': 'Reality vs illusion explored through science.',
            'logline': 'One discovery changes everything.',
            'themes': ['mystery', 'science', 'truth'],
        }
        
        text = generator._generate_idea_text(idea)
        
        # Should include content from multiple fields
        assert 'What if everything you knew was wrong' in text or 'scientist discovers' in text
    
    def test_validate_idea_dict_preserves_existing_valid_idea_text(self):
        """Test that valid existing idea_text is preserved."""
        from ai_generator import AIIdeaGenerator
        
        generator = AIIdeaGenerator()
        
        existing_text = "This is a valid idea text that is definitely long enough to meet the minimum length requirement of 100 characters."
        idea = {
            'title': 'Test',
            'idea_text': existing_text
        }
        
        validated = generator._validate_idea_dict(idea)
        
        # Should preserve the existing valid idea_text
        assert validated['idea_text'] == existing_text
    
    def test_min_idea_text_length_constant(self):
        """Test that MIN_IDEA_TEXT_LENGTH constant is 100."""
        from ai_generator import AIIdeaGenerator
        
        assert AIIdeaGenerator.MIN_IDEA_TEXT_LENGTH == 100
