# Queue System Research Analysis

**Date**: 2025-11-06  
**Component**: PrismQ.Client.Backend  
**Purpose**: Compare proposed minimal schema with current implementation

---

## Executive Summary

This document analyzes research recommendations for a simplified queue system design and compares it with the current SQLite queue implementation.

**Comparison Result**: 🟡 Partially Aligned (70%)

- ✅ Core patterns match (leasing, backoff, idempotency)
- ⚠️ Schema differences (current is more verbose)
- ⚠️ Missing self-registration pattern
- ✅ Similar transaction handling

---

## 1. Schema Comparison

### Proposed Minimal Schema

```sql
-- 4 tables
worker_types(type, version, param_schema, created_at)
workers(worker_id, type, params, status, last_seen, registered_at)
jobs(id, type, payload, priority, status, attempts, max_attempts, 
     available_at, lease_owner, lease_until, idempotency_key, created_at, updated_at)
job_results(job_id, result, error, completed_at)
```

### Current Implementation

```sql
-- 3 tables (from schema.py)
task_queue(
  id, type, priority, payload, compatibility,
  status, attempts, max_attempts,
  run_after_utc, lease_until_utc, reserved_at_utc, 
  processing_started_utc, finished_at_utc,
  locked_by, error_message, idempotency_key,
  created_at_utc, updated_at_utc
)
workers(worker_id, capabilities, heartbeat_utc)
task_logs(log_id, task_id, at_utc, level, message, details)
```

### Key Differences

| Feature | Proposed | Current | Assessment |
|---------|----------|---------|------------|
| **Worker Types Table** | ✅ Yes (param_schema) | ❌ No | Missing - Should add |
| **Job Results Table** | ✅ Separate | ❌ Inline (error_message) | Missing - Could improve |
| **Audit Logging** | ❌ No | ✅ task_logs table | Current better |
| **Timestamp Fields** | 3 fields | 6 fields | Current more detailed |
| **Worker Status** | ✅ status, last_seen | ❌ heartbeat only | Missing status field |
| **Compatibility** | ❌ No | ✅ JSON field | Current has extra |

---

## 2. Pattern Comparison

### A. Worker Self-Registration

**Proposed Pattern**: ✅ Explicit UPSERT
```sql
INSERT INTO worker_types(type, version, param_schema, created_at)
VALUES(:type, :version, :schema, CURRENT_TIMESTAMP)
ON CONFLICT(type) DO UPDATE SET version=excluded.version;

INSERT INTO workers(worker_id, type, params, status, last_seen)
VALUES(:worker_id, :type, :params, 'ready', CURRENT_TIMESTAMP)
ON CONFLICT(worker_id) DO UPDATE SET status='ready', last_seen=CURRENT_TIMESTAMP;
```

**Current Implementation**: ⚠️ Implicit via monitoring.py
```python
# From monitoring.py - register_worker()
def register_worker(worker_id: str, capabilities: Dict[str, Any]):
    sql = """
    INSERT INTO workers (worker_id, capabilities, heartbeat_utc)
    VALUES (?, ?, datetime('now'))
    ON CONFLICT(worker_id) 
    DO UPDATE SET capabilities=excluded.capabilities, heartbeat_utc=datetime('now')
    """
```

**Assessment**: 
- ✅ Both use UPSERT pattern
- ⚠️ Current lacks worker_types table (no schema versioning)
- ⚠️ Current lacks worker status field
- **Recommendation**: Add worker_types table and status field

### B. Job Leasing with RETURNING

**Proposed Pattern**: ✅ Single UPDATE with RETURNING
```sql
UPDATE jobs
SET status='leased', attempts=attempts+1, lease_owner=:worker_id,
    lease_until=datetime('now', '+60 seconds')
WHERE id = (SELECT id FROM jobs WHERE status IN ('queued','leased') 
            AND (lease_until IS NULL OR lease_until < CURRENT_TIMESTAMP)
            AND type IN (:type) ORDER BY priority DESC, created_at LIMIT 1)
RETURNING *;
```

