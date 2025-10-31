# Issue 501: Implement Unit of Work Pattern for Transaction Management

**Type**: Architecture Enhancement
**Priority**: Medium
**Status**: New
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement the Unit of Work (UoW) pattern to manage database transactions across multiple repositories, ensuring data consistency and ACID properties in complex operations that span multiple tables or repositories.

## Problem Statement

The current dual-save implementation in Source modules performs separate database operations:
1. Save to source-specific database (signals, events, lyric_snippets)
2. Save to central IdeaInspiration database

**Current Issues:**
- No transaction management across dual-save operations
- If central save fails, source-specific data is already committed
- No rollback mechanism for partial failures
- Each repository manages its own transactions independently
- Data inconsistency possible in failure scenarios

## Goals

1. **Atomic Dual-Save Operations**
   - Both saves succeed or both fail (ACID compliance)
   - Automatic rollback on any failure
   - Consistent state across databases

2. **Transaction Coordination**
   - Single transaction spanning multiple repositories
   - Commit only after all operations succeed
   - Proper error handling and cleanup

3. **Support for Complex Operations**
   - Batch processing with transactional guarantees
   - Multi-step operations (scrape → transform → save)
   - Nested transactions for complex workflows

4. **Integration with Repository Pattern**
   - Work seamlessly with Issue #500 repositories
   - Enable dependency injection for testing
   - Support both SQLite and future PostgreSQL

## Proposed Architecture

### Unit of Work Interface

```python
from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Generic

T = TypeVar('T')

class UnitOfWork(ABC, Generic[T]):
    """Abstract Unit of Work for managing transactions."""
    
    @abstractmethod
    def __enter__(self):
        """Begin transaction."""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit on success, rollback on failure."""
        pass
    
    @abstractmethod
    def commit(self):
        """Explicitly commit transaction."""
        pass
    
    @abstractmethod
    def rollback(self):
        """Explicitly rollback transaction."""
        pass
    
    @property
    @abstractmethod
    def idea_inspirations(self) -> IdeaInspirationRepository:
        """Access to IdeaInspiration repository."""
        pass
```

### SQLite Implementation

```python
class SQLiteUnitOfWork(UnitOfWork):
    """SQLite implementation of Unit of Work."""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self._connection = None
        self._repositories = {}
    
    def __enter__(self):
        self._connection = sqlite3.connect(self.database_path)
        self._connection.isolation_level = None  # Manual transaction control
        self._connection.execute("BEGIN TRANSACTION")
        
        # Initialize repositories with this connection
        self._repositories['idea_inspirations'] = \
            SQLiteIdeaInspirationRepository(self._connection)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        
        self._connection.close()
        return False  # Re-raise exceptions
    
    def commit(self):
        self._connection.execute("COMMIT")
    
    def rollback(self):
        self._connection.execute("ROLLBACK")
    
    @property
    def idea_inspirations(self):
        return self._repositories['idea_inspirations']
```

### Multi-Database Unit of Work

For dual-save operations across different databases:

```python
class MultiDatabaseUnitOfWork:
    """Coordinates transactions across multiple databases."""
    
    def __init__(self, source_db_path: str, central_db_path: str):
        self.source_uow = None  # Source-specific UoW
        self.central_uow = SQLiteUnitOfWork(central_db_path)
    
    def __enter__(self):
        # Begin both transactions
        self.source_uow.__enter__()
        self.central_uow.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            try:
                # Commit both (two-phase commit pattern)
                self.source_uow.commit()
                self.central_uow.commit()
            except Exception as e:
                # Rollback both on any failure
                self.source_uow.rollback()
                self.central_uow.rollback()
                raise
        else:
            # Rollback both on exception
            self.source_uow.rollback()
            self.central_uow.rollback()
        
        # Close connections
        self.source_uow.__exit__(None, None, None)
        self.central_uow.__exit__(None, None, None)
```

## Usage Examples

### Simple Usage

```python
# Single database transaction
def save_ideas_transactionally(ideas: List[IdeaInspiration]):
    with SQLiteUnitOfWork(get_central_database_path()) as uow:
        for idea in ideas:
            uow.idea_inspirations.add(idea)
        
        # Automatic commit on success, rollback on exception
```

### Dual-Save with Transaction

```python
# Dual-save with transactional guarantees
def scrape_with_dual_save():
    with MultiDatabaseUnitOfWork(source_db, central_db) as uow:
        ideas = plugin.scrape()
        
        for idea in ideas:
            # Both succeed or both fail
            uow.source.lyric_snippets.add(idea)
            uow.central.idea_inspirations.add(idea)
        
        # Both committed atomically
```

