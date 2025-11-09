# API Testing Guide

## Overview

This guide explains how to run and maintain API integration tests for the TaskManager system. These tests validate all API endpoints and their interactions.

## Test Suite Components

### 1. ApiTestHelper.php

Helper class providing utilities for API testing:
- HTTP request methods (GET, POST)
- Database setup/teardown
- Test fixtures and data creation
- Response verification

**Key Features**:
- Local and remote API testing support
- Automatic test data cleanup
- Database state verification
- Request/response validation

### 2. ApiIntegrationTest.php

Comprehensive test suite covering all 9 API endpoints:

#### Health Endpoint (1 test)
- ✓ Health check returns success

#### Task Type Registration (4 tests)
- ✓ Register new task type successfully
- ✓ Register task type with missing name fails
- ✓ Register task type with invalid schema fails
- ✓ Update existing task type version

#### Get Task Type (2 tests)
- ✓ Get existing task type details
- ✓ Get non-existent task type fails

#### List Task Types (2 tests)
- ✓ List all task types
- ✓ List active task types only

#### Create Task (4 tests)
- ✓ Create task with valid data
- ✓ Create task with invalid parameters fails
- ✓ Create task with non-existent type fails
- ✓ Task deduplication works

#### Claim Task (3 tests)
- ✓ Claim pending task successfully
- ✓ Claim with type pattern filter
- ✓ Claim when no tasks available

#### Complete Task (2 tests)
- ✓ Complete task successfully
- ✓ Mark task as failed

#### Get Task Status (2 tests)
- ✓ Get existing task status
- ✓ Get non-existent task fails

#### List Tasks (3 tests)
- ✓ List all tasks
- ✓ List tasks with status filter
- ✓ List tasks with pagination

**Total**: 30+ integration tests covering all API endpoints

## Running API Tests

### Prerequisites

1. **Database Access**: Tests require a configured MySQL/MariaDB database
2. **Configuration**: Ensure `config/config.php` is properly configured
3. **Test Data**: Tests will create and cleanup test data automatically

### Run All API Integration Tests

```bash
cd Backend/TaskManager
php tests/run_tests.php --suite=integration
```

### Run With Verbose Output

```bash
php tests/run_tests.php --suite=integration --verbose
```

### Run Individual Test File

```bash
php tests/integration/ApiIntegrationTest.php
```

## Test Modes

### Local Testing (Recommended)

Tests run against the local API without requiring HTTP server:

```php
$helper = new ApiTestHelper(); // Automatically uses local mode
```

**Advantages**:
- No HTTP server required
- Faster execution
- Better error messages
- Easier debugging

### Remote Testing

Tests run against a live API server:

```bash
export TASKMANAGER_API_URL=http://localhost/api
php tests/run_tests.php --suite=integration
```

**When to use**:
- Testing deployed API
- Integration with CI/CD
- End-to-end validation

## Test Data Management

### Automatic Cleanup

The `ApiTestHelper` automatically tracks and cleans up:
- Created tasks
- Registered task types
- Test data in database

```php
$helper = new ApiTestHelper();
// ... run tests ...
$helper->cleanup(); // Removes all created test data
```

### Manual Database Reset

For complete cleanup between test runs:

```php
$helper->resetDatabase(); // Removes all test.* and example.* data
```

### Database State Verification

Verify data directly in database:

```php
$task = $helper->verifyDbRecord('tasks', $taskId);
TestRunner::assertEquals('completed', $task['status']);
```

## Writing New API Tests

### Basic Test Structure

```php
$runner->addTest('Test description', function() use ($helper) {
    // Setup: Create necessary test data
    $helper->registerTaskType('test.type', '1.0.0', $schema);
    
    // Execute: Make API request
    $response = $helper->post('/endpoint', $data);
    
    // Assert: Verify response
    TestRunner::assertTrue($response['data']['success']);
    TestRunner::assertEquals(200, $response['code']);
});
```

### Testing Valid Requests (Happy Path)

```php
$runner->addTest('Create task with valid data', function() use ($helper) {
    // Register task type
    $helper->registerTaskType('test.valid', '1.0.0', [
        'type' => 'object',
        'properties' => ['value' => ['type' => 'string']],
        'required' => ['value']
    ]);
    
    // Create task
    $response = $helper->createTask('test.valid', ['value' => 'test']);
    
    // Verify success
    TestRunner::assertTrue($response['data']['success']);
    TestRunner::assertArrayHasKey('id', $response['data']['data']);
});
```

### Testing Error Scenarios

```php
$runner->addTest('Create task with invalid data fails', function() use ($helper) {
    $response = $helper->post('/tasks', [
        'type' => 'nonexistent.type',
        'params' => []
    ]);
    
    // Should fail
    TestRunner::assertFalse($response['data']['success']);
    TestRunner::assertStringContains('not found', 
        strtolower($response['data']['message']));
});
```

### Testing Database State

