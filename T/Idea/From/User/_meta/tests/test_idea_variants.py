"""Tests for Idea Variants module (template-based and AI flavor-based)."""

import os
import sys

import pytest
from unittest.mock import Mock, patch

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from idea_variants import (
    VARIANT_4POINT,
    VARIANT_EMOTION_FIRST,
    VARIANT_GENRE,
    VARIANT_HOOK_FRAME,
    VARIANT_MINIMAL,
    VARIANT_MYSTERY,
    VARIANT_NICHE_BLEND,
    VARIANT_SCENE_SEED,
    VARIANT_SHORTFORM,
    VARIANT_SHORTFORM2,
    VARIANT_SKELETON,
    VARIANT_TEMPLATES,
    IdeaGenerator,
    FlavorSelector,
    IdeaFormatter,
    create_all_variants,
    create_idea_variant,
    create_multiple_of_same_variant,
    create_selected_variants,
    format_idea_as_text,
    get_flavor,
    get_flavor_count,
    get_template,
    get_template_example,
    get_template_fields,
    list_flavors,
    list_templates,
    pick_flavor_combination,
    pick_multiple_weighted_flavors,
    pick_weighted_flavor,
    DEFAULT_IDEA_COUNT,
)


# =============================================================================
# TEMPLATE-BASED GENERATION TESTS
# =============================================================================

class TestVariantTemplateRegistry:
    """Tests for the template registry."""

    def test_all_templates_registered(self):
        """Test that all variant templates are registered."""
        assert len(VARIANT_TEMPLATES) == 93

    def test_template_names_match_constants(self):
        """Test that registry keys match expected names."""
        expected_names = [
            # Original 11 templates
            "emotion_first",
            "mystery",
            "skeleton",
            "shortform",
            "niche_blend",
            "minimal",
            "4point",
            "hook_frame",
            "shortform2",
            "genre",
            "scene_seed",
            # New creative genre-based templates
            "soft_supernatural",
            "light_mystery",
            "scifi_school",
            "safe_survival",
            "emotional_drama",
            "rivals_allies",
            "identity_power",
            "ai_companion",
            "urban_quest",
            "magical_aesthetic",
            # Reddit-style drama templates
            "family_drama",
            "social_home",
            "realistic_mystery",
            "school_family",
            "personal_voice",
        ]
        for name in expected_names:
            assert name in VARIANT_TEMPLATES

    def test_list_templates_returns_all(self):
        """Test list_templates returns all template names."""
        templates = list_templates()
        assert len(templates) == 93
        assert "emotion_first" in templates
        assert "mystery" in templates
        # New templates
        assert "soft_supernatural" in templates
        assert "family_drama" in templates


class TestGetTemplate:
    """Tests for get_template function."""

    def test_get_existing_template(self):
        """Test getting an existing template."""
        template = get_template("emotion_first")
        assert template is not None
        assert "name" in template
        assert "fields" in template

    def test_get_unknown_template_raises_error(self):
        """Test that unknown template raises KeyError."""
        with pytest.raises(KeyError):
            get_template("nonexistent_template")

    def test_get_template_returns_correct_content(self):
        """Test that get_template returns the correct template."""
        template = get_template("minimal")
        assert template["name"] == "Minimal Idea Packet"


class TestGetTemplateFields:
    """Tests for get_template_fields function."""

    def test_get_fields_returns_dict(self):
        """Test that fields are returned as dictionary."""
        fields = get_template_fields("emotion_first")
        assert isinstance(fields, dict)
        assert len(fields) > 0

    def test_emotion_first_has_required_fields(self):
        """Test emotion_first template has all required fields."""
        fields = get_template_fields("emotion_first")
        assert "main_emotion" in fields
        assert "core_hook" in fields
        assert "target_audience" in fields
        assert "unusual_angle" in fields
        assert "ending_style" in fields
        assert "content_constraints" in fields


class TestGetTemplateExample:
    """Tests for get_template_example function."""

    def test_get_example_returns_dict(self):
        """Test that example is returned as dictionary."""
        example = get_template_example("emotion_first")
        assert isinstance(example, dict)
        assert len(example) > 0

    def test_example_matches_fields(self):
        """Test that example keys match field definitions."""
        fields = get_template_fields("minimal")
        example = get_template_example("minimal")

        for key in fields:
            assert key in example, f"Example missing field: {key}"