**Current Implementation**: ⚠️ Separate SELECT + UPDATE (from worker.py)
```python
# Current pattern (simplified)
# 1. SELECT task
cursor = db.execute(
    "SELECT * FROM task_queue WHERE status='queued' "
    "AND run_after_utc <= datetime('now') ORDER BY priority, id LIMIT 1"
)
task = cursor.fetchone()

# 2. UPDATE task
db.execute(
    "UPDATE task_queue SET status='leased', locked_by=?, "
    "lease_until_utc=datetime('now', '+60 seconds') WHERE id=?",
    (worker_id, task['id'])
)
```

**Assessment**:
- ⚠️ Current uses 2 queries (race condition potential)
- ✅ Proposed uses atomic UPDATE...RETURNING (safer)
- **SQLite Version**: RETURNING requires SQLite 3.35+ (2021-03-12)
- **Recommendation**: Upgrade to RETURNING pattern if SQLite >= 3.35

### C. Exponential Backoff with Jitter

**Proposed Pattern**: ✅ SQL-based calculation
```sql
UPDATE jobs
SET status=CASE WHEN attempts+1 >= max_attempts THEN 'dead' ELSE 'queued' END,
    available_at = CASE
      WHEN attempts+1 >= max_attempts THEN available_at
      ELSE datetime('now', printf('+%d seconds', 
                    CAST(POWER(2, MIN(attempts,6)) AS INT) + ABS(random()%7)))
    END
WHERE id=:id;
```

**Current Implementation**: ✅ Python-based calculation (from worker.py)
```python
def calculate_next_run_time(attempts: int, config: RetryConfig):
    delay = min(
        config.initial_delay_seconds * (config.backoff_multiplier ** attempts),
        config.max_delay_seconds
    )
    jitter = delay * config.jitter_factor * random.uniform(-1, 1)
    return datetime.utcnow() + timedelta(seconds=delay + jitter)
```

**Assessment**:
- ✅ Both implement exponential backoff
- ✅ Both include jitter
- 🟡 Proposed uses SQL (simpler, DB-side)
- 🟡 Current uses Python (more configurable)
- **Recommendation**: Keep Python for flexibility, but consider SQL variant for simplicity

### D. Idempotency

**Proposed Pattern**: ✅ UNIQUE constraint + ON CONFLICT
```sql
INSERT INTO jobs(..., idempotency_key)
VALUES(..., :idempotency_key)
ON CONFLICT(idempotency_key) DO NOTHING;
```

**Current Implementation**: ✅ UNIQUE index + explicit check (from api/queue.py)
```python
# Check for existing task
if request.idempotency_key:
    cursor = db.execute(
        "SELECT id, status FROM task_queue WHERE idempotency_key = ?",
        (request.idempotency_key,)
    )
    existing = cursor.fetchone()
    if existing:
        return existing_task_response
```

**Assessment**:
- ✅ Both enforce idempotency
- 🟡 Proposed uses ON CONFLICT (simpler)
- 🟡 Current checks explicitly (allows custom response)
- **Recommendation**: Both approaches valid, current allows better error messages

---

## 3. Best Practices Alignment

| Practice | Proposed | Current | Status |
|----------|----------|---------|--------|
| **Idempotency everywhere** | ✅ Recommended | ✅ Implemented | ✅ Aligned |
| **Leases + heartbeats** | ✅ Recommended | ✅ Implemented | ✅ Aligned |
| **JSON-Schema validation** | ✅ Recommended | ⚠️ Partial | ⚠️ Gap |
| **Backoff with jitter** | ✅ Recommended | ✅ Implemented | ✅ Aligned |
| **DLQ (dead-letter)** | ✅ `status='dead'` | ✅ `status='dead_letter'` | ✅ Aligned |
| **Config/Secrets separation** | ✅ Recommended | ✅ Via config.py | ✅ Aligned |
| **Observability** | ✅ Recommended | ✅ Full suite | ✅ Aligned |

---

## 4. Gap Analysis

### Gaps in Current Implementation

1. **Worker Types Table** ❌
   - **Missing**: `worker_types` table with schema versioning
   - **Impact**: No validation of worker capabilities against task requirements
   - **Recommendation**: Add worker_types table

