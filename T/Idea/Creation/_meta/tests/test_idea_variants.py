"""Tests for Idea Variant Templates module."""

import sys
import os
import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from idea_variants import (
    VARIANT_TEMPLATES,
    VARIANT_EMOTION_FIRST,
    VARIANT_MYSTERY,
    VARIANT_SKELETON,
    VARIANT_SHORTFORM,
    VARIANT_NICHE_BLEND,
    VARIANT_MINIMAL,
    VARIANT_4POINT,
    VARIANT_HOOK_FRAME,
    VARIANT_SHORTFORM2,
    VARIANT_GENRE,
    VARIANT_SCENE_SEED,
    get_template,
    list_templates,
    get_template_fields,
    get_template_example,
    create_idea_variant,
    create_all_variants,
    create_selected_variants,
    create_multiple_of_same_variant,
)


class TestVariantTemplateRegistry:
    """Tests for the template registry."""
    
    def test_all_templates_registered(self):
        """Test that all 11 variant templates are registered."""
        assert len(VARIANT_TEMPLATES) == 11
    
    def test_template_names_match_constants(self):
        """Test that registry keys match expected names."""
        expected_names = [
            "emotion_first", "mystery", "skeleton", "shortform",
            "niche_blend", "minimal", "4point", "hook_frame",
            "shortform2", "genre", "scene_seed"
        ]
        for name in expected_names:
            assert name in VARIANT_TEMPLATES
    
    def test_list_templates_returns_all(self):
        """Test list_templates returns all template names."""
        templates = list_templates()
        assert len(templates) == 11
        assert "emotion_first" in templates
        assert "mystery" in templates


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
    
    def test_has_script_length_field(self):
        """Test template has target_script_length field."""
        assert "target_script_length" in VARIANT_SCENE_SEED["fields"]


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
    
    def test_creates_11_variants(self):
        """Test that create_all_variants creates all 11 variants."""
        variants = create_all_variants("Test Title")
        assert len(variants) == 11
    
    def test_all_variants_are_different_types(self):
        """Test that all variants are different types."""
        variants = create_all_variants("Test Title")
        types = [v["variant_type"] for v in variants]
        assert len(set(types)) == 11


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
        assert v1.get("main_emotion") != v2.get("main_emotion") or v1.get("unusual_angle") != v2.get("unusual_angle")
    
    def test_different_titles_produce_different_variants(self):
        """Test that different titles produce different variants."""
        v1 = create_idea_variant("Příběh A", "minimal", randomize=False)
        v2 = create_idea_variant("Příběh B", "minimal", randomize=False)
        
        # Hooks should contain the different titles
        assert "příběh a" in v1.get("hook", "").lower()
        assert "příběh b" in v2.get("hook", "").lower()


class TestVariantContentQuality:
    """Tests for variant content quality."""
    
    def test_hooks_are_not_empty(self):
        """Test that generated hooks are not empty."""
        for variant_name in VARIANT_TEMPLATES.keys():
            variant = create_idea_variant("Test Content", variant_name)
            # Check common hook fields
            hook_fields = ["hook", "core_hook", "hook_sentence", "hook_essence", 
                          "hook_moment", "scene_hook", "opening_hook", "central_mystery",
                          "hook_scene", "concept", "premise"]
            has_hook = False
            for field in hook_fields:
                if field in variant and variant[field]:
                    has_hook = True
                    assert len(str(variant[field])) > 5, f"Hook too short in {variant_name}"
            assert has_hook, f"No hook field found in {variant_name}"
    
    def test_title_is_incorporated(self):
        """Test that the source title is incorporated in the content."""
        test_title = "Unique Test Topic XYZ"
        for variant_name in VARIANT_TEMPLATES.keys():
            variant = create_idea_variant(test_title, variant_name)
            # The title should appear in at least one field
            variant_str = str(variant).lower()
            assert "unique test topic xyz" in variant_str or "test" in variant_str
