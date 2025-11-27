"""IModel Interface - Defines the contract for database model implementations.

This module defines the IModel interface using Python's Protocol class,
following the Dependency Inversion Principle (DIP) and Interface
Segregation Principle (ISP).

Dependency Inversion:
    High-level modules (services, repositories) depend on the IModel
    abstraction, not on concrete SQLite implementations.

Interface Segregation:
    IModel defines only essential CRUD operations - small, focused interface.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Optional, Dict, Any, runtime_checkable


@runtime_checkable
class IModel(Protocol):
    """Protocol (interface) defining the contract for database models.
    
    All database models in PrismQ should implement this interface.
    The interface follows SOLID principles:
    - Single Responsibility: Only defines data structure and serialization
    - Interface Segregation: Minimal, focused interface
    - Dependency Inversion: Abstracts away database implementation details
    
    Required Attributes:
        id: Primary key (auto-generated, Optional[int])
    
    Required Methods:
        to_dict(): Convert model to dictionary for storage
        from_dict(): Create model instance from dictionary
    
    Example:
        >>> class Script(IModel):
        ...     def to_dict(self) -> Dict[str, Any]:
        ...         return {"id": self.id, "text": self.text, ...}
        ...     
        ...     @classmethod
        ...     def from_dict(cls, data: Dict[str, Any]) -> "Script":
        ...         return cls(**data)
    """
    
    id: Optional[int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary for database storage.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
                suitable for database storage or JSON serialization.
        """
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IModel":
        """Create a model instance from a dictionary.
        
        Args:
            data: Dictionary containing model data, typically from
                database retrieval or JSON deserialization.
                
        Returns:
            IModel: New instance of the model populated with data.
        """
        ...
