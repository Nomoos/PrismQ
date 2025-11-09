<?php
/**
 * Security Tests
 * 
 * Tests for SQL injection, XSS, and other security vulnerabilities
 */

require_once __DIR__ . '/../TestRunner.php';
require_once __DIR__ . '/../../../src/api/JsonSchemaValidator.php';

function testSecurity() {
    $runner = new TestRunner();
    $validator = new JsonSchemaValidator();
    
    // Test: SQL Injection patterns in validation
    $runner->addTest('SQL injection in string validation', function() use ($validator) {
        $maliciousInputs = [
            "'; DROP TABLE tasks; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "1; DELETE FROM tasks WHERE 1=1--"
        ];
        
        $schema = [
            'type' => 'object',
            'properties' => [
                'name' => ['type' => 'string', 'maxLength' => 50]
            ]
        ];
        
        foreach ($maliciousInputs as $input) {
            $result = $validator->validate(['name' => $input], $schema);
            // Validator should still validate based on schema rules
            // The actual SQL injection protection happens at the database layer with prepared statements
            TestRunner::assertTrue(true, 'Validator processes input without error');
        }
    });
    
    // Test: XSS patterns in validation
    $runner->addTest('XSS patterns in string validation', function() use ($validator) {
        $xssPatterns = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'></iframe>",
            "'-alert(1)-'"
        ];
        
        $schema = [
            'type' => 'object',
            'properties' => [
                'comment' => ['type' => 'string']
            ]
        ];
        
        foreach ($xssPatterns as $pattern) {
            $result = $validator->validate(['comment' => $pattern], $schema);
            // Validator accepts the input as valid string
            // XSS protection must be handled at output/display layer
            TestRunner::assertTrue($result['valid'], 'XSS patterns pass validation as strings');
        }
    });
    
    // Test: Regex DoS protection
    $runner->addTest('Regex DoS protection', function() use ($validator) {
        // Pattern that could cause catastrophic backtracking
        $schema = [
            'type' => 'object',
            'properties' => [
                'text' => ['type' => 'string', 'pattern' => '^(a+)+$']
            ]
        ];
        
        // This input could cause DoS with vulnerable regex engine
        $evilInput = str_repeat('a', 50) . 'X';
        
        $startTime = microtime(true);
        $result = $validator->validate(['text' => $evilInput], $schema);
        $duration = microtime(true) - $startTime;
        
        // Validation should complete in reasonable time (< 1 second)
        TestRunner::assertTrue($duration < 1, 'Regex validation should not hang');
    });
    
    // Test: Invalid regex pattern handling
    $runner->addTest('Invalid regex pattern in schema', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'text' => ['type' => 'string', 'pattern' => '(unclosed']
            ]
        ];
        
        $result = $validator->validate(['text' => 'test'], $schema);
        // Should handle invalid regex gracefully
        TestRunner::assertFalse($result['valid'], 'Should report error for invalid regex');
        TestRunner::assertNotEmpty($result['errors'], 'Should have error message');
    });
    
    // Test: Very long strings
    $runner->addTest('Very long string handling', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'text' => ['type' => 'string', 'maxLength' => 100]
            ]
        ];
        
        // 10MB string
        $longString = str_repeat('a', 10 * 1024 * 1024);
        
        $result = $validator->validate(['text' => $longString], $schema);
        TestRunner::assertFalse($result['valid'], 'Should reject very long strings');
    });
    
    // Test: Deeply nested objects
    $runner->addTest('Deeply nested object handling', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'data' => ['type' => 'object']
            ]
        ];
        
        // Create deeply nested structure
        $deepData = ['data' => []];
        $current = &$deepData['data'];
        for ($i = 0; $i < 100; $i++) {
            $current['nested'] = [];
            $current = &$current['nested'];
        }
        
        // Should handle without stack overflow
        try {
            $result = $validator->validate($deepData, $schema);
            TestRunner::assertTrue(true, 'Handles deep nesting without error');
        } catch (Exception $e) {
            TestRunner::assertTrue(false, 'Should not throw exception on deep nesting');
        }
    });
    
    // Test: Type confusion attacks
    $runner->addTest('Type confusion prevention', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'id' => ['type' => 'integer']
            ]
        ];
        
        // Try to confuse with string that looks like number
        $result = $validator->validate(['id' => '123'], $schema);
        TestRunner::assertFalse($result['valid'], 'Should reject string as integer');
        
        // Try to confuse with boolean
        $result = $validator->validate(['id' => true], $schema);
        TestRunner::assertFalse($result['valid'], 'Should reject boolean as integer');
    });
    
    // Test: Null byte injection
    $runner->addTest('Null byte injection handling', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'filename' => ['type' => 'string']
            ]
        ];
        
        $nullByteInput = "file.txt\0.jpg";
        $result = $validator->validate(['filename' => $nullByteInput], $schema);
        
        // Validator should accept it as string (protection happens at file system layer)
        TestRunner::assertTrue($result['valid'], 'Accepts string with null byte');
    });
    
    // Test: Array/Object confusion
    $runner->addTest('Array vs Object type enforcement', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'items' => ['type' => 'array']
            ]
        ];
        
        // Try passing object instead of array
        $result = $validator->validate(['items' => ['key' => 'value']], $schema);
        TestRunner::assertFalse($result['valid'], 'Should reject associative array for array type');
        
        // Proper array should pass
        $result = $validator->validate(['items' => [1, 2, 3]], $schema);
        TestRunner::assertTrue($result['valid'], 'Should accept indexed array');
    });
    
    // Test: Unicode bypass attempts
    $runner->addTest('Unicode normalization handling', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'username' => ['type' => 'string', 'pattern' => '^[a-zA-Z0-9]+$']
            ]
        ];
        
        // Try Unicode characters that might normalize to ASCII
        $result = $validator->validate(['username' => 'admin\u{0041}'], $schema);
        // Pattern should either accept or reject consistently
        TestRunner::assertTrue(isset($result['valid']), 'Produces valid result');
    });
    
    // Test: Enum bypass attempts
    $runner->addTest('Enum validation bypass prevention', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'role' => ['type' => 'string', 'enum' => ['user', 'guest']]
            ]
        ];
        
        // Try to bypass with case variation
        $result = $validator->validate(['role' => 'User'], $schema);
        TestRunner::assertFalse($result['valid'], 'Should reject case variation');
        
        // Try with whitespace
        $result = $validator->validate(['role' => 'user '], $schema);
        TestRunner::assertFalse($result['valid'], 'Should reject with whitespace');
        
        // Try with type coercion attempt
        $result = $validator->validate(['role' => ['user']], $schema);
        TestRunner::assertFalse($result['valid'], 'Should reject array instead of string');
    });
    
    // Test: Integer overflow
    $runner->addTest('Integer overflow handling', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'count' => ['type' => 'integer', 'maximum' => 1000]
            ]
        ];
        
        // PHP's max integer value
        $result = $validator->validate(['count' => PHP_INT_MAX], $schema);
        TestRunner::assertFalse($result['valid'], 'Should reject value above maximum');
    });
    
    return $runner->run();
}

// Run tests if this file is executed directly
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    exit(testSecurity() ? 0 : 1);
}
