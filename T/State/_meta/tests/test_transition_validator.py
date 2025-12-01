"""Tests for State Transition Validator.

This module tests the TransitionValidator class and IValidator interface
to ensure:
1. All validators implement IValidator correctly (Liskov Substitution)
2. Valid transitions are allowed
3. Invalid transitions are rejected
4. All state transitions defined in WORKFLOW_STATE_MACHINE.md are covered

Test Categories:
- TestValidatorInterface: Tests for IValidator interface compliance
- TestTransitionValidatorBasic: Basic functionality tests
- TestValidTransitions: Tests for valid state transitions
- TestInvalidTransitions: Tests for invalid state transitions
- TestEdgeCases: Edge case handling
- TestLiskovSubstitution: Verify LSP compliance
"""

import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import pytest
from T.State.interfaces.validator_interface import IValidator, ValidationResult
from T.State.validators.transition_validator import (
    TransitionValidator,
    TRANSITIONS
)
from T.State.constants.state_names import StateNames


class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_create_valid_result(self):
        """Test creating a valid result."""
        result = ValidationResult(is_valid=True)
        
        assert result.is_valid is True
        assert result.error_message is None
        assert result.from_state is None
        assert result.to_state is None
    
    def test_create_invalid_result(self):
        """Test creating an invalid result with error message."""
        result = ValidationResult(
            is_valid=False,
            error_message="Invalid transition",
            from_state="StateA",
            to_state="StateB"
        )
        
        assert result.is_valid is False
        assert result.error_message == "Invalid transition"
        assert result.from_state == "StateA"
        assert result.to_state == "StateB"
    
    def test_bool_conversion_valid(self):
        """Test that valid result evaluates to True."""
        result = ValidationResult(is_valid=True)
        assert bool(result) is True
        
        # Can be used in if statements
        if result:
            passed = True
        else:
            passed = False
        assert passed is True
    
    def test_bool_conversion_invalid(self):
        """Test that invalid result evaluates to False."""
        result = ValidationResult(is_valid=False)
        assert bool(result) is False


