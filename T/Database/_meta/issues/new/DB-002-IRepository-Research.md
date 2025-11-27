# DB-002: Research and Implement IRepository Interface

**Priority**: Medium  
**Type**: Research + Implementation  
**Worker**: Database Specialist  
**Status**: Research Complete ✅  
**Created**: 2025-11-27  
**Updated**: 2025-11-27  
**Related**: DB-001 (Base Model Interface)

---

## Research Summary

### ✅ Decision: Implement IRepository

After analysis, implementing `IRepository` is **recommended** for PrismQ to:
1. Centralize query operations separate from model persistence
2. Support the Insert+Read only architecture
3. Enable version-based queries for tables like Title, Script

---

## Architectural Constraints

### 🔒 Insert + Read Only Architecture

**Critical Design Decision**: All database tables support only **INSERT** and **READ** operations.

| Operation | Supported | Reason |
|-----------|-----------|--------|
| INSERT | ✅ Yes | Create new records/versions |
| SELECT/READ | ✅ Yes | Query existing data |
| UPDATE | ❌ No | Data is immutable; create new version instead |
| DELETE | ❌ No | History preservation; no data removal |

### Tables Following This Pattern
- **Title**: Versioned content, new versions created on changes
- **Script**: Versioned content, new versions created on changes
- *Future tables*: Same pattern should be considered for all new tables

### Why Insert+Read Only?
1. **Version History**: Complete audit trail of all changes
2. **Data Integrity**: No accidental data loss or corruption
3. **Simplicity**: Reduced complexity in conflict resolution
4. **Reproducibility**: Any point in history can be reconstructed

---

## Research Questions - Answered

### 1. Is IRepository needed for PrismQ?

**Answer: Yes**

- **Query Patterns**: Need to find entities by ID, find latest versions, list all versions
- **Complex Queries**: Version-based queries require specialized handling
- **ISP Compliance**: Separating queries from model persistence follows ISP

### 2. Repository Pattern Benefits

| Benefit | Value for PrismQ |
|---------|------------------|
| Testability | High - Can mock repository for unit tests |
| Separation of Concerns | High - Models don't need query logic |
| Scalability | Medium - SQLite is sufficient for now |

### 3. Design Considerations

- **Generic Repository**: Yes, use `IRepository[TEntity, TId]`
- **Works with IModel**: Repository returns entities implementing `IReadable`
- **Version Queries**: Include `find_latest_version()` and `find_versions()`

---

## Proposed Interface (Final)

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

TEntity = TypeVar('TEntity')
TId = TypeVar('TId')

class IRepository(ABC, Generic[TEntity, TId]):
    """Interface for repository operations (Insert + Read only).
    
    Following the Insert+Read only architecture:
    - No update methods (create new version instead)
    - No delete methods (data is immutable)
    
    Type Parameters:
        TEntity: The entity type this repository manages
        TId: The type of the entity's identifier
    """
    
    # === READ Operations ===
    
    @abstractmethod
    def find_by_id(self, id: TId) -> Optional[TEntity]:
        """Find entity by unique identifier.
        
        Returns:
            The entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[TEntity]:
        """Find all entities.
        
        Returns:
            List of all entities (may be empty).
        """
        pass
    
    @abstractmethod
    def exists(self, id: TId) -> bool:
        """Check if entity exists by ID.
        
        Returns:
            True if entity exists, False otherwise.
        """
        pass
    
    # === INSERT Operation ===
    
    @abstractmethod
    def insert(self, entity: TEntity) -> TEntity:
        """Insert new entity (or new version).
        
        Note: This is INSERT only, not upsert. For versioned
        entities, this creates a new version row.
        
        Returns:
            The inserted entity with generated ID/timestamps.
        """
        pass


class IVersionedRepository(IRepository[TEntity, TId]):
    """Extended repository for versioned entities.
    
    Use this interface for tables like Title, Script that
    maintain version history.
    
    Version Strategy:
        Versions are represented as integers (1, 2, 3, ...).
        Each new save creates a new version with incremented number.
    """
    
    @abstractmethod
    def find_latest_version(self, id: TId) -> Optional[TEntity]:
        """Find the most recent version of an entity.
        
        Returns:
            The latest version if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def find_versions(self, id: TId) -> List[TEntity]:
        """Find all versions of an entity.
        
        Returns:
            List of all versions, ordered by version number (ascending).
        """
        pass
    
    @abstractmethod
    def find_version(self, id: TId, version: int) -> Optional[TEntity]:
        """Find a specific version of an entity.
        
        Args:
            id: The entity identifier
            version: The version number (integer, starting from 1)
        
        Returns:
            The specific version if found, None otherwise.
        """
        pass
```

---

## Implementation Plan

### Phase 1: Base Interface
1. Create `T/Database/repositories/base.py` with `IRepository`
2. Create `IVersionedRepository` extending `IRepository`
3. Unit tests for interface contracts

### Phase 2: Concrete Implementations
1. `TitleRepository` implementing `IVersionedRepository`
2. `ScriptRepository` implementing `IVersionedRepository`
3. Integration tests with SQLite

---

## Acceptance Criteria

- [x] Research completed and documented
- [x] Decision made: **Implement**
- [ ] Implementation (Phase 1):
  - [ ] `IRepository` interface created in `T/Database/repositories/base.py`
  - [ ] `IVersionedRepository` interface created
  - [ ] Unit tests with 100% coverage
  - [ ] Documentation with examples
- [ ] Implementation (Phase 2):
  - [ ] Concrete repository implementations
  - [ ] Integration tests
- [ ] Worker10 review completed

---

## Notes

- **Insert+Read Only**: This is a core architectural decision that affects all database design
- **ISP Applied**: Two interfaces (`IRepository`, `IVersionedRepository`) instead of one fat interface
- **No delete/update**: Matches `IModel` design from DB-001
- **Future Tables**: Always consider Insert+Read only pattern when creating new tables

---

## References

- [DB-001: Base Model Interface](../../../models/base.py)
- [IModel Interface Documentation](../../../__init__.py)
- [Repository Pattern - Martin Fowler](https://martinfowler.com/eaaCatalog/repository.html)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html) - Related read/write separation