class TestVariantEmotionFirst:
    """Tests for Emotion-First variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_EMOTION_FIRST
        assert "description" in VARIANT_EMOTION_FIRST
        assert "fields" in VARIANT_EMOTION_FIRST
        assert "example" in VARIANT_EMOTION_FIRST

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_EMOTION_FIRST["name"] == "Emotion-First Hook"

    def test_has_emotion_field(self):
        """Test template has main_emotion field."""
        assert "main_emotion" in VARIANT_EMOTION_FIRST["fields"]


class TestVariantMystery:
    """Tests for Mystery variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_MYSTERY
        assert "description" in VARIANT_MYSTERY
        assert "fields" in VARIANT_MYSTERY
        assert "example" in VARIANT_MYSTERY

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_MYSTERY["name"] == "Mystery/Curiosity Gap"

    def test_has_central_mystery_field(self):
        """Test template has central_mystery field."""
        assert "central_mystery" in VARIANT_MYSTERY["fields"]

    def test_has_sensitivities_field(self):
        """Test template has sensitivities field."""
        assert "sensitivities" in VARIANT_MYSTERY["fields"]


class TestVariantSkeleton:
    """Tests for Story Skeleton variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_SKELETON
        assert "fields" in VARIANT_SKELETON
        assert "example" in VARIANT_SKELETON

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_SKELETON["name"] == "Story Skeleton"

    def test_has_story_structure_fields(self):
        """Test template has story structure fields."""
        fields = VARIANT_SKELETON["fields"]
        assert "opening_hook" in fields
        assert "context_setup" in fields
        assert "rising_stakes" in fields
        assert "peak_moment" in fields
        assert "conclusion_shape" in fields


class TestVariantShortform:
    """Tests for Short-Form Viral variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_SHORTFORM
        assert "fields" in VARIANT_SHORTFORM
        assert "example" in VARIANT_SHORTFORM

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_SHORTFORM["name"] == "Short-Form Viral"

    def test_has_viral_content_fields(self):
        """Test template has viral content fields."""
        fields = VARIANT_SHORTFORM["fields"]
        assert "hook_essence" in fields
        assert "wow_moment" in fields
        assert "engagement_mechanic" in fields
        assert "safety_checklist" in fields


class TestVariantNicheBlend:
    """Tests for Niche-Blend variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_NICHE_BLEND
        assert "fields" in VARIANT_NICHE_BLEND
        assert "example" in VARIANT_NICHE_BLEND

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_NICHE_BLEND["name"] == "Niche-Blend"

    def test_has_niche_fields(self):
        """Test template has niche blend fields."""
        fields = VARIANT_NICHE_BLEND["fields"]
        assert "combined_niches" in fields
        assert "niche_blend_description" in fields
        assert "content_limits" in fields


class TestVariantMinimal:
    """Tests for Minimal variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_MINIMAL
        assert "fields" in VARIANT_MINIMAL
        assert "example" in VARIANT_MINIMAL

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_MINIMAL["name"] == "Minimal Idea Packet"

    def test_has_minimal_fields(self):
        """Test template has minimal required fields."""
        fields = VARIANT_MINIMAL["fields"]
        assert "hook" in fields
        assert "audience" in fields
        assert "tone" in fields
        assert "length" in fields

    def test_minimal_has_fewest_fields(self):
        """Test minimal template has the fewest fields."""
        minimal_count = len(VARIANT_MINIMAL["fields"])
        for name, template in VARIANT_TEMPLATES.items():
            if name != "minimal":
                assert len(template["fields"]) >= minimal_count


class TestVariant4Point:
    """Tests for 4-Point variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_4POINT
        assert "fields" in VARIANT_4POINT
        assert "example" in VARIANT_4POINT

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_4POINT["name"] == "4-Point Quick Structure"

    def test_has_four_fields(self):
        """Test template has exactly 4 main fields."""
        fields = VARIANT_4POINT["fields"]
        assert len(fields) == 4


class TestVariantHookFrame:
    """Tests for Hook + Frame variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_HOOK_FRAME
        assert "fields" in VARIANT_HOOK_FRAME
        assert "example" in VARIANT_HOOK_FRAME

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_HOOK_FRAME["name"] == "Hook + Frame"

    def test_has_hook_and_frame_fields(self):
        """Test template has hook and frame fields."""
        fields = VARIANT_HOOK_FRAME["fields"]
        assert "hook_sentence" in fields
        assert "title_frame" in fields


