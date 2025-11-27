"""State Transition Validator for PrismQ workflow.

This module implements the TransitionValidator class that validates state
transitions in the PrismQ workflow state machine.

Following the Liskov Substitution Principle (LSP):
- TransitionValidator implements IValidator interface
- Can be substituted with any other IValidator implementation
- All validators are interchangeable

State Naming Convention:
- Generation states use the 'From' pattern: PrismQ.T.<Output>.From.<Input>
  Example: PrismQ.T.Title.From.Idea, PrismQ.T.Script.From.Title.Idea
- Review states use the 'By' pattern: PrismQ.T.Review.<Target>.By.<Source>
  Example: PrismQ.T.Review.Title.By.Script.Idea

Workflow Position:
    STATE-003: Create State Transition Validator
    Part of Sprint 4 - State Refactoring
"""

from types import MappingProxyType
from typing import Dict, List, Optional

from T.State.constants.state_names import StateNames
from T.State.interfaces.validator_interface import IValidator, ValidationResult


# Valid state transitions map based on WORKFLOW_STATE_MACHINE.md
# Each state maps to a list of valid next states
# Made immutable with MappingProxyType to prevent accidental modification
_TRANSITIONS_DICT: Dict[str, List[str]] = {
    # Initial state can only go to title generation (Stage 1 -> 2)
    StateNames.IDEA_CREATION: [
        StateNames.TITLE_FROM_IDEA,
    ],
    
    # Title from idea goes to script generation (Stage 2 -> 3)
    StateNames.TITLE_FROM_IDEA: [
        StateNames.SCRIPT_FROM_TITLE_IDEA,
    ],
    
    # Script from title+idea goes to initial title review (Stage 3 -> 4)
    StateNames.SCRIPT_FROM_TITLE_IDEA: [
        StateNames.REVIEW_TITLE_BY_SCRIPT_IDEA,
    ],
    
    # Initial title review (Stage 4)
    StateNames.REVIEW_TITLE_BY_SCRIPT_IDEA: [
        StateNames.REVIEW_SCRIPT_BY_TITLE_IDEA,  # Accepted -> Stage 5
        StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE,  # Not accepted -> Stage 7 (refine title)
    ],
    
    # Initial script review (Stage 5)
    StateNames.REVIEW_SCRIPT_BY_TITLE_IDEA: [
        StateNames.REVIEW_TITLE_BY_SCRIPT,  # Accepted -> Stage 6
        StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT,  # Not accepted -> Stage 8 (refine script)
    ],
    
    # Iterative title review (Stage 6)
    StateNames.REVIEW_TITLE_BY_SCRIPT: [
        StateNames.REVIEW_SCRIPT_BY_TITLE,  # Accepted -> Stage 9
        StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE,  # Not accepted -> Stage 7 (refine title)
    ],
    
    # Title refinement from review (Stage 7)
    StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE: [
        StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT,  # After title refinement -> Stage 8
        StateNames.REVIEW_SCRIPT_BY_TITLE_IDEA,  # Back to script review
        StateNames.REVIEW_TITLE_BY_SCRIPT,  # Back to title review cycle
    ],
    
    # Script refinement from review (Stage 8)
    StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT: [
        StateNames.REVIEW_TITLE_BY_SCRIPT,  # After script refinement -> title review
        StateNames.REVIEW_SCRIPT_BY_TITLE,  # After script refinement -> script review
    ],
    
    # Iterative script review (Stage 9) - Gateway to quality reviews
    StateNames.REVIEW_SCRIPT_BY_TITLE: [
        StateNames.REVIEW_SCRIPT_GRAMMAR,  # Accepted -> Start quality reviews (Stage 10)
        StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT,  # Not accepted -> Stage 8 (refine script)
    ],
    
    # Quality review chain (Stages 10-16) - linear progression with failure paths
    StateNames.REVIEW_SCRIPT_GRAMMAR: [
        StateNames.REVIEW_SCRIPT_TONE,  # Passes -> Stage 11
        StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT,  # Fails -> Stage 8
    ],
    
    StateNames.REVIEW_SCRIPT_TONE: [
        StateNames.REVIEW_SCRIPT_CONTENT,  # Passes -> Stage 12
        StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT,  # Fails -> Stage 8
    ],
    
    StateNames.REVIEW_SCRIPT_CONTENT: [
        StateNames.REVIEW_SCRIPT_CONSISTENCY,  # Passes -> Stage 13
        StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT,  # Fails -> Stage 8
    ],
    
    StateNames.REVIEW_SCRIPT_CONSISTENCY: [
        StateNames.REVIEW_SCRIPT_EDITING,  # Passes -> Stage 14
        StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT,  # Fails -> Stage 8
    ],
    
    StateNames.REVIEW_SCRIPT_EDITING: [
        StateNames.REVIEW_TITLE_READABILITY,  # Passes -> Stage 15
        StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT,  # Fails -> Stage 8
    ],
    
    StateNames.REVIEW_TITLE_READABILITY: [
        StateNames.REVIEW_SCRIPT_READABILITY,  # Passes -> Stage 16
        StateNames.TITLE_FROM_SCRIPT_REVIEW_TITLE,  # Fails -> Stage 7
    ],
    
    StateNames.REVIEW_SCRIPT_READABILITY: [
        StateNames.STORY_REVIEW,  # Passes -> Stage 17
        StateNames.SCRIPT_FROM_TITLE_REVIEW_SCRIPT,  # Fails -> Stage 8
    ],
    
    # Expert review loop (Stages 17-18)
    StateNames.STORY_REVIEW: [
        StateNames.PUBLISHING,  # Accepted -> Terminal
        StateNames.STORY_POLISH,  # Not accepted -> Stage 18
    ],
    
    StateNames.STORY_POLISH: [
        StateNames.STORY_REVIEW,  # Loop back to Stage 17
    ],
    
    # Terminal state - no valid transitions from Publishing
    StateNames.PUBLISHING: [],
}

