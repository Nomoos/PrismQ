"""Tests for state name constants module.

Tests verify:
    - All state constants are properly defined
    - State naming convention follows PrismQ.T.<Output>.From.<Input> pattern
    - Extensibility mechanisms work correctly
    - Category mappings are accurate
    - Helper methods function as expected
"""

import sys
import os
import pytest

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))

from T.State.constants.state_names import (
    StateNames,
    StateCategory,
    INITIAL_STATES,
    TERMINAL_STATES,
    EXPERT_REVIEW_STATES,
)


class TestStateNamesConstants:
    """Tests for individual state name constants."""
    
    def test_state_prefix(self):
        """Test that STATE_PREFIX is correctly defined."""
        assert StateNames.STATE_PREFIX == "PrismQ.T"
    
    def test_idea_creation_state(self):
        """Test Idea Creation state constant."""
        assert StateNames.IDEA_CREATION == "PrismQ.T.Idea.Creation"
    
    def test_title_from_idea_state(self):
        """Test Title From Idea state constant."""
        assert StateNames.TITLE_FROM_IDEA == "PrismQ.T.Title.From.Idea"
    
    def test_script_from_idea_title_state(self):
        """Test Script From Idea Title state constant."""
        assert StateNames.SCRIPT_FROM_IDEA_TITLE == "PrismQ.T.Script.From.Idea.Title"
    
    def test_review_title_from_script_and_idea_state(self):
        """Test Review Title From Script.Idea state constant."""
        assert StateNames.REVIEW_TITLE_FROM_SCRIPT_IDEA == "PrismQ.T.Review.Title.From.Script.Idea"
    
    def test_review_script_from_title_and_idea_state(self):
        """Test Review Script From Title.Idea state constant."""
        assert StateNames.REVIEW_SCRIPT_FROM_TITLE_IDEA == "PrismQ.T.Review.Script.From.Title.Idea"
    
    def test_review_title_from_script_state(self):
        """Test Review Title From Script state constant."""
        assert StateNames.REVIEW_TITLE_FROM_SCRIPT == "PrismQ.T.Review.Title.From.Script"
    
    def test_title_from_title_review_script_state(self):
        """Test Title From Title Review Script state constant."""
        assert StateNames.TITLE_FROM_TITLE_REVIEW_SCRIPT == "PrismQ.T.Title.From.Title.Review.Script"
    
    def test_script_from_script_review_title_state(self):
        """Test Script From Script Review Title state constant."""
        assert StateNames.SCRIPT_FROM_SCRIPT_REVIEW_TITLE == "PrismQ.T.Script.From.Script.Review.Title"
    
    def test_review_script_from_title_state(self):
        """Test Review Script From Title state constant."""
        assert StateNames.REVIEW_SCRIPT_FROM_TITLE == "PrismQ.T.Review.Script.From.Title"
    
    def test_quality_review_states(self):
        """Test quality review state constants (stages 10-16)."""
        assert StateNames.REVIEW_SCRIPT_GRAMMAR == "PrismQ.T.Review.Script.Grammar"
        assert StateNames.REVIEW_SCRIPT_TONE == "PrismQ.T.Review.Script.Tone"
        assert StateNames.REVIEW_SCRIPT_CONTENT == "PrismQ.T.Review.Script.Content"
        assert StateNames.REVIEW_SCRIPT_CONSISTENCY == "PrismQ.T.Review.Script.Consistency"
        assert StateNames.REVIEW_SCRIPT_EDITING == "PrismQ.T.Review.Script.Editing"
        assert StateNames.REVIEW_TITLE_READABILITY == "PrismQ.T.Review.Title.Readability"
        assert StateNames.REVIEW_SCRIPT_READABILITY == "PrismQ.T.Review.Script.Readability"
    
    def test_expert_review_states(self):
        """Test expert review state constants (stages 17-18)."""
        assert StateNames.STORY_REVIEW == "PrismQ.T.Story.Review"
        assert StateNames.STORY_POLISH == "PrismQ.T.Story.Polish"
    
    def test_publishing_state(self):
        """Test Publishing terminal state constant."""
        assert StateNames.PUBLISHING == "PrismQ.T.Publishing"
    
    def test_all_states_have_correct_prefix(self):
        """Test that all state constants start with the correct prefix."""
        all_states = StateNames.get_all_states()
        for state in all_states:
            assert state.startswith(StateNames.STATE_PREFIX), \
                f"State {state} does not start with {StateNames.STATE_PREFIX}"