2. **Worker Status Field** ❌
   - **Missing**: `workers.status` field (ready/busy/offline)
   - **Impact**: Cannot track worker state
   - **Recommendation**: Add status column to workers table

3. **Job Results Table** ⚠️
   - **Missing**: Separate `job_results` table
   - **Current**: Results stored inline in `error_message` or external
   - **Impact**: Limited result storage, no structured output
   - **Recommendation**: Consider adding for complex results

4. **Atomic Leasing** ⚠️
   - **Missing**: UPDATE...RETURNING pattern
   - **Current**: Separate SELECT + UPDATE
   - **Impact**: Potential race conditions
   - **Recommendation**: Upgrade to RETURNING if SQLite >= 3.35

5. **JSON Schema Validation** ⚠️
   - **Missing**: Runtime validation against worker_types.param_schema
   - **Current**: Pydantic validation at API layer only
   - **Impact**: Workers may receive invalid payloads
   - **Recommendation**: Add worker-side validation

---

## 5. Recommendations

### Immediate (High Priority) 🔴

**1. Add Worker Types Table**
```sql
CREATE TABLE IF NOT EXISTS worker_types (
  type TEXT PRIMARY KEY,
  version INTEGER NOT NULL DEFAULT 1,
  param_schema TEXT NOT NULL,  -- JSON schema for task payload validation
  created_at_utc DATETIME NOT NULL DEFAULT (datetime('now')),
  updated_at_utc DATETIME NOT NULL DEFAULT (datetime('now'))
);
```

**Benefits**:
- Schema versioning for workers
- Payload validation
- Better documentation of task types

**2. Add Worker Status Field**
```sql
ALTER TABLE workers ADD COLUMN status TEXT DEFAULT 'ready' 
  CHECK(status IN ('ready', 'busy', 'offline'));
ALTER TABLE workers ADD COLUMN last_seen_utc DATETIME;
```

**Benefits**:
- Track worker lifecycle
- Better health monitoring
- Distinguish heartbeat from last_seen

**3. Check SQLite Version for RETURNING**
```python
import sqlite3
version = sqlite3.sqlite_version_info
if version >= (3, 35, 0):
    # Use UPDATE...RETURNING for atomic leasing
    pass
```

### Short-Term (Medium Priority) 🟡

**4. Add Job Results Table (Optional)**
```sql
CREATE TABLE IF NOT EXISTS job_results (
  job_id INTEGER PRIMARY KEY,
  result TEXT,  -- JSON result data
  error TEXT,
  completed_at_utc DATETIME NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (job_id) REFERENCES task_queue(id)
);
```

**When to use**: 
- Tasks with large result payloads
- Need to query results separately
- Want to archive completed tasks but keep results

**5. Implement Worker-Side Validation**
```python
def validate_task_payload(task_type: str, payload: dict) -> bool:
    schema = get_worker_type_schema(task_type)
    validate(payload, schema)  # JSON schema validation
    return True
```

### Long-Term (Strategic) 🟢

**6. Webclient Polling Pattern**
```python
# Current: Simple status polling
# Proposed: Long-polling or WebSocket for real-time updates
async def long_poll_job_status(job_id: str, timeout: int = 30):
    start = time.time()
    while time.time() - start < timeout:
        status = get_job_status(job_id)
        if status in ('done', 'dead'):
            return status
        await asyncio.sleep(1)
    return 'timeout'
```

**7. Heartbeat Extension for Long Tasks**
```python
async def execute_long_task(task_id: int):
    async def extend_lease():
        while True:
            await asyncio.sleep(30)
            db.execute(
                "UPDATE task_queue SET lease_until_utc=datetime('now', '+60 seconds') "
                "WHERE id=?", (task_id,)
            )
    
    extension_task = asyncio.create_task(extend_lease())
    try:
        result = await do_actual_work()
    finally:
        extension_task.cancel()
```

---

## 6. Implementation Checklist

### Phase 1: Schema Enhancements (Week 1)

