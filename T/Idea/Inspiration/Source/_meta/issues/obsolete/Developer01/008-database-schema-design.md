# Issue #008: Database Schema Design

**⚠️ OBSOLETE - PHP API NOT BEING IMPLEMENTED ⚠️**

**Status**: ❌ NOT APPLICABLE - REPLACED BY Developer06/008  
**Reason**: External TaskManager API already has database schema  
**Replacement**: See `Developer06/008-taskmanager-api-client-integration.md` for Python client

---

## ⚠️ Issue Superseded & Replaced

This issue was **incorrectly titled** and described implementing database schema for a PHP backend. 

**Actual Need**: Python client integration (now Developer06/008)

The external API (https://api.prismq.nomoos.cz/api/) already has its database. We just need a Python client to consume it.

---

## Original (Not Implemented) Overview

## Overview

Design and implement the complete database schema for the TaskManager API, including tables for task types, tasks, task logs, and API keys. Optimize for performance with proper indexes to achieve <10ms query times.

---

## Business Context

The database is the foundation of the entire TaskManager system. It must:
- Support high concurrency (10+ workers)
- Enable fast task claiming (<10ms)
- Provide audit trails for debugging
- Scale to thousands of tasks
- Support both SQLite (dev) and MySQL (prod)

**Impact**: Database design directly affects API performance and reliability.

---

## Complete Database Schema

### Table 1: task_types

Stores registered task type definitions with JSON Schema validation.

```sql
CREATE TABLE task_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(50) NOT NULL,
    param_schema TEXT NOT NULL,          -- JSON Schema definition
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, version)
);

-- Indexes for fast lookups
CREATE INDEX idx_task_types_name ON task_types(name);
CREATE INDEX idx_task_types_active ON task_types(is_active);
CREATE INDEX idx_task_types_name_version ON task_types(name, version);
```

**Expected Size**: ~100 rows (one per task type)  
**Query Performance Target**: <5ms for lookups

---

### Table 2: tasks

Main task queue table - most frequently accessed.

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',    -- pending, claimed, completed, failed
    params TEXT NOT NULL,                    -- JSON task parameters
    result TEXT,                             -- JSON result (when completed)
    error_message TEXT,                      -- Error details (when failed)
    dedupe_key VARCHAR(64) UNIQUE,           -- SHA256 hash for deduplication
    priority INTEGER DEFAULT 0,              -- Higher = more important
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    worker_id VARCHAR(255),                  -- Worker that claimed this task
    claimed_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_type_id) REFERENCES task_types(id),
    CHECK (status IN ('pending', 'claimed', 'completed', 'failed'))
);

-- CRITICAL INDEXES for <10ms claiming performance
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type_status ON tasks(task_type_id, status);
CREATE INDEX idx_tasks_priority_created ON tasks(priority DESC, created_at ASC);
CREATE INDEX idx_tasks_dedupe ON tasks(dedupe_key);
CREATE INDEX idx_tasks_worker ON tasks(worker_id);
CREATE INDEX idx_tasks_created ON tasks(created_at);
CREATE INDEX idx_tasks_completed ON tasks(completed_at);

-- Composite index for claiming queries
CREATE INDEX idx_tasks_claim ON tasks(status, task_type_id, priority DESC, created_at ASC);
```

**Expected Size**: Thousands to millions of rows  
**Query Performance Target**: <10ms for claims, <5ms for lookups

---

### Table 3: task_logs

Audit trail for all task events.

```sql
CREATE TABLE task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    event VARCHAR(50) NOT NULL,              -- created, claimed, completed, failed, retried
    worker_id VARCHAR(255),
    message TEXT,
    metadata TEXT,                            -- JSON for additional context
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- Indexes for audit queries
CREATE INDEX idx_task_logs_task_id ON task_logs(task_id);
CREATE INDEX idx_task_logs_event ON task_logs(event);
CREATE INDEX idx_task_logs_worker ON task_logs(worker_id);
CREATE INDEX idx_task_logs_created ON task_logs(created_at);
```

**Expected Size**: 3-5x tasks table (multiple events per task)  
**Query Performance Target**: <20ms for audit queries

---

### Table 4: api_keys

API authentication and authorization.

```sql
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash VARCHAR(64) UNIQUE NOT NULL,    -- SHA256 hash of API key
    key_prefix VARCHAR(20) NOT NULL,         -- First 12 chars for display
    name VARCHAR(255) NOT NULL,              -- Human-readable name
    permissions TEXT NOT NULL,               -- JSON array of permissions
    rate_limit INTEGER DEFAULT 100,          -- Requests per minute
    is_active BOOLEAN DEFAULT 1,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for authentication
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
```

**Expected Size**: ~20-50 rows (one per worker/developer)  
**Query Performance Target**: <2ms for authentication

---

## Database Configuration

### SQLite Configuration (Development & Shared Hosting)

```sql
-- Optimize for concurrent access
PRAGMA journal_mode = WAL;              -- Write-Ahead Logging for concurrency
PRAGMA synchronous = NORMAL;            -- Balance between safety and speed
PRAGMA foreign_keys = ON;               -- Enforce foreign key constraints
PRAGMA cache_size = 10000;              -- 10MB cache
PRAGMA temp_store = MEMORY;             -- Store temp tables in memory
PRAGMA mmap_size = 268435456;           -- 256MB memory-mapped I/O
```

### MySQL Configuration (Production)

```sql
-- InnoDB engine for transactions and foreign keys
SET default_storage_engine = InnoDB;
SET innodb_flush_log_at_trx_commit = 2;
SET innodb_buffer_pool_size = 1073741824;  -- 1GB buffer pool