class TestValidatorInterface:
    """Tests to verify IValidator interface compliance."""
    
    def test_transition_validator_implements_interface(self):
        """Test that TransitionValidator implements IValidator."""
        validator = TransitionValidator()
        
        assert isinstance(validator, IValidator)
    
    def test_interface_has_required_methods(self):
        """Test that IValidator defines required abstract methods."""
        # These methods should be abstract
        assert hasattr(IValidator, 'validate')
        assert hasattr(IValidator, 'is_valid_transition')
        assert hasattr(IValidator, 'get_valid_next_states')
    
    def test_cannot_instantiate_interface_directly(self):
        """Test that IValidator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            IValidator()


class TestTransitionValidatorBasic:
    """Basic functionality tests for TransitionValidator."""
    
    def test_create_default_validator(self):
        """Test creating validator with default transitions."""
        validator = TransitionValidator()
        
        assert validator.transitions is not None
        assert len(validator.transitions) > 0
    
    def test_create_custom_validator(self):
        """Test creating validator with custom transitions."""
        custom_transitions = {
            "StateA": ["StateB"],
            "StateB": ["StateC"],
            "StateC": [],
        }
        
        validator = TransitionValidator(transitions=custom_transitions)
        
        assert validator.transitions == custom_transitions
    
    def test_get_all_states(self):
        """Test getting all known states."""
        validator = TransitionValidator()
        states = validator.get_all_states()
        
        assert isinstance(states, list)
        assert len(states) > 0
        assert StateNames.IDEA_CREATION in states
        assert StateNames.PUBLISHING in states
    
    def test_is_terminal_state(self):
        """Test identifying terminal states."""
        validator = TransitionValidator()
        
        # Publishing is terminal (no outgoing transitions)
        assert validator.is_terminal_state(StateNames.PUBLISHING) is True
        
        # Idea creation is not terminal
        assert validator.is_terminal_state(StateNames.IDEA_CREATION) is False


class TestValidTransitions:
    """Tests for valid state transitions."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance for tests."""
        return TransitionValidator()
    
    def test_idea_to_title(self, validator):
        """Test transition from idea creation to title generation."""
        result = validator.validate(
            StateNames.IDEA_CREATION,
            StateNames.TITLE_FROM_IDEA
        )
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_title_to_script(self, validator):
        """Test transition from title to script generation."""
        result = validator.validate(
            StateNames.TITLE_FROM_IDEA,
            StateNames.SCRIPT_FROM_IDEA_TITLE
        )
        
        assert result.is_valid is True
    
    def test_script_to_review(self, validator):
        """Test transition from script to review."""
        result = validator.validate(
            StateNames.SCRIPT_FROM_IDEA_TITLE,
            StateNames.REVIEW_TITLE_FROM_SCRIPT_IDEA
        )
        
        assert result.is_valid is True
    
    def test_review_to_quality_reviews(self, validator):
        """Test transition to quality review chain."""
        result = validator.validate(
            StateNames.REVIEW_SCRIPT_FROM_TITLE,
            StateNames.REVIEW_SCRIPT_GRAMMAR
        )
        
        assert result.is_valid is True
    
    def test_quality_review_chain(self, validator):
        """Test the quality review chain progression."""
        # Grammar -> Tone
        assert validator.is_valid_transition(
            StateNames.REVIEW_SCRIPT_GRAMMAR,
            StateNames.REVIEW_SCRIPT_TONE
        )
        
        # Tone -> Content
        assert validator.is_valid_transition(
            StateNames.REVIEW_SCRIPT_TONE,
            StateNames.REVIEW_SCRIPT_CONTENT
        )
        
        # Content -> Consistency
        assert validator.is_valid_transition(
            StateNames.REVIEW_SCRIPT_CONTENT,
            StateNames.REVIEW_SCRIPT_CONSISTENCY
        )
        
        # Consistency -> Editing
        assert validator.is_valid_transition(
            StateNames.REVIEW_SCRIPT_CONSISTENCY,
            StateNames.REVIEW_SCRIPT_EDITING
        )
        
        # Editing -> Title Readability
        assert validator.is_valid_transition(
            StateNames.REVIEW_SCRIPT_EDITING,
            StateNames.REVIEW_TITLE_READABILITY
        )
        
        # Title Readability -> Script Readability
        assert validator.is_valid_transition(
            StateNames.REVIEW_TITLE_READABILITY,
            StateNames.REVIEW_SCRIPT_READABILITY
        )
    
    def test_readability_to_story_review(self, validator):
        """Test transition from readability to expert review."""
        result = validator.validate(
            StateNames.REVIEW_SCRIPT_READABILITY,
            StateNames.STORY_REVIEW
        )
        
        assert result.is_valid is True
    
    def test_story_review_to_publishing(self, validator):
        """Test transition from story review to publishing (accepted)."""
        result = validator.validate(
            StateNames.STORY_REVIEW,
            StateNames.PUBLISHING
        )
        
        assert result.is_valid is True
    
    def test_story_review_to_polish(self, validator):
        """Test transition from story review to polish (not accepted)."""
        result = validator.validate(
            StateNames.STORY_REVIEW,
            StateNames.STORY_POLISH
        )
        
        assert result.is_valid is True
    
    def test_polish_loops_to_review(self, validator):
        """Test that polish loops back to story review."""
        result = validator.validate(
            StateNames.STORY_POLISH,
            StateNames.STORY_REVIEW
        )
        
        assert result.is_valid is True
    
    def test_review_failure_paths(self, validator):
        """Test failure paths in quality reviews."""
        # Grammar failure can go to script refinement
        assert validator.is_valid_transition(
            StateNames.REVIEW_SCRIPT_GRAMMAR,
            StateNames.SCRIPT_FROM_SCRIPT_REVIEW_TITLE
        )
        
        # Title readability failure can go to title refinement
        assert validator.is_valid_transition(
            StateNames.REVIEW_TITLE_READABILITY,
            StateNames.TITLE_FROM_TITLE_REVIEW_SCRIPT
        )


class TestInvalidTransitions:
    """Tests for invalid state transitions."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance for tests."""
        return TransitionValidator()
    
    def test_cannot_skip_to_publishing(self, validator):
        """Test that can't skip directly to publishing from early states."""
        result = validator.validate(
            StateNames.IDEA_CREATION,
            StateNames.PUBLISHING
        )
        
        assert result.is_valid is False
        assert "Invalid transition" in result.error_message
    
    def test_cannot_go_backwards_from_publishing(self, validator):
        """Test that publishing is terminal (no transitions out)."""
        # Try various states
        for state in [
            StateNames.IDEA_CREATION,
            StateNames.TITLE_FROM_IDEA,
            StateNames.STORY_REVIEW
        ]:
            result = validator.validate(StateNames.PUBLISHING, state)
            assert result.is_valid is False
    
    def test_cannot_skip_review_chain(self, validator):
        """Test that can't skip steps in review chain."""
        # Can't go from grammar directly to consistency
        result = validator.validate(
            StateNames.REVIEW_SCRIPT_GRAMMAR,
            StateNames.REVIEW_SCRIPT_CONSISTENCY
        )
        
        assert result.is_valid is False
    
    def test_unknown_state(self, validator):
        """Test handling of unknown states."""
        result = validator.validate(
            "Unknown.State",
            StateNames.PUBLISHING
        )
        
        assert result.is_valid is False
        assert "Unknown state" in result.error_message
    
    def test_invalid_transition_message_includes_valid_states(self, validator):
        """Test that error message includes valid next states."""
        result = validator.validate(
            StateNames.IDEA_CREATION,
            StateNames.PUBLISHING
        )
        
        assert result.is_valid is False
        # Message should mention valid next states
        assert StateNames.TITLE_FROM_IDEA in result.error_message


