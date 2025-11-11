# Issue #340: Create Migration Utilities and Rollback Procedures

**Parent Issue**: #320 (SQLite Queue Analysis)  
**Worker**: Worker 10 - Senior Engineer  
**Status**: Planning (Phase 1)  
**Priority**: High  
**Duration**: 3-4 days (Phase 3 - Week 4)  
**Dependencies**: #339 (Integration with BackgroundTaskManager)

---

## Objective

Design and implement migration utilities, rollback procedures, and operational runbooks to ensure safe transition from in-memory task execution to SQLite queue-based persistence, with zero downtime and easy recovery options.

---

## Phase 1 Planning (Week 1) - This Document

This document represents Worker 10's **Phase 1 deliverable**: comprehensive migration planning including utilities design, rollback procedures, and operational readiness.

### Planning Scope

1. **Migration Scenarios** - Identify all transition paths
2. **Utility Design** - Plan migration tools and scripts
3. **Rollback Strategy** - Define recovery procedures
4. **Data Migration** - Handle in-flight tasks during transition
5. **Operational Runbook** - Step-by-step deployment guide
6. **Testing Strategy** - Validate migration safety

---

## Migration Scenarios

### Scenario 1: Fresh Installation (Greenfield)

**Context**: New deployment with no existing in-memory tasks

**Requirements**:
- Initialize SQLite database with schema
- Configure queue backend in settings
- Start worker processes
- No data migration needed

**Complexity**: 🟢 **LOW**

**Script**: `initialize_queue.py`

### Scenario 2: Existing Production System (Brownfield)

**Context**: Running production system with active in-memory tasks

**Requirements**:
- Preserve in-flight tasks during transition
- Zero downtime deployment
- Gradual traffic shifting (canary)
- Rollback capability

**Complexity**: 🟡 **MEDIUM**

**Scripts**:
- `migrate_inflight_tasks.py`
- `validate_migration.py`
- `rollback_to_inmemory.py`

### Scenario 3: Disaster Recovery

**Context**: Queue database corruption or worker failure

**Requirements**:
- Immediate fallback to in-memory mode
- Preserve task history for forensics
- Resume operations with minimal data loss

**Complexity**: 🔴 **HIGH**

**Scripts**:
- `emergency_rollback.py`
- `export_queue_state.py`
- `analyze_failure.py`

---

## Migration Utilities Design

### 1. Database Initialization Utility

**File**: `scripts/queue/initialize_queue.py`

**Purpose**: Set up SQLite database with proper schema, indexes, and Windows-optimized configuration

**Usage**:
```bash
python scripts/queue/initialize_queue.py \
  --db-path "C:/Data/queue/queue.db" \
  --backup-path "C:/Data/queue/backups" \
  --validate
```

