# SQLite Queue System - Quick Start Guide

**Version**: 1.0  
**Status**: Phase 1 Implementation  
**Created**: 2025-11-05  
**Last Updated**: 2025-11-05

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [First Steps](#first-steps)
- [Basic Usage](#basic-usage)
- [Common Operations](#common-operations)
- [Next Steps](#next-steps)

---

## Prerequisites

### System Requirements

| Requirement | Details |
|-------------|---------|
| **Python** | 3.10.x (required) |
| **OS** | Windows 10/11 (primary), Linux/macOS (supported) |
| **Storage** | 100MB free space minimum |
| **RAM** | 4GB minimum, 8GB+ recommended |

### Python Version Check

```bash
# Check Python version
py -3.10 --version
# or
python --version

# Should show: Python 3.10.x
```

**⚠️ Important**: Python 3.10.x is **required** for DaVinci Resolve compatibility. Do not use Python 3.11+.

---

## Installation

### 1. Clone Repository (if not already done)

```bash
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
cd PrismQ.IdeaInspiration
```

### 2. Setup Virtual Environment

**Windows (PowerShell)**:
```powershell
# Create virtual environment
py -3.10 -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -e Client/Backend
```

**Linux/macOS (bash)**:
```bash
# Create virtual environment
python3.10 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -e Client/Backend
```

### 3. Verify Installation

```python
# Test import
python -c "from queue import QueueDatabase; print('✅ Queue module installed')"
```

**Expected Output**:
```
✅ Queue module installed
```

---

## First Steps

### Create Your First Database

```python
from queue import QueueDatabase

# Create database (uses default path)
db = QueueDatabase()

# Initialize schema (creates tables and indexes)
db.initialize_schema()

print("✅ Database created successfully!")

# Close connection
db.close()
```

**Run It**:
```bash
python -c "from queue import QueueDatabase; db = QueueDatabase(); db.initialize_schema(); print('✅ Created!')"
```

### Verify Database Created

**Windows**:
```powershell
# Check database file exists
Test-Path C:\Data\PrismQ\queue\queue.db
# Should return: True

# Check database size
(Get-Item C:\Data\PrismQ\queue\queue.db).Length
# Should show: ~100KB
```

**Linux/macOS**:
```bash
# Check database file exists
ls -lh /tmp/prismq/queue/queue.db

# Should show: ~100KB
```

### Inspect Database (Optional)

**Using sqlite3 CLI**:
```bash
# Open database
sqlite3 C:\Data\PrismQ\queue\queue.db

# List tables
.tables
# Should show: task_queue  task_logs  workers

# Show schema
.schema task_queue

# Exit
.quit
```

---

## Basic Usage

### Enqueue a Task

```python
from queue import QueueDatabase, Task

# Connect to database
db = QueueDatabase()

# Enqueue task
with db.transaction() as conn:
    cursor = conn.execute("""
        INSERT INTO task_queue (type, payload, priority)
        VALUES (?, ?, ?)
    """, ("video_processing", '{"video_id": "abc123"}', 50))
    
    task_id = cursor.lastrowid
    print(f"✅ Enqueued task #{task_id}")

db.close()
```

**Run It**:
```bash
cd Client/Backend
python -c "
from queue import QueueDatabase
db = QueueDatabase()
with db.transaction() as conn:
    cursor = conn.execute(
        'INSERT INTO task_queue (type, payload, priority) VALUES (?, ?, ?)',
        ('test', '{}', 100)
    )
    print(f'✅ Created task #{cursor.lastrowid}')
db.close()
"
```

### Query Tasks

```python
from queue import QueueDatabase, Task

db = QueueDatabase()

# Query all queued tasks
cursor = db.execute("""
    SELECT * FROM task_queue
    WHERE status = 'queued'
    ORDER BY priority ASC
""")

print("📋 Queued Tasks:")
for row in cursor:
    task = Task.from_dict(dict(row))
    print(f"  Task #{task.id}: {task.type} (priority {task.priority})")

db.close()
```

**Run It**:
```bash
cd Client/Backend
python -c "
from queue import QueueDatabase, Task
db = QueueDatabase()
cursor = db.execute('SELECT * FROM task_queue')
for row in cursor:
    task = Task.from_dict(dict(row))
    print(f'Task #{task.id}: {task.type}')
db.close()
"
```

### Claim a Task (Worker)

```python
from queue import QueueDatabase, Task

db = QueueDatabase()
worker_id = "worker-01"

# Atomic claim operation
with db.transaction() as conn:
    # Find next task
    cursor = conn.execute("""
        SELECT * FROM task_queue
        WHERE status = 'queued'
          AND run_after_utc <= datetime('now')
        ORDER BY priority ASC, run_after_utc ASC
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    if row:
        task = Task.from_dict(dict(row))
        
        # Claim task
        conn.execute("""
            UPDATE task_queue
            SET status = 'processing',
                locked_by = ?,
                lease_until_utc = datetime('now', '+5 minutes'),
                reserved_at_utc = datetime('now')
            WHERE id = ?
        """, (worker_id, task.id))
        
        print(f"✅ Claimed task #{task.id}")
    else:
        print("ℹ️  No tasks available")

db.close()
```

### Complete a Task

```python
from queue import QueueDatabase

db = QueueDatabase()
task_id = 1  # Replace with actual task ID

# Mark task as completed
db.execute("""
    UPDATE task_queue
    SET status = 'completed',
        finished_at_utc = datetime('now')
    WHERE id = ?
""", (task_id,))

print(f"✅ Completed task #{task_id}")
db.close()
```

---

## Common Operations

### Check Queue Status

```python
from queue import QueueDatabase

db = QueueDatabase()

# Get counts by status
cursor = db.execute("""
    SELECT status, COUNT(*) as count
    FROM task_queue
    GROUP BY status
""")

print("📊 Queue Status:")
for row in cursor:
    print(f"  {row['status']}: {row['count']}")

db.close()
```

**Expected Output**:
```
📊 Queue Status:
  queued: 42
  processing: 3
  completed: 156
  failed: 2
```

### View Recent Tasks

```python
from queue import QueueDatabase, Task

db = QueueDatabase()

cursor = db.execute("""
    SELECT * FROM task_queue
    ORDER BY created_at_utc DESC
    LIMIT 10
""")

print("🕒 Recent Tasks:")
for row in cursor:
    task = Task.from_dict(dict(row))
    print(f"  #{task.id}: {task.type} - {task.status}")

db.close()
```

### Delete Completed Tasks

```python
from queue import QueueDatabase

db = QueueDatabase()

# Delete tasks older than 7 days
cursor = db.execute("""
    DELETE FROM task_queue
    WHERE status = 'completed'
      AND finished_at_utc < datetime('now', '-7 days')
""")

deleted_count = cursor.rowcount
print(f"🗑️  Deleted {deleted_count} old completed tasks")

db.close()
```

### Retry Failed Task

```python
from queue import QueueDatabase

db = QueueDatabase()
task_id = 1  # Failed task ID

# Reset task to queued for retry
db.execute("""
    UPDATE task_queue
    SET status = 'queued',
        locked_by = NULL,
        lease_until_utc = NULL,
        run_after_utc = datetime('now'),
        error_message = NULL
    WHERE id = ?
""", (task_id,))

print(f"🔄 Reset task #{task_id} for retry")
db.close()
```

---

## Next Steps

### Learn More

1. **[Architecture Documentation](./QUEUE_ARCHITECTURE.md)**
   - System overview and design decisions
   - Component architecture
   - Concurrency model

2. **[API Reference](./QUEUE_API_REFERENCE.md)**
   - Detailed API documentation
   - Usage examples
   - Error handling patterns

3. **[Configuration Guide](./QUEUE_CONFIGURATION.md)**
   - PRAGMA settings explained
   - Performance tuning
   - Platform-specific configuration

4. **[Integration Guide](./QUEUE_INTEGRATION.md)**
   - BackgroundTaskManager integration
   - Migration examples
   - Use case patterns

### Explore the Implementation

```bash
# View core implementation
cat Client/Backend/src/queue/database.py
cat Client/Backend/src/queue/schema.py
cat Client/Backend/src/queue/models.py

# View tests
cd Client/_meta/tests/Backend/queue
python -m pytest -v

# View demo
python Client/Backend/src/queue/demo.py
```

### Try the Demo

```bash
cd Client/Backend/src/queue
python demo.py
```

**Demo Features**:
- Creates sample database
- Enqueues test tasks
- Simulates worker claiming
- Shows task lifecycle

### Future Components (Coming Soon)

**Phase 2** (Issues #323-#332):
- **QueueClient**: High-level enqueue API
- **QueueWorker**: Worker engine with retry logic
- **Scheduling Strategies**: FIFO, LIFO, Priority, Weighted Random
- **Observability**: Metrics and monitoring
- **Maintenance**: Backup and optimization

**Phase 3** (Issues #333-#340):
- **Testing**: Comprehensive test suite
- **Integration**: BackgroundTaskManager replacement
- **Documentation**: Operational runbook

---

## Troubleshooting

### Common Issues

#### "Module 'queue' not found"

**Solution**:
```bash
# Ensure you're in the correct directory
cd Client/Backend

# Install in development mode
pip install -e .

# Verify
python -c "import queue; print(queue.__file__)"
```

#### "Permission denied" (Windows)

**Solution**:
```powershell
# Run PowerShell as Administrator, or
# Change database path to user directory

$env:PRISMQ_QUEUE_DB_PATH = "$env:USERPROFILE\queue\queue.db"
```

#### "Database is locked"

**Solution**:
```python
# Increase busy_timeout (already set to 5 seconds)
# If still occurring, check:
# 1. Antivirus scanning database directory
# 2. Multiple processes accessing database
# 3. Database on network share (not supported)
```

#### Database file not created

**Solution**:
```bash
# Check directory exists and is writable
# Windows
mkdir C:\Data\PrismQ\queue

# Linux/macOS
mkdir -p /tmp/prismq/queue

# Or use custom path
export PRISMQ_QUEUE_DB_PATH=~/queue/queue.db
```

---

## Sample Scripts

### Complete Example: Task Producer and Consumer

**producer.py**:
```python
"""Enqueue tasks continuously."""
from queue import QueueDatabase
import time

db = QueueDatabase()
db.initialize_schema()

task_num = 1
while True:
    with db.transaction() as conn:
        cursor = conn.execute("""
            INSERT INTO task_queue (type, payload, priority)
            VALUES (?, ?, ?)
        """, ("job", f'{{"id": {task_num}}}', 100))
        
        print(f"✅ Enqueued task #{cursor.lastrowid}")
    
    task_num += 1
    time.sleep(2)  # Enqueue every 2 seconds
```

**consumer.py**:
```python
"""Process tasks continuously."""
from queue import QueueDatabase, Task
import time

db = QueueDatabase()
worker_id = "worker-01"

while True:
    # Try to claim a task
    with db.transaction() as conn:
        cursor = conn.execute("""
            SELECT * FROM task_queue
            WHERE status = 'queued'
            ORDER BY priority ASC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        if row:
            task = Task.from_dict(dict(row))
            
            # Claim task
            conn.execute("""
                UPDATE task_queue
                SET status = 'processing',
                    locked_by = ?,
                    lease_until_utc = datetime('now', '+5 minutes')
                WHERE id = ?
            """, (worker_id, task.id))
            
            print(f"🔄 Processing task #{task.id}...")
    
    if row:
        # Simulate work
        time.sleep(3)
        
        # Complete task
        db.execute("""
            UPDATE task_queue
            SET status = 'completed',
                finished_at_utc = datetime('now')
            WHERE id = ?
        """, (task.id,))
        
        print(f"✅ Completed task #{task.id}")
    else:
        print("😴 No tasks, sleeping...")
        time.sleep(5)
```

**Run Both**:
```bash
# Terminal 1: Producer
python producer.py

# Terminal 2: Consumer
python consumer.py
```

---

## Quick Reference Card

### Essential Commands

```python
# Create database
from queue import QueueDatabase
db = QueueDatabase()
db.initialize_schema()

# Enqueue task
with db.transaction() as conn:
    conn.execute("INSERT INTO task_queue (type, payload) VALUES (?, ?)", 
                 ("job", "{}"))

# Query tasks
cursor = db.execute("SELECT * FROM task_queue WHERE status = 'queued'")

# Claim task
with db.transaction() as conn:
    cursor = conn.execute("SELECT * FROM task_queue WHERE status = 'queued' LIMIT 1")
    row = cursor.fetchone()
    if row:
        conn.execute("UPDATE task_queue SET status = 'processing' WHERE id = ?", 
                     (row['id'],))

# Complete task
db.execute("UPDATE task_queue SET status = 'completed' WHERE id = ?", (task_id,))

# Close
db.close()
```

### Useful Queries

```sql
-- Count tasks by status
SELECT status, COUNT(*) FROM task_queue GROUP BY status;

-- Recent failed tasks
SELECT * FROM task_queue WHERE status = 'failed' ORDER BY finished_at_utc DESC LIMIT 10;

-- Tasks by priority
SELECT priority, COUNT(*) FROM task_queue GROUP BY priority ORDER BY priority;

-- Average processing time
SELECT AVG(JULIANDAY(finished_at_utc) - JULIANDAY(processing_started_utc)) * 86400 AS avg_seconds
FROM task_queue WHERE status = 'completed';

-- Stuck tasks (processing >10 minutes)
SELECT * FROM task_queue 
WHERE status = 'processing' 
  AND processing_started_utc < datetime('now', '-10 minutes');
```

---

**Document Version**: 1.0  
**Phase**: Phase 1 - Core Infrastructure  
**Status**: Complete  
**Next**: Update with QueueClient and QueueWorker examples (Phase 2)
