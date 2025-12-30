"""Simplified tests for refactored AI Title Generation module."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Set up paths
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent.parent.parent.parent.parent.parent
_idea_model_path = _project_root / "T" / "Idea" / "Model" / "src"
_src_path = _test_dir.parent.parent / "src"

sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_idea_model_path))
sys.path.insert(0, str(_src_path))

from ai_title_generator import (
    AITitleGenerator,
    TitleGeneratorConfig,
    AIUnavailableError,
    generate_titles_from_idea,
)
from ollama_client import OllamaClient
from prompt_loader import PromptLoader
from title_scorer import TitleScorer
from title_variant import TitleVariant

from idea import Idea, IdeaStatus


class TestAITitleGeneratorRefactored:
    """Tests for refactored AITitleGenerator."""

    @patch("ollama_client.requests.get")
    def test_initialization(self, mock_get):
        """Test generator initialization."""
        mock_get.return_value = Mock(status_code=200)
        
        generator = AITitleGenerator()
        assert generator.is_available() is True

    @patch("ollama_client.requests.get")
    def test_generate_from_idea(self, mock_get):
        """Test generating titles from an idea."""
        mock_get.return_value = Mock(status_code=200)
        
        with patch("ollama_client.requests.post") as mock_post:
            # Mock response with multiple title lines (as returned by AI)
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {"response": 
                    "The Mirror's Silent Message\n"
                    "Reflections in the Dark\n"
                    "When Light Meets Shadow\n"
                    "The Echo of Glass\n"
                    "Through the Looking Glass\n"
                }
            )
            
            generator = AITitleGenerator()
            idea = Idea(
                title="Test",
                concept="A story about reflection",
                status=IdeaStatus.DRAFT
            )
            
            variants = generator.generate_from_idea(idea, num_variants=3)
            
            assert len(variants) == 3
            assert all(isinstance(v, TitleVariant) for v in variants)

    @patch("ollama_client.requests.get")
    def test_prompt_uses_literary_template(self, mock_get):
        """Test that literary-focused prompt is used."""
        mock_get.return_value = Mock(status_code=200)
        
        generator = AITitleGenerator()
        idea = Idea(
            title="Test",
            concept="A test concept",
            status=IdeaStatus.DRAFT
        )
        
        prompt = generator._create_prompt(idea)
        
        # Verify literary-focused content
        assert "creative title architect" in prompt
        assert "literary writer" in prompt
        assert "intimate novel" in prompt
        assert "{IDEA}" not in prompt  # Should be replaced
        assert "A test concept" in prompt

    @patch("ollama_client.requests.get")
    def test_unavailable_raises_error(self, mock_get):
        """Test that unavailable Ollama raises error."""
        mock_get.side_effect = Exception("Connection refused")
        
        generator = AITitleGenerator()
        idea = Idea(title="Test", concept="Test", status=IdeaStatus.DRAFT)
        
        with pytest.raises(AIUnavailableError):
            generator.generate_from_idea(idea, num_variants=3)


class TestPromptLoader:
    """Tests for PromptLoader."""

    def test_loads_title_generation_prompt(self):
        """Test loading the title generation prompt."""
        loader = PromptLoader()
        prompt = loader.get_title_generation_prompt()
        
        assert len(prompt) > 0
        assert "{IDEA}" in prompt
        assert "creative title architect" in prompt


class TestOllamaClient:
    """Tests for OllamaClient."""

    @patch("ollama_client.requests.get")
    def test_availability_check(self, mock_get):
        """Test Ollama availability check."""
        mock_get.return_value = Mock(status_code=200)
        
        client = OllamaClient()
        assert client.is_available() is True

    @patch("ollama_client.requests.get")
    @patch("ollama_client.requests.post")
    def test_generate_text(self, mock_post, mock_get):
        """Test text generation."""
        mock_get.return_value = Mock(status_code=200)
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"response": "Generated Title"}
        )
        
        client = OllamaClient()
        result = client.generate("Test prompt", temperature=0.7)
        
        assert result == "Generated Title"


class TestTitleScorer:
    """Tests for TitleScorer."""

    def test_score_by_length(self):
        """Test scoring by length."""
        scorer = TitleScorer()
        
        # Ideal length (45-52)
        ideal = "A" * 50
        assert scorer.score_by_length(ideal) == 0.95
        
        # Too long
        too_long = "A" * 70
        assert scorer.score_by_length(too_long) == 0.75

    def test_infer_style(self):
        """Test style inference."""
        scorer = TitleScorer()
        
        assert scorer.infer_style("Why Does It Matter?") == "question"
        assert scorer.infer_style("How to Succeed") == "how-to"
        assert scorer.infer_style("5 Ways to Win") == "listicle"
        assert scorer.infer_style("The Answer") == "direct"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
