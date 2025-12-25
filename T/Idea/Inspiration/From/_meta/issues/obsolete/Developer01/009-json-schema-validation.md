# Issue #009: JSON Schema Validation Enhancement

**⚠️ OBSOLETE - PHP API NOT BEING IMPLEMENTED ⚠️**

**Status**: ❌ NOT APPLICABLE  
**Reason**: External TaskManager API already implements JSON schema validation  
**Alternative**: Python client (Issue #008) will send data that conforms to schemas

---

## ⚠️ Issue Superseded

This issue was for implementing **PHP API backend JSON validation**. The external API already validates schemas. Python client will prepare data correctly.

---

## Original (Not Implemented) Overview

## Overview

Enhance JSON Schema validation with comprehensive error messages, schema caching for performance, and support for common validation patterns used in PrismQ modules.

---

## Business Context

Task types across different modules have varying parameter requirements:
- **YouTube**: Video IDs, channel IDs, search queries
- **Reddit**: Subreddits, post IDs, OAuth tokens
- **Audio**: Track IDs, artist names, metadata filters

Enhanced validation ensures:
- Clear error messages for developers
- Fast validation (<10ms) via caching
- Support for complex nested schemas
- Custom validation rules

**Impact**: Better validation reduces errors and improves developer experience.

---

## Implementation Requirements

### Enhanced Validator (src/Services/JsonSchemaValidator.php)

```php
<?php
namespace TaskManager\Services;

class JsonSchemaValidator {
    private array $schemaCache = [];
    
    /**
     * Validate data against JSON Schema (enhanced)
     */
    public function validate(array $data, array $schema): ValidationResult {
        $errors = [];
        $warnings = [];
        
        // Cache compiled schema for performance
        $schemaCacheKey = md5(json_encode($schema));
        if (!isset($this->schemaCache[$schemaCacheKey])) {
            $this->schemaCache[$schemaCacheKey] = $this->compileSchema($schema);
        }
        
        $compiledSchema = $this->schemaCache[$schemaCacheKey];
        
        // Perform validation
        $this->validateType($data, $compiledSchema, '', $errors, $warnings);
        
        return new ValidationResult($errors, $warnings);
    }
    
    /**
     * Validate type
     */
    private function validateType(
        $data,
        array $schema,
        string $path,
        array &$errors,
        array &$warnings
    ): void {
        // Type validation
        $actualType = $this->getType($data);
        $expectedType = $schema['type'] ?? 'any';
        
        if ($expectedType !== 'any' && $actualType !== $expectedType) {
            $errors[] = "{$path}: Expected type '{$expectedType}', got '{$actualType}'";
            return;
        }
        
        // Object validation
        if ($expectedType === 'object' && is_array($data)) {
            $this->validateObject($data, $schema, $path, $errors, $warnings);
        }
        
        // Array validation
        if ($expectedType === 'array' && is_array($data)) {
            $this->validateArray($data, $schema, $path, $errors, $warnings);
        }
        
        // String validation
        if ($expectedType === 'string') {
            $this->validateString($data, $schema, $path, $errors, $warnings);
        }
        
        // Number validation
        if (in_array($expectedType, ['number', 'integer'])) {
            $this->validateNumber($data, $schema, $path, $errors, $warnings);
        }
    }
    
    /**
     * Validate object properties
     */
    private function validateObject(
        array $data,
        array $schema,
        string $path,
        array &$errors,
        array &$warnings
    ): void {
        // Required fields
        if (isset($schema['required'])) {
            foreach ($schema['required'] as $field) {
                if (!isset($data[$field])) {
                    $errors[] = "{$path}.{$field}: Required field missing";
                }
            }
        }
        
        // Validate each property
        if (isset($schema['properties'])) {
            foreach ($data as $key => $value) {
                if (isset($schema['properties'][$key])) {
                    $newPath = $path ? "{$path}.{$key}" : $key;
                    $this->validateType(
                        $value,
                        $schema['properties'][$key],
                        $newPath,
                        $errors,
                        $warnings
                    );
                } elseif ($schema['additionalProperties'] ?? true) {
                    // Allow additional properties
                } else {
                    $warnings[] = "{$path}.{$key}: Unexpected property";
                }
            }
        }
    }
    
    /**
     * Validate string constraints
     */
    private function validateString(
        string $data,
        array $schema,
        string $path,
        array &$errors,
        array &$warnings
    ): void {
        // Pattern validation
        if (isset($schema['pattern'])) {
            if (!preg_match("/{$schema['pattern']}/", $data)) {
                $errors[] = "{$path}: Does not match pattern '{$schema['pattern']}'";
            }
        }
        
        // Enum validation
        if (isset($schema['enum'])) {
            if (!in_array($data, $schema['enum'])) {
                $allowed = implode(', ', $schema['enum']);
                $errors[] = "{$path}: Must be one of: {$allowed}";
            }
        }
        
        // Length validation
        if (isset($schema['minLength']) && strlen($data) < $schema['minLength']) {
            $errors[] = "{$path}: String too short (min: {$schema['minLength']})";
        }
        
        if (isset($schema['maxLength']) && strlen($data) > $schema['maxLength']) {
            $errors[] = "{$path}: String too long (max: {$schema['maxLength']})";
        }
        
        // Format validation
        if (isset($schema['format'])) {
            $this->validateFormat($data, $schema['format'], $path, $errors);
        }
    }
    
    /**
     * Validate common formats
     */
    private function validateFormat(
        string $data,
        string $format,
        string $path,
        array &$errors
    ): void {
        switch ($format) {
            case 'email':
                if (!filter_var($data, FILTER_VALIDATE_EMAIL)) {
                    $errors[] = "{$path}: Invalid email format";
                }
                break;
            
            case 'url':
                if (!filter_var($data, FILTER_VALIDATE_URL)) {
                    $errors[] = "{$path}: Invalid URL format";
                }
                break;
            
            case 'date-time':
                if (!strtotime($data)) {
                    $errors[] = "{$path}: Invalid date-time format";
                }
                break;
            
            case 'youtube-video-id':
                if (!preg_match('/^[A-Za-z0-9_-]{11}$/', $data)) {
                    $errors[] = "{$path}: Invalid YouTube video ID";
                }
                break;
            
            case 'reddit-subreddit':
                if (!preg_match('/^[A-Za-z0-9_]{3,21}$/', $data)) {
                    $errors[] = "{$path}: Invalid subreddit name";
                }
                break;
        }
    }
    
    /**
     * Compile schema for faster validation
     */
    private function compileSchema(array $schema): array {
        // Pre-compile regex patterns
        if (isset($schema['pattern'])) {
            $schema['_compiled_pattern'] = "/{$schema['pattern']}/";
        }
        
        // Recursively compile nested schemas
        if (isset($schema['properties'])) {
            foreach ($schema['properties'] as $key => $prop) {
                $schema['properties'][$key] = $this->compileSchema($prop);
            }
        }
        
        return $schema;
    }
    
    private function getType($value): string {
        if (is_array($value)) {
            return array_keys($value) === range(0, count($value) - 1) ? 'array' : 'object';
        }
        if (is_bool($value)) return 'boolean';
        if (is_int($value)) return 'integer';
        if (is_float($value)) return 'number';
        if (is_string($value)) return 'string';
        if (is_null($value)) return 'null';
        return 'unknown';
    }
}

/**
 * Validation result with errors and warnings
 */
class ValidationResult {
    public array $errors;
    public array $warnings;
    
    public function __construct(array $errors, array $warnings = []) {
        $this->errors = $errors;
        $this->warnings = $warnings;
    }
    
    public function isValid(): bool {
        return empty($this->errors);
    }
    
    public function hasWarnings(): bool {
        return !empty($this->warnings);
    }
}
```

---

## Common Schema Patterns

### YouTube Video Task Schema

```json
{
  "type": "object",
  "properties": {
    "video_id": {
      "type": "string",
      "pattern": "^[A-Za-z0-9_-]{11}$",
      "description": "YouTube video ID"
    },
    "quality": {
      "type": "string",
      "enum": ["hd", "sd", "4k"],
      "default": "hd"
    },
    "extract_metadata": {
      "type": "boolean",
      "default": true
    }
  },
  "required": ["video_id"]
}
```

### Reddit Post Task Schema

```json
{
  "type": "object",
  "properties": {
    "subreddit": {
      "type": "string",
      "pattern": "^[A-Za-z0-9_]{3,21}$"
    },
    "post_id": {
      "type": "string",
      "pattern": "^[A-Za-z0-9]{6,7}$"
    },
    "include_comments": {
      "type": "boolean",
      "default": false
    }
  },
  "required": ["subreddit", "post_id"]
}
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] Enhanced validation with clear error messages
- [ ] Schema caching for performance
- [ ] Support for custom formats (youtube-video-id, etc.)
- [ ] Support for nested object validation
- [ ] Support for array validation
- [ ] Support for string constraints (minLength, maxLength, pattern)
- [ ] Support for number constraints (min, max)
- [ ] Warnings for unexpected properties

### Non-Functional Requirements
- [ ] Validation completes in <10ms (p95)
- [ ] Schema compilation caches patterns
- [ ] Memory efficient (limit cache size)

### Testing
- [ ] Unit tests for all validation types
- [ ] Performance tests with caching
- [ ] Test custom formats

### Documentation
- [ ] Common schema patterns documented
- [ ] Custom format list documented

---

## Definition of Done

- [ ] Enhanced validator implemented
- [ ] Schema caching working
- [ ] Custom formats supported
- [ ] Unit tests passing (>80% coverage)
- [ ] Performance targets met
- [ ] Code reviewed by Developer10
- [ ] Documentation complete

---

**Status**: Ready for Implementation  
**Estimated Timeline**: 1-2 days  
**Assignee**: Developer02  
**Reviewer**: Developer10
