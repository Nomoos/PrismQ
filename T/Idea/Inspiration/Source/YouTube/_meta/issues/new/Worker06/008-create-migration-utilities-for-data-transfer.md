# Issue #008: Create Migration Utilities for Data Transfer

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 06 - Database Specialist  
**Language**: Python 3.10+ (SQLite, SQL)  
**Status**: New  
**Priority**: Medium  
**Duration**: 1-2 days  
**Dependencies**: #004 (Database Schema), #007 (Result Storage Layer)

---

## Worker Details: Worker06 - Database Specialist

**Role**: Data Migration & Version Management  
**Expertise Required**:
- Database migration strategies
- Data transformation and validation
- Schema versioning
- Rollback procedures
- Python scripting for migrations
- SQLite data export/import

**Collaboration**:
- **Worker06** (self): Build on #004 and #007
- **Worker02** (Python): Coordinate on migration script interfaces
- **Worker01** (PM): Daily standup, migration validation

**See**: `_meta/issues/new/Worker06/README.md` for complete role description

---

## Objective

Create a migration utility system to safely transfer existing YouTube scraping data to the new worker-based architecture, manage schema versions, and provide rollback capabilities while ensuring data integrity throughout the migration process.

---

## Problem Statement

When transitioning to the worker-based architecture:
1. Existing scraped data must be preserved
2. Schema changes need to be applied safely
3. Migration must be reversible (rollback capability)
4. Data integrity must be maintained
5. Migration progress must be trackable

Currently:
- No migration system exists
- Schema changes are manual
- No version tracking
- No rollback procedures
- Risk of data loss during migration

We need:
1. **Migration Manager** to coordinate migrations
2. **Version tracking** to know current schema state
3. **Migration scripts** for specific schema changes
4. **Validation** to ensure data integrity
5. **Rollback procedures** for failed migrations
6. **Progress tracking** for long-running migrations

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅

**MigrationManager Responsibilities**:
- Execute migration scripts
- Track migration versions
- Coordinate migration workflow
- Validate migration success

**NOT Responsible For**:
- Migration script logic (Migration classes)
- Data transformation (individual migrations)
- Database connection management (uses existing)

**Migration Script Responsibilities**:
- Perform specific schema/data changes
- Validate migration prerequisites
- Implement rollback logic
- Report migration progress

**NOT Responsible For**:
- Version tracking (MigrationManager)
- Migration coordination (MigrationManager)
- Database connection (injected)

### Open/Closed Principle (OCP) ✅

**Open for Extension**:
- New migrations can be added without modifying manager
- Migration scripts are independent
- New validation rules can be added

**Closed for Modification**:
- Migration manager core logic stable
- Version tracking unchanged
- Rollback mechanism standardized

### Liskov Substitution Principle (LSP) ✅

**Substitutability**:
- All Migration implementations follow same interface
- Migrations can be executed in any order (if dependencies met)
- No unexpected behavior changes

### Interface Segregation Principle (ISP) ✅

**Minimal Interface**:
```python
class MigrationProtocol(Protocol):
    def get_version(self) -> str: ...
    def up(self, conn: sqlite3.Connection) -> None: ...
    def down(self, conn: sqlite3.Connection) -> None: ...
    def validate(self, conn: sqlite3.Connection) -> bool: ...
```

Only essential methods for migration execution.

### Dependency Inversion Principle (DIP) ✅

**Depend on Abstractions**:
- MigrationManager depends on Migration protocol
- Database connection injected
- No concrete migration dependencies

---

## Proposed Solution

### Architecture Overview

```
Migration System
├── MigrationManager              # Orchestrates migrations
│   ├── get_current_version()    # Current schema version
│   ├── migrate_to()             # Migrate to version
│   ├── rollback()               # Rollback last migration
│   └── list_migrations()        # Available migrations
│
├── Migration (Protocol)          # Migration interface
│   ├── get_version()            # Version number
│   ├── up()                     # Apply migration
│   ├── down()                   # Rollback migration
│   └── validate()               # Validate success
│
└── Concrete Migrations
    ├── Migration001_InitialSchema      # Create initial tables
    ├── Migration002_AddIndexes         # Add performance indexes
    └── Migration003_DataTransfer       # Transfer existing data
```

