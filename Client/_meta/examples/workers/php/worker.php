#!/usr/bin/env php
<?php

/**
 * TaskManager PHP Worker Example
 *
 * A complete, production-ready worker implementation that demonstrates:
 * - Task claiming from the TaskManager API
 * - Task processing with custom handlers
 * - Comprehensive error handling and retry logic
 * - Graceful shutdown on signals (SIGTERM, SIGINT)
 * - Configurable polling intervals and timeouts
 * - Support for filtering tasks by type pattern
 *
 * Usage:
 *   php worker.php [options]
 *
 * Options:
 *   --api-url=URL          TaskManager API base URL (default: http://localhost/api)
 *   --worker-id=ID         Worker identifier (default: auto-generated)
 *   --type-pattern=PATTERN Filter tasks by type pattern (e.g., "PrismQ.Script.%")
 *   --poll-interval=SEC    Seconds to wait between polls when no tasks (default: 10)
 *   --max-runs=NUM         Maximum number of tasks to process (default: unlimited)
 *   --debug                Enable debug logging
 *   --help                 Show this help message
 *
 * Examples:
 *   # Run worker with default settings
 *   php worker.php
 *
 *   # Run worker with custom API URL
 *   php worker.php --api-url=https://example.com/api
 *
 *   # Process only specific task types
 *   php worker.php --type-pattern="PrismQ.Script.%"
 *
 *   # Process up to 100 tasks then exit
 *   php worker.php --max-runs=100
 */

// Require the WorkerClient helper class
require_once __DIR__ . '/WorkerClient.php';

use PrismQ\TaskManager\Worker\WorkerClient;

// ============================================================================
// Configuration
// ============================================================================

// Parse command line arguments
$config = parseArguments($argv);

// Worker configuration
$apiUrl = $config['api-url'];
$workerId = $config['worker-id'];
$typePattern = $config['type-pattern'];
$pollInterval = $config['poll-interval'];
$maxRuns = $config['max-runs'];
$debug = $config['debug'];

// ============================================================================
// Worker State
// ============================================================================

$shouldStop = false;
$tasksProcessed = 0;
$tasksFailed = 0;
$consecutiveErrors = 0;
$maxConsecutiveErrors = 5;

// Make client and current task available globally for progress updates
$currentTaskId = null;

// ============================================================================
// Signal Handling
// ============================================================================

// Register signal handlers for graceful shutdown
if (function_exists('pcntl_signal')) {
    pcntl_signal(SIGTERM, function () use (&$shouldStop) {
        echo "\n[SHUTDOWN] Received SIGTERM, finishing current task and exiting...\n";
        $shouldStop = true;
    });

    pcntl_signal(SIGINT, function () use (&$shouldStop) {
        echo "\n[SHUTDOWN] Received SIGINT (Ctrl+C), finishing current task and exiting...\n";
        $shouldStop = true;
    });
    if ($debug) {
        echo "[INFO] Signal handlers registered (SIGTERM, SIGINT)\n";
    }
}

// ============================================================================
// Worker Initialization
// ============================================================================

echo "================================\n";
echo "TaskManager PHP Worker\n";
echo "================================\n";
echo "Worker ID:      {$workerId}\n";
echo "API URL:        {$apiUrl}\n";
echo "Type Pattern:   " . ($typePattern ?? 'all types') . "\n";
echo "Poll Interval:  {$pollInterval}s\n";
echo "Max Runs:       " . ($maxRuns > 0 ? $maxRuns : 'unlimited') . "\n";
echo "Debug:          " . ($debug ? 'enabled' : 'disabled') . "\n";
echo "================================\n\n";

// Create worker client
$client = new WorkerClient($apiUrl, $workerId, $debug);

// Check API connectivity
echo "[STARTUP] Checking API connectivity...\n";
if (!$client->checkHealth()) {
    die(
        "[ERROR] Failed to connect to TaskManager API at {$apiUrl}\n" .
        "Please verify the URL and ensure the API is running.\n"
    );
}
echo "[STARTUP] ✓ Connected to TaskManager API\n\n";

// ============================================================================
// Main Worker Loop
// ============================================================================

echo "[WORKER] Starting task processing loop\n";
echo "[WORKER] Press Ctrl+C to stop gracefully\n\n";

