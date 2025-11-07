# SQLite Queue Maintenance Runbook

**Version**: 1.0  
**Date**: 2025-11-05  
**Related**: Issue #331 - Database Maintenance and Backup  
**Platform**: Windows 10/11 with NVIDIA RTX 5090

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Backup Procedures](#backup-procedures)
4. [Restore Procedures](#restore-procedures)
5. [Maintenance Operations](#maintenance-operations)
6. [Monitoring and Health Checks](#monitoring-and-health-checks)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance Schedule](#maintenance-schedule)

---

## Overview

This runbook provides operational procedures for maintaining the SQLite task queue database. The queue uses SQLite with WAL (Write-Ahead Logging) mode for concurrent access, optimized for Windows SSD performance.

### Key Characteristics

- **Database Location**: `C:\Data\PrismQ\queue\queue.db` (Windows)
- **Backup Location**: `C:\Data\PrismQ\queue\backups\` (Windows)
- **Journal Mode**: WAL (Write-Ahead Logging)
- **Expected Size**: Grows linearly with task count
- **Typical Throughput**: 200-400 tasks/minute

### Maintenance Goals

- **Data Protection**: Regular backups with retention policy
- **Performance**: Optimize query planner and reclaim free space
- **Reliability**: Monitor database health and clean up stale data
- **Recovery**: Quick restoration from backups when needed

---

## Quick Reference

### Common Commands

```python
from Client.Backend.src.queue import QueueDatabase, QueueBackup, QueueMaintenance

# Initialize
db = QueueDatabase()
backup = QueueBackup(db)
maint = QueueMaintenance(db)

# Backup
backup_path = backup.create_backup()  # Create backup
backup.verify_backup(backup_path)     # Verify integrity

# Maintenance
maint.checkpoint()                    # Checkpoint WAL
maint.analyze()                       # Update statistics (fast)
maint.cleanup_stale_leases()          # Clean expired leases
maint.optimize(full=False)            # Quick optimization

# Stats
stats = maint.get_database_stats()    # Get database metrics
backups = backup.list_backups()       # List available backups
```

### Recommended Schedule

| Operation | Frequency | Duration | Impact |
|-----------|-----------|----------|--------|
| Backup | Daily | <10s | None (non-blocking) |
| ANALYZE | Daily | <5s | None (non-blocking) |
| Checkpoint | Automatic | <1s | Low (non-blocking) |
| Cleanup Stale Leases | Hourly | <1s | None |
| VACUUM | Weekly | 1-5min | High (blocks writes) |
| Integrity Check | Weekly | <30s | Low |

---

## Backup Procedures

### Creating a Backup

**Purpose**: Create a consistent point-in-time copy of the database

**Frequency**: Daily (recommended), before major operations

**Steps**:

```python
from Client.Backend.src.queue import QueueDatabase, QueueBackup

# 1. Initialize
db = QueueDatabase()
backup = QueueBackup(db)

# 2. Create backup
backup_path = backup.create_backup(name="daily")
print(f"Backup created: {backup_path}")

# 3. Verify backup
is_valid = backup.verify_backup(backup_path)
print(f"Backup valid: {is_valid}")

# 4. List all backups
backups = backup.list_backups()
for b in backups:
    print(f"  {b.path.name} - {b.size_mb:.2f} MB - {b.created_at}")
```

**Expected Output**:
```
Backup created: C:\Data\PrismQ\queue\backups\queue_backup_daily_20251105_143022.db
Backup valid: True
  queue_backup_daily_20251105_143022.db - 2.45 MB - 2025-11-05 14:30:22
```

**Notes**:
- Backups are non-blocking and can run while database is in use
- Backup includes entire database state (tasks, workers, logs)
- Typical backup time: <10 seconds for databases up to 100MB

### Automated Backup Script

Save as `scripts/backup_queue.py`:

```python
#!/usr/bin/env python3
"""Daily backup script for SQLite queue database."""

import sys
from datetime import datetime
from pathlib import Path

# Add Client/Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Client" / "Backend"))

from src.queue import QueueDatabase, QueueBackup

def main():
    # Initialize
    db = QueueDatabase()
    backup = QueueBackup(db)
    
    # Create backup
    print(f"[{datetime.now()}] Starting daily backup...")
    try:
        backup_path = backup.create_backup(name="daily")
        print(f"[{datetime.now()}] Backup created: {backup_path}")
        
        # Verify
        is_valid = backup.verify_backup(backup_path)
        if not is_valid:
            print(f"[{datetime.now()}] ERROR: Backup verification failed!")
            return 1
        
        print(f"[{datetime.now()}] Backup verified successfully")
        
        # Cleanup old backups (keep last 10)
        deleted = backup.cleanup_old_backups(keep_count=10)
        print(f"[{datetime.now()}] Cleaned up {deleted} old backups")
        
        # List current backups
        backups = backup.list_backups()
        print(f"[{datetime.now()}] Total backups: {len(backups)}")
        
        return 0
        
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
```

Run via Task Scheduler (Windows):
```powershell
# Create scheduled task for daily backup at 2 AM
schtasks /create /tn "PrismQ Queue Backup" /tr "python C:\Path\To\scripts\backup_queue.py" /sc daily /st 02:00
```

### Backup Retention Policy

**Default Policy**: Keep last 10 backups

**Customization**:

```python
# Keep last 30 backups
backup.cleanup_old_backups(keep_count=30)

# Keep 7 daily + 4 weekly (manual script)
# Implement custom retention logic based on backup age
```

**Considerations**:
- Each backup is ~same size as database
- Monitor disk space if database is large
- Older backups can be archived to cheaper storage

---

## Restore Procedures

### Restoring from Backup

**Purpose**: Recover database from a previous backup

**When to Use**:
- Database corruption detected
- Accidental data deletion
- Testing or development setup

**Steps**:

```python
from Client.Backend.src.queue import QueueDatabase, QueueBackup
from pathlib import Path

# 1. Initialize (use temporary location for testing)
db = QueueDatabase()
backup = QueueBackup(db)

# 2. List available backups
backups = backup.list_backups()
for i, b in enumerate(backups):
    print(f"{i}: {b.path.name} - {b.created_at}")

# 3. Select backup to restore
selected_backup = backups[0].path  # Latest backup

# 4. IMPORTANT: Close database before restoring
db.close()

# 5. Restore
print(f"Restoring from: {selected_backup}")
backup.restore_backup(selected_backup)
print("Restore complete!")

# 6. Verify restored database
db2 = QueueDatabase()
results = QueueMaintenance(db2).integrity_check()
print(f"Integrity check: {results}")
db2.close()
```

**Warning**: Restore will **overwrite** the current database!

### Emergency Restore Procedure

If database is corrupted and Python is unavailable:

1. **Stop the application** (ensure no processes are using the database)

2. **Manual file copy** (PowerShell):
   ```powershell
   # Backup current (corrupted) database
   Copy-Item C:\Data\PrismQ\queue\queue.db C:\Data\PrismQ\queue\queue.db.corrupted
   
   # Find latest backup
   Get-ChildItem C:\Data\PrismQ\queue\backups\queue_backup_*.db | Sort-Object LastWriteTime -Descending | Select-Object -First 1
   
   # Restore from backup
   Copy-Item C:\Data\PrismQ\queue\backups\queue_backup_YYYYMMDD_HHMMSS.db C:\Data\PrismQ\queue\queue.db -Force
   ```

3. **Verify with SQLite CLI**:
   ```bash
   sqlite3 C:\Data\PrismQ\queue\queue.db "PRAGMA integrity_check;"
   ```

4. **Restart the application**

---

## Maintenance Operations

### WAL Checkpoint

**Purpose**: Merge WAL file back into main database file

**Modes**:
- **PASSIVE** (default): Non-blocking, checkpoints what's possible
- **FULL**: Blocks readers until WAL is checkpointed
- **RESTART**: Like FULL, also resets WAL
- **TRUNCATE**: Like RESTART, also truncates WAL to 0 bytes

**Usage**:

```python
from Client.Backend.src.queue import QueueDatabase, QueueMaintenance

db = QueueDatabase()
maint = QueueMaintenance(db)

# Passive checkpoint (non-blocking)
result = maint.checkpoint(mode=QueueMaintenance.CHECKPOINT_PASSIVE)
print(f"Checkpoint result: {result}")

# Full checkpoint (blocks readers)
result = maint.checkpoint(mode=QueueMaintenance.CHECKPOINT_FULL)
print(f"Pages written: {result['log']}, checkpointed: {result['checkpointed']}")

db.close()
```

**When to Use**:
- PASSIVE: Automatic, runs periodically
- FULL: Before VACUUM or when WAL is too large
- TRUNCATE: To reset WAL file size

### VACUUM Operation

**Purpose**: Reclaim free space and defragment database

**Impact**: **HIGH** - Blocks all writes, can take 1-5 minutes

**Usage**:

```python
from Client.Backend.src.queue import QueueDatabase, QueueMaintenance

db = QueueDatabase()
maint = QueueMaintenance(db)

# Get stats before VACUUM
stats_before = maint.get_database_stats()
print(f"Before: {stats_before['total_size_mb']:.2f} MB, {stats_before['freelist_count']} free pages")

# Run VACUUM (blocking operation)
print("Running VACUUM (this may take a few minutes)...")
maint.vacuum()

# Get stats after VACUUM
stats_after = maint.get_database_stats()
print(f"After: {stats_after['total_size_mb']:.2f} MB, {stats_after['freelist_count']} free pages")

db.close()
```

**When to Use**:
- Weekly during maintenance window
- After large DELETE operations
- When free pages > 20% of database

**Alternatives**:
- Enable `auto_vacuum` in PRAGMA (trades space for performance)
- Run during off-peak hours or maintenance windows

### ANALYZE Operation

**Purpose**: Update query planner statistics for better performance

**Impact**: LOW - Non-blocking, fast (<5 seconds)

**Usage**:

```python
from Client.Backend.src.queue import QueueDatabase, QueueMaintenance

db = QueueDatabase()
maint = QueueMaintenance(db)

# Analyze all tables
maint.analyze()

# Analyze specific table
maint.analyze(table="task_queue")

db.close()
```

**When to Use**:
- Daily (recommended)
- After large data changes
- After schema changes

### Stale Lease Cleanup

**Purpose**: Requeue tasks with expired leases (crashed workers)

**Impact**: None - Safe, atomic operation

**Usage**:

```python
from Client.Backend.src.queue import QueueDatabase, QueueMaintenance

db = QueueDatabase()
maint = QueueMaintenance(db)

# Cleanup leases expired more than 5 minutes ago
count = maint.cleanup_stale_leases(timeout_seconds=300)
print(f"Requeued {count} tasks with stale leases")

db.close()
```

**When to Use**:
- Hourly (recommended)
- After worker crashes
- When tasks appear stuck

**Timeout Recommendations**:
- Normal operations: 300 seconds (5 minutes)
- Long-running tasks: 600-1800 seconds (10-30 minutes)

### Combined Optimization

**Purpose**: Run multiple maintenance operations together

**Usage**:

```python
from Client.Backend.src.queue import QueueDatabase, QueueMaintenance

db = QueueDatabase()
maint = QueueMaintenance(db)

# Quick optimization (ANALYZE only)
result = maint.optimize(full=False)
print(f"Quick optimization: analyzed={result['analyzed']}")

# Full optimization (ANALYZE + VACUUM)
result = maint.optimize(full=True)
print(f"Full optimization: analyzed={result['analyzed']}, vacuumed={result['vacuumed']}")
print(f"Size before: {result['stats_before']['total_size_mb']:.2f} MB")
print(f"Size after: {result['stats_after']['total_size_mb']:.2f} MB")

db.close()
```

---

## Monitoring and Health Checks

### Database Statistics

```python
from Client.Backend.src.queue import QueueDatabase, QueueMaintenance

db = QueueDatabase()
maint = QueueMaintenance(db)

stats = maint.get_database_stats()

print(f"Database Size: {stats['total_size_mb']:.2f} MB")
print(f"Page Count: {stats['page_count']}")
print(f"Page Size: {stats['page_size']} bytes")
print(f"Free Pages: {stats['freelist_count']}")
print(f"WAL Mode: {stats['wal_mode']}")
print(f"WAL Size: {stats['wal_size_mb']:.2f} MB")

# Calculate fragmentation
fragmentation_pct = (stats['freelist_count'] / stats['page_count']) * 100
print(f"Fragmentation: {fragmentation_pct:.1f}%")

db.close()
```

### Health Check Script

```python
"""Queue database health check."""

def check_queue_health():
    db = QueueDatabase()
    maint = QueueMaintenance(db)
    
    # 1. Integrity check
    results = maint.integrity_check()
    if results != ["ok"]:
        print(f"CRITICAL: Integrity check failed: {results}")
        return False
    
    # 2. Check database size
    stats = maint.get_database_stats()
    if stats['total_size_mb'] > 1000:  # 1 GB threshold
        print(f"WARNING: Database size is {stats['total_size_mb']:.2f} MB")
    
    # 3. Check WAL size
    if stats['wal_size_mb'] > 100:  # 100 MB threshold
        print(f"WARNING: WAL size is {stats['wal_size_mb']:.2f} MB - consider checkpoint")
    
    # 4. Check fragmentation
    fragmentation = (stats['freelist_count'] / stats['page_count']) * 100
    if fragmentation > 20:
        print(f"WARNING: Fragmentation is {fragmentation:.1f}% - consider VACUUM")
    
    # 5. Clean stale leases
    stale_count = maint.cleanup_stale_leases()
    if stale_count > 0:
        print(f"INFO: Cleaned up {stale_count} stale leases")
    
    print("Health check PASSED")
    db.close()
    return True
```

### Metrics to Monitor

| Metric | Warning Threshold | Critical Threshold | Action |
|--------|-------------------|-------------------|--------|
| Database Size | >500 MB | >1 GB | Consider archiving old data |
| WAL Size | >50 MB | >100 MB | Run checkpoint |
| Fragmentation | >10% | >20% | Run VACUUM |
| Stale Leases | >10 | >50 | Investigate worker issues |
| Free Disk Space | <10 GB | <5 GB | Clean up backups/logs |

---

## Troubleshooting

### Problem: Database Locked Errors

**Symptoms**: `sqlite3.OperationalError: database is locked`

**Causes**:
- WAL mode not enabled
- Insufficient busy_timeout
- Long-running VACUUM operation

**Solutions**:

1. Verify WAL mode:
   ```python
   cursor = conn.execute("PRAGMA journal_mode")
   print(cursor.fetchone()[0])  # Should be "wal"
   ```

2. Check busy_timeout:
   ```python
   cursor = conn.execute("PRAGMA busy_timeout")
   print(cursor.fetchone()[0])  # Should be 5000
   ```

3. Avoid VACUUM during peak hours

See also: [SQLITE_QUEUE_TROUBLESHOOTING.md](./SQLITE_QUEUE_TROUBLESHOOTING.md#issue-database-is-locked)

### Problem: Backup Fails

**Symptoms**: `QueueBackupError: Backup failed`

**Causes**:
- Insufficient disk space
- Permission issues
- Database corruption

**Solutions**:

1. Check disk space:
   ```powershell
   Get-PSDrive C | Select-Object Used,Free
   ```

2. Verify permissions:
   ```powershell
   icacls C:\Data\PrismQ\queue\backups
   ```

3. Run integrity check:
   ```python
   results = maint.integrity_check()
   print(results)  # Should be ["ok"]
   ```

### Problem: VACUUM Takes Too Long

**Symptoms**: VACUUM blocks database for >10 minutes

**Causes**:
- Database is very large
- High fragmentation
- Slow disk I/O

**Solutions**:

1. Use `optimize(full=False)` instead (ANALYZE only)
2. Schedule VACUUM during maintenance windows
3. Consider incremental vacuuming with `auto_vacuum`

### Problem: Stale Leases Not Cleaned

**Symptoms**: Tasks stuck in "processing" state

**Causes**:
- Lease timeout too short
- Workers crashed without cleanup
- Clock skew between servers

**Solutions**:

1. Increase timeout:
   ```python
   maint.cleanup_stale_leases(timeout_seconds=600)  # 10 minutes
   ```

2. Check worker logs for crashes

3. Verify system time is synchronized

---

## Maintenance Schedule

### Daily Tasks (Automated)

**Time**: 2:00 AM  
**Duration**: <1 minute  
**Script**: `scripts/daily_maintenance.py`

```python
# Daily maintenance script
db = QueueDatabase()
backup = QueueBackup(db)
maint = QueueMaintenance(db)

# 1. Create backup
backup_path = backup.create_backup(name="daily")
backup.verify_backup(backup_path)
backup.cleanup_old_backups(keep_count=10)

# 2. Quick optimization
maint.analyze()
maint.checkpoint()

# 3. Cleanup
maint.cleanup_stale_leases()

db.close()
```

### Weekly Tasks (Manual)

**Time**: Saturday 2:00 AM  
**Duration**: 5-10 minutes  
**Steps**:

1. Stop application (optional, for safety)
2. Create backup
3. Run integrity check
4. Run VACUUM
5. Verify database
6. Restart application

```python
# Weekly maintenance script
db = QueueDatabase()
backup = QueueBackup(db)
maint = QueueMaintenance(db)

# 1. Backup
backup_path = backup.create_backup(name="weekly")

# 2. Integrity check
results = maint.integrity_check()
assert results == ["ok"], f"Integrity check failed: {results}"

# 3. Full optimization
result = maint.optimize(full=True)
print(f"Size reduced: {result['stats_before']['total_size_mb'] - result['stats_after']['total_size_mb']:.2f} MB")

db.close()
```

### Hourly Tasks (Automated)

**Script**: Run via cron/Task Scheduler

```python
# Hourly maintenance script
db = QueueDatabase()
maint = QueueMaintenance(db)

# Cleanup stale leases
count = maint.cleanup_stale_leases(timeout_seconds=300)
if count > 0:
    print(f"Cleaned {count} stale leases")

db.close()
```

---

## References

- [SQLite Backup API Documentation](https://www.sqlite.org/backup.html)
- [SQLite WAL Mode](https://www.sqlite.org/wal.html)
- [VACUUM Command](https://www.sqlite.org/lang_vacuum.html)
- [ANALYZE Command](https://www.sqlite.org/lang_analyze.html)
- Issue #331: Database Maintenance and Backup
- Issue #337: SQLite Concurrency Tuning Research
- `Client/Backend/src/queue/README.md` - Queue module documentation
- `_meta/docs/SQLITE_QUEUE_TROUBLESHOOTING.md` - Troubleshooting guide

---

**Last Updated**: 2025-11-05  
**Version**: 1.0  
**Maintainer**: Worker 06 - DevOps Engineer
