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
]