class TestGetValidNextStates:
    """Tests for get_valid_next_states method."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance for tests."""
        return TransitionValidator()
    
    def test_idea_creation_next_states(self, validator):
        """Test valid next states from idea creation."""
        next_states = validator.get_valid_next_states(StateNames.IDEA_CREATION)
        
        assert StateNames.TITLE_FROM_IDEA in next_states
        assert len(next_states) == 1
    
    def test_publishing_has_no_next_states(self, validator):
        """Test that publishing has no valid next states."""
        next_states = validator.get_valid_next_states(StateNames.PUBLISHING)
        
        assert len(next_states) == 0
    
    def test_unknown_state_returns_empty_list(self, validator):
        """Test that unknown state returns empty list."""
        next_states = validator.get_valid_next_states("Unknown.State")
        
        assert len(next_states) == 0
    
    def test_story_review_has_multiple_next_states(self, validator):
        """Test states with multiple valid transitions."""
        next_states = validator.get_valid_next_states(StateNames.STORY_REVIEW)
        
        assert StateNames.PUBLISHING in next_states
        assert StateNames.STORY_POLISH in next_states
        assert len(next_states) == 2


class TestPathValidation:
    """Tests for path validation."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance for tests."""
        return TransitionValidator()
    
    def test_valid_ideal_path(self, validator):
        """Test validating the ideal (happy) path through workflow."""
        ideal_path = [
            StateNames.IDEA_CREATION,
            StateNames.TITLE_FROM_IDEA,
            StateNames.SCRIPT_FROM_IDEA_TITLE,
            StateNames.REVIEW_TITLE_FROM_SCRIPT_IDEA,
            StateNames.REVIEW_SCRIPT_FROM_TITLE_IDEA,
            StateNames.REVIEW_TITLE_FROM_SCRIPT,
            StateNames.REVIEW_SCRIPT_FROM_TITLE,
            StateNames.REVIEW_SCRIPT_GRAMMAR,
            StateNames.REVIEW_SCRIPT_TONE,
            StateNames.REVIEW_SCRIPT_CONTENT,
            StateNames.REVIEW_SCRIPT_CONSISTENCY,
            StateNames.REVIEW_SCRIPT_EDITING,
            StateNames.REVIEW_TITLE_READABILITY,
            StateNames.REVIEW_SCRIPT_READABILITY,
            StateNames.STORY_REVIEW,
            StateNames.PUBLISHING,
        ]
        
        result = validator.get_path_validation(ideal_path)
        
        assert result.is_valid is True
    
    def test_valid_path_with_iteration(self, validator):
        """Test path that includes iteration (polish loop)."""
        path_with_iteration = [
            StateNames.STORY_REVIEW,
            StateNames.STORY_POLISH,
            StateNames.STORY_REVIEW,
            StateNames.PUBLISHING,
        ]
        
        result = validator.get_path_validation(path_with_iteration)
        
        assert result.is_valid is True
    
    def test_invalid_path(self, validator):
        """Test detecting invalid path."""
        invalid_path = [
            StateNames.IDEA_CREATION,
            StateNames.PUBLISHING,  # Can't skip to publishing
        ]
        
        result = validator.get_path_validation(invalid_path)
        
        assert result.is_valid is False
        assert "Invalid transition" in result.error_message
    
    def test_empty_path_is_valid(self, validator):
        """Test that empty path is valid."""
        result = validator.get_path_validation([])
        
        assert result.is_valid is True
    
    def test_single_state_path(self, validator):
        """Test that single state path is valid for known states."""
        result = validator.get_path_validation([StateNames.IDEA_CREATION])
        
        assert result.is_valid is True
    
    def test_single_unknown_state_path(self, validator):
        """Test that single unknown state path is invalid."""
        result = validator.get_path_validation(["Unknown.State"])
        
        assert result.is_valid is False


