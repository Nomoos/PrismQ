<?php
/**
 * API Integration Tests
 * 
 * Tests all TaskManager API endpoints with various scenarios:
 * - Valid requests (happy path)
 * - Invalid inputs (validation errors)
 * - Error scenarios (not found, unauthorized)
 * - Edge cases (empty data, large payloads)
 * 
 * Note: These tests require a running database.
 * Use a test database to avoid affecting production data.
 */

require_once __DIR__ . '/../TestRunner.php';
require_once __DIR__ . '/ApiTestHelper.php';

function testApiIntegration() {
    $runner = new TestRunner();
    $helper = new ApiTestHelper();
    
    // Clean up any previous test data
    $helper->resetDatabase();
    
    // ========================================================================
    // Health Endpoint Tests
    // ========================================================================
    
    $runner->addTest('Health check returns success', function() use ($helper) {
        $response = $helper->get('/health');
        
        TestRunner::assertEquals(200, $response['code'], 'Health check should return 200');
        TestRunner::assertTrue($response['data']['success'], 'Health check should succeed');
        TestRunner::assertArrayHasKey('timestamp', $response['data'], 'Should include timestamp');
    });
    
    // ========================================================================
    // Task Type Registration Tests
    // ========================================================================
    
    $runner->addTest('Register new task type successfully', function() use ($helper) {
        $response = $helper->registerTaskType('test.register.new', '1.0.0', [
            'type' => 'object',
            'properties' => [
                'value' => ['type' => 'string']
            ],
            'required' => ['value']
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Registration should succeed');
        TestRunner::assertStringContains('registered successfully', $response['data']['message']);
    });
    
    $runner->addTest('Register task type with missing name fails', function() use ($helper) {
        $response = $helper->post('/task-types/register', [
            'version' => '1.0.0',
            'param_schema' => ['type' => 'object']
        ]);
        
        TestRunner::assertFalse($response['data']['success'], 'Should fail without name');
        TestRunner::assertStringContains('required', strtolower($response['data']['message']));
    });
    
    $runner->addTest('Register task type with invalid schema fails', function() use ($helper) {
        $response = $helper->post('/task-types/register', [
            'name' => 'test.invalid.schema',
            'version' => '1.0.0',
            'param_schema' => 'not-an-object'
        ]);
        
        TestRunner::assertFalse($response['data']['success'], 'Should fail with invalid schema');
    });
    
    $runner->addTest('Update existing task type version', function() use ($helper) {
        // First registration
        $helper->registerTaskType('test.version.update', '1.0.0', [
            'type' => 'object',
            'properties' => ['field1' => ['type' => 'string']]
        ]);
        
        // Update with new version
        $response = $helper->registerTaskType('test.version.update', '2.0.0', [
            'type' => 'object',
            'properties' => [
                'field1' => ['type' => 'string'],
                'field2' => ['type' => 'number']
            ]
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Version update should succeed');
    });
    
    // ========================================================================
    // Get Task Type Tests
    // ========================================================================
    
    $runner->addTest('Get existing task type details', function() use ($helper) {
        // Register a task type first
        $helper->registerTaskType('test.get.details', '1.0.0', [
            'type' => 'object',
            'properties' => ['name' => ['type' => 'string']]
        ]);
        
        $response = $helper->get('/task-types/test.get.details');
        
        TestRunner::assertTrue($response['data']['success'], 'Get should succeed');
        TestRunner::assertEquals('test.get.details', $response['data']['data']['name']);
        TestRunner::assertEquals('1.0.0', $response['data']['data']['version']);
    });
    
    $runner->addTest('Get non-existent task type fails', function() use ($helper) {
        $response = $helper->get('/task-types/test.nonexistent.type');
        
        TestRunner::assertFalse($response['data']['success'], 'Should fail for non-existent type');
        TestRunner::assertStringContains('not found', strtolower($response['data']['message']));
    });
    
    // ========================================================================
    // List Task Types Tests
    // ========================================================================
    
    $runner->addTest('List all task types', function() use ($helper) {
        // Register a few task types
        $helper->registerTaskType('test.list.one', '1.0.0', ['type' => 'object']);
        $helper->registerTaskType('test.list.two', '1.0.0', ['type' => 'object']);
        
        $response = $helper->get('/task-types');
        
        TestRunner::assertTrue($response['data']['success'], 'List should succeed');
        TestRunner::assertArrayHasKey('data', $response['data'], 'Should have data array');
        TestRunner::assertTrue(is_array($response['data']['data']), 'Data should be array');
    });
    
    $runner->addTest('List active task types only', function() use ($helper) {
        $response = $helper->get('/task-types', ['active_only' => 'true']);
        
        TestRunner::assertTrue($response['data']['success'], 'List active should succeed');
        TestRunner::assertTrue(is_array($response['data']['data']), 'Should return array');
    });
    
    // ========================================================================
    // Create Task Tests
    // ========================================================================
    
    $runner->addTest('Create task with valid data', function() use ($helper) {
        // Register task type first
        $helper->registerTaskType('test.create.valid', '1.0.0', [
            'type' => 'object',
            'properties' => [
                'message' => ['type' => 'string']
            ],
            'required' => ['message']
        ]);
        
        $response = $helper->createTask('test.create.valid', [
            'message' => 'Test message'
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Task creation should succeed');
        TestRunner::assertArrayHasKey('id', $response['data']['data'], 'Should return task ID');
        TestRunner::assertEquals('pending', $response['data']['data']['status'], 'Status should be pending');
    });
    
    $runner->addTest('Create task with invalid parameters fails', function() use ($helper) {
        // Use existing task type with required fields
        $helper->registerTaskType('test.create.invalid', '1.0.0', [
            'type' => 'object',
            'properties' => [
                'required_field' => ['type' => 'string']
            ],
            'required' => ['required_field']
        ]);
        
        $response = $helper->createTask('test.create.invalid', [
            'wrong_field' => 'value'
        ]);
        
        TestRunner::assertFalse($response['data']['success'], 'Should fail with invalid params');
    });
    
    $runner->addTest('Create task with non-existent type fails', function() use ($helper) {
        $response = $helper->post('/tasks', [
            'type' => 'test.nonexistent.type',
            'params' => []
        ]);
        
        TestRunner::assertFalse($response['data']['success'], 'Should fail for non-existent type');
    });
    
    $runner->addTest('Task deduplication works', function() use ($helper) {
        // Register task type
        $helper->registerTaskType('test.dedupe', '1.0.0', [
            'type' => 'object',
            'properties' => ['value' => ['type' => 'string']]
        ]);
        
        // Create first task
        $response1 = $helper->createTask('test.dedupe', ['value' => 'same']);
        $taskId1 = $response1['data']['data']['id'];
        
        // Create duplicate task
        $response2 = $helper->createTask('test.dedupe', ['value' => 'same']);
        $taskId2 = $response2['data']['data']['id'];
        
        TestRunner::assertEquals($taskId1, $taskId2, 'Duplicate task should return same ID');
    });
    
    // ========================================================================
    // Claim Task Tests
    // ========================================================================
    
    $runner->addTest('Claim pending task successfully', function() use ($helper) {
        // Register and create a task
        $helper->registerTaskType('test.claim.valid', '1.0.0', [
            'type' => 'object',
            'properties' => ['data' => ['type' => 'string']]
        ]);
        
        // Get task type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.claim.valid']);
        $taskType = $stmt->fetch();
        
        $createResponse = $helper->createTask('test.claim.valid', ['data' => 'test']);
        
        // Claim the task
        $claimResponse = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-claim',
            'task_type_id' => $taskType['id']
        ]);
        
        TestRunner::assertTrue($claimResponse['data']['success'], 'Claim should succeed');
        TestRunner::assertArrayHasKey('id', $claimResponse['data']['data'], 'Should return task');
        TestRunner::assertArrayHasKey('type', $claimResponse['data']['data'], 'Should include type');
        TestRunner::assertArrayHasKey('params', $claimResponse['data']['data'], 'Should include params');
    });
    
    $runner->addTest('Claim with type pattern filter', function() use ($helper) {
        // Create tasks of different types
        $helper->registerTaskType('test.pattern.match', '1.0.0', ['type' => 'object']);
        $helper->registerTaskType('other.pattern.match', '1.0.0', ['type' => 'object']);
        
        // Get task type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.pattern.match']);
        $taskType = $stmt->fetch();
        
        $helper->createTask('test.pattern.match', []);
        $helper->createTask('other.pattern.match', []);
        
        // Claim with pattern
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-pattern',
            'task_type_id' => $taskType['id'],
            'type_pattern' => 'test.%'
        ]);
        
        if ($response['data']['success'] && isset($response['data']['data']['type'])) {
            TestRunner::assertStringContains('test.', $response['data']['data']['type'], 
                'Claimed task should match pattern');
        }
    });
    
    $runner->addTest('Claim when no tasks available', function() use ($helper) {
        // Clean up all pending tasks first
        $helper->getDb()->exec("UPDATE tasks SET status = 'completed' WHERE status = 'pending'");
        
        // Register a task type to get an ID
        $helper->registerTaskType('test.empty', '1.0.0', ['type' => 'object']);
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.empty']);
        $taskType = $stmt->fetch();
        
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-empty',
            'task_type_id' => $taskType['id']
        ]);
        
        // Should return success=false or empty data
        if (!$response['data']['success']) {
            TestRunner::assertStringContains('no tasks', strtolower($response['data']['message']));
        }
    });
    
    // ========================================================================
    // Complete Task Tests
    // ========================================================================
    
    $runner->addTest('Complete task successfully', function() use ($helper) {
        // Register, create, and claim a task
        $helper->registerTaskType('test.complete.success', '1.0.0', ['type' => 'object']);
        
        // Get task type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.complete.success']);
        $taskType = $stmt->fetch();
        
        $createResponse = $helper->createTask('test.complete.success', []);
        $taskId = $createResponse['data']['data']['id'];
        
        $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-complete',
            'task_type_id' => $taskType['id']
        ]);
        
        // Complete the task
        $response = $helper->post("/tasks/{$taskId}/complete", [
            'worker_id' => 'test-worker-complete',
            'success' => true,
            'result' => ['output' => 'Task completed']
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Complete should succeed');
        
        // Verify status in database
        $task = $helper->verifyDbRecord('tasks', $taskId);
        TestRunner::assertEquals('completed', $task['status'], 'Status should be completed');
    });
    
    $runner->addTest('Mark task as failed', function() use ($helper) {
        // Register, create, and claim a task
        $helper->registerTaskType('test.complete.fail', '1.0.0', ['type' => 'object']);
        
        // Get task type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.complete.fail']);
        $taskType = $stmt->fetch();
        
        $createResponse = $helper->createTask('test.complete.fail', []);
        $taskId = $createResponse['data']['data']['id'];
        
        $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-fail',
            'task_type_id' => $taskType['id']
        ]);
        
        // Mark as failed
        $response = $helper->post("/tasks/{$taskId}/complete", [
            'worker_id' => 'test-worker-fail',
            'success' => false,
            'error' => 'Task processing failed'
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Failure marking should succeed');
        
        // Verify status in database
        $task = $helper->verifyDbRecord('tasks', $taskId);
        TestRunner::assertContains($task['status'], ['failed', 'pending'], 
            'Status should be failed or pending (for retry)');
    });
    
    // ========================================================================
    // Get Task Status Tests
    // ========================================================================
    
    $runner->addTest('Get existing task status', function() use ($helper) {
        // Create a task
        $helper->registerTaskType('test.get.status', '1.0.0', ['type' => 'object']);
        $createResponse = $helper->createTask('test.get.status', []);
        $taskId = $createResponse['data']['data']['id'];
        
        // Get status
        $response = $helper->get("/tasks/{$taskId}");
        
        TestRunner::assertTrue($response['data']['success'], 'Get status should succeed');
        TestRunner::assertEquals($taskId, $response['data']['data']['id'], 'Should return correct task');
        TestRunner::assertArrayHasKey('status', $response['data']['data'], 'Should include status');
    });
    
    $runner->addTest('Get non-existent task fails', function() use ($helper) {
        $response = $helper->get('/tasks/999999');
        
        TestRunner::assertFalse($response['data']['success'], 'Should fail for non-existent task');
    });
    
    // ========================================================================
    // List Tasks Tests
    // ========================================================================
    
    $runner->addTest('List all tasks', function() use ($helper) {
        $response = $helper->get('/tasks');
        
        TestRunner::assertTrue($response['data']['success'], 'List should succeed');
        TestRunner::assertArrayHasKey('data', $response['data'], 'Should have data');
        TestRunner::assertTrue(is_array($response['data']['data']), 'Data should be array');
    });
    
    $runner->addTest('List tasks with status filter', function() use ($helper) {
        $response = $helper->get('/tasks', ['status' => 'pending']);
        
        TestRunner::assertTrue($response['data']['success'], 'Filtered list should succeed');
        
        // Verify all returned tasks have pending status
        if (!empty($response['data']['data'])) {
            foreach ($response['data']['data'] as $task) {
                TestRunner::assertEquals('pending', $task['status'], 
                    'All tasks should have pending status');
            }
        }
    });
    
    $runner->addTest('List tasks with pagination', function() use ($helper) {
        $response = $helper->get('/tasks', ['limit' => 5, 'offset' => 0]);
        
        TestRunner::assertTrue($response['data']['success'], 'Paginated list should succeed');
        // Verify we get at most 5 tasks (might be fewer if less data available)
        if (!empty($response['data']['data'])) {
            TestRunner::assertTrue(
                count($response['data']['data']) <= 5, 
                'Should return at most 5 tasks'
            );
        }
    });
    
    // Clean up
    $helper->cleanup();
    
    return $runner->run();
}

// Allow running directly
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    exit(testApiIntegration() ? 0 : 1);
}
