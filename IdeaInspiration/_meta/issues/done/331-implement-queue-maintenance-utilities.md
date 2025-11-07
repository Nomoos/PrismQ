# Issue #331: Database Maintenance and Backup

**Status**: New  
**Priority**: High  
**Category**: Infrastructure/DevOps  
**Estimated Time**: 3-5 days  
**Created**: 2025-11-05  
**Worker**: Worker 06 - DevOps Engineer

---

## Overview

Implement comprehensive database maintenance and backup utilities for the SQLite task queue system. This includes online backup, WAL checkpoint management, VACUUM/ANALYZE scheduling, and stale lease cleanup to ensure database health and reliability.

---

## Problem Statement

The SQLite queue database (implemented in #321) requires regular maintenance to:
- **Prevent data loss**: Automated backup and recovery procedures
- **Maintain performance**: Regular VACUUM and ANALYZE operations
- **Clean up stale data**: Remove expired leases and dead tasks
- **Manage WAL file growth**: Control checkpoint frequency and WAL size
- **Ensure reliability**: Operational procedures for common maintenance tasks

Without proper maintenance, the database can experience:
- Performance degradation over time
- Excessive WAL file growth
- Stale lease accumulation blocking task execution
- Risk of data loss without backup procedures

---

## Dependencies

- **#321**: Core Infrastructure (✅ COMPLETED)
  - Requires `QueueDatabase`, schema, and models
  - Uses existing PRAGMA settings
  - Builds on transaction support

---

## Scope

### In Scope

1. **Backup Implementation**
   - SQLite online backup API
   - Non-blocking backup while database is in use
   - Configurable backup directory and retention
   - Backup verification and integrity checks

2. **WAL Checkpoint Management**
   - Manual checkpoint triggering
   - Checkpoint mode selection (PASSIVE, FULL, RESTART, TRUNCATE)
   - Monitoring WAL file size
   - Checkpoint scheduling recommendations

3. **Database Optimization**
   - VACUUM operation (reclaim free space)
   - ANALYZE operation (update query planner statistics)
   - Integrity checks (PRAGMA integrity_check)
   - Safe scheduling during low-traffic periods

4. **Stale Lease Cleanup** (Issue #332)
   - Detect and clean up expired leases
   - Requeue tasks with expired leases
   - Configurable lease timeout threshold
   - Prevent task starvation

5. **Operational Documentation**
   - Maintenance runbook with procedures
   - Troubleshooting guide integration
   - Monitoring recommendations
   - Recovery procedures

### Out of Scope

- Schema migrations (deferred to #340)
- Distributed backup to remote storage
- Automated backup scheduling (manual for now)
- Performance benchmarking (covered in #337)
- Integration with monitoring systems (deferred to #329)

---

## Technical Design

### Architecture

```
Client/Backend/src/queue/
├── maintenance.py      # Main maintenance utilities
├── backup.py          # Backup-specific operations  
└── database.py        # Existing (no changes needed)

_meta/docs/
└── QUEUE_MAINTENANCE_RUNBOOK.md  # Operational guide
```

### Key Components

#### 1. Backup Module (`backup.py`)

```python
class QueueBackup:
    """
    SQLite online backup implementation.
    
    Uses SQLite backup API for non-blocking backup while database is in use.
    """
    
    def __init__(self, db: QueueDatabase, backup_dir: str = None):
        """Initialize backup manager."""
        
    def create_backup(self, name: str = None) -> Path:
        """
        Create a backup of the queue database.
        
        Args:
            name: Optional backup name (default: timestamp-based)
            
        Returns:
            Path to backup file
            
        Raises:
            QueueBackupError: If backup fails
        """
        
    def verify_backup(self, backup_path: Path) -> bool:
        """Verify backup integrity."""
        
    def restore_backup(self, backup_path: Path) -> None:
        """Restore database from backup."""
        
    def list_backups(self) -> List[BackupInfo]:
        """List available backups with metadata."""
        
    def cleanup_old_backups(self, keep_count: int = 10) -> None:
        """Remove old backups, keeping most recent N."""
```

#### 2. Maintenance Module (`maintenance.py`)

```python
class QueueMaintenance:
    """
    Database maintenance utilities.
    
    Handles WAL checkpoints, VACUUM, ANALYZE, and cleanup operations.
    """
    
    def __init__(self, db: QueueDatabase):
        """Initialize maintenance manager."""
        
    def checkpoint(self, mode: str = "PASSIVE") -> dict:
        """
        Execute WAL checkpoint.
        
        Args:
            mode: PASSIVE, FULL, RESTART, or TRUNCATE
            
        Returns:
            Checkpoint statistics (pages written, checkpointed)
        """
        
    def vacuum(self) -> None:
        """Reclaim free space and defragment database."""
        
    def analyze(self, table: str = None) -> None:
        """Update query planner statistics."""
        
    def integrity_check(self) -> List[str]:
        """Run database integrity check."""
        
    def cleanup_stale_leases(self, timeout_seconds: int = 300) -> int:
        """
        Clean up expired task leases and requeue tasks.
        
        Args:
            timeout_seconds: Lease expiration threshold
            
        Returns:
            Number of tasks requeued
        """
        
    def get_database_stats(self) -> dict:
        """Get database statistics (size, WAL size, page count, etc.)."""
        
    def optimize(self, full: bool = False) -> dict:
        """
        Run optimization operations.
        
        Executes ANALYZE and optionally VACUUM based on database stats.
        
        Args:
            full: If True, run VACUUM (slow, blocks writes)
            
        Returns:
            Operation statistics
        """
```

#### 3. Configuration

Add to `config.py`:

```python
@dataclass
class MaintenanceConfig:
    """Maintenance operation configuration."""
    
    # Backup settings
    backup_dir: Path = Path("C:\\Data\\PrismQ\\queue\\backups")
    backup_retention_count: int = 10
    
    # Checkpoint settings  
    checkpoint_mode: str = "PASSIVE"
    wal_size_threshold_mb: int = 100
    
    # Optimization settings
    vacuum_threshold_mb: int = 500  # Free space threshold
    analyze_interval_hours: int = 24
    
    # Cleanup settings
    stale_lease_timeout_seconds: int = 300  # 5 minutes
    
    @classmethod
    def from_env(cls) -> "MaintenanceConfig":
        """Load configuration from environment variables."""
```

### Best Practices

1. **Thread Safety**
   - Use existing `QueueDatabase._lock` for synchronization
   - VACUUM requires exclusive lock (blocking)
   - Checkpoints can run concurrently (non-blocking)

2. **Error Handling**
   - Custom exceptions: `QueueBackupError`, `QueueMaintenanceError`
   - Proper resource cleanup with context managers
   - Log all operations for audit trail

3. **Performance**
   - VACUUM should run during low-traffic periods
   - CHECKPOINT PASSIVE is non-blocking
   - ANALYZE is fast and non-blocking
   - Monitor WAL size and trigger checkpoints proactively

4. **Windows Compatibility**
   - Use `Path` for cross-platform paths
   - Handle Windows file locking during backup
   - Test with Windows-style paths

---

## Acceptance Criteria

### Functional Requirements

- [ ] Can create backup of active database without downtime
- [ ] Backup files are valid and can be opened with SQLite
- [ ] Can restore database from backup file
- [ ] Can list and clean up old backups
- [ ] Can trigger WAL checkpoint with different modes
- [ ] Can run VACUUM and ANALYZE operations
- [ ] Can detect and clean up stale leases
- [ ] Can requeue tasks with expired leases
- [ ] All operations handle errors gracefully
- [ ] Operations are thread-safe

### Quality Requirements

- [ ] >80% test coverage for maintenance module
- [ ] >80% test coverage for backup module
- [ ] All public methods have docstrings
- [ ] Type hints for all parameters and return values
- [ ] Code passes security scan (CodeQL)
- [ ] No breaking changes to existing code
- [ ] Works on Windows 10/11 (tested on Linux, Windows-compatible)

### Documentation Requirements

- [ ] Operational runbook created
- [ ] Backup procedures documented
- [ ] Recovery procedures documented
- [ ] Maintenance schedule recommendations
- [ ] Troubleshooting integration
- [ ] API documentation in docstrings

---

## Implementation Plan

### Phase 1: Backup Implementation (1-2 days)

1. Create `backup.py` module
   - Implement `QueueBackup` class
   - SQLite backup API integration
   - Backup verification
   - Backup listing and cleanup

2. Add tests for backup operations
   - Test backup creation
   - Test backup verification
   - Test backup restoration
   - Test cleanup logic

### Phase 2: Maintenance Operations (1-2 days)

1. Create `maintenance.py` module
   - Implement `QueueMaintenance` class
   - WAL checkpoint operations
   - VACUUM and ANALYZE
   - Integrity checks
   - Database statistics

2. Add tests for maintenance operations
   - Test each checkpoint mode
   - Test VACUUM and ANALYZE
   - Test integrity checks
   - Test stats retrieval

### Phase 3: Stale Lease Cleanup (1 day)

1. Implement stale lease detection
   - Query for expired leases
   - Requeue tasks safely
   - Handle edge cases

2. Add tests for cleanup
   - Test lease expiration detection
   - Test requeuing logic
   - Test concurrent access

### Phase 4: Documentation (1 day)

1. Create operational runbook
   - Backup procedures
   - Recovery procedures
   - Maintenance schedule
   - Troubleshooting tips

2. Update module documentation
   - API reference
   - Usage examples
   - Best practices

---

## Test Plan

### Unit Tests

1. **Backup Tests** (`test_backup.py`)
   - Backup creation and verification
   - Backup listing and filtering
   - Old backup cleanup
   - Error handling

2. **Maintenance Tests** (`test_maintenance.py`)
   - Checkpoint operations
   - VACUUM and ANALYZE
   - Integrity checks
   - Stale lease cleanup
   - Database statistics

### Integration Tests

1. **End-to-End Backup/Restore**
   - Create backup of active database
   - Verify backup integrity
   - Restore to new location
   - Validate data consistency

2. **Concurrent Operations**
   - Run backup while writing
   - Run checkpoint during queries
   - Clean stale leases during task execution

### Edge Cases

1. Disk space exhaustion during backup
2. Database locked during VACUUM
3. Invalid backup file restoration
4. Concurrent cleanup of same stale lease

---

## Success Metrics

- **Code Quality**: >80% test coverage, 0 security vulnerabilities
- **Reliability**: Backup/restore tested with real data
- **Performance**: Backup completes in <10 seconds for typical database
- **Usability**: Clear documentation and runbook
- **Maintainability**: Clean code following SOLID principles

---

## Integration Points

### Dependencies From

- **#321**: `QueueDatabase`, schema, models, exceptions

### Feeds Into

- **#329**: Observability (maintenance metrics)
- **#333**: Testing (maintenance test scenarios)
- **#335**: Documentation (maintenance guide)
- **#337**: Research findings (checkpoint recommendations)
- **#339**: Integration (maintenance scheduling)
- **#340**: Migration utilities (backup for migrations)

---

## Risks and Mitigations

### Risk 1: VACUUM Blocking Writes
- **Impact**: High - Can block task processing
- **Probability**: Medium
- **Mitigation**: 
  - Document VACUUM as admin-only operation
  - Recommend running during maintenance windows
  - Provide non-blocking alternative (PRAGMA auto_vacuum)

### Risk 2: Backup File Corruption
- **Impact**: High - Invalid backups useless for recovery
- **Probability**: Low
- **Mitigation**:
  - Implement backup verification
  - Test restoration regularly
  - Keep multiple backup copies

### Risk 3: Disk Space Exhaustion
- **Impact**: Medium - Backup or VACUUM failure
- **Probability**: Low
- **Mitigation**:
  - Check available space before operations
  - Implement backup retention limits
  - Monitor disk space in runbook

### Risk 4: Stale Lease Race Conditions
- **Impact**: Medium - Task double-execution
- **Probability**: Low
- **Mitigation**:
  - Use atomic SQL operations
  - Proper WHERE clause conditions
  - Transaction isolation

---

## References

- [SQLite Backup API](https://www.sqlite.org/backup.html)
- [WAL Checkpointing](https://www.sqlite.org/wal.html#checkpointing)
- [VACUUM Command](https://www.sqlite.org/lang_vacuum.html)
- [ANALYZE Command](https://www.sqlite.org/lang_analyze.html)
- Issue #321: Core Infrastructure
- Issue #337: Concurrency Research
- `_meta/docs/SQLITE_QUEUE_TROUBLESHOOTING.md`

---

## Timeline

- **Day 1-2**: Backup implementation and tests
- **Day 3-4**: Maintenance operations and tests
- **Day 5**: Stale lease cleanup and documentation
- **Total**: 3-5 days

---

**Status**: Ready for Implementation  
**Assigned**: Worker 06 - DevOps Engineer  
**Created**: 2025-11-05
