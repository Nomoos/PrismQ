"""Tests for Idea Variants module (flavor-based API)."""

import os
import sys

import pytest
from unittest.mock import Mock, patch

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from idea_variants import (
    IdeaGenerator,
    FlavorSelector,
    IdeaFormatter,
    create_ideas_from_input,
    generate_idea_from_flavor,
    format_idea_as_text,
    pick_weighted_flavor,
    pick_multiple_weighted_flavors,
    pick_flavor_combination,
    list_flavors,
    get_flavor,
    get_flavor_count,
    DEFAULT_IDEA_COUNT,
    # Backward compatibility aliases
    list_templates,
    get_template,
)


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_default_idea_count_is_10(self):
        """Test that DEFAULT_IDEA_COUNT is 10 per report requirement."""
        assert DEFAULT_IDEA_COUNT == 10

    def test_default_idea_count_matches_flavor_selector(self):
        """Test that DEFAULT_IDEA_COUNT matches FlavorSelector.DEFAULT_COUNT."""
        assert DEFAULT_IDEA_COUNT == FlavorSelector.DEFAULT_COUNT

    def test_multi_flavor_chance_is_0_4(self):
        """Test that MULTI_FLAVOR_CHANCE is 0.4 (40% dual-flavor per report)."""
        assert FlavorSelector.MULTI_FLAVOR_CHANCE == 0.4

    def test_no_flavor_chance_is_0_05(self):
        """Test that NO_FLAVOR_CHANCE is 0.05 per spec."""
        assert FlavorSelector.NO_FLAVOR_CHANCE == 0.05


class TestFlavorRegistry:
    """Tests for the flavor registry (replaces old VARIANT_TEMPLATES tests)."""

    def test_flavors_available(self):
        """Test that flavors are loaded and available."""
        flavors = list_flavors()
        assert len(flavors) > 0

    def test_flavors_count_matches_get_flavor_count(self):
        """Test that list_flavors and get_flavor_count return consistent results."""
        assert len(list_flavors()) == get_flavor_count()

    def test_known_flavor_exists(self):
        """Test that known flavor names exist in the registry."""
        flavors = list_flavors()
        assert "Emotion-First Hook" in flavors
        assert "Mystery/Curiosity Gap" in flavors
        assert "Light Mystery + Adventure" in flavors

    def test_get_flavor_returns_dict(self):
        """Test that get_flavor returns a dictionary."""
        flavor = get_flavor("Emotion-First Hook")
        assert isinstance(flavor, dict)

    def test_get_flavor_has_required_fields(self):
        """Test that a flavor has expected structure fields."""
        flavor = get_flavor("Emotion-First Hook")
        assert "description" in flavor
        assert "weight" in flavor

    def test_get_unknown_flavor_raises_error(self):
        """Test that unknown flavor raises KeyError."""
        with pytest.raises(KeyError):
            get_flavor("nonexistent_flavor_xyz")

    def test_flavor_count_is_at_least_10(self):
        """Test that at least 10 flavors exist to support default batch size."""
        assert get_flavor_count() >= 10


class TestBackwardCompatibilityAliases:
    """Tests for backward compatibility aliases."""

    def test_list_templates_is_alias_for_list_flavors(self):
        """Test that list_templates returns same result as list_flavors."""
        assert list_templates() == list_flavors()

    def test_get_template_is_alias_for_get_flavor(self):
        """Test that get_template returns same result as get_flavor."""
        flavor_name = list_flavors()[0]
        assert get_template(flavor_name) == get_flavor(flavor_name)