**Implementation**:
```python
#!/usr/bin/env python3
"""Initialize SQLite queue database."""

import sqlite3
import sys
from pathlib import Path
from typing import Optional


def initialize_database(
    db_path: Path,
    backup_path: Optional[Path] = None,
    validate: bool = True
) -> bool:
    """
    Initialize SQLite queue database with schema and configuration.
    
    Args:
        db_path: Path to SQLite database file
        backup_path: Optional backup directory path
        validate: Whether to validate schema after creation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Set Windows-optimized PRAGMAs (from #321)
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
        
        # Create schema (from #321)
        create_schema(cursor)
        
        # Create indexes (from #321)
        create_indexes(cursor)
        
        # Commit changes
        conn.commit()
        
        # Validate if requested
        if validate:
            validation_errors = validate_schema(cursor)
            if validation_errors:
                print(f"❌ Schema validation failed: {validation_errors}")
                return False
        
        print(f"✅ Database initialized: {db_path}")
        print(f"📊 WAL mode: {cursor.execute('PRAGMA journal_mode').fetchone()[0]}")
        print(f"🔄 Page size: {cursor.execute('PRAGMA page_size').fetchone()[0]} bytes")
        
        # Create backup directory if specified
        if backup_path:
            backup_path.mkdir(parents=True, exist_ok=True)
            print(f"💾 Backup directory: {backup_path}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def create_schema(cursor: sqlite3.Cursor) -> None:
    """Create task_queue, workers, and task_logs tables."""
    # Implementation from #321
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_queue (
          id                 INTEGER PRIMARY KEY AUTOINCREMENT,
          type               TEXT NOT NULL,
          priority           INTEGER NOT NULL DEFAULT 100,
          payload            TEXT NOT NULL,
          compatibility      TEXT NOT NULL DEFAULT '{}',
          
          status             TEXT NOT NULL DEFAULT 'queued',
          attempts           INTEGER NOT NULL DEFAULT 0,
          max_attempts       INTEGER NOT NULL DEFAULT 5,
          
          run_after_utc      DATETIME NOT NULL DEFAULT (datetime('now')),
          lease_until_utc    DATETIME,
          reserved_at_utc    DATETIME,
          processing_started_utc DATETIME,
          finished_at_utc    DATETIME,
          
          locked_by          TEXT,
          error_message      TEXT,
          idempotency_key    TEXT,
          
          created_at_utc     DATETIME NOT NULL DEFAULT (datetime('now')),
          updated_at_utc     DATETIME NOT NULL DEFAULT (datetime('now')),
          
          region             TEXT GENERATED ALWAYS AS (json_extract(compatibility, '$.region')) VIRTUAL,
          format             TEXT GENERATED ALWAYS AS (json_extract(payload, '$.format')) VIRTUAL
        )
    """)
    
    # Workers and task_logs tables (from #321)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
          worker_id      TEXT PRIMARY KEY,
          capabilities   TEXT NOT NULL,
          heartbeat_utc  DATETIME NOT NULL DEFAULT (datetime('now'))
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_logs (
          log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
          task_id    INTEGER NOT NULL,
          at_utc     DATETIME NOT NULL DEFAULT (datetime('now')),
          level      TEXT NOT NULL,
          message    TEXT,
          details    TEXT,
          FOREIGN KEY (task_id) REFERENCES task_queue(id)
        )
    """)


def create_indexes(cursor: sqlite3.Cursor) -> None:
    """Create indexes for query optimization."""
    # From #321
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_task_status_prio_time
          ON task_queue (status, priority, run_after_utc, id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_task_type_status
          ON task_queue (type, status)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_task_region 
          ON task_queue (region)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_task_format 
          ON task_queue (format)
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_task_idempotency
          ON task_queue (idempotency_key)
          WHERE idempotency_key IS NOT NULL
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_logs_task 
          ON task_logs (task_id, at_utc)
    """)


def validate_schema(cursor: sqlite3.Cursor) -> list:
    """Validate schema is correct."""
    errors = []
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    
    required_tables = {'task_queue', 'workers', 'task_logs'}
    missing = required_tables - tables
    if missing:
        errors.append(f"Missing tables: {missing}")
    
    # Check indexes exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = {row[0] for row in cursor.fetchall()}
    
    required_indexes = {
        'ix_task_status_prio_time',
        'ix_task_type_status',
        'uq_task_idempotency'
    }
    missing_idx = required_indexes - indexes
    if missing_idx:
        errors.append(f"Missing indexes: {missing_idx}")
    
    # Check WAL mode
    cursor.execute("PRAGMA journal_mode")
    mode = cursor.fetchone()[0]
    if mode != 'wal':
        errors.append(f"Journal mode is {mode}, expected 'wal'")
    
    return errors


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize SQLite queue database")
    parser.add_argument("--db-path", required=True, help="Path to database file")
    parser.add_argument("--backup-path", help="Path to backup directory")
    parser.add_argument("--validate", action="store_true", help="Validate schema")
    
    args = parser.parse_args()
    
    success = initialize_database(
        db_path=Path(args.db_path),
        backup_path=Path(args.backup_path) if args.backup_path else None,
        validate=args.validate
    )
    
    sys.exit(0 if success else 1)
```

