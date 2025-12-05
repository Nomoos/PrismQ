"""Tests for AI Script Generator (Qwen2.5-14B-Instruct).

These tests verify:
1. AIScriptGeneratorConfig default values
2. AIScriptGenerator initialization
3. Prompt engineering output
4. Fallback behavior when AI is unavailable
5. Integration with ScriptGenerator
"""

import pytest
from unittest.mock import patch, MagicMock

from T.Script.From.Idea.Title.src.ai_script_generator import (
    AIScriptGenerator,
    AIScriptGeneratorConfig,
    generate_ai_script
)
from T.Script.From.Idea.Title.src.script_generator import (
    ScriptGenerator,
    ScriptGeneratorConfig,
    ScriptV1,
    ScriptStructure,
    PlatformTarget,
    ScriptTone
)

# Patch paths for mocking
AI_SCRIPT_GEN_REQUESTS_GET = 'T.Script.From.Idea.Title.src.ai_script_generator.requests.get'
AI_SCRIPT_GEN_REQUESTS_POST = 'T.Script.From.Idea.Title.src.ai_script_generator.requests.post'
SCRIPT_GEN_AI_MODULE = 'T.Script.From.Idea.Title.src.script_generator._get_ai_generator_module'

# Import Idea for test data
import sys
from pathlib import Path
_t_module_dir = Path(__file__).parent.parent / 'T' / 'Idea' / 'Model' / 'src'
sys.path.insert(0, str(_t_module_dir))
from idea import Idea, ContentGenre


@pytest.fixture
def sample_idea():
    """Create a sample Idea for testing."""
    return Idea(
        title="The Mystery of the Abandoned House",
        concept="A girl discovers a time-loop in an abandoned house",
        premise="When Maya explores an abandoned house, she discovers she's trapped in a time loop, reliving the same terrifying night.",
        hook="Every night at midnight, she returns to the same moment.",
        synopsis="Maya enters an abandoned house looking for her lost cat. Inside, she finds herself trapped in a repeating nightmare.",
        genre=ContentGenre.HORROR,
        target_audience="Horror enthusiasts aged 14-29"
    )


@pytest.fixture
def sample_idea_data():
    """Create sample idea data as a dictionary."""
    return {
        "concept": "A girl discovers a time-loop in an abandoned house",
        "synopsis": "Maya enters an abandoned house looking for her lost cat. Inside, she finds herself trapped in a repeating nightmare.",
        "hook": "Every night at midnight, she returns to the same moment.",
        "premise": "When Maya explores an abandoned house, she discovers she's trapped in a time loop, reliving the same terrifying night.",
        "genre": "horror",
        "target_audience": "Horror enthusiasts aged 14-29",
        "themes": ["mystery", "time-loop", "horror"]
    }


class TestAIScriptGeneratorConfig:
    """Tests for AIScriptGeneratorConfig."""
    
    def test_default_model_is_qwen(self):
        """Test that default model is Qwen2.5-14B-Instruct."""
        config = AIScriptGeneratorConfig()
        assert config.model == "qwen2.5:14b-instruct"
    
    def test_default_api_base(self):
        """Test default API base URL."""
        config = AIScriptGeneratorConfig()
        assert config.api_base == "http://localhost:11434"
    
    def test_default_temperature(self):
        """Test default temperature for script generation."""
        config = AIScriptGeneratorConfig()
        assert config.temperature == 0.7
    
    def test_default_timeout(self):
        """Test default timeout is adequate for script generation."""
        config = AIScriptGeneratorConfig()
        assert config.timeout >= 60  # Scripts need longer generation time
    
    def test_enable_ai_default(self):
        """Test AI is enabled by default."""
        config = AIScriptGeneratorConfig()
        assert config.enable_ai is True
    
    def test_custom_model_configuration(self):
        """Test custom model configuration."""
        config = AIScriptGeneratorConfig(
            model="llama3.1:70b",
            temperature=0.5,
            max_tokens=3000
        )
        assert config.model == "llama3.1:70b"
        assert config.temperature == 0.5
        assert config.max_tokens == 3000


