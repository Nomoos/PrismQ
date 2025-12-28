"""Test AI integration in idea_variants module.

This test verifies that:
1. AI generation is required and errors are raised when Ollama is unavailable
2. AI generation works correctly when Ollama is available
3. Generated content is meaningful and not template-like
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from idea_variants import IdeaGenerator, create_ideas_from_input
from ai_generator import AIIdeaGenerator, AIConfig


class TestAIIntegration:
    """Tests for AI integration in idea generation."""
    
    # Test data constants
    MOCK_AI_CONTENT = (
        "Sarah discovers an ancient map hidden in her grandmother's attic, leading to a treasure hunt through Acadia's moonlit trails. "
        "The journey becomes a test of courage as mysterious lights guide her deeper into the forest."
    )
    
    def test_ai_generator_initialization_when_available(self):
        """Test that AI generator is initialized when Ollama is available."""
        # Mock the AI generator to simulate Ollama being available
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            mock_ai_gen_class.return_value = mock_ai_instance
            
            generator = IdeaGenerator(use_ai=True)
            
            assert generator.ai_generator is not None
            assert generator.use_ai is True
    
    def test_error_when_ollama_unavailable(self):
        """Test that RuntimeError is raised when Ollama is unavailable."""
        # Mock the AI generator to simulate Ollama being unavailable
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = False
            mock_ai_gen_class.return_value = mock_ai_instance
            
            # Should raise RuntimeError when AI is requested but unavailable
            with pytest.raises(RuntimeError, match="Ollama is not available"):
                IdeaGenerator(use_ai=True)
    
    def test_no_error_when_ai_disabled(self):
        """Test that no error is raised when AI is explicitly disabled."""
        # Create generator without AI
        generator = IdeaGenerator(use_ai=False)
        
        assert generator.ai_generator is None
        assert generator.use_ai is False
    
    def test_ai_content_generation_with_mock(self):
        """Test AI content generation with mocked AI generator."""
        # Mock the AI generator
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            # Mock the generate_with_custom_prompt method to return AI-like content
            def mock_generate(input_text, **kwargs):
                field_desc = kwargs.get('field_description', 'content')
                flavor = kwargs.get('flavor', 'default')
                return f"This is AI-generated content about {input_text} with {flavor} flavor, addressing {field_desc}. It's engaging and specific, not template-like."
            
            mock_ai_instance.generate_with_custom_prompt = mock_generate
            mock_ai_gen_class.return_value = mock_ai_instance
            
            generator = IdeaGenerator(use_ai=True)
            
            idea = generator.generate_from_flavor(
                input_text="Mountain Adventure: A thrilling journey",
                flavor_name="Emotion-First Hook",
            )
            
            assert idea is not None
            assert 'hook' in idea
            # Should contain AI-generated content, not template text
            assert 'AI-generated content' in idea['hook']
            assert 'How' not in idea['hook'] or 'relates to' not in idea['hook'].lower()
    
    def test_no_template_phrases_in_ai_content(self):
        """Verify that AI-generated content doesn't contain template phrases."""
        # Mock the AI generator
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            # Use test data constant for realistic AI content
            mock_ai_instance.generate_with_custom_prompt = lambda **kwargs: self.MOCK_AI_CONTENT
            
            mock_ai_gen_class.return_value = mock_ai_instance
            
            generator = IdeaGenerator(use_ai=True)
            
            idea = generator.generate_from_flavor(
                input_text="Acadia Night Hikers",
                flavor_name="Light Mystery + Adventure"
            )
            
            # Check that generated content doesn't have template patterns
            template_phrases = [
                "How",
                "relates to",
                "the attention-grabbing opening or central question",
                "the main idea or premise in 1-2 sentences",
                "overall tone and style approach"
            ]
            
            for field_name, field_value in idea.items():
                if field_name in ['hook', 'core_concept', 'emotional_core', 'audience_connection', 'key_elements', 'tone_style']:
                    for phrase in template_phrases:
                        assert phrase.lower() not in field_value.lower(), (
                            f"Template phrase '{phrase}' found in {field_name}: {field_value}"
                        )
    
    def test_create_ideas_from_input_requires_ai(self):
        """Test that create_ideas_from_input requires AI to be available."""
        # Mock AI as unavailable
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = False
            mock_ai_gen_class.return_value = mock_ai_instance
            
            # Should raise RuntimeError when AI is not available
            with pytest.raises(RuntimeError, match="Ollama is not available"):
                create_ideas_from_input("Test Title", count=2)


class TestErrorHandling:
    """Tests for error handling when AI is unavailable."""
    
    def test_generation_fails_without_ai(self):
        """Test that idea generation fails when AI is disabled."""
        generator = IdeaGenerator(use_ai=False)
        
        # Should raise RuntimeError when trying to generate without AI
        with pytest.raises(RuntimeError, match="AI generator not available"):
            generator.generate_from_flavor(
                input_text="Test Title",
                flavor_name="Emotion-First Hook"
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
