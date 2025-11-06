# SQLite Queue System - Configuration Guide

**Version**: 1.0  
**Status**: Phase 1 Implementation  
**Created**: 2025-11-05  
**Last Updated**: 2025-11-05

---

## Table of Contents

- [Overview](#overview)
- [Database Configuration](#database-configuration)
- [PRAGMA Settings](#pragma-settings)
- [Environment Variables](#environment-variables)
- [Platform-Specific Configuration](#platform-specific-configuration)
- [Performance Tuning](#performance-tuning)
- [Production Recommendations](#production-recommendations)

---

## Overview

The SQLite Queue System is designed to work out-of-the-box with sensible defaults optimized for Windows platform. This guide covers configuration options for different use cases and environments.

**Default Configuration**:
- **Database Location**: `C:\Data\PrismQ\queue\queue.db` (Windows)
- **Journal Mode**: WAL (Write-Ahead Logging)
- **Synchronous**: NORMAL (balanced durability/performance)
- **Busy Timeout**: 5000ms (5 seconds)
- **Cache Size**: ~20MB

---

## Database Configuration

### Database Location

**Default Paths**:

| Platform | Default Path |
|----------|--------------|
| **Windows** | `C:\Data\PrismQ\queue\queue.db` |
| **Linux** | `/tmp/prismq/queue/queue.db` |
| **macOS** | `/tmp/prismq/queue/queue.db` |

**Custom Path** (via environment variable):

```bash
# Windows (PowerShell)
$env:PRISMQ_QUEUE_DB_PATH = "D:\Data\queue\queue.db"

# Windows (Command Prompt)
set PRISMQ_QUEUE_DB_PATH=D:\Data\queue\queue.db

# Linux/macOS (bash)
export PRISMQ_QUEUE_DB_PATH=/var/lib/prismq/queue/queue.db
```

**Custom Path** (via code):

```python
from queue import QueueDatabase

# Explicit path
db = QueueDatabase(db_path="C:/custom/path/queue.db")

# Relative path (not recommended for production)
db = QueueDatabase(db_path="./data/queue.db")
```

### Storage Requirements

**Disk Space**:
- **Base Database**: ~100KB empty, grows with tasks
- **WAL File**: Typically 2-10MB (auto-checkpointed at 1000 pages)
- **Estimate**: ~10KB per 1000 tasks (with moderate payload size)

**Example Calculations**:
```
1,000 tasks   = ~10KB
10,000 tasks  = ~100KB
100,000 tasks = ~1MB
1,000,000 tasks = ~10MB (plus WAL ~2-5MB)
```

**Recommendations**:
- **Minimum**: 100MB free space
- **Recommended**: 1GB free space (allows growth + checkpoints)
- **Maintenance**: Run VACUUM monthly if deleting many tasks

---

## PRAGMA Settings

### Windows-Optimized Defaults

The following PRAGMAs are automatically applied on connection:

```python
PRAGMAS = {
    'journal_mode': 'WAL',           # Write-Ahead Logging
    'synchronous': 'NORMAL',         # Balance durability vs performance
    'busy_timeout': 5000,            # 5 seconds for lock retries
    'wal_autocheckpoint': 1000,      # Checkpoint every 1000 pages
    'foreign_keys': 'ON',            # Enable FK constraints
    'temp_store': 'MEMORY',          # Temp tables in memory
    'mmap_size': 134217728,          # 128MB memory-mapped I/O
    'page_size': 4096,               # Match filesystem block size
    'cache_size': -20000,            # ~20MB cache (negative = KiB)
}
```

### PRAGMA Explanations

#### journal_mode = WAL

**Purpose**: Enable Write-Ahead Logging for concurrency

**Options**:
- `DELETE`: Traditional rollback journal (default SQLite)
- `WAL`: Write-Ahead Logging (recommended)
- `TRUNCATE`: Like DELETE but truncates journal
- `PERSIST`: Like DELETE but persists journal
- `MEMORY`: Memory-only journal (not durable)
- `OFF`: No journal (dangerous!)

**Why WAL?**
- ✅ Concurrent reads during writes
- ✅ Reduces transaction overhead (30ms → <1ms)
- ✅ Better write throughput
- ⚠️ Requires periodic checkpoints
- ⚠️ Slightly larger disk usage

**Trade-offs**:
```
WAL Mode:
  + Concurrency: Unlimited readers
  + Performance: <1ms transactions
  - Checkpoint: Periodic maintenance needed
  - Disk: WAL file + main database

DELETE Mode:
  + Simplicity: Single file
  + Compatibility: All platforms
  - Performance: 30ms transactions
  - Concurrency: Readers blocked during writes
```

**When to Use DELETE Mode**:
- Very low write frequency (<10 writes/min)
- Single-user application
- Network file systems (NFS, SMB) - WAL not recommended

#### synchronous = NORMAL

**Purpose**: Balance between durability and performance

**Options**:
- `OFF`: No sync (fastest, **data loss risk**)
- `NORMAL`: Sync at critical moments (recommended)
- `FULL`: Sync after every write (safest, slowest)
- `EXTRA`: Like FULL + additional sync

**Durability Guarantees**:

| Mode | Power Loss | OS Crash | App Crash | Performance |
|------|-----------|----------|-----------|-------------|
| `OFF` | ❌ Data loss | ❌ Data loss | ✅ Safe | ⚡ Fastest |
| `NORMAL` | ❌ Possible corruption | ✅ Safe | ✅ Safe | ⚡ Fast |
| `FULL` | ✅ Safe | ✅ Safe | ✅ Safe | 🐌 Slow |

**Recommendation**:
- **Development**: `NORMAL` (balanced)
- **Production**: `NORMAL` (with UPS) or `FULL` (without UPS)
- **Testing**: `OFF` (speed over durability)

**Production Considerations**:
```python
# With UPS (Uninterruptible Power Supply)
PRAGMA synchronous = NORMAL  # Safe + Fast

# Without UPS
PRAGMA synchronous = FULL  # Safe but slower
```

#### busy_timeout = 5000

**Purpose**: How long to wait when database is locked

**Value**: Milliseconds (5000 = 5 seconds)

**Why 5 seconds?**
- Windows file locking is slower than POSIX
- Prevents spurious SQLITE_BUSY errors
- Allows multiple workers time to acquire locks

**Adjustment Guidelines**:

```python
# Low contention (1-2 workers)
PRAGMA busy_timeout = 2000  # 2 seconds

# Medium contention (3-5 workers)
PRAGMA busy_timeout = 5000  # 5 seconds (default)

# High contention (6+ workers)
PRAGMA busy_timeout = 10000  # 10 seconds
```

**Monitoring**:
```sql
-- Check if busy_timeout is sufficient
-- If SQLITE_BUSY errors occur frequently, increase timeout
SELECT COUNT(*) FROM task_queue  -- If this times out, increase timeout
```

#### wal_autocheckpoint = 1000

**Purpose**: Automatically checkpoint WAL every N pages

**Value**: Pages (1000 = ~4MB with 4KB pages)

**Why 1000 pages?**
- Prevents WAL from growing too large
- Balances checkpoint frequency vs performance
- ~4MB WAL size before checkpoint

**Adjustment Guidelines**:

```python
# Low write frequency (<50 writes/min)
PRAGMA wal_autocheckpoint = 500  # Checkpoint more often

# High write frequency (>500 writes/min)
PRAGMA wal_autocheckpoint = 2000  # Less frequent checkpoints
```

**Manual Checkpoint** (future: Issue #331):
```python
# Periodic checkpoint (e.g., nightly maintenance)
db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
```

#### foreign_keys = ON

**Purpose**: Enable foreign key constraint checking

**Why ON?**
- ✅ Data integrity (prevent orphaned logs)
- ✅ Referential integrity enforcement
- ⚠️ Slight performance overhead on deletes

**Example**:
```sql
-- With foreign_keys = ON
DELETE FROM task_queue WHERE id = 1;
-- Also deletes related task_logs (CASCADE)

-- With foreign_keys = OFF
DELETE FROM task_queue WHERE id = 1;
-- Leaves orphaned task_logs (data inconsistency)
```

#### temp_store = MEMORY

**Purpose**: Store temporary tables in memory vs disk

**Options**:
- `DEFAULT`: Use compile-time default (usually FILE)
- `FILE`: Temporary tables on disk
- `MEMORY`: Temporary tables in memory (recommended)

**Why MEMORY?**
- ✅ Faster temporary table operations
- ✅ No disk I/O for temp tables
- ⚠️ Uses RAM (not an issue with 64GB)

**Trade-off**:
```
MEMORY:
  + Speed: Fast temp table operations
  + I/O: No disk writes
  - RAM: Uses memory (negligible with 64GB)

FILE:
  + RAM: No memory usage
  - Speed: Disk I/O overhead
  - SSD: Extra wear on SSD
```

#### mmap_size = 134217728

**Purpose**: Memory-mapped I/O size (128MB)

**Value**: Bytes (134217728 = 128MB)

**Why 128MB?**
- Maps database file into memory
- Reduces system calls on Windows
- Improves read performance

**Adjustment Guidelines**:

```python
# Small database (<10MB)
PRAGMA mmap_size = 33554432  # 32MB

# Medium database (10-100MB)
PRAGMA mmap_size = 134217728  # 128MB (default)

# Large database (>100MB)
PRAGMA mmap_size = 268435456  # 256MB

# Disable (if issues)
PRAGMA mmap_size = 0
```

**Platform Notes**:
- Works well on Windows 10/11
- Not recommended for 32-bit systems
- May cause issues on network file systems

#### page_size = 4096

**Purpose**: Database page size

**Value**: Bytes (4096 = 4KB)

**Why 4096?**
- Matches NTFS allocation unit size (Windows)
- Optimal for SSD I/O
- Balance between overhead and efficiency

**⚠️ Important**: Can only be set **before** database creation

```python
# Must set BEFORE creating tables
db.execute("PRAGMA page_size = 4096")
db.initialize_schema()  # Now page size is locked
```

**Adjustment Guidelines**:

```python
# Small records (<100 bytes)
PRAGMA page_size = 1024  # 1KB (more overhead, less waste)

# Medium records (100-1000 bytes)
PRAGMA page_size = 4096  # 4KB (default, recommended)

# Large records (>1000 bytes, e.g., large JSON payloads)
PRAGMA page_size = 8192  # 8KB (less overhead, more waste)
```

#### cache_size = -20000

**Purpose**: Page cache size

**Value**: 
- **Positive**: Number of pages (e.g., 2000 = 2000 pages)
- **Negative**: KiB (e.g., -20000 = ~20MB)

**Why -20000 (20MB)?**
- Large cache improves query performance
- 20MB is negligible with 64GB RAM
- Reduces disk I/O

**Adjustment Guidelines**:

```python
# Low RAM (<4GB) - Use smaller cache
PRAGMA cache_size = -5000  # ~5MB

# Medium RAM (4-16GB) - Moderate cache
PRAGMA cache_size = -10000  # ~10MB

# High RAM (>16GB) - Large cache (default)
PRAGMA cache_size = -20000  # ~20MB

# Very high RAM (>32GB) - Extra large cache
PRAGMA cache_size = -50000  # ~50MB
```

**Formula**:
```
Negative value = KiB
cache_size = -(desired_MB * 1024)

Example:
  50MB cache = -(50 * 1024) = -51200
```

---

## Environment Variables

### PRISMQ_QUEUE_DB_PATH

**Purpose**: Override default database path

**Examples**:

```bash
# Windows - PowerShell
$env:PRISMQ_QUEUE_DB_PATH = "D:\Data\queue\queue.db"

# Windows - Command Prompt
set PRISMQ_QUEUE_DB_PATH=D:\Data\queue\queue.db

# Linux/macOS
export PRISMQ_QUEUE_DB_PATH=/var/lib/prismq/queue/queue.db

# Python
import os
os.environ["PRISMQ_QUEUE_DB_PATH"] = "/custom/path/queue.db"
```

**Usage in Code**:
```python
# Automatically uses PRISMQ_QUEUE_DB_PATH if set
db = QueueDatabase()

# Or explicitly
db_path = os.getenv("PRISMQ_QUEUE_DB_PATH", default_path)
db = QueueDatabase(db_path)
```

### Future Environment Variables (Phase 2-3)

```bash
# Worker configuration
PRISMQ_QUEUE_WORKER_ID=worker-01
PRISMQ_QUEUE_LEASE_DURATION=300  # 5 minutes
PRISMQ_QUEUE_MAX_WORKERS=8

# Scheduling
PRISMQ_QUEUE_STRATEGY=priority  # fifo, lifo, priority, weighted

# Observability
PRISMQ_QUEUE_LOG_LEVEL=INFO
PRISMQ_QUEUE_METRICS_ENABLED=true
```

---

## Platform-Specific Configuration

### Windows (Primary Platform)

**Optimizations**:
- `page_size=4096`: Matches NTFS allocation unit
- `busy_timeout=5000`: Windows file locking is slower
- `mmap_size=128MB`: Memory-mapped I/O performs well

**SSD vs HDD**:

```python
# SSD (Recommended)
PRAGMAS = {
    'synchronous': 'NORMAL',  # Fast fsync
    'page_size': 4096,        # NTFS optimal
    'mmap_size': 134217728,   # Memory-mapped I/O
}

# HDD (Not recommended for queue)
PRAGMAS = {
    'synchronous': 'FULL',    # Slower, ensure durability
    'page_size': 8192,        # Larger pages for sequential reads
    'mmap_size': 0,           # Disable mmap on HDD
}
```

**Antivirus Considerations**:

```
1. Exclude database directory from real-time scanning:
   C:\Data\PrismQ\queue\

2. If performance issues persist, disable for process:
   Add pythonw.exe to antivirus exclusions

3. Monitor SQLITE_BUSY errors:
   If frequent, antivirus may be locking files
```

### Linux/macOS (Development/Testing)

**Optimizations**:
- `page_size=4096`: Common ext4/APFS block size
- `busy_timeout=2000`: POSIX file locking is faster
- `synchronous=NORMAL`: Good for development

**Docker Considerations**:

```yaml
# docker-compose.yml
services:
  queue_worker:
    volumes:
      # Use named volume for persistence
      - queue_data:/var/lib/prismq/queue
    environment:
      PRISMQ_QUEUE_DB_PATH: /var/lib/prismq/queue/queue.db

volumes:
  queue_data:
```

---

## Performance Tuning

### Workload-Specific Tuning

#### Low Throughput (<100 tasks/min)

```python
PRAGMAS = {
    'journal_mode': 'WAL',
    'synchronous': 'FULL',         # Extra safety
    'busy_timeout': 2000,          # Low contention
    'wal_autocheckpoint': 500,     # Checkpoint often
    'cache_size': -10000,          # 10MB cache
}
```

#### Medium Throughput (100-500 tasks/min) - **Default**

```python
PRAGMAS = {
    'journal_mode': 'WAL',
    'synchronous': 'NORMAL',       # Balanced
    'busy_timeout': 5000,          # Medium contention
    'wal_autocheckpoint': 1000,    # Default checkpoint
    'cache_size': -20000,          # 20MB cache
}
```

#### High Throughput (>500 tasks/min)

```python
PRAGMAS = {
    'journal_mode': 'WAL',
    'synchronous': 'NORMAL',       # Still safe with UPS
    'busy_timeout': 10000,         # High contention
    'wal_autocheckpoint': 2000,    # Less frequent checkpoints
    'cache_size': -50000,          # 50MB cache
}
```

### Concurrent Workers Tuning

```python
# 1-2 workers
busy_timeout = 2000

# 3-5 workers (default)
busy_timeout = 5000

# 6-8 workers
busy_timeout = 10000

# 9+ workers - Consider PostgreSQL migration
# SQLite may struggle with >8 concurrent writers
```

### Index Optimization

**Current Indexes** (optimized for claiming):

```sql
-- Primary index for task claiming
CREATE INDEX ix_task_status_prio_time
  ON task_queue (status, priority, run_after_utc, id);

-- Query plan (uses index):
SELECT * FROM task_queue
WHERE status = 'queued'
  AND run_after_utc <= datetime('now')
ORDER BY priority ASC, run_after_utc ASC
LIMIT 1;
```

**Verify Index Usage**:

```sql
EXPLAIN QUERY PLAN
SELECT * FROM task_queue
WHERE status = 'queued'
ORDER BY priority, run_after_utc
LIMIT 1;
-- Should show: SEARCH task_queue USING INDEX ix_task_status_prio_time
```

---

## Production Recommendations

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4GB | 8GB+ |
| **Storage** | HDD | **NVMe SSD** |
| **Free Space** | 100MB | 1GB+ |

### Deployment Checklist

- [ ] **Database on local SSD** (never network share)
- [ ] **Adequate free space** (>1GB for growth)
- [ ] **Antivirus exclusions** (database directory)
- [ ] **UPS or synchronous=FULL** (power loss protection)
- [ ] **Backup strategy** (daily backups)
- [ ] **Monitoring** (SQLITE_BUSY errors, throughput)
- [ ] **Maintenance** (monthly VACUUM if needed)

### Monitoring Metrics

```sql
-- Database size
SELECT page_count * page_size / 1024 / 1024 AS size_mb
FROM pragma_page_count(), pragma_page_size();

-- WAL size
SELECT name, size / 1024 / 1024 AS size_mb
FROM pragma_database_list()
WHERE name = 'main';

-- Task counts by status
SELECT status, COUNT(*) AS count
FROM task_queue
GROUP BY status;

-- Average attempts
SELECT AVG(attempts) AS avg_attempts
FROM task_queue
WHERE status IN ('completed', 'failed');
```

### Backup Strategy

```python
# Online backup (SQLite API)
import sqlite3

def backup_database(source_path, dest_path):
    """Perform online backup without locking."""
    source = sqlite3.connect(source_path)
    dest = sqlite3.connect(dest_path)
    
    with dest:
        source.backup(dest)
    
    source.close()
    dest.close()

# Daily backup
backup_database(
    "C:/Data/PrismQ/queue/queue.db",
    "C:/Backups/PrismQ/queue/queue-{date}.db"
)
```

### Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| **Checkpoint** | Nightly | `PRAGMA wal_checkpoint(TRUNCATE)` |
| **VACUUM** | Monthly | `VACUUM` (if many deletes) |
| **Backup** | Daily | SQLite online backup |
| **Analyze** | Weekly | `ANALYZE` (update statistics) |

---

## Troubleshooting

### Common Issues

#### SQLITE_BUSY Errors

**Symptoms**: `QueueBusyError` exceptions

**Solutions**:
1. Increase `busy_timeout` (5000 → 10000)
2. Reduce concurrent workers (8 → 4)
3. Check antivirus (exclude database directory)
4. Verify database is on local SSD (not network)

#### Slow Queries

**Symptoms**: Task claiming takes >100ms

**Solutions**:
1. Increase `cache_size` (20MB → 50MB)
2. Run `ANALYZE` to update statistics
3. Verify index usage (EXPLAIN QUERY PLAN)
4. Check disk I/O (SSD recommended)

#### Large WAL File

**Symptoms**: WAL file >100MB

**Solutions**:
1. Decrease `wal_autocheckpoint` (1000 → 500)
2. Manual checkpoint: `PRAGMA wal_checkpoint(TRUNCATE)`
3. Check for long-running readers blocking checkpoint

---

**Document Version**: 1.0  
**Phase**: Phase 1 - Core Infrastructure  
**Status**: Complete  
**Next**: Update with production tuning from #337 benchmarks
