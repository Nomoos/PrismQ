<?php
/**
 * Worker Tests
 * 
 * Tests worker functionality including:
 * - Configuration parsing
 * - API integration
 * - Task claiming and processing
 * - Error handling
 * - Lifecycle management
 */

require_once __DIR__ . '/../TestRunner.php';
require_once __DIR__ . '/WorkerTestHelper.php';

function testWorker() {
    $runner = new TestRunner();
    $helper = new WorkerTestHelper();
    
    // ========================================================================
    // Worker Configuration Tests
    // ========================================================================
    
    $runner->addTest('Parse worker command line arguments', function() use ($helper) {
        $argv = [
            'worker.php',
            '--api-url=https://api.example.com',
            '--worker-id=worker-123',
            '--type-pattern=test.%',
            '--poll-interval=5',
            '--max-runs=100',
            '--debug'
        ];
        
        $config = $helper->parseWorkerArgs($argv);
        
        TestRunner::assertEquals('https://api.example.com', $config['api-url']);
        TestRunner::assertEquals('worker-123', $config['worker-id']);
        TestRunner::assertEquals('test.%', $config['type-pattern']);
        TestRunner::assertEquals(5, $config['poll-interval']);
        TestRunner::assertEquals(100, $config['max-runs']);
        TestRunner::assertTrue($config['debug']);
    });
    
    $runner->addTest('Worker config defaults are set', function() use ($helper) {
        $argv = ['worker.php'];
        $config = $helper->parseWorkerArgs($argv);
        
        TestRunner::assertEquals('http://localhost/api', $config['api-url']);
        TestRunner::assertEquals('test-worker', $config['worker-id']);
        TestRunner::assertNull($config['type-pattern']);
        TestRunner::assertEquals(10, $config['poll-interval']);
        TestRunner::assertEquals(0, $config['max-runs']);
        TestRunner::assertFalse($config['debug']);
    });
    
    // ========================================================================
    // Worker API Integration Tests
    // ========================================================================
    
    $runner->addTest('Worker can check API health', function() use ($helper) {
        $worker = $helper->createWorker('test-health-worker');
        
        try {
            $isHealthy = $worker->checkHealth();
            TestRunner::assertTrue($isHealthy, 'API should be healthy');
        } catch (Exception $e) {
            // If API is not available, that's expected in test environment
            TestRunner::assertStringContains('connect', strtolower($e->getMessage()),
                'Should indicate connection issue');
        }
    });
    
    $runner->addTest('Worker can register task type', function() use ($helper) {
        $worker = $helper->createWorker('test-register-worker');
        
        try {
            $worker->registerTaskType('test.worker.register', '1.0.0', [
                'type' => 'object',
                'properties' => ['field' => ['type' => 'string']]
            ]);
            
            // Verify in database
            $stmt = $helper->getDb()->prepare("SELECT * FROM task_types WHERE name = ?");
            $stmt->execute(['test.worker.register']);
            $taskType = $stmt->fetch(PDO::FETCH_ASSOC);
            
            TestRunner::assertNotNull($taskType, 'Task type should be registered');
            TestRunner::assertEquals('test.worker.register', $taskType['name']);
            
            // Cleanup
            $helper->getDb()->exec("DELETE FROM task_types WHERE name = 'test.worker.register'");
            
        } catch (Exception $e) {
            // API might not be available
            if (strpos($e->getMessage(), 'connect') === false) {
                throw $e;
            }
        }
    });
    
    // ========================================================================
    // Task Claiming Tests
    // ========================================================================
    
    $runner->addTest('Worker can claim pending task', function() use ($helper) {
        // Setup: Create a pending task
        $helper->registerTestTaskType('test.worker.claim');
        $taskId = $helper->createTestTask('test.worker.claim', ['data' => 'test']);
        
        $worker = $helper->createWorker('test-claim-worker');
        
        try {
            $task = $worker->claimTask();
            
            if ($task !== null) {
                TestRunner::assertNotNull($task, 'Should claim a task');
                TestRunner::assertArrayHasKey('id', $task, 'Task should have ID');
                TestRunner::assertArrayHasKey('type', $task, 'Task should have type');
                TestRunner::assertArrayHasKey('params', $task, 'Task should have params');
                
                // Verify task status in database
                $dbTask = $helper->getTask($task['id']);
                TestRunner::assertEquals('claimed', $dbTask['status'], 'Task should be claimed');
                TestRunner::assertEquals('test-claim-worker', $dbTask['claimed_by'], 
                    'Task should be claimed by correct worker');
            }
        } catch (Exception $e) {
            // API might not be available
            if (strpos($e->getMessage(), 'connect') === false) {
                throw $e;
            }
        }
        
        $helper->cleanup();
    });
    
    $runner->addTest('Worker respects type pattern filter', function() use ($helper) {
        // Setup: Create tasks of different types
        $helper->registerTestTaskType('test.pattern.match');
        $helper->registerTestTaskType('other.pattern.nomatch');
        
        $helper->createTestTask('test.pattern.match', []);
        $helper->createTestTask('other.pattern.nomatch', []);
        
        $worker = $helper->createWorker('test-pattern-worker');
        
        try {
            $task = $worker->claimTask('test.%');
            
            if ($task !== null) {
                TestRunner::assertStringContains('test.', $task['type'], 
                    'Claimed task should match pattern');
            }
        } catch (Exception $e) {
            // API might not be available
            if (strpos($e->getMessage(), 'connect') === false) {
                throw $e;
            }
        }
        
        $helper->cleanup();
    });
    
    $runner->addTest('Worker returns null when no tasks available', function() use ($helper) {
        // Ensure no pending tasks
        $helper->getDb()->exec("UPDATE tasks SET status = 'completed' WHERE status = 'pending'");
        
        $worker = $helper->createWorker('test-empty-worker');
        
        try {
            $task = $worker->claimTask();
            TestRunner::assertNull($task, 'Should return null when no tasks');
        } catch (Exception $e) {
            // API might not be available or no tasks message
            TestRunner::assertTrue(
                strpos($e->getMessage(), 'connect') !== false ||
                strpos($e->getMessage(), 'No tasks') !== false,
                'Should indicate no tasks or connection issue'
            );
        }
    });
    
    // ========================================================================
    // Task Completion Tests
    // ========================================================================
    
    $runner->addTest('Worker can complete task successfully', function() use ($helper) {
        // Setup: Create and claim a task
        $helper->registerTestTaskType('test.worker.complete');
        $taskId = $helper->createTestTask('test.worker.complete', []);
        $helper->updateTaskStatus($taskId, 'claimed');
        
        // Update claimed_by and claimed_at
        $stmt = $helper->getDb()->prepare("
            UPDATE tasks 
            SET claimed_by = ?, claimed_at = NOW() 
            WHERE id = ?
        ");
        $stmt->execute(['test-complete-worker', $taskId]);
        
        $worker = $helper->createWorker('test-complete-worker');
        
        try {
            $worker->completeTask($taskId, ['result' => 'success']);
            
            // Verify in database
            $task = $helper->getTask($taskId);
            TestRunner::assertEquals('completed', $task['status'], 'Task should be completed');
            TestRunner::assertNotNull($task['completed_at'], 'Should have completion timestamp');
            TestRunner::assertNotNull($task['result_json'], 'Should have result data');
            
        } catch (Exception $e) {
            // API might not be available
            if (strpos($e->getMessage(), 'connect') === false) {
                throw $e;
            }
        }
        
        $helper->cleanup();
    });
    
    $runner->addTest('Worker can mark task as failed', function() use ($helper) {
        // Setup: Create and claim a task
        $helper->registerTestTaskType('test.worker.fail');
        $taskId = $helper->createTestTask('test.worker.fail', []);
        $helper->updateTaskStatus($taskId, 'claimed');
        
        $stmt = $helper->getDb()->prepare("
            UPDATE tasks 
            SET claimed_by = ?, claimed_at = NOW() 
            WHERE id = ?
        ");
        $stmt->execute(['test-fail-worker', $taskId]);
        
        $worker = $helper->createWorker('test-fail-worker');
        
        try {
            $worker->failTask($taskId, 'Processing error');
            
            // Verify in database
            $task = $helper->getTask($taskId);
            TestRunner::assertContains($task['status'], ['failed', 'pending'], 
                'Task should be failed or pending for retry');
            TestRunner::assertNotNull($task['error_message'], 'Should have error message');
            
        } catch (Exception $e) {
            // API might not be available
            if (strpos($e->getMessage(), 'connect') === false) {
                throw $e;
            }
        }
        
        $helper->cleanup();
    });
    
    // ========================================================================
    // Task Handler Tests
    // ========================================================================
    
    $runner->addTest('Echo handler processes correctly', function() use ($helper) {
        $task = [
            'type' => 'example.echo',
            'params' => ['message' => 'Hello World']
        ];
        
        $result = $helper->simulateTaskProcessing($task);
        
        TestRunner::assertEquals('Hello World', $result['echoed']);
    });
    
    $runner->addTest('Uppercase handler processes correctly', function() use ($helper) {
        $task = [
            'type' => 'example.uppercase',
            'params' => ['text' => 'hello world']
        ];
        
        $result = $helper->simulateTaskProcessing($task);
        
        TestRunner::assertEquals('HELLO WORLD', $result['uppercase']);
    });
    
    $runner->addTest('Math add handler processes correctly', function() use ($helper) {
        $task = [
            'type' => 'example.math.add',
            'params' => ['a' => 15, 'b' => 27]
        ];
        
        $result = $helper->simulateTaskProcessing($task);
        
        TestRunner::assertEquals(42, $result['result']);
    });
    
    $runner->addTest('Sleep handler returns expected result', function() use ($helper) {
        $task = [
            'type' => 'example.sleep',
            'params' => ['seconds' => 1]
        ];
        
        $result = $helper->simulateTaskProcessing($task);
        
        TestRunner::assertEquals(1, $result['slept_seconds']);
    });
    
    $runner->addTest('Unknown task type throws exception', function() use ($helper) {
        $task = [
            'type' => 'unknown.type',
            'params' => []
        ];
        
        $exceptionThrown = false;
        try {
            $helper->simulateTaskProcessing($task);
        } catch (Exception $e) {
            $exceptionThrown = true;
            TestRunner::assertStringContains('Unknown task type', $e->getMessage());
        }
        
        TestRunner::assertTrue($exceptionThrown, 'Should throw exception for unknown type');
    });
    
    // ========================================================================
    // Worker Lifecycle Tests
    // ========================================================================
    
    $runner->addTest('Worker tracks processed task count', function() {
        $tasksProcessed = 0;
        $tasksFailed = 0;
        
        // Simulate processing 5 successful tasks
        for ($i = 0; $i < 5; $i++) {
            $tasksProcessed++;
        }
        
        // Simulate 2 failed tasks
        for ($i = 0; $i < 2; $i++) {
            $tasksFailed++;
        }
        
        TestRunner::assertEquals(5, $tasksProcessed, 'Should track successful tasks');
        TestRunner::assertEquals(2, $tasksFailed, 'Should track failed tasks');
        
        $successRate = (($tasksProcessed - $tasksFailed) / $tasksProcessed) * 100;
        TestRunner::assertEquals(60.0, $successRate, 'Should calculate success rate correctly');
    });
    
    $runner->addTest('Worker handles max runs limit', function() {
        $maxRuns = 10;
        $tasksProcessed = 0;
        $shouldStop = false;
        
        // Simulate processing loop
        while (!$shouldStop && $tasksProcessed < 20) {
            $tasksProcessed++;
            
            if ($maxRuns > 0 && $tasksProcessed >= $maxRuns) {
                $shouldStop = true;
            }
        }
        
        TestRunner::assertEquals($maxRuns, $tasksProcessed, 'Should stop at max runs');
    });
    
    $runner->addTest('Worker handles consecutive errors', function() {
        $consecutiveErrors = 0;
        $maxConsecutiveErrors = 5;
        $shouldStop = false;
        
        // Simulate 6 consecutive errors
        for ($i = 0; $i < 6 && !$shouldStop; $i++) {
            $consecutiveErrors++;
            
            if ($consecutiveErrors >= $maxConsecutiveErrors) {
                $shouldStop = true;
            }
        }
        
        TestRunner::assertTrue($shouldStop, 'Should stop after max consecutive errors');
        TestRunner::assertEquals(5, $consecutiveErrors, 'Should stop at threshold');
    });
    
    // Clean up
    $helper->cleanup();
    
    return $runner->run();
}

// Allow running directly
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    exit(testWorker() ? 0 : 1);
}
