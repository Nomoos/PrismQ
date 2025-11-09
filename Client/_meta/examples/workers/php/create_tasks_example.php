#!/usr/bin/env php
<?php

/**
 * Example: Create Tasks for TaskManager
 *
 * This script demonstrates how to programmatically:
 * 1. Register task types with JSON schemas
 * 2. Create tasks with validated parameters
 * 3. Monitor task status
 *
 * Usage:
 *   php create_tasks_example.php [--api-url=URL]
 */

require_once __DIR__ . '/WorkerClient.php';

use PrismQ\TaskManager\Worker\WorkerClient;

// Parse arguments
$apiUrl = 'http://localhost/api';
foreach ($argv as $arg) {
    if (strpos($arg, '--api-url=') === 0) {
        $apiUrl = substr($arg, strlen('--api-url='));
    }
}

echo "================================\n";
echo "TaskManager - Create Tasks Example\n";
echo "================================\n";
echo "API URL: {$apiUrl}\n\n";

// Create client (use 'admin' or 'creator' as worker ID for task creation)
$client = new WorkerClient($apiUrl, 'task-creator', true);

// Check API health
echo "Checking API connectivity...\n";
if (!$client->checkHealth()) {
    die("ERROR: Cannot connect to TaskManager API at {$apiUrl}\n");
}
echo "✓ Connected to API\n\n";

// Example 1: Register a custom task type
echo "Example 1: Register Task Type\n";
echo "------------------------------\n";

try {
    $client->registerTaskType(
        'PrismQ.Script.Generate',
        '1.0.0',
        [
            'type' => 'object',
            'properties' => [
                'topic' => [
                    'type' => 'string',
                    'minLength' => 1,
                    'maxLength' => 200,
                    'description' => 'Script topic or subject'
                ],
                'style' => [
                    'type' => 'string',
                    'enum' => ['formal', 'casual', 'technical'],
                    'description' => 'Writing style'
                ],
                'length' => [
                    'type' => 'integer',
                    'minimum' => 100,
                    'maximum' => 5000,
                    'description' => 'Target word count'
                ],
                'language' => [
                    'type' => 'string',
                    'default' => 'en',
                    'description' => 'Output language (ISO code)'
                ]
            ],
            'required' => ['topic', 'style']
        ]
    );
    echo "✓ Task type registered: PrismQ.Script.Generate\n\n";
} catch (Exception $e) {
    if (strpos($e->getMessage(), 'already exists') !== false) {
        echo "✓ Task type already exists: PrismQ.Script.Generate\n\n";
    } else {
        echo "✗ Error: {$e->getMessage()}\n\n";
    }
}

// Example 2: Create individual tasks
echo "Example 2: Create Individual Tasks\n";
echo "-----------------------------------\n";

$tasks = [
    [
        'type' => 'PrismQ.Script.Generate',
        'params' => [
            'topic' => 'AI in Healthcare',
            'style' => 'technical',
            'length' => 1500,
            'language' => 'en'
        ]
    ],
    [
        'type' => 'PrismQ.Script.Generate',
        'params' => [
            'topic' => 'Climate Change Solutions',
            'style' => 'formal',
            'length' => 2000
        ]
    ],
    [
        'type' => 'example.echo',
        'params' => [
            'message' => 'Processing batch job #' . time()
        ]
    ]
];

$createdTaskIds = [];

foreach ($tasks as $taskData) {
    try {
        $task = $client->createTask($taskData['type'], $taskData['params']);
        $createdTaskIds[] = $task['id'];

        echo "✓ Created task #{$task['id']}\n";
        echo "  Type: {$task['type']}\n";
        echo "  Status: {$task['status']}\n";

        if (isset($task['deduplicated']) && $task['deduplicated']) {
            echo "  Note: Task was deduplicated (already exists)\n";
        }

        echo "\n";
    } catch (Exception $e) {
        echo "✗ Failed to create task: {$e->getMessage()}\n\n";
    }
}

// Example 3: Create batch of tasks
echo "Example 3: Create Batch of Tasks\n";
echo "---------------------------------\n";

$batchTopics = [
    'Quantum Computing Basics',
    'Machine Learning in Finance',
    'Renewable Energy Technologies',
    'Space Exploration Future',
    'Biotechnology Advances'
];

foreach ($batchTopics as $topic) {
    try {
        $task = $client->createTask('PrismQ.Script.Generate', [
            'topic' => $topic,
            'style' => 'casual',
            'length' => 1000
        ]);

        $createdTaskIds[] = $task['id'];
        echo "✓ Created task #{$task['id']}: {$topic}\n";
    } catch (Exception $e) {
        echo "✗ Failed: {$topic} - {$e->getMessage()}\n";
    }
}
echo "\n";

// Example 4: Monitor task status
echo "Example 4: Monitor Task Status\n";
echo "-------------------------------\n";

echo "Created " . count($createdTaskIds) . " tasks\n";
echo "Task IDs: " . implode(', ', $createdTaskIds) . "\n\n";

// Check status of first few tasks
$tasksToCheck = array_slice($createdTaskIds, 0, 3);
foreach ($tasksToCheck as $taskId) {
    try {
        $task = $client->getTask($taskId);

        echo "Task #{$taskId}:\n";
        echo "  Status: {$task['status']}\n";
        echo "  Type: {$task['type']}\n";
        echo "  Attempts: {$task['attempts']}\n";

        if ($task['claimed_by']) {
            echo "  Claimed by: {$task['claimed_by']}\n";
            echo "  Claimed at: {$task['claimed_at']}\n";
        }

        if ($task['status'] === 'completed' && isset($task['result'])) {
            echo "  Result: " . json_encode($task['result'], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
        }

        if ($task['error_message']) {
            echo "  Error: {$task['error_message']}\n";
        }

        echo "\n";
    } catch (Exception $e) {
        echo "✗ Failed to get task #{$taskId}: {$e->getMessage()}\n\n";
    }
}

// Example 5: List pending tasks
echo "Example 5: List Pending Tasks\n";
echo "------------------------------\n";

try {
    $result = $client->listTasks([
        'status' => 'pending',
        'limit' => 10
    ]);

    echo "Found {$result['count']} pending tasks:\n";

    foreach ($result['tasks'] as $task) {
        echo "  - Task #{$task['id']} ({$task['type']}) - created {$task['created_at']}\n";
    }
    echo "\n";
} catch (Exception $e) {
    echo "✗ Failed to list tasks: {$e->getMessage()}\n\n";
}

// Summary
echo "================================\n";
echo "Summary\n";
echo "================================\n";
echo "Total tasks created: " . count($createdTaskIds) . "\n";
echo "\n";
echo "Next steps:\n";
echo "1. Start a worker: php worker.php --api-url={$apiUrl}\n";
echo "2. Monitor progress: curl {$apiUrl}/tasks?status=pending\n";
echo "3. Check results: curl {$apiUrl}/tasks/{$createdTaskIds[0]}\n";
echo "\n";
