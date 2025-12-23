"""Tests for AI Script Generator (Qwen3:30b).

These tests verify:
1. AIContentGeneratorConfig default values
2. AIContentGenerator initialization
3. Seed variations functionality (504 simple words like "pudding", "fire", "ocean")
4. AI generation with Title + Idea + Seed + Audience
5. Integration with ContentGenerator
"""

from unittest.mock import MagicMock, patch

import pytest

from T.Content.From.Idea.Title.src.ai_content_generator import (
    SEED_VARIATIONS,
    AIContentGenerator,
    AIContentGeneratorConfig,
    generate_content,
    get_random_seed,
    get_seed_by_index,
)
from T.Content.From.Idea.Title.src.content_generator import (
    ContentGenerator,
    ContentGeneratorConfig,
    ContentV1,
)

# Patch paths for mocking
AI_SCRIPT_GEN_REQUESTS_GET = "T.Content.From.Idea.Title.src.ai_content_generator.requests.get"
AI_SCRIPT_GEN_REQUESTS_POST = "T.Content.From.Idea.Title.src.ai_content_generator.requests.post"
SCRIPT_GEN_AI_MODULE = "T.Content.From.Idea.Title.src.content_generator._get_ai_generator_module"

# Import Idea for test data
import sys
from pathlib import Path

_t_module_dir = Path(__file__).parent.parent / "T" / "Idea" / "Model" / "src"
sys.path.insert(0, str(_t_module_dir))
from idea import ContentGenre, Idea


@pytest.fixture
def sample_idea():
    """Create a sample Idea for testing."""
    return Idea(
        title="The Mystery of the Abandoned House",
        concept="A girl discovers a time-loop in an abandoned house",
        premise="When Maya explores an abandoned house, she discovers she's trapped in a time loop.",
        hook="Every night at midnight, she returns to the same moment.",
        synopsis="Maya enters an abandoned house looking for her lost cat.",
        genre=ContentGenre.HORROR,
        target_audience="Horror enthusiasts aged 14-29",
    )


class TestSeedVariations:
    """Tests for seed variations functionality."""

    def test_seed_variations_count(self):
        """Test that there are approximately 500 seed variations."""
        assert len(SEED_VARIATIONS) >= 400  # At least 400
        assert len(SEED_VARIATIONS) <= 600  # No more than 600

    def test_seed_variations_are_simple_words(self):
        """Test that seeds are simple words/concepts."""
        # Check some expected simple seeds
        simple_seeds = [
            "pudding",
            "fire",
            "water",
            "sister",
            "ocean",
            "Chicago",
            "Germany",
            "chill",
        ]
        for seed in simple_seeds:
            assert seed in SEED_VARIATIONS, f"Expected '{seed}' in SEED_VARIATIONS"

    def test_get_random_seed_returns_string(self):
        """Test that get_random_seed returns a string."""
        seed = get_random_seed()
        assert isinstance(seed, str)
        assert len(seed) > 0

    def test_get_random_seed_returns_from_list(self):
        """Test that random seed comes from the list."""
        for _ in range(10):
            seed = get_random_seed()
            assert seed in SEED_VARIATIONS

    def test_get_seed_by_index(self):
        """Test getting seed by specific index."""
        assert get_seed_by_index(0) == SEED_VARIATIONS[0]
        assert get_seed_by_index(100) == SEED_VARIATIONS[100]

    def test_get_seed_by_index_wraps(self):
        """Test that index wraps around."""
        length = len(SEED_VARIATIONS)
        assert get_seed_by_index(length) == get_seed_by_index(0)
        assert get_seed_by_index(length + 5) == get_seed_by_index(5)


class TestAIContentGeneratorConfig:
    """Tests for AIContentGeneratorConfig."""

    def test_default_model_is_qwen(self):
        """Test that default model is Qwen3:30b."""
        config = AIContentGeneratorConfig()
        assert config.model == "qwen3:32b"

    def test_default_api_base(self):
        """Test default API base URL."""
        config = AIContentGeneratorConfig()
        assert config.api_base == "http://localhost:11434"

    def test_default_temperature(self):
        """Test default temperature for content generation."""
        config = AIContentGeneratorConfig()
        assert config.temperature == 0.7

    def test_default_timeout(self):
        """Test default timeout is adequate for content generation."""
        config = AIContentGeneratorConfig()
        assert config.timeout >= 60