class TestAIScriptGenerator:
    """Tests for AIScriptGenerator."""
    
    def test_initialization_with_disabled_ai(self):
        """Test initialization with AI disabled."""
        config = AIScriptGeneratorConfig(enable_ai=False)
        generator = AIScriptGenerator(config=config)
        assert generator.is_available() is False
    
    def test_initialization_with_default_config(self):
        """Test initialization with default config."""
        generator = AIScriptGenerator()
        # Should not be available if Ollama is not running
        assert generator.config.model == "qwen2.5:14b-instruct"
    
    def test_generate_full_script_returns_none_when_unavailable(self, sample_idea_data):
        """Test that generate_full_script returns None when AI is unavailable."""
        config = AIScriptGeneratorConfig(enable_ai=False)
        generator = AIScriptGenerator(config=config)
        
        result = generator.generate_full_script(
            idea_data=sample_idea_data,
            title="The Mystery of the Abandoned House"
        )
        
        assert result is None
    
    def test_generate_hook_returns_none_when_unavailable(self, sample_idea_data):
        """Test that generate_hook returns None when AI is unavailable."""
        config = AIScriptGeneratorConfig(enable_ai=False)
        generator = AIScriptGenerator(config=config)
        
        result = generator.generate_hook(
            idea_data=sample_idea_data,
            title="Test Title"
        )
        
        assert result is None
    
    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    @patch(AI_SCRIPT_GEN_REQUESTS_POST)
    def test_generate_full_script_with_mock_api(self, mock_post, mock_get, sample_idea_data):
        """Test script generation with mocked Ollama API."""
        # Mock API availability check
        mock_get.return_value = MagicMock(status_code=200)
        
        # Mock script generation response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Every night at midnight, I return to the same moment. "
                       "The clock strikes twelve, and I'm standing at the entrance "
                       "of the abandoned house again. This is the story of how I "
                       "discovered the time loop that changed my life forever."
        }
        mock_post.return_value = mock_response
        
        generator = AIScriptGenerator()
        
        result = generator.generate_full_script(
            idea_data=sample_idea_data,
            title="The Mystery of the Abandoned House",
            target_duration_seconds=60
        )
        
        assert result is not None
        assert len(result) > 0
        # Verify API was called
        mock_post.assert_called_once()
    
    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    @patch(AI_SCRIPT_GEN_REQUESTS_POST)
    def test_prompt_contains_qwen_model(self, mock_post, mock_get, sample_idea_data):
        """Test that the API call uses Qwen model."""
        mock_get.return_value = MagicMock(status_code=200)
        mock_post.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"response": "Test script content"})
        )
        
        generator = AIScriptGenerator()
        generator.generate_full_script(
            idea_data=sample_idea_data,
            title="Test Title"
        )
        
        # Verify the model parameter - safely extract json_data
        call_args = mock_post.call_args
        json_data = None
        if call_args.kwargs:
            json_data = call_args.kwargs.get('json')
        if json_data is None and len(call_args) > 1 and call_args[1]:
            json_data = call_args[1].get('json')
        
        assert json_data is not None, "API call should include json parameter"
        assert json_data['model'] == 'qwen2.5:14b-instruct'


class TestGenerateAiScriptConvenience:
    """Tests for the generate_ai_script convenience function."""
    
    def test_returns_none_when_ai_disabled(self, sample_idea_data):
        """Test convenience function returns None when AI is disabled."""
        config = AIScriptGeneratorConfig(enable_ai=False)
        result = generate_ai_script(
            idea_data=sample_idea_data,
            title="Test Title",
            config=config
        )
        assert result is None
    
    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    @patch(AI_SCRIPT_GEN_REQUESTS_POST)
    def test_generates_script_with_mock_api(self, mock_post, mock_get, sample_idea_data):
        """Test convenience function with mocked API."""
        mock_get.return_value = MagicMock(status_code=200)
        mock_post.return_value = MagicMock(
            status_code=200,
            json=MagicMock(return_value={"response": "Generated script text"})
        )
        
        result = generate_ai_script(
            idea_data=sample_idea_data,
            title="Test Title"
        )
        
        assert result is not None


class TestScriptGeneratorAIIntegration:
    """Tests for ScriptGenerator AI integration."""
    
    def test_config_has_ai_settings(self):
        """Test that ScriptGeneratorConfig has AI settings."""
        config = ScriptGeneratorConfig()
        assert hasattr(config, 'use_ai')
        assert hasattr(config, 'ai_model')
        assert hasattr(config, 'ai_api_base')
        assert hasattr(config, 'ai_temperature')
        assert hasattr(config, 'ai_timeout')
    
    def test_default_ai_model_is_qwen(self):
        """Test that default AI model is Qwen2.5-14B-Instruct."""
        config = ScriptGeneratorConfig()
        assert config.ai_model == "qwen2.5:14b-instruct"
    
    def test_use_ai_enabled_by_default(self):
        """Test that AI is enabled by default."""
        config = ScriptGeneratorConfig()
        assert config.use_ai is True
    
    def test_generator_has_is_ai_available_method(self):
        """Test that ScriptGenerator has is_ai_available method."""
        generator = ScriptGenerator()
        assert hasattr(generator, 'is_ai_available')
        assert isinstance(generator.is_ai_available(), bool)
    
    def test_generator_falls_back_to_rule_based(self, sample_idea):
        """Test that generator falls back to rule-based when AI unavailable."""
        # Disable AI to force fallback
        config = ScriptGeneratorConfig(use_ai=False)
        generator = ScriptGenerator(config=config)
        
        script = generator.generate_script_v1(
            idea=sample_idea,
            title="The Mystery of the Abandoned House"
        )
        
        assert script is not None
        assert isinstance(script, ScriptV1)
        assert script.full_text is not None
        assert len(script.sections) > 0
        # Should indicate rule-based generation
        assert script.metadata.get('ai_generated') is False
    
    def test_metadata_includes_ai_info(self, sample_idea):
        """Test that script metadata includes AI generation info."""
        config = ScriptGeneratorConfig(use_ai=False)
        generator = ScriptGenerator(config=config)
        
        script = generator.generate_script_v1(
            idea=sample_idea,
            title="Test Title"
        )
        
        assert 'ai_generated' in script.metadata
        assert 'generation_config' in script.metadata
        assert 'use_ai' in script.metadata['generation_config']
        assert 'ai_model' in script.metadata['generation_config']
    
    @patch(SCRIPT_GEN_AI_MODULE)
    def test_ai_generation_with_mock(self, mock_get_module, sample_idea):
        """Test AI generation with mocked AI module."""
        # Create a mock AI generator
        mock_ai_generator = MagicMock()
        mock_ai_generator.is_available.return_value = True
        mock_ai_generator.generate_full_script.return_value = (
            "Every night at midnight, I return. This is my story of discovery."
        )
        
        mock_module = MagicMock()
        mock_module.AIScriptGeneratorConfig = AIScriptGeneratorConfig
        mock_module.AIScriptGenerator.return_value = mock_ai_generator
        mock_get_module.return_value = mock_module
        
        config = ScriptGeneratorConfig(use_ai=True)
        generator = ScriptGenerator(config=config)
        
        # Force reinitialize with mock
        generator._ai_generator = mock_ai_generator
        generator._ai_available = True
        
        script = generator.generate_script_v1(
            idea=sample_idea,
            title="The Mystery of the Abandoned House"
        )
        
        assert script is not None
        assert script.metadata.get('ai_generated') is True
        assert 'AI-powered' in script.notes


