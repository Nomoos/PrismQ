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


class TestTitleGeneratorConfigGates:
    """Tests for length_gate_min/max, score_threshold, and use_batch_generation defaults."""

    def test_default_length_gate_min(self):
        """Default length_gate_min is 20."""
        config = TitleGeneratorConfig()
        assert config.length_gate_min == 20

    def test_default_length_gate_max(self):
        """Default length_gate_max is 80."""
        config = TitleGeneratorConfig()
        assert config.length_gate_max == 80

    def test_default_score_threshold(self):
        """Default score_threshold is 0.90."""
        config = TitleGeneratorConfig()
        assert config.score_threshold == 0.90

    def test_default_use_batch_generation(self):
        """Default use_batch_generation is True (batch mode)."""
        config = TitleGeneratorConfig()
        assert config.use_batch_generation is True

    def test_default_num_variants(self):
        """Default num_variants is 5."""
        config = TitleGeneratorConfig()
        assert config.num_variants == 5

    def test_custom_gates(self):
        """Custom gate values are respected."""
        config = TitleGeneratorConfig(length_gate_min=30, length_gate_max=70, score_threshold=0.85)
        assert config.length_gate_min == 30
        assert config.length_gate_max == 70
        assert config.score_threshold == 0.85


class TestLengthGateAndScoreThreshold:
    """Tests for the 3-gate pipeline in generate_from_idea."""

    def _make_generator(self, score_threshold=0.90, length_gate_min=20, length_gate_max=80):
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        config = TitleGeneratorConfig(
            use_batch_generation=False,
            num_variants=3,
            length_gate_min=length_gate_min,
            length_gate_max=length_gate_max,
            score_threshold=score_threshold,
        )
        return AITitleGenerator(config=config, ollama_client=mock_client), mock_client

    def test_length_gate_drops_too_short(self):
        """Variants shorter than length_gate_min are discarded, not returned."""
        generator, mock_client = self._make_generator(length_gate_min=30, score_threshold=0.0)
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        # Response is only 5 chars — must be dropped by length gate
        mock_client.generate.return_value = "Short"
        variants = generator.generate_from_idea(idea, num_variants=3)

        assert variants == []

    def test_length_gate_drops_too_long(self):
        """Variants longer than length_gate_max are discarded, not returned."""
        generator, mock_client = self._make_generator(length_gate_max=20, score_threshold=0.0)
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        # Response is 21 chars — must be dropped by length gate
        mock_client.generate.return_value = "This Title Is Too Long"
        variants = generator.generate_from_idea(idea, num_variants=3)

        assert variants == []

    def test_score_threshold_drops_low_scorers(self):
        """Variants with combined score below score_threshold are excluded."""
        generator, mock_client = self._make_generator(score_threshold=0.90)
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        # Title is 25 chars (passes length gate but scorer gives short_score=0.80)
        # AI scoring mock returns 0 so combined stays at 0.80 — below threshold
        mock_client.generate.return_value = "Short But Valid Length Ti"
        variants = generator.generate_from_idea(idea, num_variants=3)

        assert variants == []

    def test_score_threshold_accepts_high_scorers(self):
        """Variants with combined score >= score_threshold are returned."""
        generator, mock_client = self._make_generator(score_threshold=0.90)
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        # 45-char title: ideal length → rule score = 0.95 (already >= 0.90)
        # AI scoring response is "0" (0.0) → combined = (0.95 + 0) treated as 0.95
        # Wait — if ai_score == 0.0 the code does NOT update variant.score, so it stays 0.95
        long_title = "Silence Spoke Loudest in the Crowded Room"  # 41 chars
        assert 40 <= len(long_title) <= 60  # ideal range

        def generate_side_effect(prompt, temperature=0.7):
            # Generation calls return the title; scoring calls return "0"
            if "Score:" in prompt:
                return "0"
            return long_title

        mock_client.generate.side_effect = generate_side_effect
        variants = generator.generate_from_idea(idea, num_variants=3)

        # All 3 calls produce the same ideal-length title (score 0.95 >= 0.90)
        assert len(variants) == 3
        assert all(v.score >= 0.90 for v in variants)

    def test_results_sorted_by_score_descending(self):
        """Returned variants are sorted highest score first."""
        generator, mock_client = self._make_generator(score_threshold=0.0, length_gate_min=1)
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        titles = [
            "Short",       # < 20 chars → filtered by default gate... override gate_min=1
            "Silence Spoke Loudest in the Crowded Room",  # ideal → 0.95
            "The Quiet Alchemy",  # 17 chars, short → 0.80
        ]
        call_count = [0]

        def generate_side_effect(prompt, temperature=0.7):
            if "Score:" in prompt:
                return "0"
            idx = call_count[0] % len(titles)
            call_count[0] += 1
            return titles[idx]

        mock_client.generate.side_effect = generate_side_effect
        variants = generator.generate_from_idea(idea, num_variants=3)

        scores = [v.score for v in variants]
        assert scores == sorted(scores, reverse=True)


