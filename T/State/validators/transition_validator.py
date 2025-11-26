"""State Transition Validator for PrismQ workflow.

This module implements the TransitionValidator class that validates state
transitions in the PrismQ workflow state machine.

Following the Liskov Substitution Principle (LSP):
- TransitionValidator implements IValidator interface
- Can be substituted with any other IValidator implementation
- All validators are interchangeable

State Naming Convention:
- States follow the pattern: PrismQ.T.<Output>.From.<Input>
- Example: PrismQ.T.Title.From.Idea, PrismQ.T.Script.From.Idea.Title

Workflow Position:
    STATE-003: Create State Transition Validator
    Part of Sprint 4 - State Refactoring
"""

from typing import Dict, List, Optional
from T.State.interfaces.validator_interface import IValidator, ValidationResult


# State name constants following PrismQ naming convention
# Pattern: PrismQ.T.<Output>.From.<Input>
class StateNames:
    """State name constants for the PrismQ.T workflow.
    
    All state names follow the pattern: PrismQ.T.<Output>.From.<Input>
    These are used for state machine transitions and validation.
    """
    # Initial state
    IDEA_CREATION = "PrismQ.T.Idea.Creation"
    
    # Title generation states
    TITLE_FROM_IDEA = "PrismQ.T.Title.From.Idea"
    TITLE_FROM_SCRIPT_REVIEW = "PrismQ.T.Title.From.Script.Review.Title"
    
    # Script generation states
    SCRIPT_FROM_IDEA_TITLE = "PrismQ.T.Script.From.Idea.Title"
    SCRIPT_FROM_TITLE_REVIEW = "PrismQ.T.Script.From.Title.Review.Script"
    
    # Review states
    REVIEW_TITLE_FROM_SCRIPT_IDEA = "PrismQ.T.Review.Title.From.Script.Idea"
    REVIEW_SCRIPT_FROM_TITLE_IDEA = "PrismQ.T.Review.Script.From.Title.Idea"
    REVIEW_TITLE_FROM_SCRIPT = "PrismQ.T.Review.Title.From.Script"
    REVIEW_SCRIPT_FROM_TITLE = "PrismQ.T.Review.Script.From.Title"
    
    # Quality review states
    REVIEW_SCRIPT_GRAMMAR = "PrismQ.T.Review.Script.Grammar"
    REVIEW_SCRIPT_TONE = "PrismQ.T.Review.Script.Tone"
    REVIEW_SCRIPT_CONTENT = "PrismQ.T.Review.Script.Content"
    REVIEW_SCRIPT_CONSISTENCY = "PrismQ.T.Review.Script.Consistency"
    REVIEW_SCRIPT_EDITING = "PrismQ.T.Review.Script.Editing"
    REVIEW_TITLE_READABILITY = "PrismQ.T.Review.Title.Readability"
    REVIEW_SCRIPT_READABILITY = "PrismQ.T.Review.Script.Readability"
    
    # Story review states
    STORY_REVIEW = "PrismQ.T.Story.Review"
    STORY_POLISH = "PrismQ.T.Story.Polish"
    
    # Terminal state
    PUBLISHING = "PrismQ.T.Publishing"


