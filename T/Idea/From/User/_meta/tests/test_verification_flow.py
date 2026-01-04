"""Comprehensive verification test for T.Idea.From.User functionality.

This test verifies that the module:
1. Creates Idea objects from text input using AI
2. Stores the text form of the idea returned from local AI

According to the problem statement:
"01_PrismQ.T.Idea.From.User - Vytváření nápadů (Idea objektů) z textového vstupu 
pomocí AI, ukládající textovou podobu nápadu vráceného z lokální AI"
(Creating ideas (Idea objects) from text input using AI, storing the text form 
of the idea returned from local AI)
"""

import os
import sys
import sqlite3
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

# Add repo root src for IdeaTable
repo_root = os.path.join(os.path.dirname(__file__), "../../../../../..")
sys.path.insert(0, os.path.join(repo_root, "src"))

from idea_variants import IdeaGenerator

# Try to import IdeaTable for real database tests
try:
    from idea import IdeaTable
    IDEA_TABLE_AVAILABLE = True
except ImportError:
    IDEA_TABLE_AVAILABLE = False


class TestIdeaCreationFlow:
    """Test the complete flow: text input → AI generation → database storage."""
    
    def test_complete_flow_with_mocked_ai_and_db(self):
        """Test complete flow from text input to database storage with mocked components.
        
        Verifies:
        1. Text input is passed to AI
        2. AI generates idea text
        3. Idea text is stored in database
        """
        # Mock the AI generator
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            # AI returns generated text
            ai_generated_text = (
                "A thrilling night hiking adventure in Acadia National Park. "
                "The group encounters mysterious phenomena and must work together "
                "to navigate through the darkness while uncovering secrets of the forest."
            )
            
            def mock_generate(input_text, **kwargs):
                # Verify input text is passed
                assert input_text == "Acadia Night Hikers"
                return ai_generated_text
            
            mock_ai_instance.generate_with_custom_prompt = mock_generate
            mock_ai_gen_class.return_value = mock_ai_instance
            
            # Mock database
            mock_db = Mock()
            mock_db_idea_id = 42
            
            def mock_insert_idea(text, version):
                # Verify the AI-generated text is what's being stored
                assert text == ai_generated_text
                assert version == 1
                return mock_db_idea_id
            
            mock_db.insert_idea = mock_insert_idea
            
            # Create generator and generate idea
            generator = IdeaGenerator(use_ai=True)
            
            input_text = "Acadia Night Hikers"
            idea = generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text=input_text,
                db=mock_db
            )
            
            # Verify the result
            assert 'text' in idea, "Generated idea should contain 'text' field"
            assert idea['text'] == ai_generated_text, "Text should be the AI-generated content"
            assert 'variant_name' in idea, "Generated idea should contain 'variant_name' field"
            assert 'idea_id' in idea, "Generated idea should contain 'idea_id' when saved to DB"
            assert idea['idea_id'] == mock_db_idea_id
    
    def test_text_input_not_parsed(self):
        """Test that input text is passed directly to AI without parsing."""
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            captured_inputs = []
            
            def mock_generate(input_text, **kwargs):
                captured_inputs.append(input_text)
                return "Generated content " * 20  # Meet minimum length
            
            mock_ai_instance.generate_with_custom_prompt = mock_generate
            mock_ai_gen_class.return_value = mock_ai_instance
            
            generator = IdeaGenerator(use_ai=True)
            
            # Test various input formats
            test_cases = [
                "Simple text",
                "Text with special chars: !@#$%",
                '{"story_title": "JSON", "tone": "dark"}',
                "Multi\nLine\nText",
            ]
            
            for test_input in test_cases:
                captured_inputs.clear()
                
                idea = generator.generate_from_flavor(
                    flavor_name="Emotion-First Hook",
                    input_text=test_input,
                )
                
                # Verify exact input was passed to AI
                assert len(captured_inputs) == 1
                assert captured_inputs[0] == test_input, (
                    f"Input should be passed as-is. "
                    f"Expected: {test_input!r}, Got: {captured_inputs[0]!r}"
                )
    
    def test_ai_generated_text_is_stored(self):
        """Test that the AI-generated text is what gets stored in the database."""
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            # Different AI responses to test
            test_cases = [
                "Short idea text that meets minimum length requirement for AI content",
                "A much longer idea text with detailed narrative content " * 5,
                "Text with\nmultiple\nlines and special chars: éñ",
            ]
            
            for ai_response in test_cases:
                def mock_generate(input_text, **kwargs):
                    return ai_response
                
                mock_ai_instance.generate_with_custom_prompt = mock_generate
                mock_ai_gen_class.return_value = mock_ai_instance
                
                mock_db = Mock()
                stored_texts = []
                
                def mock_insert_idea(text, version):
                    stored_texts.append(text)
                    return 1
                
                mock_db.insert_idea = mock_insert_idea
                
                generator = IdeaGenerator(use_ai=True)
                
                idea = generator.generate_from_flavor(
                    flavor_name="Emotion-First Hook",
                    input_text="Test input",
                    db=mock_db
                )
                
                # Verify AI response is what's stored
                assert len(stored_texts) == 1
                assert stored_texts[0] == ai_response, (
                    f"AI-generated text should be stored as-is. "
                    f"Expected: {ai_response!r}, Got: {stored_texts[0]!r}"
                )
                assert idea['text'] == ai_response
    
    def test_ai_unavailable_raises_error(self):
        """Test that error is raised when AI is not available."""
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = False  # AI not available
            mock_ai_gen_class.return_value = mock_ai_instance
            
            # Should raise RuntimeError during initialization
            with pytest.raises(RuntimeError, match="AI generation requested but Ollama is not available"):
                generator = IdeaGenerator(use_ai=True)
    
    def test_minimal_content_length_validation(self):
        """Test that AI-generated content meets minimum length requirements."""
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            # AI returns content that's too short
            def mock_generate(input_text, **kwargs):
                return "Too short"
            
            mock_ai_instance.generate_with_custom_prompt = mock_generate
            mock_ai_gen_class.return_value = mock_ai_instance
            
            generator = IdeaGenerator(use_ai=True)
            
            # Should raise error for insufficient content
            with pytest.raises(RuntimeError, match="AI generated insufficient content"):
                generator.generate_from_flavor(
                    flavor_name="Emotion-First Hook",
                    input_text="Test input",
                )
    
    def test_database_storage_with_version(self):
        """Test that ideas are stored with correct version number."""
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            ai_text = "Generated idea content " * 10
            mock_ai_instance.generate_with_custom_prompt = lambda *args, **kwargs: ai_text
            mock_ai_gen_class.return_value = mock_ai_instance
            
            mock_db = Mock()
            captured_calls = []
            
            def mock_insert_idea(text, version):
                captured_calls.append({'text': text, 'version': version})
                return 1
            
            mock_db.insert_idea = mock_insert_idea
            
            generator = IdeaGenerator(use_ai=True)
            
            idea = generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text="Test",
                db=mock_db
            )
            
            # Verify database call
            assert len(captured_calls) == 1
            assert captured_calls[0]['version'] == 1
            assert captured_calls[0]['text'] == ai_text


