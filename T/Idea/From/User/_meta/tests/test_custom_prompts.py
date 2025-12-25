#!/usr/bin/env python3
"""Tests for custom prompt templating system.

This module tests the new flexible templating functionality added to
the AI generator, including placeholder substitution and custom prompts.
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
TEST_DIR = Path(__file__).parent.absolute()
CREATION_ROOT = TEST_DIR.parent.parent
sys.path.insert(0, str(CREATION_ROOT / "src"))

from ai_generator import (
    AIIdeaGenerator,
    AIConfig,
    list_available_prompts,
    apply_template,
    _load_prompt,
)


class TestApplyTemplate(unittest.TestCase):
    """Tests for apply_template function."""
    
    def test_standard_placeholder_format(self):
        """Test standard {variable} placeholder format."""
        template = "Hello {name}!"
        result = apply_template(template, name="World")
        self.assertEqual(result, "Hello World!")
    
    def test_multiple_standard_placeholders(self):
        """Test multiple {variable} placeholders."""
        template = "Hello {name}, welcome to {place}!"
        result = apply_template(template, name="Alice", place="PrismQ")
        self.assertEqual(result, "Hello Alice, welcome to PrismQ!")
    
    def test_inserttexthere_format(self):
        """Test INSERTTEXTHERE placeholder format."""
        template = "Text: INSERTTEXTHERE"
        result = apply_template(template, input="My text")
        self.assertEqual(result, "Text: My text")
    
    def test_insert_text_here_underscore_format(self):
        """Test INSERT_TEXT_HERE placeholder format."""
        template = "Text: INSERT_TEXT_HERE"
        result = apply_template(template, input="My text")
        self.assertEqual(result, "Text: My text")
    
    def test_insert_text_here_space_format(self):
        """Test INSERT TEXT HERE placeholder format."""
        template = "Text: INSERT TEXT HERE"
        result = apply_template(template, input="My text")
        self.assertEqual(result, "Text: My text")
    
    def test_mixed_placeholder_formats(self):
        """Test mixing standard and custom placeholder formats."""
        template = "Input: INSERTTEXTHERE, Name: {name}"
        result = apply_template(template, input="Test", name="User")
        self.assertEqual(result, "Input: Test, Name: User")
    
    def test_missing_placeholder_graceful(self):
        """Test that missing placeholders are handled gracefully."""
        template = "Hello {name}!"
        # Should not raise error if placeholder is missing
        result = apply_template(template)
        # The {name} should remain as-is if not provided
        self.assertIn("{name}", result)
    
    def test_extra_kwargs_ignored(self):
        """Test that extra kwargs are ignored gracefully."""
        template = "Hello {name}!"
        result = apply_template(template, name="World", extra="ignored")
        self.assertEqual(result, "Hello World!")
    
    def test_multiline_template(self):
        """Test multiline templates."""
        template = """Line 1: {var1}