# Valid state transitions map based on WORKFLOW_STATE_MACHINE.md
# Each state maps to a list of valid next states
TRANSITIONS: Dict[str, List[str]] = {
    # Initial state can only go to title generation
    StateNames.IDEA_CREATION: [
        StateNames.TITLE_FROM_IDEA,
    ],
    
    # Title from idea goes to script generation
    StateNames.TITLE_FROM_IDEA: [
        StateNames.SCRIPT_FROM_IDEA_TITLE,
    ],
    
    # Script from idea+title goes to initial reviews
    StateNames.SCRIPT_FROM_IDEA_TITLE: [
        StateNames.REVIEW_TITLE_FROM_SCRIPT_IDEA,
    ],
    
    # Initial title review
    StateNames.REVIEW_TITLE_FROM_SCRIPT_IDEA: [
        StateNames.REVIEW_SCRIPT_FROM_TITLE_IDEA,
        StateNames.TITLE_FROM_SCRIPT_REVIEW,  # If review suggests changes
    ],
    
    # Initial script review
    StateNames.REVIEW_SCRIPT_FROM_TITLE_IDEA: [
        StateNames.REVIEW_TITLE_FROM_SCRIPT,
        StateNames.SCRIPT_FROM_TITLE_REVIEW,  # If review suggests changes
    ],
    
    # Iterative title review
    StateNames.REVIEW_TITLE_FROM_SCRIPT: [
        StateNames.REVIEW_SCRIPT_FROM_TITLE,
        StateNames.TITLE_FROM_SCRIPT_REVIEW,  # If review suggests changes
    ],
    
    # Iterative script review
    StateNames.REVIEW_SCRIPT_FROM_TITLE: [
        StateNames.REVIEW_SCRIPT_GRAMMAR,  # Move to quality reviews
        StateNames.SCRIPT_FROM_TITLE_REVIEW,  # If review suggests changes
    ],
    
    # Title refinement from review
    StateNames.TITLE_FROM_SCRIPT_REVIEW: [
        StateNames.REVIEW_SCRIPT_FROM_TITLE_IDEA,
        StateNames.REVIEW_TITLE_FROM_SCRIPT,
        StateNames.SCRIPT_FROM_TITLE_REVIEW,
    ],
    
    # Script refinement from review  
    StateNames.SCRIPT_FROM_TITLE_REVIEW: [
        StateNames.REVIEW_SCRIPT_FROM_TITLE,
        StateNames.REVIEW_TITLE_FROM_SCRIPT,
    ],
    
    # Quality review chain (linear progression with failure paths)
    StateNames.REVIEW_SCRIPT_GRAMMAR: [
        StateNames.REVIEW_SCRIPT_TONE,
        StateNames.SCRIPT_FROM_TITLE_REVIEW,  # Failure path
    ],
    
    StateNames.REVIEW_SCRIPT_TONE: [
        StateNames.REVIEW_SCRIPT_CONTENT,
        StateNames.SCRIPT_FROM_TITLE_REVIEW,  # Failure path
    ],
    
    StateNames.REVIEW_SCRIPT_CONTENT: [
        StateNames.REVIEW_SCRIPT_CONSISTENCY,
        StateNames.SCRIPT_FROM_TITLE_REVIEW,  # Failure path
    ],
    
    StateNames.REVIEW_SCRIPT_CONSISTENCY: [
        StateNames.REVIEW_SCRIPT_EDITING,
        StateNames.SCRIPT_FROM_TITLE_REVIEW,  # Failure path
    ],
    
    StateNames.REVIEW_SCRIPT_EDITING: [
        StateNames.REVIEW_TITLE_READABILITY,
        StateNames.SCRIPT_FROM_TITLE_REVIEW,  # Failure path
    ],
    
    StateNames.REVIEW_TITLE_READABILITY: [
        StateNames.REVIEW_SCRIPT_READABILITY,
        StateNames.TITLE_FROM_SCRIPT_REVIEW,  # Failure path
    ],
    
    StateNames.REVIEW_SCRIPT_READABILITY: [
        StateNames.STORY_REVIEW,
        StateNames.SCRIPT_FROM_TITLE_REVIEW,  # Failure path
    ],
    
    # Expert review loop
    StateNames.STORY_REVIEW: [
        StateNames.PUBLISHING,  # Accepted
        StateNames.STORY_POLISH,  # Not accepted - needs polish
    ],
    
    StateNames.STORY_POLISH: [
        StateNames.STORY_REVIEW,  # Loop back to review
    ],
    
    # Terminal state - no valid transitions from Publishing
    StateNames.PUBLISHING: [],
}


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
            if path[0] in self.transitions or path[0] in [
                state for states in self.transitions.values() for state in states
            ]:
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


__all__ = ["TransitionValidator", "StateNames", "TRANSITIONS"]
