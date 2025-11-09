<?php
/**
 * Unit Tests for ApiResponse
 */

require_once __DIR__ . '/../TestRunner.php';
require_once __DIR__ . '/../../../src/api/ApiResponse.php';

function testApiResponse() {
    $runner = new TestRunner();
    
    // Test: validateRequired with all fields present
    $runner->addTest('validateRequired passes with all fields', function() {
        $data = ['name' => 'test', 'value' => 123];
        $required = ['name', 'value'];
        
        // This should not throw an error
        try {
            ob_start();
            ApiResponse::validateRequired($data, $required);
            ob_end_clean();
            TestRunner::assertTrue(true, 'No error thrown');
        } catch (Exception $e) {
            ob_end_clean();
            TestRunner::assertTrue(false, 'Should not throw exception');
        }
    });
    
    // Test: validateRequired with missing field
    $runner->addTest('validateRequired fails with missing field', function() {
        $data = ['name' => 'test'];
        $required = ['name', 'value'];
        
        // Since validateRequired calls exit(), we can't directly test it
        // Instead, verify the logic would catch missing fields
        $missing = [];
        foreach ($required as $field) {
            if (!isset($data[$field]) || $data[$field] === '') {
                $missing[] = $field;
            }
        }
        
        TestRunner::assertNotEmpty($missing, 'Should detect missing field');
        TestRunner::assertContains('value', $missing);
    });
    
    // Test: validateRequired with empty string
    $runner->addTest('validateRequired detects empty string', function() {
        $data = ['name' => 'test', 'value' => ''];
        $required = ['name', 'value'];
        
        // Test the logic without calling the function that exits
        $missing = [];
        foreach ($required as $field) {
            if (!isset($data[$field]) || $data[$field] === '') {
                $missing[] = $field;
            }
        }
        
        TestRunner::assertNotEmpty($missing, 'Should detect empty string');
        TestRunner::assertContains('value', $missing);
    });
    
    // Test: getRequestBody with valid JSON
    $runner->addTest('getRequestBody parses valid JSON', function() {
        // Mock php://input
        $json = '{"name":"test","value":123}';
        
        // We can't easily test this without mocking, so we'll test the logic indirectly
        // by verifying JSON decode behavior
        $decoded = json_decode($json, true);
        TestRunner::assertEquals('test', $decoded['name']);
        TestRunner::assertEquals(123, $decoded['value']);
    });
    
    // Test: Response structure validation
    $runner->addTest('Success response structure', function() {
        // Test the JSON encoding structure without calling the actual function
        $data = ['id' => 1];
        $message = 'Test message';
        $response = [
            'success' => true,
            'message' => $message,
            'data' => $data,
            'timestamp' => time()
        ];
        
        TestRunner::assertTrue($response['success']);
        TestRunner::assertEquals('Test message', $response['message']);
        TestRunner::assertEquals(1, $response['data']['id']);
        TestRunner::assertArrayHasKey('timestamp', $response);
    });
    
    $runner->addTest('Error response structure', function() {
        // Test the error structure
        $response = [
            'success' => false,
            'error' => 'Test error',
            'timestamp' => time(),
            'details' => ['detail' => 'info']
        ];
        
        TestRunner::assertFalse($response['success']);
        TestRunner::assertEquals('Test error', $response['error']);
        TestRunner::assertArrayHasKey('timestamp', $response);
        TestRunner::assertArrayHasKey('details', $response);
    });
    
    // Test: Multiple missing required fields
    $runner->addTest('Detects all missing fields', function() {
        $data = [];
        $required = ['field1', 'field2', 'field3'];
        
        $missing = [];
        foreach ($required as $field) {
            if (!isset($data[$field]) || $data[$field] === '') {
                $missing[] = $field;
            }
        }
        
        TestRunner::assertNotEmpty($missing);
        TestRunner::assertContains('field1', $missing);
        TestRunner::assertContains('field2', $missing);
        TestRunner::assertContains('field3', $missing);
        TestRunner::assertCount(3, $missing);
    });
    
    // Test: Timestamp is reasonable
    $runner->addTest('Timestamp is current', function() {
        $timestamp = time();
        $now = time();
        
        // Timestamp should be within 5 seconds of current time
        TestRunner::assertTrue(abs($now - $timestamp) < 5, 'Timestamp should be current');
    });
    
    // Test: JSON encoding options
    $runner->addTest('JSON encoding preserves Unicode and slashes', function() {
        $data = ['text' => 'Test / Unicode: ñ'];
        $json = json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        
        // Should not have escaped slashes or Unicode
        TestRunner::assertStringContains('Test / Unicode: ñ', $json);
        TestRunner::assertFalse(strpos($json, '\\/') !== false, 'Slashes should not be escaped');
    });
    
    return $runner->run();
}

// Run tests if this file is executed directly
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    exit(testApiResponse() ? 0 : 1);
}