# Immutable view of transitions - prevents accidental modification
TRANSITIONS = MappingProxyType(_TRANSITIONS_DICT)


class TransitionValidator(IValidator):
    """Validates state transitions in the PrismQ workflow.
    
    This validator implements the IValidator interface and checks if
    state transitions are valid according to the defined transition map.
    
    Following Liskov Substitution Principle (LSP):
    - Can be substituted with any other IValidator implementation
    - Behavior is consistent with the interface contract
    - Does not throw unexpected exceptions
    
    Attributes:
        transitions: Dictionary mapping states to valid next states
        
    Example:
        >>> validator = TransitionValidator()
        >>> result = validator.validate(
        ...     StateNames.IDEA_CREATION,
        ...     StateNames.TITLE_FROM_IDEA
        ... )
        >>> print(result.is_valid)
        True
        >>> print(validator.is_valid_transition(
        ...     StateNames.TITLE_FROM_IDEA,
        ...     StateNames.PUBLISHING  # Invalid - can't skip to publishing
        ... ))
        False
    """
    
    def __init__(
        self,
        transitions: Optional[Dict[str, List[str]]] = None
    ):
        """Initialize the TransitionValidator.
        
        Args:
            transitions: Optional custom transition map. If not provided,
                        uses the default TRANSITIONS constant.
        """
        self.transitions = transitions if transitions is not None else TRANSITIONS
    
    def validate(self, from_state: str, to_state: str) -> ValidationResult:
        """Validate a state transition.
        
        Args:
            from_state: The current/source state
            to_state: The target state to transition to
            
        Returns:
            ValidationResult indicating whether the transition is valid
        """
        # Check if from_state exists in the transition map
        if from_state not in self.transitions:
            return ValidationResult(
                is_valid=False,
                error_message=f"Unknown state: {from_state}",
                from_state=from_state,
                to_state=to_state
            )
        
        # Check if to_state is in the list of valid next states
        valid_next_states = self.transitions[from_state]
        
        if to_state in valid_next_states:
            return ValidationResult(
                is_valid=True,
                from_state=from_state,
                to_state=to_state
            )
        
        return ValidationResult(
            is_valid=False,
            error_message=(
                f"Invalid transition from {from_state} to {to_state}. "
                f"Valid next states: {valid_next_states}"
            ),
            from_state=from_state,
            to_state=to_state
        )
    
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a state transition is valid.
        
        Args:
            from_state: The current/source state
            to_state: The target state to transition to
            
        Returns:
            True if the transition is valid, False otherwise
        """
        return self.validate(from_state, to_state).is_valid
    
    def get_valid_next_states(self, current_state: str) -> List[str]:
        """Get all valid next states from the current state.
        
        Args:
            current_state: The current state
            
        Returns:
            List of state names that are valid transitions from current_state.
            Returns empty list if state is unknown.
        """
        return self.transitions.get(current_state, [])
    
    def get_all_states(self) -> List[str]:
        """Get all known states in the transition map.
        
        Returns:
            List of all state names
        """
        # Collect all states (both as keys and values)
        all_states = set(self.transitions.keys())
        for next_states in self.transitions.values():
            all_states.update(next_states)
        return sorted(list(all_states))
    
    def is_terminal_state(self, state: str) -> bool:
        """Check if a state is terminal (no valid outgoing transitions).
        
        Args:
            state: The state to check
            
        Returns:
            True if the state has no valid outgoing transitions
        """
        return len(self.get_valid_next_states(state)) == 0
    
    def get_path_validation(self, path: List[str]) -> ValidationResult:
        """Validate an entire path through the state machine.
        
        Args:
            path: List of states representing a path through the workflow
            
        Returns:
            ValidationResult indicating whether the entire path is valid
        """
        if not path:
            return ValidationResult(
                is_valid=True,
                error_message=None
            )
        
        if len(path) == 1:
            # Single state is valid if it's a known state
            # Use the get_all_states method which returns a cached view of all states
            all_states = set(self.get_all_states())
            if path[0] in all_states:
                return ValidationResult(is_valid=True)
            return ValidationResult(
                is_valid=False,
                error_message=f"Unknown state: {path[0]}"
            )
        
        # Validate each transition in the path
        for i in range(len(path) - 1):
            from_state = path[i]
            to_state = path[i + 1]
            result = self.validate(from_state, to_state)
            if not result.is_valid:
                return ValidationResult(
                    is_valid=False,
                    error_message=(
                        f"Invalid transition at step {i + 1}: "
                        f"{result.error_message}"
                    ),
                    from_state=from_state,
                    to_state=to_state
                )
        
        return ValidationResult(is_valid=True)


__all__ = ["TransitionValidator", "TRANSITIONS"]