Line 2: INSERTTEXTHERE
Line 3: {var2}"""
        result = apply_template(template, var1="A", input="B", var2="C")
        self.assertIn("Line 1: A", result)
        self.assertIn("Line 2: B", result)
        self.assertIn("Line 3: C", result)


class TestListAvailablePrompts(unittest.TestCase):
    """Tests for list_available_prompts function."""
    
    def test_lists_prompts(self):
        """Test that it lists available prompts."""
        prompts = list_available_prompts()
        self.assertIsInstance(prompts, list)
        # Should include the default and new templates
        self.assertIn("idea_from_title", prompts)
        self.assertIn("idea_from_description", prompts)
        self.assertIn("idea_improvement", prompts)
    
    def test_returns_sorted_list(self):
        """Test that prompts are returned sorted."""
        prompts = list_available_prompts()
        self.assertEqual(prompts, sorted(prompts))


class TestLoadPrompt(unittest.TestCase):
    """Tests for _load_prompt function."""
    
    def test_load_existing_prompt(self):
        """Test loading an existing prompt file."""
        content = _load_prompt("idea_improvement.txt")
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)
        # Should contain the task description
        self.assertIn("rewrite", content)
        self.assertIn("{input}", content)
    
    def test_load_nonexistent_prompt_raises(self):
        """Test that loading nonexistent prompt raises error."""
        with self.assertRaises(FileNotFoundError):
            _load_prompt("nonexistent_prompt.txt")


class TestAIIdeaGeneratorCustomPrompts(unittest.TestCase):
    """Tests for AIIdeaGenerator custom prompt functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AIConfig()
        self.generator = AIIdeaGenerator(self.config)
    
    def test_initialization(self):
        """Test that generator initializes correctly."""
        self.assertIsInstance(self.generator, AIIdeaGenerator)
        self.assertIsInstance(self.generator.config, AIConfig)
    
    def test_get_prompt_template_default(self):
        """Test getting default prompt template."""
        template = self.generator.get_prompt_template(for_description=False)
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)
        self.assertIn("{input}", template)
    
    def test_set_prompt_template(self):
        """Test setting custom prompt template."""
        custom = "Custom template with {input}"
        self.generator.set_prompt_template(custom)
        result = self.generator.get_prompt_template()
        self.assertEqual(result, custom)
    
    @patch.object(AIIdeaGenerator, '_call_ollama')
    def test_generate_with_custom_prompt_by_name(self, mock_call):
        """Test generate_with_custom_prompt using template name."""
        mock_call.return_value = "Generated output"
        
        # Mark as available for testing
        self.generator.available = True
        
        result = self.generator.generate_with_custom_prompt(
            input_text="Test input",
            prompt_template_name="idea_improvement"
        )
        
        self.assertEqual(result, "Generated output")
        mock_call.assert_called_once()
        
        # Check that the prompt was properly formatted
        call_args = mock_call.call_args[0][0]
        self.assertIn("Test input", call_args)
    
    @patch.object(AIIdeaGenerator, '_call_ollama')
    def test_generate_with_custom_prompt_inline(self, mock_call):
        """Test generate_with_custom_prompt using inline template."""
        mock_call.return_value = "Generated output"
        
        # Mark as available for testing
        self.generator.available = True
        
        result = self.generator.generate_with_custom_prompt(
            input_text="Test input",
            prompt_template="Process: {input}"
        )
        
        self.assertEqual(result, "Generated output")
        mock_call.assert_called_once()
        
        # Check that the prompt was properly formatted
        call_args = mock_call.call_args[0][0]
        self.assertIn("Test input", call_args)
    
    def test_generate_with_custom_prompt_no_template_raises(self):
        """Test that missing template raises error."""
        with self.assertRaises(ValueError):
            self.generator.generate_with_custom_prompt(
                input_text="Test input"
            )
    
    def test_generate_with_custom_prompt_not_available(self):
        """Test behavior when Ollama is not available."""
        self.generator.available = False
        
        result = self.generator.generate_with_custom_prompt(
            input_text="Test input",
            prompt_template="Test {input}"
        )
        
        # Should return empty string when not available
        self.assertEqual(result, "")
    
    @patch.object(AIIdeaGenerator, '_call_ollama')
    def test_generate_with_additional_kwargs(self, mock_call):
        """Test passing additional kwargs to template."""
        mock_call.return_value = "Generated output"
        self.generator.available = True
        
        result = self.generator.generate_with_custom_prompt(
            input_text="Test input",
            prompt_template="Process {input} for {audience}",
            audience="young adults"
        )
        
        # Check that both input and audience were in the prompt
        call_args = mock_call.call_args[0][0]
        self.assertIn("Test input", call_args)
        self.assertIn("young adults", call_args)


class TestIntegration(unittest.TestCase):
    """Integration tests for the templating system."""
    
    def test_end_to_end_template_workflow(self):
        """Test complete workflow: list, load, apply template."""
        # List available prompts
        prompts = list_available_prompts()
        self.assertGreater(len(prompts), 0)
        
        # Load a prompt
        template = _load_prompt("idea_improvement.txt")
        self.assertGreater(len(template), 0)
        
        # Apply template with input
        result = apply_template(template, input="The Vanishing Tide")
        self.assertIn("The Vanishing Tide", result)
        self.assertNotIn("{input}", result)
        self.assertNotIn("INSERTTEXTHERE", result)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