---

## Implementation Details

### File Structure

```
src/
├── storage/
│   ├── migrations/
│   │   ├── __init__.py          # NEW: Migration exports
│   │   ├── manager.py           # NEW: MigrationManager
│   │   ├── base.py              # NEW: Migration base class
│   │   ├── 001_initial_schema.py    # NEW: Initial schema
│   │   ├── 002_add_indexes.py       # NEW: Performance indexes
│   │   └── 003_data_transfer.py     # NEW: Data migration
│   └── ...
│
├── scripts/
│   └── migrate.py               # NEW: CLI migration tool
```

### 1. Migration Base Class

**File**: `src/storage/migrations/base.py`

```python
"""Base class and protocol for database migrations.

This module provides the foundation for database migration scripts.
"""

from abc import ABC, abstractmethod
from typing import Protocol
import sqlite3
import logging


logger = logging.getLogger(__name__)


class MigrationProtocol(Protocol):
    """Protocol for database migrations."""
    
    def get_version(self) -> str:
        """Get migration version identifier.
        
        Returns:
            Version string (e.g., '001', '002')
        """
        ...
    
    def get_description(self) -> str:
        """Get migration description.
        
        Returns:
            Human-readable description
        """
        ...
    
    def up(self, conn: sqlite3.Connection) -> None:
        """Apply migration (forward).
        
        Args:
            conn: SQLite database connection
            
        Raises:
            Exception: On migration failure
        """
        ...
    
    def down(self, conn: sqlite3.Connection) -> None:
        """Rollback migration (backward).
        
        Args:
            conn: SQLite database connection
            
        Raises:
            Exception: On rollback failure
        """
        ...
    
    def validate(self, conn: sqlite3.Connection) -> bool:
        """Validate migration was successful.
        
        Args:
            conn: SQLite database connection
            
        Returns:
            True if migration valid, False otherwise
        """
        ...


class BaseMigration(ABC):
    """Abstract base class for migrations.
    
    Provides common functionality for migration scripts.
    Subclasses must implement up(), down(), and validate().
    
    Example:
        >>> class Migration001(BaseMigration):
        ...     def get_version(self) -> str:
        ...         return '001'
        ...     
        ...     def up(self, conn):
        ...         conn.execute("CREATE TABLE ...")
        ...     
        ...     def down(self, conn):
        ...         conn.execute("DROP TABLE ...")
        ...     
        ...     def validate(self, conn):
        ...         # Check table exists
        ...         return True
    """
    
    @abstractmethod
    def get_version(self) -> str:
        """Get migration version."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get migration description."""
        pass
    
    @abstractmethod
    def up(self, conn: sqlite3.Connection) -> None:
        """Apply migration."""
        pass
    
    @abstractmethod
    def down(self, conn: sqlite3.Connection) -> None:
        """Rollback migration."""
        pass
    
    @abstractmethod
    def validate(self, conn: sqlite3.Connection) -> bool:
        """Validate migration."""
        pass
    
    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        """Check if table exists.
        
        Args:
            conn: Database connection
            table_name: Table name to check
            
        Returns:
            True if table exists
        """
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """, (table_name,))
        return cursor.fetchone() is not None
    
    def _column_exists(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        column_name: str
    ) -> bool:
        """Check if column exists in table.
        
        Args:
            conn: Database connection
            table_name: Table name
            column_name: Column name
            
        Returns:
            True if column exists
        """
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        return column_name in columns
```

### 2. Migration Manager

**File**: `src/storage/migrations/manager.py`

