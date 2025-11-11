# Performance Monitoring Setup

## Overview

TaskManager includes minimal-overhead performance monitoring designed for production use. This monitoring helps identify performance bottlenecks based on real usage data.

## Philosophy: Deferred Optimization

We follow the principle: **"Make it work, make it right, make it fast - IN THAT ORDER"**

1. ✅ **Make it work**: TaskManager is functional
2. ✅ **Make it right**: Code is clean and tested  
3. ⏳ **Make it fast**: Optimize based on production data (when needed)

## Monitoring Infrastructure

### PerformanceMonitor Class

Located: `Backend/TaskManager/api/PerformanceMonitor.php`

**Features**:
- Minimal overhead (< 0.1ms per request)
- Only logs operations exceeding threshold (default: 200ms)
- No logs = everything is fast
- Can be disabled via environment variable

**Usage Example**:
```php
// Wrap a time-critical operation
$result = PerformanceMonitor::measure('create_task', function() use ($data) {
    return $this->createTask($data);
});

// Or time manually
$start = microtime(true);
$tasks = $this->getTasks($typeId);
$duration = (microtime(true) - $start) * 1000;
PerformanceMonitor::time('get_tasks', $duration);
```

### QueryProfiler Class

Located: `Backend/TaskManager/api/QueryProfiler.php`

**Features**:
- Automatic database query profiling
- Tracks query execution time and parameters
- Logs slow queries automatically
- Provides detailed query statistics
- Minimal overhead (< 0.1ms per query)

**Usage Example**:
```php
// Queries are automatically profiled when using Database class
$db = Database::getInstance();
$stmt = $db->prepare("SELECT * FROM tasks WHERE id = ?");
$stmt->execute([123]);

// Get query statistics
$stats = QueryProfiler::getSummary();
echo "Average query time: {$stats['average_time']}ms\n";
echo "Slow queries: {$stats['slow_queries']}\n";
```

**See**: [QUERY_PROFILER_GUIDE.md](QUERY_PROFILER_GUIDE.md) for complete documentation.

### Configuration

**Environment Variables**:
```bash
# PerformanceMonitor - Set threshold (default: 200ms)
PERFORMANCE_MONITOR_THRESHOLD=200
PERFORMANCE_MONITOR_ENABLED=true

# QueryProfiler - Set slow query threshold (default: 100ms)
QUERY_PROFILER_SLOW_THRESHOLD=100
QUERY_PROFILER_ENABLED=true
```

**In Code**:
```php
// Set threshold
PerformanceMonitor::setThreshold(100); // Log operations > 100ms

// Disable monitoring
PerformanceMonitor::disable();
```

## What Gets Monitored

Currently, performance monitoring can be added to:
- Task creation
- Task claiming
- Task completion
- Database queries
- JSON schema validation
- Any operation you want to measure

**Note**: Monitoring is **not yet implemented** in endpoints. Add it when deploying to production if you want to track performance.

## MySQL Slow Query Log

Enable in production MySQL configuration:

```ini
# my.cnf or my.ini
[mysqld]
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-query.log
long_query_time = 0.1  # Log queries > 100ms
log_queries_not_using_indexes = 0
```

**Analyze slow queries**:
```bash
# Most common slow queries
mysqldumpslow -s c -t 10 /var/log/mysql/slow-query.log

# Slowest queries
mysqldumpslow -s t -t 10 /var/log/mysql/slow-query.log
```

## Production Monitoring Workflow

### Week 1-2: Baseline Collection
1. Deploy to production
2. Enable performance monitoring (if not already enabled)
3. Enable MySQL slow query log
4. Monitor error logs daily
5. Note any user complaints

### Week 3-4: Analysis
1. Review performance logs
2. Check slow query log
3. Calculate baseline metrics (P50, P95, P99)
4. Identify any bottlenecks
5. Document findings

### Decision Point
After 2-4 weeks of monitoring:
- **No issues?** Continue monitoring, no optimization needed ✅
- **Issues found?** Follow optimization guide 🔧

## When to Optimize