-- Character set
SET character_set_server = utf8mb4;
SET collation_server = utf8mb4_unicode_ci;
```

---

## Migration System

### Migration File Structure

```
database/
├── schema.sql                  -- Complete schema for fresh install
├── migrations/
│   ├── 001_initial_schema.sql
│   ├── 002_add_task_logs.sql
│   ├── 003_add_api_keys.sql
│   └── ...
└── seeds/
    └── dev_data.sql           -- Sample data for development
```

### Migration Manager (src/Database/MigrationManager.php)

```php
<?php
namespace TaskManager\Database;

use TaskManager\Core\Database;

class MigrationManager {
    private Database $db;
    
    public function __construct(Database $db) {
        $this->db = $db;
    }
    
    /**
     * Run all pending migrations
     */
    public function migrate(): void {
        $this->createMigrationsTable();
        
        $applied = $this->getAppliedMigrations();
        $pending = $this->getPendingMigrations($applied);
        
        foreach ($pending as $migration) {
            $this->runMigration($migration);
        }
    }
    
    /**
     * Create migrations tracking table
     */
    private function createMigrationsTable(): void {
        $sql = "CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )";
        $this->db->execute($sql);
    }
    
    /**
     * Get list of applied migrations
     */
    private function getAppliedMigrations(): array {
        $sql = "SELECT migration FROM migrations ORDER BY id";
        $results = $this->db->fetchAll($sql);
        return array_column($results, 'migration');
    }
    
    /**
     * Get list of pending migrations
     */
    private function getPendingMigrations(array $applied): array {
        $files = glob(__DIR__ . '/../../database/migrations/*.sql');
        sort($files);
        
        $pending = [];
        foreach ($files as $file) {
            $name = basename($file);
            if (!in_array($name, $applied)) {
                $pending[] = $name;
            }
        }
        
        return $pending;
    }
    
    /**
     * Run a single migration
     */
    private function runMigration(string $migration): void {
        $path = __DIR__ . '/../../database/migrations/' . $migration;
        $sql = file_get_contents($path);
        
        $this->db->beginTransaction();
        
        try {
            $this->db->execute($sql);
            
            $this->db->execute(
                "INSERT INTO migrations (migration) VALUES (?)",
                [$migration]
            );
            
            $this->db->commit();
            
            echo "Applied migration: {$migration}\n";
            
        } catch (\Exception $e) {
            $this->db->rollback();
            throw new \RuntimeException(
                "Migration failed: {$migration}. Error: " . $e->getMessage()
            );
        }
    }
}
```

---

## Performance Optimization

### Query Optimization Guidelines

1. **Always use indexes** for WHERE, JOIN, ORDER BY columns
2. **Avoid SELECT *** - select only needed columns
3. **Use LIMIT** for large result sets
4. **Use transactions** for multi-query operations
5. **Monitor query plans** with EXPLAIN

### Example Optimized Claim Query

```sql
-- Fast claim query (<10ms target)
SELECT * FROM tasks 
WHERE status = 'pending'           -- Uses idx_tasks_status
  AND task_type_id = ?             -- Uses idx_tasks_type_status
ORDER BY priority DESC,            -- Uses idx_tasks_claim
         created_at ASC
LIMIT 1;

-- Followed by atomic update
UPDATE tasks 
SET status = 'claimed', 
    worker_id = ?, 
    claimed_at = datetime('now')
WHERE id = ? AND status = 'pending';
```

### Index Usage Verification

```sql
-- Check if query uses indexes (SQLite)
EXPLAIN QUERY PLAN
SELECT * FROM tasks 
WHERE status = 'pending' AND task_type_id = 1
ORDER BY priority DESC, created_at ASC
LIMIT 1;

-- Expected output should include "USING INDEX idx_tasks_claim"
```

---

## Database Monitoring Views

### View: task_stats

```sql
CREATE VIEW task_stats AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(attempts) as avg_attempts,
    MAX(attempts) as max_attempts