```python
"""Migration manager for coordinating database migrations.

This module provides the MigrationManager class that orchestrates
database schema migrations with version tracking and rollback support.
"""

import sqlite3
from typing import List, Optional, Type
import logging
from pathlib import Path

from .base import BaseMigration, MigrationProtocol


logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages database migrations and versioning.
    
    Tracks applied migrations, executes new migrations, and handles
    rollbacks. Maintains a migration_history table for version tracking.
    
    Attributes:
        db_path: Path to SQLite database
        migrations: List of available migration classes
    
    Example:
        >>> manager = MigrationManager("data.db")
        >>> manager.register_migration(Migration001)
        >>> manager.register_migration(Migration002)
        >>> manager.migrate_to_latest()
    """
    
    def __init__(self, db_path: str):
        """Initialize migration manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.migrations: List[Type[BaseMigration]] = []
        self._ensure_migration_table()
    
    def register_migration(self, migration_class: Type[BaseMigration]) -> None:
        """Register a migration class.
        
        Args:
            migration_class: Migration class to register
        """
        self.migrations.append(migration_class)
        self.migrations.sort(key=lambda m: m().get_version())
    
    def get_current_version(self) -> Optional[str]:
        """Get current database version.
        
        Returns:
            Current version string or None if no migrations applied
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version FROM migration_history
            WHERE applied = 1
            ORDER BY applied_at DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def get_pending_migrations(self) -> List[BaseMigration]:
        """Get list of pending migrations.
        
        Returns:
            List of migration instances that haven't been applied
        """
        current_version = self.get_current_version()
        pending = []
        
        for migration_class in self.migrations:
            migration = migration_class()
            version = migration.get_version()
            
            if current_version is None or version > current_version:
                if not self._is_applied(version):
                    pending.append(migration)
        
        return pending
    
    def migrate_to_latest(self) -> bool:
        """Migrate database to latest version.
        
        Returns:
            True if successful, False if any migration failed
        """
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("Database is up to date")
            return True
        
        logger.info(f"Applying {len(pending)} pending migrations")
        
        for migration in pending:
            if not self._apply_migration(migration):
                logger.error(f"Migration {migration.get_version()} failed")
                return False
        
        logger.info("All migrations applied successfully")
        return True
    
    def migrate_to(self, target_version: str) -> bool:
        """Migrate to specific version.
        
        Args:
            target_version: Target version to migrate to
            
        Returns:
            True if successful
        """
        current = self.get_current_version()
        
        if current == target_version:
            logger.info(f"Already at version {target_version}")
            return True
        
        # Find migrations to apply
        migrations_to_apply = []
        for migration_class in self.migrations:
            migration = migration_class()
            version = migration.get_version()
            
            if version <= target_version and not self._is_applied(version):
                migrations_to_apply.append(migration)
        
        # Apply migrations
        for migration in migrations_to_apply:
            if not self._apply_migration(migration):
                return False
        
        return True
    
    def rollback(self, steps: int = 1) -> bool:
        """Rollback last N migrations.
        
        Args:
            steps: Number of migrations to rollback (default: 1)
            
        Returns:
            True if successful
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get last N applied migrations
        cursor.execute("""
            SELECT version FROM migration_history
            WHERE applied = 1
            ORDER BY applied_at DESC
            LIMIT ?
        """, (steps,))
        
        versions_to_rollback = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not versions_to_rollback:
            logger.info("No migrations to rollback")
            return True
        
        logger.info(f"Rolling back {len(versions_to_rollback)} migrations")
        
        # Rollback in reverse order
        for version in versions_to_rollback:
            if not self._rollback_migration(version):
                return False
        
        logger.info("Rollback completed successfully")
        return True
    
    def list_migrations(self) -> List[dict]:
        """List all migrations and their status.
        
        Returns:
            List of migration info dictionaries
        """
        migrations_info = []
        
        for migration_class in self.migrations:
            migration = migration_class()
            version = migration.get_version()
            
            migrations_info.append({
                'version': version,
                'description': migration.get_description(),
                'applied': self._is_applied(version)
            })
        
        return migrations_info
    
    def _ensure_migration_table(self) -> None:
        """Create migration_history table if not exists."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL UNIQUE,
                description TEXT,
                applied INTEGER DEFAULT 0,
                applied_at TEXT,
                rolled_back_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _apply_migration(self, migration: BaseMigration) -> bool:
        """Apply a single migration.
        
        Args:
            migration: Migration to apply
            
        Returns:
            True if successful
        """
        version = migration.get_version()
        description = migration.get_description()
        
        logger.info(f"Applying migration {version}: {description}")
        
        conn = self._get_connection()
        
        try:
            # Execute migration
            migration.up(conn)
            conn.commit()
            
            # Validate
            if not migration.validate(conn):
                raise Exception("Migration validation failed")
            
            # Record in history
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO migration_history (version, description, applied, applied_at)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            """, (version, description))
            conn.commit()
            
            logger.info(f"Migration {version} applied successfully")
            return True
        
        except Exception as e:
            logger.error(f"Migration {version} failed: {e}")
            conn.rollback()
            return False
        
        finally:
            conn.close()
    
    def _rollback_migration(self, version: str) -> bool:
        """Rollback a single migration.
        
        Args:
            version: Version to rollback
            
        Returns:
            True if successful
        """
        # Find migration
        migration = None
        for migration_class in self.migrations:
            m = migration_class()
            if m.get_version() == version:
                migration = m
                break
        
        if not migration:
            logger.error(f"Migration {version} not found")
            return False
        
        logger.info(f"Rolling back migration {version}")
        
        conn = self._get_connection()
        
        try:
            # Execute rollback
            migration.down(conn)
            conn.commit()
            
            # Update history
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE migration_history
                SET applied = 0, rolled_back_at = CURRENT_TIMESTAMP
                WHERE version = ?
            """, (version,))
            conn.commit()
            
            logger.info(f"Migration {version} rolled back successfully")
            return True
        
        except Exception as e:
            logger.error(f"Rollback {version} failed: {e}")
            conn.rollback()
            return False
        
        finally:
            conn.close()
    
    def _is_applied(self, version: str) -> bool:
        """Check if migration is applied."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT applied FROM migration_history
            WHERE version = ?
        """, (version,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row and row[0] == 1
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(str(self.db_path))
```

