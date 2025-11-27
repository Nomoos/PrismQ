"""Interfaces for PrismQ State module.

This package contains abstract interfaces that define contracts for state
management components.
"""

from T.State.interfaces.validator_interface import IValidator

__all__ = [
    "IValidator",
"""PrismQ.T.State.interfaces - State Machine Interfaces.

This module provides interfaces (abstract base classes) for the state machine
implementation.

Main Classes:
    - IState: Interface defining state behavior contract
"""

from .state_interface import IState

__all__ = [
    'IState',
]