class TestScriptGeneratorConfigOverrides:
    """Tests for configuration overrides."""
    
    def test_can_override_use_ai_in_kwargs(self, sample_idea):
        """Test that use_ai can be overridden in generate_script_v1."""
        config = ScriptGeneratorConfig(use_ai=True)
        generator = ScriptGenerator(config=config)
        
        # Override to disable AI for this specific call
        script = generator.generate_script_v1(
            idea=sample_idea,
            title="Test Title",
            use_ai=False
        )
        
        assert script is not None
        assert script.metadata.get('ai_generated') is False
    
    def test_can_override_ai_model_in_kwargs(self, sample_idea):
        """Test that ai_model can be overridden in generate_script_v1."""
        config = ScriptGeneratorConfig(use_ai=False)  # Disable to avoid actual API calls
        generator = ScriptGenerator(config=config)
        
        script = generator.generate_script_v1(
            idea=sample_idea,
            title="Test Title",
            ai_model="llama3.1:8b"
        )
        
        assert script is not None
        assert script.metadata['generation_config']['ai_model'] == "llama3.1:8b"


class TestAIPromptEngineering:
    """Tests for AI prompt engineering."""
    
    def test_platform_instructions_exist(self):
        """Test that platform-specific instructions exist."""
        generator = AIScriptGenerator()
        
        platforms = ['youtube_short', 'youtube_medium', 'youtube_long', 'tiktok', 'instagram_reel']
        for platform in platforms:
            instructions = generator._get_platform_instructions(platform)
            assert instructions is not None
            assert len(instructions) > 0
    
    def test_full_script_prompt_includes_key_elements(self, sample_idea_data):
        """Test that full script prompt includes key elements."""
        generator = AIScriptGenerator()
        
        prompt = generator._create_full_script_prompt(
            idea_data=sample_idea_data,
            title="Test Title",
            target_duration=90,
            platform="youtube_medium",
            tone="engaging"
        )
        
        # Should include title
        assert "Test Title" in prompt
        # Should include concept
        assert sample_idea_data['concept'] in prompt
        # Should include tone
        assert "engaging" in prompt
        # Should include structure guidance
        assert "Hook" in prompt or "hook" in prompt
        assert "Body" in prompt or "body" in prompt
        assert "Conclusion" in prompt or "conclusion" in prompt


class TestAIScriptGeneratorRobustness:
    """Tests for AI generator robustness and error handling."""
    
    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    def test_handles_connection_error(self, mock_get, sample_idea_data):
        """Test handling of connection errors."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        generator = AIScriptGenerator()
        
        # Should not raise, should return None
        result = generator.generate_full_script(
            idea_data=sample_idea_data,
            title="Test Title"
        )
        
        # Generator should be unavailable
        assert generator.is_available() is False
    
    @patch(AI_SCRIPT_GEN_REQUESTS_GET)
    @patch(AI_SCRIPT_GEN_REQUESTS_POST)
    def test_handles_api_error(self, mock_post, mock_get, sample_idea_data):
        """Test handling of API errors."""
        import requests
        mock_get.return_value = MagicMock(status_code=200)
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        
        generator = AIScriptGenerator()
        
        # Should not raise, should return None
        result = generator.generate_full_script(
            idea_data=sample_idea_data,
            title="Test Title"
        )
        
        assert result is None
    
    def test_handles_empty_idea_data(self):
        """Test handling of empty idea data."""
        config = AIScriptGeneratorConfig(enable_ai=False)
        generator = AIScriptGenerator(config=config)
        
        result = generator.generate_full_script(
            idea_data={},
            title="Test Title"
        )
        
        # Should return None when AI is disabled
        assert result is None
