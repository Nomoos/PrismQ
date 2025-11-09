# ISSUE-TASKMANAGER-007: PHP Code Refactoring and Best Practices

## Status
🟢 IN PROGRESS

## Component
Backend/TaskManager/api

## Type
Refactoring / Code Quality

## Priority
Medium

## Assigned To
Worker03 - PHP Backend Expert

## Description
Review and refactor PHP codebase to ensure best practices, proper error handling, and maintainable code structure.

## Problem Statement
While the initial implementation is functional, there are opportunities to improve:
- Code organization and structure
- Error handling consistency
- PSR-12 coding standards compliance
- Type hints and return types
- Dependency injection
- Code reusability

## Solution
Refactor PHP code to follow best practices:
1. Apply PSR-12 coding standards
2. Add proper type hints and return types
3. Improve error handling
4. Extract reusable components
5. Add code comments where needed
6. Implement dependency injection
7. Create helper functions/classes

## Acceptance Criteria
- [ ] All classes follow PSR-12 standards
- [ ] Type hints added to all method parameters
- [ ] Return types declared for all methods
- [ ] Consistent error handling across codebase
- [ ] Code comments for complex logic
- [ ] No code duplication
- [ ] Dependency injection implemented where appropriate
- [ ] Helper classes created for common operations
- [ ] Code review by Worker10 passed

## Dependencies
- ISSUE-TASKMANAGER-002 (API endpoints) ✅
- ISSUE-TASKMANAGER-003 (Validation) ✅

## Related Issues
- ISSUE-TASKMANAGER-005 (Testing)
- ISSUE-TASKMANAGER-009 (Performance)
- ISSUE-TASKMANAGER-010 (Review)

## Refactoring Areas

### 1. Type Safety
**Before**:
```php
public function validate($data, $schema) {
    // ...
}
```

**After**:
```php
public function validate(array $data, array $schema): array {
    // ...
}
```

### 2. Error Handling
**Before**:
```php
try {
    // code
} catch (Exception $e) {
    error_log($e->getMessage());
    ApiResponse::error('Internal server error', 500);
}
```

**After**:
```php
try {
    // code
} catch (PDOException $e) {
    $this->logError($e);
    throw new DatabaseException('Database operation failed', 0, $e);
} catch (ValidationException $e) {
    $this->logError($e);
    ApiResponse::error($e->getMessage(), 400);
}
```

### 3. Dependency Injection
**Before**:
```php
class TaskController {
    private $db;
    
    public function __construct() {
        $this->db = Database::getInstance()->getConnection();
    }
}
```

**After**:
```php
class TaskController {
    private PDO $db;
    private JsonSchemaValidator $validator;
    
    public function __construct(PDO $db, JsonSchemaValidator $validator) {
        $this->db = $db;
        $this->validator = $validator;
    }
}
```

### 4. Extract Common Logic
Create helper classes:
- `RequestValidator`: Validate and sanitize requests
- `ResponseFormatter`: Format API responses
- `QueryBuilder`: Build common SQL queries
- `ErrorHandler`: Centralized error handling

### 5. Code Organization
```
api/
├── Controllers/
│   ├── TaskTypeController.php
│   └── TaskController.php
├── Helpers/
│   ├── RequestValidator.php
│   ├── ResponseFormatter.php
│   └── QueryBuilder.php
├── Exceptions/
│   ├── DatabaseException.php
│   ├── ValidationException.php
│   └── NotFoundException.php
├── Validators/
│   └── JsonSchemaValidator.php
└── index.php
```

## Specific Improvements

### TaskController.php
- [ ] Add type hints to all methods
- [ ] Extract SQL queries to QueryBuilder
- [ ] Improve transaction handling
- [ ] Add method-level comments
- [ ] Split long methods (> 50 lines)

### TaskTypeController.php
- [ ] Add type hints to all methods
- [ ] Extract validation logic
- [ ] Improve error messages
- [ ] Add method-level comments

### JsonSchemaValidator.php
- [ ] Add return type hints
- [ ] Extract validation rules to separate methods
- [ ] Improve error message generation
- [ ] Add support for additional schema features

### Database.php
- [ ] Add connection pooling
- [ ] Improve error handling
- [ ] Add query logging (optional)
- [ ] Add transaction helpers

## PSR-12 Compliance Checklist
- [ ] Consistent indentation (4 spaces)
- [ ] Line length < 120 characters
- [ ] Proper namespace usage
- [ ] Class names in PascalCase
- [ ] Method names in camelCase
- [ ] Constants in UPPER_SNAKE_CASE
- [ ] Opening brace on new line for classes
- [ ] Opening brace on same line for methods
- [ ] No trailing whitespace

## Documentation Improvements
- [ ] Add PHPDoc blocks to all classes
- [ ] Add PHPDoc blocks to all methods
- [ ] Document parameters and return types
- [ ] Add @throws annotations
- [ ] Add usage examples in comments

## Testing
- [ ] Refactored code passes all existing tests
- [ ] New helper classes have unit tests
- [ ] No regression issues
- [ ] Performance not degraded

## Estimated Effort
- Type safety improvements: 2 days
- Error handling refactoring: 1 day
- Dependency injection: 1 day
- Extract common logic: 2 days
- PSR-12 compliance: 1 day
- Documentation: 1 day
- Testing: 1 day
- **Total: 9 days**

## Success Criteria
✅ All code follows PSR-12 standards  
✅ Type hints on all methods  
✅ No code duplication  
✅ Consistent error handling  
✅ Tests pass after refactoring  
✅ Code review by Worker10 passed  
✅ No performance regression