class TestRealDatabaseIntegration:
    """Test with real database (using temporary database)."""
    
    def test_real_database_storage(self):
        """Test storing idea in a real SQLite database."""
        if not IDEA_TABLE_AVAILABLE:
            pytest.skip("IdeaTable not available")
        
        with patch('idea_variants.AIIdeaGenerator') as mock_ai_gen_class:
            mock_ai_instance = Mock()
            mock_ai_instance.available = True
            
            ai_text = "This is a complete AI-generated idea with sufficient length to meet requirements."
            mock_ai_instance.generate_with_custom_prompt = lambda *args, **kwargs: ai_text
            mock_ai_gen_class.return_value = mock_ai_instance
            
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                tmp_db_path = tmp.name
            
            try:
                # Setup database
                db = IdeaTable(tmp_db_path)
                db.connect()
                db.create_tables()
                
                # Generate and store idea
                generator = IdeaGenerator(use_ai=True)
                
                input_text = "Test idea input"
                idea = generator.generate_from_flavor(
                    flavor_name="Emotion-First Hook",
                    input_text=input_text,
                    db=db
                )
                
                # Verify idea was stored
                assert 'idea_id' in idea
                idea_id = idea['idea_id']
                
                # Retrieve from database
                stored_idea = db.get_idea(idea_id)
                
                assert stored_idea is not None
                assert stored_idea['text'] == ai_text
                assert stored_idea['version'] == 1
                assert stored_idea['id'] == idea_id
                
                db.close()
            finally:
                # Cleanup
                if os.path.exists(tmp_db_path):
                    os.remove(tmp_db_path)


class TestExpectedBehavior:
    """Document expected behavior with real AI."""
    
    def test_expected_behavior_documentation(self):
        """Document the expected behavior when using real AI (Ollama).
        
        This test documents what should happen with a real AI setup:
        
        1. User provides text input (e.g., "Acadia Night Hikers")
        2. Text is passed directly to AI without parsing
        3. AI (via Ollama) generates a complete idea narrative
        4. The AI-generated text is stored in database with version=1
        5. The result includes: text, variant_name, and idea_id (if saved to DB)
        
        With Ollama running:
        - Input: "Acadia Night Hikers"
        - AI generates: A detailed narrative about night hiking in Acadia
        - Database stores: The complete AI-generated text
        - Returns: {
            'text': '<AI-generated narrative>',
            'variant_name': 'Emotion-First Hook',
            'idea_id': <database_id>
          }
        
        Without Ollama:
        - Raises RuntimeError during IdeaGenerator initialization
        - Error message guides user to install and start Ollama
        """
        # This is a documentation test - always passes
        assert True, "See docstring for expected behavior"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
