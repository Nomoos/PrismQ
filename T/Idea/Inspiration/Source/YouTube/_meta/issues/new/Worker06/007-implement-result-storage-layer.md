# Issue #007: Implement Result Storage Layer

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 06 - Database Specialist  
**Language**: Python 3.10+ (SQLite, SQL)  
**Status**: New  
**Priority**: High  
**Duration**: 2 days  
**Dependencies**: #004 (Database Schema)

---

## Worker Details: Worker06 - Database Specialist

**Role**: Result Storage & Data Persistence  
**Expertise Required**:
- SQLite database design and optimization
- Repository pattern implementation
- Data deduplication algorithms
- SQL query optimization and indexing
- Transaction management and ACID compliance
- Python sqlite3 module

**Collaboration**:
- **Worker02** (Python): Coordinate on storage interfaces
- **Worker06** (self): Build on #004 schema
- **Worker01** (PM): Daily standup, performance validation

**See**: `_meta/issues/new/Worker06/README.md` for complete role description

---

## Objective

Implement a robust result storage layer using the Repository pattern to store YouTube scraping results in SQLite, with built-in deduplication, transaction management, and optimized query interfaces following SOLID principles.

---

## Problem Statement

Currently, YouTube scraping results are stored in various ways:
- Direct database operations scattered throughout plugins
- Inconsistent data storage patterns
- Limited deduplication logic
- No centralized result management
- Lack of transaction consistency

We need a result storage layer that:
1. Provides a clean interface for storing scraping results
2. Handles deduplication automatically (by source + source_id)
3. Manages transactions properly (ACID compliance)
4. Optimizes for Windows SQLite performance
5. Follows Repository pattern for abstraction
6. Supports batch operations for efficiency

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅

**ResultStorage Responsibilities**:
- Store scraping results in database
- Handle deduplication logic
- Manage database transactions
- Provide query interfaces

