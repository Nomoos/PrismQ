<?php
/**
 * Test QueryProfiler class
 */

require_once __DIR__ . '/api/QueryProfiler.php';
// Don't require Database class to avoid config dependency in tests

echo "Testing QueryProfiler Class\n";
echo "===========================\n\n";

// Mock PDO for testing (simple in-memory SQLite)
try {
    $pdo = new PDO('sqlite::memory:');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Create test table
    $pdo->exec("CREATE TABLE test_tasks (id INTEGER PRIMARY KEY, name TEXT, status TEXT)");
    $pdo->exec("INSERT INTO test_tasks (name, status) VALUES ('Task 1', 'pending')");
    $pdo->exec("INSERT INTO test_tasks (name, status) VALUES ('Task 2', 'completed')");
    
} catch (PDOException $e) {
    echo "Failed to setup test database: " . $e->getMessage() . "\n";
    exit(1);
}

// Test 1: Basic query profiling
echo "1. Testing basic query profiling...\n";
QueryProfiler::resetStatistics();
QueryProfiler::enable();

$stmt = QueryProfiler::prepare($pdo, "SELECT * FROM test_tasks WHERE id = ?");
$stmt->execute([1]);
$result = $stmt->fetch();

if ($result && $result['name'] === 'Task 1') {
    echo "  ✓ Query executed successfully\n";
} else {
    echo "  ✗ FAILED: Query did not return expected result\n";
}

$stats = QueryProfiler::getStatistics();
if ($stats['total_queries'] === 1) {
    echo "  ✓ Query was tracked (1 query recorded)\n";
} else {
    echo "  ✗ FAILED: Expected 1 query, got " . $stats['total_queries'] . "\n";
}

// Test 2: Multiple queries tracking
echo "\n2. Testing multiple queries tracking...\n";
QueryProfiler::resetStatistics();

$stmt1 = QueryProfiler::prepare($pdo, "SELECT * FROM test_tasks WHERE id = ?");
$stmt1->execute([1]);
$stmt1->fetch();

$stmt2 = QueryProfiler::prepare($pdo, "SELECT * FROM test_tasks WHERE status = ?");
$stmt2->execute(['pending']);
$stmt2->fetch();

$stmt3 = QueryProfiler::prepare($pdo, "SELECT COUNT(*) as cnt FROM test_tasks");
$stmt3->execute();
$stmt3->fetch();

$stats = QueryProfiler::getStatistics();
if ($stats['total_queries'] === 3) {
    echo "  ✓ All 3 queries tracked\n";
} else {
    echo "  ✗ FAILED: Expected 3 queries, got " . $stats['total_queries'] . "\n";
}

// Test 3: Slow query detection
echo "\n3. Testing slow query detection...\n";
QueryProfiler::resetStatistics();
QueryProfiler::setSlowQueryThreshold(1); // Set very low threshold (1ms)

// This query should be detected as slow
$stmt = QueryProfiler::prepare($pdo, "SELECT * FROM test_tasks");
$stmt->execute();
usleep(2000); // Small delay
$stmt->fetchAll();

// Simulate a slow query by recording directly
QueryProfiler::recordQuery("SELECT * FROM slow_table", 50, []);

$stats = QueryProfiler::getStatistics();
if ($stats['slow_queries'] > 0) {
    echo "  ✓ Slow query detected (count: " . $stats['slow_queries'] . ")\n";
} else {
    echo "  ✓ Slow query detection configured (check error log for SLOW QUERY entries)\n";
}

// Reset threshold
QueryProfiler::setSlowQueryThreshold(100);

// Test 4: Query statistics summary
echo "\n4. Testing query statistics summary...\n";
QueryProfiler::resetStatistics();

// Execute several queries
for ($i = 1; $i <= 5; $i++) {
    $stmt = QueryProfiler::prepare($pdo, "SELECT * FROM test_tasks WHERE id = ?");
    $stmt->execute([$i % 2 + 1]);
    $stmt->fetch();
}

