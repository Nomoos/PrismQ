"""Validator interface for PrismQ state machine.

This module defines the IValidator interface and ValidationResult dataclass
for state transition validation.

Following Interface Segregation Principle (ISP):
- Small, focused interface with single responsibility
- Implementations only need to implement what they use
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ValidationResult:
    """Result of a validation operation.
    
    Attributes:
        is_valid: Whether the validation passed
        error_message: Description of the error (if is_valid is False)
        from_state: The source state (optional, for transition validations)
        to_state: The target state (optional, for transition validations)
    """
    is_valid: bool
    error_message: Optional[str] = None
    from_state: Optional[str] = None
    to_state: Optional[str] = None
    
    def __bool__(self) -> bool:
        """Allow ValidationResult to be used in boolean context."""
        return self.is_valid


class IValidator(ABC):
    """Interface for state validators.
    
    Validators check if state transitions are valid according to
    the workflow rules.
    
    Following Liskov Substitution Principle (LSP):
    - All implementations should be substitutable
    - Behavior should be consistent with the interface contract
    """
    
    @abstractmethod
    def validate(self, from_state: str, to_state: str) -> ValidationResult:
        """Validate a state transition.
        
        Args:
            from_state: The current/source state
            to_state: The target state to transition to
            
        Returns:
            ValidationResult indicating whether the transition is valid
        """
        pass
    
    @abstractmethod
    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a state transition is valid.
        
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
            List of state names that are valid transitions
        """
        pass