**Features**:
- ✅ Creates schema with all tables and indexes
- ✅ Sets Windows-optimized PRAGMAs
- ✅ Validates schema correctness
- ✅ Idempotent (safe to run multiple times)
- ✅ Creates backup directory structure

---

### 2. In-Flight Task Migration Utility

**File**: `scripts/queue/migrate_inflight_tasks.py`

**Purpose**: Safely migrate in-memory tasks to SQLite queue during deployment

**Challenge**: 
- In-memory `RunRegistry` has active tasks
- Cannot lose these tasks during migration
- Need to preserve status and progress

**Strategy**:
1. Enumerate all tasks in `RunRegistry`
2. Filter tasks with status QUEUED or RUNNING
3. Serialize task data to SQLite queue format
4. Enqueue to SQLite with preserved status
5. Verify migration success

**Usage**:
```bash
python scripts/queue/migrate_inflight_tasks.py \
  --registry-export "C:/Data/temp/registry_export.json" \
  --db-path "C:/Data/queue/queue.db" \
  --dry-run
```

**Implementation Sketch**:
```python
"""Migrate in-flight tasks from in-memory to SQLite queue."""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any


def export_registry_state(registry_path: Path) -> List[Dict[str, Any]]:
    """
    Export current RunRegistry state to JSON.
    
    This would be called before shutdown in production:
    - API endpoint: GET /api/admin/export-registry
    - Exports all QUEUED and RUNNING tasks
    """
    # In production, this would query RunRegistry
    # For migration, pre-export to file before deployment
    with open(registry_path, 'r') as f:
        return json.load(f)


def migrate_tasks(
    registry_export: Path,
    db_path: Path,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Migrate tasks from registry export to SQLite queue.
    
    Returns:
        Migration statistics
    """
    # Load export
    tasks = export_registry_state(registry_export)
    
    # Connect to queue DB
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    stats = {
        "total": len(tasks),
        "migrated": 0,
        "skipped": 0,
        "errors": []
    }
    
    for task in tasks:
        # Only migrate QUEUED and RUNNING tasks
        if task["status"] not in ["QUEUED", "RUNNING"]:
            stats["skipped"] += 1
            continue
        
        try:
            # Convert Run object to queue task format
            queue_task = convert_run_to_task(task)
            
            if not dry_run:
                # Insert into task_queue
                cursor.execute("""
                    INSERT INTO task_queue 
                      (type, payload, status, created_at_utc, priority)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    queue_task["type"],
                    json.dumps(queue_task["payload"]),
                    queue_task["status"],
                    queue_task["created_at"],
                    queue_task.get("priority", 100)
                ))
                
            stats["migrated"] += 1
            
        except Exception as e:
            stats["errors"].append(f"Task {task['run_id']}: {e}")
    
    if not dry_run:
        conn.commit()
    
    conn.close()
    return stats


def convert_run_to_task(run: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Run object format to queue task format."""
    return {
        "type": run["module_id"],
        "payload": {
            "module_path": run["module_id"],
            "parameters": run["parameters"],
            "run_id": run["run_id"]
        },
        "status": run["status"].lower(),
        "created_at": run["created_at"],
        "priority": 100  # Default priority
    }
```

**Safety Features**:
- ✅ Dry-run mode for validation
- ✅ Only migrates QUEUED/RUNNING tasks
- ✅ Detailed statistics and error reporting
- ✅ Atomic transaction (all or nothing)

---

### 3. Rollback Utility

**File**: `scripts/queue/rollback_to_inmemory.py`

**Purpose**: Emergency rollback from queue backend to in-memory backend

**Scenarios**:
1. Queue database corruption
2. Unacceptable performance issues
3. Critical bug in queue implementation

**Usage**:
```bash
python scripts/queue/rollback_to_inmemory.py \
  --config-file "C:/PrismQ/config.yaml" \
  --export-queue-state \
  --reason "Database corruption detected"
```