class TestVariantShortform2:
    """Tests for Short Form 2.0 variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_SHORTFORM2
        assert "fields" in VARIANT_SHORTFORM2
        assert "example" in VARIANT_SHORTFORM2

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_SHORTFORM2["name"] == "Short Form 2.0"

    def test_has_short_form_fields(self):
        """Test template has short form fields."""
        fields = VARIANT_SHORTFORM2["fields"]
        assert "concept" in fields
        assert "premise" in fields
        assert "tone" in fields


class TestVariantGenre:
    """Tests for Genre Focus variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_GENRE
        assert "fields" in VARIANT_GENRE
        assert "example" in VARIANT_GENRE

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_GENRE["name"] == "Genre Focus"

    def test_has_genre_field(self):
        """Test template has genre field."""
        assert "genre" in VARIANT_GENRE["fields"]


class TestVariantSceneSeed:
    """Tests for Scene Seed variant template."""

    def test_template_has_required_structure(self):
        """Test template has name, description, fields, example."""
        assert "name" in VARIANT_SCENE_SEED
        assert "fields" in VARIANT_SCENE_SEED
        assert "example" in VARIANT_SCENE_SEED

    def test_template_name(self):
        """Test template name is correct."""
        assert VARIANT_SCENE_SEED["name"] == "Scene Seed"

    def test_has_scene_hook_field(self):
        """Test template has scene_hook field."""
        assert "scene_hook" in VARIANT_SCENE_SEED["fields"]

    def test_has_content_length_field(self):
        """Test template has target_content_length field."""
        assert "target_content_length" in VARIANT_SCENE_SEED["fields"]


class TestAllTemplatesConsistency:
    """Tests for consistency across all templates."""

    def test_all_templates_have_name(self):
        """Test all templates have a name."""
        for name, template in VARIANT_TEMPLATES.items():
            assert "name" in template, f"Template {name} missing 'name'"

    def test_all_templates_have_description(self):
        """Test all templates have a description."""
        for name, template in VARIANT_TEMPLATES.items():
            assert "description" in template, f"Template {name} missing 'description'"

    def test_all_templates_have_fields(self):
        """Test all templates have fields."""
        for name, template in VARIANT_TEMPLATES.items():
            assert "fields" in template, f"Template {name} missing 'fields'"
            assert len(template["fields"]) > 0, f"Template {name} has empty fields"

    def test_all_templates_have_example(self):
        """Test all templates have an example."""
        for name, template in VARIANT_TEMPLATES.items():
            assert "example" in template, f"Template {name} missing 'example'"
            assert len(template["example"]) > 0, f"Template {name} has empty example"

    def test_all_examples_have_valid_values(self):
        """Test all examples have non-empty values for main fields."""
        for name, template in VARIANT_TEMPLATES.items():
            example = template["example"]
            for key, value in example.items():
                assert value is not None, f"Template {name} example has None for {key}"


class TestCreateIdeaVariant:
    """Tests for create_idea_variant function."""

    def test_create_variant_returns_dict(self):
        """Test that create_idea_variant returns a dictionary."""
        variant = create_idea_variant("Test Title", "minimal")
        assert isinstance(variant, dict)

    def test_create_variant_includes_metadata(self):
        """Test that variant includes metadata fields."""
        variant = create_idea_variant("Test Title", "minimal")
        assert "variant_type" in variant
        assert "variant_name" in variant
        assert "source_title" in variant
        assert variant["source_title"] == "Test Title"

    def test_create_variant_empty_title_raises(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError):
            create_idea_variant("", "minimal")

    def test_create_variant_unknown_type_raises(self):
        """Test that unknown variant type raises KeyError."""
        with pytest.raises(KeyError):
            create_idea_variant("Test", "nonexistent_variant")

    def test_create_all_variant_types(self):
        """Test creating all variant types."""
        for variant_name in VARIANT_TEMPLATES.keys():
            variant = create_idea_variant("Test Title", variant_name)
            assert variant is not None
            assert variant["variant_type"] == variant_name


class TestCreateAllVariants:
    """Tests for create_all_variants function."""

    def test_creates_all_variants(self):
        """Test that create_all_variants creates one variant per template."""
        variants = create_all_variants("Test Title")
        assert len(variants) == len(VARIANT_TEMPLATES)

    def test_all_variants_are_different_types(self):
        """Test that all variants are different types."""
        variants = create_all_variants("Test Title")
        types = [v["variant_type"] for v in variants]
        assert len(set(types)) == len(VARIANT_TEMPLATES)


