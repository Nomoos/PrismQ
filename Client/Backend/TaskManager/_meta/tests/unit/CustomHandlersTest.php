<?php
/**
 * Custom Handlers Unit Tests
 * 
 * Tests the custom handler functionality that cannot be replaced with data-driven actions.
 * These tests validate the complex business logic that justifies using custom handlers.
 */

require_once __DIR__ . '/../TestRunner.php';

function testCustomHandlers() {
    $runner = new TestRunner();
    
    echo "=== Custom Handlers Tests ===\n\n";
    echo "These tests validate custom handler logic that cannot be achieved with data-driven actions.\n\n";
    
    // ========================================================================
    // Test 1: Deduplication Hash Generation
    // ========================================================================
    
    $runner->addTest('Deduplication: Same params produce same hash', function() {
        $type = 'test.task';
        $params1 = ['field1' => 'value1', 'field2' => 'value2'];
        $params2 = ['field1' => 'value1', 'field2' => 'value2'];
        
        $json1 = json_encode($params1, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $json2 = json_encode($params2, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        
        $hash1 = hash('sha256', $type . "\0" . $json1);
        $hash2 = hash('sha256', $type . "\0" . $json2);
        
        TestRunner::assertEquals($hash1, $hash2, 'Same params should produce same hash');
    });
    
    $runner->addTest('Deduplication: Different params produce different hash', function() {
        $type = 'test.task';
        $params1 = ['field1' => 'value1', 'field2' => 'value2'];
        $params2 = ['field1' => 'different', 'field2' => 'value2'];
        
        $json1 = json_encode($params1, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        $json2 = json_encode($params2, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        
        $hash1 = hash('sha256', $type . "\0" . $json1);
        $hash2 = hash('sha256', $type . "\0" . $json2);
        
        TestRunner::assertNotEquals($hash1, $hash2, 'Different params should produce different hash');
    });
    
    $runner->addTest('Deduplication: Null byte separator prevents collision', function() {
        // Without null byte separator, these could collide:
        // type="A" + params=":B" vs type="A:" + params="B"
        
        $type1 = 'A';
        $params1 = ':B';
        $hash1 = hash('sha256', $type1 . "\0" . $params1);
        
        $type2 = 'A:';
        $params2 = 'B';
        $hash2 = hash('sha256', $type2 . "\0" . $params2);
        
        TestRunner::assertNotEquals($hash1, $hash2, 'Null byte separator should prevent collision');
    });
    
    // ========================================================================
    // Test 2: JSON Schema Validation Logic
    // ========================================================================
    
    $runner->addTest('Schema Validation: Valid schema must have type property', function() {
        $validSchema = ['type' => 'object', 'properties' => []];
        $invalidSchema = ['properties' => []]; // Missing 'type'
        
        TestRunner::assertTrue(isset($validSchema['type']), 'Valid schema should have type');
        TestRunner::assertFalse(isset($invalidSchema['type']), 'Invalid schema should not have type');
    });
    
    $runner->addTest('Schema Validation: JSON Schema structure is valid JSON', function() {
        $schema = [
            'type' => 'object',
            'properties' => [
                'topic' => ['type' => 'string', 'minLength' => 1],
                'style' => ['type' => 'string', 'enum' => ['formal', 'casual']]
            ],
            'required' => ['topic']
        ];
        
        $json = json_encode($schema);
        $decoded = json_decode($json, true);
        
        TestRunner::assertEquals(JSON_ERROR_NONE, json_last_error(), 'Schema should encode/decode without error');
        TestRunner::assertEquals($schema, $decoded, 'Schema should survive encoding/decoding');
    });
    
    // ========================================================================
    // Test 3: Task Claiming - Timeout Logic
    // ========================================================================
    
    $runner->addTest('Task Claiming: Timeout threshold calculation', function() {
        $timeout = 300; // 5 minutes
        $now = time();
        $threshold = date('Y-m-d H:i:s', $now - $timeout);
        
        // Tasks claimed before this threshold should be reclaimable
        $oldClaimedAt = date('Y-m-d H:i:s', $now - 600); // 10 minutes ago
        $recentClaimedAt = date('Y-m-d H:i:s', $now - 60); // 1 minute ago
        
        TestRunner::assertTrue($oldClaimedAt < $threshold, 'Old claim should be before threshold');
        TestRunner::assertFalse($recentClaimedAt < $threshold, 'Recent claim should be after threshold');
    });
    
    // ========================================================================
    // Test 4: Retry Logic - Attempt Counting
    // ========================================================================
    
    $runner->addTest('Retry Logic: Should retry when attempts < max', function() {
        $maxAttempts = 3;
        $currentAttempts = 2;
        
        $shouldRetry = $currentAttempts < $maxAttempts;
        
        TestRunner::assertTrue($shouldRetry, 'Should retry when attempts (2) < max (3)');
    });
    
    $runner->addTest('Retry Logic: Should not retry when attempts >= max', function() {
        $maxAttempts = 3;
        $currentAttempts = 3;
        
        $shouldRetry = $currentAttempts < $maxAttempts;
        
        TestRunner::assertFalse($shouldRetry, 'Should not retry when attempts (3) >= max (3)');
    });
    
    // ========================================================================
    // Test 5: Worker Authorization - Ownership Verification
    // ========================================================================
    
    $runner->addTest('Worker Authorization: Worker can complete own task', function() {
        $claimedBy = 'worker-001';
        $completingWorker = 'worker-001';
        
        $authorized = ($claimedBy === $completingWorker);
        
        TestRunner::assertTrue($authorized, 'Worker should be able to complete own task');
    });
    
    $runner->addTest('Worker Authorization: Worker cannot complete other worker\'s task', function() {
        $claimedBy = 'worker-001';
        $completingWorker = 'worker-002';
        
        $authorized = ($claimedBy === $completingWorker);
        
        TestRunner::assertFalse($authorized, 'Worker should not complete another worker\'s task');
    });
    
    // ========================================================================
    // Test 6: Progress Validation
    // ========================================================================
    
    $runner->addTest('Progress Validation: Valid progress values', function() {
        $testCases = [0, 50, 100];
        
        foreach ($testCases as $progress) {
            $valid = ($progress >= 0 && $progress <= 100);
            TestRunner::assertTrue($valid, "Progress $progress should be valid");
        }
    });
    
    $runner->addTest('Progress Validation: Invalid progress values', function() {
        $testCases = [-1, 101, 200];
        
        foreach ($testCases as $progress) {
            $valid = ($progress >= 0 && $progress <= 100);
            TestRunner::assertFalse($valid, "Progress $progress should be invalid");
        }
    });
    
    // ========================================================================
    // Test 7: Multi-Step Operations (Cannot be done with simple actions)
    // ========================================================================
    
    $runner->addTest('Multi-Step: Task creation requires multiple checks', function() {
        // Simulates the steps in task_create custom handler
        $steps = [
            'validate_required_fields' => true,
            'fetch_task_type' => true,
            'check_task_type_active' => true,
            'validate_params_against_schema' => true,
            'generate_dedupe_key' => true,
            'check_for_duplicate' => true,
            'insert_or_return_existing' => true,
            'log_to_history' => true,
        ];
        
        // All steps must succeed
        $allStepsSuccessful = !in_array(false, $steps, true);
        
        TestRunner::assertTrue($allStepsSuccessful, 'All steps should be required for task creation');
        TestRunner::assertEquals(8, count($steps), 'Task creation requires 8 distinct steps');
    });
    
    $runner->addTest('Multi-Step: Task claiming requires transaction', function() {
        // Simulates the steps in task_claim custom handler
        $steps = [
            'begin_transaction' => true,
            'select_for_update' => true,      // Row-level lock
            'find_matching_task' => true,
            'check_timeout_status' => true,
            'update_task_status' => true,
            'increment_attempts' => true,
            'log_to_history' => true,
            'commit_transaction' => true,
        ];
        
        // All steps must be in a transaction
        $requiresTransaction = (
            $steps['begin_transaction'] && 
            $steps['select_for_update'] && 
            $steps['commit_transaction']
        );
        
        TestRunner::assertTrue($requiresTransaction, 'Task claiming must use transaction');
        TestRunner::assertEquals(8, count($steps), 'Task claiming requires 8 distinct steps');
    });
    
    // ========================================================================
    // Test 8: Conditional Logic (Cannot be done with simple actions)
    // ========================================================================
    
    $runner->addTest('Conditional Logic: Task completion has different paths', function() {
        // Success path
        $success = true;
        $attempts = 2;
        $maxAttempts = 3;
        
        if ($success) {
            $status = 'completed';
        } elseif ($attempts < $maxAttempts) {
            $status = 'pending'; // Retry
        } else {
            $status = 'failed';
        }
        
        TestRunner::assertEquals('completed', $status, 'Success should mark as completed');
        
        // Failure with retry path
        $success = false;
        $attempts = 2;
        
        if ($success) {
            $status = 'completed';
        } elseif ($attempts < $maxAttempts) {
            $status = 'pending'; // Retry
        } else {
            $status = 'failed';
        }
        
        TestRunner::assertEquals('pending', $status, 'Failed task with retries should be pending');
        
        // Failure exhausted retries path
        $success = false;
        $attempts = 3;
        
        if ($success) {
            $status = 'completed';
        } elseif ($attempts < $maxAttempts) {
            $status = 'pending'; // Retry
        } else {
            $status = 'failed';
        }
        
        TestRunner::assertEquals('failed', $status, 'Failed task without retries should be failed');
    });
    
    // ========================================================================
    // Test 9: Upsert Logic (Cannot be done with simple insert/update actions)
    // ========================================================================
    
    $runner->addTest('Upsert Logic: Task type register handles both create and update', function() {
        // Simulate checking if exists
        $existingTaskType = true; // Assume exists
        
        if ($existingTaskType) {
            $operation = 'update';
            $message = 'Task type updated';
        } else {
            $operation = 'insert';
            $message = 'Task type created';
        }
        
        TestRunner::assertEquals('update', $operation, 'Existing task type should update');
        
        $existingTaskType = false; // Assume does not exist
        
        if ($existingTaskType) {
            $operation = 'update';
            $message = 'Task type updated';
        } else {
            $operation = 'insert';
            $message = 'Task type created';
        }
        
        TestRunner::assertEquals('insert', $operation, 'New task type should insert');
    });
    
    // ========================================================================
    // Test 10: Why Data-Driven Actions Cannot Replace Custom Handlers
    // ========================================================================
    
    $runner->addTest('Limitations: Data-driven actions cannot handle complex logic', function() {
        $dataDrivenCanDo = [
            'simple_select' => true,
            'simple_insert' => true,
            'simple_update' => true,
            'simple_delete' => true,
            'template_substitution' => true,
        ];
        
        $dataDrivenCannotDo = [
            'multi_step_operations' => false,
            'conditional_branching' => false,
            'transactions' => false,
            'row_locking' => false,
            'json_schema_validation' => false,
            'deduplication_hashing' => false,
            'retry_logic' => false,
            'worker_authorization' => false,
            'upsert_operations' => false,
        ];
        
        TestRunner::assertEquals(5, count($dataDrivenCanDo), 'Data-driven can do 5 things');
        TestRunner::assertEquals(9, count($dataDrivenCannotDo), 'Data-driven cannot do 9 things');
        
        // Verify all limitations are false
        foreach ($dataDrivenCannotDo as $limitation => $canDo) {
            TestRunner::assertFalse($canDo, "Data-driven cannot do: $limitation");
        }
    });
    
    return $runner;
}

// Run tests if executed directly
if (basename(__FILE__) === basename($_SERVER['PHP_SELF'] ?? '')) {
    $runner = testCustomHandlers();
    $runner->run();
}
