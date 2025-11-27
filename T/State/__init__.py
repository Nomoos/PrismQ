"""PrismQ.T.State - State Machine for Content Production Workflow.

This module provides state machine infrastructure for the PrismQ workflow,
including state interfaces, validators, constants, and transition logic.

Following SOLID principles:
- Single Responsibility: Each state has one responsibility
- Open/Closed: States can be extended without modification
- Liskov Substitution: All validators are interchangeable
- Interface Segregation: Small, focused interfaces
- Dependency Inversion: Depend on abstractions, not concretions

Main Classes:
    - IState: Interface defining state behavior contract
    - IValidator: Interface for state validators
    - TransitionValidator: Validates state transitions
    - StateNames: Constants for all workflow states
    - StateCategory: State categorization enum

Example:
    >>> from typing import List
    >>> from T.State import IState, IValidator, TransitionValidator, StateNames
    >>> 
    >>> # Use TransitionValidator to validate transitions
    >>> validator = TransitionValidator()
    >>> result = validator.validate(StateNames.IDEA_CREATION, StateNames.TITLE_FROM_IDEA)
    >>> print(result.is_valid)  # True
"""

from T.State.interfaces.state_interface import IState
from T.State.interfaces.validator_interface import IValidator
from T.State.validators.transition_validator import TransitionValidator
from T.State.constants.state_names import StateNames, StateCategory

__all__ = [
    "IState",
    "IValidator",
    "TransitionValidator",
    "StateNames",
    "StateCategory",
]