**Implementation**:
```python
"""Emergency rollback from queue to in-memory backend."""

import yaml
from pathlib import Path
from typing import Optional


def rollback_to_inmemory(
    config_file: Path,
    export_queue_state: bool = True,
    reason: Optional[str] = None
) -> bool:
    """
    Rollback from queue backend to in-memory backend.
    
    Steps:
    1. Export current queue state (if requested)
    2. Update config: TASK_BACKEND = "in-memory"
    3. Restart service (manual step, documented)
    
    Args:
        config_file: Path to configuration file
        export_queue_state: Whether to export queue before rollback
        reason: Reason for rollback (for logging)
        
    Returns:
        True if successful
    """
    print(f"🔄 Starting rollback to in-memory backend")
    if reason:
        print(f"📝 Reason: {reason}")
    
    # Step 1: Export queue state
    if export_queue_state:
        export_path = config_file.parent / "queue_rollback_export.json"
        success = export_current_queue_state(export_path)
        if not success:
            print("⚠️  Queue export failed, continuing anyway")
        else:
            print(f"✅ Queue state exported to {export_path}")
    
    # Step 2: Update config
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    config["task_execution"]["backend"] = "in-memory"
    config["task_execution"]["queue_fallback_enabled"] = True
    
    # Backup original config
    backup_path = config_file.with_suffix('.yaml.backup')
    with open(backup_path, 'w') as f:
        yaml.dump(config, f)
    print(f"💾 Config backed up to {backup_path}")
    
    # Write updated config
    with open(config_file, 'w') as f:
        yaml.dump(config, f)
    print(f"✅ Config updated: TASK_BACKEND = in-memory")
    
    # Step 3: Instructions for restart
    print("\n" + "="*60)
    print("⚠️  MANUAL STEP REQUIRED:")
    print("   Restart the PrismQ service to apply changes:")
    print("   > Restart-Service PrismQBackend")
    print("="*60)
    
    return True


def export_current_queue_state(export_path: Path) -> bool:
    """Export all tasks from queue to JSON file."""
    # Implementation would query SQLite and export to JSON
    # For forensics and potential manual recovery
    pass
```

**Recovery Time Objective (RTO)**: ≤ 5 minutes

**Process**:
1. Run rollback script (1 minute)
2. Restart service (2 minutes)
3. Verify in-memory mode active (2 minutes)

---

### 4. Validation Utility

**File**: `scripts/queue/validate_migration.py`

**Purpose**: Verify migration completed successfully and system is healthy

**Checks**:
1. ✅ Database file exists and is readable
2. ✅ Schema is correct (tables, indexes)
3. ✅ WAL mode enabled
4. ✅ Worker processes running
5. ✅ Can enqueue test task
6. ✅ Worker can claim test task
7. ✅ Task completes successfully

**Usage**:
```bash
python scripts/queue/validate_migration.py \
  --db-path "C:/Data/queue/queue.db" \
  --run-integration-test
```

**Output**:
```
🔍 Validating SQLite Queue Migration
=====================================

✅ Database file exists: C:/Data/queue/queue.db (1.2 MB)
✅ Schema validation passed
✅ WAL mode: enabled
✅ Indexes: 6/6 present
✅ Workers: 3 active (heartbeat within 30s)

🧪 Running integration test...
  → Enqueuing test task... ✅
  → Worker claiming task... ✅ (claimed by worker-01)
  → Task executing... ✅ (completed in 2.3s)
  → Status update: completed ✅

=====================================
✅ All validation checks passed!
```

---

## Rollback Procedures

### Procedure 1: Planned Rollback (Non-Emergency)

**Trigger**: Performance issues, bugs discovered in testing

**Timeline**: 10-15 minutes

**Steps**:

1. **Announce Maintenance Window** (if production)
   ```
   POST /api/admin/maintenance-mode ON
   ```