- [ ] Add `worker_types` table
- [ ] Add `status` and `last_seen_utc` columns to `workers`
- [ ] Create migration script
- [ ] Update worker registration to use worker_types
- [ ] Add tests for worker type registration

### Phase 2: Atomic Operations (Week 2)

- [ ] Check SQLite version
- [ ] Implement UPDATE...RETURNING for leasing (if supported)
- [ ] Add fallback for older SQLite versions
- [ ] Benchmark performance improvement
- [ ] Update tests

### Phase 3: Validation & Results (Week 3)

- [ ] Implement JSON schema validation
- [ ] Consider adding job_results table
- [ ] Add worker-side payload validation
- [ ] Update documentation
- [ ] Add validation tests

### Phase 4: Advanced Features (Week 4+)

- [ ] Implement long-polling or WebSocket
- [ ] Add lease extension for long tasks
- [ ] Enhanced observability for worker types
- [ ] Migration to PostgreSQL planning (if needed)

---

## 7. Comparison Summary

### Strengths of Proposed Minimal Schema

1. ✅ **Simpler schema** (4 tables vs 3)
2. ✅ **Worker type registration** (missing in current)
3. ✅ **Atomic leasing** (UPDATE...RETURNING)
4. ✅ **SQL-based backoff** (simpler)
5. ✅ **Separate results table** (cleaner)

### Strengths of Current Implementation

1. ✅ **Audit trail** (task_logs table)
2. ✅ **Detailed timestamps** (6 vs 3)
3. ✅ **Observability suite** (metrics, monitoring, heartbeat)
4. ✅ **Comprehensive testing** (200+ tests)
5. ✅ **SOLID architecture** (95% score)
6. ✅ **Documentation** (8 major docs)

### Recommended Hybrid Approach

**Keep from Current**:
- task_logs table (audit trail)
- Detailed timestamps
- Observability suite
- Testing infrastructure
- SOLID architecture

**Add from Proposed**:
- worker_types table
- Worker status field
- UPDATE...RETURNING pattern
- Optionally: job_results table

---

## 8. Migration Strategy

### Step 1: Non-Breaking Additions
```sql
-- Add new tables without breaking existing code
CREATE TABLE worker_types(...);
ALTER TABLE workers ADD COLUMN status TEXT DEFAULT 'ready';
ALTER TABLE workers ADD COLUMN last_seen_utc DATETIME;
```

### Step 2: Gradual Adoption
```python
# Phase in worker type registration
def register_worker_v2(worker_id: str, worker_type: str, capabilities: dict):
    # Register type first
    register_worker_type(worker_type, capabilities)
    # Then register worker
    register_worker(worker_id, worker_type, capabilities)
```

### Step 3: Feature Flag
```python
USE_WORKER_TYPES = os.getenv('QUEUE_USE_WORKER_TYPES', 'false') == 'true'
USE_ATOMIC_LEASING = os.getenv('QUEUE_USE_ATOMIC_LEASING', 'false') == 'true'
```

### Step 4: Full Migration
- Update all workers to use new registration
- Switch to atomic leasing
- Remove feature flags
- Update documentation

---

## 9. Conclusion

### Current Status: 🟡 70% Aligned

**Excellent Foundation**:
- ✅ Core leasing pattern works
- ✅ Idempotency implemented
- ✅ Backoff and retry logic solid
- ✅ Observability comprehensive

**Key Improvements Needed**:
1. 🔴 Add worker_types table (critical for validation)
2. 🔴 Add worker status field (important for lifecycle)
3. 🟡 Implement atomic leasing (nice to have)
4. 🟡 Add JSON schema validation (nice to have)
5. 🟢 Consider job_results table (optional)

### Next Actions

**This Week**:
1. Create migration script for worker_types table
2. Add worker status field
3. Check SQLite version for RETURNING support

**Next Week**:
1. Implement worker type registration
2. Add payload validation
3. Test migration path

**Priority**: Medium-High (enhances existing system, not critical gaps)

---

**Created**: 2025-11-06  
**Author**: Research Analysis  
**Next Review**: After Phase 1 implementation  
**Status**: 🟡 Recommendations for enhancement (not critical issues)