class TestStateNamingConvention:
    """Tests for state naming convention compliance."""
    
    def test_naming_pattern_dot_separation(self):
        """Test that all states use dot separation."""
        all_states = StateNames.get_all_states()
        for state in all_states:
            assert '.' in state, f"State {state} does not use dot separation"
    
    def test_no_underscores_in_state_names(self):
        """Test that state names don't contain underscores (use dots instead)."""
        all_states = StateNames.get_all_states()
        for state in all_states:
            assert '_' not in state, f"State {state} contains underscore instead of dots"
    
    def test_generation_states_have_from_pattern(self):
        """Test that generation states follow PrismQ.T.<Output>.From.<Input> pattern."""
        generation_states = StateNames.get_generation_states()
        for state in generation_states:
            assert '.From.' in state, \
                f"Generation state {state} does not follow From pattern"
    
    def test_review_states_have_review_pattern(self):
        """Test that review states include 'Review' in the name."""
        review_states = StateNames.get_review_states()
        for state in review_states:
            # Story.Review is a special case
            assert 'Review' in state, \
                f"Review state {state} does not contain 'Review'"


class TestStateCategory:
    """Tests for StateCategory enum."""
    
    def test_category_values(self):
        """Test that all category values are defined."""
        assert StateCategory.CREATION.value == "creation"
        assert StateCategory.GENERATION.value == "generation"
        assert StateCategory.REVIEW.value == "review"
        assert StateCategory.REFINEMENT.value == "refinement"
        assert StateCategory.PUBLISHING.value == "publishing"
    
    def test_category_count(self):
        """Test that we have the expected number of categories."""
        assert len(StateCategory) == 5


class TestGetAllStates:
    """Tests for get_all_states method."""
    
    def test_returns_list(self):
        """Test that get_all_states returns a list."""
        states = StateNames.get_all_states()
        assert isinstance(states, list)
    
    def test_returns_expected_count(self):
        """Test that get_all_states returns expected number of states."""
        states = StateNames.get_all_states()
        # Based on WORKFLOW_STATE_MACHINE.md, we have 19 unique states
        assert len(states) >= 19
    
    def test_all_elements_are_strings(self):
        """Test that all returned elements are strings."""
        states = StateNames.get_all_states()
        for state in states:
            assert isinstance(state, str)
    
    def test_contains_all_primary_states(self):
        """Test that primary workflow states are included."""
        states = StateNames.get_all_states()
        expected_states = [
            StateNames.IDEA_CREATION,
            StateNames.TITLE_FROM_IDEA,
            StateNames.SCRIPT_FROM_IDEA_TITLE,
            StateNames.PUBLISHING,
        ]
        for expected in expected_states:
            assert expected in states, f"Missing state: {expected}"


class TestGetStatesByCategory:
    """Tests for get_states_by_category method."""
    
    def test_creation_category(self):
        """Test getting states by CREATION category."""
        states = StateNames.get_states_by_category(StateCategory.CREATION)
        assert StateNames.IDEA_CREATION in states
    
    def test_generation_category(self):
        """Test getting states by GENERATION category."""
        states = StateNames.get_states_by_category(StateCategory.GENERATION)
        assert StateNames.TITLE_FROM_IDEA in states
        assert StateNames.SCRIPT_FROM_IDEA_TITLE in states
    
    def test_review_category(self):
        """Test getting states by REVIEW category."""
        states = StateNames.get_states_by_category(StateCategory.REVIEW)
        assert StateNames.REVIEW_SCRIPT_GRAMMAR in states
        assert StateNames.STORY_REVIEW in states
    
    def test_refinement_category(self):
        """Test getting states by REFINEMENT category."""
        states = StateNames.get_states_by_category(StateCategory.REFINEMENT)
        assert StateNames.STORY_POLISH in states
    
    def test_publishing_category(self):
        """Test getting states by PUBLISHING category."""
        states = StateNames.get_states_by_category(StateCategory.PUBLISHING)
        assert StateNames.PUBLISHING in states
    
    def test_returns_list(self):
        """Test that method returns a list."""
        for category in StateCategory:
            states = StateNames.get_states_by_category(category)
            assert isinstance(states, list)


