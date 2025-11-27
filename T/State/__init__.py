"""PrismQ State module for state management and validation.

This module provides state machine infrastructure for the PrismQ workflow,
including state interfaces, validators, and transition logic.

Following SOLID principles:
- Single Responsibility: Each state has one responsibility
- Open/Closed: States can be extended without modification
- Liskov Substitution: All validators are interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions, not concretions
"""

from T.State.interfaces.validator_interface import IValidator
from T.State.validators.transition_validator import TransitionValidator

__all__ = [
    "IValidator",
    "TransitionValidator",
"""State module for PrismQ.T workflow state management.

This module provides state constants and utilities for the text generation pipeline.
"""

from T.State.constants.state_names import StateNames, StateCategory

__all__ = ["StateNames", "StateCategory"]
"""PrismQ.T.State - State Machine for Content Production Workflow.

This module provides the state machine implementation for the PrismQ
content production workflow. It includes:

- IState interface defining the contract for all state implementations
- State transition logic
- State validation

Main Classes:
    - IState: Interface defining state behavior contract

Example:
    >>> from typing import List
    >>> from T.State.interfaces import IState
    >>> 
    >>> class MyState(IState):
    ...     def get_name(self) -> str:
    ...         return "MyState"
    ...     
    ...     def get_next_states(self) -> List[str]:
    ...         return ["NextState1", "NextState2"]
    ...     
    ...     def can_transition_to(self, target_state: str) -> bool:
    ...         return target_state in self.get_next_states()
"""

from .interfaces import IState

__all__ = [
    'IState',
]
