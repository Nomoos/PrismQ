# Issue 502: Add SQLAlchemy ORM Layer for Advanced Database Features

**Type**: Infrastructure Enhancement
**Priority**: Medium
**Status**: New
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Implement an SQLAlchemy ORM layer as an alternative repository implementation, providing advanced querying capabilities, connection pooling, and future support for multiple database backends (PostgreSQL, MySQL).

## Current State

The current implementation uses raw SQLite operations:
- ✅ Simple and lightweight
- ✅ Works well for basic CRUD operations
- ❌ Manual SQL query construction
- ❌ Limited query optimization
- ❌ No connection pooling
- ❌ Difficult complex queries (joins, subqueries)
- ❌ Hard to migrate to PostgreSQL

## Goals

1. **Advanced Query Capabilities**
   - Complex filtering with multiple conditions
   - Joins across tables (when Classification/Scoring tables added)
   - Aggregations and analytics queries
   - Full-text search support

2. **Database Abstraction**
   - Support SQLite (development)
   - Support PostgreSQL (production)
   - Support MySQL (if needed)
   - Seamless migration between databases

3. **Performance Optimization**
   - Connection pooling
   - Query optimization
   - Lazy loading for relationships
   - Bulk operations

4. **Maintain Compatibility**
   - Coexist with raw SQLite implementation
   - Provide SQLAlchemy as optional backend
   - No breaking changes to existing code

## Proposed Architecture

### ORM Models

```python
# Model/infrastructure/orm/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class IdeaInspirationORM(Base):
    """SQLAlchemy ORM model for IdeaInspiration."""
    
    __tablename__ = 'idea_inspiration'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    content = Column(Text)
    keywords = Column(Text)  # JSON
    source_type = Column(String(20))
    metadata = Column(Text)  # JSON
    source_id = Column(String(255), index=True)
    source_url = Column(Text)
    source_created_by = Column(String(255))
    source_created_at = Column(String(50))
    score = Column(Integer)
    category = Column(String(100), index=True)
    subcategory_relevance = Column(Text)  # JSON
    contextual_category_scores = Column(Text)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Future relationships
    # classifications = relationship("Classification", back_populates="idea")
    # scores = relationship("Score", back_populates="idea")
    
    def to_domain_model(self) -> IdeaInspiration:
        """Convert ORM model to domain model."""
        import json
        return IdeaInspiration.from_dict({
            'title': self.title,
            'description': self.description or '',
            'content': self.content or '',
            'keywords': json.loads(self.keywords) if self.keywords else [],
            'source_type': self.source_type,
            'metadata': json.loads(self.metadata) if self.metadata else {},
            'source_id': self.source_id,
            'source_url': self.source_url,
            'source_created_by': self.source_created_by,
            'source_created_at': self.source_created_at,
            'score': self.score,
            'category': self.category,
            'subcategory_relevance': json.loads(self.subcategory_relevance) if self.subcategory_relevance else {},
            'contextual_category_scores': json.loads(self.contextual_category_scores) if self.contextual_category_scores else {}
        })
    
    @classmethod
    def from_domain_model(cls, idea: IdeaInspiration) -> 'IdeaInspirationORM':
        """Create ORM model from domain model."""
        import json
        data = idea.to_dict()
        return cls(
            title=data['title'],
            description=data['description'],
            content=data['content'],
            keywords=json.dumps(data['keywords']),
            source_type=data['source_type'],
            metadata=json.dumps(data['metadata']),
            source_id=data['source_id'],
            source_url=data['source_url'],
            source_created_by=data['source_created_by'],
            source_created_at=data['source_created_at'],
            score=data['score'],
            category=data['category'],
            subcategory_relevance=json.dumps(data['subcategory_relevance']),
            contextual_category_scores=json.dumps(data['contextual_category_scores'])
        )
```

### SQLAlchemy Repository Implementation