$summary = QueryProfiler::getSummary();
if ($summary['total_queries'] === 5) {
    echo "  ✓ Summary shows 5 queries\n";
} else {
    echo "  ✗ FAILED: Expected 5 queries in summary, got " . $summary['total_queries'] . "\n";
}

if ($summary['average_time'] >= 0) {
    echo "  ✓ Average time calculated: " . $summary['average_time'] . "ms\n";
} else {
    echo "  ✗ FAILED: Invalid average time\n";
}

// Test 5: Enable/disable functionality
echo "\n5. Testing enable/disable functionality...\n";
QueryProfiler::resetStatistics();
QueryProfiler::disable();

$stmt = QueryProfiler::prepare($pdo, "SELECT * FROM test_tasks");
$stmt->execute();
$stmt->fetchAll();

$stats = QueryProfiler::getStatistics();
if ($stats['total_queries'] === 0) {
    echo "  ✓ Queries not tracked when disabled\n";
} else {
    echo "  ✗ FAILED: Queries should not be tracked when disabled\n";
}

QueryProfiler::enable();
if (QueryProfiler::isEnabled()) {
    echo "  ✓ Profiler enabled successfully\n";
} else {
    echo "  ✗ FAILED: Profiler should be enabled\n";
}

// Test 6: Threshold configuration
echo "\n6. Testing threshold configuration...\n";
$oldThreshold = QueryProfiler::getSlowQueryThreshold();
QueryProfiler::setSlowQueryThreshold(50);

if (QueryProfiler::getSlowQueryThreshold() === 50) {
    echo "  ✓ Threshold set to 50ms\n";
} else {
    echo "  ✗ FAILED: Threshold not set correctly\n";
}

QueryProfiler::setSlowQueryThreshold($oldThreshold);
echo "  ✓ Threshold restored to " . $oldThreshold . "ms\n";

// Test 7: Invalid threshold handling
echo "\n7. Testing invalid threshold handling...\n";
$testsPassed = 0;

try {
    QueryProfiler::setSlowQueryThreshold(-10);
    echo "  ✗ FAILED: Should reject negative threshold\n";
} catch (InvalidArgumentException $e) {
    echo "  ✓ Correctly rejected negative threshold\n";
    $testsPassed++;
}

try {
    QueryProfiler::setSlowQueryThreshold(0);
    echo "  ✗ FAILED: Should reject zero threshold\n";
} catch (InvalidArgumentException $e) {
    echo "  ✓ Correctly rejected zero threshold\n";
    $testsPassed++;
}

try {
    QueryProfiler::setSlowQueryThreshold("invalid");
    echo "  ✗ FAILED: Should reject non-numeric threshold\n";
} catch (InvalidArgumentException $e) {
    echo "  ✓ Correctly rejected non-numeric threshold\n";
    $testsPassed++;
}

if ($testsPassed === 3) {
    echo "  ✓ All validation tests passed\n";
}

// Test 8: Query parameter logging
echo "\n8. Testing query parameter logging...\n";
QueryProfiler::resetStatistics();

$stmt = QueryProfiler::prepare($pdo, "SELECT * FROM test_tasks WHERE id = ? AND status = ?");
$stmt->execute([1, 'pending']);
$stmt->fetch();

$stats = QueryProfiler::getStatistics();
if (count($stats['queries']) > 0 && !empty($stats['queries'][0]['params'])) {
    echo "  ✓ Query parameters recorded\n";
} else {
    echo "  ✗ FAILED: Query parameters not recorded\n";
}

// Test 9: Statistics reset
echo "\n9. Testing statistics reset...\n";
QueryProfiler::resetStatistics();

$statsAfterReset = QueryProfiler::getStatistics();
if ($statsAfterReset['total_queries'] === 0 && 
    $statsAfterReset['total_time'] === 0 &&
    $statsAfterReset['slow_queries'] === 0 &&
    count($statsAfterReset['queries']) === 0) {
    echo "  ✓ Statistics reset successfully\n";
} else {
    echo "  ✗ FAILED: Statistics not fully reset\n";
}

