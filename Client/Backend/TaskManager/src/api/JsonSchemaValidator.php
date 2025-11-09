<?php
/**
 * Simple JSON Schema Validator
 * 
 * Basic JSON Schema validation for task parameters.
 * Supports common validation rules without external dependencies.
 */

class JsonSchemaValidator {
    
    /**
     * Validate data against JSON schema
     */
    public function validate($data, $schema) {
        $errors = [];
        $this->validateValue($data, $schema, '', $errors);
        
        return [
            'valid' => empty($errors),
            'errors' => $errors
        ];
    }
    
    /**
     * Validate a value against schema rules
     */
    private function validateValue($value, $schema, $path, &$errors) {
        // Check type
        if (isset($schema['type'])) {
            $expectedType = $schema['type'];
            $actualType = $this->getJsonType($value);
            
            if ($actualType !== $expectedType) {
                $errors[] = "Type mismatch at $path: expected $expectedType, got $actualType";
                return; // Stop further validation if type is wrong
            }
        }
        
        // Check required properties for objects
        if (isset($schema['required']) && is_array($value)) {
            foreach ($schema['required'] as $requiredKey) {
                if (!isset($value[$requiredKey])) {
                    $errors[] = "Missing required property: $path.$requiredKey";
                }
            }
        }
        
        // Validate object properties
        if (isset($schema['properties']) && is_array($value)) {
            foreach ($value as $key => $val) {
                $propPath = $path ? "$path.$key" : $key;
                
                if (isset($schema['properties'][$key])) {
                    $this->validateValue($val, $schema['properties'][$key], $propPath, $errors);
                } elseif (isset($schema['additionalProperties']) && $schema['additionalProperties'] === false) {
                    $errors[] = "Additional property not allowed: $propPath";
                }
            }
        }
        
        // Validate array items
        if (isset($schema['items']) && is_array($value)) {
            foreach ($value as $index => $item) {
                $itemPath = "$path[$index]";
                $this->validateValue($item, $schema['items'], $itemPath, $errors);
            }
        }
        
        // String validations
        if ($actualType === 'string') {
            if (isset($schema['minLength']) && strlen($value) < $schema['minLength']) {
                $errors[] = "String too short at $path: minimum length is {$schema['minLength']}";
            }
            if (isset($schema['maxLength']) && strlen($value) > $schema['maxLength']) {
                $errors[] = "String too long at $path: maximum length is {$schema['maxLength']}";
            }
            if (isset($schema['pattern'])) {
                // Use a delimiter that's unlikely to be in the pattern (# instead of /)
                $pattern = '#' . $schema['pattern'] . '#';
                
                // Check for regex compilation errors first
                $result = @preg_match($pattern, $value);
                if ($result === false) {
                    // Invalid regex pattern in schema
                    $errors[] = "Invalid regex pattern in schema at $path";
                } elseif ($result === 0) {
                    // Valid regex but value doesn't match
                    $errors[] = "String does not match pattern at $path";
                }
            }
        }
        
        // Number validations
        if ($actualType === 'number' || $actualType === 'integer') {
            if (isset($schema['minimum']) && $value < $schema['minimum']) {
                $errors[] = "Number too small at $path: minimum is {$schema['minimum']}";
            }
            if (isset($schema['maximum']) && $value > $schema['maximum']) {
                $errors[] = "Number too large at $path: maximum is {$schema['maximum']}";
            }
        }
        
        // Array validations
        if ($actualType === 'array') {
            if (isset($schema['minItems']) && count($value) < $schema['minItems']) {
                $errors[] = "Array too short at $path: minimum items is {$schema['minItems']}";
            }
            if (isset($schema['maxItems']) && count($value) > $schema['maxItems']) {
                $errors[] = "Array too long at $path: maximum items is {$schema['maxItems']}";
            }
        }
        
        // Enum validation
        if (isset($schema['enum']) && !in_array($value, $schema['enum'], true)) {
            $enumStr = implode(', ', $schema['enum']);
            $errors[] = "Value at $path must be one of: $enumStr";
        }
    }
    
    /**
     * Get JSON type of a value
     */
    private function getJsonType($value) {
        if (is_null($value)) {
            return 'null';
        }
        if (is_bool($value)) {
            return 'boolean';
        }
        if (is_int($value)) {
            return 'integer';
        }
        if (is_float($value)) {
            return 'number';
        }
        if (is_string($value)) {
            return 'string';
        }
        if (is_array($value)) {
            // Check if it's an associative array (object) or indexed array
            if (empty($value) || array_keys($value) === range(0, count($value) - 1)) {
                return 'array';
            } else {
                return 'object';
            }
        }
        return 'unknown';
    }
}