```python
# Model/infrastructure/repositories/sqlalchemy_idea_inspiration_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional

class SQLAlchemyIdeaInspirationRepository(IdeaInspirationRepository):
    """SQLAlchemy implementation of IdeaInspirationRepository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add(self, idea: IdeaInspiration) -> int:
        orm_idea = IdeaInspirationORM.from_domain_model(idea)
        self.session.add(orm_idea)
        self.session.flush()  # Get ID without committing
        return orm_idea.id
    
    def add_batch(self, ideas: List[IdeaInspiration]) -> int:
        orm_ideas = [IdeaInspirationORM.from_domain_model(i) for i in ideas]
        self.session.bulk_save_objects(orm_ideas)
        return len(orm_ideas)
    
    def get_by_id(self, id: int) -> Optional[IdeaInspiration]:
        orm_idea = self.session.query(IdeaInspirationORM).filter_by(id=id).first()
        return orm_idea.to_domain_model() if orm_idea else None
    
    def get_by_source_id(self, source_id: str) -> Optional[IdeaInspiration]:
        orm_idea = self.session.query(IdeaInspirationORM).filter_by(source_id=source_id).first()
        return orm_idea.to_domain_model() if orm_idea else None
    
    def find_all(self, **filters) -> List[IdeaInspiration]:
        query = self.session.query(IdeaInspirationORM)
        
        # Apply filters dynamically
        if 'source_type' in filters:
            query = query.filter(IdeaInspirationORM.source_type == filters['source_type'])
        if 'category' in filters:
            query = query.filter(IdeaInspirationORM.category == filters['category'])
        if 'limit' in filters:
            query = query.limit(filters['limit'])
        if 'offset' in filters:
            query = query.offset(filters['offset'])
        
        orm_ideas = query.all()
        return [orm.to_domain_model() for orm in orm_ideas]
    
    def count(self, **filters) -> int:
        query = self.session.query(IdeaInspirationORM)
        
        if 'source_type' in filters:
            query = query.filter(IdeaInspirationORM.source_type == filters['source_type'])
        if 'category' in filters:
            query = query.filter(IdeaInspirationORM.category == filters['category'])
        
        return query.count()
```

### Session Factory

```python
# Model/infrastructure/database/session_factory.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

class SessionFactory:
    """Factory for creating SQLAlchemy sessions."""
    
    def __init__(self, database_url: str, **engine_kwargs):
        """
        Args:
            database_url: SQLAlchemy database URL
                - SQLite: "sqlite:///path/to/db.s3db"
                - PostgreSQL: "postgresql://user:pass@host:5432/dbname"
                - MySQL: "mysql://user:pass@host:3306/dbname"
            engine_kwargs: Additional engine configuration
        """
        self.engine = create_engine(
            database_url,
            **engine_kwargs
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    @contextmanager
    def session(self) -> Session:
        """Get a database session."""
        session = self.SessionLocal()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_all_tables(self):
        """Create all tables defined in Base metadata."""
        Base.metadata.create_all(self.engine)
```

## Usage Examples

### Basic Usage

```python
# Using SQLAlchemy repository
from Model.infrastructure.database.session_factory import SessionFactory
from Model.infrastructure.repositories.sqlalchemy_idea_inspiration_repository import SQLAlchemyIdeaInspirationRepository

# Initialize
factory = SessionFactory("sqlite:///db.s3db")
factory.create_all_tables()

# Use with context manager
with factory.session() as session:
    repo = SQLAlchemyIdeaInspirationRepository(session)
    
    # Add idea
    idea_id = repo.add(idea)
    
    # Query
    ideas = repo.find_all(category='technology', limit=10)
    
    # Transaction committed automatically
```

### Advanced Querying

```python
# Complex query with SQLAlchemy
with factory.session() as session:
    repo = SQLAlchemyIdeaInspirationRepository(session)
    
    # Query builder pattern
    query = session.query(IdeaInspirationORM)\
        .filter(IdeaInspirationORM.category == 'technology')\
        .filter(IdeaInspirationORM.score > 80)\
        .order_by(IdeaInspirationORM.created_at.desc())\
        .limit(20)
    
    orm_ideas = query.all()
    ideas = [orm.to_domain_model() for orm in orm_ideas]
```

### Migration to PostgreSQL

```python
# Simply change the database URL
factory = SessionFactory(
    "postgresql://user:pass@localhost:5432/prismq",
    pool_size=10,
    max_overflow=20
)

# Same code works with PostgreSQL!
with factory.session() as session:
    repo = SQLAlchemyIdeaInspirationRepository(session)
    repo.add(idea)
```