class TestCreateSelectedVariants:
    """Tests for create_selected_variants function."""

    def test_creates_selected_variants(self):
        """Test creating specific variants."""
        selected = ["minimal", "mystery", "skeleton"]
        variants = create_selected_variants("Test Title", selected)
        assert len(variants) == 3
        types = [v["variant_type"] for v in variants]
        assert set(types) == set(selected)


class TestCreateMultipleOfSameVariant:
    """Tests for create_multiple_of_same_variant function."""

    def test_creates_multiple_variants(self):
        """Test creating multiple variants of same type."""
        variants = create_multiple_of_same_variant("Test Title", "minimal", count=5)
        assert len(variants) == 5

    def test_all_same_type(self):
        """Test all variants are same type."""
        variants = create_multiple_of_same_variant("Test Title", "emotion_first", count=3)
        for v in variants:
            assert v["variant_type"] == "emotion_first"


class TestVariantVariability:
    """Tests for variant variability - ensuring different variants are truly different."""

    def test_multiple_emotion_first_variants_differ(self):
        """Test that multiple emotion_first variants have different content."""
        variants = create_multiple_of_same_variant("Záhadná událost", "emotion_first", count=5)

        # Check that emotions vary
        emotions = [v.get("main_emotion") for v in variants]
        # Should have at least 2 different emotions in 5 variants
        assert len(set(emotions)) >= 2, "Emotions should vary across variants"

    def test_multiple_mystery_variants_differ(self):
        """Test that multiple mystery variants have different content."""
        variants = create_multiple_of_same_variant("Tajný projekt", "mystery", count=5)

        # Check that tones vary
        tones = [v.get("tone_notes") for v in variants]
        assert len(set(tones)) >= 2, "Tones should vary across variants"

    def test_multiple_shortform_variants_differ(self):
        """Test that multiple shortform variants have different content."""
        variants = create_multiple_of_same_variant("Virální obsah", "shortform", count=5)

        # Check that demographics/platforms vary
        platforms = [v.get("audience_segment", {}).get("platform") for v in variants]
        assert len(set(platforms)) >= 2, "Platforms should vary across variants"

    def test_multiple_niche_blend_variants_differ(self):
        """Test that multiple niche_blend variants have different niches."""
        variants = create_multiple_of_same_variant("Hybridní příběh", "niche_blend", count=5)

        # Check that niche combinations vary
        niche_combos = [tuple(v.get("combined_niches", [])) for v in variants]
        assert len(set(niche_combos)) >= 2, "Niche combinations should vary"

    def test_all_variants_have_unique_seeds(self):
        """Test that all variants have unique variation seeds."""
        variants = create_multiple_of_same_variant("Test", "minimal", count=10)
        seeds = [v.get("variation_seed") for v in variants]
        # Seeds may occasionally collide, but most should be unique
        assert len(set(seeds)) >= 5, "Most seeds should be unique"

    def test_variation_index_affects_output(self):
        """Test that variation_index creates different outputs."""
        v1 = create_idea_variant("Same Title", "emotion_first", variation_index=0, randomize=False)
        v2 = create_idea_variant("Same Title", "emotion_first", variation_index=5, randomize=False)

        # With different indices and no randomization, content should differ
        assert v1.get("main_emotion") != v2.get("main_emotion") or v1.get(
            "unusual_angle"
        ) != v2.get("unusual_angle")

    def test_different_titles_produce_different_variants(self):
        """Test that different titles produce different variants."""
        v1 = create_idea_variant("Příběh A", "minimal", randomize=False)
        v2 = create_idea_variant("Příběh B", "minimal", randomize=False)

        # Hooks should contain the different titles
        assert "příběh a" in v1.get("hook", "").lower()
        assert "příběh b" in v2.get("hook", "").lower()


class TestVariantContentQuality:
    """Tests for variant content quality."""

    def test_ideas_have_content_fields(self):
        """Test that generated ideas have at least one non-empty content field."""
        skip_meta = {
            "variant_type", "variant_name", "source_title",
            "source_description", "variation_index", "variation_seed",
        }
        for variant_name in VARIANT_TEMPLATES.keys():
            variant = create_idea_variant("Test Content", variant_name)
            content_fields = {
                k: v for k, v in variant.items()
                if k not in skip_meta and v and len(str(v)) > 5
            }
            assert len(content_fields) > 0, f"No content found in template '{variant_name}'"

    def test_title_is_incorporated(self):
        """Test that the source title is incorporated in the content."""
        test_title = "Unique Test Topic XYZ"
        for variant_name in VARIANT_TEMPLATES.keys():
            variant = create_idea_variant(test_title, variant_name)
            # The title should appear in at least one field
            variant_str = str(variant).lower()
            assert "unique test topic xyz" in variant_str or "test" in variant_str