class TestIdeaGeneratorClass:
    """Tests for the IdeaGenerator class."""

    def test_initialization_without_ai(self):
        """Test IdeaGenerator can be initialized without AI."""
        generator = IdeaGenerator(use_ai=False)
        assert generator.use_ai is False
        assert generator.ai_generator is None

    def test_initialization_with_ai_available(self):
        """Test IdeaGenerator initializes AI when available."""
        with patch('idea_variants.AIIdeaGenerator') as mock_cls:
            mock_instance = Mock()
            mock_instance.available = True
            mock_cls.return_value = mock_instance

            generator = IdeaGenerator(use_ai=True)
            assert generator.ai_generator is not None
            assert generator.use_ai is True

    def test_initialization_with_ai_unavailable_raises(self):
        """Test IdeaGenerator raises RuntimeError when AI is unavailable."""
        with patch('idea_variants.AIIdeaGenerator') as mock_cls:
            mock_instance = Mock()
            mock_instance.available = False
            mock_cls.return_value = mock_instance

            with pytest.raises(RuntimeError, match="Ollama is not available"):
                IdeaGenerator(use_ai=True)

    def test_generate_from_flavor_requires_nonempty_input(self):
        """Test that empty input raises ValueError."""
        generator = IdeaGenerator(use_ai=False)
        with pytest.raises(ValueError):
            generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text="",
            )

    def test_generate_from_flavor_without_ai_raises(self):
        """Test that generation without AI raises RuntimeError."""
        generator = IdeaGenerator(use_ai=False)
        with pytest.raises(RuntimeError, match="AI generator not available"):
            generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text="Test input",
            )

    def test_generate_from_flavor_returns_dict_with_text(self):
        """Test that generate_from_flavor returns dict with required keys."""
        with patch('idea_variants.AIIdeaGenerator') as mock_cls:
            mock_instance = Mock()
            mock_instance.available = True
            ai_text = "Generated idea content " * 10
            mock_instance.generate_with_custom_prompt = lambda *a, **kw: ai_text
            mock_cls.return_value = mock_instance

            generator = IdeaGenerator(use_ai=True)
            result = generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text="Test input",
            )

            assert isinstance(result, dict)
            assert 'text' in result
            assert 'variant_name' in result
            assert 'source_input' in result
            assert result['source_input'] == "Test input"

    def test_generate_from_flavor_saves_to_db_with_version_1(self):
        """Test that ideas are saved to DB with version=1 per report requirement."""
        with patch('idea_variants.AIIdeaGenerator') as mock_cls:
            mock_instance = Mock()
            mock_instance.available = True
            ai_text = "Generated idea content " * 10
            mock_instance.generate_with_custom_prompt = lambda *a, **kw: ai_text
            mock_cls.return_value = mock_instance

            mock_db = Mock()
            mock_db.insert_idea.return_value = 42

            generator = IdeaGenerator(use_ai=True)
            result = generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text="Test input",
                db=mock_db,
            )

            # Verify db.insert_idea was called with version=1
            mock_db.insert_idea.assert_called_once_with(text=ai_text, version=1)
            assert result.get('idea_id') == 42

    def test_generate_from_flavor_unknown_flavor_raises(self):
        """Test that unknown flavor name raises KeyError."""
        with patch('idea_variants.AIIdeaGenerator') as mock_cls:
            mock_instance = Mock()
            mock_instance.available = True
            mock_cls.return_value = mock_instance

            generator = IdeaGenerator(use_ai=True)
            with pytest.raises(KeyError):
                generator.generate_from_flavor(
                    flavor_name="nonexistent_flavor_xyz",
                    input_text="Test input",
                )

    def test_generate_from_flavor_raw_input_passed_to_ai(self):
        """Test that input text is passed to AI without any modification."""
        with patch('idea_variants.AIIdeaGenerator') as mock_cls:
            mock_instance = Mock()
            mock_instance.available = True
            captured = []

            def capture_generate(input_text, **kwargs):
                captured.append(input_text)
                return "Generated idea content " * 10

            mock_instance.generate_with_custom_prompt = capture_generate
            mock_cls.return_value = mock_instance

            generator = IdeaGenerator(use_ai=True)
            raw_input = "Raw input with special chars: !@#$%^&*()"
            generator.generate_from_flavor(
                flavor_name="Emotion-First Hook",
                input_text=raw_input,
            )

            assert len(captured) == 1
            assert captured[0] == raw_input

    def test_generate_multiple_returns_list(self):
        """Test that generate_multiple returns a list."""
        with patch('idea_variants.AIIdeaGenerator') as mock_cls:
            mock_instance = Mock()
            mock_instance.available = True
            mock_instance.generate_with_custom_prompt = lambda *a, **kw: "Generated content " * 10
            mock_cls.return_value = mock_instance

            generator = IdeaGenerator(use_ai=True)
            results = generator.generate_multiple(
                input_text="Test input",
                count=3,
                specific_flavors=["Emotion-First Hook", "Mystery/Curiosity Gap", "Light Mystery + Adventure"],
            )

            assert isinstance(results, list)
            assert len(results) == 3


class TestIdeaFormatterClass:
    """Tests for the IdeaFormatter class."""

    def test_format_as_text_returns_string(self):
        """Test that format_as_text returns a string."""
        formatter = IdeaFormatter()
        result = formatter.format_as_text({'text': 'Some content', 'hook': 'Hook text'})
        assert isinstance(result, str)

    def test_format_idea_as_text_convenience(self):
        """Test the format_idea_as_text convenience function."""
        result = format_idea_as_text({'hook': 'A compelling hook here', 'text': 'Idea text'})
        assert isinstance(result, str)


class TestFlavorSelectionFunctions:
    """Tests for flavor selection convenience functions."""

    def test_pick_weighted_flavor_returns_string(self):
        """Test that pick_weighted_flavor returns a string flavor name."""
        flavor = pick_weighted_flavor()
        assert isinstance(flavor, str)
        assert flavor in list_flavors()

    def test_pick_multiple_weighted_flavors_default_10(self):
        """Test that pick_multiple_weighted_flavors returns 10 by default."""
        flavors = pick_multiple_weighted_flavors()
        assert len(flavors) == 10

    def test_pick_multiple_weighted_flavors_custom_count(self):
        """Test pick_multiple_weighted_flavors with custom count."""
        flavors = pick_multiple_weighted_flavors(count=5)
        assert len(flavors) == 5

    def test_pick_flavor_combination_returns_list(self):
        """Test that pick_flavor_combination returns a list."""
        result = pick_flavor_combination(seed=0)
        assert isinstance(result, list)

    def test_pick_flavor_combination_with_no_flavor_chance_1(self):
        """Test pick_flavor_combination returns empty list when no_flavor_chance=1.0."""
        result = pick_flavor_combination(seed=0, no_flavor_chance=1.0)
        assert result == []

    def test_pick_flavor_combination_with_primary(self):
        """Test that primary_flavor is first in combination."""
        primary = "Mystery/Curiosity Gap"
        result = pick_flavor_combination(primary_flavor=primary, seed=42, no_flavor_chance=0.0)
        assert result[0] == primary


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_create_ideas_from_input_raises_when_ai_unavailable(self):
        """Test that create_ideas_from_input raises when AI is unavailable."""
        with patch('idea_variants.AIIdeaGenerator') as mock_cls:
            mock_instance = Mock()
            mock_instance.available = False
            mock_cls.return_value = mock_instance

            with pytest.raises(RuntimeError):
                create_ideas_from_input("Test", count=2)

    def test_generate_idea_from_flavor_raises_when_ai_unavailable(self):
        """Test that generate_idea_from_flavor raises when AI is unavailable."""
        with patch('idea_variants.AIIdeaGenerator') as mock_cls:
            mock_instance = Mock()
            mock_instance.available = False
            mock_cls.return_value = mock_instance

            with pytest.raises(RuntimeError):
                generate_idea_from_flavor("Emotion-First Hook", "Test input")