while (!$shouldStop) {
    // Process pending signals
    if (function_exists('pcntl_signal_dispatch')) {
        pcntl_signal_dispatch();
    }

    // Check if we've reached max runs
    if ($maxRuns > 0 && $tasksProcessed >= $maxRuns) {
        echo "[WORKER] Reached maximum task count ({$maxRuns}), exiting\n";
        break;
    }

    try {
        // Try to claim a task
        $task = $client->claimTask($typePattern);

        if ($task === null) {
            // No tasks available, wait before trying again
            if ($debug) {
                echo "[IDLE] No tasks available, waiting {$pollInterval}s...\n";
            }
            sleep($pollInterval);
            continue;
        }

        // Reset consecutive error counter on successful claim
        $consecutiveErrors = 0;

        // Set current task ID for progress updates
        $currentTaskId = $task['id'];

        // Process the task
        echo "[TASK #{$task['id']}] Processing (type: {$task['type']}, attempt: {$task['attempts']})\n";

        try {
            $result = processTask($task);

            // Mark task as completed
            $client->completeTask($task['id'], $result);

            $tasksProcessed++;
            echo "[TASK #{$task['id']}] ✓ Completed successfully ({$tasksProcessed} total)\n\n";
        } catch (Exception $e) {
            // Task processing failed, mark as failed
            $errorMessage = $e->getMessage();
            echo "[TASK #{$task['id']}] ✗ Failed: {$errorMessage}\n";

            $client->failTask($task['id'], $errorMessage);

            $tasksFailed++;
            echo "[TASK #{$task['id']}] Marked as failed ({$tasksFailed} total failures)\n\n";
        } finally {
            // Clear current task ID
            $currentTaskId = null;
        }
    } catch (Exception $e) {
        // API communication error
        $consecutiveErrors++;

        echo "[ERROR] API error: {$e->getMessage()}\n";
        echo "[ERROR] Consecutive errors: {$consecutiveErrors}/{$maxConsecutiveErrors}\n";

        if ($consecutiveErrors >= $maxConsecutiveErrors) {
            echo "[ERROR] Too many consecutive errors, exiting\n";
            break;
        }

        // Wait longer on errors
        echo "[ERROR] Waiting " . ($pollInterval * 2) . "s before retry...\n\n";
        sleep($pollInterval * 2);
    }
}

// ============================================================================
// Worker Shutdown
// ============================================================================

echo "\n================================\n";
echo "Worker Shutdown Summary\n";
echo "================================\n";
echo "Tasks Processed: {$tasksProcessed}\n";
echo "Tasks Failed:    {$tasksFailed}\n";
echo "Success Rate:    ";

if ($tasksProcessed > 0) {
    $successRate = (($tasksProcessed - $tasksFailed) / $tasksProcessed) * 100;
    echo number_format($successRate, 1) . "%\n";
} else {
    echo "N/A (no tasks processed)\n";
}

echo "================================\n";

exit(0);

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Process a task based on its type
 *
 * This is where you implement your task-specific logic.
 * Add handlers for each task type your worker supports.
 *
 * @param array $task Task data from TaskManager
 * @return mixed Result data to store in TaskManager
 * @throws Exception on processing errors
 */
function processTask(array $task): mixed
{
    $type = $task['type'];
    $params = $task['params'];

    // Route to appropriate handler based on task type
    switch ($type) {
        case 'example.echo':
            return handleEchoTask($params);

        case 'example.uppercase':
            return handleUppercaseTask($params);

        case 'example.math.add':
            return handleMathAddTask($params);

        case 'example.sleep':
            return handleSleepTask($params);

        case 'example.error':
            return handleErrorTask($params);

        default:
            // Unknown task type - you can either handle it generically or fail
            throw new Exception("Unknown task type: {$type}");
    }
}

/**
 * Example handler: Echo task
 * Simply returns the input message
 *
 * @param array $params Task parameters
 * @return array Result data
 * @throws Exception on validation errors
 */
function handleEchoTask(array $params): array
{
    if (!isset($params['message'])) {
        throw new Exception("Missing required parameter: message");
    }

    return [
        'echoed' => $params['message'],
        'processed_at' => date('c')
    ];
}

/**
 * Example handler: Uppercase task
 * Converts text to uppercase
 *
 * @param array $params Task parameters
 * @return array Result data
 * @throws Exception on validation errors
 */
function handleUppercaseTask(array $params): array
{
    if (!isset($params['text'])) {
        throw new Exception("Missing required parameter: text");
    }

    return [
        'original' => $params['text'],
        'uppercase' => strtoupper($params['text']),
        'length' => strlen($params['text'])
    ];
}

/**
 * Example handler: Math addition task
 * Adds two numbers
 *
 * @param array $params Task parameters
 * @return array Result data
 * @throws Exception on validation errors
 */
function handleMathAddTask(array $params): array
{
    if (!isset($params['a']) || !isset($params['b'])) {
        throw new Exception("Missing required parameters: a, b");
    }

    if (!is_numeric($params['a']) || !is_numeric($params['b'])) {
        throw new Exception("Parameters must be numeric");
    }

    return [
        'a' => $params['a'],
        'b' => $params['b'],
        'result' => $params['a'] + $params['b']
    ];
}

