"""IState Interface - Defines the contract for state implementations.

This module defines the IState interface following the Single Responsibility
Principle. The interface defines the minimal contract that all state
implementations must follow.

Single Responsibility:
    IState is responsible ONLY for defining the state's identity and
    transition capabilities. It does NOT handle:
    - State execution logic (handled by state implementations)
    - State persistence (handled by repository layer)
    - State machine orchestration (handled by state machine)
"""

from abc import ABC, abstractmethod
from typing import List


class IState(ABC):
    """Interface defining the contract for state implementations.
    
    All states in the PrismQ workflow must implement this interface.
    The interface follows the Single Responsibility Principle by focusing
    only on state identity and transition validation.
    
    Methods:
        get_name(): Returns the unique name of the state
        get_next_states(): Returns list of valid next state names
        can_transition_to(): Validates if transition to target state is allowed
    
    Example:
        >>> class IdeaCreationState(IState):
        ...     def get_name(self) -> str:
        ...         return "IdeaCreation"
        ...     
        ...     def get_next_states(self) -> List[str]:
        ...         return ["TitleFromIdea"]
        ...     
        ...     def can_transition_to(self, target_state: str) -> bool:
        ...         return target_state in self.get_next_states()
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the unique name of this state.
        
        Returns:
            str: The unique identifier for this state.
            
        Note:
            State names should match the naming convention used in the
            workflow documentation (e.g., "IdeaCreation", "TitleFromIdea").
        """
        pass
    
    @abstractmethod
    def get_next_states(self) -> List[str]:
        """Return the list of valid next state names.
        
        Returns:
            List[str]: List of state names that can be transitioned to
                from this state. Returns an empty list for terminal states.
                
        Note:
            The returned list should contain only valid state names
            as defined in the workflow documentation.
        """
        pass
    
    @abstractmethod
    def can_transition_to(self, target_state: str) -> bool:
        """Check if transition to the target state is allowed.
        
        Args:
            target_state: The name of the state to transition to.
            
        Returns:
            bool: True if transition to target_state is allowed,
                False otherwise.
                
        Note:
            This method should validate that the target_state is in
            the list returned by get_next_states().
        """
        pass