### Complex Multi-Step Operation

```python
def process_and_save_batch():
    with SQLiteUnitOfWork(db_path) as uow:
        # Step 1: Fetch unprocessed
        unprocessed = uow.idea_inspirations.find_all(processed=False)
        
        # Step 2: Transform
        transformed = [transform(idea) for idea in unprocessed]
        
        # Step 3: Update
        for idea in transformed:
            uow.idea_inspirations.update(idea)
        
        # All steps committed together
```

## Implementation Steps

1. **Phase 1: Define Interface** (Week 1)
   - Create abstract `UnitOfWork` class
   - Define context manager protocol
   - Document transaction semantics

2. **Phase 2: SQLite Implementation** (Week 1-2)
   - Implement `SQLiteUnitOfWork`
   - Integration with repositories from Issue #500
   - Connection and transaction management

3. **Phase 3: Multi-Database Support** (Week 2)
   - Implement `MultiDatabaseUnitOfWork`
   - Two-phase commit coordination
   - Error handling and rollback

4. **Phase 4: Update Source Modules** (Week 2-3)
   - Migrate LyricSnippets to use UoW
   - Update GoogleTrends for transactional dual-save
   - Update CalendarHolidays

5. **Phase 5: Testing** (Week 3)
   - Unit tests for UoW behavior
   - Integration tests for dual-save
   - Failure scenario testing

6. **Phase 6: Documentation** (Week 3)
   - Update DATABASE_INTEGRATION.md
   - Add UoW pattern guide
   - Migration examples

## Benefits

1. **Data Consistency**
   - ACID compliance for dual-save operations
   - No partial saves (all or nothing)
   - Automatic rollback on failures

2. **Simplified Error Handling**
   - Automatic cleanup on exceptions
   - Centralized transaction management
   - Reduced boilerplate code

3. **Better Testing**
   - Mock UoW for unit tests
   - In-memory UoW for fast tests
   - Predictable transaction behavior

4. **Scalability**
   - Easy addition of new repositories
   - Support for complex workflows
   - Foundation for distributed transactions (future)

## Testing Strategy

```python
def test_transaction_rollback_on_failure():
    """Test that UoW rolls back on exception."""
    uow = SQLiteUnitOfWork(":memory:")
    
    try:
        with uow:
            uow.idea_inspirations.add(idea1)
            uow.idea_inspirations.add(idea2)
            raise ValueError("Simulated failure")
    except ValueError:
        pass
    
    # Verify rollback - no ideas saved
    with uow:
        assert uow.idea_inspirations.count() == 0

def test_dual_save_atomicity():
    """Test that dual-save is atomic."""
    multi_uow = MultiDatabaseUnitOfWork(source_db, central_db)
    
    # Simulate failure in central save
    with pytest.raises(Exception):
        with multi_uow:
            multi_uow.source.add(idea)
            multi_uow.central.add(idea)
            raise Exception("Central save failed")
    
    # Verify both rolled back
    assert source_repo.count() == 0
    assert central_repo.count() == 0
```

## Related Issues

- Issue #500: Repository Pattern Implementation (foundational)
- Issue #502: Add SQLAlchemy ORM Layer (advanced transactions)
- Issue #504: Implement Saga Pattern (distributed transactions)

## Success Criteria

- [ ] UnitOfWork interface defined
- [ ] SQLite UoW implementation working
- [ ] Multi-database UoW for dual-save
- [ ] At least one Source module migrated
- [ ] Comprehensive test coverage (>90%)
- [ ] Documentation with examples
- [ ] Performance benchmarks (no degradation)
- [ ] Error scenarios properly handled

## Estimated Effort

3 weeks (1 developer)

## Best Practices References

Based on industry research:
- Unit of Work pattern manages transactions across repositories
- Context manager protocol provides clean resource management
- Two-phase commit for distributed transactions
- Integration with Repository pattern for clean architecture

Sources:
- CosmicPython (UoW pattern in Python)
- Enterprise Application Architecture Patterns (Martin Fowler)
- SQLAlchemy Session patterns

## Migration Strategy

1. **Backward Compatible**: Keep existing dual-save working
2. **Gradual Migration**: Update Source modules one at a time
3. **Optional Adoption**: Sources can opt-in to UoW pattern
4. **Performance Testing**: Ensure no regression
5. **Rollback Plan**: Can revert to direct database access if needed

## Notes

The Unit of Work pattern is particularly valuable for the dual-save architecture, ensuring data consistency across source-specific and central databases. It should be implemented after the Repository Pattern (Issue #500) is in place.
