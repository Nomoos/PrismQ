"""IModel Interface - Defines the contract for database model implementations.

This module defines the IModel interface following the Interface Segregation
Principle. The interface defines a minimal, focused contract for CRUD (Create,
Read, Update, Delete) operations that all database model implementations must
follow.

Interface Segregation Principle:
    IModel is responsible ONLY for defining basic CRUD operations.
    It does NOT handle:
    - Complex queries (handled by repository/query interfaces)
    - Relationships/joins (handled by relationship interfaces)
    - Validation logic (handled by validator interfaces)
    - Transaction management (handled by unit of work pattern)

The interface is intentionally small and focused to allow clients to depend
only on the operations they need, following the ISP principle of "no client
should be forced to depend on methods it does not use."
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any

# Type variable for the model's identifier type
TId = TypeVar('TId')


class IModel(ABC, Generic[TId]):
    """Interface defining the contract for database model implementations.
    
    All database models in PrismQ must implement this interface.
    The interface follows the Interface Segregation Principle by defining
    only essential CRUD operations, keeping the interface small and focused.
    
    Type Parameters:
        TId: The type of the model's unique identifier (e.g., str, int, UUID)
    
    Methods:
        get_id(): Returns the unique identifier of the model
        save(): Persists the model (create or update)
        delete(): Removes the model from persistence
        refresh(): Reloads the model from persistence
    
    Example:
        >>> class ContentModel(IModel[str]):
        ...     def __init__(self, id: str, content: str):
        ...         self._id = id
        ...         self._content = content
        ...     
        ...     def get_id(self) -> str:
        ...         return self._id
        ...     
        ...     def save(self) -> bool:
        ...         # Persist to database
        ...         return True
        ...     
        ...     def delete(self) -> bool:
        ...         # Remove from database
        ...         return True
        ...     
        ...     def refresh(self) -> bool:
        ...         # Reload from database
        ...         return True
    """
    
    @abstractmethod
    def get_id(self) -> Optional[TId]:
        """Return the unique identifier of this model.
        
        Returns:
            Optional[TId]: The unique identifier of the model, or None
                if the model has not been persisted yet.
                
        Note:
            The identifier type is specified by the generic type parameter
            TId when implementing this interface.
        """
        pass
    
    @abstractmethod
    def save(self) -> bool:
        """Persist the model to the database.
        
        This method handles both creation of new records and updates
        to existing records (upsert behavior).
        
        Returns:
            bool: True if the save operation was successful,
                False otherwise.
                
        Note:
            After a successful save, get_id() should return a valid
            identifier if the model was newly created.
        """
        pass
    
    @abstractmethod
    def delete(self) -> bool:
        """Remove the model from the database.
        
        Returns:
            bool: True if the delete operation was successful,
                False otherwise (e.g., if the model doesn't exist).
                
        Note:
            After a successful delete, the model instance may still
            exist in memory but should not be used for further
            database operations.
        """
        pass
    
    @abstractmethod
    def refresh(self) -> bool:
        """Reload the model's data from the database.
        
        This method updates the model's attributes with the current
        values from the database, discarding any unsaved changes.
        
        Returns:
            bool: True if the refresh operation was successful,
                False otherwise (e.g., if the model doesn't exist
                in the database).
                
        Note:
            This operation requires the model to have a valid identifier
            (get_id() should not return None).
        """
        pass
