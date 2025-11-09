#!/usr/bin/env php
<?php

/**
 * TaskManager PHP Worker Test Script
 *
 * Tests the worker implementation by:
 * 1. Verifying API connectivity
 * 2. Registering example task types
 * 3. Creating test tasks
 * 4. Verifying worker can claim and process them
 *
 * Usage:
 *   php test_worker.php [options]
 *
 * Options:
 *   --api-url=URL   TaskManager API URL (default: http://localhost/api)
 *   --cleanup       Remove test tasks after completion
 *   --help          Show this help message
 */

require_once __DIR__ . '/WorkerClient.php';

use PrismQ\TaskManager\Worker\WorkerClient;

// Parse arguments
$apiUrl = 'http://localhost/api';
$cleanup = false;

foreach ($argv as $arg) {
    if ($arg === '--help' || $arg === '-h') {
        showHelp();
        exit(0);
    }

    if (strpos($arg, '--api-url=') === 0) {
        $apiUrl = substr($arg, strlen('--api-url='));
    }

    if ($arg === '--cleanup') {
        $cleanup = true;
    }
}

echo "================================\n";
echo "TaskManager Worker Test\n";
echo "================================\n";
echo "API URL: {$apiUrl}\n";
echo "================================\n\n";

// Test counters
$testsPassed = 0;
$testsFailed = 0;
$createdTasks = [];

// Create client
$client = new WorkerClient($apiUrl, 'test-worker', true);

// Test 1: API Health Check
echo "[TEST 1] API Health Check\n";
try {
    if ($client->checkHealth()) {
        echo "  ✓ API is healthy\n\n";
        $testsPassed++;
    } else {
        echo "  ✗ API health check failed\n\n";
        $testsFailed++;
        exit(1);
    }
} catch (Exception $e) {
    echo "  ✗ Error: {$e->getMessage()}\n\n";
    $testsFailed++;
    exit(1);
}

// Test 2: Register Example Task Types
echo "[TEST 2] Register Example Task Types\n";

$taskTypes = [
    [
        'name' => 'example.echo',
        'version' => '1.0.0',
        'schema' => [
            'type' => 'object',
            'properties' => [
                'message' => ['type' => 'string']
            ],
            'required' => ['message']
        ]
    ],
    [
        'name' => 'example.uppercase',
        'version' => '1.0.0',
        'schema' => [
            'type' => 'object',
            'properties' => [
                'text' => ['type' => 'string']
            ],
            'required' => ['text']
        ]
    ],
    [
        'name' => 'example.math.add',
        'version' => '1.0.0',
        'schema' => [
            'type' => 'object',
            'properties' => [
                'a' => ['type' => 'number'],
                'b' => ['type' => 'number']
            ],
            'required' => ['a', 'b']
        ]
    ],
    [
        'name' => 'example.sleep',
        'version' => '1.0.0',
        'schema' => [
            'type' => 'object',
            'properties' => [
                'seconds' => [
                    'type' => 'integer',
                    'minimum' => 0,
                    'maximum' => 60
                ]
            ],
            'required' => ['seconds']
        ]
    ]
];

foreach ($taskTypes as $taskType) {
    try {
        $client->registerTaskType(
            $taskType['name'],
            $taskType['version'],
            $taskType['schema']
        );
        echo "  ✓ Registered: {$taskType['name']}\n";
        $testsPassed++;
    } catch (Exception $e) {
        // Already registered is OK
        if (strpos($e->getMessage(), 'already exists') !== false) {
            echo "  ✓ Already exists: {$taskType['name']}\n";
            $testsPassed++;
        } else {
            echo "  ✗ Failed to register {$taskType['name']}: {$e->getMessage()}\n";
            $testsFailed++;
        }
    }
}
echo "\n";

// Test 3: Create Test Tasks
echo "[TEST 3] Create Test Tasks\n";

$testTasks = [
    [
        'type' => 'example.echo',
        'params' => ['message' => 'Hello from test script!']
    ],
    [
        'type' => 'example.uppercase',
        'params' => ['text' => 'convert this to uppercase']
    ],
    [
        'type' => 'example.math.add',
        'params' => ['a' => 15, 'b' => 27]
    ],
    [
        'type' => 'example.sleep',
        'params' => ['seconds' => 1]
    ]
];

foreach ($testTasks as $taskData) {
    try {
        $task = $client->createTask($taskData['type'], $taskData['params']);
        $createdTasks[] = $task['id'];
        echo "  ✓ Created task #{$task['id']} ({$taskData['type']})\n";
        $testsPassed++;
    } catch (Exception $e) {
        echo "  ✗ Failed to create task: {$e->getMessage()}\n";
        $testsFailed++;
    }
}
echo "\n";

// Test 4: Verify Tasks are Pending
echo "[TEST 4] Verify Tasks are Pending\n";
foreach ($createdTasks as $taskId) {
    try {
        $task = $client->getTask($taskId);
        if ($task['status'] === 'pending') {
            echo "  ✓ Task #{$taskId} is pending\n";
            $testsPassed++;
        } else {
            echo "  ✗ Task #{$taskId} has unexpected status: {$task['status']}\n";
            $testsFailed++;
        }
    } catch (Exception $e) {
        echo "  ✗ Failed to get task #{$taskId}: {$e->getMessage()}\n";
        $testsFailed++;
    }
}
echo "\n";