class TestAIScriptGenerator:
    """Tests for AIContentGenerator."""

    def test_initialization_with_default_config(self):
        """Test initialization with default config."""
        generator = AIContentGenerator()
        assert generator.config.model == "qwen3:32b"

    def test_is_available_returns_bool(self):
        """Test that is_available returns boolean."""
        generator = AIContentGenerator()
        assert isinstance(generator.is_available(), bool)

    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    @patch(AI_SCRIPT_GEN_REQUESTS_POST)
    def test_generate_content_with_mock_api(self, mock_post, mock_get):
        """Test content generation with mocked Ollama API."""
        # Mock API availability check
        mock_get.return_value = MagicMock(status_code=200)

        # Mock content generation response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Every night at midnight, I return to the same moment. "
            "The clock strikes twelve, and I'm standing at the entrance "
            "of the abandoned house again."
        }
        mock_post.return_value = mock_response

        generator = AIContentGenerator()

        result = generator.generate_content(
            title="The Mystery of the Abandoned House",
            idea_text="A girl discovers a time-loop in an abandoned house",
            target_duration_seconds=60,
        )

        assert result is not None
        assert len(result) > 0
        mock_post.assert_called_once()

    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    @patch(AI_SCRIPT_GEN_REQUESTS_POST)
    def test_generate_content_with_specific_seed(self, mock_post, mock_get):
        """Test content generation with a specific seed."""
        mock_get.return_value = MagicMock(status_code=200)
        mock_post.return_value = MagicMock(
            status_code=200, json=MagicMock(return_value={"response": "Test script content"})
        )

        generator = AIContentGenerator()
        result = generator.generate_content(
            title="Test Title", idea_text="Test idea", seed="ocean"  # Specific seed
        )

        assert result is not None

    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    @patch(AI_SCRIPT_GEN_REQUESTS_POST)
    def test_prompt_contains_seed(self, mock_post, mock_get):
        """Test that the prompt includes the seed."""
        mock_get.return_value = MagicMock(status_code=200)
        mock_post.return_value = MagicMock(
            status_code=200, json=MagicMock(return_value={"response": "Test"})
        )

        generator = AIContentGenerator()
        generator.generate_content(title="Test", idea_text="Test idea", seed="fire")

        # Check the prompt contains the seed
        call_args = mock_post.call_args
        json_data = None
        if call_args.kwargs:
            json_data = call_args.kwargs.get("json")
        if json_data is None and len(call_args) > 1 and call_args[1]:
            json_data = call_args[1].get("json")

        assert json_data is not None
        assert "fire" in json_data.get("prompt", "")


class TestGenerateScriptConvenience:
    """Tests for the generate_content convenience function."""

    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    @patch(AI_SCRIPT_GEN_REQUESTS_POST)
    def test_generates_content_with_mock_api(self, mock_post, mock_get):
        """Test convenience function with mocked API."""
        mock_get.return_value = MagicMock(status_code=200)
        mock_post.return_value = MagicMock(
            status_code=200, json=MagicMock(return_value={"response": "Generated content text"})
        )

        result = generate_content(title="Test Title", idea_text="Test idea text")

        assert result is not None


class TestScriptGeneratorAIIntegration:
    """Tests for ContentGenerator AI integration."""

    def test_config_has_new_settings(self):
        """Test that ContentGeneratorConfig has new multiplatform settings."""
        config = ContentGeneratorConfig()
        assert hasattr(config, "target_duration_seconds")
        assert hasattr(config, "max_duration_seconds")
        assert hasattr(config, "audience")
        assert config.target_duration_seconds == 120
        assert config.max_duration_seconds == 175

    def test_config_has_audience_defaults(self):
        """Test that ContentGeneratorConfig has audience defaults."""
        config = ContentGeneratorConfig()
        assert config.audience["age_range"] == "13-23"
        assert config.audience["gender"] == "Female"
        assert config.audience["country"] == "United States"

    def test_generator_has_is_ai_available_method(self):
        """Test that ContentGenerator has is_ai_available method."""
        try:
            generator = ContentGenerator()
            assert hasattr(generator, "is_ai_available")
        except RuntimeError:
            # Expected if AI module not available
            pass

    def test_generator_raises_error_when_ai_unavailable(self, sample_idea):
        """Test that generator raises error when AI is unavailable."""
        try:
            generator = ContentGenerator()
            if not generator.is_ai_available():
                with pytest.raises(RuntimeError) as exc_info:
                    generator.generate_content_v1(idea=sample_idea, title="Test Title")
                assert "AI content generation is not available" in str(exc_info.value)
        except RuntimeError:
            # Expected if AI module not available
            pass

    @patch(SCRIPT_GEN_AI_MODULE)
    def test_ai_generation_with_mock(self, mock_get_module, sample_idea):
        """Test AI generation with mocked AI module."""
        # Create a mock AI generator
        mock_ai_generator = MagicMock()
        mock_ai_generator.is_available.return_value = True
        mock_ai_generator.generate_content.return_value = (
            "Every night at midnight, I return. This is my story of discovery."
        )

        mock_module = MagicMock()
        mock_module.AIContentGeneratorConfig = AIContentGeneratorConfig
        mock_module.AIContentGenerator.return_value = mock_ai_generator
        mock_get_module.return_value = mock_module

        config = ContentGeneratorConfig()
        generator = ContentGenerator(config=config)

        # Force reinitialize with mock
        generator._ai_generator = mock_ai_generator
        generator._ai_available = True

        script = generator.generate_content_v1(
            idea=sample_idea, title="The Mystery of the Abandoned House"
        )

        assert script is not None
        assert script.metadata.get("ai_generated") is True
        assert "AI-powered" in script.notes


class TestAIScriptGeneratorRobustness:
    """Tests for AI generator robustness and error handling."""

    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    def test_handles_connection_error(self, mock_get):
        """Test handling of connection errors."""
        import requests

        mock_get.side_effect = requests.exceptions.ConnectionError()

        generator = AIContentGenerator()
        assert generator.is_available() is False

    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    @patch(AI_SCRIPT_GEN_REQUESTS_POST)
    def test_handles_api_error(self, mock_post, mock_get):
        """Test handling of API errors."""
        import requests

        mock_get.return_value = MagicMock(status_code=200)
        mock_post.side_effect = requests.exceptions.RequestException("API Error")

        generator = AIContentGenerator()

        with pytest.raises(RuntimeError):
            generator.generate_content(title="Test Title", idea_text="Test idea")