2. **Export Current Queue State**
   ```bash
   python scripts/queue/export_queue_state.py \
     --db-path "C:/Data/queue/queue.db" \
     --output "C:/Data/backups/queue_state_$(date +%Y%m%d_%H%M%S).json"
   ```

3. **Update Configuration**
   ```bash
   python scripts/queue/rollback_to_inmemory.py \
     --config-file "C:/PrismQ/config.yaml" \
     --export-queue-state \
     --reason "Performance degradation"
   ```

4. **Restart Service**
   ```powershell
   Restart-Service PrismQBackend
   ```

5. **Verify In-Memory Mode Active**
   ```bash
   python scripts/queue/validate_config.py --check-backend
   # Expected: TASK_BACKEND = in-memory
   ```

6. **Run Smoke Tests**
   ```bash
   python scripts/test_api.py --smoke-test
   ```

7. **Resume Operations**
   ```
   POST /api/admin/maintenance-mode OFF
   ```

**Success Criteria**:
- ✅ Service running on in-memory backend
- ✅ API endpoints responding
- ✅ Tasks executing successfully
- ✅ No queue-related errors in logs

---

### Procedure 2: Emergency Rollback

**Trigger**: Critical production issue (database corruption, worker crashes, data loss)

**Timeline**: 2-5 minutes

**Steps**:

1. **Immediate Config Change** (bypass scripts for speed)
   ```yaml
   # Edit config.yaml directly
   task_execution:
     backend: "in-memory"  # Change from "queue"
     queue_fallback_enabled: true
   ```

2. **Restart Service**
   ```powershell
   Restart-Service PrismQBackend -Force
   ```

3. **Verify Service Running**
   ```powershell
   Get-Service PrismQBackend
   # Status: Running
   ```

4. **Post-Incident** (after service restored)
   - Export queue database for forensic analysis
   - File incident report
   - Root cause analysis

**Acceptance Criteria**:
- ✅ Service restored within 5 minutes
- ✅ Zero additional data loss
- ✅ In-memory mode operational

---

### Procedure 3: Data Recovery from Backup

**Trigger**: Queue database corruption, need to restore from backup

**Prerequisites**: Regular backups via Worker 06's utilities (#331)

**Steps**:

1. **Stop Service**
   ```powershell
   Stop-Service PrismQBackend
   ```