FROM tasks
GROUP BY status;

-- Usage: SELECT * FROM task_stats;
-- Output:
-- | status    | count | avg_attempts | max_attempts |
-- |-----------|-------|--------------|--------------|
-- | pending   | 245   | 0.0          | 0            |
-- | claimed   | 15    | 0.2          | 1            |
-- | completed | 1230  | 1.1          | 3            |
-- | failed    | 45    | 3.0          | 3            |
```

### View: worker_stats

```sql
CREATE VIEW worker_stats AS
SELECT 
    worker_id,
    COUNT(*) as tasks_processed,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    AVG(JULIANDAY(completed_at) - JULIANDAY(claimed_at)) * 24 * 60 as avg_processing_time_minutes
FROM tasks
WHERE worker_id IS NOT NULL
GROUP BY worker_id;
```

---

## Testing Strategy

### Schema Tests

```php
class SchemaTest extends TestCase {
    public function testTablesCreated() {
        $this->assertTrue($this->tableExists('task_types'));
        $this->assertTrue($this->tableExists('tasks'));
        $this->assertTrue($this->tableExists('task_logs'));
        $this->assertTrue($this->tableExists('api_keys'));
    }
    
    public function testIndexesCreated() {
        $indexes = $this->getIndexes('tasks');
        $this->assertContains('idx_tasks_status', $indexes);
        $this->assertContains('idx_tasks_claim', $indexes);
    }
    
    public function testForeignKeysEnforced() {
        $this->expectException(\Exception::class);
        
        // Try to insert task with invalid task_type_id
        $this->db->execute(
            "INSERT INTO tasks (task_type_id, params) VALUES (?, ?)",
            [999999, '{}']
        );
    }
}
```

### Performance Tests

```php
class PerformanceTest extends TestCase {
    public function testClaimQueryPerformance() {
        // Create 10,000 pending tasks
        for ($i = 0; $i < 10000; $i++) {
            $this->createTask(['status' => 'pending']);
        }
        
        // Measure claim query time
        $start = microtime(true);
        
        $sql = "SELECT * FROM tasks 
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1";
        $task = $this->db->fetchOne($sql);
        
        $elapsed = (microtime(true) - $start) * 1000; // Convert to ms
        
        $this->assertLessThan(10, $elapsed, "Claim query took {$elapsed}ms (target: <10ms)");
    }
}
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] All 4 tables created successfully
- [ ] All indexes created
- [ ] Foreign key constraints enforced
- [ ] Check constraints enforced (status values)
- [ ] UNIQUE constraints work (dedupe_key, api_key_hash)
- [ ] Timestamps auto-populate correctly
- [ ] Migration system works
- [ ] Can rollback migrations
- [ ] Views created successfully

### Non-Functional Requirements
- [ ] Task claim queries <10ms (p95)
- [ ] Task lookups <5ms (p95)
- [ ] Authentication queries <2ms (p95)
- [ ] Audit log inserts <3ms (p95)
- [ ] Database supports 10+ concurrent connections
- [ ] WAL mode enables concurrent readers

### Testing
- [ ] Schema tests passing
- [ ] Performance tests passing
- [ ] Migration tests passing
- [ ] Foreign key tests passing
- [ ] Concurrent access tests passing

### Documentation
- [ ] Schema diagram created
- [ ] Index strategy documented
- [ ] Migration guide written
- [ ] Performance tuning guide written

---

## SOLID Principles

- **SRP**: Each table has single purpose
- **OCP**: Can add migrations without modifying existing
- **DIP**: Repository pattern abstracts database access

---

## Dependencies

### Depends On
- #001 - API Foundation (Database class)

### Blocks
- #003 - Task Types (needs task_types table)
- #004 - Task Creation (needs tasks table)
- #005 - Task Claiming (needs tasks table)
- #006 - Task Completion (needs tasks table)
- #007 - Authentication (needs api_keys table)

---

## Related Issues
- All TaskManager API issues depend on this

---

## Definition of Done

- [ ] All tables created with proper schema
- [ ] All indexes created and verified
- [ ] SQLite configuration optimized
- [ ] MySQL schema prepared
- [ ] Migration system implemented
- [ ] Rollback capability working
- [ ] Performance tests passing (<10ms claims)
- [ ] Monitoring views created
- [ ] Code reviewed by Developer10
- [ ] Documentation complete
- [ ] Can support 10+ concurrent workers

---

**Status**: Ready for Implementation  
**Estimated Timeline**: 2-3 days  
**Assignee**: Developer06 (Database Specialist)  
**Reviewer**: Developer10  
**Critical Performance Target**: <10ms task claiming
