"""Tests for modular prompt composition system.

This test suite verifies that:
1. Prompt templates load correctly
2. Composition functions work as expected
3. Variables are resolved properly
4. No placeholders remain unresolved
5. Output structure matches expectations
"""

import pytest
from T.Review.Title.prompts import (
    BASE_REVIEW_PROMPT,
    IDEA_CONTEXT_PROMPT,
    COMPARISON_CONTEXT_PROMPT,
    WEIGHTS_V1_WITH_IDEA,
    WEIGHTS_V2_CONTENT_ONLY,
    compose_review_prompt_with_idea,
    compose_review_prompt_content_only,
    compose_comparison_prompt,
    get_v1_review_prompt,
    get_v2_review_prompt,
)


class TestPromptLoading:
    """Test that prompt templates load correctly."""

    def test_base_review_loads(self):
        """Test base review template loads."""
        assert len(BASE_REVIEW_PROMPT) > 0
        assert "Content Alignment" in BASE_REVIEW_PROMPT
        assert "Engagement" in BASE_REVIEW_PROMPT
        assert "SEO & Length" in BASE_REVIEW_PROMPT

    def test_idea_context_loads(self):
        """Test idea context template loads."""
        assert len(IDEA_CONTEXT_PROMPT) > 0
        assert "Idea Alignment" in IDEA_CONTEXT_PROMPT

    def test_comparison_context_loads(self):
        """Test comparison context template loads."""
        assert len(COMPARISON_CONTEXT_PROMPT) > 0
        assert "Improvement Detection" in COMPARISON_CONTEXT_PROMPT
        assert "Overall Assessment" in COMPARISON_CONTEXT_PROMPT


class TestPromptComposition:
    """Test prompt composition functions."""

    def test_compose_with_idea_basic(self):
        """Test basic composition with idea context."""
        prompt = compose_review_prompt_with_idea(
            title_text="Test Title",
            content_text="Test content text",
            idea_summary="Test idea summary",
            target_audience="Test audience",
        )

        # Check all sections present
        assert "Content Alignment" in prompt
        assert "Engagement" in prompt
        assert "SEO & Length" in prompt
        assert "Idea Alignment" in prompt

        # Check variables resolved
        assert "Test Title" in prompt
        assert "Test content text" in prompt
        assert "Test idea summary" in prompt
        assert "Test audience" in prompt

        # Check no unresolved placeholders
        assert "{title_text}" not in prompt
        assert "{content_text}" not in prompt
        assert "{idea_summary}" not in prompt
        assert "{target_audience}" not in prompt

    def test_compose_with_idea_default_weights(self):
        """Test composition uses default weights correctly."""
        prompt = compose_review_prompt_with_idea(
            title_text="Title",
            content_text="Content",
            idea_summary="Idea",
        )

        # Check default weights present
        assert "30%" in prompt  # content_weight
        assert "25%" in prompt  # idea_weight and engagement_weight
        assert "20%" in prompt  # seo_weight

    def test_compose_with_idea_custom_weights(self):
        """Test composition with custom weights."""
        custom_weights = {
            "content_weight": 35,
            "idea_weight": 30,
            "engagement_weight": 20,
            "seo_weight": 15,
        }

        prompt = compose_review_prompt_with_idea(
            title_text="Title",
            content_text="Content",
            idea_summary="Idea",
            weights=custom_weights,
        )

        # Check custom weights present
        assert "35%" in prompt  # content_weight
        assert "30%" in prompt  # idea_weight
        assert "20%" in prompt  # engagement_weight
        assert "15%" in prompt  # seo_weight

    def test_compose_content_only_basic(self):
        """Test basic composition for content-only review."""
        prompt = compose_review_prompt_content_only(
            title_text="Test Title",
            content_text="Test content text",
        )

        # Check required sections present
        assert "Content Alignment" in prompt
        assert "Engagement" in prompt
        assert "SEO & Length" in prompt

        # Check idea section NOT present
        assert "Idea Alignment" not in prompt

        # Check variables resolved
        assert "Test Title" in prompt
        assert "Test content text" in prompt

        # Check no unresolved placeholders
        assert "{title_text}" not in prompt
        assert "{content_text}" not in prompt

    def test_compose_content_only_default_weights(self):
        """Test content-only composition uses v2 weights."""
        prompt = compose_review_prompt_content_only(
            title_text="Title",
            content_text="Content",
        )

        # Check v2 default weights (higher content weight)
        assert "40%" in prompt  # content_weight
        assert "30%" in prompt  # engagement_weight

    def test_compose_comparison_basic(self):
        """Test basic comparison prompt composition."""
        prompt = compose_comparison_prompt(
            title_current="Current Title",
            title_previous="Previous Title",
            content_text="Test content",
            score_current=78,
            score_previous=65,
            feedback_previous="Previous feedback text",
        )

        # Check sections present
        assert "Improvement Detection" in prompt
        assert "Overall Assessment" in prompt

        # Check variables resolved
        assert "Current Title" in prompt
        assert "Previous Title" in prompt
        assert "78" in prompt
        assert "65" in prompt
        assert "Previous feedback text" in prompt

        # Check version labels
        assert "v2" in prompt  # current_version
        assert "v1" in prompt  # previous_version
        assert "v3" in prompt  # next_version

    def test_compose_comparison_custom_versions(self):
        """Test comparison with custom version labels."""
        prompt = compose_comparison_prompt(
            title_current="Title v3",
            title_previous="Title v2",
            content_text="Content",
            score_current=85,
            score_previous=78,
            feedback_previous="Feedback",
            current_version="v3",
            previous_version="v2",
            next_version="v4",
        )

        # Check custom version labels
        assert "v3" in prompt
        assert "v2" in prompt
        assert "v4" in prompt


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""

    def test_get_v1_review_prompt(self):
        """Test v1 review prompt convenience function."""
        prompt = get_v1_review_prompt(
            title_text="Title",
            content_text="Content",
            idea_summary="Idea",
            target_audience="Audience",
        )

        # Should include idea context
        assert "Idea Alignment" in prompt
        assert "Title" in prompt
        assert "Content" in prompt
        assert "Idea" in prompt
        assert "Audience" in prompt

    def test_get_v2_review_prompt(self):
        """Test v2 review prompt convenience function."""
        prompt = get_v2_review_prompt(
            title_text="Title",
            content_text="Content",
        )

        # Should NOT include idea context
        assert "Idea Alignment" not in prompt
        assert "Title" in prompt
        assert "Content" in prompt