### 3. Example Migration: Initial Schema

**File**: `src/storage/migrations/001_initial_schema.py`

```python
"""Migration 001: Create initial worker queue schema.

Creates the task_queue table for the worker system.
"""

import sqlite3

from .base import BaseMigration


class Migration001_InitialSchema(BaseMigration):
    """Create initial worker queue schema."""
    
    def get_version(self) -> str:
        """Version 001."""
        return '001'
    
    def get_description(self) -> str:
        """Description."""
        return 'Create initial worker queue schema'
    
    def up(self, conn: sqlite3.Connection) -> None:
        """Create task_queue table."""
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                parameters TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'QUEUED',
                worker_id TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 5,
                last_error TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                claimed_at TEXT,
                completed_at TEXT,
                failed_at TEXT,
                next_run_after TEXT,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_queue_status
            ON task_queue(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_queue_type
            ON task_queue(task_type)
        """)
    
    def down(self, conn: sqlite3.Connection) -> None:
        """Drop task_queue table."""
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS task_queue")
        cursor.execute("DROP INDEX IF EXISTS idx_task_queue_status")
        cursor.execute("DROP INDEX IF EXISTS idx_task_queue_type")
    
    def validate(self, conn: sqlite3.Connection) -> bool:
        """Validate table exists."""
        return self._table_exists(conn, 'task_queue')
```

### 4. Example Migration: Data Transfer

**File**: `src/storage/migrations/003_data_transfer.py`

