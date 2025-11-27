"""PrismQ.T.State.interfaces - State Machine Interfaces.

This package contains abstract interfaces that define contracts for state
management components.

Main Classes:
    - IState: Interface defining state behavior contract
    - IValidator: Interface for state validators
"""

from T.State.interfaces.state_interface import IState
from T.State.interfaces.validator_interface import IValidator

__all__ = [
    "IState",
    "IValidator",
]
