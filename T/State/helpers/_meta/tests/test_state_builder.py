"""Tests for State Builder module.

Tests the StateBuilder class and related functions for building, parsing,
and validating Story.state values.
"""

import pytest
from T.State.helpers.state_builder import (
    StateBuilder,
    StateParts,
    build_state,
    parse_state,
    validate_state_format,
    get_state_output,
    get_state_inputs,
    is_generation_state,
    is_review_state,
    STATE_PREFIX,
    GENERATION_ACTION,
    REVIEW_ACTION,
)


class TestStateParts:
    """Tests for StateParts dataclass."""
    
    def test_create_state_parts(self):
        """Test creating StateParts object."""
        parts = StateParts(
            prefix="PrismQ.T",
            output="Title",
            action="From",
            inputs=("Idea",),
            raw="PrismQ.T.Title.From.Idea"
        )
        assert parts.prefix == "PrismQ.T"
        assert parts.output == "Title"
        assert parts.action == "From"
        assert parts.inputs == ("Idea",)
    
    def test_is_generation_state_true(self):
        """Test is_generation_state property returns True for From states."""
        parts = StateParts(
            prefix="PrismQ.T",
            output="Title",
            action="From",
            inputs=("Idea",),
            raw="PrismQ.T.Title.From.Idea"
        )
        assert parts.is_generation_state is True
    
    def test_is_generation_state_false(self):
        """Test is_generation_state property returns False for non-From states."""
        parts = StateParts(
            prefix="PrismQ.T",
            output="Review",
            action=None,
            inputs=("Script", "Grammar"),
            raw="PrismQ.T.Review.Script.Grammar"
        )
        assert parts.is_generation_state is False
    
    def test_is_review_state_true_output(self):
        """Test is_review_state property for Review output."""
        parts = StateParts(
            prefix="PrismQ.T",
            output="Review",
            action=None,
            inputs=("Script", "Grammar"),
            raw="PrismQ.T.Review.Script.Grammar"
        )
        assert parts.is_review_state is True
    
    def test_components_after_output_with_action(self):
        """Test components_after_output with action."""
        parts = StateParts(
            prefix="PrismQ.T",
            output="Script",
            action="From",
            inputs=("Idea", "Title"),
            raw="PrismQ.T.Script.From.Idea.Title"
        )
        assert parts.components_after_output == ("From", "Idea", "Title")
    
    def test_components_after_output_without_action(self):
        """Test components_after_output without action."""
        parts = StateParts(
            prefix="PrismQ.T",
            output="Review",
            action=None,
            inputs=("Script", "Grammar"),
            raw="PrismQ.T.Review.Script.Grammar"
        )
        assert parts.components_after_output == ("Script", "Grammar")


class TestStateBuilder:
    """Tests for StateBuilder class."""
    
    def test_build_simple_state(self):
        """Test building a simple state."""
        state = StateBuilder().output("Idea").component("Creation").build()
        assert state == "PrismQ.T.Idea.Creation"
    
    def test_build_from_state(self):
        """Test building a From state."""
        state = StateBuilder().output("Title").from_inputs("Idea").build()
        assert state == "PrismQ.T.Title.From.Idea"
    
    def test_build_from_state_multiple_inputs(self):
        """Test building a From state with multiple inputs."""
        state = StateBuilder().output("Script").from_inputs("Idea", "Title").build()
        assert state == "PrismQ.T.Script.From.Idea.Title"
    
    def test_build_review_state(self):
        """Test building a review state."""
        state = StateBuilder().output("Review").component("Script").component("Grammar").build()
        assert state == "PrismQ.T.Review.Script.Grammar"
    
    def test_build_by_state(self):
        """Test building a By state."""
        state = StateBuilder().output("Review").by_source("Script").build()
        assert state == "PrismQ.T.Review.By.Script"
    
    def test_build_without_output_raises(self):
        """Test that building without output raises ValueError."""
        with pytest.raises(ValueError, match="Output must be set"):
            StateBuilder().from_inputs("Idea").build()
    
    def test_invalid_output_raises(self):
        """Test that invalid output raises ValueError."""
        with pytest.raises(ValueError, match="Invalid output component"):
            StateBuilder().output("123invalid").build()
    
    def test_invalid_input_raises(self):
        """Test that invalid input raises ValueError."""
        with pytest.raises(ValueError, match="Invalid input component"):
            StateBuilder().output("Title").from_inputs("invalid-input").build()
    
    def test_invalid_component_raises(self):
        """Test that invalid component raises ValueError."""
        with pytest.raises(ValueError, match="Invalid component"):
            StateBuilder().output("Review").component("invalid.component").build()
    
    def test_method_chaining(self):
        """Test that methods return self for chaining."""
        builder = StateBuilder()
        result = builder.output("Title")
        assert result is builder
        result = builder.from_inputs("Idea")
        assert result is builder