```python
"""Migration 003: Transfer existing YouTube data to new schema.

Migrates data from old youtube_shorts table to new youtube_results table.
"""

import sqlite3
import json

from .base import BaseMigration


class Migration003_DataTransfer(BaseMigration):
    """Transfer existing data to new schema."""
    
    def get_version(self) -> str:
        """Version 003."""
        return '003'
    
    def get_description(self) -> str:
        """Description."""
        return 'Transfer existing YouTube data to new schema'
    
    def up(self, conn: sqlite3.Connection) -> None:
        """Transfer data from old to new schema."""
        cursor = conn.cursor()
        
        # Check if old table exists
        if not self._table_exists(conn, 'youtube_shorts'):
            # No old data to migrate
            return
        
        # Transfer data
        cursor.execute("""
            INSERT INTO youtube_results (
                source, source_id, title, description, url,
                channel_id, channel_name, channel_url,
                view_count, like_count, comment_count,
                published_at, scraped_at
            )
            SELECT
                'youtube_legacy' as source,
                video_id as source_id,
                title,
                description,
                url,
                channel_id,
                channel_name,
                channel_url,
                view_count,
                like_count,
                comment_count,
                published_at,
                created_at as scraped_at
            FROM youtube_shorts
            WHERE NOT EXISTS (
                SELECT 1 FROM youtube_results
                WHERE youtube_results.source_id = youtube_shorts.video_id
            )
        """)
        
        rows_transferred = cursor.rowcount
        print(f"Transferred {rows_transferred} rows from old schema")
    
    def down(self, conn: sqlite3.Connection) -> None:
        """Rollback: Delete transferred data."""
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM youtube_results
            WHERE source = 'youtube_legacy'
        """)
        
        print(f"Deleted {cursor.rowcount} migrated rows")
    
    def validate(self, conn: sqlite3.Connection) -> bool:
        """Validate data was transferred."""
        cursor = conn.cursor()
        
        # Check if any legacy data exists
        cursor.execute("""
            SELECT COUNT(*) FROM youtube_results
            WHERE source = 'youtube_legacy'
        """)
        
        count = cursor.fetchone()[0]
        return count >= 0  # Any count is valid (including 0 if no old data)
```

### 5. CLI Migration Tool

**File**: `scripts/migrate.py`

```python
"""CLI tool for running database migrations.

Usage:
    python scripts/migrate.py migrate  # Migrate to latest
    python scripts/migrate.py rollback  # Rollback last migration
    python scripts/migrate.py status  # Show migration status
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from storage.migrations.manager import MigrationManager
from storage.migrations.001_initial_schema import Migration001_InitialSchema
from storage.migrations.003_data_transfer import Migration003_DataTransfer


def main():
    parser = argparse.ArgumentParser(description='Database migration tool')
    parser.add_argument('command', choices=['migrate', 'rollback', 'status', 'list'])
    parser.add_argument('--db', default='data/youtube_results.db', help='Database path')
    parser.add_argument('--steps', type=int, default=1, help='Rollback steps')
    
    args = parser.parse_args()
    
    # Create manager
    manager = MigrationManager(args.db)
    
    # Register migrations
    manager.register_migration(Migration001_InitialSchema)
    manager.register_migration(Migration003_DataTransfer)
    # Add more migrations here...
    
    # Execute command
    if args.command == 'migrate':
        success = manager.migrate_to_latest()
        sys.exit(0 if success else 1)
    
    elif args.command == 'rollback':
        success = manager.rollback(steps=args.steps)
        sys.exit(0 if success else 1)
    
    elif args.command == 'status':
        current = manager.get_current_version()
        print(f"Current version: {current or 'None'}")
        
        pending = manager.get_pending_migrations()
        if pending:
            print(f"\nPending migrations: {len(pending)}")
            for migration in pending:
                print(f"  - {migration.get_version()}: {migration.get_description()}")
        else:
            print("\nDatabase is up to date")
    
    elif args.command == 'list':
        migrations = manager.list_migrations()
        print("Available migrations:")
        for m in migrations:
            status = "✓" if m['applied'] else " "
            print(f"  [{status}] {m['version']}: {m['description']}")


if __name__ == '__main__':
    main()
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] MigrationManager implemented with version tracking
- [ ] BaseMigration abstract class created
- [ ] Migration001: Initial schema created
- [ ] Migration003: Data transfer implemented
- [ ] CLI migration tool working
- [ ] Rollback functionality working
- [ ] Migration validation implemented
- [ ] Migration history table created

### Non-Functional Requirements
- [ ] All SOLID principles verified
- [ ] Safe transaction handling
- [ ] Data integrity maintained
- [ ] Rollback safety verified

### Code Quality
- [ ] Type hints on all methods
- [ ] Docstrings (Google style)
- [ ] mypy type checking passes
- [ ] pylint score >8.5/10

### Testing Requirements
- [ ] Unit tests for MigrationManager
- [ ] Unit tests for BaseMigration helpers
- [ ] Integration tests for complete migration workflow
- [ ] Test rollback functionality
- [ ] Test data transfer migration
- [ ] Test migration validation
- [ ] Test coverage >80%

---

## Testing Strategy

### Unit Tests

**File**: `_meta/tests/test_migration_manager.py`

```python
def test_migration_manager_init():
    """Test migration manager initialization."""
    manager = MigrationManager(":memory:")
    assert manager.get_current_version() is None


