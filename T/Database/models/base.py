"""IModel Interface - Defines the contract for database model implementations.

This module defines the IModel interface following the Interface Segregation
Principle. The interface defines the minimal contract that all database
model implementations must follow for serialization operations.

Interface Segregation:
    IModel provides a small, focused interface with only essential
    serialization methods. Models should depend on abstractions (IModel),
    not concrete database implementations (Dependency Inversion Principle).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IModel(ABC):
    """Interface defining the contract for database model implementations.
    
    All database models in PrismQ must implement this interface.
    The interface follows the Interface Segregation Principle by focusing
    only on essential serialization operations.
    
    Methods:
        to_dict(): Convert model instance to dictionary for database storage
        from_dict(data): Create model instance from dictionary (class method)
    
    Note:
        Concrete implementations should handle database connection
        details, leaving the interface database-agnostic.
    
    Example:
        >>> class TitleModel(IModel):
        ...     # Implementation for Title entity
        ...     pass
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary for database storage.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model.
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IModel":
        """Create model instance from dictionary.
        
        Args:
            data: Dictionary containing model field values.
            
        Returns:
            IModel: New instance of the model.
        """
        pass