class TestGetStateCategory:
    """Tests for get_state_category method."""
    
    def test_returns_creation_for_idea_creation(self):
        """Test getting category for IDEA_CREATION."""
        category = StateNames.get_state_category(StateNames.IDEA_CREATION)
        assert category == StateCategory.CREATION
    
    def test_returns_generation_for_title_from_idea(self):
        """Test getting category for TITLE_FROM_IDEA."""
        category = StateNames.get_state_category(StateNames.TITLE_FROM_IDEA)
        assert category == StateCategory.GENERATION
    
    def test_returns_review_for_review_states(self):
        """Test getting category for review states."""
        category = StateNames.get_state_category(StateNames.REVIEW_SCRIPT_GRAMMAR)
        assert category == StateCategory.REVIEW
    
    def test_returns_publishing_for_publishing(self):
        """Test getting category for PUBLISHING."""
        category = StateNames.get_state_category(StateNames.PUBLISHING)
        assert category == StateCategory.PUBLISHING
    
    def test_returns_none_for_unknown_state(self):
        """Test that unknown states return None."""
        category = StateNames.get_state_category("PrismQ.T.Unknown.State")
        assert category is None


class TestIsValidState:
    """Tests for is_valid_state method."""
    
    def test_valid_state_returns_true(self):
        """Test that valid states return True."""
        assert StateNames.is_valid_state(StateNames.IDEA_CREATION) is True
        assert StateNames.is_valid_state(StateNames.PUBLISHING) is True
    
    def test_invalid_state_returns_false(self):
        """Test that invalid states return False."""
        assert StateNames.is_valid_state("PrismQ.T.Invalid.State") is False
        assert StateNames.is_valid_state("") is False
        assert StateNames.is_valid_state("RandomString") is False


class TestConvenienceMethods:
    """Tests for convenience methods."""
    
    def test_get_review_states(self):
        """Test get_review_states convenience method."""
        states = StateNames.get_review_states()
        assert StateNames.REVIEW_SCRIPT_GRAMMAR in states
        assert StateNames.STORY_REVIEW in states
    
    def test_get_generation_states(self):
        """Test get_generation_states convenience method."""
        states = StateNames.get_generation_states()
        assert StateNames.TITLE_FROM_IDEA in states
        assert StateNames.SCRIPT_FROM_IDEA_TITLE in states
    
    def test_get_quality_review_states(self):
        """Test get_quality_review_states method."""
        states = StateNames.get_quality_review_states()
        assert len(states) == 7  # 7 quality review states
        assert StateNames.REVIEW_SCRIPT_GRAMMAR in states
        assert StateNames.REVIEW_SCRIPT_TONE in states
        assert StateNames.REVIEW_SCRIPT_CONTENT in states
        assert StateNames.REVIEW_SCRIPT_CONSISTENCY in states
        assert StateNames.REVIEW_SCRIPT_EDITING in states
        assert StateNames.REVIEW_TITLE_READABILITY in states
        assert StateNames.REVIEW_SCRIPT_READABILITY in states
    
    def test_count_states(self):
        """Test count_states method."""
        count = StateNames.count_states()
        assert count >= 19  # At least 19 states defined


class TestParseStateName:
    """Tests for parse_state_name method."""
    
    def test_parse_simple_state(self):
        """Test parsing a simple state name."""
        result = StateNames.parse_state_name(StateNames.IDEA_CREATION)
        assert result['prefix'] == 'PrismQ.T'
        assert result['output'] == 'Idea'
    
    def test_parse_from_pattern_state(self):
        """Test parsing a state with From pattern."""
        result = StateNames.parse_state_name(StateNames.TITLE_FROM_IDEA)
        assert result['prefix'] == 'PrismQ.T'
        assert result['output'] == 'Title'
        assert result['action'] == 'From'
        assert result['input'] == 'Idea'
    
    def test_parse_complex_state(self):
        """Test parsing a complex state name."""
        result = StateNames.parse_state_name(StateNames.SCRIPT_FROM_IDEA_TITLE)
        assert result['prefix'] == 'PrismQ.T'
        assert result['output'] == 'Script'
        assert result['action'] == 'From'
        assert 'Idea.Title' in result['input']
    
    def test_parse_invalid_state_raises_error(self):
        """Test that parsing invalid state raises ValueError."""
        with pytest.raises(ValueError, match="Invalid state name"):
            StateNames.parse_state_name("Invalid.State.Name")
    
    def test_parse_malformed_state_raises_error(self):
        """Test that parsing malformed state with too few parts raises ValueError."""
        with pytest.raises(ValueError, match="Invalid state name"):
            StateNames.parse_state_name("PrismQ")