class TestLiskovSubstitution:
    """Tests to verify Liskov Substitution Principle compliance."""
    
    def test_custom_validator_substitution(self):
        """Test that a custom validator can substitute TransitionValidator."""
        # Create a simple custom validator
        class SimpleValidator(IValidator):
            def __init__(self):
                self.transitions = {"A": ["B"], "B": []}
            
            def validate(self, from_state: str, to_state: str) -> ValidationResult:
                valid = to_state in self.transitions.get(from_state, [])
                return ValidationResult(
                    is_valid=valid,
                    from_state=from_state,
                    to_state=to_state
                )
            
            def is_valid_transition(self, from_state: str, to_state: str) -> bool:
                return self.validate(from_state, to_state).is_valid
            
            def get_valid_next_states(self, current_state: str) -> List[str]:
                return self.transitions.get(current_state, [])
        
        # Both validators should work the same way through the interface
        simple = SimpleValidator()
        transition = TransitionValidator()
        
        # Both are IValidator instances
        assert isinstance(simple, IValidator)
        assert isinstance(transition, IValidator)
        
        # Both have the same interface methods
        assert hasattr(simple, 'validate')
        assert hasattr(simple, 'is_valid_transition')
        assert hasattr(simple, 'get_valid_next_states')
        
        # Simple validator works correctly
        assert simple.is_valid_transition("A", "B") is True
        assert simple.is_valid_transition("A", "C") is False
    
    def test_validator_can_be_passed_to_function(self):
        """Test that validators can be passed to functions expecting IValidator."""
        def check_transition(validator: IValidator, from_s: str, to_s: str) -> bool:
            return validator.is_valid_transition(from_s, to_s)
        
        validator = TransitionValidator()
        
        result = check_transition(
            validator,
            StateNames.IDEA_CREATION,
            StateNames.TITLE_FROM_IDEA
        )
        
        assert result is True


class TestStateNames:
    """Tests for StateNames constants."""
    
    def test_state_names_follow_convention(self):
        """Test that all state names follow PrismQ.T.* convention."""
        # Get all string attributes that start with the state prefix (actual state constants)
        state_attrs = [
            (attr, getattr(StateNames, attr))
            for attr in dir(StateNames)
            if not attr.startswith('_') 
            and attr.isupper()
            and isinstance(getattr(StateNames, attr), str)
            and getattr(StateNames, attr).startswith(StateNames.STATE_PREFIX + '.')
        ]
        
        # Ensure we found state constants
        assert len(state_attrs) > 0, "No state constants found"
        
        for attr, state_name in state_attrs:
            assert state_name.startswith("PrismQ.T."), \
                f"State {attr} doesn't follow naming convention: {state_name}"
    
    def test_all_states_in_transitions_exist(self):
        """Test that all states referenced in TRANSITIONS are defined."""
        # Get all state names from StateNames class
        defined_states = set(
            getattr(StateNames, attr) 
            for attr in dir(StateNames) 
            if not attr.startswith('_') and attr.isupper()
        )
        
        # Get all states from TRANSITIONS
        transition_states = set(TRANSITIONS.keys())
        for next_states in TRANSITIONS.values():
            transition_states.update(next_states)
        
        # All transition states should be defined
        for state in transition_states:
            assert state in defined_states, \
                f"State {state} used in transitions but not defined in StateNames"


class TestWorkflowCoverage:
    """Tests to ensure all workflow states from WORKFLOW_STATE_MACHINE.md are covered."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance for tests."""
        return TransitionValidator()
    
    def test_initial_state_defined(self, validator):
        """Test that initial state (IdeaCreation) is defined."""
        states = validator.get_all_states()
        assert StateNames.IDEA_CREATION in states
    
    def test_terminal_state_defined(self, validator):
        """Test that terminal state (Publishing) is defined."""
        states = validator.get_all_states()
        assert StateNames.PUBLISHING in states
    
    def test_all_quality_review_states_defined(self, validator):
        """Test that all quality review states are defined."""
        quality_states = [
            StateNames.REVIEW_SCRIPT_GRAMMAR,
            StateNames.REVIEW_SCRIPT_TONE,
            StateNames.REVIEW_SCRIPT_CONTENT,
            StateNames.REVIEW_SCRIPT_CONSISTENCY,
            StateNames.REVIEW_SCRIPT_EDITING,
            StateNames.REVIEW_TITLE_READABILITY,
            StateNames.REVIEW_SCRIPT_READABILITY,
        ]
        
        states = validator.get_all_states()
        for state in quality_states:
            assert state in states, f"Quality review state {state} not defined"
    
    def test_expert_review_loop_defined(self, validator):
        """Test that expert review loop states are defined."""
        assert StateNames.STORY_REVIEW in validator.get_all_states()
        assert StateNames.STORY_POLISH in validator.get_all_states()
        
        # Loop should work
        assert validator.is_valid_transition(
            StateNames.STORY_REVIEW,
            StateNames.STORY_POLISH
        )
        assert validator.is_valid_transition(
            StateNames.STORY_POLISH,
            StateNames.STORY_REVIEW
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
