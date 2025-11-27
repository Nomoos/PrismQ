# DB-002: Research and Implement IRepository Interface

**Priority**: Medium  
**Type**: Research + Implementation  
**Worker**: Database Specialist  
**Status**: New  
**Created**: 2025-11-27  
**Related**: DB-001 (Base Model Interface)

---

## Background

The current `IModel` interface follows the Active Record pattern where models know how to persist themselves. This works well for simple CRUD operations but has limitations:

1. **Query Operations**: `IModel` intentionally excludes query methods (`find`, `find_all`, `find_by`) per ISP
2. **Separation of Concerns**: Domain models are coupled with persistence logic
3. **Testing**: Mocking persistence is harder with Active Record
4. **Complex Queries**: No standard interface for complex/aggregate queries

## Research Questions

1. **Is IRepository needed for PrismQ?**
   - What query patterns does the workflow require?
   - Are complex queries needed or just simple lookups by ID?
   - Does the versioning strategy affect query needs?

2. **Repository Pattern Benefits**
   - Would it improve testability?
   - Would it enable better separation of concerns?
   - Does the team prefer Repository over Active Record?

3. **Design Considerations**
   - Generic vs specific repositories?
   - Should repositories work with `IModel` or raw entities?
   - How to handle version-based queries?

## Proposed Interface (Draft)

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from datetime import datetime

TEntity = TypeVar('TEntity')
TId = TypeVar('TId')

class IRepository(ABC, Generic[TEntity, TId]):
    """Interface for repository operations (queries and persistence)."""
    
    @abstractmethod
    def find_by_id(self, id: TId) -> Optional[TEntity]:
        """Find entity by unique identifier."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[TEntity]:
        """Find all entities."""
        pass
    
    @abstractmethod
    def exists(self, id: TId) -> bool:
        """Check if entity exists by ID."""
        pass
    
    @abstractmethod
    def save(self, entity: TEntity) -> TEntity:
        """Persist entity (create new version)."""
        pass
    
    # Optional: Version-specific queries
    @abstractmethod
    def find_latest_version(self, id: TId) -> Optional[TEntity]:
        """Find latest version of entity."""
        pass
    
    @abstractmethod
    def find_versions(self, id: TId) -> List[TEntity]:
        """Find all versions of entity."""
        pass
```

## Acceptance Criteria

- [ ] Research completed and documented
- [ ] Decision made: Implement or Defer
- [ ] If implementing:
  - [ ] `IRepository` interface created in `T/Database/repositories/base.py`
  - [ ] Unit tests with 100% coverage
  - [ ] Documentation with examples
  - [ ] Integration with existing `IModel` design
- [ ] Worker10 review completed

## Notes

- This issue was identified during DB-001 review as gap #4
- Consider ISP: May need multiple small interfaces (`IQueryable`, `IVersionedRepository`)
- No delete operations needed (matches `IModel` design)

---

## References

- [DB-001: Base Model Interface](../../../models/base.py)
- [IModel Interface Documentation](../../../__init__.py)
- [Repository Pattern - Martin Fowler](https://martinfowler.com/eaaCatalog/repository.html)
