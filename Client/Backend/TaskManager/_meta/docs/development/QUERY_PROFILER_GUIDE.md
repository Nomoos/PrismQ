# Query Profiler - Database Query Performance Tracking

## Overview

The Query Profiler is a lightweight database query performance monitoring tool designed for production use. It tracks query execution time, identifies slow queries, and provides detailed statistics with minimal overhead.

## Features

- **Automatic Query Tracking**: Transparently profiles all database queries
- **Slow Query Detection**: Automatically logs queries exceeding threshold
- **Query Statistics**: Provides detailed metrics (total queries, avg time, slow query %)
- **Minimal Overhead**: < 0.1ms overhead per query
- **Production Ready**: Can be enabled/disabled via environment variables
- **Parameter Logging**: Records query parameters for slow query analysis

## Quick Start

### 1. Enable Query Profiling

```php
// In your application bootstrap
require_once __DIR__ . '/api/QueryProfiler.php';

// Enable profiling (enabled by default)
QueryProfiler::enable();

// Set slow query threshold (default: 100ms)
QueryProfiler::setSlowQueryThreshold(100);
```

### 2. Use with Database Class

The `Database` class has been enhanced with query profiling support:

```php
// Get database instance
$db = Database::getInstance();

// Use the prepare method - queries are automatically profiled
$stmt = $db->prepare("SELECT * FROM tasks WHERE id = ?");
$stmt->execute([123]);
$result = $stmt->fetch();
```

### 3. Direct Usage (Advanced)

You can also use QueryProfiler directly with any PDO connection:

```php
$pdo = new PDO(...);
$stmt = QueryProfiler::prepare($pdo, "SELECT * FROM tasks WHERE status = ?");
$stmt->execute(['pending']);
$results = $stmt->fetchAll();
```

## Configuration

### Environment Variables

Configure via environment variables:

```bash
# Set slow query threshold (milliseconds)
QUERY_PROFILER_SLOW_THRESHOLD=100

# Enable/disable profiling
QUERY_PROFILER_ENABLED=true
```

### Runtime Configuration

```php
// Set threshold
QueryProfiler::setSlowQueryThreshold(50); // Log queries > 50ms

// Enable/disable
QueryProfiler::enable();
QueryProfiler::disable();

// Check status
if (QueryProfiler::isEnabled()) {
    // Profiling is active
}
```

## Query Statistics

### Get Detailed Statistics

```php
$stats = QueryProfiler::getStatistics();

// Returns:
// [
//     'total_queries' => 150,
//     'total_time' => 1234.56,  // milliseconds
//     'slow_queries' => 5,
//     'queries' => [...]  // Array of query details
// ]
```

### Get Summary

```php
$summary = QueryProfiler::getSummary();

// Returns:
// [
//     'total_queries' => 150,
//     'total_time' => 1234.56,
//     'average_time' => 8.23,  // ms per query
//     'slow_queries' => 5,
//     'slow_query_percentage' => 3.33
// ]
```

### Reset Statistics

```php
// Clear all collected statistics
QueryProfiler::resetStatistics();
```

## Slow Query Logging

When a query exceeds the threshold, it's automatically logged:

```
SLOW QUERY [245.67ms] at 2025-11-09 10:30:45: SELECT * FROM tasks WHERE type_id = ? AND status = ? | Params: [3,"pending"]
```

### Log Format

- **Duration**: Execution time in milliseconds
- **Timestamp**: When the query was executed
- **Query**: SQL query (truncated to 200 chars if longer)
- **Parameters**: Bound parameters (JSON encoded)

## Use Cases

### 1. Production Monitoring

Monitor production query performance:

```php
// Enable at application startup
QueryProfiler::enable();
QueryProfiler::setSlowQueryThreshold(200);

// ... application runs ...

// At request end, log summary if needed
if (QueryProfiler::getSummary()['slow_queries'] > 0) {
    error_log('Request had slow queries: ' . json_encode(QueryProfiler::getSummary()));
}
```

### 2. Development Profiling

Profile queries during development:

```php
// Set aggressive threshold for development
QueryProfiler::setSlowQueryThreshold(10);

// Run your code
runTaskProcessing();

// Check what queries were slow
$summary = QueryProfiler::getSummary();
echo "Average query time: {$summary['average_time']}ms\n";
echo "Slow queries: {$summary['slow_queries']}\n";
```

### 3. Performance Testing

Track query performance in tests:

```php
class PerformanceTest {
    public function testQueryPerformance() {
        QueryProfiler::resetStatistics();
        QueryProfiler::enable();
        
        // Run your operation
        $this->createTask($data);
        
        // Assert performance
        $summary = QueryProfiler::getSummary();
        $this->assertLessThan(50, $summary['average_time']);
        $this->assertEquals(0, $summary['slow_queries']);
    }
}
```

## Integration Examples

### Example 1: TaskController with Profiling

```php
class TaskController {
    private $db;
    
    public function __construct() {
        $this->db = Database::getInstance();
    }
    
    public function create() {
        // Queries are automatically profiled
        $stmt = $this->db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute([$typeName]);
        $taskType = $stmt->fetch();
        
        // If this query is slow, you'll see:
        // SLOW QUERY [150.00ms] at 2025-11-09 10:30:45: SELECT id FROM task_types WHERE name = ? | Params: ["email_task"]
    }
}
```

