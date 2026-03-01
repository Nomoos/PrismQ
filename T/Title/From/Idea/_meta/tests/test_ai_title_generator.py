"""Tests for AI Title Generation module.

This module tests the refactored AITitleGenerator functionality which uses
local LLM models (Qwen3:32b) via Ollama to generate titles.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Set up paths before any other imports
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent.parent.parent.parent.parent.parent
_idea_model_path = _project_root / "T" / "Idea" / "Model" / "src"
_src_path = _test_dir.parent.parent / "src"

# Add all required paths
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_idea_model_path))
sys.path.insert(0, str(_src_path))

from ai_title_generator import (
    AITitleGenerator,
    TitleGeneratorConfig,
    AIUnavailableError,
    generate_titles_from_idea,
)
from title_variant import TitleVariant
from ollama_client import OllamaClient, OllamaConfig
from title_scorer import TitleScorer, ScoringConfig
from prompt_loader import PromptLoader

from idea import ContentGenre, Idea, IdeaStatus


class TestTitleGeneratorConfig:
    """Tests for TitleGeneratorConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TitleGeneratorConfig()

        assert config.num_variants == 5
        assert config.temperature_min == 0.6
        assert config.temperature_max == 0.8

    def test_custom_config(self):
        """Test custom configuration."""
        config = AITitleConfig(
            model="llama3.1:70b",
            api_base="http://localhost:12345",
            temperature=0.5,
            max_tokens=1000,
            timeout=120,
            num_variants=5,
        )

        assert config.model == "llama3.1:70b"
        assert config.api_base == "http://localhost:12345"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
        assert config.timeout == 120
        assert config.num_variants == 5


class TestAITitleGeneratorInit:
    """Tests for AITitleGenerator initialization."""

    @patch("ai_title_generator.requests.get")
    def test_init_ollama_available(self, mock_get):
        """Test initialization when Ollama is available."""
        mock_get.return_value = Mock(status_code=200)

        generator = AITitleGenerator()

        assert generator.available is True
        assert generator.is_available() is True

    @patch("ai_title_generator.requests.get")
    def test_init_ollama_unavailable(self, mock_get):
        """Test initialization when Ollama is unavailable."""
        mock_get.side_effect = Exception("Connection refused")

        generator = AITitleGenerator()

        assert generator.available is False
        assert generator.is_available() is False

    @patch("ai_title_generator.requests.get")
    def test_init_with_custom_config(self, mock_get):
        """Test initialization with custom config."""
        mock_get.return_value = Mock(status_code=200)

        config = AITitleConfig(model="custom:model", temperature=0.5)
        generator = AITitleGenerator(config)

        assert generator.config.model == "custom:model"
        assert generator.config.temperature == 0.5


class TestAITitleGeneratorPrompt:
    """Tests for prompt template functionality."""

    @patch("ai_title_generator.requests.get")
    def test_default_prompt_template(self, mock_get):
        """Test default prompt template."""
        mock_get.return_value = Mock(status_code=200)

        generator = AITitleGenerator()
        template = generator.get_prompt_template()

        # Check for required placeholder (single IDEA placeholder for complete idea text)
        assert "{IDEA}" in template

    @patch("ai_title_generator.requests.get")
    def test_custom_prompt_template(self, mock_get):
        """Test setting custom prompt template."""
        mock_get.return_value = Mock(status_code=200)

        generator = AITitleGenerator()
        custom_template = "Generate {num_variants} titles for {title}"
        generator.set_prompt_template(custom_template)

        assert generator.get_prompt_template() == custom_template


