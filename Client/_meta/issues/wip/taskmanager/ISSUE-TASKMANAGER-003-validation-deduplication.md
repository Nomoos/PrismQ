# ISSUE-TASKMANAGER-003: Validation and Deduplication

## Status
🟢 IN PROGRESS

## Component
Backend/TaskManager/api

## Type
Feature

## Priority
High

## Description
Implement JSON Schema validation for task parameters and SHA-256 hash-based deduplication to prevent duplicate task creation.

## Problem Statement
Tasks must be validated before creation to ensure parameters match expected schema. Additionally, identical tasks (same type + same parameters) should not create duplicates in the system. This requires:
- JSON Schema validation without external dependencies (PHP native)
- Consistent hash generation for deduplication
- Handling of edge cases (parameter ordering, encoding)

## Solution
**JSON Schema Validator**:
- Implement basic JSON Schema validation in pure PHP
- Support common validation rules: type, required, properties, enum, min/max
- Return detailed validation errors
- No external dependencies (compatible with shared hosting)

**Deduplication**:
- Generate SHA-256 hash from `type + params_json`
- Store as `dedupe_key` with unique constraint
- Return existing task if duplicate detected
- Handle JSON encoding consistently (unescaped Unicode, unescaped slashes)

## Acceptance Criteria
- [x] JsonSchemaValidator class implemented
- [x] Validation supports common JSON Schema features:
  - [x] Type checking (string, number, integer, boolean, object, array, null)
  - [x] Required properties
  - [x] Object properties and additionalProperties
  - [x] Array items validation
  - [x] String: minLength, maxLength, pattern
  - [x] Number: minimum, maximum
  - [x] Array: minItems, maxItems
  - [x] Enum values
- [x] Detailed error messages with field paths
- [x] Deduplication using SHA-256 hash
- [x] Consistent JSON encoding for hash generation
- [x] Duplicate detection returns existing task
- [x] Integration with task creation endpoint

## Dependencies
- ISSUE-TASKMANAGER-001 (Database schema) ✅
- ISSUE-TASKMANAGER-002 (API endpoints) ✅

## Related Issues
- ISSUE-TASKMANAGER-004 (Documentation)

## Implementation Details

### JSON Schema Validation

**Supported Features**:
```php
// Type validation
"type": "string|number|integer|boolean|object|array|null"

// Required properties (for objects)
"required": ["field1", "field2"]

// Object properties
"properties": {
  "field1": { "type": "string" },
  "field2": { "type": "number" }
}

// Additional properties control
"additionalProperties": false

// Array items
"items": { "type": "string" }

// String constraints
"minLength": 1,
"maxLength": 100,
"pattern": "^[A-Za-z]+$"

// Number constraints
"minimum": 0,
"maximum": 100

// Array constraints
"minItems": 1,
"maxItems": 10

// Enum validation
"enum": ["value1", "value2", "value3"]
```

**Error Format**:
```json
{
  "valid": false,
  "errors": [
    "Type mismatch at params.age: expected integer, got string",
    "Missing required property: params.email",
    "String too short at params.name: minimum length is 1"
  ]
}
```

### Deduplication

**Hash Generation**:
```php
$params_json = json_encode($params, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
$dedupe_key = hash('sha256', $type_name . ':' . $params_json);
```

**Deduplication Flow**:
1. Task creation receives type + params
2. Generate dedupe_key hash
3. Query database for existing dedupe_key
4. If exists: Return existing task ID and status
5. If not: Create new task with dedupe_key

**Database Constraint**:
```sql
UNIQUE KEY unique_dedupe (dedupe_key)
```

### Edge Cases

**Parameter Ordering**:
Problem: `{"a":1,"b":2}` vs `{"b":2,"a":1}` create different hashes
Solution: Accept this behavior - parameters should be sent consistently

**Encoding**:
Problem: Different JSON encoding can create different hashes
Solution: Use consistent flags: `JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES`

**Type Coercion**:
Problem: `"1"` vs `1` are different but might be semantically same
Solution: Schema validation enforces type correctness upfront

## Testing

### Validation Testing
```bash
# Test valid parameters
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"Test.Schema","params":{"name":"John","age":30}}'
# Expected: 201 Created

# Test missing required field
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"Test.Schema","params":{"name":"John"}}'
# Expected: 400 Bad Request with validation errors

# Test type mismatch
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"Test.Schema","params":{"name":"John","age":"thirty"}}'
# Expected: 400 Bad Request with type error

# Test enum validation
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"Test.Schema","params":{"status":"invalid"}}'
# Expected: 400 Bad Request with enum error
```

### Deduplication Testing
```bash
# Create first task
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"Test.Dedupe","params":{"msg":"Hello"}}'
# Expected: 201 Created, returns task ID 1

# Create duplicate task
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"Test.Dedupe","params":{"msg":"Hello"}}'
# Expected: 200 OK, returns task ID 1, deduplicated=true

# Create similar but different task
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"type":"Test.Dedupe","params":{"msg":"World"}}'
# Expected: 201 Created, returns task ID 2
```

### Schema Examples for Testing

**Simple Schema**:
```json
{
  "name": "Test.Simple",
  "version": "1.0.0",
  "param_schema": {
    "type": "object",
    "properties": {
      "message": {"type": "string", "minLength": 1}
    },
    "required": ["message"]
  }
}
```

**Complex Schema**:
```json
{
  "name": "Test.Complex",
  "version": "1.0.0",
  "param_schema": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "minLength": 1,
        "maxLength": 100
      },
      "age": {
        "type": "integer",
        "minimum": 0,
        "maximum": 150
      },
      "email": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
      },
      "tags": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "maxItems": 10
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"]
      }
    },
    "required": ["name", "email", "priority"]
  }
}
```

## Files Created
- `/Backend/TaskManager/api/JsonSchemaValidator.php`

## Files Modified
- `/Backend/TaskManager/api/TaskController.php` - Integrated validation and deduplication

## Notes
- JSON Schema validation is basic but sufficient for most use cases
- For advanced validation, consider integrating external library like `justinrainbow/json-schema`
- Hash collisions are theoretically possible with SHA-256 but practically impossible
- Deduplication works at creation time only - parameter changes don't update existing tasks
- Parameter ordering matters for deduplication - document this in API guide
- Schema validation can be disabled via config for performance if needed

## Limitations
- JSON Schema validator doesn't support all JSON Schema features
- Not supported: $ref, allOf, anyOf, oneOf, dependencies, format
- These could be added if needed for specific use cases
- For full JSON Schema support, would need external library

## Performance Considerations
- Schema validation adds ~10-50ms per task creation (acceptable)
- Hash generation is very fast (<1ms)
- Database unique constraint check is indexed and fast
- Consider caching parsed schemas if same type used frequently
- Validation can be disabled in config if performance critical

## Security Considerations
- Validation prevents malformed data in database
- Deduplication prevents DoS via massive duplicate submissions
- Hash algorithm (SHA-256) is cryptographically secure
- No risk of hash collision in practical use
- Schema injection not possible - schemas stored as JSON text