## Implementation Steps

1. **Phase 1: ORM Models** (Week 1)
   - Define SQLAlchemy models
   - Implement domain model conversion
   - Create migration scripts

2. **Phase 2: Repository Implementation** (Week 1-2)
   - Implement SQLAlchemy repository
   - Session management
   - Query builders

3. **Phase 3: Session Factory** (Week 2)
   - Connection pooling
   - Multiple database support
   - Configuration management

4. **Phase 4: Migration Tools** (Week 2-3)
   - Alembic integration for schema migrations
   - Data migration utilities
   - Backup/restore tools

5. **Phase 5: Testing** (Week 3)
   - Unit tests with SQLite
   - Integration tests with PostgreSQL
   - Performance benchmarks

6. **Phase 6: Documentation** (Week 3-4)
   - SQLAlchemy usage guide
   - Migration guide (SQLite → PostgreSQL)
   - Performance tuning tips

## Benefits

1. **Advanced Features**
   - Complex queries with joins and aggregations
   - Full-text search capabilities
   - Relationship management (future)
   - Query optimization

2. **Database Flexibility**
   - Easy migration to PostgreSQL
   - Support for multiple databases
   - Connection pooling for better performance

3. **Developer Experience**
   - Familiar ORM patterns
   - Better query composition
   - Type-safe queries
   - IDE autocomplete support

4. **Production Ready**
   - Connection pooling
   - Transaction management
   - Performance optimization
   - Battle-tested library

## Testing Strategy

```python
def test_sqlalchemy_repository_equivalence():
    """Verify SQLAlchemy repo behaves same as SQLite repo."""
    sqlite_repo = SQLiteIdeaInspirationRepository(":memory:")
    
    factory = SessionFactory("sqlite:///:memory:")
    factory.create_all_tables()
    
    with factory.session() as session:
        sqlalchemy_repo = SQLAlchemyIdeaInspirationRepository(session)
        
        # Same operations, same results
        sqlite_repo.add(idea)
        sqlalchemy_repo.add(idea)
        
        assert sqlite_repo.count() == sqlalchemy_repo.count()

def test_postgresql_compatibility():
    """Test PostgreSQL database backend."""
    factory = SessionFactory("postgresql://localhost/test")
    
    with factory.session() as session:
        repo = SQLAlchemyIdeaInspirationRepository(session)
        repo.add(idea)
        
        retrieved = repo.get_by_source_id(idea.source_id)
        assert retrieved.title == idea.title
```

## Related Issues

- Issue #500: Repository Pattern Implementation (foundational)
- Issue #501: Unit of Work Pattern (transaction management)
- Issue #503: Specification Pattern (query composition)

## Success Criteria

- [ ] SQLAlchemy ORM models defined
- [ ] Repository implementation complete
- [ ] Session factory with connection pooling
- [ ] Works with SQLite and PostgreSQL
- [ ] Migration from raw SQLite works
- [ ] Performance equal or better than raw SQLite
- [ ] Comprehensive documentation
- [ ] All tests passing

## Estimated Effort

4 weeks (1 developer)

## Dependencies

```python
# requirements.txt additions
sqlalchemy>=2.0.0
alembic>=1.12.0  # For migrations
psycopg2-binary>=2.9.0  # For PostgreSQL
```

## Migration Strategy

1. **Optional Adoption**: SQLAlchemy is opt-in, raw SQLite remains default
2. **Gradual Migration**: One module at a time
3. **Performance Testing**: Benchmark before/after
4. **Rollback Plan**: Can revert to raw SQLite if needed
5. **Documentation**: Clear migration guides

## Best Practices References

Based on industry research:
- SQLAlchemy is industry-standard Python ORM
- Repository pattern works well with SQLAlchemy sessions
- Connection pooling critical for production
- Alembic for schema migrations
- Separation of ORM and domain models prevents tight coupling

## Notes

This issue provides an alternative to the raw SQLite implementation, offering more advanced features and future-proofing for PostgreSQL migration. It should be implemented after Repository Pattern (Issue #500) to maintain clean architecture.