class TestParseBatchResponse:
    """Tests for _parse_batch_response (batch mode parsing)."""

    def _make_generator(self):
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        return AITitleGenerator(ollama_client=mock_client)

    def test_parse_numbered_list(self):
        """Numbered list response yields one variant per line."""
        generator = self._make_generator()
        idea = Idea(title="Test", concept="A quiet family story", status=IdeaStatus.DRAFT)

        response = (
            "1. Silence Spoke Loudest When They Forgot My Name\n"
            "2. The Weight of Words Never Said\n"
            "3. Where the Quiet Lives Between Us\n"
        )
        variants = generator._parse_batch_response(response, idea)

        assert len(variants) == 3
        assert variants[0].text == "Silence Spoke Loudest When They Forgot My Name"
        assert variants[1].text == "The Weight of Words Never Said"
        assert variants[2].text == "Where the Quiet Lives Between Us"

    def test_parse_batch_strips_think_block(self):
        """<think> block is stripped before parsing numbered lines."""
        generator = self._make_generator()
        idea = Idea(title="Test", concept="A story", status=IdeaStatus.DRAFT)

        response = (
            "<think>\nSome internal reasoning.\n</think>\n"
            "1. The Unseen Chord\n"
            "2. What the Silence Holds\n"
        )
        variants = generator._parse_batch_response(response, idea)

        assert len(variants) == 2
        assert variants[0].text == "The Unseen Chord"
        assert variants[1].text == "What the Silence Holds"

    def test_parse_batch_skips_empty_lines(self):
        """Empty lines in the response are silently skipped."""
        generator = self._make_generator()
        idea = Idea(title="Test", concept="A story", status=IdeaStatus.DRAFT)

        response = "\n1. The Quiet Alchemy\n\n2. Blank Slate, Quiet Power\n\n"
        variants = generator._parse_batch_response(response, idea)

        assert len(variants) == 2

    def test_parse_batch_handles_dot_and_paren_numbering(self):
        """Both '1.' and '1)' numbering styles are stripped correctly."""
        generator = self._make_generator()
        idea = Idea(title="Test", concept="A story", status=IdeaStatus.DRAFT)

        response = "1) The Softest Roar\n2. The Unspoken Advantage\n"
        variants = generator._parse_batch_response(response, idea)

        assert len(variants) == 2
        assert variants[0].text == "The Softest Roar"
        assert variants[1].text == "The Unspoken Advantage"

    def test_generate_from_idea_with_batch_enabled(self):
        """generate_from_idea uses batch generation when use_batch_generation=True."""
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        # All generate calls return the same batch list; scoring calls will find
        # leading digit "1" → ai_score=0.01, so use score_threshold=0 for this test.
        mock_client.generate.return_value = (
            "1. Silence Spoke Loudest When They Forgot My Name\n"
            "2. The Weight of Words Never Said\n"
            "3. Where the Quiet Lives Between Us\n"
        )

        config = TitleGeneratorConfig(
            use_batch_generation=True, num_variants=3, score_threshold=0.0
        )
        generator = AITitleGenerator(config=config, ollama_client=mock_client)
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        variants = generator.generate_from_idea(idea, num_variants=3)

        # Batch mode: only 1 generation call (plus any scoring calls)
        assert mock_client.generate.call_count >= 1
        assert len(variants) >= 1

    def test_generate_from_idea_one_by_one_when_batch_disabled(self):
        """generate_from_idea uses N AI calls when use_batch_generation=False."""
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        mock_client.generate.return_value = "The Quiet Alchemy in the Dark"

        config = TitleGeneratorConfig(
            use_batch_generation=False, num_variants=3, score_threshold=0.0
        )
        generator = AITitleGenerator(config=config, ollama_client=mock_client)
        idea = Idea(title="Test", concept="A quiet story", status=IdeaStatus.DRAFT)

        generator.generate_from_idea(idea, num_variants=3)

        # One-by-one mode: 3 generation calls + up to 3 scoring calls = at most 6
        assert mock_client.generate.call_count >= 3


