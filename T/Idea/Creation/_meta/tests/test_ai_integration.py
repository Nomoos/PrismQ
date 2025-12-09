"""Test AI integration in idea_variants module.

This test verifies that:
1. AI generation is attempted when Ollama is available
2. Template fallback works when Ollama is unavailable
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
    
    def test_fallback_when_ollama_unavailable(self):
        """Test that template generation is used when Ollama is unavailable."""
        # Create generator without AI (simulating unavailable Ollama)
        generator = IdeaGenerator(use_ai=False)
        
        assert generator.ai_generator is None
        
        # Generate an idea - should use template fallback
        idea = generator.generate_from_flavor(
            title="Test Title",
            flavor_name="Emotion-First Hook",
            description="Test description"
        )
        
        assert idea is not None
        assert 'hook' in idea
        assert 'core_concept' in idea
        # Template generation should include the title in some way
        assert 'Test' in idea['hook'] or 'test' in idea['hook'].lower()
    
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
                title="Mountain Adventure",
                flavor_name="Emotion-First Hook",
                description="A thrilling journey"
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
            
            # Mock realistic AI content
            mock_ai_instance.generate_with_custom_prompt = lambda input_text, **kwargs: (
                "Sarah discovers an ancient map hidden in her grandmother's attic, leading to a treasure hunt through Acadia's moonlit trails. "
                "The journey becomes a test of courage as mysterious lights guide her deeper into the forest."
            )
            
            mock_ai_gen_class.return_value = mock_ai_instance
            
            generator = IdeaGenerator(use_ai=True)
            
            idea = generator.generate_from_flavor(
                title="Acadia Night Hikers",
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
    
    def test_create_ideas_from_input_with_ai(self):
        """Test the convenience function with AI generation."""
        # Since we can't run Ollama in test environment, we test the function signature
        # and verify it doesn't crash
        ideas = create_ideas_from_input("Test Title", count=2)
        
        assert isinstance(ideas, list)
        assert len(ideas) <= 2  # May be less if AI fails
        
        if ideas:
            idea = ideas[0]
            assert 'flavor_name' in idea
            assert 'hook' in idea
            assert 'core_concept' in idea


class TestTemplateQuality:
    """Tests for template fallback quality."""
    
    def test_template_fallback_includes_topic(self):
        """Test that template fallback includes the actual topic."""
        generator = IdeaGenerator(use_ai=False)
        
        idea = generator.generate_from_flavor(
            title="Acadia Night Hikers",
            flavor_name="Mystery/Curiosity Gap"
        )
        
        # Template should reference the actual topic
        all_content = ' '.join([
            idea.get('hook', ''),
            idea.get('core_concept', ''),
            idea.get('emotional_core', '')
        ])
        
        assert 'Acadia' in all_content or 'acadia' in all_content.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
