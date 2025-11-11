# Production Optimization Guide

**For**: Future optimization when production data justifies it  
**Author**: Worker09 - Performance & Optimization Expert  
**Status**: Reference Document  
**Last Updated**: 2025-11-07

---

## Overview

This guide documents optimization techniques and tools to use **when production monitoring indicates a need**. Do not implement these optimizations prematurely.

**See Also**: [PERFORMANCE_MONITORING_STRATEGY.md](PERFORMANCE_MONITORING_STRATEGY.md) for when to optimize.

---

## Table of Contents

1. [Database Optimization](#database-optimization)
2. [PHP Code Optimization](#php-code-optimization)
3. [Caching Strategies](#caching-strategies)
4. [Profiling Tools](#profiling-tools)
5. [Load Testing](#load-testing)
6. [Common Bottlenecks](#common-bottlenecks)

---

## Database Optimization

### When to Use
- Slow query log shows queries > 100ms
- Database CPU usage > 70%
- Task claim operation is slow

### Index Optimization

#### Analyze Current Indexes
```sql
-- Show all indexes on tasks table
SHOW INDEX FROM tasks;

-- Show table structure
DESCRIBE tasks;

-- Analyze table
ANALYZE TABLE tasks;
```

#### Identify Missing Indexes
```sql
-- Use EXPLAIN to analyze query performance
EXPLAIN SELECT * FROM tasks 
WHERE type_id = 1 
AND status = 'pending' 
ORDER BY created_at ASC 
LIMIT 1;

-- Look for:
-- - "type: ALL" = full table scan (BAD)
-- - "Extra: Using filesort" = no index for ORDER BY (BAD)
-- - "possible_keys: NULL" = no usable index (BAD)
```

#### Common Index Patterns

**For Task Claim Queries:**
```sql
-- Composite index for claim operation
-- Order matters: most selective column first
CREATE INDEX idx_claim ON tasks(type_id, status, created_at);

-- This optimizes:
-- SELECT * FROM tasks 
-- WHERE type_id = ? AND status = 'pending' 
-- ORDER BY created_at ASC LIMIT 1;
```

**For Task Status Queries:**
```sql
-- Index for filtering by status
CREATE INDEX idx_status_created ON tasks(status, created_at);

-- This optimizes:
-- SELECT * FROM tasks WHERE status = 'pending' ORDER BY created_at;
```

**For Task Type Lookups:**
```sql
-- Unique index on task type name (if not already present)
CREATE UNIQUE INDEX idx_type_name ON task_types(name);

-- This optimizes:
-- SELECT * FROM task_types WHERE name = ?;
```

#### Index Trade-offs

**Pros:**
- Faster SELECT queries
- Faster WHERE clause evaluation
- Faster ORDER BY operations

**Cons:**
- Slower INSERT/UPDATE/DELETE (index must be updated)
- Additional disk space
- Index maintenance overhead

**Rule**: Only add indexes when slow query log shows specific slow queries.

### Query Optimization

#### Avoid N+1 Queries

**Before (N+1 problem):**
```php
// Get all tasks
$tasks = $db->query("SELECT * FROM tasks")->fetchAll();

// For each task, get its type (N queries)
foreach ($tasks as $task) {
    $type = $db->query(
        "SELECT * FROM task_types WHERE id = ?", 
        [$task['type_id']]
    )->fetch();
    $task['type_name'] = $type['name'];
}
```

**After (Single JOIN):**
```php
// Get tasks with types in one query
$tasks = $db->query("
    SELECT 
        t.*,
        tt.name as type_name,
        tt.schema as type_schema
    FROM tasks t
    JOIN task_types tt ON t.type_id = tt.id
")->fetchAll();
```

#### Use Prepared Statements
```php
// Already used throughout - no changes needed
$stmt = $db->prepare("SELECT * FROM tasks WHERE id = ?");
$stmt->execute([$id]);
```

#### Limit Result Sets
```php
// Add LIMIT when you don't need all results
$stmt = $db->prepare("
    SELECT * FROM tasks 
    WHERE type_id = ? AND status = 'pending'
    LIMIT 100
");
```

### Connection Pooling

**Already implemented** via singleton pattern in TaskManager. No changes needed.

---

## PHP Code Optimization

### When to Use
- Profiler shows PHP bottlenecks
- CPU usage high but database is fast
- Response time high without slow queries

### Enable OPcache

**In production php.ini:**
```ini
[opcache]
opcache.enable=1
opcache.enable_cli=0
opcache.memory_consumption=128
opcache.interned_strings_buffer=8
opcache.max_accelerated_files=10000
opcache.validate_timestamps=0  # Don't check for changes in production
opcache.save_comments=0        # Save memory
opcache.fast_shutdown=1
```

**Impact**: 2-3x faster PHP execution

### JSON Optimization

**Before:**
```php
// Full options every time
$json = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
```

**After:**
```php
// Minimal flags for API responses
$json = json_encode($data, JSON_UNESCAPED_SLASHES);

// Pretty print only in development
if ($_ENV['APP_ENV'] === 'development') {
    $json = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
} else {
    $json = json_encode($data, JSON_UNESCAPED_SLASHES);
}
```

### Memory Optimization

**Unset Large Variables:**
```php
$largeResult = $db->query("SELECT * FROM tasks")->fetchAll();
// Process results...
unset($largeResult);  // Free memory
```

**Use Generators for Large Datasets:**
```php
function getTasks($db) {
    $stmt = $db->query("SELECT * FROM tasks");
    while ($row = $stmt->fetch()) {
        yield $row;  // One at a time, not all in memory
    }
}

// Usage
foreach (getTasks($db) as $task) {
    // Process one task at a time
}
```

### Function-Level Optimization

**Only if profiler shows this function is hot:**

```php
// Before: Multiple string operations
function formatTaskId($id) {
    return 'task_' . strtoupper(str_pad($id, 10, '0', STR_PAD_LEFT));
}

// After: Single sprintf (if profiler shows benefit)
function formatTaskId($id) {
    return sprintf('TASK_%010d', $id);
}
```

**Note**: Only optimize if profiler shows this is a bottleneck.

---

## Caching Strategies

### When to Use
- Same data read frequently (monitoring shows this)
- Read-heavy workload (reads >> writes)
- Data changes infrequently

### Schema Caching

**Use Case**: JSON schemas are parsed repeatedly but rarely change

```php
class SchemaCache {
    private static $cache = [];
    
    /**
     * Get parsed schema, caching the result
     */
    public static function get($typeId, $schemaJson) {
        if (!isset(self::$cache[$typeId])) {
            self::$cache[$typeId] = json_decode($schemaJson, true);
        }
        return self::$cache[$typeId];
    }
    
    /**
     * Invalidate cache for a type (call when type is updated)
     */
    public static function invalidate($typeId) {
        unset(self::$cache[$typeId]);
    }
    
    /**
     * Clear entire cache (call on deployment)
     */
    public static function clear() {
        self::$cache = [];
    }
}

// Usage in validator
$schema = SchemaCache::get($typeId, $schemaJson);
$validator->validate($data, $schema);
```

**Impact**: Faster validation, less CPU usage

**Trade-off**: 
- Pros: Faster, less CPU
- Cons: Memory usage, cache invalidation complexity

### Task Type Caching

**Use Case**: Task types are read frequently but rarely change

```php
class TaskTypeCache {
    private static $cache = [];
    private static $cacheTime = 300;  // 5 minutes
    
    public static function get($db, $typeName) {
        $key = "type_$typeName";
        
        // Check cache
        if (isset(self::$cache[$key])) {
            $cached = self::$cache[$key];
            if (time() - $cached['time'] < self::$cacheTime) {
                return $cached['data'];
            }
        }
        
        // Cache miss - fetch from DB
        $stmt = $db->prepare("SELECT * FROM task_types WHERE name = ?");
        $stmt->execute([$typeName]);
        $type = $stmt->fetch();
        
        // Store in cache
        self::$cache[$key] = [
            'data' => $type,
            'time' => time()
        ];
        
        return $type;
    }
    
    public static function invalidate($typeName) {
        unset(self::$cache["type_$typeName"]);
    }
}
```

**Note**: Only implement if monitoring shows task_types queries are frequent.

### Response Caching

**Use Case**: Same API responses requested repeatedly

**Caution**: TaskManager has `Cache-Control: no-store` requirement. Only cache if appropriate.

```php
// Only for non-critical reads, if monitoring shows benefit
class ResponseCache {
    private static $cache = [];
    private static $ttl = 60;  // 1 minute
    
    public static function get($key) {
        if (isset(self::$cache[$key])) {
            $cached = self::$cache[$key];
            if (time() - $cached['time'] < self::$ttl) {
                return $cached['data'];
            }
        }
        return null;
    }
    
    public static function set($key, $data) {
        self::$cache[$key] = [
            'data' => $data,
            'time' => time()
        ];
    }
}

// Usage for read-only endpoints (if safe)
$cacheKey = "tasks_pending_" . $typeId;
$result = ResponseCache::get($cacheKey);
if ($result === null) {
    $result = $this->getTasks($typeId);
    ResponseCache::set($cacheKey, $result);
}
```

**Warning**: Be careful with caching. Stale data can cause bugs.

---

## Profiling Tools

### XDebug Profiler

**Setup:**
```ini
; php.ini
zend_extension=xdebug.so
xdebug.mode=profile
xdebug.output_dir=/tmp/xdebug
xdebug.trigger_value=XDEBUG_PROFILE
```

**Usage:**
```bash
# Profile a request
curl "http://localhost/api/tasks?XDEBUG_TRIGGER=XDEBUG_PROFILE"

# Analyze with KCacheGrind or QCacheGrind
kcachegrind /tmp/xdebug/cachegrind.out.*
```

**Look For:**
- Hot functions (most time spent)
- Function call counts
- Memory allocation

### Blackfire.io

**Best for production profiling** (low overhead):

```bash
# Install Blackfire agent
# See: https://blackfire.io/docs/up-and-running/installation

# Profile a request
blackfire curl http://localhost/api/tasks

# View results in web UI
# Shows: timeline, call graph, recommendations
```

### Custom Timing

**Simple built-in profiling:**

```php
class Profiler {
    private static $timings = [];
    
    public static function start($label) {
        self::$timings[$label] = microtime(true);
    }
    
    public static function end($label) {
        if (!isset(self::$timings[$label])) {
            return;
        }
        $duration = (microtime(true) - self::$timings[$label]) * 1000;
        error_log("PROFILE [$label]: {$duration}ms");
    }
    
    public static function report() {
        foreach (self::$timings as $label => $start) {
            $duration = (microtime(true) - $start) * 1000;
            error_log("PROFILE [$label]: {$duration}ms");
        }
    }
}

// Usage
Profiler::start('create_task');
$task = $this->createTask($data);
Profiler::end('create_task');
```

---

## Load Testing

### Apache Bench (ab)

**Simple load testing:**

```bash
# Test task creation
# First, create task.json with test data
cat > task.json << 'EOF'
{
  "type": "test_task",
  "data": {"key": "value"}
}
EOF

# Run load test
ab -n 1000 -c 10 \
   -p task.json \
   -T "application/json" \
   http://localhost/api/tasks

# Read results:
# - Requests per second
# - Time per request (mean)
# - Failed requests
# - Connection times (min/mean/max)
```

**Test health endpoint:**
```bash
ab -n 10000 -c 50 http://localhost/api/health

# Should be very fast (< 10ms)
```

### JMeter

**For complex scenarios:**
- Multiple endpoints
- Realistic user flows
- Ramp-up patterns
- Think times

**Setup**: Create JMeter test plan with:
1. Thread Group (users)
2. HTTP Request samplers
3. Listeners for results
4. Assertions for validation

### Locust

**Python-based load testing:**

```python
from locust import HttpUser, task, between

class TaskManagerUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_tasks(self):
        self.client.get("/api/tasks?type=test_task")
    
    @task(1)
    def create_task(self):
        self.client.post("/api/tasks", json={
            "type": "test_task",
            "data": {"key": "value"}
        })
    
    @task(1)
    def claim_task(self):
        self.client.post("/api/tasks/claim", json={
            "type": "test_task",
            "worker_id": "test_worker"
        })

# Run: locust -f locustfile.py --host=http://localhost
```

---

## Common Bottlenecks

### Database Bottlenecks

**Symptom**: Slow query log has many entries  
**Diagnosis**: 
```sql
-- Analyze query
EXPLAIN SELECT ...;

-- Check index usage
SHOW INDEX FROM tasks;
```
**Fix**: Add appropriate indexes

**Symptom**: High database CPU  
**Diagnosis**: Many queries per second  
**Fix**: 
- Reduce query count (combine queries)
- Add caching
- Optimize queries

### PHP Bottlenecks

**Symptom**: High CPU but few database queries  
**Diagnosis**: Profile with XDebug  
**Fix**: 
- Enable OPcache
- Optimize hot functions
- Reduce string operations

### Network Bottlenecks

**Symptom**: Large response times despite fast code  
**Diagnosis**: Large response sizes  
**Fix**:
- Paginate large responses
- Enable gzip compression
- Reduce response payload

### Concurrency Bottlenecks

**Symptom**: Good performance at low load, poor at high load  
**Diagnosis**: Locking or resource contention  
**Fix**:
- Check for table locks
- Optimize transactions
- Consider read replicas

---

## Optimization Workflow

1. **Identify Bottleneck**
   - Review slow query log
   - Check error logs
   - Profile with XDebug/Blackfire
   - Analyze monitoring data

2. **Measure Baseline**
   - Record current performance
   - P50, P95, P99 response times
   - Query times
   - Error rates

3. **Implement Fix**
   - Add index
   - Optimize query
   - Add caching
   - Optimize code

4. **Test**
   - Run load tests
   - Verify improvement
   - Check for regressions

5. **Deploy**
   - Deploy to production
   - Monitor metrics
   - Verify improvement in production

6. **Document**
   - Document what was optimized
   - Document why
   - Document measured improvement

---

## Optimization Checklist

### Before Optimizing
- [ ] Have production data showing issue
- [ ] Know the specific bottleneck
- [ ] Have baseline metrics
- [ ] Know what success looks like

### Database Optimization
- [ ] Analyzed slow query log
- [ ] Used EXPLAIN on slow queries
- [ ] Added only necessary indexes
- [ ] Tested impact of indexes
- [ ] Verified write performance not degraded

### Code Optimization
- [ ] Profiled to find hot path
- [ ] Optimized only hot functions
- [ ] Tested for correctness
- [ ] Measured improvement
- [ ] OPcache enabled in production

### Caching
- [ ] Identified cacheable data
- [ ] Designed cache invalidation
- [ ] Implemented cache with TTL
- [ ] Tested cache invalidation
- [ ] Measured cache hit rate

### Deployment
- [ ] Tested in staging
- [ ] Created rollback plan
- [ ] Deployed to production
- [ ] Monitored metrics
- [ ] Verified improvement

---

## Summary

**Remember**: Only optimize when production data shows a need.

**Process**:
1. Monitor production
2. Identify bottleneck with data
3. Measure baseline
4. Implement targeted fix
5. Verify improvement
6. Document

**Resources**:
- [PERFORMANCE_MONITORING_STRATEGY.md](PERFORMANCE_MONITORING_STRATEGY.md) - When to optimize
- [ISSUE-TASKMANAGER-008](../issues/new/Worker09/ISSUE-TASKMANAGER-008-performance-optimization.md) - Performance issue
- MySQL slow query log - Find slow queries
- XDebug/Blackfire - Profile PHP code

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-07  
**Status**: Reference for future use
