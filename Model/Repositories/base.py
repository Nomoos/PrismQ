"""Database Repository Interfaces - Defines contracts for data access operations.

This module defines repository interfaces following the Interface Segregation Principle.
Repositories handle query and insert operations, separate from model persistence logic.

Architecture:
    PrismQ uses two distinct patterns based on data characteristics:
    
    1. INSERT + READ Only (Title, Script, Review, StoryReview):
       - INSERT: Create new records/versions
       - READ: Query existing data
       - UPDATE: Not supported (create new version instead)
       - DELETE: Not supported (data is immutable for history preservation)
    
    2. CRUD with UPDATE (Story):
       - CREATE: Create new story
       - READ: Query story data
       - UPDATE: Update state field (workflow progression)
       - DELETE: Not supported (stories never deleted)

Interface Segregation Principle:
    - IRepository: Base interface for Insert + Read operations
    - IVersionedRepository: Extended interface for versioned entities (Title, Script)
    - IUpdatableRepository: Extended interface for updatable entities (Story)
    
    These interfaces do NOT handle:
    - Model persistence logic (handled by IModel)
    - Transaction management (handled by unit of work pattern)

The interfaces are intentionally small and focused to allow clients to depend
only on the operations they need.

Example:
    >>> from Model.Database.repositories.base import IRepository, IVersionedRepository
    >>> 
    >>> class TitleRepository(IVersionedRepository[Title, int]):
    ...     def find_by_id(self, id: int) -> Optional[Title]:
    ...         # Query database
    ...         pass
    ...     
    ...     def find_latest_version(self, story_id: int) -> Optional[Title]:
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
        Versions are represented as integers starting from 0 (0, 1, 2, ...).
        Version 0 is the initial version, and each subsequent insert creates
        a new version with an incremented number.
        The story_id remains the same across versions of the same content.
    
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
        >>> class TitleRepository(IVersionedRepository[Title, int]):
        ...     def find_latest_version(self, story_id: int) -> Optional[Title]:
        ...         return self._db.query(Title) \\
        ...             .filter_by(story_id=story_id) \\
        ...             .order_by(Title.version.desc()) \\
        ...             .first()
        ...     
        ...     def find_versions(self, story_id: int) -> List[Title]:
        ...         return self._db.query(Title) \\
        ...             .filter_by(story_id=story_id) \\
        ...             .order_by(Title.version.asc()) \\
        ...             .all()
        ...     
        ...     def find_version(self, story_id: int, version: int) -> Optional[Title]:
        ...         return self._db.query(Title) \\
        ...             .filter_by(story_id=story_id, version=version) \\
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
            version: The version number (integer, starting from 0).
            
        Returns:
            Optional[TEntity]: The specific version if found, None otherwise.
            
        Note:
            Version numbers start from 0 (initial version) and increment
            with each new version.
        """
        pass
    
    @abstractmethod
    def find_by_story_id(self, story_id: int) -> List[TEntity]:
        """Find all versions of content for a specific story.
        
        Args:
            story_id: The story identifier (integer, references Story table).
            
        Returns:
            List[TEntity]: List of all versions for the story, ordered by
                version number in ascending order.
                Returns empty list if no content exists for the story.
                
        Note:
            This method uses int for story_id as it references the Story
            table's primary key. The generic TId parameter refers to the
            entity's own identifier, not the story reference.
        """
        pass


class IUpdatableRepository(IRepository[TEntity, TId]):
    """Extended repository interface for updatable entities.
    
    Use this interface for tables like Story that require UPDATE operations
    for state changes. This extends the base IRepository with update capability.
    
    Unlike versioned entities (Title, Script) which create new rows on changes,
    updatable entities modify existing rows in place.
    
    Type Parameters:
        TEntity: The updatable entity type this repository manages
        TId: The type of the entity's identifier
    
    Methods (inherited from IRepository):
        find_by_id(): Find entity by unique identifier
        find_all(): Find all entities
        exists(): Check if entity exists by ID
        insert(): Insert new entity
        
    Methods (defined here):
        update(): Update existing entity in place
    
    Example:
        >>> class StoryRepository(IUpdatableRepository[Story, int]):
        ...     def update(self, entity: Story) -> Story:
        ...         self._conn.execute(
        ...             "UPDATE Story SET state = ? WHERE id = ?",
        ...             (entity.state, entity.id)
        ...         )
        ...         self._conn.commit()
        ...         return entity
    
    Note:
        This interface does NOT support delete operations.
        Stories and other updatable entities are never deleted.
    """
    
    @abstractmethod
    def update(self, entity: TEntity) -> TEntity:
        """Update existing entity in place.
        
        This method updates an existing entity's fields in the database.
        Unlike versioned entities, this modifies the same row rather than
        creating a new version.
        
        Args:
            entity: The entity to update. Must have a valid ID.
            
        Returns:
            TEntity: The updated entity (same instance with changes persisted).
            
        Raises:
            ValueError: If entity has no ID (not yet persisted).
            
        Note:
            After update:
            - Entity should have updated_at timestamp set (if applicable)
            - Original created_at timestamp should be preserved
            
        Example:
            >>> story = repo.find_by_id(1)
            >>> story.state = "TITLE"
            >>> updated = repo.update(story)
        """
        pass
