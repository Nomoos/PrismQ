"""PrismQ.T.State - State Machine for Content Production Workflow.

This module provides the state machine implementation for the PrismQ
content production workflow. It includes:

- IState interface defining the contract for all state implementations
- State transition logic
- State validation

Main Classes:
    - IState: Interface defining state behavior contract

Example:
    >>> from T.State.interfaces import IState
    >>> 
    >>> class MyState(IState):
    ...     def get_name(self) -> str:
    ...         return "MyState"
    ...     
    ...     def get_next_states(self) -> list[str]:
    ...         return ["NextState1", "NextState2"]
    ...     
    ...     def can_transition_to(self, target_state: str) -> bool:
    ...         return target_state in self.get_next_states()
"""

from .interfaces import IState

__all__ = [
    'IState',
]
