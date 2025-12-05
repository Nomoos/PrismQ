"""Tests for prompts module - Critical Story Review Prompt Templates."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from T.Story.Review import (
    CRITICAL_STORY_REVIEW_PROMPT,
    FINAL_POLISH_THRESHOLD,
    REVIEW_FOCUS_AREAS,
    REVIEW_OUTPUT_STRUCTURE,
    REVIEW_CONSTRAINTS,
    get_critical_review_prompt,
    get_critical_review_prompt_template,
    is_ready_for_final_polish,
    get_readiness_statement
)


class TestCriticalReviewPrompt:
    """Test the critical story review prompt template."""
    
    def test_prompt_exists(self):
        """Test that the prompt constant is defined."""
        assert CRITICAL_STORY_REVIEW_PROMPT is not None
        assert isinstance(CRITICAL_STORY_REVIEW_PROMPT, str)
        assert len(CRITICAL_STORY_REVIEW_PROMPT) > 0
    
    def test_prompt_contains_key_requirements(self):
        """Test that the prompt contains all key requirements."""
        prompt = CRITICAL_STORY_REVIEW_PROMPT
        
        # Check for length requirement
        assert "1200 words" in prompt
        assert "Do NOT exceed" in prompt
        
        # Check for tone requirements
        assert "analytical" in prompt
        assert "objective" in prompt
        assert "constructive" in prompt
        
        # Check for focus areas
        assert "pacing" in prompt.lower()
        assert "worldbuilding" in prompt.lower()
        assert "logic" in prompt.lower()
        assert "character" in prompt.lower()
        assert "thematic" in prompt.lower()
        assert "structure" in prompt.lower()
    
    def test_prompt_contains_output_structure(self):
        """Test that the prompt specifies the output structure."""
        prompt = CRITICAL_STORY_REVIEW_PROMPT
        
        assert "Introduction" in prompt
        assert "Major Flaws" in prompt
        assert "Suggestions for Improvement" in prompt
        assert "Conclusion" in prompt
        assert "Final Score" in prompt
        assert "Readiness Statement" in prompt
    
    def test_prompt_contains_score_range(self):
        """Test that the prompt specifies the score range."""
        prompt = CRITICAL_STORY_REVIEW_PROMPT
        assert "0–100%" in prompt or "0-100%" in prompt
    
    def test_prompt_contains_readiness_threshold(self):
        """Test that the prompt contains the 75% readiness threshold."""
        prompt = CRITICAL_STORY_REVIEW_PROMPT
        assert "75%" in prompt
    
    def test_prompt_contains_readiness_statements(self):
        """Test that the prompt contains both readiness statement options."""
        prompt = CRITICAL_STORY_REVIEW_PROMPT
        assert "ready for final polish" in prompt.lower()
        assert "not yet ready for final polish" in prompt.lower()
    
    def test_prompt_contains_placeholder(self):
        """Test that the prompt contains the story placeholder."""
        prompt = CRITICAL_STORY_REVIEW_PROMPT
        assert "[INSERT STORY HERE]" in prompt
    
    def test_prompt_contains_avoid_list(self):
        """Test that the prompt specifies what to avoid."""
        prompt = CRITICAL_STORY_REVIEW_PROMPT
        assert "Superlatives" in prompt
        assert "Unjustified praise" in prompt
        assert "Vague criticism" in prompt


class TestGetCriticalReviewPrompt:
    """Test the get_critical_review_prompt function."""
    
    def test_story_insertion(self):
        """Test that story text is properly inserted."""
        test_story = "Once upon a time, in a land far away..."
        prompt = get_critical_review_prompt(test_story)
        
        assert test_story in prompt
        assert "[INSERT STORY HERE]" not in prompt
    
    def test_preserves_prompt_structure(self):
        """Test that the prompt structure is preserved after insertion."""
        test_story = "A short story about testing."
        prompt = get_critical_review_prompt(test_story)
        
        # Check key elements are still present
        assert "1200 words" in prompt
        assert "Major Flaws" in prompt
        assert "Final Score" in prompt
    
    def test_empty_story(self):
        """Test handling of empty story text."""
        prompt = get_critical_review_prompt("")
        # Should still work, just with empty insertion
        assert "1200 words" in prompt
    
    def test_long_story(self):
        """Test handling of long story text."""
        long_story = "The story continues. " * 1000
        prompt = get_critical_review_prompt(long_story)
        assert long_story in prompt


class TestGetCriticalReviewPromptTemplate:
    """Test the get_critical_review_prompt_template function."""
    
    def test_returns_template_with_placeholder(self):
        """Test that template contains placeholder."""
        template = get_critical_review_prompt_template()
        assert "[INSERT STORY HERE]" in template
    
    def test_matches_constant(self):
        """Test that function returns the same as the constant."""
        template = get_critical_review_prompt_template()
        assert template == CRITICAL_STORY_REVIEW_PROMPT


class TestFinalPolishThreshold:
    """Test the final polish threshold constant."""
    
    def test_threshold_value(self):
        """Test that threshold is 75."""
        assert FINAL_POLISH_THRESHOLD == 75
    
    def test_threshold_is_integer(self):
        """Test that threshold is an integer."""
        assert isinstance(FINAL_POLISH_THRESHOLD, int)


class TestIsReadyForFinalPolish:
    """Test the is_ready_for_final_polish function."""
    
    def test_score_at_threshold(self):
        """Test score exactly at threshold (75) returns True."""
        assert is_ready_for_final_polish(75) is True
    
    def test_score_above_threshold(self):
        """Test scores above threshold return True."""
        assert is_ready_for_final_polish(76) is True
        assert is_ready_for_final_polish(80) is True
        assert is_ready_for_final_polish(95) is True
        assert is_ready_for_final_polish(100) is True
    
    def test_score_below_threshold(self):
        """Test scores below threshold return False."""
        assert is_ready_for_final_polish(74) is False
        assert is_ready_for_final_polish(50) is False
        assert is_ready_for_final_polish(0) is False
    
    def test_edge_cases(self):
        """Test edge case scores."""
        assert is_ready_for_final_polish(0) is False
        assert is_ready_for_final_polish(100) is True


class TestGetReadinessStatement:
    """Test the get_readiness_statement function."""
    
    def test_ready_statement(self):
        """Test statement for scores at or above threshold."""
        statement = get_readiness_statement(75)
        assert statement == "This story is ready for final polish."
        
        statement = get_readiness_statement(80)
        assert statement == "This story is ready for final polish."
        
        statement = get_readiness_statement(100)
        assert statement == "This story is ready for final polish."
    
    def test_not_ready_statement(self):
        """Test statement for scores below threshold."""
        statement = get_readiness_statement(74)
        assert statement == "This story is not yet ready for final polish."
        
        statement = get_readiness_statement(50)
        assert statement == "This story is not yet ready for final polish."
        
        statement = get_readiness_statement(0)
        assert statement == "This story is not yet ready for final polish."
    
    def test_statement_format(self):
        """Test that statements match the prompt format."""
        # Check that statements use the exact phrases from the prompt
        ready_statement = get_readiness_statement(75)
        not_ready_statement = get_readiness_statement(74)
        
        prompt = CRITICAL_STORY_REVIEW_PROMPT
        assert ready_statement.strip('.') in prompt
        assert "not yet ready for final polish" in not_ready_statement


class TestReviewFocusAreas:
    """Test the review focus areas constant."""
    
    def test_focus_areas_is_list(self):
        """Test that focus areas is a list."""
        assert isinstance(REVIEW_FOCUS_AREAS, list)
    
    def test_focus_areas_not_empty(self):
        """Test that focus areas is not empty."""
        assert len(REVIEW_FOCUS_AREAS) > 0
    
    def test_contains_expected_areas(self):
        """Test that expected focus areas are included."""
        assert "pacing" in REVIEW_FOCUS_AREAS
        assert "worldbuilding" in REVIEW_FOCUS_AREAS
        assert "logic" in REVIEW_FOCUS_AREAS
        assert "structure" in REVIEW_FOCUS_AREAS


class TestReviewOutputStructure:
    """Test the review output structure constant."""
    
    def test_output_structure_is_dict(self):
        """Test that output structure is a dictionary."""
        assert isinstance(REVIEW_OUTPUT_STRUCTURE, dict)
    
    def test_contains_required_sections(self):
        """Test that all required sections are defined."""
        required_sections = [
            "introduction",
            "major_flaws",
            "suggestions",
            "conclusion",
            "final_score",
            "readiness_statement"
        ]
        
        for section in required_sections:
            assert section in REVIEW_OUTPUT_STRUCTURE


class TestReviewConstraints:
    """Test the review constraints constant."""
    
    def test_constraints_is_dict(self):
        """Test that constraints is a dictionary."""
        assert isinstance(REVIEW_CONSTRAINTS, dict)
    
    def test_max_words_constraint(self):
        """Test the max words constraint."""
        assert REVIEW_CONSTRAINTS["max_words"] == 1200
    
    def test_tone_constraint(self):
        """Test the tone constraint."""
        assert "analytical" in REVIEW_CONSTRAINTS["tone"]
        assert "objective" in REVIEW_CONSTRAINTS["tone"]
        assert "constructive" in REVIEW_CONSTRAINTS["tone"]
    
    def test_avoid_list(self):
        """Test the avoid list."""
        avoid = REVIEW_CONSTRAINTS["avoid"]
        assert isinstance(avoid, list)
        assert len(avoid) > 0
    
    def test_evidence_requirement(self):
        """Test that evidence is required."""
        assert REVIEW_CONSTRAINTS["require_evidence"] is True
    
    def test_actionable_suggestions_requirement(self):
        """Test that actionable suggestions are required."""
        assert REVIEW_CONSTRAINTS["require_actionable_suggestions"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