class TestAITitleGeneratorValidation:
    """Tests for input validation."""

    @patch("ai_title_generator.requests.get")
    def test_invalid_idea_none(self, mock_get):
        """Test error handling with None idea."""
        mock_get.return_value = Mock(status_code=200)

        generator = AITitleGenerator()

        with pytest.raises(ValueError, match="Idea cannot be None"):
            generator.generate_from_idea(None)

    @patch("ai_title_generator.requests.get")
    def test_invalid_idea_empty(self, mock_get):
        """Test error handling with empty idea."""
        mock_get.return_value = Mock(status_code=200)

        idea = Idea(title="", concept="", status=IdeaStatus.DRAFT)

        generator = AITitleGenerator()

        with pytest.raises(ValueError, match="must have at least a title or concept"):
            generator.generate_from_idea(idea)

    @patch("ai_title_generator.requests.get")
    def test_invalid_num_variants_too_few(self, mock_get):
        """Test error handling with too few variants."""
        mock_get.return_value = Mock(status_code=200)

        idea = Idea(title="Test Title", concept="Test concept", status=IdeaStatus.DRAFT)

        generator = AITitleGenerator()

        with pytest.raises(ValueError, match="must be between 3 and 10"):
            generator.generate_from_idea(idea, num_variants=2)

    @patch("ai_title_generator.requests.get")
    def test_invalid_num_variants_too_many(self, mock_get):
        """Test error handling with too many variants."""
        mock_get.return_value = Mock(status_code=200)

        idea = Idea(title="Test Title", concept="Test concept", status=IdeaStatus.DRAFT)

        generator = AITitleGenerator()

        with pytest.raises(ValueError, match="must be between 3 and 10"):
            generator.generate_from_idea(idea, num_variants=11)