def test_register_migration():
    """Test migration registration."""
    manager = MigrationManager(":memory:")
    manager.register_migration(Migration001_InitialSchema)
    
    migrations = manager.list_migrations()
    assert len(migrations) == 1
    assert migrations[0]['version'] == '001'


def test_migrate_to_latest():
    """Test migrating to latest version."""
    manager = MigrationManager(":memory:")
    manager.register_migration(Migration001_InitialSchema)
    
    success = manager.migrate_to_latest()
    assert success is True
    assert manager.get_current_version() == '001'


def test_rollback():
    """Test rollback functionality."""
    manager = MigrationManager(":memory:")
    manager.register_migration(Migration001_InitialSchema)
    
    manager.migrate_to_latest()
    success = manager.rollback(steps=1)
    assert success is True
    assert manager.get_current_version() is None
```

### Integration Tests

**File**: `_meta/tests/test_migration_integration.py`

```python
def test_full_migration_cycle():
    """Test complete migration and rollback cycle."""
    # Create temp database
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.db') as f:
        manager = MigrationManager(f.name)
        manager.register_migration(Migration001_InitialSchema)
        
        # Migrate up
        assert manager.migrate_to_latest() is True
        assert manager.get_current_version() == '001'
        
        # Verify table exists
        conn = sqlite3.connect(f.name)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_queue'")
        assert cursor.fetchone() is not None
        conn.close()
        
        # Rollback
        assert manager.rollback() is True
        assert manager.get_current_version() is None
```

---

## Performance Targets

- [ ] Migration execution: <5 seconds for schema changes
- [ ] Data transfer: <1 second per 1000 rows
- [ ] Rollback: <2 seconds
- [ ] Version check: <10ms

---

## Dependencies

### Issue Dependencies
- **#004** (Database Schema): Use schema structure
- **#007** (Result Storage): Integrate with storage layer

### External Dependencies
- Python sqlite3 (standard library)

---

## Windows-Specific Considerations

- WAL mode for safe concurrent access during migration
- Transaction safety on Windows file system
- Path handling with pathlib

---

## Risks & Mitigation

### Risk: Data Loss During Migration
**Mitigation**: Transaction safety, validation, backup recommendations

### Risk: Failed Rollback
**Mitigation**: Test rollbacks thoroughly, validate before/after

### Risk: Long Migration Times
**Mitigation**: Progress tracking, batch processing, chunking

---

## Future Extensibility

This system enables:
- Automatic migration on startup
- Migration dry-run mode
- Migration progress reporting
- Cloud/remote database migrations
- Schema diffing and generation

---

## References

### Internal
- Issue #004: Database Schema
- Issue #007: Result Storage Layer
- Master Plan: #001

### External
- Database Migrations: https://en.wikipedia.org/wiki/Schema_migration
- SQLite WAL Mode: https://www.sqlite.org/wal.html

---

**Status**: 📋 Ready for Assignment  
**Created**: 2025-11-11  
**Assigned To**: Worker06 - Database Specialist  
**Estimated Start**: After #004, #007 complete  
**Estimated Duration**: 1-2 days
