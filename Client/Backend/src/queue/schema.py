"""Database schema definitions and SQL constants for task queue."""

# Windows-optimized PRAGMA settings for SQLite
PRAGMAS = {
    "journal_mode": "WAL",  # Enable WAL for concurrency
    "synchronous": "NORMAL",  # Balance durability vs performance
    "busy_timeout": 5000,  # 5 seconds for lock retries
    "wal_autocheckpoint": 1000,  # Checkpoint every 1000 pages
    "foreign_keys": "ON",  # Enable FK constraints
    "temp_store": "MEMORY",  # Temp tables in memory
    "mmap_size": 134217728,  # 128MB memory-mapped I/O
    "page_size": 4096,  # Match filesystem block size
    "cache_size": -20000,  # ~20MB cache (negative = KiB)
}

# Task queue table schema
CREATE_TASK_QUEUE_TABLE = """
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
  
  -- Generated columns for JSON filtering
  -- region: from compatibility (worker matching), format: from payload (task data)
  region             TEXT GENERATED ALWAYS AS (json_extract(compatibility, '$.region')) VIRTUAL,
  format             TEXT GENERATED ALWAYS AS (json_extract(payload, '$.format')) VIRTUAL
);
"""

# Workers table schema
CREATE_WORKERS_TABLE = """
CREATE TABLE IF NOT EXISTS workers (
  worker_id      TEXT PRIMARY KEY,
  capabilities   TEXT NOT NULL,
  heartbeat_utc  DATETIME NOT NULL DEFAULT (datetime('now'))
);
"""

# Task logs table schema
CREATE_TASK_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS task_logs (
  log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id    INTEGER NOT NULL,
  at_utc     DATETIME NOT NULL DEFAULT (datetime('now')),
  level      TEXT NOT NULL,
  message    TEXT,
  details    TEXT,
  FOREIGN KEY (task_id) REFERENCES task_queue(id)
);
"""

# Indexes for task_queue table
CREATE_TASK_STATUS_PRIO_TIME_INDEX = """
CREATE INDEX IF NOT EXISTS ix_task_status_prio_time
  ON task_queue (status, priority, run_after_utc, id);
"""

CREATE_TASK_TYPE_STATUS_INDEX = """
CREATE INDEX IF NOT EXISTS ix_task_type_status
  ON task_queue (type, status);
"""

CREATE_TASK_REGION_INDEX = """
CREATE INDEX IF NOT EXISTS ix_task_region 
  ON task_queue (region);
"""

CREATE_TASK_FORMAT_INDEX = """
CREATE INDEX IF NOT EXISTS ix_task_format 
  ON task_queue (format);
"""

CREATE_TASK_IDEMPOTENCY_INDEX = """
CREATE UNIQUE INDEX IF NOT EXISTS uq_task_idempotency
  ON task_queue (idempotency_key)
  WHERE idempotency_key IS NOT NULL;
"""

# Index for task_logs table
CREATE_LOGS_TASK_INDEX = """
CREATE INDEX IF NOT EXISTS ix_logs_task 
  ON task_logs (task_id, at_utc);
"""

# Observability Views (Issue #329)

# Queue Status Summary View
CREATE_QUEUE_STATUS_SUMMARY_VIEW = """
CREATE VIEW IF NOT EXISTS v_queue_status_summary AS
SELECT
    status,
    COUNT(*) as task_count,
    ROUND(AVG(attempts), 2) as avg_attempts,
    MIN(created_at_utc) as oldest_task,
    MAX(created_at_utc) as newest_task
FROM task_queue
GROUP BY status;
"""

# Queue Type Summary View
CREATE_QUEUE_TYPE_SUMMARY_VIEW = """
CREATE VIEW IF NOT EXISTS v_queue_type_summary AS
SELECT
    type,
    status,
    COUNT(*) as task_count,
    ROUND(AVG(priority), 2) as avg_priority
FROM task_queue
GROUP BY type, status;
"""

# Worker Status View
CREATE_WORKER_STATUS_VIEW = """
CREATE VIEW IF NOT EXISTS v_worker_status AS
SELECT
    w.worker_id,
    w.capabilities,
    w.heartbeat_utc,
    COUNT(t.id) as active_tasks,
    ROUND((JULIANDAY('now') - JULIANDAY(w.heartbeat_utc)) * 86400) as seconds_since_heartbeat
FROM workers w
LEFT JOIN task_queue t ON t.locked_by = w.worker_id AND t.status = 'processing'
GROUP BY w.worker_id, w.capabilities, w.heartbeat_utc;
"""

# Task Performance View
CREATE_TASK_PERFORMANCE_VIEW = """
CREATE VIEW IF NOT EXISTS v_task_performance AS
SELECT
    type,
    status,
    COUNT(*) as task_count,
    ROUND(AVG(JULIANDAY(finished_at_utc) - JULIANDAY(processing_started_utc)) * 86400, 2) as avg_processing_seconds,
    ROUND(AVG(attempts), 2) as avg_attempts
FROM task_queue
WHERE finished_at_utc IS NOT NULL
GROUP BY type, status;
"""

# Recent Failures View
CREATE_RECENT_FAILURES_VIEW = """
CREATE VIEW IF NOT EXISTS v_recent_failures AS
SELECT
    id,
    type,
    status,
    attempts,
    error_message,
    finished_at_utc
FROM task_queue
WHERE status IN ('failed', 'dead_letter')
ORDER BY finished_at_utc DESC
LIMIT 100;
"""

# All schema creation statements in order
SCHEMA_STATEMENTS = [
    CREATE_TASK_QUEUE_TABLE,
    CREATE_WORKERS_TABLE,
    CREATE_TASK_LOGS_TABLE,
    CREATE_TASK_STATUS_PRIO_TIME_INDEX,
    CREATE_TASK_TYPE_STATUS_INDEX,
    CREATE_TASK_REGION_INDEX,
    CREATE_TASK_FORMAT_INDEX,
    CREATE_TASK_IDEMPOTENCY_INDEX,
    CREATE_LOGS_TASK_INDEX,
    CREATE_QUEUE_STATUS_SUMMARY_VIEW,
    CREATE_QUEUE_TYPE_SUMMARY_VIEW,
    CREATE_WORKER_STATUS_VIEW,
    CREATE_TASK_PERFORMANCE_VIEW,
    CREATE_RECENT_FAILURES_VIEW,
]