2. **Backup Corrupted Database** (for analysis)
   ```powershell
   Copy-Item "C:/Data/queue/queue.db" `
     "C:/Data/queue/corrupted_$(Get-Date -Format yyyyMMdd_HHmmss).db"
   ```

3. **Restore from Backup**
   ```bash
   python scripts/queue/restore_backup.py \
     --backup-path "C:/Data/queue/backups/queue_20251104_120000.db" \
     --target-path "C:/Data/queue/queue.db" \
     --validate
   ```

4. **Validate Restored Database**
   ```bash
   python scripts/queue/validate_migration.py \
     --db-path "C:/Data/queue/queue.db"
   ```

5. **Restart Service**
   ```powershell
   Start-Service PrismQBackend
   ```

6. **Verify Operations**
   - Check worker heartbeats
   - Verify task claiming works
   - Run integration test

---

## Data Migration Strategy

### In-Flight Task Handling

**Challenge**: Tasks running when deploying queue backend

**Options**:

**Option A: Drain Before Deploy** (Recommended)
1. Stop accepting new tasks (`/api/admin/pause-intake`)
2. Wait for all in-flight tasks to complete
3. Verify `RunRegistry` empty (no QUEUED/RUNNING)
4. Deploy queue backend
5. Resume intake

**Pros**: ✅ Zero migration needed, clean cutover  
**Cons**: ❌ Requires downtime (typically 5-15 minutes)

**Option B: Migrate In-Flight Tasks**
1. Export `RunRegistry` state to JSON
2. Deploy queue backend
3. Import QUEUED/RUNNING tasks to SQLite
4. Workers pick up migrated tasks

**Pros**: ✅ Zero downtime  
**Cons**: ❌ More complex, risk of task duplication

**Recommendation**: **Option A for initial deployment**, Option B for future zero-downtime upgrades

---

### Task History Preservation

**Question**: What about completed task history in `RunRegistry`?

**Answer**: 

**Phase 3 Approach** (Simple):
- Start fresh with queue backend
- Historical tasks remain in `RunRegistry` (in-memory)
- No migration of completed tasks
- Acceptable: History is for reference only, not operational

**Future Enhancement** (Post-Phase 3):
- Export historical runs to separate SQLite database
- Create `run_history.db` for long-term storage
- API queries both sources (queue + history)

---

## Operational Runbook

### Deployment Checklist

#### Pre-Deployment (1 week before)

- [ ] **Worker 01-06**: All Phase 2 components merged and tested
- [ ] **Worker 07**: Integration tests passing (≥90% coverage)
- [ ] **Worker 08**: Documentation complete
- [ ] **Worker 09**: Performance benchmarks baseline established
- [ ] **Worker 10**: Migration utilities tested in staging

#### Deployment Day - 1 (Staging)

- [ ] Deploy queue backend to staging environment
- [ ] Run `initialize_queue.py` to create database
- [ ] Start 2 worker processes
- [ ] Run integration tests from Worker 07
- [ ] Run performance benchmarks from Worker 09
- [ ] Validate all API endpoints work
- [ ] Test rollback procedure
- [ ] Document any issues found

#### Deployment Day (Production)

**Timeline**: 2-hour maintenance window (off-peak hours)

**T-0:00 - Preparation**
- [ ] Announce maintenance window to users
- [ ] Enable maintenance mode: `POST /api/admin/maintenance-mode ON`
- [ ] Backup current configuration
- [ ] Backup current data (if any)

**T-0:10 - Drain In-Flight Tasks**
- [ ] Pause new task intake: `POST /api/admin/pause-intake`
- [ ] Wait for in-flight tasks to complete (typically 5-10 minutes)
- [ ] Verify RunRegistry empty: `GET /api/admin/registry-status`

**T-0:20 - Initialize Queue**
- [ ] Run database initialization:
  ```bash
  python scripts/queue/initialize_queue.py \
    --db-path "C:/Data/queue/queue.db" \
    --backup-path "C:/Data/queue/backups" \
    --validate
  ```
- [ ] Verify database created and validated

**T-0:25 - Update Configuration**
- [ ] Update config.yaml:
  ```yaml
  task_execution:
    backend: "queue"  # Changed from "in-memory"
    queue_db_path: "C:/Data/queue/queue.db"
    queue_fallback_enabled: true  # Safety net
  ```
- [ ] Validate configuration file syntax

**T-0:30 - Deploy Queue Backend**
- [ ] Deploy new code (includes Workers 01-06 components)
- [ ] Restart service: `Restart-Service PrismQBackend`
- [ ] Verify service started successfully
- [ ] Check logs for errors

**T-0:35 - Start Workers**
- [ ] Start 3 worker processes:
  ```bash
  python scripts/queue/start_workers.py --count 3 --capabilities "all"
  ```
- [ ] Verify workers registered in database:
  ```sql
  SELECT * FROM workers WHERE heartbeat_utc > datetime('now', '-1 minute');
  ```

**T-0:40 - Validation**
- [ ] Run validation script:
  ```bash
  python scripts/queue/validate_migration.py \
    --db-path "C:/Data/queue/queue.db" \
    --run-integration-test
  ```
- [ ] All checks passing

**T-0:50 - Smoke Tests**
- [ ] Enqueue test tasks via API
- [ ] Verify workers claim and execute tasks
- [ ] Check task status updates
- [ ] Test task cancellation
- [ ] Verify error handling

**T-1:00 - Resume Operations**
- [ ] Resume task intake: `POST /api/admin/resume-intake`
- [ ] Disable maintenance mode: `POST /api/admin/maintenance-mode OFF`
- [ ] Announce service restored

**T-1:05 - Monitoring (First Hour)**
- [ ] Monitor worker heartbeats
- [ ] Monitor task throughput
- [ ] Monitor error rates
- [ ] Monitor database size and performance
- [ ] Check for SQLITE_BUSY errors

**T-2:00 - Deployment Complete**
- [ ] Document deployment results
- [ ] Update runbook with lessons learned
- [ ] Send completion notice

---

### Rollback Decision Tree

```
                    ┌─────────────────────┐
                    │  Issue Detected?    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Severity Level?    │
                    └──┬────────┬────────┬┘
                       │        │        │
             ┌─────────▼─┐   ┌─▼──┐   ┌─▼────────┐
             │  Critical  │   │ High│   │ Medium/Low│
             └─────┬──────┘   └─┬──┘   └─┬────────┘
                   │            │         │
         ┌─────────▼──────┐     │    ┌────▼────────┐
         │Emergency Rollback│    │    │ Investigate │
         │   (2-5 min)      │    │    │  & Monitor  │
         └──────────────────┘    │    └─────────────┘
                                 │
                          ┌──────▼──────┐
                          │Planned Rollback│
                          │  (10-15 min)  │
                          └───────────────┘

