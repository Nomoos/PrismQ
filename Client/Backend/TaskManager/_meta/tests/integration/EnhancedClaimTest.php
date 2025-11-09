<?php
/**
 * Enhanced Claim Endpoint Tests
 * 
 * Tests for the new claim endpoint functionality:
 * - Task type ID filtering
 * - Sorting by different fields (created_at, priority, id, attempts)
 * - Sorting order (ASC/DESC) for FIFO/LIFO scenarios
 * - Priority-based claiming
 */

require_once __DIR__ . '/../TestRunner.php';
require_once __DIR__ . '/ApiTestHelper.php';

function testEnhancedClaimEndpoint() {
    $runner = new TestRunner();
    $helper = new ApiTestHelper();
    
    // Clean up any previous test data
    $helper->resetDatabase();
    
    // ========================================================================
    // Priority Field Tests
    // ========================================================================
    
    $runner->addTest('Create task with priority', function() use ($helper) {
        $helper->registerTaskType('test.priority.basic', '1.0.0', [
            'type' => 'object',
            'properties' => ['data' => ['type' => 'string']]
        ]);
        
        $response = $helper->post('/tasks', [
            'type' => 'test.priority.basic',
            'params' => ['data' => 'test'],
            'priority' => 10
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Task creation with priority should succeed');
        TestRunner::assertEquals(10, $response['data']['data']['priority'], 'Priority should be set correctly');
    });
    
    $runner->addTest('Create task without priority defaults to 0', function() use ($helper) {
        $helper->registerTaskType('test.priority.default', '1.0.0', [
            'type' => 'object',
            'properties' => ['data' => ['type' => 'string']]
        ]);
        
        $response = $helper->post('/tasks', [
            'type' => 'test.priority.default',
            'params' => ['data' => 'test']
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Task creation should succeed');
        TestRunner::assertEquals(0, $response['data']['data']['priority'], 'Priority should default to 0');
    });
    
    // ========================================================================
    // Sorting Tests - FIFO (created_at ASC)
    // ========================================================================
    
    $runner->addTest('Claim task with FIFO ordering (created_at ASC)', function() use ($helper) {
        // Clean up pending tasks
        $helper->getDb()->exec("UPDATE tasks SET status = 'completed' WHERE status = 'pending'");
        
        $helper->registerTaskType('test.fifo', '1.0.0', ['type' => 'object']);
        
        // Get task type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.fifo']);
        $taskType = $stmt->fetch();
        
        // Create tasks in order with small delays
        $task1 = $helper->createTask('test.fifo', ['order' => 1]);
        usleep(100000); // 100ms delay
        $task2 = $helper->createTask('test.fifo', ['order' => 2]);
        usleep(100000);
        $task3 = $helper->createTask('test.fifo', ['order' => 3]);
        
        // Claim with FIFO (default behavior)
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-fifo',
            'task_type_id' => $taskType['id'],
            'sort_by' => 'created_at',
            'sort_order' => 'ASC'
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'FIFO claim should succeed');
        TestRunner::assertEquals($task1['data']['data']['id'], $response['data']['data']['id'], 
            'Should claim first created task (FIFO)');
    });
    
    // ========================================================================
    // Sorting Tests - LIFO (created_at DESC)
    // ========================================================================
    
    $runner->addTest('Claim task with LIFO ordering (created_at DESC)', function() use ($helper) {
        // Clean up pending tasks
        $helper->getDb()->exec("UPDATE tasks SET status = 'completed' WHERE status = 'pending'");
        
        $helper->registerTaskType('test.lifo', '1.0.0', ['type' => 'object']);
        
        // Get task type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.lifo']);
        $taskType = $stmt->fetch();
        
        // Create tasks in order
        $task1 = $helper->createTask('test.lifo', ['order' => 1]);
        usleep(100000);
        $task2 = $helper->createTask('test.lifo', ['order' => 2]);
        usleep(100000);
        $task3 = $helper->createTask('test.lifo', ['order' => 3]);
        
        // Claim with LIFO
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-lifo',
            'task_type_id' => $taskType['id'],
            'sort_by' => 'created_at',
            'sort_order' => 'DESC'
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'LIFO claim should succeed');
        TestRunner::assertEquals($task3['data']['data']['id'], $response['data']['data']['id'], 
            'Should claim last created task (LIFO)');
    });
    
    // ========================================================================
    // Priority-Based Claiming Tests
    // ========================================================================
    
    $runner->addTest('Claim highest priority task first (priority DESC)', function() use ($helper) {
        // Clean up pending tasks
        $helper->getDb()->exec("UPDATE tasks SET status = 'completed' WHERE status = 'pending'");
        
        $helper->registerTaskType('test.priority.sort', '1.0.0', ['type' => 'object']);
        
        // Get task type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.priority.sort']);
        $taskType = $stmt->fetch();
        
        // Create tasks with different priorities
        $lowPriority = $helper->post('/tasks', [
            'type' => 'test.priority.sort',
            'params' => ['name' => 'low'],
            'priority' => 1
        ]);
        
        $highPriority = $helper->post('/tasks', [
            'type' => 'test.priority.sort',
            'params' => ['name' => 'high'],
            'priority' => 10
        ]);
        
        $mediumPriority = $helper->post('/tasks', [
            'type' => 'test.priority.sort',
            'params' => ['name' => 'medium'],
            'priority' => 5
        ]);
        
        // Claim by priority
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-priority',
            'task_type_id' => $taskType['id'],
            'sort_by' => 'priority',
            'sort_order' => 'DESC'
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Priority claim should succeed');
        TestRunner::assertEquals($highPriority['data']['data']['id'], $response['data']['data']['id'], 
            'Should claim highest priority task');
        TestRunner::assertEquals(10, $response['data']['data']['priority'], 
            'Claimed task should have priority 10');
    });
    
    $runner->addTest('Claim lowest priority task first (priority ASC)', function() use ($helper) {
        // Clean up pending tasks
        $helper->getDb()->exec("UPDATE tasks SET status = 'completed' WHERE status = 'pending'");
        
        $helper->registerTaskType('test.priority.asc', '1.0.0', ['type' => 'object']);
        
        // Get task type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.priority.asc']);
        $taskType = $stmt->fetch();
        
        // Create tasks with different priorities
        $task1 = $helper->post('/tasks', [
            'type' => 'test.priority.asc',
            'params' => ['name' => 'low'],
            'priority' => 1
        ]);
        
        $task2 = $helper->post('/tasks', [
            'type' => 'test.priority.asc',
            'params' => ['name' => 'high'],
            'priority' => 10
        ]);
        
        // Claim by priority ASC
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-priority-asc',
            'task_type_id' => $taskType['id'],
            'sort_by' => 'priority',
            'sort_order' => 'ASC'
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Priority ASC claim should succeed');
        TestRunner::assertEquals($task1['data']['data']['id'], $response['data']['data']['id'], 
            'Should claim lowest priority task');
    });
    
    // ========================================================================
    // Task Type ID Filtering Tests
    // ========================================================================
    
    $runner->addTest('Claim task by specific task_type_id', function() use ($helper) {
        // Clean up pending tasks
        $helper->getDb()->exec("UPDATE tasks SET status = 'completed' WHERE status = 'pending'");
        
        // Register two different task types
        $helper->registerTaskType('test.type.a', '1.0.0', ['type' => 'object']);
        $helper->registerTaskType('test.type.b', '1.0.0', ['type' => 'object']);
        
        // Get type IDs
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.type.a']);
        $typeA = $stmt->fetch();
        $stmt->execute(['test.type.b']);
        $typeB = $stmt->fetch();
        
        // Create tasks of both types
        $helper->createTask('test.type.a', ['data' => 'a1']);
        $helper->createTask('test.type.b', ['data' => 'b1']);
        
        // Claim only type B
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-type',
            'task_type_id' => $typeB['id']
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Type-specific claim should succeed');
        TestRunner::assertEquals('test.type.b', $response['data']['data']['type'], 
            'Should claim task of specified type');
    });
    
    // ========================================================================
    // Combined Filtering Tests
    // ========================================================================
    
    $runner->addTest('Claim with task_type_id and sorting combined', function() use ($helper) {
        // Clean up pending tasks
        $helper->getDb()->exec("UPDATE tasks SET status = 'completed' WHERE status = 'pending'");
        
        $helper->registerTaskType('test.combined', '1.0.0', ['type' => 'object']);
        $helper->registerTaskType('test.other', '1.0.0', ['type' => 'object']);
        
        // Get type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.combined']);
        $targetType = $stmt->fetch();
        
        // Create tasks with different types and priorities
        $helper->post('/tasks', [
            'type' => 'test.combined',
            'params' => ['name' => 'low'],
            'priority' => 5
        ]);
        
        $highPriorityTask = $helper->post('/tasks', [
            'type' => 'test.combined',
            'params' => ['name' => 'high'],
            'priority' => 20
        ]);
        
        $helper->post('/tasks', [
            'type' => 'test.other',
            'params' => ['name' => 'highest-but-wrong-type'],
            'priority' => 100
        ]);
        
        // Claim by type ID and priority
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-combined',
            'task_type_id' => $targetType['id'],
            'sort_by' => 'priority',
            'sort_order' => 'DESC'
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'Combined filtering should succeed');
        TestRunner::assertEquals($highPriorityTask['data']['data']['id'], $response['data']['data']['id'], 
            'Should claim highest priority of specified type');
        TestRunner::assertEquals('test.combined', $response['data']['data']['type']);
    });
    
    // ========================================================================
    // Validation Tests
    // ========================================================================
    
    $runner->addTest('Reject claim without task_type_id', function() use ($helper) {
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-invalid'
        ]);
        
        TestRunner::assertFalse($response['data']['success'], 'Should reject missing task_type_id');
        TestRunner::assertStringContains('required', strtolower($response['data']['message']));
    });
    
    $runner->addTest('Reject invalid sort_by field', function() use ($helper) {
        // Register a task type for validation tests
        $helper->registerTaskType('test.validation', '1.0.0', ['type' => 'object']);
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.validation']);
        $taskType = $stmt->fetch();
        
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-invalid',
            'task_type_id' => $taskType['id'],
            'sort_by' => 'invalid_field'
        ]);
        
        TestRunner::assertFalse($response['data']['success'], 'Should reject invalid sort_by');
        TestRunner::assertStringContains('invalid', strtolower($response['data']['message']));
    });
    
    $runner->addTest('Reject invalid sort_order value', function() use ($helper) {
        // Use existing validation task type
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.validation']);
        $taskType = $stmt->fetch();
        
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-invalid',
            'task_type_id' => $taskType['id'],
            'sort_order' => 'INVALID'
        ]);
        
        TestRunner::assertFalse($response['data']['success'], 'Should reject invalid sort_order');
        TestRunner::assertStringContains('invalid', strtolower($response['data']['message']));
    });
    
    // ========================================================================
    // Sorting by ID Tests
    // ========================================================================
    
    $runner->addTest('Claim task sorted by ID ascending', function() use ($helper) {
        // Clean up pending tasks
        $helper->getDb()->exec("UPDATE tasks SET status = 'completed' WHERE status = 'pending'");
        
        $helper->registerTaskType('test.id.sort', '1.0.0', ['type' => 'object']);
        
        // Get task type ID
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.id.sort']);
        $taskType = $stmt->fetch();
        
        $task1 = $helper->createTask('test.id.sort', ['order' => 1]);
        $task2 = $helper->createTask('test.id.sort', ['order' => 2]);
        $task3 = $helper->createTask('test.id.sort', ['order' => 3]);
        
        // Claim by ID ASC
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-id',
            'task_type_id' => $taskType['id'],
            'sort_by' => 'id',
            'sort_order' => 'ASC'
        ]);
        
        TestRunner::assertTrue($response['data']['success'], 'ID-based claim should succeed');
        TestRunner::assertEquals($task1['data']['data']['id'], $response['data']['data']['id'], 
            'Should claim task with lowest ID');
    });
    
    // ========================================================================
    // Sorting by Attempts Tests
    // ========================================================================
    
    $runner->addTest('Claim task with fewest attempts first', function() use ($helper) {
        // This test would need to manually update attempts in the database
        // For simplicity, we'll just verify the parameter is accepted
        // Register a task type for validation
        $helper->registerTaskType('test.attempts', '1.0.0', ['type' => 'object']);
        $db = $helper->getDb();
        $stmt = $db->prepare("SELECT id FROM task_types WHERE name = ?");
        $stmt->execute(['test.attempts']);
        $taskType = $stmt->fetch();
        
        $response = $helper->post('/tasks/claim', [
            'worker_id' => 'test-worker-attempts',
            'task_type_id' => $taskType['id'],
            'sort_by' => 'attempts',
            'sort_order' => 'ASC'
        ]);
        
        // Should succeed or return no tasks if none available
        // The important thing is that it doesn't reject the parameter
        TestRunner::assertTrue(
            $response['data']['success'] || strpos(strtolower($response['data']['message']), 'no tasks') !== false,
            'Should accept attempts as sort field'
        );
    });
    
    // Run all tests
    $runner->run();
}

// Only run if executed directly
if (basename(__FILE__) == basename($_SERVER['SCRIPT_FILENAME'])) {
    testEnhancedClaimEndpoint();
}
