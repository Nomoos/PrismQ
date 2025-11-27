"""Validator interface for PrismQ State validation.

This module defines the IValidator interface that all validators must implement.
Following the Liskov Substitution Principle (LSP), any validator implementing
this interface can be substituted without affecting the correctness of the program.

The interface follows SOLID principles:
- Single Responsibility: Defines only validation contract
- Open/Closed: Extensible through new implementations
- Liskov Substitution: All implementations are interchangeable
- Interface Segregation: Minimal, focused interface
- Dependency Inversion: Programs depend on this abstraction
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation operation.
    
    Attributes:
        is_valid: Whether the validation passed
        error_message: Optional error message if validation failed
        from_state: The source state that was validated (if applicable)
        to_state: The target state that was validated (if applicable)
    """
    is_valid: bool
    error_message: Optional[str] = None
    from_state: Optional[str] = None
    to_state: Optional[str] = None
    
    def __bool__(self) -> bool:
        """Allow ValidationResult to be used in boolean context."""
        return self.is_valid


class IValidator(ABC):
    """Abstract interface for state validators.
    
    All validators implementing this interface can be substituted without
    affecting the correctness of the program (Liskov Substitution Principle).
    
    This interface defines the contract for validating state transitions
    in the PrismQ workflow state machine.
    
    Example:
        >>> class MyValidator(IValidator):
        ...     def validate(self, from_state, to_state):
        ...         # Custom validation logic
        ...         return ValidationResult(is_valid=True)
        ...
        ...     def is_valid_transition(self, from_state, to_state):
        ...         return self.validate(from_state, to_state).is_valid
        ...
        ...     def get_valid_next_states(self, current_state):
        ...         return []
    """
    
    @abstractmethod
    def validate(self, from_state: str, to_state: str) -> ValidationResult:
        """Validate a state transition.
        
        Args:
            from_state: The current/source state
            to_state: The target state to transition to
            
        Returns:
            ValidationResult indicating whether the transition is valid
            and any error message if invalid
        """
        pass
    
    @abstractmethod
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a state transition is valid.
        
        This is a convenience method that returns a simple boolean.
        For detailed results, use validate() instead.
        
        Args:
            from_state: The current/source state
            to_state: The target state to transition to
            
        Returns:
            True if the transition is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_valid_next_states(self, current_state: str) -> List[str]:
        """Get all valid next states from the current state.
        
        Args:
            current_state: The current state
            
        Returns:
            List of state names that are valid transitions from current_state
        """
        pass


__all__ = ["IValidator", "ValidationResult"]
