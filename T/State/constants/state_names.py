"""State name constants for PrismQ.T workflow state machine.

This module re-exports from T.Model.state for backward compatibility.
The canonical location for state constants is now T/Model/state.py.

Example Usage:
    >>> from T.Model import StateNames, StoryState  # Preferred
    >>> # or for backward compatibility:
    >>> from T.State.constants.state_names import StateNames, StoryState
"""

# Re-export from canonical location
from T.Model.state import (
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