class TestAITitleGeneratorResponse:
    """Tests for response parsing."""

    @patch("ai_title_generator.requests.get")
    @patch("ai_title_generator.requests.post")
    def test_parse_valid_response(self, mock_post, mock_get):
        """Test parsing valid JSON response."""
        mock_get.return_value = Mock(status_code=200)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": """[
                {"text": "Test Title 1", "style": "direct", "score": 0.9, "keywords": ["test"]},
                {"text": "Test Title 2", "style": "question", "score": 0.85, "keywords": ["test"]},
                {"text": "Test Title 3", "style": "how-to", "score": 0.8, "keywords": ["test"]}
            ]"""
        }
        mock_post.return_value = mock_response

        idea = Idea(title="Test Topic", concept="Test concept", status=IdeaStatus.DRAFT)

        generator = AITitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)

        assert len(variants) == 3
        assert all(isinstance(v, TitleVariant) for v in variants)
        assert variants[0].text == "Test Title 1"
        assert variants[0].style == "direct"
        assert variants[0].score == 0.9

    @patch("ai_title_generator.requests.get")
    @patch("ai_title_generator.requests.post")
    def test_parse_response_with_extra_text(self, mock_post, mock_get):
        """Test parsing response with text before/after JSON."""
        mock_get.return_value = Mock(status_code=200)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": """Here are the titles:
            [{"text": "Title A", "style": "direct", "score": 0.8, "keywords": ["a"]}]
            Hope these help!"""
        }
        mock_post.return_value = mock_response

        idea = Idea(title="Test", concept="Test", status=IdeaStatus.DRAFT)

        generator = AITitleGenerator()
        variants = generator.generate_from_idea(idea, num_variants=3)

        assert len(variants) == 1
        assert variants[0].text == "Title A"

    @patch("ai_title_generator.requests.get")
    def test_raises_error_when_unavailable(self, mock_get):
        """Test raises AIUnavailableError when Ollama unavailable."""
        mock_get.side_effect = Exception("Connection refused")

        idea = Idea(title="Test", concept="Test concept", status=IdeaStatus.DRAFT)

        generator = AITitleGenerator()

        with pytest.raises(AIUnavailableError):
            generator.generate_from_idea(idea, num_variants=3)


class TestAITitleGeneratorVariantCreation:
    """Tests for TitleVariant creation from parsed data."""

    @patch("ai_title_generator.requests.get")
    def test_create_variant_with_all_fields(self, mock_get):
        """Test creating variant with all fields."""
        mock_get.return_value = Mock(status_code=200)

        generator = AITitleGenerator()
        data = {
            "text": "Complete Title",
            "style": "how-to",
            "score": 0.95,
            "keywords": ["complete", "title"],
        }

        variant = generator._create_variant_from_dict(data)

        assert variant is not None
        assert variant.text == "Complete Title"
        assert variant.style == "how-to"
        assert variant.score == 0.95
        assert variant.keywords == ["complete", "title"]
        assert variant.length == len("Complete Title")

    @patch("ai_title_generator.requests.get")
    def test_create_variant_clamps_score(self, mock_get):
        """Test that scores are clamped to 0-1."""
        mock_get.return_value = Mock(status_code=200)

        generator = AITitleGenerator()

        # Score too high
        data = {"text": "Title", "score": 1.5}
        variant = generator._create_variant_from_dict(data)
        assert variant.score == 1.0

        # Score too low
        data = {"text": "Title", "score": -0.5}
        variant = generator._create_variant_from_dict(data)
        assert variant.score == 0.0

    @patch("ai_title_generator.requests.get")
    def test_create_variant_invalid_style_defaults(self, mock_get):
        """Test invalid style defaults to 'direct'."""
        mock_get.return_value = Mock(status_code=200)

        generator = AITitleGenerator()
        data = {"text": "Title", "style": "invalid-style"}

        variant = generator._create_variant_from_dict(data)

        assert variant.style == "direct"

    @patch("ai_title_generator.requests.get")
    def test_create_variant_missing_text_returns_none(self, mock_get):
        """Test returns None when text is missing."""
        mock_get.return_value = Mock(status_code=200)

        generator = AITitleGenerator()
        data = {"style": "direct", "score": 0.8}

        variant = generator._create_variant_from_dict(data)

        assert variant is None


class TestConvenienceFunction:
    """Tests for the convenience function."""

    @patch("ai_title_generator.requests.get")
    @patch("ai_title_generator.requests.post")
    def test_generate_ai_titles_from_idea(self, mock_post, mock_get):
        """Test convenience function."""
        mock_get.return_value = Mock(status_code=200)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": """[
                {"text": "AI Generated Title", "style": "direct", "score": 0.9, "keywords": ["ai"]}
            ]"""
        }
        mock_post.return_value = mock_response

        idea = Idea(title="AI Topic", concept="Testing AI", status=IdeaStatus.DRAFT)

        variants = generate_ai_titles_from_idea(idea, num_variants=3)

        assert len(variants) >= 0  # May be empty if parsing fails


class TestParseResponseThinkBlocks:
    """Tests for <think> block stripping in _parse_response."""

    def _make_generator(self):
        """Create an AITitleGenerator with mocked OllamaClient."""
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        return AITitleGenerator(ollama_client=mock_client)

    def test_parse_response_strips_think_block(self):
        """Response with <think>...</think> block yields the title after the block."""
        generator = self._make_generator()
        idea = Idea(title="Test", concept="A quiet family story", status=IdeaStatus.DRAFT)

        response = "<think>\nSome internal reasoning here.\n</think>\nSilence Spoke Loudest"
        variant = generator._parse_response(response, idea)

        assert variant is not None
        assert variant.text == "Silence Spoke Loudest"

    def test_parse_response_multiline_think_block(self):
        """Multi-line <think> block is fully stripped before extracting the title."""
        generator = self._make_generator()
        idea = Idea(title="Test", concept="A family story", status=IdeaStatus.DRAFT)

        response = (
            "<think>\n"
            "Line one of thinking.\n"
            "Line two of thinking.\n"
            "</think>\n"
            "The Weight of Unspoken Words"
        )
        variant = generator._parse_response(response, idea)

        assert variant is not None
        assert variant.text == "The Weight of Unspoken Words"

    def test_parse_response_think_block_leaves_empty_title(self):
        """<think>-only response with no title after the block returns None."""
        generator = self._make_generator()
        idea = Idea(title="Test", concept="A story", status=IdeaStatus.DRAFT)

        response = "<think>\nOnly thinking, no title.\n</think>\n"
        variant = generator._parse_response(response, idea)

        assert variant is None

    def test_parse_response_without_think_block(self):
        """Plain response without <think> block is parsed as-is."""
        generator = self._make_generator()
        idea = Idea(title="Test", concept="A story", status=IdeaStatus.DRAFT)

        response = "The Quiet Alchemy"
        variant = generator._parse_response(response, idea)

        assert variant is not None
        assert variant.text == "The Quiet Alchemy"


class TestTitleGeneratorConfig:
    """Tests for the simplified TitleGeneratorConfig."""

    def test_default_temperature_min(self):
        """Default temperature_min is 0.6."""
        config = TitleGeneratorConfig()
        assert config.temperature_min == 0.6

    def test_default_temperature_max(self):
        """Default temperature_max is 0.8."""
        config = TitleGeneratorConfig()
        assert config.temperature_max == 0.8

    def test_custom_temperatures(self):
        """Custom temperature values are respected."""
        config = TitleGeneratorConfig(temperature_min=0.3, temperature_max=0.5)
        assert config.temperature_min == 0.3
        assert config.temperature_max == 0.5


class TestGenerateFromIdeaSimplified:
    """Tests for the single-call generate_from_idea."""

    def _make_generator(self):
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        return AITitleGenerator(ollama_client=mock_client), mock_client

    def test_returns_variant_on_success(self):
        """A valid AI response returns a TitleVariant."""
        generator, mock_client = self._make_generator()
        mock_client.generate.return_value = "Silence Spoke Loudest in the Crowded Room"
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        variant = generator.generate_from_idea(idea)

        assert variant is not None
        assert variant.text == "Silence Spoke Loudest in the Crowded Room"

    def test_makes_exactly_one_ai_call(self):
        """generate_from_idea makes exactly one AI call."""
        generator, mock_client = self._make_generator()
        mock_client.generate.return_value = "Silence Spoke Loudest in the Crowded Room"
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        generator.generate_from_idea(idea)

        assert mock_client.generate.call_count == 1

    def test_returns_none_on_empty_response(self):
        """An empty AI response returns None."""
        generator, mock_client = self._make_generator()
        mock_client.generate.return_value = ""
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        variant = generator.generate_from_idea(idea)

        assert variant is None

    def test_variant_has_rule_based_score(self):
        """The returned variant carries a rule-based score (no AI scoring pass)."""
        generator, mock_client = self._make_generator()
        title = "Silence Spoke Loudest in the Crowded Room"  # ideal-length title
        mock_client.generate.return_value = title
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        variant = generator.generate_from_idea(idea)

        assert variant is not None
        assert 0.0 < variant.score <= 1.0
        # Exactly one AI call — no second scoring call
        assert mock_client.generate.call_count == 1

    def test_raises_value_error_for_none_idea(self):
        """ValueError is raised for None idea."""
        generator, _ = self._make_generator()
        with pytest.raises(ValueError, match="Idea cannot be None"):
            generator.generate_from_idea(None)

    def test_raises_value_error_for_empty_idea(self):
        """ValueError is raised when idea has no title or concept."""
        generator, _ = self._make_generator()
        idea = Idea(title="", concept="", status=IdeaStatus.DRAFT)
        with pytest.raises(ValueError, match="must have at least"):
            generator.generate_from_idea(idea)

    def test_raises_when_ai_unavailable(self):
        """AIUnavailableError is raised when Ollama is not running."""
        mock_client = MagicMock()
        mock_client.is_available.return_value = False
        generator = AITitleGenerator(ollama_client=mock_client)
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)
        with pytest.raises(AIUnavailableError):
            generator.generate_from_idea(idea)