/**
 * Example handler: Sleep task
 * Simulates long-running task with progress updates
 *
 * @param array $params Task parameters
 * @return array Result data
 * @throws Exception on validation errors
 */
function handleSleepTask(array $params): array
{
    global $client, $currentTaskId;
    
    if (!isset($params['seconds'])) {
        throw new Exception("Missing required parameter: seconds");
    }

    $seconds = intval($params['seconds']);

    if ($seconds < 0 || $seconds > 60) {
        throw new Exception("Sleep duration must be between 0 and 60 seconds");
    }

    // Simulate progress updates during long-running task
    $steps = min($seconds, 10); // Update progress at most 10 times
    $stepDuration = $seconds / $steps;
    
    for ($i = 1; $i <= $steps; $i++) {
        sleep($stepDuration);
        
        // Update progress
        $progress = intval(($i / $steps) * 100);
        if ($currentTaskId && $client) {
            try {
                $client->updateProgress($currentTaskId, $progress, "Step {$i}/{$steps}");
            } catch (Exception $e) {
                // Log but don't fail the task on progress update errors
                echo "[WARNING] Failed to update progress: {$e->getMessage()}\n";
            }
        }
    }

    return [
        'slept_seconds' => $seconds,
        'completed_at' => date('c')
    ];
}

/**
 * Example handler: Error task
 * Intentionally fails to demonstrate error handling
 *
 * @param array $params Task parameters
 * @throws Exception always
 */
function handleErrorTask(array $params): never
{
    $errorType = $params['error_type'] ?? 'generic';

    switch ($errorType) {
        case 'exception':
            throw new Exception("Intentional exception for testing");

        case 'validation':
            throw new Exception("Validation failed: Invalid input data");

        case 'timeout':
            throw new Exception("Operation timed out after 30 seconds");

        default:
            throw new Exception("Generic error for testing");
    }
}

/**
 * Parse command line arguments
 *
 * @param array $argv Command line arguments
 * @return array Configuration array
 */
function parseArguments(array $argv): array
{
    $config = [
        'api-url' => getenv('TASKMANAGER_API_URL') ?: 'http://localhost/api',
        'worker-id' => getenv('WORKER_ID') ?: ('worker-' . gethostname() . '-' . getmypid()),
        'type-pattern' => getenv('TASK_TYPE_PATTERN') ?: null,
        'poll-interval' => intval(getenv('POLL_INTERVAL') ?: 10),
        'max-runs' => intval(getenv('MAX_RUNS') ?: 0),
        'debug' => (getenv('DEBUG') === 'true' || getenv('DEBUG') === '1')
    ];

    // Parse command line arguments
    foreach ($argv as $arg) {
        if ($arg === '--help' || $arg === '-h') {
            showHelp();
            exit(0);
        }

        if (strpos($arg, '--') === 0) {
            $parts = explode('=', substr($arg, 2), 2);
            $key = $parts[0];
            $value = isset($parts[1]) ? $parts[1] : true;

            if ($key === 'debug') {
                $config['debug'] = true;
            } elseif (isset($config[$key])) {
                $config[$key] = $value;
            }
        }
    }

    return $config;
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
TaskManager PHP Worker Example

Usage:
  php {$script} [options]

Options:
  --api-url=URL          TaskManager API base URL (default: http://localhost/api)
  --worker-id=ID         Worker identifier (default: auto-generated)
  --type-pattern=PATTERN Filter tasks by type pattern (e.g., "PrismQ.Script.%")
  --poll-interval=SEC    Seconds to wait between polls when no tasks (default: 10)
  --max-runs=NUM         Maximum number of tasks to process (default: unlimited)
  --debug                Enable debug logging
  --help, -h             Show this help message

Environment Variables:
  TASKMANAGER_API_URL    API base URL (overridden by --api-url)
  WORKER_ID              Worker identifier (overridden by --worker-id)
  TASK_TYPE_PATTERN      Task type filter (overridden by --type-pattern)
  POLL_INTERVAL          Poll interval in seconds (overridden by --poll-interval)
  MAX_RUNS               Maximum tasks to process (overridden by --max-runs)
  DEBUG                  Enable debug logging (set to 'true' or '1')

Examples:
  # Run worker with default settings
  php {$script}

  # Run worker with custom API URL
  php {$script} --api-url=https://example.com/api

  # Process only specific task types
  php {$script} --type-pattern="PrismQ.Script.%"

  # Process up to 100 tasks then exit
  php {$script} --max-runs=100

  # Enable debug logging
  php {$script} --debug

  # Use environment variables
  export TASKMANAGER_API_URL=https://example.com/api
  export WORKER_ID=my-worker-01
  export DEBUG=true
  php {$script}

HELP;
}