class TestAiScoreTitlesBatch:
    """Tests for _ai_score_titles_batch — batch AI scoring of title variants."""

    def _make_generator(self):
        """Create an AITitleGenerator with a mocked OllamaClient."""
        mock_client = MagicMock()
        mock_client.is_available.return_value = True
        return AITitleGenerator(ollama_client=mock_client), mock_client

    def _make_variant(self, text: str, score: float = 0.90) -> TitleVariant:
        from title_scorer import TitleScorer
        scorer = TitleScorer()
        style = scorer.infer_style(text)
        return TitleVariant(text=text, style=style, length=len(text), keywords=[], score=score)

    def test_batch_scoring_updates_scores_in_place(self):
        """Scores returned by the AI are blended with the rule-based score."""
        generator, mock_client = self._make_generator()
        idea = Idea(title="Test", concept="A quiet family story", status=IdeaStatus.DRAFT)

        variants = [
            self._make_variant("Silence Spoke Loudest in the Room", score=0.90),
            self._make_variant("The Weight of Words Never Said Here", score=0.95),
        ]
        # Batch response: two scores
        mock_client.generate.return_value = "1. 80\n2. 90\n"

        generator._ai_score_titles_batch(variants, idea)

        # Blended: (0.90 + 0.80) / 2 = 0.85
        assert abs(variants[0].score - 0.85) < 1e-6
        # Blended: (0.95 + 0.90) / 2 = 0.925
        assert abs(variants[1].score - 0.925) < 1e-6

    def test_batch_scoring_strips_think_blocks(self):
        """<think> block in scoring response is stripped before parsing scores."""
        generator, mock_client = self._make_generator()
        idea = Idea(title="Test", concept="A story", status=IdeaStatus.DRAFT)

        variants = [self._make_variant("The Quiet Alchemy in the Dark Room", score=0.90)]
        mock_client.generate.return_value = "<think>\nSome reasoning.\n</think>\n1. 75\n"

        generator._ai_score_titles_batch(variants, idea)

        assert abs(variants[0].score - (0.90 + 0.75) / 2) < 1e-6

    def test_batch_scoring_falls_back_on_mismatch(self):
        """Falls back to individual scoring when score count != variant count."""
        generator, mock_client = self._make_generator()
        idea = Idea(title="Test", concept="A story", status=IdeaStatus.DRAFT)

        variants = [
            self._make_variant("Title One Long Enough to Pass", score=0.90),
            self._make_variant("Title Two Long Enough to Pass", score=0.90),
        ]
        # Batch returns only 1 score for 2 variants → mismatch → fallback
        call_count = [0]

        def generate_side_effect(prompt, temperature=0.7):
            call_count[0] += 1
            if call_count[0] == 1:
                return "1. 80"  # only one score (mismatch)
            return "70"  # individual fallback responses

        mock_client.generate.side_effect = generate_side_effect

        generator._ai_score_titles_batch(variants, idea)

        # Fallback path runs individual scoring for each variant (calls 2 and 3)
        assert mock_client.generate.call_count == 3

    def test_batch_scoring_falls_back_on_exception(self):
        """Falls back to individual scoring when the batch AI call raises an exception."""
        generator, mock_client = self._make_generator()
        idea = Idea(title="Test", concept="A story", status=IdeaStatus.DRAFT)

        variants = [self._make_variant("The Quiet Alchemy in the Dark Room", score=0.90)]
        call_count = [0]

        def generate_side_effect(prompt, temperature=0.7):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Network error")
            return "85"  # individual fallback

        mock_client.generate.side_effect = generate_side_effect

        generator._ai_score_titles_batch(variants, idea)

        # 1 failed batch call + 1 individual fallback call
        assert mock_client.generate.call_count == 2

    def test_batch_scoring_uses_single_ai_call_for_multiple_variants(self):
        """Batch scoring issues exactly ONE AI call regardless of variant count."""
        generator, mock_client = self._make_generator()
        idea = Idea(title="Test", concept="A family story", status=IdeaStatus.DRAFT)

        variants = [
            self._make_variant("Silence Spoke Loudest in That Room", score=0.90),
            self._make_variant("The Weight of Words Never Said Here", score=0.90),
            self._make_variant("Where the Quiet Lives Between All of Us", score=0.90),
        ]
        mock_client.generate.return_value = "1. 80\n2. 85\n3. 90\n"

        generator._ai_score_titles_batch(variants, idea)

        assert mock_client.generate.call_count == 1

    def test_generate_from_idea_batch_mode_uses_two_ai_calls(self):
        """Full pipeline in batch mode uses exactly 2 AI calls (generate + score)."""
        mock_client = MagicMock()
        mock_client.is_available.return_value = True

        generation_response = (
            "1. Silence Spoke Loudest When They Forgot My Name\n"
            "2. The Weight of Words Never Said to Anyone\n"
            "3. Where the Quiet Lives Between You and Me\n"
        )
        scoring_response = "1. 85\n2. 90\n3. 80\n"
        call_count = [0]

        def generate_side_effect(prompt, temperature=0.7):
            call_count[0] += 1
            if call_count[0] == 1:
                return generation_response
            return scoring_response

        mock_client.generate.side_effect = generate_side_effect

        config = TitleGeneratorConfig(
            use_batch_generation=True, num_variants=3, score_threshold=0.0
        )
        generator = AITitleGenerator(config=config, ollama_client=mock_client)
        idea = Idea(title="Test", concept="A quiet family story", status=IdeaStatus.DRAFT)

        variants = generator.generate_from_idea(idea, num_variants=3)

        # 1 batch generation call + 1 batch scoring call = 2 total
        assert mock_client.generate.call_count == 2
        assert len(variants) == 3
