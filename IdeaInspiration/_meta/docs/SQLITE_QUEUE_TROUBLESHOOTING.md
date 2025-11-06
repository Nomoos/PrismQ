# SQLite Queue Troubleshooting Guide

**Version**: 1.0  
**Date**: 2025-11-05  
**Related**: Issue #337 - SQLite Concurrency Research  
**Platform**: Windows 10/11 with NVIDIA RTX 5090

---

## Table of Contents

1. [Common Issues](#common-issues)
2. [Performance Degradation](#performance-degradation)
3. [SQLITE_BUSY Errors](#sqlite_busy-errors)
4. [Checkpoint Blocking](#checkpoint-blocking)
5. [Database Corruption](#database-corruption)
6. [Recovery Procedures](#recovery-procedures)
7. [Monitoring & Diagnostics](#monitoring--diagnostics)
8. [Windows-Specific Issues](#windows-specific-issues)

---

## Common Issues

### Issue: Database File Not Found

**Symptoms**:
```
sqlite3.OperationalError: unable to open database file
```

**Causes**:
- Database directory doesn't exist
- Incorrect file path
- Permission issues

**Solutions**:

```python
from pathlib import Path

# Ensure directory exists
db_path = r"C:\Data\PrismQ\queue\queue.db"
Path(db_path).parent.mkdir(parents=True, exist_ok=True)

# Verify path is accessible
assert Path(db_path).parent.exists(), f"Directory does not exist: {Path(db_path).parent}"
```

**Prevention**:
- Use `ensure_db_directory()` from `config.py` before creating connection
- Always use absolute paths, not relative paths

---

### Issue: Database is Locked

**Symptoms**:
```
sqlite3.OperationalError: database is locked
```

**Causes**:
- Another process has exclusive lock
- Previous connection not closed properly
- WAL mode not enabled
- Insufficient `busy_timeout`

**Solutions**:

1. **Check WAL mode is enabled**:
```python
conn = sqlite3.connect(db_path)
cursor = conn.execute("PRAGMA journal_mode")
mode = cursor.fetchone()[0]
print(f"Journal mode: {mode}")  # Should be "wal"

if mode != 'wal':
    conn.execute("PRAGMA journal_mode=WAL")
    conn.commit()
```

2. **Increase busy_timeout**:
```python
conn.execute("PRAGMA busy_timeout=5000")  # 5 seconds
```

3. **Use context managers to ensure cleanup**:
```python
# BAD - connection may not close on error
conn = sqlite3.connect(db_path)
conn.execute(...)
conn.close()

# GOOD - automatically closes
with sqlite3.connect(db_path) as conn:
    conn.execute(...)
```

4. **Check for orphaned connections**:
```bash
# On Windows, check for processes holding the database file
handle.exe "C:\Data\PrismQ\queue\queue.db"

# Or use Process Explorer to find which process has the file open
```

**Prevention**:
- Always enable WAL mode
- Set appropriate `busy_timeout` (5000ms recommended)
- Use context managers for all database connections
- Ensure all connections are properly closed

---

### Issue: WAL File Growing Too Large

**Symptoms**:
- WAL file (`queue.db-wal`) exceeds 50MB
- Performance degradation
- Disk space issues

**Causes**:
- Checkpoints not running
- Long-running readers preventing checkpoints
- `wal_autocheckpoint` set too high

**Solutions**:

1. **Manual checkpoint**:
```python
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
conn.close()
```

2. **Check autocheckpoint setting**:
```python
cursor = conn.execute("PRAGMA wal_autocheckpoint")
value = cursor.fetchone()[0]
print(f"WAL autocheckpoint: {value}")  # Should be 1000

if value != 1000:
    conn.execute("PRAGMA wal_autocheckpoint=1000")
```

3. **Monitor WAL file size**:
```python
from pathlib import Path

db_path = Path(r"C:\Data\PrismQ\queue\queue.db")
wal_path = db_path.with_suffix('.db-wal')

if wal_path.exists():
    wal_size_mb = wal_path.stat().st_size / (1024 * 1024)
    print(f"WAL file size: {wal_size_mb:.2f} MB")
    
    if wal_size_mb > 50:
        print("WARNING: WAL file is too large!")
```

**Prevention**:
- Set `wal_autocheckpoint=1000` (recommended)
- Run manual checkpoints during maintenance windows
- Monitor WAL file size and alert if > 50MB
- Close long-running read connections promptly

---

## Performance Degradation

### Symptom: Slow Task Insertion

**Expected Performance**: 200-400 tasks/minute  
**Degraded Performance**: <100 tasks/minute

**Diagnostic Steps**:

1. **Check current PRAGMA settings**:
```python
def check_pragmas(conn):
    pragmas = ['journal_mode', 'synchronous', 'busy_timeout', 
               'wal_autocheckpoint', 'cache_size']
    
    for pragma in pragmas:
        cursor = conn.execute(f"PRAGMA {pragma}")
        value = cursor.fetchone()[0]
        print(f"{pragma}: {value}")

# Run diagnostics
conn = sqlite3.connect(db_path)
check_pragmas(conn)
```

2. **Verify database location**:
```python
import os

db_path = r"C:\Data\PrismQ\queue\queue.db"

# Check it's on local drive (not network)
if db_path.startswith(r"\\"):
    print("ERROR: Database is on network share - move to local SSD!")
elif not db_path.startswith("C:") and not db_path.startswith("D:"):
    print("WARNING: Database not on C: or D: drive")
else:
    print("OK: Database on local drive")
```

3. **Check disk performance**:
```python
import time

# Simple write test
start = time.perf_counter()
with open(r"C:\Data\PrismQ\test_write.tmp", 'wb') as f:
    f.write(b'0' * 1024 * 1024)  # 1MB
    f.flush()
    os.fsync(f.fileno())
duration = time.perf_counter() - start

print(f"1MB sync write: {duration*1000:.2f}ms")
if duration > 0.1:  # >100ms is very slow
    print("WARNING: Slow disk I/O - check if SSD or if antivirus is scanning")
```

4. **Check for antivirus interference**:
- Open Windows Security → Virus & threat protection → Manage settings
- Add exclusion for `C:\Data\PrismQ\queue\`
- Restart application and re-test performance

**Solutions**:

1. **Reapply production configuration**:
```python
from Client.Backend.src.queue.config import apply_pragmas

conn = sqlite3.connect(db_path)
apply_pragmas(conn)
conn.close()
```

2. **Run VACUUM to defragment**:
```python
# WARNING: This locks the database - run during maintenance window
conn = sqlite3.connect(db_path)
conn.execute("VACUUM")
conn.close()
```

3. **Rebuild indexes**:
```python
conn = sqlite3.connect(db_path)
conn.execute("REINDEX")
conn.close()
```

---

### Symptom: High Latency (P95 > 20ms)

**Expected Latency**: P95 < 10ms  
**Degraded Latency**: P95 > 20ms

**Diagnostic Steps**:

1. **Measure actual latency**:
```python
import time
import statistics

latencies = []
conn = sqlite3.connect(db_path)

for i in range(100):
    start = time.perf_counter()
    conn.execute("SELECT COUNT(*) FROM task_queue WHERE status='queued'")
    duration = (time.perf_counter() - start) * 1000  # ms
    latencies.append(duration)

# Calculate percentiles
latencies.sort()
p50 = latencies[50]
p95 = latencies[95]
p99 = latencies[99]

print(f"P50: {p50:.2f}ms, P95: {p95:.2f}ms, P99: {p99:.2f}ms")
```

2. **Check for missing indexes**:
```python
cursor = conn.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='index' AND tbl_name='task_queue'
""")
indexes = [row[0] for row in cursor.fetchall()]
print(f"Indexes: {indexes}")

# Should include: idx_status_priority
if 'idx_status_priority' not in indexes:
    print("ERROR: Missing critical index!")
```

**Solutions**:

1. **Recreate missing indexes**:
```python
conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_status_priority 
        ON task_queue(status, priority DESC, created_at ASC)
""")
conn.commit()
```

2. **Analyze query performance**:
```python
# Enable query plan output
cursor = conn.execute("""
    EXPLAIN QUERY PLAN
    SELECT * FROM task_queue 
    WHERE status='queued' 
    ORDER BY priority DESC, created_at ASC 
    LIMIT 1
""")

for row in cursor:
    print(row)
# Should show "USING INDEX idx_status_priority"
```

---

## SQLITE_BUSY Errors

### Understanding SQLITE_BUSY

**What it means**: Another connection has a lock that prevents your operation

**When it occurs**:
- Multiple writers trying to commit simultaneously
- Reader holding lock during writer attempt
- Checkpoint operation blocking writes

**Expected rate**: 1-2% under normal load  
**Problematic rate**: >5%

### Diagnostic: Measure Error Rate

```python
import sqlite3
from concurrent.futures import ThreadPoolExecutor

def measure_error_rate(num_operations=1000, num_workers=4):
    """Measure SQLITE_BUSY error rate under load."""
    errors = 0
    successes = 0
    
    def worker(worker_id):
        nonlocal errors, successes
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA busy_timeout=5000")
        
        for i in range(num_operations // num_workers):
            try:
                conn.execute("""
                    INSERT INTO task_queue 
                    (task_id, task_type, parameters, created_at, updated_at)
                    VALUES (?, 'test', '{}', datetime('now'), datetime('now'))
                """, (f"w{worker_id}_t{i}",))
                conn.commit()
                successes += 1
            except sqlite3.OperationalError as e:
                if 'locked' in str(e) or 'busy' in str(e):
                    errors += 1
                else:
                    raise
        
        conn.close()
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for i in range(num_workers):
            executor.submit(worker, i)
    
    total = errors + successes
    error_rate = (errors / total) * 100 if total > 0 else 0
    
    print(f"Operations: {total}")
    print(f"Errors: {errors}")
    print(f"Error rate: {error_rate:.2f}%")
    
    return error_rate

# Run test
error_rate = measure_error_rate()

if error_rate > 5:
    print("WARNING: Error rate too high!")
elif error_rate > 2:
    print("NOTICE: Error rate slightly elevated")
else:
    print("OK: Error rate within normal range")
```

### Solution: Implement Retry Logic

```python
import time
import sqlite3
from typing import Any, Callable

def execute_with_retry(
    conn: sqlite3.Connection,
    operation: Callable,
    max_retries: int = 3,
    initial_backoff_ms: int = 100
) -> Any:
    """
    Execute database operation with exponential backoff retry.
    
    Args:
        conn: Database connection
        operation: Function to execute (takes conn as argument)
        max_retries: Maximum number of retry attempts
        initial_backoff_ms: Initial backoff duration in milliseconds
        
    Returns:
        Result from operation
        
    Raises:
        sqlite3.OperationalError: If all retries exhausted
    """
    for attempt in range(max_retries):
        try:
            return operation(conn)
        except sqlite3.OperationalError as e:
            if 'locked' in str(e).lower() or 'busy' in str(e).lower():
                if attempt < max_retries - 1:
                    # Exponential backoff: 100ms, 200ms, 400ms, ...
                    wait_ms = initial_backoff_ms * (2 ** attempt)
                    time.sleep(wait_ms / 1000.0)
                else:
                    # Final attempt failed
                    raise
            else:
                # Different error, don't retry
                raise

# Usage example
def claim_task(conn):
    """Operation to retry."""
    conn.execute("BEGIN IMMEDIATE")
    cursor = conn.execute("""
        SELECT id FROM task_queue 
        WHERE status='queued' 
        ORDER BY priority DESC, created_at ASC 
        LIMIT 1
    """)
    row = cursor.fetchone()
    
    if row:
        conn.execute("""
            UPDATE task_queue 
            SET status='processing', started_at=datetime('now')
            WHERE id=?
        """, (row[0],))
        conn.commit()
        return row[0]
    else:
        conn.rollback()
        return None

# Execute with retry
task_id = execute_with_retry(conn, claim_task, max_retries=3)
```

### Solution: Reduce Concurrent Workers

If error rate remains high even with retries:

```python
# In config.py
MAX_CONCURRENT_WORKERS = 4  # Reduce from 6 to 4

# Or reduce dynamically based on error rate
current_workers = 6
if error_rate > 5:
    current_workers = max(2, current_workers - 1)
    print(f"Reducing workers to {current_workers} due to high error rate")
```

---

## Checkpoint Blocking

### Symptom: Periodic Write Stalls

**Observation**: Periodic delays in write operations every few minutes

**Cause**: Automatic checkpoint blocking writers

**Diagnostic**:

```python
# Monitor checkpoint activity
conn = sqlite3.connect(db_path)

# Get WAL checkpoint info
cursor = conn.execute("PRAGMA wal_checkpoint")
busy, log, checkpointed = cursor.fetchone()

print(f"Busy: {busy}")
print(f"Log size: {log} pages")
print(f"Checkpointed: {checkpointed} pages")

if log > 5000:  # >20MB
    print("WARNING: Large WAL file, checkpoint recommended")
```

**Solution 1**: Manual checkpoint during low-traffic periods

```python
import schedule
import time

def run_checkpoint():
    """Run checkpoint during maintenance window."""
    try:
        conn = sqlite3.connect(db_path)
        print("Starting checkpoint...")
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        print("Checkpoint complete")
        conn.close()
    except Exception as e:
        print(f"Checkpoint failed: {e}")

# Schedule for 3 AM daily
schedule.every().day.at("03:00").do(run_checkpoint)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Solution 2**: Adjust autocheckpoint threshold

```python
# If checkpoints are too frequent (causing stalls)
conn.execute("PRAGMA wal_autocheckpoint=2000")  # Increase from 1000

# If WAL is growing too large
conn.execute("PRAGMA wal_autocheckpoint=500")   # Decrease from 1000
```

---

## Database Corruption

### Symptom: Database Integrity Errors

**Symptoms**:
```
sqlite3.DatabaseError: database disk image is malformed
```

**Immediate Actions**:

1. **STOP all writes immediately** - prevent further corruption
2. **Make backup** of current state (even if corrupted)
3. **Check integrity**

```python
# Step 1: Backup corrupted database
import shutil
from datetime import datetime

backup_path = f"queue_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
shutil.copy2(db_path, backup_path)
print(f"Backup saved: {backup_path}")

# Step 2: Check integrity
conn = sqlite3.connect(db_path)
cursor = conn.execute("PRAGMA integrity_check")
results = cursor.fetchall()

for row in results:
    print(row[0])

# If not "ok", database is corrupted
if results != [('ok',)]:
    print("DATABASE IS CORRUPTED!")
else:
    print("Database integrity: OK")
```

### Recovery Procedure

**Option 1: Dump and Restore** (if database is readable)

```python
import subprocess

# Dump database to SQL
dump_file = "queue_dump.sql"
subprocess.run([
    "sqlite3",
    db_path,
    f".output {dump_file}",
    ".dump"
])

# Create new database from dump
new_db = "queue_new.db"
subprocess.run([
    "sqlite3",
    new_db,
    f".read {dump_file}"
])

# Verify new database
conn = sqlite3.connect(new_db)
cursor = conn.execute("PRAGMA integrity_check")
if cursor.fetchone()[0] == 'ok':
    print("Recovery successful!")
    # Replace old database with new one
    shutil.move(db_path, f"{db_path}.corrupted")
    shutil.move(new_db, db_path)
```

**Option 2: Restore from Backup**

```python
# Find latest backup
import glob

backups = sorted(glob.glob("queue_backup_*.db"), reverse=True)
if backups:
    latest_backup = backups[0]
    print(f"Restoring from: {latest_backup}")
    
    # Restore
    shutil.move(db_path, f"{db_path}.corrupted")
    shutil.copy2(latest_backup, db_path)
    
    print("Restore complete - verify data")
else:
    print("No backups found!")
```

**Prevention**:

1. **Regular backups**:
```python
# Daily backup script
import shutil
from datetime import datetime
from pathlib import Path

def backup_database():
    """Create daily backup of database."""
    backup_dir = Path(r"C:\Data\PrismQ\backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Checkpoint first
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    conn.close()
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"queue_{timestamp}.db"
    
    shutil.copy2(db_path, backup_path)
    print(f"Backup created: {backup_path}")
    
    # Keep only last 7 days
    backups = sorted(backup_dir.glob("queue_*.db"))
    for old_backup in backups[:-7]:
        old_backup.unlink()
        print(f"Removed old backup: {old_backup}")

# Run daily at 2 AM
schedule.every().day.at("02:00").do(backup_database)
```

2. **Use WAL mode** (already enabled)
3. **Ensure disk health**: Run `chkdsk` on Windows regularly
4. **Avoid force shutdowns**: Proper shutdown procedures
5. **UPS recommended**: Prevent corruption from power loss

---

## Recovery Procedures

### Procedure 1: Reset Database

**When to use**: During development or if data can be lost

```python
def reset_database():
    """Completely reset the database - DESTROYS ALL DATA!"""
    import os
    
    # Close all connections first
    # ...
    
    # Delete database files
    for ext in ['', '-shm', '-wal']:
        file_path = db_path + ext
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
    
    # Reinitialize
    conn = sqlite3.connect(db_path)
    from Client.Backend.src.queue.config import apply_pragmas
    apply_pragmas(conn)
    
    # Create schema
    conn.execute("""
        CREATE TABLE task_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE NOT NULL,
            task_type TEXT NOT NULL,
            parameters TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            status TEXT DEFAULT 'queued',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE INDEX idx_status_priority 
            ON task_queue(status, priority DESC, created_at ASC)
    """)
    
    conn.commit()
    conn.close()
    
    print("Database reset complete")
```

### Procedure 2: Vacuum and Optimize

**When to use**: Periodic maintenance, after large deletions

```python
def optimize_database():
    """Optimize database - run during maintenance window."""
    conn = sqlite3.connect(db_path)
    
    print("Step 1: Checkpoint...")
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    
    print("Step 2: Analyze...")
    conn.execute("ANALYZE")
    
    print("Step 3: Reindex...")
    conn.execute("REINDEX")
    
    print("Step 4: Vacuum...")
    conn.execute("VACUUM")
    
    conn.close()
    print("Optimization complete")

# Run monthly
schedule.every().month.at("02:00").do(optimize_database)
```

---

## Monitoring & Diagnostics

### Health Check Script

```python
def health_check():
    """Comprehensive database health check."""
    import os
    from pathlib import Path
    
    print("=== SQLite Queue Health Check ===\n")
    
    # 1. File existence
    db_file = Path(db_path)
    if not db_file.exists():
        print("❌ Database file not found!")
        return False
    
    print(f"✓ Database file exists: {db_file}")
    
    # 2. File size
    db_size_mb = db_file.stat().st_size / (1024 * 1024)
    print(f"  Size: {db_size_mb:.2f} MB")
    
    # 3. WAL file size
    wal_file = db_file.with_suffix('.db-wal')
    if wal_file.exists():
        wal_size_mb = wal_file.stat().st_size / (1024 * 1024)
        print(f"  WAL size: {wal_size_mb:.2f} MB")
        if wal_size_mb > 50:
            print("  ⚠️  WARNING: WAL file is large!")
    
    # 4. Connection test
    try:
        conn = sqlite3.connect(db_path)
        print("✓ Connection successful")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # 5. PRAGMA check
    print("\n=== PRAGMA Settings ===")
    pragmas = {
        'journal_mode': 'wal',
        'synchronous': '1',  # NORMAL
        'busy_timeout': '5000',
    }
    
    for pragma, expected in pragmas.items():
        cursor = conn.execute(f"PRAGMA {pragma}")
        actual = str(cursor.fetchone()[0])
        match = "✓" if actual.lower() == expected.lower() else "❌"
        print(f"{match} {pragma}: {actual} (expected: {expected})")
    
    # 6. Integrity check
    print("\n=== Integrity Check ===")
    cursor = conn.execute("PRAGMA integrity_check")
    result = cursor.fetchone()[0]
    if result == 'ok':
        print("✓ Database integrity: OK")
    else:
        print(f"❌ Database integrity: {result}")
        return False
    
    # 7. Table stats
    print("\n=== Table Statistics ===")
    cursor = conn.execute("SELECT COUNT(*) FROM task_queue")
    total = cursor.fetchone()[0]
    print(f"  Total tasks: {total}")
    
    cursor = conn.execute("""
        SELECT status, COUNT(*) 
        FROM task_queue 
        GROUP BY status
    """)
    for status, count in cursor:
        print(f"  {status}: {count}")
    
    conn.close()
    
    print("\n=== Health Check Complete ===")
    return True

# Run health check
if __name__ == '__main__':
    health_check()
```

### Performance Metrics

```python
import time
from collections import defaultdict

class QueueMetrics:
    """Track queue performance metrics."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = defaultdict(int)
        self.latencies = []
        self.start_time = time.time()
    
    def record_operation(self, operation: str, duration_ms: float, success: bool):
        """Record an operation."""
        self.metrics[f'{operation}_total'] += 1
        if success:
            self.metrics[f'{operation}_success'] += 1
            self.latencies.append(duration_ms)
        else:
            self.metrics[f'{operation}_error'] += 1
    
    def get_summary(self):
        """Get metrics summary."""
        runtime = time.time() - self.start_time
        
        return {
            'runtime_seconds': runtime,
            'operations_per_second': self.metrics.get('enqueue_total', 0) / runtime,
            'error_rate': (
                self.metrics.get('enqueue_error', 0) / 
                max(1, self.metrics.get('enqueue_total', 1))
            ) * 100,
            'latency_p95': sorted(self.latencies)[int(len(self.latencies) * 0.95)] 
                          if self.latencies else 0,
        }

# Usage
metrics = QueueMetrics()

# Record operations
start = time.perf_counter()
try:
    # ... database operation ...
    success = True
except:
    success = False
duration = (time.perf_counter() - start) * 1000

metrics.record_operation('enqueue', duration, success)

# Get summary
summary = metrics.get_summary()
print(f"Throughput: {summary['operations_per_second']:.2f} ops/sec")
print(f"Error rate: {summary['error_rate']:.2f}%")
print(f"P95 latency: {summary['latency_p95']:.2f}ms")
```

---

## Windows-Specific Issues

### Issue: Database on Network Drive

**Symptoms**:
- Very slow performance
- Frequent lock errors
- Occasional corruption

**Detection**:
```python
import os

db_path = r"C:\Data\PrismQ\queue\queue.db"

# Check if on network drive
if db_path.startswith(r"\\"):
    print("ERROR: Database is on network drive (UNC path)")
    print("Move to local drive immediately!")

# Check if on mapped network drive
drive = os.path.splitdrive(db_path)[0]
if drive:
    import win32file
    drive_type = win32file.GetDriveType(f"{drive}\\")
    # DRIVE_REMOTE = 4
    if drive_type == 4:
        print("ERROR: Database is on mapped network drive")
        print("Move to local drive immediately!")
```

**Solution**: Move database to local SSD

```python
import shutil

old_path = r"\\server\share\queue.db"  # Network path
new_path = r"C:\Data\PrismQ\queue\queue.db"  # Local path

# Ensure directory exists
Path(new_path).parent.mkdir(parents=True, exist_ok=True)

# Copy database
shutil.copy2(old_path, new_path)

# Update application configuration
# Update DB_PATH in config.py or environment variable
```

### Issue: Antivirus Blocking

**Symptoms**:
- Intermittent slowness
- Random lock errors
- Operations timeout

**Solution**: Add exclusions

1. Open Windows Security
2. Go to "Virus & threat protection"
3. Click "Manage settings"
4. Scroll to "Exclusions" and click "Add or remove exclusions"
5. Add folder: `C:\Data\PrismQ\queue\`

**Verify exclusions**:
```powershell
# Run in PowerShell as Administrator
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

### Issue: Insufficient Permissions

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied
```

**Solution**:

```powershell
# Run in PowerShell as Administrator
# Grant full control to current user
$path = "C:\Data\PrismQ\queue"
$acl = Get-Acl $path
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME,"FullControl","ContainerInherit,ObjectInherit","None","Allow"
)
$acl.SetAccessRule($accessRule)
Set-Acl $path $acl
```

---

## Quick Reference

### Essential Commands

```python
# Check database status
conn.execute("PRAGMA integrity_check")           # Check for corruption
conn.execute("PRAGMA journal_mode")              # Should be "wal"
conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # Manual checkpoint
conn.execute("VACUUM")                           # Defragment (maintenance only)

# Get database info
conn.execute("PRAGMA page_count")                # Number of pages
conn.execute("PRAGMA page_size")                 # Page size in bytes
conn.execute("PRAGMA freelist_count")            # Unused pages

# Performance
conn.execute("ANALYZE")                          # Update query planner statistics
conn.execute("REINDEX")                          # Rebuild indexes
```

### When to Contact Support

Contact support if:
- Error rate consistently > 10%
- Latency P95 consistently > 50ms
- Database corruption occurs more than once
- WAL file grows > 100MB
- Any data loss occurs

### Emergency Contacts

- **Issue Tracker**: GitHub Issues on PrismQ.IdeaInspiration repository
- **Documentation**: `_meta/docs/` directory
- **Configuration**: `Client/Backend/src/queue/config.py`

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-05  
**Maintained By**: Worker 09 - Research Engineer  
**Related Issue**: #337 - SQLite Concurrency Research