class TestBuildState:
    """Tests for build_state convenience function."""
    
    def test_build_state_simple(self):
        """Test building a simple state."""
        state = build_state("Idea", "Creation")
        assert state == "PrismQ.T.Idea.Creation"
    
    def test_build_state_with_from(self):
        """Test building a From state."""
        state = build_state("Title", "From", "Idea")
        assert state == "PrismQ.T.Title.From.Idea"
    
    def test_build_state_multiple_inputs(self):
        """Test building a state with multiple inputs."""
        state = build_state("Script", "From", "Idea", "Title")
        assert state == "PrismQ.T.Script.From.Idea.Title"
    
    def test_build_state_no_action(self):
        """Test building a state without action."""
        state = build_state("Publishing")
        assert state == "PrismQ.T.Publishing"


class TestParseState:
    """Tests for parse_state function."""
    
    def test_parse_simple_state(self):
        """Test parsing a simple state."""
        parts = parse_state("PrismQ.T.Idea.Creation")
        assert parts.prefix == "PrismQ.T"
        assert parts.output == "Idea"
        assert parts.action is None
        assert parts.inputs == ("Creation",)
    
    def test_parse_from_state(self):
        """Test parsing a From state."""
        parts = parse_state("PrismQ.T.Title.From.Idea")
        assert parts.output == "Title"
        assert parts.action == "From"
        assert parts.inputs == ("Idea",)
    
    def test_parse_from_state_multiple_inputs(self):
        """Test parsing a From state with multiple inputs."""
        parts = parse_state("PrismQ.T.Script.From.Idea.Title")
        assert parts.output == "Script"
        assert parts.action == "From"
        assert parts.inputs == ("Idea", "Title")
    
    def test_parse_review_state(self):
        """Test parsing a review state."""
        parts = parse_state("PrismQ.T.Review.Script.Grammar")
        assert parts.output == "Review"
        assert parts.action is None
        assert parts.inputs == ("Script", "Grammar")
    
    def test_parse_by_state(self):
        """Test parsing a By state."""
        parts = parse_state("PrismQ.T.Review.By.Script")
        assert parts.output == "Review"
        assert parts.action == "By"
        assert parts.inputs == ("Script",)
    
    def test_parse_terminal_state(self):
        """Test parsing terminal state."""
        parts = parse_state("PrismQ.T.Publishing")
        assert parts.output == "Publishing"
        assert parts.action is None
        assert parts.inputs == ()
    
    def test_parse_empty_raises(self):
        """Test parsing empty state raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_state("")
    
    def test_parse_invalid_prefix_raises(self):
        """Test parsing state with invalid prefix raises ValueError."""
        with pytest.raises(ValueError, match="must start with"):
            parse_state("Invalid.State")
    
    def test_parse_only_prefix_raises(self):
        """Test parsing state with only prefix raises ValueError."""
        with pytest.raises(ValueError, match="at least an output"):
            parse_state("PrismQ.T.")
    
    def test_parse_preserves_raw(self):
        """Test that parse_state preserves the raw state string."""
        state = "PrismQ.T.Title.From.Idea"
        parts = parse_state(state)
        assert parts.raw == state


class TestValidateStateFormat:
    """Tests for validate_state_format function."""
    
    def test_valid_simple_state(self):
        """Test validating a simple valid state."""
        is_valid, error = validate_state_format("PrismQ.T.Idea.Creation")
        assert is_valid is True
        assert error is None
    
    def test_valid_from_state(self):
        """Test validating a From state."""
        is_valid, error = validate_state_format("PrismQ.T.Title.From.Idea")
        assert is_valid is True
        assert error is None
    
    def test_valid_complex_state(self):
        """Test validating a complex state."""
        is_valid, error = validate_state_format("PrismQ.T.Script.From.Idea.Title")
        assert is_valid is True
        assert error is None
    
    def test_invalid_empty(self):
        """Test that empty state is invalid."""
        is_valid, error = validate_state_format("")
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_invalid_prefix(self):
        """Test that state with wrong prefix is invalid."""
        is_valid, error = validate_state_format("Wrong.Prefix.State")
        assert is_valid is False
        assert "PrismQ.T" in error
    
    def test_invalid_component(self):
        """Test that state with invalid component is invalid."""
        is_valid, error = validate_state_format("PrismQ.T.123Invalid.State")
        assert is_valid is False
        assert "Invalid component" in error


class TestGetStateOutput:
    """Tests for get_state_output function."""
    
    def test_get_output_from_state(self):
        """Test getting output from a From state."""
        output = get_state_output("PrismQ.T.Title.From.Idea")
        assert output == "Title"
    
    def test_get_output_review_state(self):
        """Test getting output from a review state."""
        output = get_state_output("PrismQ.T.Review.Script.Grammar")
        assert output == "Review"
    
    def test_get_output_terminal_state(self):
        """Test getting output from terminal state."""
        output = get_state_output("PrismQ.T.Publishing")
        assert output == "Publishing"


class TestGetStateInputs:
    """Tests for get_state_inputs function."""
    
    def test_get_inputs_single(self):
        """Test getting single input."""
        inputs = get_state_inputs("PrismQ.T.Title.From.Idea")
        assert inputs == ["Idea"]
    
    def test_get_inputs_multiple(self):
        """Test getting multiple inputs."""
        inputs = get_state_inputs("PrismQ.T.Script.From.Idea.Title")
        assert inputs == ["Idea", "Title"]
    
    def test_get_inputs_none(self):
        """Test getting inputs when there are none."""
        inputs = get_state_inputs("PrismQ.T.Publishing")
        assert inputs == []
    
    def test_get_inputs_non_from_state(self):
        """Test getting inputs from non-From state."""
        inputs = get_state_inputs("PrismQ.T.Review.Script.Grammar")
        assert inputs == ["Script", "Grammar"]


class TestIsGenerationState:
    """Tests for is_generation_state function."""
    
    def test_from_state_is_generation(self):
        """Test that From state is generation state."""
        assert is_generation_state("PrismQ.T.Title.From.Idea") is True
    
    def test_review_state_not_generation(self):
        """Test that review state is not generation state."""
        assert is_generation_state("PrismQ.T.Review.Script.Grammar") is False
    
    def test_invalid_state_returns_false(self):
        """Test that invalid state returns False."""
        assert is_generation_state("Invalid") is False


class TestIsReviewState:
    """Tests for is_review_state function."""
    
    def test_review_output_is_review_state(self):
        """Test that Review output is review state."""
        assert is_review_state("PrismQ.T.Review.Script.Grammar") is True
    
    def test_from_state_not_review(self):
        """Test that From state is not review state."""
        assert is_review_state("PrismQ.T.Title.From.Idea") is False
    
    def test_invalid_state_returns_false(self):
        """Test that invalid state returns False."""
        assert is_review_state("Invalid") is False


class TestConstants:
    """Tests for module constants."""
    
    def test_state_prefix(self):
        """Test STATE_PREFIX constant."""
        assert STATE_PREFIX == "PrismQ.T"
    
    def test_generation_action(self):
        """Test GENERATION_ACTION constant."""
        assert GENERATION_ACTION == "From"
    
    def test_review_action(self):
        """Test REVIEW_ACTION constant."""
        assert REVIEW_ACTION == "By"


class TestRealWorldStates:
    """Tests with real workflow states from DATABASE_DESIGN.md."""
    
    def test_idea_creation(self):
        """Test parsing IDEA_CREATION state."""
        parts = parse_state("PrismQ.T.Idea.Creation")
        assert parts.output == "Idea"
        assert parts.inputs == ("Creation",)
    
    def test_title_from_idea(self):
        """Test parsing TITLE_FROM_IDEA state."""
        parts = parse_state("PrismQ.T.Title.From.Idea")
        assert parts.output == "Title"
        assert parts.action == "From"
        assert parts.inputs == ("Idea",)
    
    def test_script_from_idea_title(self):
        """Test parsing SCRIPT_FROM_IDEA_TITLE state."""
        parts = parse_state("PrismQ.T.Script.From.Idea.Title")
        assert parts.output == "Script"
        assert parts.action == "From"
        assert parts.inputs == ("Idea", "Title")
    
    def test_review_script_grammar(self):
        """Test parsing REVIEW_SCRIPT_GRAMMAR state."""
        parts = parse_state("PrismQ.T.Review.Script.Grammar")
        assert parts.output == "Review"
        assert parts.inputs == ("Script", "Grammar")
    
    def test_publishing(self):
        """Test parsing PUBLISHING state."""
        parts = parse_state("PrismQ.T.Publishing")
        assert parts.output == "Publishing"
        assert parts.inputs == ()
    
    def test_story_review(self):
        """Test parsing STORY_REVIEW state."""
        parts = parse_state("PrismQ.T.Story.Review")
        assert parts.output == "Story"
        assert parts.inputs == ("Review",)
    
    def test_roundtrip_title_from_idea(self):
        """Test building and parsing TITLE_FROM_IDEA."""
        built = StateBuilder().output("Title").from_inputs("Idea").build()
        parsed = parse_state(built)
        assert parsed.output == "Title"
        assert parsed.action == "From"
        assert parsed.inputs == ("Idea",)
    
    def test_roundtrip_script_from_idea_title(self):
        """Test building and parsing SCRIPT_FROM_IDEA_TITLE."""
        built = StateBuilder().output("Script").from_inputs("Idea", "Title").build()
        parsed = parse_state(built)
        assert parsed.output == "Script"
        assert parsed.action == "From"
        assert parsed.inputs == ("Idea", "Title")