### Example 2: Monitoring Endpoint

Create an endpoint to check query performance:

```php
class MonitoringController {
    public function queryStats() {
        $summary = QueryProfiler::getSummary();
        
        ApiResponse::success([
            'total_queries' => $summary['total_queries'],
            'average_time_ms' => $summary['average_time'],
            'slow_queries' => $summary['slow_queries'],
            'slow_percentage' => $summary['slow_query_percentage']
        ]);
    }
}
```

## Performance Impact

### Overhead Analysis

- **Per Query Overhead**: < 0.1ms
- **Memory Usage**: ~1KB per 100 queries stored
- **CPU Impact**: Negligible (simple timing and logging)

### When Disabled

When profiling is disabled, the overhead is nearly zero:
- Profiled statements behave like regular PDOStatements
- No timing or statistics collection
- No logging overhead

## Best Practices

### 1. Set Appropriate Thresholds

```php
// Development: Aggressive threshold
QueryProfiler::setSlowQueryThreshold(10);

// Staging: Moderate threshold
QueryProfiler::setSlowQueryThreshold(50);

// Production: Conservative threshold
QueryProfiler::setSlowQueryThreshold(100);
```

### 2. Monitor Slow Query Percentage

```php
$summary = QueryProfiler::getSummary();
if ($summary['slow_query_percentage'] > 5) {
    // Alert: More than 5% of queries are slow
    error_log("WARNING: High slow query percentage: {$summary['slow_query_percentage']}%");
}
```

### 3. Reset Statistics Periodically

```php
// Reset statistics every hour to prevent memory growth
if (time() % 3600 === 0) {
    QueryProfiler::resetStatistics();
}
```

### 4. Use with MySQL Slow Query Log

Combine with MySQL's slow query log for comprehensive analysis:

```ini
# MySQL configuration
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-query.log
long_query_time = 0.1  # 100ms
```

## Troubleshooting

### Queries Not Being Tracked

**Check if profiling is enabled:**
```php
if (!QueryProfiler::isEnabled()) {
    QueryProfiler::enable();
}
```

**Verify you're using the Database->prepare() method:**
```php
// ✓ Correct - uses profiling
$stmt = $this->db->prepare("SELECT * FROM tasks");

// ✗ Wrong - bypasses profiling
$stmt = $this->db->getConnection()->prepare("SELECT * FROM tasks");
```

### No Slow Queries Logged

**Check your threshold:**
```php
echo "Current threshold: " . QueryProfiler::getSlowQueryThreshold() . "ms\n";
```

**Verify queries are actually slow:**
```php
$stats = QueryProfiler::getStatistics();
foreach ($stats['queries'] as $query) {
    echo "{$query['query']}: {$query['duration']}ms\n";
}
```

### High Memory Usage

**Limit stored queries:**
The profiler stores up to 100 queries by default. If needed, reset periodically:
```php
// Reset after every request
register_shutdown_function(function() {
    QueryProfiler::resetStatistics();
});
```

## API Reference

### QueryProfiler Class

#### Methods

**`enable()`**
- Enable query profiling
- Returns: void

**`disable()`**
- Disable query profiling
- Returns: void

**`isEnabled()`**
- Check if profiling is enabled
- Returns: bool

**`setSlowQueryThreshold(int $milliseconds)`**
- Set threshold for slow query logging
- Parameters: $milliseconds (must be > 0)
- Returns: void
- Throws: InvalidArgumentException

**`getSlowQueryThreshold()`**
- Get current slow query threshold
- Returns: int (milliseconds)

**`prepare(PDO $pdo, string $query)`**
- Prepare a statement with profiling
- Parameters: 
  - $pdo: PDO connection
  - $query: SQL query
- Returns: ProfiledPDOStatement|PDOStatement

**`getStatistics()`**
- Get detailed query statistics
- Returns: array

**`getSummary()`**
- Get summary statistics
- Returns: array

**`resetStatistics()`**
- Clear all collected statistics
- Returns: void

**`recordQuery(string $query, float $duration, array $params = [])`**
- Manually record a query (advanced usage)
- Parameters:
  - $query: SQL query
  - $duration: Duration in milliseconds
  - $params: Query parameters
- Returns: void

## Testing

Run the test suite:

```bash
php test_query_profiler.php
```

Expected output:
```
Testing QueryProfiler Class
===========================

1. Testing basic query profiling...
  ✓ Query executed successfully
  ✓ Query was tracked (1 query recorded)

...

All basic tests completed successfully! ✓
```

## See Also

- [PERFORMANCE_MONITORING.md](PERFORMANCE_MONITORING.md) - General performance monitoring
- [PERFORMANCE_MONITORING_STRATEGY.md](_meta/docs/PERFORMANCE_MONITORING_STRATEGY.md) - Overall strategy
- [Database.php](database/Database.php) - Database connection class

---

**Last Updated**: 2025-11-09  
**Status**: Production Ready  
**Version**: 1.0.0
