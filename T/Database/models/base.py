"""Database Model Interfaces - Defines contracts for database model implementations.

This module defines interfaces for database models following the Interface Segregation
Principle. Each interface is minimal and focused, allowing clients to depend only on
the operations they need.

Interface Segregation Principle:
    - IReadable: Read-only operations (get_id, exists, get_created_at)
    - IModel: Full persistence operations (extends IReadable with save, refresh)
    
    These interfaces do NOT handle:
    - Complex queries (handled by repository/query interfaces)
    - Relationships/joins (handled by relationship interfaces)
    - Validation logic (handled by validator interfaces)
    - Transaction management (handled by unit of work pattern)
    - Delete operations (data is immutable; new versions are created instead)

The interfaces are intentionally small and focused to allow clients to depend
only on the operations they need, following the ISP principle of "no client
should be forced to depend on methods it does not use."
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar, Generic, Optional

# Type variable for the model's identifier type
TId = TypeVar('TId')


class IReadable(ABC, Generic[TId]):
    """Interface for read-only model operations.
    
    This interface defines the minimal contract for reading model data.
    Use this interface when you only need to read data without modification.
    
    Type Parameters:
        TId: The type of the model's unique identifier (e.g., str, int, UUID)
    
    Methods:
        get_id(): Returns the unique identifier of the model
        exists(): Checks if the model exists in persistence
        get_created_at(): Returns the creation timestamp
    
    Example:
        >>> class ReadOnlyContent(IReadable[str]):
        ...     def __init__(self, id: str):
        ...         self._id = id
        ...         self._created_at = datetime.now()
        ...     
        ...     def get_id(self) -> str:
        ...         return self._id
        ...     
        ...     def exists(self) -> bool:
        ...         return self._id is not None
        ...     
        ...     def get_created_at(self) -> Optional[datetime]:
        ...         return self._created_at
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
    def exists(self) -> bool:
        """Check if the model exists in the database.
        
        Returns:
            bool: True if the model exists in persistence (has been saved),
                False otherwise.
                
        Note:
            This is a convenience method. A model exists if it has a valid
            identifier (get_id() returns a non-None value).
        """
        pass
    
    @abstractmethod
    def get_created_at(self) -> Optional[datetime]:
        """Return the creation timestamp of this model.
        
        Returns:
            Optional[datetime]: The timestamp when the model was first
                persisted, or None if the model has not been saved yet.
                
        Note:
            This timestamp is immutable and set only once during the
            initial save operation. Due to the versioning strategy,
            there is no updated_at timestamp - new versions create
            new rows instead of modifying existing ones.
        """
        pass


class IModel(IReadable[TId], Generic[TId]):
    """Interface defining the contract for database model implementations.
    
    All database models in PrismQ must implement this interface.
    The interface follows the Interface Segregation Principle by defining
    only essential persistence operations, keeping the interface small and focused.
    
    This interface extends IReadable with write operations. Note that there is
    no delete operation - data is immutable and new versions are created instead
    of modifying or deleting existing records.
    
    Type Parameters:
        TId: The type of the model's unique identifier (e.g., str, int, UUID)
    
    Methods (inherited from IReadable):
        get_id(): Returns the unique identifier of the model
        exists(): Checks if the model exists in persistence
        get_created_at(): Returns the creation timestamp
        
    Methods (defined here):
        save(): Persists the model (creates new record/version)
        refresh(): Reloads the model from persistence
    
    Example:
        >>> class ContentModel(IModel[str]):
        ...     def __init__(self, id: str, content: str):
        ...         self._id = id
        ...         self._content = content
        ...         self._created_at = None
        ...     
        ...     def get_id(self) -> str:
        ...         return self._id
        ...     
        ...     def exists(self) -> bool:
        ...         return self._id is not None
        ...     
        ...     def get_created_at(self) -> Optional[datetime]:
        ...         return self._created_at
        ...     
        ...     def save(self) -> bool:
        ...         # Persist to database (creates new version)
        ...         if self._created_at is None:
        ...             self._created_at = datetime.now()
        ...         return True
        ...     
        ...     def refresh(self) -> bool:
        ...         # Reload from database
        ...         return True
    """
    
    @abstractmethod
    def save(self) -> bool:
        """Persist the model to the database.
        
        This method creates a new record (or new version for versioned tables).
        Due to the immutable data strategy, this does not update existing records
        but creates new versions instead.
        
        Returns:
            bool: True if the save operation was successful,
                False otherwise.
                
        Note:
            After a successful save:
            - get_id() should return a valid identifier
            - get_created_at() should return the creation timestamp
            - exists() should return True
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
            This operation requires the model to exist in the database
            (exists() should return True).
        """
        pass
