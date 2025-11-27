"""Database Repository Interfaces - Defines contracts for data access operations.

This module defines repository interfaces following the Interface Segregation Principle.
Repositories handle query and insert operations, separate from model persistence logic.

Architecture: INSERT + READ Only
    All repositories in PrismQ follow an Insert+Read only pattern:
    - INSERT: Create new records/versions (supported via insert())
    - READ: Query existing data (supported via find_* methods)
    - UPDATE: Not supported (create new version instead)
    - DELETE: Not supported (data is immutable for history preservation)

Interface Segregation Principle:
    - IRepository: Base interface for Insert + Read operations
    - IVersionedRepository: Extended interface for versioned entities (Title, Script)
    
    These interfaces do NOT handle:
    - Model persistence logic (handled by IModel)
    - Update operations (data is immutable)
    - Delete operations (history preservation)
    - Transaction management (handled by unit of work pattern)

The interfaces are intentionally small and focused to allow clients to depend
only on the operations they need.

Example:
    >>> from T.Database.repositories.base import IRepository, IVersionedRepository
    >>> 
    >>> class TitleRepository(IVersionedRepository[Title, str]):
    ...     def find_by_id(self, id: str) -> Optional[Title]:
    ...         # Query database
    ...         pass
    ...     
    ...     def find_latest_version(self, id: str) -> Optional[Title]:
    ...         # Query for latest version
    ...         pass
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

# Type variables for entity and identifier types
TEntity = TypeVar('TEntity')
TId = TypeVar('TId')


class IRepository(ABC, Generic[TEntity, TId]):
    """Interface for repository operations (Insert + Read only).
    
    This interface defines the contract for basic data access operations.
    Following the Insert+Read only architecture:
    - No update methods (create new version instead)
    - No delete methods (data is immutable)
    
    Type Parameters:
        TEntity: The entity type this repository manages
        TId: The type of the entity's identifier (e.g., str, int, UUID)
    
    Methods:
        find_by_id(): Find entity by unique identifier
        find_all(): Find all entities
        exists(): Check if entity exists by ID
        insert(): Insert new entity
    
    Example:
        >>> class ContentRepository(IRepository[Content, str]):
        ...     def find_by_id(self, id: str) -> Optional[Content]:
        ...         # Query database by ID
        ...         return self._db.query(Content).filter_by(id=id).first()
        ...     
        ...     def find_all(self) -> List[Content]:
        ...         return self._db.query(Content).all()
        ...     
        ...     def exists(self, id: str) -> bool:
        ...         return self.find_by_id(id) is not None
        ...     
        ...     def insert(self, entity: Content) -> Content:
        ...         self._db.add(entity)
        ...         self._db.commit()
        ...         return entity
    """
    
    # === READ Operations ===
    
    @abstractmethod
    def find_by_id(self, id: TId) -> Optional[TEntity]:
        """Find entity by unique identifier.
        
        Args:
            id: The unique identifier of the entity to find.
            
        Returns:
            Optional[TEntity]: The entity if found, None otherwise.
            
        Note:
            For versioned entities, this returns the record with the
            exact ID (which may include version information depending
            on the implementation).
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[TEntity]:
        """Find all entities.
        
        Returns:
            List[TEntity]: List of all entities. Returns empty list
                if no entities exist.
                
        Note:
            For large datasets, consider pagination or streaming
            in concrete implementations.
        """
        pass
    
    @abstractmethod
    def exists(self, id: TId) -> bool:
        """Check if entity exists by ID.
        
        Args:
            id: The unique identifier to check.
            
        Returns:
            bool: True if entity exists, False otherwise.
            
        Note:
            This is a convenience method that may be more efficient
            than find_by_id() when you only need to check existence.
        """
        pass
    
    # === INSERT Operation ===
    
    @abstractmethod
    def insert(self, entity: TEntity) -> TEntity:
        """Insert new entity (or new version).
        
        This method performs INSERT only, not upsert. For versioned
        entities, this creates a new version row.
        
        Args:
            entity: The entity to insert.
            
        Returns:
            TEntity: The inserted entity with generated ID and timestamps.
            
        Note:
            After insertion:
            - Entity should have a valid ID
            - Entity should have created_at timestamp set
            - For versioned entities, version number should be assigned
        """
        pass


class IVersionedRepository(IRepository[TEntity, TId]):
    """Extended repository interface for versioned entities.
    
    Use this interface for tables like Title, Script that maintain
    version history. Each entity can have multiple versions, and this
    interface provides methods to query specific versions.
    
    Version Strategy:
        Versions are represented as integers (1, 2, 3, ...).
        Each insert creates a new version with an incremented number.
        The original entity ID remains the same across versions.
    
    Type Parameters:
        TEntity: The versioned entity type this repository manages
        TId: The type of the entity's identifier
    
    Methods (inherited from IRepository):
        find_by_id(): Find entity by unique identifier
        find_all(): Find all entities
        exists(): Check if entity exists by ID
        insert(): Insert new entity/version
        
    Methods (defined here):
        find_latest_version(): Find the most recent version
        find_versions(): Find all versions of an entity
        find_version(): Find a specific version
    
    Example:
        >>> class TitleRepository(IVersionedRepository[Title, str]):
        ...     def find_latest_version(self, id: str) -> Optional[Title]:
        ...         return self._db.query(Title) \\
        ...             .filter_by(entity_id=id) \\
        ...             .order_by(Title.version.desc()) \\
        ...             .first()
        ...     
        ...     def find_versions(self, id: str) -> List[Title]:
        ...         return self._db.query(Title) \\
        ...             .filter_by(entity_id=id) \\
        ...             .order_by(Title.version.asc()) \\
        ...             .all()
        ...     
        ...     def find_version(self, id: str, version: int) -> Optional[Title]:
        ...         return self._db.query(Title) \\
        ...             .filter_by(entity_id=id, version=version) \\
        ...             .first()
    """
    
    @abstractmethod
    def find_latest_version(self, id: TId) -> Optional[TEntity]:
        """Find the most recent version of an entity.
        
        Args:
            id: The entity identifier (not including version).
            
        Returns:
            Optional[TEntity]: The latest version if found, None otherwise.
            
        Note:
            The entity ID should be the base identifier that remains
            constant across versions.
        """
        pass
    
    @abstractmethod
    def find_versions(self, id: TId) -> List[TEntity]:
        """Find all versions of an entity.
        
        Args:
            id: The entity identifier (not including version).
            
        Returns:
            List[TEntity]: List of all versions, ordered by version
                number in ascending order (oldest first).
                Returns empty list if entity doesn't exist.
        """
        pass
    
    @abstractmethod
    def find_version(self, id: TId, version: int) -> Optional[TEntity]:
        """Find a specific version of an entity.
        
        Args:
            id: The entity identifier (not including version).
            version: The version number (integer, starting from 1).
            
        Returns:
            Optional[TEntity]: The specific version if found, None otherwise.
            
        Note:
            Version numbers start from 1 and increment with each
            new version. Version 0 is not valid.
        """
        pass