class TestWeightConfigurations:
    """Test weight configuration constants."""

    def test_v1_weights_sum_to_100(self):
        """Test v1 weights sum to 100%."""
        total = sum(WEIGHTS_V1_WITH_IDEA.values())
        assert total == 100, f"V1 weights sum to {total}, expected 100"

    def test_v2_weights_sum_to_100(self):
        """Test v2 weights sum to 100%."""
        total = sum(WEIGHTS_V2_CONTENT_ONLY.values())
        assert total == 100, f"V2 weights sum to {total}, expected 100"

    def test_v1_has_idea_weight(self):
        """Test v1 weights include idea_weight."""
        assert "idea_weight" in WEIGHTS_V1_WITH_IDEA

    def test_v2_no_idea_weight(self):
        """Test v2 weights do not include idea_weight."""
        assert "idea_weight" not in WEIGHTS_V2_CONTENT_ONLY


class TestJSONOutputFormat:
    """Test JSON output format specifications."""

    def test_v1_includes_idea_alignment_score(self):
        """Test v1 prompt includes idea_alignment_score in JSON output."""
        prompt = get_v1_review_prompt(
            title_text="Title",
            content_text="Content",
            idea_summary="Idea",
        )

        assert "idea_alignment_score" in prompt

    def test_v2_excludes_idea_alignment_score(self):
        """Test v2 prompt excludes idea_alignment_score from JSON output."""
        prompt = get_v2_review_prompt(
            title_text="Title",
            content_text="Content",
        )

        assert "idea_alignment_score" not in prompt

    def test_comparison_has_correct_fields(self):
        """Test comparison prompt has correct JSON fields."""
        prompt = compose_comparison_prompt(
            title_current="Current",
            title_previous="Previous",
            content_text="Content",
            score_current=80,
            score_previous=70,
            feedback_previous="Feedback",
        )

        # Check expected JSON fields
        assert "comparisons" in prompt
        assert "overall_assessment" in prompt
        assert "key_improvements" in prompt
        assert "remaining_issues" in prompt
        assert "recommendation" in prompt
        assert "next_steps" in prompt


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_title_text(self):
        """Test handling of empty title text."""
        prompt = compose_review_prompt_with_idea(
            title_text="",
            content_text="Content",
            idea_summary="Idea",
        )

        # Should still compose, just with empty value
        assert "Content" in prompt

    def test_very_long_content(self):
        """Test handling of very long content text."""
        long_content = "A" * 10000

        prompt = compose_review_prompt_content_only(
            title_text="Title",
            content_text=long_content,
        )

        # Should include the long content
        assert long_content in prompt

    def test_special_characters_in_text(self):
        """Test handling of special characters."""
        prompt = compose_review_prompt_with_idea(
            title_text="Title: The \"Echo\" & More",
            content_text="Content with special chars: {}, [], <>, @#$",
            idea_summary="Idea with 'quotes' and \"double quotes\"",
        )

        # Should preserve special characters
        assert '"Echo"' in prompt
        assert "{}, []" in prompt
        assert "'quotes'" in prompt


class TestPromptStructure:
    """Test overall prompt structure and organization."""

    def test_v1_prompt_has_proper_sections(self):
        """Test v1 prompt has all required sections in order."""
        prompt = get_v1_review_prompt(
            title_text="Title",
            content_text="Content",
            idea_summary="Idea",
        )

        # Find section positions
        content_pos = prompt.find("Content Alignment")
        engagement_pos = prompt.find("Engagement")
        seo_pos = prompt.find("SEO & Length")
        idea_pos = prompt.find("Idea Alignment")
        provide_pos = prompt.find("Provide:")

        # Check order
        assert content_pos < engagement_pos < seo_pos < idea_pos < provide_pos

    def test_v2_prompt_has_proper_sections(self):
        """Test v2 prompt has required sections in order."""
        prompt = get_v2_review_prompt(
            title_text="Title",
            content_text="Content",
        )

        # Find section positions
        content_pos = prompt.find("Content Alignment")
        engagement_pos = prompt.find("Engagement")
        seo_pos = prompt.find("SEO & Length")
        provide_pos = prompt.find("Provide:")

        # Check order
        assert content_pos < engagement_pos < seo_pos < provide_pos

    def test_prompt_ends_with_json_format(self):
        """Test prompts end with JSON format specification."""
        prompt = get_v1_review_prompt(
            title_text="Title",
            content_text="Content",
            idea_summary="Idea",
        )

        assert "JSON format" in prompt
        assert prompt.strip().endswith(".")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
