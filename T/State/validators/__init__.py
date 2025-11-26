"""Validators for PrismQ State module.

This package contains concrete validator implementations that follow
the Liskov Substitution Principle - all validators are interchangeable
via the IValidator interface.
"""

from T.State.validators.transition_validator import TransitionValidator

__all__ = [
    "TransitionValidator",
]