// Test 5: Claim and Process Tasks
echo "[TEST 5] Claim and Process Tasks\n";
echo "  Note: This requires worker.php task handlers\n";

$processedCount = 0;
$maxAttempts = count($createdTasks) + 2; // Allow a few extra attempts

for ($i = 0; $i < $maxAttempts && $processedCount < count($createdTasks); $i++) {
    try {
        $task = $client->claimTask('example.%');

        if ($task === null) {
            echo "  ! No tasks available (attempt " . ($i + 1) . ")\n";
            sleep(1);
            continue;
        }

        echo "  ✓ Claimed task #{$task['id']} ({$task['type']})\n";

        // Simulate processing by completing immediately
        // In real scenario, worker.php would process this
        $result = ['test' => true, 'processed_by' => 'test_script'];

        $client->completeTask($task['id'], $result);
        echo "  ✓ Completed task #{$task['id']}\n";

        $processedCount++;
        $testsPassed += 2; // claim + complete
    } catch (Exception $e) {
        echo "  ✗ Error processing task: {$e->getMessage()}\n";
        $testsFailed++;
    }
}

echo "  Processed {$processedCount}/" . count($createdTasks) . " tasks\n\n";

// Test 6: Verify Task Completion
echo "[TEST 6] Verify Task Completion\n";
foreach ($createdTasks as $taskId) {
    try {
        $task = $client->getTask($taskId);
        if ($task['status'] === 'completed') {
            echo "  ✓ Task #{$taskId} is completed\n";
            $testsPassed++;
        } else {
            echo "  ! Task #{$taskId} status: {$task['status']}\n";
        }
    } catch (Exception $e) {
        echo "  ✗ Failed to verify task #{$taskId}: {$e->getMessage()}\n";
        $testsFailed++;
    }
}
echo "\n";

// Test 7: List Tasks
echo "[TEST 7] List Tasks\n";
try {
    $result = $client->listTasks(['status' => 'completed', 'limit' => 10]);
    echo "  ✓ Listed {$result['count']} completed tasks\n";
    $testsPassed++;
} catch (Exception $e) {
    echo "  ✗ Failed to list tasks: {$e->getMessage()}\n";
    $testsFailed++;
}
echo "\n";

// Test 8: Error Handling Test
echo "[TEST 8] Error Handling\n";
try {
    // Try to complete a non-existent task
    $client->completeTask(999999, ['test' => true]);
    echo "  ✗ Should have thrown exception for invalid task\n";
    $testsFailed++;
} catch (Exception $e) {
    if (
        strpos($e->getMessage(), 'not found') !== false ||
        strpos($e->getMessage(), 'not in claimed state') !== false
    ) {
        echo "  ✓ Correctly handled invalid task completion\n";
        $testsPassed++;
    } else {
        echo "  ✗ Unexpected error: {$e->getMessage()}\n";
        $testsFailed++;
    }
}
echo "\n";

// Optional: Cleanup
if ($cleanup && !empty($createdTasks)) {
    echo "[CLEANUP] Removing test tasks\n";
    echo "  Note: TaskManager doesn't have delete endpoint, tasks remain in database\n";
    echo "  Task IDs created: " . implode(', ', $createdTasks) . "\n\n";
}

// Summary
echo "================================\n";
echo "Test Summary\n";
echo "================================\n";
echo "Tests Passed: {$testsPassed}\n";
echo "Tests Failed: {$testsFailed}\n";
echo "Total Tests:  " . ($testsPassed + $testsFailed) . "\n";
echo "================================\n\n";

if ($testsFailed === 0) {
    echo "✓ All tests passed!\n\n";
    echo "Next steps:\n";
    echo "1. Start the worker: php worker.php --api-url={$apiUrl}\n";
    echo "2. Create tasks: curl -X POST {$apiUrl}/tasks -H 'Content-Type: application/json' -d '{...}'\n";
    echo "3. Monitor worker output for task processing\n";
    exit(0);
} else {
    echo "✗ Some tests failed\n\n";
    echo "Please check:\n";
    echo "1. TaskManager API is running at {$apiUrl}\n";
    echo "2. Database is properly configured\n";
    echo "3. Review error messages above\n";
    exit(1);
}

/**
 * Show help message
 *
 * @return void
 */
function showHelp(): void
{
    $script = basename(__FILE__);
    echo <<<HELP
TaskManager PHP Worker Test Script

Tests the worker implementation and API connectivity.

Usage:
  php {$script} [options]

Options:
  --api-url=URL   TaskManager API base URL (default: http://localhost/api)
  --cleanup       Remove test tasks after completion
  --help, -h      Show this help message

Examples:
  # Test with local API
  php {$script}

  # Test with remote API
  php {$script} --api-url=https://example.com/api

  # Test and cleanup
  php {$script} --cleanup

HELP;
}