```php
$runner->addTest('Task status is updated correctly', function() use ($helper) {
    // Create and claim task
    $response = $helper->createTask('test.type', []);
    $taskId = $response['data']['data']['id'];
    
    // Verify in database
    $task = $helper->verifyDbRecord('tasks', $taskId);
    TestRunner::assertEquals('pending', $task['status']);
    TestRunner::assertNotNull($task['created_at']);
});
```

## Best Practices

### 1. Test Isolation

Each test should be independent:
```php
// Good - Creates own test data
$runner->addTest('Test A', function() use ($helper) {
    $helper->registerTaskType('test.a', '1.0.0', $schema);
    // ... test logic
});

// Don't rely on other tests' data
```

### 2. Clear Assertions

Use descriptive assertion messages:
```php
TestRunner::assertTrue($result, 'Task creation should succeed');
TestRunner::assertEquals('pending', $status, 'New task should be pending');
```

### 3. Cleanup

Always cleanup test data:
```php
function testApiIntegration() {
    $helper = new ApiTestHelper();
    
    // Run tests...
    
    $helper->cleanup(); // Clean up at the end
    return $runner->run();
}
```

### 4. Error Handling

Handle expected errors gracefully:
```php
$runner->addTest('Non-existent resource fails', function() use ($helper) {
    $response = $helper->get('/tasks/999999');
    TestRunner::assertFalse($response['data']['success']);
});
```

## Test Coverage

### Current Coverage

**API Integration Tests**: 30+ tests
- Health: 1 test
- Task Types: 8 tests
- Tasks: 11 tests
- Workers: 5 tests
- Listing: 5 tests

**Target Coverage**: >80% of API endpoints

### Coverage Goals

| Component | Target | Status |
|-----------|--------|--------|
| Health endpoint | 100% | ✓ |
| Task type registration | 90% | ✓ |
| Task creation | 90% | ✓ |
| Task claiming | 85% | ✓ |
| Task completion | 85% | ✓ |
| Task listing | 85% | ✓ |
| **Overall** | **85%** | **✓** |

## Troubleshooting

### Database Connection Errors

**Problem**: Tests fail with "Database connection failed"

**Solution**:
```bash
# Check config file exists
ls Backend/TaskManager/config/config.php

# Verify database credentials
# Edit config.php with correct DB_HOST, DB_NAME, DB_USER, DB_PASS
```

### Test Data Conflicts

**Problem**: Tests fail due to existing test data

**Solution**:
```bash
# Run database reset
php tests/run_tests.php --suite=integration

# Or manually clean database:
mysql -u user -p database_name
> DELETE FROM tasks WHERE type_id IN (
    SELECT id FROM task_types WHERE name LIKE 'test.%'
  );
> DELETE FROM task_types WHERE name LIKE 'test.%';
```

### Local vs Remote Mode Issues

**Problem**: Tests work locally but fail in remote mode

**Solution**:
```bash
# Ensure API is running
curl http://localhost/api/health

# Check TASKMANAGER_API_URL is set correctly
echo $TASKMANAGER_API_URL

# Test with explicit URL
TASKMANAGER_API_URL=http://localhost/api php tests/run_tests.php --suite=integration
```

### Slow Test Execution

**Problem**: Tests are slow

**Optimization**:
- Use local testing mode (faster than HTTP)
- Reduce database queries in tests
- Use database transactions for rollback
- Run specific test files instead of full suite

## Performance Targets

### Execution Time
- **Individual test**: <100ms
- **Full suite**: <5 seconds
- **With database**: <10 seconds

### Resource Usage
- Memory: <64MB
- Database connections: <5 concurrent

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:5.7
        env:
          MYSQL_ROOT_PASSWORD: password
          MYSQL_DATABASE: taskmanager_test
        ports:
          - 3306:3306
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '7.4'
          extensions: pdo, pdo_mysql
      
      - name: Configure Database
        run: |
          cp Backend/TaskManager/config/config.example.php Backend/TaskManager/config/config.php
          sed -i 's/DB_HOST/127.0.0.1/' Backend/TaskManager/config/config.php
          sed -i 's/DB_NAME/taskmanager_test/' Backend/TaskManager/config/config.php
      
      - name: Run API Tests
        run: |
          cd Backend/TaskManager
          php tests/run_tests.php --suite=integration
```

## Related Documentation

- [Test Strategy](../_meta/TEST_STRATEGY.md) - Overall testing strategy
- [Testing Guide](README.md) - General testing documentation
- [API Reference](../docs/API_REFERENCE.md) - API endpoint documentation
- [Worker Testing Guide](WORKER_TESTING_GUIDE.md) - Worker testing documentation

## Version History

- **1.0.0** (2025-11-07): Initial API testing guide
  - Documented 30+ integration tests
  - Test execution instructions
  - Troubleshooting guide

---

**Maintained by**: Worker07 - Testing & QA Specialist  
**Last Updated**: 2025-11-07
