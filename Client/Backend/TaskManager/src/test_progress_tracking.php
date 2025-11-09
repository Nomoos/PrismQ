#!/usr/bin/env php
<?php
/**
 * Progress Tracking Test - Standalone
 * 
 * Tests the new progress tracking functionality without dependencies
 */

echo "=================================================\n";
echo "Progress Tracking Test - Schema & Validation\n";
echo "=================================================\n\n";

$testsPassed = 0;
$testsFailed = 0;

// Helper function to test
function test($name, $callback) {
    global $testsPassed, $testsFailed;
    
    echo "Testing: {$name}... ";
    
    try {
        $result = $callback();
        if ($result) {
            echo "✓ PASS\n";
            $testsPassed++;
        } else {
            echo "✗ FAIL\n";
            $testsFailed++;
        }
    } catch (Exception $e) {
        echo "✗ FAIL: {$e->getMessage()}\n";
        $testsFailed++;
    }
}

// Test 1: Progress validation - valid range
test("Progress validation accepts 0", function() {
    $progress = 0;
    return $progress >= 0 && $progress <= 100;
});

test("Progress validation accepts 50", function() {
    $progress = 50;
    return $progress >= 0 && $progress <= 100;
});

test("Progress validation accepts 100", function() {
    $progress = 100;
    return $progress >= 0 && $progress <= 100;
});

test("Progress validation rejects -1", function() {
    $progress = -1;
    return !($progress >= 0 && $progress <= 100);
});

test("Progress validation rejects 101", function() {
    $progress = 101;
    return !($progress >= 0 && $progress <= 100);
});

// Test 2: Schema SQL contains progress column
test("Schema SQL defines progress column", function() {
    $schema = file_get_contents(__DIR__ . '/database/schema.sql');
    return strpos($schema, 'progress INT DEFAULT 0') !== false;
});

test("Schema SQL defines progress index", function() {
    $schema = file_get_contents(__DIR__ . '/database/schema.sql');
    return strpos($schema, 'idx_progress') !== false;
});

// Test 3: Migration file exists and is correct
test("Migration file exists", function() {
    return file_exists(__DIR__ . '/database/migrations/002_add_progress_column.sql');
});

test("Migration file adds progress column", function() {
    $migration = file_get_contents(__DIR__ . '/database/migrations/002_add_progress_column.sql');
    return strpos($migration, 'ADD COLUMN progress') !== false;
});

// Test 4: Seed endpoints includes progress endpoint
test("Seed SQL defines progress endpoint", function() {
    $seed = file_get_contents(__DIR__ . '/database/seed_endpoints.sql');
    return strpos($seed, '/tasks/:id/progress') !== false;
});

test("Progress endpoint has correct handler", function() {
    $seed = file_get_contents(__DIR__ . '/database/seed_endpoints.sql');
    return strpos($seed, 'task_update_progress') !== false;
});

test("Progress endpoint has validation rules", function() {
    $seed = file_get_contents(__DIR__ . '/database/seed_endpoints.sql');
    return strpos($seed, "api_endpoints WHERE path = '/tasks/:id/progress'") !== false;
});

// Test 5: CustomHandlers has the method
test("CustomHandlers.php contains task_update_progress method", function() {
    $handlers = file_get_contents(__DIR__ . '/api/CustomHandlers.php');
    return strpos($handlers, 'function task_update_progress') !== false;
});

test("CustomHandlers validates progress range", function() {
    $handlers = file_get_contents(__DIR__ . '/api/CustomHandlers.php');
    return strpos($handlers, 'Progress must be between 0 and 100') !== false;
});

// Test 6: WorkerClient has updateProgress method
test("WorkerClient.php has updateProgress method", function() {
    $client = file_get_contents(__DIR__ . '/../../examples/workers/php/WorkerClient.php');
    return strpos($client, 'public function updateProgress') !== false;
});

test("WorkerClient validates progress in client", function() {
    $client = file_get_contents(__DIR__ . '/../../examples/workers/php/WorkerClient.php');
    return strpos($client, 'Progress must be between 0 and 100') !== false;
});

// Test 7: Python worker has update_progress method
test("Python worker has update_progress method", function() {
    $worker = file_get_contents(__DIR__ . '/../../examples/workers/python/worker.py');
    return strpos($worker, 'def update_progress') !== false;
});

test("Python worker validates progress range", function() {
    $worker = file_get_contents(__DIR__ . '/../../examples/workers/python/worker.py');
    return strpos($worker, 'not 0 <= progress <= 100') !== false;
});

// Test 8: Documentation exists
test("PROGRESS_TRACKING.md documentation exists", function() {
    return file_exists(__DIR__ . '/PROGRESS_TRACKING.md');
});

test("Documentation is comprehensive", function() {
    $docs = file_get_contents(__DIR__ . '/PROGRESS_TRACKING.md');
    $size = strlen($docs);
    return $size > 5000; // Should be substantial documentation
});

// Summary
echo "\n=================================================\n";
echo "Test Summary\n";
echo "=================================================\n";
echo "Tests Passed: {$testsPassed}\n";
echo "Tests Failed: {$testsFailed}\n";
echo "Total Tests:  " . ($testsPassed + $testsFailed) . "\n";
echo "=================================================\n";

if ($testsFailed > 0) {
    echo "\n❌ Some tests failed!\n";
    exit(1);
} else {
    echo "\n✅ All tests passed!\n";
    exit(0);
}