Critical: Data loss, service down, workers crashed
High: Performance degradation >50%, high error rate
Medium/Low: Minor issues, can be fixed without rollback
```

**Critical Issues** (Emergency Rollback):
- Database corruption
- All workers crashing
- Data loss detected
- API unresponsive

**High Severity Issues** (Planned Rollback):
- Performance degradation >50% vs baseline
- Error rate >5%
- Intermittent worker crashes
- Memory leaks

**Medium/Low Issues** (Monitor & Fix):
- Occasional SQLITE_BUSY errors (<1%)
- Performance within 20% of baseline
- Minor bugs in non-critical paths

---

## Testing Strategy

### Pre-Deployment Tests

**Unit Tests** (Worker 10):
- [ ] Test migration utilities (dry-run mode)
- [ ] Test rollback scripts (mock environment)
- [ ] Test validation scripts (various scenarios)

**Integration Tests** (Worker 07):
- [ ] Test end-to-end task flow with queue backend
- [ ] Test migration from in-memory to queue
- [ ] Test rollback from queue to in-memory
- [ ] Test worker crash recovery

**Performance Tests** (Worker 09):
- [ ] Baseline: In-memory backend throughput
- [ ] Compare: Queue backend throughput
- [ ] Target: Queue ≥ 50% of in-memory speed
- [ ] Stress test: 10x normal load

### Post-Deployment Monitoring

**Day 1**: Intensive monitoring
- Check every 15 minutes for first 4 hours
- Monitor worker heartbeats
- Check error logs
- Validate task completion rates

**Week 1**: Daily monitoring
- Daily health checks
- Review error patterns
- Performance metrics vs baseline
- Database size growth

**Week 2-4**: Weekly monitoring
- Weekly status report
- Performance trends
- Backup verification
- Plan for 100% rollout (if canary)

---

## Documentation Deliverables

### For Phase 3 (Week 4)

1. **Migration Guide** (`_meta/docs/QUEUE_MIGRATION_GUIDE.md`)
   - Prerequisites checklist
   - Step-by-step deployment procedure
   - Rollback instructions
   - Troubleshooting common issues

2. **Operational Runbook** (`_meta/docs/QUEUE_OPERATIONS_RUNBOOK.md`)
   - Daily operational tasks
   - Monitoring dashboards
   - Incident response procedures
   - Backup and restore procedures

3. **Configuration Reference** (`_meta/docs/QUEUE_CONFIGURATION.md`)
   - All configuration options
   - Recommended settings for Windows
   - Tuning guide (from Worker 09's research)

4. **Troubleshooting Guide** (`_meta/docs/QUEUE_TROUBLESHOOTING.md`)
   - Common error messages and solutions
   - Performance debugging
   - Database maintenance
   - Worker management

---

## Success Metrics

### Phase 1 Success (This Planning Document)

- [x] Migration scenarios identified and documented
- [x] Utilities designed (initialize, migrate, rollback, validate)
- [x] Rollback procedures defined (emergency and planned)
- [x] Operational runbook created
- [x] Testing strategy outlined
- [x] Documentation plan defined

### Phase 3 Success (Week 4 Implementation)

- [ ] All utilities implemented and tested
- [ ] Successful staging deployment with rollback test
- [ ] Documentation complete and reviewed
- [ ] Runbook validated in staging
- [ ] Ready for production deployment

### Post-Deployment Success

- [ ] Production deployment completed within 2-hour window
- [ ] Zero data loss during migration
- [ ] Rollback procedure validated (test or actual)
- [ ] Performance targets met (≥50% of baseline)
- [ ] No critical incidents in first week

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Data loss during migration** | Low | Critical | Drain tasks before deploy, export state |
| **Rollback doesn't work** | Low | Critical | Test rollback in staging, keep fallback enabled |
| **Long downtime** | Medium | High | Drain approach minimizes downtime, practice in staging |
| **Worker startup failure** | Low | High | Validate workers start before resuming intake |
| **Database initialization errors** | Low | Medium | Validate schema, test on Windows environment |
| **Config syntax errors** | Medium | Medium | Validate YAML before deploy, backup configs |
| **Performance regression** | Medium | Medium | Benchmark in staging, monitor closely post-deploy |

---

## Dependencies

### Requires from Phase 2

**Worker 01** (#321):
- Database schema scripts (for initialize_queue.py)
- PRAGMA configuration recommendations

**Worker 06** (#331):
- Backup utilities (for restore_backup.py)
- Database maintenance scripts

### Requires from Phase 3

**Worker 10** (#339):
- QueuedTaskManager implementation (for integration)
- Configuration schema (task_backend toggle)

### Provides to

**Worker 07** (#333):
- Test fixtures for migration testing
- Rollback test procedures

**Worker 08** (#336):
- Migration guide content
- Operational runbook content

---

## Related Documentation

### Prerequisites
- [#339 Integration with BackgroundTaskManager](339-integrate-sqlite-queue-with-backgroundtaskmanager.md)
- [#321 Core Infrastructure](../Worker01/321-implement-sqlite-queue-core-infrastructure.md)
- [#331 Maintenance Utilities](../Worker06/331-implement-queue-maintenance-utilities.md)

### References
- [Worker Allocation Matrix](../Infrastructure_DevOps/QUEUE-SYSTEM-PARALLELIZATION.md)
- [Queue System Summary](../Infrastructure_DevOps/QUEUE-SYSTEM-SUMMARY.md)

---

## Notes

### Design Principles

**Fail-Safe Design**:
- Every deployment has rollback procedure
- Fallback mode always enabled initially
- Export state before destructive operations
- Validate before committing changes

**Operational Excellence**:
- Clear checklists for procedures
- Time estimates for each step
- Success criteria defined upfront
- Monitoring from day one

**Minimal Downtime**:
- Drain approach for clean cutover
- Fast rollback (≤5 minutes)
- Validate extensively in staging

### Future Improvements

**Zero-Downtime Migration** (Post-Phase 3):
- Dual-write to in-memory + queue
- Gradual traffic shifting
- Shadow mode validation

**Advanced Monitoring** (Post-Phase 3):
- Automated health checks
- Alerting on anomalies
- Dashboard for queue metrics

**Automated Rollback** (Post-Phase 3):
- Circuit breaker pattern
- Automatic rollback on high error rate
- Requires robust monitoring

---

**Status**: ✅ Phase 1 Planning Complete  
**Next Phase**: Integration planning during Week 2-3  
**Implementation**: Week 4 (days 5-7, after #339 complete)  
**Owner**: Worker 10 - Senior Engineer
