<?php
/**
 * Unit Tests for JsonSchemaValidator
 */

require_once __DIR__ . '/../TestRunner.php';
require_once __DIR__ . '/../../../src/api/JsonSchemaValidator.php';

function testJsonSchemaValidator() {
    $runner = new TestRunner();
    $validator = new JsonSchemaValidator();
    
    // Test: Valid object with required fields
    $runner->addTest('Valid object with required fields', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'name' => ['type' => 'string']
            ],
            'required' => ['name']
        ];
        
        $result = $validator->validate(['name' => 'test'], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid');
        TestRunner::assertEmpty($result['errors'], 'Should have no errors');
    });
    
    // Test: Missing required field
    $runner->addTest('Missing required field', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'name' => ['type' => 'string']
            ],
            'required' => ['name']
        ];
        
        $result = $validator->validate([], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid');
        TestRunner::assertNotEmpty($result['errors'], 'Should have errors');
    });
    
    // Test: Type mismatch
    $runner->addTest('Type mismatch', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'age' => ['type' => 'integer']
            ]
        ];
        
        $result = $validator->validate(['age' => 'not a number'], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid');
        TestRunner::assertNotEmpty($result['errors'], 'Should have errors');
    });
    
    // Test: String min/max length
    $runner->addTest('String minLength validation', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'name' => ['type' => 'string', 'minLength' => 3]
            ]
        ];
        
        $result = $validator->validate(['name' => 'ab'], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid (too short)');
        
        $result = $validator->validate(['name' => 'abc'], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid (exactly min length)');
    });
    
    $runner->addTest('String maxLength validation', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'name' => ['type' => 'string', 'maxLength' => 5]
            ]
        ];
        
        $result = $validator->validate(['name' => 'toolong'], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid (too long)');
        
        $result = $validator->validate(['name' => 'ok'], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid');
    });
    
    // Test: Number min/max
    $runner->addTest('Number minimum validation', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'age' => ['type' => 'integer', 'minimum' => 18]
            ]
        ];
        
        $result = $validator->validate(['age' => 17], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid (below minimum)');
        
        $result = $validator->validate(['age' => 18], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid');
    });
    
    $runner->addTest('Number maximum validation', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'age' => ['type' => 'integer', 'maximum' => 100]
            ]
        ];
        
        $result = $validator->validate(['age' => 101], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid (above maximum)');
        
        $result = $validator->validate(['age' => 100], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid');
    });
    
    // Test: Pattern matching
    $runner->addTest('Pattern validation', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'email' => ['type' => 'string', 'pattern' => '^[a-z]+@[a-z]+\\.com$']
            ]
        ];
        
        $result = $validator->validate(['email' => 'test@example.com'], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid');
        
        $result = $validator->validate(['email' => 'invalid-email'], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid');
    });
    
    // Test: Enum validation
    $runner->addTest('Enum validation', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'status' => ['type' => 'string', 'enum' => ['pending', 'active', 'completed']]
            ]
        ];
        
        $result = $validator->validate(['status' => 'active'], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid');
        
        $result = $validator->validate(['status' => 'invalid'], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid');
    });
    
    // Test: Array validation
    $runner->addTest('Array items validation', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'tags' => [
                    'type' => 'array',
                    'items' => ['type' => 'string']
                ]
            ]
        ];
        
        $result = $validator->validate(['tags' => ['tag1', 'tag2']], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid');
        
        $result = $validator->validate(['tags' => ['tag1', 123]], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid (wrong item type)');
    });
    
    $runner->addTest('Array minItems/maxItems validation', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'tags' => [
                    'type' => 'array',
                    'minItems' => 2,
                    'maxItems' => 5
                ]
            ]
        ];
        
        $result = $validator->validate(['tags' => ['one']], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid (too few items)');
        
        $result = $validator->validate(['tags' => ['1', '2']], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid');
        
        $result = $validator->validate(['tags' => ['1', '2', '3', '4', '5', '6']], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid (too many items)');
    });
    
    // Test: Additional properties
    $runner->addTest('Additional properties not allowed', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'name' => ['type' => 'string']
            ],
            'additionalProperties' => false
        ];
        
        $result = $validator->validate(['name' => 'test', 'extra' => 'value'], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid (extra property)');
    });
    
    // Test: Nested objects
    $runner->addTest('Nested object validation', function() use ($validator) {
        $schema = [
            'type' => 'object',
            'properties' => [
                'user' => [
                    'type' => 'object',
                    'properties' => [
                        'name' => ['type' => 'string'],
                        'age' => ['type' => 'integer']
                    ],
                    'required' => ['name']
                ]
            ]
        ];
        
        $result = $validator->validate(['user' => ['name' => 'John', 'age' => 30]], $schema);
        TestRunner::assertTrue($result['valid'], 'Should be valid');
        
        $result = $validator->validate(['user' => ['age' => 30]], $schema);
        TestRunner::assertFalse($result['valid'], 'Should be invalid (missing required nested field)');
    });
    
    // Test: Type detection
    $runner->addTest('Type detection for various values', function() use ($validator) {
        $schema = ['type' => 'string'];
        TestRunner::assertTrue($validator->validate('text', $schema)['valid']);
        
        $schema = ['type' => 'integer'];
        TestRunner::assertTrue($validator->validate(42, $schema)['valid']);
        
        $schema = ['type' => 'number'];
        TestRunner::assertTrue($validator->validate(3.14, $schema)['valid']);
        
        $schema = ['type' => 'boolean'];
        TestRunner::assertTrue($validator->validate(true, $schema)['valid']);
        
        $schema = ['type' => 'null'];
        TestRunner::assertTrue($validator->validate(null, $schema)['valid']);
        
        $schema = ['type' => 'array'];
        TestRunner::assertTrue($validator->validate([1, 2, 3], $schema)['valid']);
    });
    
    return $runner->run();
}

// Run tests if this file is executed directly
if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {
    exit(testJsonSchemaValidator() ? 0 : 1);
}
