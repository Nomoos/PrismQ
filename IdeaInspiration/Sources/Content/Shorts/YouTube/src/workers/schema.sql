-- Worker Task Queue Schema
-- Version: 1.0
-- Created: 2025-11-11
-- Purpose: Persistent task queue for YouTube scraping workers
-- Platform: Windows with SQLite 3.35+ (WAL mode)

-- Drop existing views (in reverse dependency order)
DROP VIEW IF EXISTS v_task_stats;
DROP VIEW IF EXISTS v_worker_status;
DROP VIEW IF EXISTS v_active_tasks;

-- Drop existing tables (in reverse dependency order)
DROP TABLE IF EXISTS task_logs;
DROP TABLE IF EXISTS worker_heartbeats;
DROP TABLE IF EXISTS task_queue;

-- ============================================================================
-- TABLE: task_queue
-- Purpose: Main task storage and queue
-- ============================================================================
CREATE TABLE IF NOT EXISTS task_queue (
    -- Identity
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,  -- 'channel_scrape', 'trending_scrape', 'keyword_search'
    
    -- Parameters (stored as JSON text)
    parameters TEXT NOT NULL,  -- JSON: {"channel_url": "...", "top_n": 50}
    
    -- Scheduling
    priority INTEGER NOT NULL DEFAULT 5,  -- 1 (lowest) to 10 (highest)
    run_after_utc TEXT,  -- ISO 8601: '2025-11-11T12:00:00Z'
    
    -- Status tracking
    status TEXT NOT NULL DEFAULT 'queued',  
        -- 'queued', 'claimed', 'running', 'completed', 'failed', 'cancelled'
    
    -- Worker assignment
    claimed_by TEXT,  -- worker_id
    claimed_at TEXT,  -- ISO 8601 timestamp
    
    -- Retry logic
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    
    -- Results
    result_data TEXT,  -- JSON result data
    error_message TEXT,  -- Error details if failed
    
    -- Timestamps
    created_at TEXT NOT NULL,  -- ISO 8601 timestamp
    updated_at TEXT NOT NULL,  -- ISO 8601 timestamp
    completed_at TEXT,  -- ISO 8601 timestamp
    
    -- Constraints
    CHECK (priority BETWEEN 1 AND 10),
    CHECK (retry_count <= max_retries),
    CHECK (status IN ('queued', 'claimed', 'running', 'completed', 'failed', 'cancelled'))
);

-- Indexes for fast claiming (critical for performance)
CREATE INDEX IF NOT EXISTS idx_task_queue_claiming 
    ON task_queue(status, priority DESC, created_at DESC)
    WHERE status = 'queued';

-- Index for monitoring queries
CREATE INDEX IF NOT EXISTS idx_task_queue_worker
    ON task_queue(claimed_by, status);

-- Index for time-based queries
CREATE INDEX IF NOT EXISTS idx_task_queue_created
    ON task_queue(created_at);

-- ============================================================================
-- TABLE: worker_heartbeats
-- Purpose: Track active workers and their health
-- ============================================================================
CREATE TABLE IF NOT EXISTS worker_heartbeats (
    worker_id TEXT PRIMARY KEY,
    last_heartbeat TEXT NOT NULL,  -- ISO 8601 timestamp
    tasks_processed INTEGER NOT NULL DEFAULT 0,
    tasks_failed INTEGER NOT NULL DEFAULT 0,
    current_task_id INTEGER,  -- Reference to task_queue.id
    strategy TEXT NOT NULL DEFAULT 'LIFO',  -- 'FIFO', 'LIFO', 'PRIORITY'
    
    -- Metadata
    started_at TEXT NOT NULL,  -- ISO 8601 timestamp
    updated_at TEXT NOT NULL,  -- ISO 8601 timestamp
    
    FOREIGN KEY (current_task_id) REFERENCES task_queue(id)
);

-- Index for finding stale workers
CREATE INDEX IF NOT EXISTS idx_worker_heartbeat
    ON worker_heartbeats(last_heartbeat);

-- ============================================================================
-- TABLE: task_logs
-- Purpose: Audit trail and debugging
-- ============================================================================
CREATE TABLE IF NOT EXISTS task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    worker_id TEXT,
    event_type TEXT NOT NULL,  
        -- 'created', 'claimed', 'started', 'progress', 'completed', 'failed', 'retry'
    message TEXT,
    details TEXT,  -- JSON for structured data
    timestamp TEXT NOT NULL,  -- ISO 8601 timestamp
    
    FOREIGN KEY (task_id) REFERENCES task_queue(id),
    FOREIGN KEY (worker_id) REFERENCES worker_heartbeats(worker_id)
);

-- Index for task history queries
CREATE INDEX IF NOT EXISTS idx_task_logs_task
    ON task_logs(task_id, timestamp);

-- Index for worker activity queries
CREATE INDEX IF NOT EXISTS idx_task_logs_worker
    ON task_logs(worker_id, timestamp);

-- ============================================================================
-- VIEW: v_active_tasks
-- Purpose: Monitor currently active tasks
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_active_tasks AS
SELECT 
    t.id,
    t.task_type,
    t.status,
    t.claimed_by,
    t.priority,
    t.retry_count,
    t.created_at,
    t.claimed_at,
    CAST((julianday('now') - julianday(t.created_at)) * 24 * 60 AS INTEGER) as age_minutes
FROM task_queue t
WHERE t.status IN ('queued', 'claimed', 'running');

-- ============================================================================
-- VIEW: v_worker_status
-- Purpose: Monitor worker health and activity
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_worker_status AS
SELECT 
    w.worker_id,
    w.last_heartbeat,
    w.tasks_processed,
    w.tasks_failed,
    w.strategy,
    t.task_type as current_task_type,
    t.id as current_task_id,
    CAST((julianday('now') - julianday(w.last_heartbeat)) * 60 AS INTEGER) as minutes_since_heartbeat
FROM worker_heartbeats w
LEFT JOIN task_queue t ON w.current_task_id = t.id;

-- ============================================================================
-- VIEW: v_task_stats
-- Purpose: Task statistics for monitoring and analytics
-- ============================================================================
CREATE VIEW IF NOT EXISTS v_task_stats AS
SELECT 
    task_type,
    status,
    COUNT(*) as count,
    AVG(retry_count) as avg_retries,
    MIN(created_at) as oldest,
    MAX(created_at) as newest
FROM task_queue
GROUP BY task_type, status;