**NOT Responsible For**:
- Scraping logic (Plugins)
- Data transformation (IdeaProcessor)
- Metrics calculation (UniversalMetrics)
- Database schema creation (QueueDatabase from #004)

**DeduplicationStrategy Responsibilities**:
- Determine if record is duplicate
- Define uniqueness constraints
- Generate composite keys

**NOT Responsible For**:
- Data storage (ResultStorage)
- Database operations (SQLite connection)

### Open/Closed Principle (OCP) ✅

**Open for Extension**:
- New storage strategies can be added
- New deduplication rules can be implemented
- New query methods can be added

**Closed for Modification**:
- Core storage logic remains stable
- Repository interface is fixed
- Transaction management unchanged

### Liskov Substitution Principle (LSP) ✅

**Substitutability**:
- Different storage implementations can be swapped
- DeduplicationStrategy implementations interchangeable
- No unexpected behavior changes

### Interface Segregation Principle (ISP) ✅

**Minimal Interface**:
```python
class ResultStorageProtocol(Protocol):
    def save(self, result: Dict[str, Any]) -> int: ...
    def save_batch(self, results: List[Dict[str, Any]]) -> int: ...
    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]: ...
    def exists(self, source: str, source_id: str) -> bool: ...
```

Only essential methods for result storage.

### Dependency Inversion Principle (DIP) ✅

**Depend on Abstractions**:
- Workers depend on ResultStorage interface, not concrete implementation
- Database connection injected via constructor
- Deduplication strategy injected (optional)

---

## Proposed Solution

### Architecture Overview

```
Result Storage System
├── ResultStorage                # Repository pattern
│   ├── save()                  # Save single result
│   ├── save_batch()            # Batch save (optimized)
│   ├── get_by_id()             # Retrieve by ID
│   ├── exists()                # Check if exists
│   └── query()                 # Query results
│
├── DeduplicationStrategy        # Deduplication logic
│   ├── is_duplicate()          # Check if duplicate
│   ├── get_key()               # Get uniqueness key
│   └── handle_duplicate()      # Duplicate handling
│
└── ResultDatabase               # Database wrapper
    ├── create_tables()         # Schema creation
    ├── get_connection()        # Connection management
    └── optimize_for_windows()  # Windows-specific tuning
```

---

## Implementation Details

### File Structure

```
src/
├── storage/
│   ├── __init__.py             # NEW: Storage exports
│   ├── result_storage.py       # NEW: Repository implementation
│   ├── deduplication.py        # NEW: Deduplication strategies
│   ├── result_database.py      # NEW: Database wrapper
│   └── schema.sql              # NEW: Results schema
│
├── core/
│   └── database.py             # EXISTING: Keep for backward compat
```

### 1. Results Database Schema

**File**: `src/storage/schema.sql`

```sql
-- Results storage for scraped YouTube content
-- Optimized for Windows SQLite with WAL mode

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;  -- 64MB cache
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456;  -- 256MB memory-mapped I/O

-- Main results table
CREATE TABLE IF NOT EXISTS youtube_results (
    -- Identity
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Source identification
    source TEXT NOT NULL,  -- 'youtube_channel', 'youtube_trending', etc.
    source_id TEXT NOT NULL,  -- YouTube video ID
    
    -- Content metadata
    title TEXT NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    thumbnail_url TEXT,
    
    -- Channel information
    channel_id TEXT,
    channel_name TEXT,
    channel_url TEXT,
    
    -- Video metadata
    duration_seconds INTEGER,
    published_at TEXT,  -- ISO 8601 timestamp
    tags TEXT,  -- JSON array
    category TEXT,
    
    -- Statistics (raw)
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    
    -- Engagement metrics (calculated)
    engagement_rate REAL,
    like_ratio REAL,
    views_per_day REAL,
    views_per_hour REAL,
    
    -- Universal metrics (normalized 0-1)
    universal_engagement REAL,
    universal_virality REAL,
    universal_quality REAL,
    universal_recency REAL,
    universal_score REAL,
    
    -- Additional data (JSON)
    subtitles TEXT,  -- JSON object
    extra_metadata TEXT,  -- JSON object
    
    -- Timestamps
    scraped_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(source, source_id)  -- Deduplication constraint
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_youtube_results_source 
    ON youtube_results(source);

CREATE INDEX IF NOT EXISTS idx_youtube_results_source_id 
    ON youtube_results(source_id);

CREATE INDEX IF NOT EXISTS idx_youtube_results_channel 
    ON youtube_results(channel_id);

CREATE INDEX IF NOT EXISTS idx_youtube_results_published 
    ON youtube_results(published_at DESC);

CREATE INDEX IF NOT EXISTS idx_youtube_results_score 
    ON youtube_results(universal_score DESC);

CREATE INDEX IF NOT EXISTS idx_youtube_results_scraped 
    ON youtube_results(scraped_at DESC);

-- Composite index for deduplication check
CREATE UNIQUE INDEX IF NOT EXISTS idx_youtube_results_unique 
    ON youtube_results(source, source_id);

-- Full-text search (optional, for title/description search)
CREATE VIRTUAL TABLE IF NOT EXISTS youtube_results_fts 
    USING fts5(title, description, tags, content='youtube_results', content_rowid='id');

-- Trigger to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS youtube_results_fts_insert 
AFTER INSERT ON youtube_results BEGIN
    INSERT INTO youtube_results_fts(rowid, title, description, tags)
    VALUES (new.id, new.title, new.description, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS youtube_results_fts_update 
AFTER UPDATE ON youtube_results BEGIN
    UPDATE youtube_results_fts 
    SET title = new.title,
        description = new.description,
        tags = new.tags
    WHERE rowid = new.id;
END;

CREATE TRIGGER IF NOT EXISTS youtube_results_fts_delete 
AFTER DELETE ON youtube_results BEGIN
    DELETE FROM youtube_results_fts WHERE rowid = old.id;
END;

-- Statistics view for monitoring
CREATE VIEW IF NOT EXISTS youtube_results_stats AS
SELECT
    source,
    COUNT(*) as total_results,
    AVG(universal_score) as avg_score,
    MAX(scraped_at) as last_scraped,
    MIN(scraped_at) as first_scraped
FROM youtube_results
GROUP BY source;
```

### 2. Result Database Wrapper

**File**: `src/storage/result_database.py`

```python
"""Database wrapper for results storage.

This module provides a database connection wrapper with
Windows optimization and schema management.
"""

import sqlite3
from pathlib import Path
from typing import Optional
import logging


logger = logging.getLogger(__name__)


class ResultDatabase:
    """Database wrapper for result storage.
    
    Manages SQLite connection, schema creation, and Windows optimization.
    
    Attributes:
        db_path: Path to SQLite database file
        connection: SQLite connection (lazy-loaded)
    
    Example:
        >>> db = ResultDatabase("results.db")
        >>> conn = db.get_connection()
        >>> # Use connection...
    """
    
    def __init__(self, db_path: str):
        """Initialize database wrapper.
        
        Args:
            db_path: Path to database file
        """
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        self._initialized = False
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection (lazy-loaded).
        
        Returns:
            SQLite connection
        """
        if self._connection is None:
            self._connection = self._create_connection()
            self._optimize_for_windows()
            if not self._initialized:
                self._create_schema()
                self._initialized = True
        
        return self._connection
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create SQLite connection.
        
        Returns:
            SQLite connection with Row factory
        """
        # Create parent directory if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create connection
        conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,  # Allow multi-threaded access
            timeout=30.0  # 30 second timeout for locks
        )
        
        # Enable Row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        logger.info(f"Connected to database: {self.db_path}")
        
        return conn
    
    def _optimize_for_windows(self) -> None:
        """Apply Windows-specific SQLite optimizations."""
        cursor = self._connection.cursor()
        
        # WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode = WAL")
        
        # Normal synchronous for better performance
        cursor.execute("PRAGMA synchronous = NORMAL")
        
        # Increase cache size (64MB)
        cursor.execute("PRAGMA cache_size = -64000")
        
        # Use memory for temp tables
        cursor.execute("PRAGMA temp_store = MEMORY")
        
        # Memory-mapped I/O (256MB)
        cursor.execute("PRAGMA mmap_size = 268435456")
        
        # Increase page size for better performance
        cursor.execute("PRAGMA page_size = 4096")
        
        self._connection.commit()
        
        logger.debug("Applied Windows optimizations to database")
    
    def _create_schema(self) -> None:
        """Create database schema from SQL file."""
        schema_file = Path(__file__).parent / "schema.sql"
        
        if not schema_file.exists():
            logger.warning(f"Schema file not found: {schema_file}")
            return
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        cursor = self._connection.cursor()
        cursor.executescript(schema_sql)
        self._connection.commit()
        
        logger.info("Database schema created/verified")
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
```

### 3. Deduplication Strategy

**File**: `src/storage/deduplication.py`

```python
"""Deduplication strategies for result storage.

This module provides strategies for detecting and handling
duplicate results based on various uniqueness criteria.
"""

from typing import Dict, Any, Protocol, Tuple
import hashlib
import json


class DeduplicationStrategyProtocol(Protocol):
    """Protocol for deduplication strategies."""
    
    def get_key(self, result: Dict[str, Any]) -> Tuple[str, str]:
        """Get uniqueness key for result.
        
        Args:
            result: Result dictionary
            
        Returns:
            Tuple of (source, unique_id)
        """
        ...
    
    def should_update(self, existing: Dict[str, Any], new: Dict[str, Any]) -> bool:
        """Determine if existing result should be updated.
        
        Args:
            existing: Existing result in database
            new: New result to potentially store
            
        Returns:
            True if should update, False to skip
        """
        ...


class SourceIdDeduplication:
    """Deduplication based on source and source_id.
    
    This is the default strategy that prevents duplicate entries
    for the same video from the same source.
    
    Example:
        >>> strategy = SourceIdDeduplication()
        >>> key = strategy.get_key({'source': 'youtube_channel', 'source_id': 'abc123'})
        >>> key
        ('youtube_channel', 'abc123')
    """
    
    def get_key(self, result: Dict[str, Any]) -> Tuple[str, str]:
        """Get (source, source_id) as key."""
        source = result.get('source', 'unknown')
        source_id = result.get('source_id', '')
        return (source, source_id)
    
    def should_update(self, existing: Dict[str, Any], new: Dict[str, Any]) -> bool:
        """Update if new result has more recent data.
        
        Updates if:
        - New result has higher view count (indicates updated stats)
        - New result has subtitle data and existing doesn't
        - Scraped more than 24 hours apart
        """
        # Update if view count increased
        if new.get('view_count', 0) > existing.get('view_count', 0):
            return True
        
        # Update if new has subtitles and old doesn't
        if new.get('subtitles') and not existing.get('subtitles'):
            return True
        
        # Default: don't update (keep original)
        return False


class ContentHashDeduplication:
    """Deduplication based on content hash.
    
    Uses hash of title + description to detect true duplicates
    (same content from different sources/IDs).
    """
    
    def get_key(self, result: Dict[str, Any]) -> Tuple[str, str]:
        """Get content hash as key."""
        title = result.get('title', '')
        description = result.get('description', '')
        
        content = f"{title}|{description}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        return ('content_hash', content_hash)
    
    def should_update(self, existing: Dict[str, Any], new: Dict[str, Any]) -> bool:
        """Always update to keep most recent version."""
        return True
```

### 4. Result Storage Repository

**File**: `src/storage/result_storage.py`

```python
"""Result storage repository following Repository pattern.

This module provides the main interface for storing and retrieving
YouTube scraping results.
"""

import sqlite3
from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime

from .result_database import ResultDatabase
from .deduplication import SourceIdDeduplication, DeduplicationStrategyProtocol


logger = logging.getLogger(__name__)


class ResultStorage:
    """Repository for YouTube scraping results.
    
    Provides high-level interface for storing and querying results
    with built-in deduplication and transaction management.
    
    Attributes:
        database: ResultDatabase instance
        dedup_strategy: Deduplication strategy
    
    Example:
        >>> storage = ResultStorage("results.db")
        >>> result = {
        ...     'source': 'youtube_channel',
        ...     'source_id': 'abc123',
        ...     'title': 'Test Video',
        ...     'url': 'https://youtube.com/watch?v=abc123',
        ...     'view_count': 1000
        ... }
        >>> result_id = storage.save(result)
        >>> print(f"Saved result {result_id}")
    """
    
    def __init__(
        self,
        db_path: str,
        dedup_strategy: Optional[DeduplicationStrategyProtocol] = None
    ):
        """Initialize result storage.
        
        Args:
            db_path: Path to SQLite database
            dedup_strategy: Deduplication strategy (default: SourceIdDeduplication)
        """
        self.database = ResultDatabase(db_path)
        self.dedup_strategy = dedup_strategy or SourceIdDeduplication()
    
    def save(self, result: Dict[str, Any]) -> int:
        """Save single result with deduplication.
        
        Args:
            result: Result dictionary
            
        Returns:
            Result ID (existing or new)
            
        Raises:
            ValueError: If required fields missing
        """
        # Validate required fields
        self._validate_result(result)
        
        # Get deduplication key
        source, source_id = self.dedup_strategy.get_key(result)
        
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("""
            SELECT id, * FROM youtube_results
            WHERE source = ? AND source_id = ?
        """, (source, source_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # Check if should update
            if self.dedup_strategy.should_update(dict(existing), result):
                result_id = self._update_result(existing['id'], result)
                logger.debug(f"Updated existing result {result_id}")
            else:
                result_id = existing['id']
                logger.debug(f"Skipped duplicate result {result_id}")
        else:
            # Insert new result
            result_id = self._insert_result(result)
            logger.debug(f"Inserted new result {result_id}")
        
        conn.commit()
        
        return result_id
    
    def save_batch(self, results: List[Dict[str, Any]]) -> int:
        """Save multiple results efficiently.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Number of results saved (inserted or updated)
        """
        if not results:
            return 0
        
        conn = self.database.get_connection()
        saved_count = 0
        
        try:
            # Process in transaction for atomicity
            for result in results:
                try:
                    self.save(result)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Failed to save result: {e}")
                    # Continue with next result
            
            conn.commit()
            logger.info(f"Batch saved {saved_count}/{len(results)} results")
        
        except Exception as e:
            conn.rollback()
            logger.error(f"Batch save failed: {e}")
            raise
        
        return saved_count
    
    def get_by_id(self, result_id: int) -> Optional[Dict[str, Any]]:
        """Get result by ID.
        
        Args:
            result_id: Result ID
            
        Returns:
            Result dictionary or None if not found
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM youtube_results WHERE id = ?", (result_id,))
        row = cursor.fetchone()
        
        return dict(row) if row else None
    
    def exists(self, source: str, source_id: str) -> bool:
        """Check if result exists.
        
        Args:
            source: Source name
            source_id: Source-specific ID
            
        Returns:
            True if exists, False otherwise
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 1 FROM youtube_results
            WHERE source = ? AND source_id = ?
            LIMIT 1
        """, (source, source_id))
        
        return cursor.fetchone() is not None
    
    def query(
        self,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "scraped_at DESC"
    ) -> List[Dict[str, Any]]:
        """Query results with filters.
        
        Args:
            source: Filter by source (optional)
            limit: Maximum results to return
            offset: Results offset for pagination
            order_by: ORDER BY clause
            
        Returns:
            List of result dictionaries
        """
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM youtube_results"
        params = []
        
        if source:
            sql += " WHERE source = ?"
            params.append(source)
        
        sql += f" ORDER BY {order_by} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(sql, params)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def _validate_result(self, result: Dict[str, Any]) -> None:
        """Validate result has required fields."""
        required = ['source', 'source_id', 'title', 'url']
        
        for field in required:
            if field not in result:
                raise ValueError(f"Missing required field: {field}")
    
    def _insert_result(self, result: Dict[str, Any]) -> int:
        """Insert new result."""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        # Serialize JSON fields
        tags = json.dumps(result.get('tags', []))
        subtitles = json.dumps(result.get('subtitles', {}))
        extra_metadata = json.dumps(result.get('extra_metadata', {}))
        
        cursor.execute("""
            INSERT INTO youtube_results (
                source, source_id, title, description, url, thumbnail_url,
                channel_id, channel_name, channel_url,
                duration_seconds, published_at, tags, category,
                view_count, like_count, comment_count,
                engagement_rate, like_ratio, views_per_day, views_per_hour,
                universal_engagement, universal_virality, universal_quality,
                universal_recency, universal_score,
                subtitles, extra_metadata, scraped_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, CURRENT_TIMESTAMP
            )
        """, (
            result['source'],
            result['source_id'],
            result['title'],
            result.get('description'),
            result['url'],
            result.get('thumbnail_url'),
            result.get('channel_id'),
            result.get('channel_name'),
            result.get('channel_url'),
            result.get('duration_seconds'),
            result.get('published_at'),
            tags,
            result.get('category'),
            result.get('view_count', 0),
            result.get('like_count', 0),
            result.get('comment_count', 0),
            result.get('engagement_rate'),
            result.get('like_ratio'),
            result.get('views_per_day'),
            result.get('views_per_hour'),
            result.get('universal_engagement'),
            result.get('universal_virality'),
            result.get('universal_quality'),
            result.get('universal_recency'),
            result.get('universal_score'),
            subtitles,
            extra_metadata
        ))
        
        return cursor.lastrowid
    
    def _update_result(self, result_id: int, result: Dict[str, Any]) -> int:
        """Update existing result."""
        conn = self.database.get_connection()
        cursor = conn.cursor()
        
        # Serialize JSON fields
        tags = json.dumps(result.get('tags', []))
        subtitles = json.dumps(result.get('subtitles', {}))
        extra_metadata = json.dumps(result.get('extra_metadata', {}))
        
        cursor.execute("""
            UPDATE youtube_results SET
                title = ?, description = ?, url = ?, thumbnail_url = ?,
                channel_id = ?, channel_name = ?, channel_url = ?,
                duration_seconds = ?, published_at = ?, tags = ?, category = ?,
                view_count = ?, like_count = ?, comment_count = ?,
                engagement_rate = ?, like_ratio = ?, views_per_day = ?, views_per_hour = ?,
                universal_engagement = ?, universal_virality = ?, universal_quality = ?,
                universal_recency = ?, universal_score = ?,
                subtitles = ?, extra_metadata = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            result['title'],
            result.get('description'),
            result['url'],
            result.get('thumbnail_url'),
            result.get('channel_id'),
            result.get('channel_name'),
            result.get('channel_url'),
            result.get('duration_seconds'),
            result.get('published_at'),
            tags,
            result.get('category'),
            result.get('view_count', 0),
            result.get('like_count', 0),
            result.get('comment_count', 0),
            result.get('engagement_rate'),
            result.get('like_ratio'),
            result.get('views_per_day'),
            result.get('views_per_hour'),
            result.get('universal_engagement'),
            result.get('universal_virality'),
            result.get('universal_quality'),
            result.get('universal_recency'),
            result.get('universal_score'),
            subtitles,
            extra_metadata,
            result_id
        ))
        
        return result_id
```

### 5. Package Exports

**File**: `src/storage/__init__.py`

```python
"""Result storage package.

Provides Repository pattern implementation for storing YouTube
scraping results with deduplication and query interfaces.
"""

from .result_storage import ResultStorage
from .result_database import ResultDatabase
from .deduplication import (
    SourceIdDeduplication,
    ContentHashDeduplication,
    DeduplicationStrategyProtocol
)


__all__ = [
    'ResultStorage',
    'ResultDatabase',
    'SourceIdDeduplication',
    'ContentHashDeduplication',
    'DeduplicationStrategyProtocol',
]
```

---

## Integration with Workers

Workers will use ResultStorage to save scraping results:

```python
# In BaseWorker or plugin

from src.storage import ResultStorage

class BaseWorker:
    def __init__(self, ..., results_db_path: str):
        self.result_storage = ResultStorage(results_db_path)
    
    def report_result(self, task: Task, result: TaskResult):
        """Save task results to storage."""
        if result.success and result.data:
            # Save each scraped item
            saved_count = self.result_storage.save_batch(result.data)
            logger.info(f"Saved {saved_count} results for task {task.id}")
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] ResultDatabase wrapper with Windows optimization
- [ ] ResultStorage repository with save/save_batch/get_by_id/exists/query
- [ ] SourceIdDeduplication strategy implemented
- [ ] ContentHashDeduplication strategy implemented (alternative)
- [ ] Database schema created with indexes
- [ ] Full-text search support (optional)
- [ ] Transaction management (ACID compliance)
- [ ] Batch operations for efficiency

### Non-Functional Requirements
- [ ] All SOLID principles verified
- [ ] Thread-safe database access
- [ ] Windows SQLite optimization applied
- [ ] Query performance <100ms for common queries

### Code Quality
- [ ] Type hints on all methods
- [ ] Docstrings (Google style)
- [ ] mypy type checking passes
- [ ] pylint score >8.5/10

### Testing Requirements
- [ ] Unit tests for ResultDatabase
- [ ] Unit tests for deduplication strategies
- [ ] Unit tests for ResultStorage (with mock DB)
- [ ] Integration tests with real SQLite
- [ ] Test batch operations
- [ ] Test deduplication logic
- [ ] Test transaction rollback
- [ ] Test coverage >80%

---

## Testing Strategy

### Unit Tests

**File**: `_meta/tests/test_result_database.py`

```python
def test_result_database_creation():
    """Test database creation."""
    db = ResultDatabase(":memory:")
    conn = db.get_connection()
    assert conn is not None


def test_windows_optimization():
    """Test Windows optimization applied."""
    db = ResultDatabase(":memory:")
    conn = db.get_connection()
    
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode")
    assert cursor.fetchone()[0] == 'wal'
```

**File**: `_meta/tests/test_deduplication.py`

```python
def test_source_id_deduplication():
    """Test source+ID deduplication."""
    strategy = SourceIdDeduplication()
    
    result = {
        'source': 'youtube_channel',
        'source_id': 'abc123'
    }
    
    key = strategy.get_key(result)
    assert key == ('youtube_channel', 'abc123')


def test_should_update_higher_views():
    """Test update when view count increases."""
    strategy = SourceIdDeduplication()
    
    existing = {'view_count': 1000}
    new = {'view_count': 2000}
    
    assert strategy.should_update(existing, new) is True
```

**File**: `_meta/tests/test_result_storage.py`

```python
def test_save_result():
    """Test saving a result."""
    storage = ResultStorage(":memory:")
    
    result = {
        'source': 'youtube_channel',
        'source_id': 'abc123',
        'title': 'Test Video',
        'url': 'https://youtube.com/watch?v=abc123',
        'view_count': 1000
    }
    
    result_id = storage.save(result)
    assert result_id > 0


def test_deduplication():
    """Test deduplication prevents duplicates."""
    storage = ResultStorage(":memory:")
    
    result = {
        'source': 'youtube_channel',
        'source_id': 'abc123',
        'title': 'Test Video',
        'url': 'https://youtube.com/watch?v=abc123'
    }
    
    id1 = storage.save(result)
    id2 = storage.save(result)  # Should return same ID
    
    assert id1 == id2


def test_batch_save():
    """Test batch save operation."""
    storage = ResultStorage(":memory:")
    
    results = [
        {'source': 'test', 'source_id': f'id{i}', 'title': f'Video {i}', 'url': f'http://test.com/{i}'}
        for i in range(10)
    ]
    
    saved_count = storage.save_batch(results)
    assert saved_count == 10
```

---

## Performance Targets

- [ ] Save single result: <10ms
- [ ] Batch save 100 results: <500ms
- [ ] Deduplication check: <1ms
- [ ] Query 100 results: <100ms
- [ ] Full-text search: <200ms

---

## Dependencies

### Issue Dependencies
- **#004** (Database Schema): Use similar schema approach

### External Dependencies
- Python sqlite3 (standard library)

---

## Windows-Specific Considerations

- WAL mode for better concurrency on Windows
- Memory-mapped I/O optimization
- Increased cache size
- NORMAL synchronous mode (safer than OFF)

---

## Risks & Mitigation

### Risk: Database Corruption
**Mitigation**: WAL mode, proper transaction management

### Risk: Performance Degradation with Large Data
**Mitigation**: Proper indexing, batch operations

### Risk: Deduplication False Positives
**Mitigation**: Test with real data, adjustable strategies

---

## Future Extensibility

This system enables:
- Custom deduplication strategies
- Result caching layers
- Data archival
- Analytics and reporting
- Export to other formats

---

## References

### Internal
- Issue #004: Database Schema
- Master Plan: #001
- Current database.py: `src/core/database.py`

### External
- SQLite FTS5: https://www.sqlite.org/fts5.html
- Repository Pattern: Design Patterns book

---

**Status**: 📋 Ready for Assignment  
**Created**: 2025-11-11  
**Assigned To**: Worker06 - Database Specialist  
**Estimated Start**: After #004 complete  
**Estimated Duration**: 2 days
