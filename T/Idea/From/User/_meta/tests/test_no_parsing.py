"""Test that input text is NOT parsed, extracted, validated, or cleaned.

This test verifies that text flows directly to the AI template as-is.
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from idea_variants import IdeaGenerator


class TestNoParsing:
    """Tests to verify that no parsing occurs on input text."""
    
    def test_raw_text_passed_to_ai(self):
        """Test that raw text is passed to AI without parsing."""
        # Mock the AI generator
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            # Track what input_text was passed to the AI
            captured_input = []
            
            def mock_generate(input_text, **kwargs):
                captured_input.append(input_text)
                return "Generated idea content " * 10  # Meet minimum length
            
            mock_ai_instance.generate_with_custom_prompt = mock_generate
            mock_ai_gen_class.return_value = mock_ai_instance
            
            generator = IdeaGenerator(use_ai=True)
            
            # Test with various input formats
            test_inputs = [
                "Simple title",
                "Complex text with special chars: !@#$%^&*()",
                '{"story_title": "JSON Input", "narrator_gender": "female"}',
                "Multi\nLine\nText\nInput",
                "Very long text that could be parsed as title and description but should not be parsed at all because we want raw input",
            ]
            
            for test_input in test_inputs:
                captured_input.clear()
                
                idea = generator.generate_from_flavor(
                    flavor_name="Emotion-First Hook",
                    input_text=test_input,
                )
                
                # Verify the EXACT input text was passed to AI
                assert len(captured_input) == 1, "AI should be called exactly once"
                assert captured_input[0] == test_input, (
                    f"Input text should be passed as-is without parsing.\n"
                    f"Expected: {test_input!r}\n"
                    f"Got: {captured_input[0]!r}"
                )
                
                # Verify the input is stored in the idea
                assert idea['source_input'] == test_input
    
    def test_json_not_parsed(self):
        """Test that JSON input is NOT parsed into fields."""
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            captured_input = []
            
            def mock_generate(input_text, **kwargs):
                captured_input.append(input_text)
                return "Generated idea content " * 10
            
            mock_ai_instance.generate_with_custom_prompt = mock_generate
            mock_ai_gen_class.return_value = mock_ai_instance
            
            generator = IdeaGenerator(use_ai=True)
            
            json_input = '{"story_title": "My Story", "narrator_gender": "female", "tone": "dark"}'
            
            idea = generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text=json_input,
            )
            
            # Verify JSON was NOT parsed - it should be passed as-is
            assert captured_input[0] == json_input
            # The idea should store the raw JSON as source_input
            assert idea['source_input'] == json_input
    
    def test_no_title_description_extraction(self):
        """Test that long text is NOT split into title and description."""
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            captured_input = []
            
            def mock_generate(input_text, **kwargs):
                captured_input.append(input_text)
                return "Generated idea content " * 10
            
            mock_ai_instance.generate_with_custom_prompt = mock_generate
            mock_ai_gen_class.return_value = mock_ai_instance
            
            generator = IdeaGenerator(use_ai=True)
            
            # Long text that the old code would have split into title and description
            long_text = (
                "This is a long story about adventure. "
                "It involves hiking in the mountains. "
                "The characters face many challenges. "
                "They overcome their fears and succeed."
            )
            
            idea = generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text=long_text,
            )
            
            # Verify the ENTIRE text was passed as-is, not split
            assert captured_input[0] == long_text
            assert idea['source_input'] == long_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
