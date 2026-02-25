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
        """Test generating titles from an idea (one-by-one approach with AI scoring)."""
        mock_get.return_value = Mock(status_code=200)
        
        with patch("ollama_client.requests.post") as mock_post:
            # Mock response with single title per generation call and score for scoring calls
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {"response": "The Mirror's Silent Message"}
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
            # Verify AI was called for generation (3) + scoring (3) = 6 times
            assert mock_post.call_count == 6

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

    @patch("ollama_client.requests.get")
    @patch("ollama_client.requests.post")
    def test_ai_scores_each_variant(self, mock_post, mock_get):
        """Test that AI scoring is applied to each generated variant."""
        mock_get.return_value = Mock(status_code=200)
        
        call_count = [0]
        
        def mock_response(*args, **kwargs):
            call_count[0] += 1
            # Generation calls return a title; scoring calls return a score
            if call_count[0] <= 3:
                return Mock(status_code=200, json=lambda: {"response": "The Mirror's Silent Message"})
            else:
                return Mock(status_code=200, json=lambda: {"response": "85"})
        
        mock_post.side_effect = mock_response
        
        generator = AITitleGenerator()
        idea = Idea(title="Test", concept="A story about reflection", status=IdeaStatus.DRAFT)
        
        variants = generator.generate_from_idea(idea, num_variants=3)
        
        assert len(variants) == 3
        # Scoring calls returned "85" → ai_score=0.85, combined with rule score
        for variant in variants:
            assert variant.score > 0.0


class TestPromptLoader:
    """Tests for PromptLoader."""

    def test_loads_title_generation_prompt(self):
        """Test loading the title generation prompt."""
        loader = PromptLoader()
        prompt = loader.get_title_generation_prompt()
        
        assert len(prompt) > 0
        assert "{IDEA}" in prompt
        assert "creative title architect" in prompt

    def test_loads_title_scoring_prompt(self):
        """Test loading the title scoring prompt."""
        loader = PromptLoader()
        prompt = loader.get_title_scoring_prompt()
        
        assert len(prompt) > 0
        assert "{IDEA}" in prompt
        assert "{TITLE}" in prompt


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
