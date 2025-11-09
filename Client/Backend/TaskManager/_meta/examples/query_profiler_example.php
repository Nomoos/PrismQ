<?php
/**
 * Example: Using QueryProfiler with TaskManager
 * 
 * This demonstrates how QueryProfiler automatically tracks database queries
 * when using the TaskManager controllers.
 */

require_once __DIR__ . '/../api/QueryProfiler.php';

echo "QueryProfiler Integration Example\n";
echo "==================================\n\n";

// Setup: Enable query profiling
QueryProfiler::enable();
QueryProfiler::setSlowQueryThreshold(50); // Log queries > 50ms

// Create a test database connection
try {
    $pdo = new PDO('sqlite::memory:');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Create test tables
    $pdo->exec("
        CREATE TABLE task_types (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            param_schema_json TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    ");
    
    $pdo->exec("
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            type_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            params_json TEXT NOT NULL,
            dedupe_key TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (type_id) REFERENCES task_types(id)
        )
    ");
    
    // Seed test data
    $pdo->exec("
        INSERT INTO task_types (id, name, version, param_schema_json, is_active)
        VALUES (1, 'email_task', '1.0.0', '{\"type\":\"object\"}', 1)
    ");
    
    echo "✓ Test database created\n\n";
    
} catch (PDOException $e) {
    echo "Failed to setup test database: " . $e->getMessage() . "\n";
    exit(1);
}

// Example 1: Basic query profiling
echo "Example 1: Basic Query Profiling\n";
echo "---------------------------------\n";

QueryProfiler::resetStatistics();

// Simulate what TaskController does
$stmt = QueryProfiler::prepare($pdo, "SELECT id, param_schema_json, is_active FROM task_types WHERE name = ?");
$stmt->execute(['email_task']);
$taskType = $stmt->fetch();

echo "Query executed: SELECT task type by name\n";
echo "Result: Found task type with ID " . $taskType['id'] . "\n";

$stats = QueryProfiler::getStatistics();
echo "Queries tracked: " . $stats['total_queries'] . "\n";
echo "Total time: " . round($stats['total_time'], 2) . "ms\n\n";

// Example 2: Multiple queries
echo "Example 2: Multiple Queries\n";
echo "---------------------------\n";

QueryProfiler::resetStatistics();

// Create a task (multiple queries)
$stmt1 = QueryProfiler::prepare($pdo, "SELECT id FROM task_types WHERE name = ?");
$stmt1->execute(['email_task']);
$type = $stmt1->fetch();

$stmt2 = QueryProfiler::prepare($pdo, "SELECT id FROM tasks WHERE dedupe_key = ?");
$stmt2->execute(['test_key_123']);
$existing = $stmt2->fetch();

if (!$existing) {
    $stmt3 = QueryProfiler::prepare($pdo, "INSERT INTO tasks (type_id, status, params_json, dedupe_key, priority) VALUES (?, ?, ?, ?, ?)");
    $stmt3->execute([1, 'pending', '{"email":"test@example.com"}', 'test_key_123', 0]);
}

$summary = QueryProfiler::getSummary();
echo "Total queries: " . $summary['total_queries'] . "\n";
echo "Average query time: " . $summary['average_time'] . "ms\n";
echo "Slow queries: " . $summary['slow_queries'] . "\n\n";

// Example 3: Detecting slow queries
echo "Example 3: Slow Query Detection\n";
echo "--------------------------------\n";

QueryProfiler::resetStatistics();
QueryProfiler::setSlowQueryThreshold(1); // Very low threshold for demo

// Simulate a slow query
$stmt = QueryProfiler::prepare($pdo, "SELECT * FROM tasks WHERE status = ?");
$stmt->execute(['pending']);
usleep(2000); // Add 2ms delay
$results = $stmt->fetchAll();

// Record a simulated slow query
QueryProfiler::recordQuery("SELECT * FROM tasks WHERE created_at < ?", 75.5, ['2025-01-01']);

$summary = QueryProfiler::getSummary();
echo "Total queries: " . $summary['total_queries'] . "\n";
echo "Slow queries detected: " . $summary['slow_queries'] . "\n";
echo "Slow query percentage: " . $summary['slow_query_percentage'] . "%\n";
echo "\nCheck error log for SLOW QUERY entries!\n\n";

// Reset threshold
QueryProfiler::setSlowQueryThreshold(100);

// Example 4: Query statistics over time
echo "Example 4: Statistics Over Time\n";
echo "--------------------------------\n";

QueryProfiler::resetStatistics();

// Simulate API endpoint handling multiple tasks
for ($i = 1; $i <= 10; $i++) {
    $stmt = QueryProfiler::prepare($pdo, "SELECT * FROM tasks WHERE id = ?");
    $stmt->execute([$i]);
    $stmt->fetch();
}

$stats = QueryProfiler::getStatistics();
echo "Queries executed: " . $stats['total_queries'] . "\n";
echo "Total time: " . round($stats['total_time'], 2) . "ms\n";

$summary = QueryProfiler::getSummary();
echo "Average time per query: " . $summary['average_time'] . "ms\n";
echo "Performance: ";
if ($summary['average_time'] < 10) {
    echo "Excellent ✓\n";
} elseif ($summary['average_time'] < 50) {
    echo "Good ✓\n";
} else {
    echo "Needs optimization ⚠\n";
}
echo "\n";

// Example 5: Production monitoring pattern
echo "Example 5: Production Monitoring Pattern\n";
echo "-----------------------------------------\n";

QueryProfiler::resetStatistics();
QueryProfiler::setSlowQueryThreshold(100);

// Simulate a request lifecycle
function simulateRequest($pdo) {
    // Get task type
    $stmt = QueryProfiler::prepare($pdo, "SELECT * FROM task_types WHERE name = ?");
    $stmt->execute(['email_task']);
    $type = $stmt->fetch();
    
    // Check for existing task
    $stmt = QueryProfiler::prepare($pdo, "SELECT * FROM tasks WHERE dedupe_key = ?");
    $stmt->execute(['dedupe_' . time()]);
    $existing = $stmt->fetch();
    
    // Create task if not exists
    if (!$existing) {
        $stmt = QueryProfiler::prepare($pdo, "INSERT INTO tasks (type_id, status, params_json, dedupe_key) VALUES (?, ?, ?, ?)");
        $stmt->execute([1, 'pending', '{}', 'dedupe_' . time()]);
    }
}

// Simulate multiple requests
for ($i = 0; $i < 5; $i++) {
    simulateRequest($pdo);
}

$summary = QueryProfiler::getSummary();
echo "Requests handled: 5\n";
echo "Total queries: " . $summary['total_queries'] . "\n";
echo "Average query time: " . $summary['average_time'] . "ms\n";
echo "Slow queries: " . $summary['slow_queries'] . " (" . $summary['slow_query_percentage'] . "%)\n";

// Production recommendation
if ($summary['slow_query_percentage'] > 5) {
    echo "\n⚠ WARNING: More than 5% of queries are slow!\n";
    echo "   Recommendation: Review slow queries and optimize\n";
} else {
    echo "\n✓ Query performance is healthy\n";
}

echo "\n";

// Example 6: Detailed query analysis
echo "Example 6: Detailed Query Analysis\n";
echo "-----------------------------------\n";

QueryProfiler::resetStatistics();

// Run various queries
$queries = [
    "SELECT * FROM task_types WHERE is_active = 1",
    "SELECT COUNT(*) FROM tasks WHERE status = 'pending'",
    "SELECT * FROM tasks WHERE type_id = ?",
    "UPDATE tasks SET status = 'processing' WHERE id = ?"
];

foreach ($queries as $query) {
    $stmt = QueryProfiler::prepare($pdo, $query);
    if (strpos($query, '?') !== false) {
        $stmt->execute([1]);
    } else {
        $stmt->execute();
    }
    if (strpos($query, 'SELECT') !== false) {
        $stmt->fetchAll();
    }
}

// Analyze the queries
$stats = QueryProfiler::getStatistics();
echo "Queries analyzed: " . count($stats['queries']) . "\n\n";

foreach ($stats['queries'] as $idx => $query) {
    echo "Query " . ($idx + 1) . ":\n";
    echo "  SQL: " . substr($query['query'], 0, 60) . "...\n";
    echo "  Time: " . round($query['duration'], 2) . "ms\n";
    echo "  Status: " . ($query['is_slow'] ? '⚠ SLOW' : '✓ OK') . "\n";
    echo "\n";
}

// Summary
echo "================================\n";
echo "Integration Example Complete\n";
echo "================================\n\n";

$finalSummary = QueryProfiler::getSummary();
echo "Summary:\n";
echo "- Total queries profiled: " . $finalSummary['total_queries'] . "\n";
echo "- Average query time: " . $finalSummary['average_time'] . "ms\n";
echo "- Slow queries: " . $finalSummary['slow_queries'] . "\n";
echo "- Performance: " . ($finalSummary['slow_query_percentage'] < 5 ? '✓ Good' : '⚠ Needs attention') . "\n";

echo "\nNext steps:\n";
echo "1. Enable QueryProfiler in production (it's on by default)\n";
echo "2. Monitor error logs for SLOW QUERY entries\n";
echo "3. Review getSummary() at end of each request\n";
echo "4. Optimize queries that consistently appear as slow\n";
echo "\n";