Only optimize when one or more conditions are met:

1. **User Complaints** ⚠️ - Users report slowness
2. **Slow Operations** 🔴 - P95 response time > 500ms
3. **High Error Rate** 🔴 - Error rate > 1% due to timeouts
4. **Slow Queries** 🟡 - Same query in slow log > 10 times/day
5. **Resource Issues** 🟡 - CPU > 80% or Memory > 90%

**If none of these**: Don't optimize, continue monitoring ✅

## Optimization Resources

When optimization is needed, see:
- [PERFORMANCE_MONITORING_STRATEGY.md](../_meta/docs/PERFORMANCE_MONITORING_STRATEGY.md) - Complete strategy
- [PRODUCTION_OPTIMIZATION_GUIDE.md](../_meta/docs/PRODUCTION_OPTIMIZATION_GUIDE.md) - How to optimize
- [ISSUE-TASKMANAGER-008](../_meta/issues/new/Worker09/ISSUE-TASKMANAGER-008-performance-optimization.md) - Worker09 issue

## Example: Adding Monitoring to an Endpoint

**Before**:
```php
public function create() {
    $data = ApiResponse::getRequestBody();
    // ... validation ...
    $taskId = $this->insertTask($data);
    return ApiResponse::success(['task_id' => $taskId]);
}
```

**After** (with monitoring):
```php
require_once __DIR__ . '/PerformanceMonitor.php';

public function create() {
    $data = ApiResponse::getRequestBody();
    // ... validation ...
    
    // Monitor the database insert
    $taskId = PerformanceMonitor::measure('task_insert', function() use ($data) {
        return $this->insertTask($data);
    });
    
    return ApiResponse::success(['task_id' => $taskId]);
}
```

**Result**: If `insertTask()` takes > 200ms, you'll see:
```
SLOW [task_insert]: 345.67ms at 2025-11-07 10:30:45
```

## Log Analysis

**Check for slow operations**:
```bash
# Count slow operations
grep "SLOW" /var/log/php/error.log | wc -l

# Most common slow operations
grep "SLOW" /var/log/php/error.log | cut -d'[' -f2 | cut -d']' -f1 | sort | uniq -c | sort -rn

# Slowest operations
grep "SLOW" /var/log/php/error.log | grep -oP '\d+\.\d+ms' | sort -n | tail -20
```

## Best Practices

1. **Don't optimize prematurely** - Wait for production data
2. **Monitor first, optimize later** - Always measure before optimizing
3. **Focus on bottlenecks** - Optimize what production shows is slow
4. **Measure impact** - Verify optimizations actually help
5. **Keep it simple** - Simple code is better than fast code (usually)

## FAQ

**Q: Should I add monitoring to every function?**  
A: No. Only add to key operations (task CRUD, claiming). Excessive monitoring adds overhead.

**Q: What's the threshold value?**  
A: Default is 200ms. Adjust based on your needs. 100ms for critical operations, 500ms for background tasks.

**Q: Will monitoring slow down my API?**  
A: No. Overhead is < 0.1ms per request. Only slow operations get logged.

**Q: When should I optimize?**  
A: Only when production monitoring shows a problem. See "When to Optimize" above.

**Q: What if everything is fast?**  
A: Great! No optimization needed. Continue monitoring.

## Summary

- ✅ Monitoring infrastructure is ready
- ✅ Strategy documented
- ⏳ Add monitoring to endpoints when deploying to production
- ⏳ Monitor for 2-4 weeks
- ⏳ Optimize only if data shows need

---

**See Also**:
- [PERFORMANCE_MONITORING_STRATEGY.md](../_meta/docs/PERFORMANCE_MONITORING_STRATEGY.md) - Complete monitoring strategy
- [PRODUCTION_OPTIMIZATION_GUIDE.md](../_meta/docs/PRODUCTION_OPTIMIZATION_GUIDE.md) - Optimization techniques
- [Worker09 README](../_meta/issues/new/Worker09/README.md) - Worker09 status

**Last Updated**: 2025-11-07  
**Status**: Ready for production deployment
