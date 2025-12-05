"""State name constants for PrismQ.T workflow state machine.

This module re-exports from Model.state for backward compatibility.
The canonical location for state constants is now Model/state.py.

Example Usage:
    >>> from Model import StateNames, StoryState  # Preferred
    >>> # or for backward compatibility:
    >>> from Model.State.constants.state_names import StateNames, StoryState
"""

# Re-export from canonical location
from Model.state import (
    StateCategory,
    StoryState,
    StateNames,
    INITIAL_STATES,
    TERMINAL_STATES,
    EXPERT_REVIEW_STATES,
)

__all__ = [
    "StateCategory",
    "StoryState",
    "StateNames",
    "INITIAL_STATES",
    "TERMINAL_STATES",
    "EXPERT_REVIEW_STATES",
]
