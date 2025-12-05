# Repository Pattern Documentation for PrismQ

**Author**: Worker10 (Database Specialist)  
**Created**: 2025-11-27  
**Status**: Research Complete, Implementation Ready

---

## Table of Contents

1. [Overview](#overview)
2. [What is Repository Pattern?](#what-is-repository-pattern)
3. [PrismQ Architecture](#prismq-architecture)
4. [Interface Hierarchy](#interface-hierarchy)
5. [Concrete Implementations](#concrete-implementations)
6. [Usage Examples](#usage-examples)
7. [Testing Strategy](#testing-strategy)
8. [Best Practices](#best-practices)
9. [FAQ](#faq)

---

## Overview

Repository Pattern in PrismQ provides an abstraction layer between domain models and data access logic, following SOLID principles with special consideration for PrismQ's unique dual-pattern architecture:

| Pattern | Tables | Operations | Use Case |
|---------|--------|------------|----------|
| **INSERT+READ Only** | Title, Script, Review | Insert, Read | Immutable versioned content |
| **Full CRUD** | Story | Create, Read, Update | State machine transitions |

---

## What is Repository Pattern?

### Definition

> "A Repository mediates between the domain and data mapping layers, acting like an in-memory domain object collection." - Martin Fowler

### Key Benefits

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Service  │  │ Handler  │  │Controller│  │  Worker  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │             │             │             │           │
│       └─────────────┴──────┬──────┴─────────────┘           │
│                            │                                 │
│                            ▼                                 │
│              ┌─────────────────────────┐                    │
│              │    REPOSITORY LAYER     │ ◄── Abstraction   │
│              │  ┌─────────────────┐    │                    │
│              │  │  IRepository    │    │                    │
│              │  │  - find_by_id() │    │                    │
│              │  │  - insert()     │    │                    │
│              │  └─────────────────┘    │                    │
│              └───────────┬─────────────┘                    │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                          │
│              ┌─────────────────────────┐                     │
│              │  SQLite / PostgreSQL    │ ◄── Swappable      │
│              │  or Any Database        │                     │
│              └─────────────────────────┘                     │
└──────────────────────────────────────────────────────────────┘
```

### SOLID Principles Applied

| Principle | Application in Repository Pattern |
|-----------|----------------------------------|
| **S**ingle Responsibility | Repository handles only data access, not business logic |
| **O**pen/Closed | New query methods via inheritance without modifying base |
| **L**iskov Substitution | Any IRepository implementation can be swapped |
| **I**nterface Segregation | Separate interfaces: IRepository, IVersionedRepository, IUpdatableRepository |
| **D**ependency Inversion | Domain depends on IRepository abstraction, not SQLite |

---

## PrismQ Architecture

### Dual Pattern Approach

PrismQ uses **two distinct patterns** based on data characteristics:

#### Pattern 1: INSERT + READ Only (Versioned Content)

```
┌────────────────────────────────────────────────────────────┐
│              INSERT + READ ONLY PATTERN                    │
│                                                            │
│   Title v0 ──INSERT──▶ Title v1 ──INSERT──▶ Title v2     │
│      │                    │                    │          │
│      │                    │                    │          │
│      ▼                    ▼                    ▼          │
│   ┌──────┐            ┌──────┐            ┌──────┐       │
│   │ ROW  │            │ ROW  │            │ ROW  │       │
│   │ id=1 │            │ id=2 │            │ id=3 │       │
│   └──────┘            └──────┘            └──────┘       │
│                                                            │
│   ❌ UPDATE (Create new version instead)                   │
│   ❌ DELETE (History preservation)                         │
└────────────────────────────────────────────────────────────┘

Tables: Title, Script, Review, StoryReview
```

#### Pattern 2: Full CRUD (State Machine)

```
┌────────────────────────────────────────────────────────────┐
│                   FULL CRUD PATTERN                        │
│                                                            │
│   Story ─────UPDATE state────▶ Story (same row)           │
│     │                             │                        │
│     │    state: "IDEA"           │    state: "TITLE"      │
│     │                             │                        │
│     ▼                             ▼                        │
│   ┌────────────────────────────────────────┐              │
│   │              SINGLE ROW                 │              │
│   │  id=1, state changes in place          │              │
│   └────────────────────────────────────────┘              │
│                                                            │
│   ✅ CREATE                                                │
│   ✅ READ                                                  │
│   ✅ UPDATE (state field only)                            │
│   ❌ DELETE (Story never deleted)                         │
└────────────────────────────────────────────────────────────┘

Tables: Story (state field updates)
```

### Why Two Patterns?

| Aspect | INSERT+READ | Full CRUD |
|--------|-------------|-----------|
| **Purpose** | Content versioning | State tracking |
| **Audit Trail** | Complete (all versions preserved) | Partial (only current state) |
| **Data Volume** | Grows with versions | Constant per entity |
| **Queries** | Version-based | State-based |
| **Use Case** | Title, Script evolution | Workflow progression |

---

## Interface Hierarchy

### Class Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    INTERFACE HIERARCHY                        │
│                                                               │
│   ┌─────────────────────────────────────────┐                │
│   │           IRepository[TEntity, TId]      │ ◄── Base      │
│   │  ─────────────────────────────────────   │                │
│   │  + find_by_id(id: TId) → Optional[T]     │                │
│   │  + find_all() → List[T]                  │                │
│   │  + exists(id: TId) → bool                │                │
│   │  + insert(entity: T) → T                 │                │
│   └──────────────────┬──────────────────────┘                │
│                      │                                        │
│          ┌───────────┴───────────┐                           │
│          │                       │                            │
│          ▼                       ▼                            │
│   ┌──────────────────┐   ┌──────────────────┐                │
│   │IVersionedRepository│   │IUpdatableRepository│             │
│   │──────────────────│   │──────────────────│                │
│   │+find_latest_ver()│   │+update(entity)→T │                │
│   │+find_versions()  │   │                  │                │
│   │+find_version()   │   │                  │                │
│   │+find_by_story_id│   │                  │                │
│   └──────────────────┘   └──────────────────┘                │
│          │                       │                            │
│          ▼                       ▼                            │
│   ┌──────────────────┐   ┌──────────────────┐                │
│   │ TitleRepository  │   │  StoryRepository │                │
│   │ ScriptRepository │   │                  │                │
│   └──────────────────┘   └──────────────────┘                │
└──────────────────────────────────────────────────────────────┘
```

### Interface Definitions

#### IRepository (Base)

```python
class IRepository(ABC, Generic[TEntity, TId]):
    """Base repository interface - Insert + Read operations."""
    
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
        """Check if entity exists."""
        pass
    
    @abstractmethod
    def insert(self, entity: TEntity) -> TEntity:
        """Insert new entity."""
        pass
```

#### IVersionedRepository (For Title, Script)

```python
class IVersionedRepository(IRepository[TEntity, TId]):
    """Extended interface for versioned entities."""
    
    @abstractmethod
    def find_latest_version(self, id: TId) -> Optional[TEntity]:
        """Find most recent version."""
        pass
    
    @abstractmethod
    def find_versions(self, id: TId) -> List[TEntity]:
        """Find all versions ordered by version number."""
        pass
    
    @abstractmethod
    def find_version(self, id: TId, version: int) -> Optional[TEntity]:
        """Find specific version."""
        pass
    
    @abstractmethod
    def find_by_story_id(self, story_id: int) -> List[TEntity]:
        """Find all versions for a story."""
        pass
```

#### IUpdatableRepository (For Story)

```python
class IUpdatableRepository(IRepository[TEntity, TId]):
    """Extended interface for updatable entities."""
    
    @abstractmethod
    def update(self, entity: TEntity) -> TEntity:
        """Update existing entity."""
        pass
```

---

## Concrete Implementations

### TitleRepository (SQLite)

```python
class TitleRepository(IVersionedRepository[Title, int]):
    """SQLite implementation for Title entities."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self._conn = db_connection
    
    def find_by_id(self, id: int) -> Optional[Title]:
        cursor = self._conn.execute(
            "SELECT * FROM Title WHERE id = ?", (id,)
        )
        row = cursor.fetchone()
        return Title.from_dict(dict(row)) if row else None
    
    def find_latest_version(self, story_id: int) -> Optional[Title]:
        cursor = self._conn.execute(
            """SELECT * FROM Title 
               WHERE story_id = ? 
               ORDER BY version DESC 
               LIMIT 1""",
            (story_id,)
        )
        row = cursor.fetchone()
        return Title.from_dict(dict(row)) if row else None
    
    def insert(self, entity: Title) -> Title:
        cursor = self._conn.execute(
            """INSERT INTO Title (story_id, version, text, review_id, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (entity.story_id, entity.version, entity.text, 
             entity.review_id, entity.created_at.isoformat())
        )
        self._conn.commit()
        entity.id = cursor.lastrowid
        return entity
```

### StoryRepository (SQLite)

```python
class StoryRepository(IUpdatableRepository[Story, int]):
    """SQLite implementation for Story entities with UPDATE support."""
    
    def update(self, entity: Story) -> Story:
        self._conn.execute(
            """UPDATE Story SET state = ?, updated_at = ? WHERE id = ?""",
            (entity.state, datetime.now().isoformat(), entity.id)
        )
        self._conn.commit()
        return entity
```

---

## Usage Examples

### Basic CRUD Operations

```python
from T.Database.repositories import TitleRepository
from T.Database.models import Title

# Initialize repository
repo = TitleRepository(db_connection)

# CREATE - Insert new title (version 0)
title = Title(story_id=1, version=0, text="Original Title")
saved_title = repo.insert(title)
print(f"Saved with ID: {saved_title.id}")

# READ - Find by ID
found = repo.find_by_id(saved_title.id)

# READ - Find latest version
latest = repo.find_latest_version(story_id=1)

# READ - Find all versions
all_versions = repo.find_versions(story_id=1)

# "UPDATE" via new version (INSERT+READ only pattern)
new_version = latest.create_next_version("Improved Title")
repo.insert(new_version)
```

### Story State Updates

```python
from T.Database.repositories import StoryRepository
from T.Database.models import Story

repo = StoryRepository(db_connection)

# CREATE
story = Story(idea_id=1, state="IDEA")
saved = repo.insert(story)

# UPDATE state (allowed for Story)
saved.state = "TITLE"
repo.update(saved)
```

### Testing with Mock Repository

```python
from unittest.mock import Mock

def test_workflow_service():
    # Create mock repository
    mock_repo = Mock(spec=IVersionedRepository)
    mock_repo.find_latest_version.return_value = Title(
        id=1, story_id=1, version=0, text="Test"
    )
    
    # Test service with mock
    service = WorkflowService(title_repo=mock_repo)
    result = service.process_title(story_id=1)
    
    # Verify interactions
    mock_repo.find_latest_version.assert_called_once_with(1)
```

---

## Testing Strategy

### Unit Tests (Mock DB)

```python
class TestTitleRepository:
    """Unit tests with mocked database connection."""
    
    def test_find_by_id_returns_title(self):
        # Arrange
        mock_conn = Mock()
        mock_conn.execute.return_value.fetchone.return_value = {
            "id": 1, "story_id": 1, "version": 0, 
            "text": "Test", "created_at": "2025-01-01T00:00:00"
        }
        repo = TitleRepository(mock_conn)
        
        # Act
        result = repo.find_by_id(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
```

### Integration Tests (Real SQLite)

```python
class TestTitleRepositoryIntegration:
    """Integration tests with real SQLite database."""
    
    @pytest.fixture
    def db_connection(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        # Create schema
        conn.executescript(TITLE_SCHEMA)
        yield conn
        conn.close()
    
    def test_insert_and_find(self, db_connection):
        repo = TitleRepository(db_connection)
        
        title = Title(story_id=1, version=0, text="Test")
        saved = repo.insert(title)
        
        found = repo.find_by_id(saved.id)
        
        assert found is not None
        assert found.text == "Test"
```

---

## Best Practices

### DO ✅

1. **Use interfaces for dependencies**
   ```python
   class WorkflowService:
       def __init__(self, repo: IVersionedRepository[Title, int]):
           self._repo = repo  # Depend on abstraction
   ```

2. **Keep repositories focused**
   ```python
   # One repository per aggregate root
   TitleRepository  # For Title operations
   StoryRepository  # For Story operations
   ```

3. **Return domain objects**
   ```python
   def find_by_id(self, id: int) -> Optional[Title]:
       # Return Title, not dictionary or row
   ```

4. **Use factory methods for complex creation**
   ```python
   title = Title.create_new(story_id=1, text="Title")
   repo.insert(title)
   ```

### DON'T ❌

1. **Don't mix patterns**
   ```python
   # WRONG: Update on versioned entity
   title = repo.find_by_id(1)
   title.text = "New text"
   repo.update(title)  # ❌ Versioned entities don't update
   
   # CORRECT: Create new version
   new_version = title.create_next_version("New text")
   repo.insert(new_version)  # ✅
   ```

2. **Don't expose database details**
   ```python
   # WRONG: Exposing SQL in service layer
   titles = repo.execute_sql("SELECT * FROM Title WHERE...")
   
   # CORRECT: Use repository methods
   titles = repo.find_by_story_id(story_id)
   ```

3. **Don't put business logic in repository**
   ```python
   # WRONG: Business logic in repository
   def find_titles_needing_review(self):
       return [t for t in self.find_all() if t.should_review()]
   
   # CORRECT: Service handles business logic
   class ReviewService:
       def find_titles_needing_review(self):
           return [t for t in self._repo.find_all() if t.should_review()]
   ```

---

## FAQ

### Q: Why not use an ORM like SQLAlchemy?

**A:** PrismQ uses raw SQLite for simplicity and performance in single-user workflow. ORM overhead is unnecessary for INSERT+READ pattern.

### Q: Should repositories handle transactions?

**A:** Basic repositories use auto-commit. For complex operations spanning multiple entities, use Unit of Work pattern (future implementation).

### Q: How do I test without a database?

**A:** Use mock repositories:
```python
mock_repo = Mock(spec=IVersionedRepository)
mock_repo.find_by_id.return_value = Title(...)
```

### Q: What about connection management?

**A:** Pass connection to repository constructor. Consider connection pooling for concurrent access (not needed for current single-user scenario).

---

## References

- [Repository Pattern - Martin Fowler](https://martinfowler.com/eaaCatalog/repository.html)
- [Domain-Driven Design - Eric Evans](https://domainlanguage.com/ddd/)
- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
- [SQLite Best Practices](https://sqlite.org/bestpractice.html)

---

**Next Steps:**
1. ✅ Documentation complete
2. 🔄 Implement `IUpdatableRepository` interface
3. 🔄 Create concrete `TitleRepository` implementation
4. 🔄 Create concrete `StoryRepository` implementation
5. 🔄 Integration tests with SQLite