class TestConvenienceAliases:
    """Tests for convenience aliases."""
    
    def test_initial_states(self):
        """Test INITIAL_STATES alias."""
        assert StateNames.IDEA_CREATION in INITIAL_STATES
        assert len(INITIAL_STATES) == 1
    
    def test_terminal_states(self):
        """Test TERMINAL_STATES alias."""
        assert StateNames.PUBLISHING in TERMINAL_STATES
        assert len(TERMINAL_STATES) == 1
    
    def test_expert_review_states(self):
        """Test EXPERT_REVIEW_STATES alias."""
        assert StateNames.STORY_REVIEW in EXPERT_REVIEW_STATES
        assert StateNames.STORY_POLISH in EXPERT_REVIEW_STATES
        assert len(EXPERT_REVIEW_STATES) == 2


class TestExtensibility:
    """Tests to verify extensibility of the design."""
    
    def test_can_access_category_mappings(self):
        """Test that category mappings are accessible."""
        mappings = StateNames._CATEGORY_MAPPINGS
        assert isinstance(mappings, dict)
        assert StateCategory.CREATION in mappings
    
    def test_all_states_in_categories(self):
        """Test that all states belong to at least one category."""
        all_states = StateNames.get_all_states()
        categorized_states = set()
        for category in StateCategory:
            categorized_states.update(StateNames.get_states_by_category(category))
        
        for state in all_states:
            assert state in categorized_states, \
                f"State {state} is not in any category"
    
    def test_no_duplicate_states_across_categories(self):
        """Test that states don't appear in multiple categories."""
        seen_states = set()
        for category in StateCategory:
            states = StateNames.get_states_by_category(category)
            for state in states:
                assert state not in seen_states, \
                    f"State {state} appears in multiple categories"
                seen_states.add(state)


class TestStateMachineAlignment:
    """Tests to verify alignment with WORKFLOW_STATE_MACHINE.md."""
    
    def test_stage_1_exists(self):
        """Test Stage 1: IdeaCreation exists."""
        assert StateNames.IDEA_CREATION == "PrismQ.T.Idea.Creation"
    
    def test_stage_2_exists(self):
        """Test Stage 2: TitleFromIdea exists."""
        assert StateNames.TITLE_FROM_IDEA == "PrismQ.T.Title.From.Idea"
    
    def test_stage_3_exists(self):
        """Test Stage 3: ScriptFromIdeaTitle exists."""
        assert StateNames.SCRIPT_FROM_IDEA_TITLE == "PrismQ.T.Script.From.Idea.Title"
    
    def test_stages_4_6_review_cycle(self):
        """Test Stages 4-6: Initial review cycle states exist."""
        assert StateNames.is_valid_state(StateNames.REVIEW_TITLE_FROM_SCRIPT_IDEA)
        assert StateNames.is_valid_state(StateNames.REVIEW_SCRIPT_FROM_TITLE_IDEA)
        assert StateNames.is_valid_state(StateNames.REVIEW_TITLE_FROM_SCRIPT)
    
    def test_stages_7_9_refinement(self):
        """Test Stages 7-9: Refinement states exist."""
        assert StateNames.is_valid_state(StateNames.TITLE_FROM_TITLE_REVIEW_SCRIPT)
        assert StateNames.is_valid_state(StateNames.SCRIPT_FROM_SCRIPT_REVIEW_TITLE)
        assert StateNames.is_valid_state(StateNames.REVIEW_SCRIPT_FROM_TITLE)
    
    def test_stages_10_16_quality_reviews(self):
        """Test Stages 10-16: Quality review states exist."""
        quality_states = StateNames.get_quality_review_states()
        assert len(quality_states) == 7
    
    def test_stages_17_18_expert_review(self):
        """Test Stages 17-18: Expert review states exist."""
        assert StateNames.is_valid_state(StateNames.STORY_REVIEW)
        assert StateNames.is_valid_state(StateNames.STORY_POLISH)
    
    def test_terminal_state_exists(self):
        """Test Terminal state: Publishing exists."""
        assert StateNames.is_valid_state(StateNames.PUBLISHING)