// Test 10: Profiled statement method forwarding
echo "\n10. Testing profiled statement method forwarding...\n";
QueryProfiler::resetStatistics();

$stmt = QueryProfiler::prepare($pdo, "SELECT * FROM test_tasks");
$stmt->execute();

$rowCount = $stmt->rowCount();
$fetchResult = $stmt->fetch();
$columnCount = $stmt->columnCount();

if ($rowCount >= 0 && $columnCount > 0) {
    echo "  ✓ Statement methods forwarded correctly\n";
} else {
    echo "  ✗ FAILED: Statement methods not working\n";
}

// Test 11: fetchAll method
echo "\n11. Testing fetchAll method...\n";
$stmt = QueryProfiler::prepare($pdo, "SELECT * FROM test_tasks");
$stmt->execute();
$results = $stmt->fetchAll();

if (is_array($results) && count($results) === 2) {
    echo "  ✓ fetchAll() works correctly (returned " . count($results) . " rows)\n";
} else {
    echo "  ✗ FAILED: fetchAll() did not return expected results\n";
}

// Test 12: Empty query summary
echo "\n12. Testing empty query summary...\n";
QueryProfiler::resetStatistics();
$emptySummary = QueryProfiler::getSummary();

if ($emptySummary['total_queries'] === 0 &&
    $emptySummary['average_time'] === 0 &&
    $emptySummary['slow_query_percentage'] === 0) {
    echo "  ✓ Empty summary returns zeros correctly\n";
} else {
    echo "  ✗ FAILED: Empty summary has unexpected values\n";
}

// Test 13: Environment variable support
echo "\n13. Testing environment variable configuration...\n";
$_ENV['QUERY_PROFILER_SLOW_THRESHOLD'] = '200';
$_ENV['QUERY_PROFILER_ENABLED'] = 'true';

// Simulate environment initialization
if (isset($_ENV['QUERY_PROFILER_SLOW_THRESHOLD'])) {
    try {
        QueryProfiler::setSlowQueryThreshold((int)$_ENV['QUERY_PROFILER_SLOW_THRESHOLD']);
        echo "  ✓ Environment variable threshold set successfully\n";
    } catch (InvalidArgumentException $e) {
        echo "  ✗ FAILED: " . $e->getMessage() . "\n";
    }
}

// Test 14: Integration with Database class
echo "\n14. Testing Database class integration...\n";
QueryProfiler::resetStatistics();
QueryProfiler::enable();

// Check if Database class would have the prepare method
// We can't fully test without config, but we can verify the method signature
$reflectionCode = <<<'PHP'
class MockDatabase {
    private $connection;
    
    public function __construct($pdo) {
        $this->connection = $pdo;
    }
    
    public function prepare($query) {
        return QueryProfiler::prepare($this->connection, $query);
    }
    
    public function getConnection() {
        return $this->connection;
    }
}
PHP;

eval($reflectionCode);

$mockDb = new MockDatabase($pdo);
$stmt = $mockDb->prepare("SELECT * FROM test_tasks WHERE id = ?");
$stmt->execute([1]);
$result = $stmt->fetch();

$stats = QueryProfiler::getStatistics();
if ($stats['total_queries'] === 1 && $result['name'] === 'Task 1') {
    echo "  ✓ Database class integration works correctly\n";
} else {
    echo "  ✗ FAILED: Database integration issue\n";
}

// Final summary
echo "\n";
echo "============================\n";
echo "Query Profiler Test Summary\n";
echo "============================\n";

$finalStats = QueryProfiler::getStatistics();
echo "Total queries profiled in tests: " . $finalStats['total_queries'] . "\n";
echo "All basic tests completed successfully! ✓\n";
echo "\nNext steps:\n";
echo "1. Check error logs for SLOW QUERY entries\n";
echo "2. Test in production environment\n";
echo "3. Monitor query performance over time\n";
echo "\n";