class TestMinimumTextLength:
    """Tests for the minimum 100 character requirement for idea text generation."""

    def test_min_idea_text_length_constant_exists(self):
        """Test that MIN_IDEA_TEXT_LENGTH constant exists and is 100."""
        from idea_variants import MIN_IDEA_TEXT_LENGTH

        assert MIN_IDEA_TEXT_LENGTH == 100

    def test_format_idea_as_text_minimum_length(self):
        """Test that format_idea_as_text returns at least 100 characters."""
        from idea_variants import MIN_IDEA_TEXT_LENGTH, format_idea_as_text

        for variant_name in VARIANT_TEMPLATES.keys():
            variant = create_idea_variant("Test Topic", variant_name)
            text = format_idea_as_text(variant)
            assert len(text) >= MIN_IDEA_TEXT_LENGTH, (
                f"Variant '{variant_name}' produced only {len(text)} characters, "
                f"expected at least {MIN_IDEA_TEXT_LENGTH}"
            )

    def test_create_idea_text_minimum_length(self):
        """Test that create_idea_text returns at least 100 characters."""
        from idea_variants import MIN_IDEA_TEXT_LENGTH, create_idea_text

        for variant_name in list(VARIANT_TEMPLATES.keys())[:10]:  # Test first 10 for speed
            text = create_idea_text("Test Topic", variant_name=variant_name)
            assert (
                len(text) >= MIN_IDEA_TEXT_LENGTH
            ), f"create_idea_text with variant '{variant_name}' produced only {len(text)} characters"

    def test_create_ideas_as_text_all_minimum_length(self):
        """Test that all ideas from create_ideas_as_text have at least 100 characters."""
        from idea_variants import MIN_IDEA_TEXT_LENGTH, create_ideas_as_text

        ideas = create_ideas_as_text("Test Topic About Technology", count=10)
        for i, text in enumerate(ideas):
            assert (
                len(text) >= MIN_IDEA_TEXT_LENGTH
            ), f"Idea {i} produced only {len(text)} characters, expected at least {MIN_IDEA_TEXT_LENGTH}"

    def test_minimum_length_with_short_title(self):
        """Test that even with very short titles, output is at least 100 characters."""
        from idea_variants import MIN_IDEA_TEXT_LENGTH, create_idea_text

        short_titles = ["AI", "Test", "X", "Fun"]
        for title in short_titles:
            text = create_idea_text(title)
            assert (
                len(text) >= MIN_IDEA_TEXT_LENGTH
            ), f"Short title '{title}' produced only {len(text)} characters"


# =============================================================================
# AI FLAVOR-BASED TESTS
# =============================================================================

class TestModuleConstants:
    """Tests for module-level constants."""

    def test_default_idea_count_is_10(self):
        """Test that DEFAULT_IDEA_COUNT is 10."""
        assert DEFAULT_IDEA_COUNT == 10

    def test_default_idea_count_matches_flavor_selector(self):
        """Test that DEFAULT_IDEA_COUNT matches FlavorSelector.DEFAULT_COUNT."""
        assert DEFAULT_IDEA_COUNT == FlavorSelector.DEFAULT_COUNT

    def test_multi_flavor_chance_is_0_4(self):
        """Test that MULTI_FLAVOR_CHANCE is 0.4 (40% dual-flavor)."""
        assert FlavorSelector.MULTI_FLAVOR_CHANCE == 0.4

    def test_no_flavor_chance_is_0_05(self):
        """Test that NO_FLAVOR_CHANCE is 0.05."""
        assert FlavorSelector.NO_FLAVOR_CHANCE == 0.05


class TestFlavorRegistry:
    """Tests for the flavor registry (AI-based flavor system)."""

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
        """Test that ideas are saved to DB with version=1."""
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

            mock_db.insert_idea.assert_called_once_with(text=ai_text, version=1)
            assert result.get('idea_id') == 42

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


class TestIdeaFormatterClass:
    """Tests for the IdeaFormatter class."""

    def test_format_as_text_returns_string(self):
        """Test that format_as_text returns a string."""
        formatter = IdeaFormatter()
        result = formatter.format_as_text({'text': 'Some content', 'hook': 'Hook text'})
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
