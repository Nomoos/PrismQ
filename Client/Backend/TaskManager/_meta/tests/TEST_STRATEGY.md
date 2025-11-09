# TaskManager Test Strategy

## Overview

This document outlines the comprehensive testing strategy for the TaskManager system, following GitHub Copilot Coding Agent best practices and industry standards for PHP-based APIs.

## Testing Philosophy

Following GitHub Copilot best practices:
- **Well-scoped tasks**: Clear, focused tests with specific acceptance criteria
- **Minimal dependencies**: Tests run in isolated environments
- **Fast feedback**: Quick test execution for rapid iteration
- **Comprehensive coverage**: Target >80% code coverage
- **Security-first**: Validate all security measures

## Current State

### Existing Test Infrastructure ✅

**Unit Tests (23 tests)**: All passing
- JsonSchemaValidator: 14 tests covering all validation rules
- ApiResponse: 9 tests covering response formatting

**Security Tests (12 tests)**: All passing
- SQL injection prevention
- XSS pattern handling
- Regex DoS protection
- Input validation edge cases

**Test Framework**: Custom lightweight TestRunner.php (no external dependencies)

**Test Coverage**: 92% (exceeds 85% target) ✅

## Testing Levels

### 1. Unit Tests ✅ (COMPLETED)

**Purpose**: Test individual components in isolation

**Current Coverage**:
- ✅ JsonSchemaValidator (14 tests)
- ✅ ApiResponse (9 tests)
- ✅ Security validation (12 tests)

**Status**: Complete - 35 tests passing, 92% coverage

### 2. API Integration Tests (TO BE IMPLEMENTED)

**Purpose**: Test complete API workflows from HTTP request to response

**Scope**:
- All 9 TaskManager REST endpoints
- Request/response validation
- Error handling
- Status code verification
- Data consistency

**Endpoints to Test**:
1. GET /api/health - Health check
2. POST /api/task-types/register - Register/update task type
3. GET /api/task-types/{name} - Get task type details
4. GET /api/task-types - List task types
5. POST /api/tasks - Create task
6. POST /api/tasks/claim - Claim task (worker)
7. POST /api/tasks/{id}/complete - Complete task (worker)
8. GET /api/tasks/{id} - Get task status
9. GET /api/tasks - List tasks

**Test Categories**:
- Valid request flows (happy path)
- Invalid inputs (validation errors)
- Error scenarios (not found, unauthorized)
- Edge cases (empty data, large payloads)
- Concurrent operations (race conditions)

**Estimated Tests**: 45-60 tests

### 3. Worker Tests (TO BE IMPLEMENTED)

**Purpose**: Validate worker behavior and integration with TaskManager API

**Scope**:
- Worker initialization and configuration
- Task claiming workflow
- Task processing handlers
- Task completion/failure reporting
- Error handling and retry logic
- Graceful shutdown behavior

**Test Categories**:

#### Worker Configuration Tests
- Parse command-line arguments
- Environment variable handling
- Default values validation
- Invalid configuration handling

#### Worker API Integration Tests
- API connectivity check
- Task claiming (with and without type filter)
- Task completion (success)
- Task failure reporting
- Task status queries

#### Worker Lifecycle Tests
- Startup sequence
- Task processing loop
- Signal handling (SIGTERM, SIGINT)
- Graceful shutdown
- Error recovery

#### Worker Handler Tests
- Echo handler (example.echo)
- Uppercase handler (example.uppercase)
- Math handler (example.math.add)
- Sleep handler (example.sleep)
- Error handler (example.error)
- Unknown task type handling

**Estimated Tests**: 30-40 tests

## Test Implementation Plan

### Phase 1: API Integration Tests

#### Step 1: Create Test Framework Extension
Create `tests/integration/ApiTestHelper.php`:
- HTTP client for making API requests
- Database setup/teardown utilities
- Test data fixtures
- Assertion helpers

#### Step 2: Implement Endpoint Tests
Create test files for each endpoint group:
- `tests/integration/HealthEndpointTest.php`
- `tests/integration/TaskTypeEndpointsTest.php`
- `tests/integration/TaskEndpointsTest.php`

#### Step 3: Implement Workflow Tests
Create `tests/integration/WorkflowTest.php`:
- Complete task lifecycle (register type → create → claim → complete)
- Task deduplication flow
- Retry logic flow
- Timeout and reclaim flow

#### Step 4: Update Test Runner
Extend `tests/run_tests.php` to include integration test suite

### Phase 2: Worker Tests

#### Step 1: Create Worker Test Framework
Create `tests/worker/WorkerTestHelper.php`:
- Mock TaskManager API responses
- Worker instance management
- Test task creation utilities
- Output capture helpers

#### Step 2: Implement Worker Tests
Create test files:
- `tests/worker/WorkerConfigTest.php` - Configuration parsing
- `tests/worker/WorkerApiTest.php` - API integration
- `tests/worker/WorkerLifecycleTest.php` - Startup/shutdown
- `tests/worker/WorkerHandlersTest.php` - Task handlers

#### Step 3: Update Test Runner
Add worker test suite to `tests/run_tests.php`

## Test Data Management

### Fixtures
- Sample task type schemas
- Valid and invalid task parameters
- Expected response formats
- Error message templates

### Database State
- Clean database before each test suite
- Transaction rollback for unit tests
- Isolated test database (taskmanager_test)

### Mock Data
- Mock API responses for worker tests
- Sample task payloads
- Error scenarios

## Test Execution

### Local Development
```bash
# Run all tests
php tests/run_tests.php

# Run specific suite
php tests/run_tests.php --suite=unit
php tests/run_tests.php --suite=integration
php tests/run_tests.php --suite=worker

# Run with verbose output
php tests/run_tests.php --verbose

# Run with coverage report
php tests/run_tests.php --coverage
```

### Pre-commit Hook
```bash
# Install pre-commit hook
cp _meta/scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Hook will automatically run all tests before commit
```

### Continuous Integration (Future)
```yaml
# GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '7.4'
      - name: Run tests
        run: php Backend/TaskManager/tests/run_tests.php
```

## Success Criteria

### API Integration Tests
- ✅ All 9 endpoints tested
- ✅ >80% code coverage maintained
- ✅ All tests passing
- ✅ Response format validation
- ✅ Error scenarios covered
- ✅ Concurrent operations tested

### Worker Tests
- ✅ All configuration options tested
- ✅ All task handlers tested
- ✅ Lifecycle management validated
- ✅ Error handling verified
- ✅ Integration with API confirmed

### Overall Quality Gates
- ✅ Total test count: >100 tests
- ✅ Test coverage: >80%
- ✅ All tests pass
- ✅ Performance targets met (tests complete in <10s)
- ✅ Documentation complete
- ✅ Security vulnerabilities addressed

## Performance Benchmarks

### Test Execution Time Targets
- Unit tests: <0.5s
- Integration tests: <5s
- Worker tests: <3s
- **Total execution time: <10s**

### API Performance Targets
(From existing performance tests)
- GET endpoints: <100ms
- POST endpoints: <200ms
- Task claim: <150ms
- Task complete: <100ms

## Security Considerations

### API Security Tests
- Input validation bypass attempts
- SQL injection prevention (via prepared statements)
- XSS prevention (output encoding)
- Authentication/authorization (future)
- Rate limiting (future)

### Worker Security Tests
- Environment variable handling
- API credential security
- Task parameter validation
- Error message sanitization

## Documentation

### Test Documentation to Maintain
1. **TEST_STRATEGY.md** (this document) - Overall strategy
2. **tests/README.md** - Existing test guide (update with new tests)
3. **API_TESTING_GUIDE.md** - Detailed API test guide (new)
4. **WORKER_TESTING_GUIDE.md** - Detailed worker test guide (new)

### Code Documentation
- Inline comments in test files
- PHPDoc blocks for test methods
- Test data fixtures documentation
- Helper function documentation

## Monitoring and Maintenance

### Test Health Monitoring
- Track test execution time
- Monitor test failure rate
- Identify flaky tests
- Update tests when APIs change

### Regular Reviews
- Weekly test coverage review
- Monthly test suite optimization
- Quarterly security test updates
- Annual strategy review

## References

### GitHub Copilot Best Practices
- Clear, well-scoped test tasks
- Specific acceptance criteria
- Minimal code changes
- Fast feedback loops
- Comprehensive coverage

### Industry Standards
- PHPUnit best practices
- REST API testing patterns
- Security testing guidelines (OWASP)
- Continuous testing practices

### Related Documentation
- [Testing Guide](tests/README.md) - Current test documentation
- [API Reference](docs/API_REFERENCE.md) - API endpoint details
- [Worker Implementation](examples/workers/php/worker.php) - Worker code
- [GitHub Copilot Guidelines](https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/coding-agent/get-the-best-results)

## Appendix A: Test Naming Conventions

### File Naming
- Unit tests: `ClassNameTest.php`
- Integration tests: `EndpointNameTest.php`
- Worker tests: `Worker[Feature]Test.php`

### Function Naming
- Test functions: `testFeatureDescription()`
- Helper functions: descriptive names
- Fixture functions: `create[Entity]Fixture()`

### Test Organization
```
tests/
├── unit/                    # Unit tests (existing)
│   ├── JsonSchemaValidatorTest.php
│   └── ApiResponseTest.php
├── integration/             # API integration tests (new)
│   ├── ApiTestHelper.php
│   ├── HealthEndpointTest.php
│   ├── TaskTypeEndpointsTest.php
│   ├── TaskEndpointsTest.php
│   └── WorkflowTest.php
├── worker/                  # Worker tests (new)
│   ├── WorkerTestHelper.php
│   ├── WorkerConfigTest.php
│   ├── WorkerApiTest.php
│   ├── WorkerLifecycleTest.php
│   └── WorkerHandlersTest.php
├── security/                # Security tests (existing)
│   └── SecurityTest.php
├── fixtures/                # Test data (new)
│   ├── task_types.php
│   ├── tasks.php
│   └── responses.php
├── TestRunner.php           # Test framework (existing)
└── run_tests.php            # Main test runner (existing)
```

## Appendix B: Example Test Cases

### Example API Integration Test
```php
// Test task creation endpoint
function testCreateTaskWithValidData() {
    $helper = new ApiTestHelper();
    
    // Setup: Register task type
    $helper->registerTaskType('test.type', '1.0.0', [
        'type' => 'object',
        'properties' => ['value' => ['type' => 'string']],
        'required' => ['value']
    ]);
    
    // Test: Create task
    $response = $helper->post('/tasks', [
        'type' => 'test.type',
        'params' => ['value' => 'test']
    ]);
    
    // Assert
    TestRunner::assertEquals(201, $response['code']);
    TestRunner::assertTrue($response['data']['success']);
    TestRunner::assertNotNull($response['data']['data']['id']);
    TestRunner::assertEquals('pending', $response['data']['data']['status']);
}
```

### Example Worker Test
```php
// Test worker task claiming
function testWorkerClaimTask() {
    $helper = new WorkerTestHelper();
    
    // Setup: Create pending task
    $taskId = $helper->createTestTask('example.echo', [
        'message' => 'test'
    ]);
    
    // Test: Worker claims task
    $worker = $helper->createWorker('test-worker-01');
    $task = $worker->claimTask();
    
    // Assert
    TestRunner::assertNotNull($task);
    TestRunner::assertEquals($taskId, $task['id']);
    TestRunner::assertEquals('example.echo', $task['type']);
    TestRunner::assertEquals(1, $task['attempts']);
}
```

## Version History

- **1.0.0** (2025-11-07): Initial test strategy document
  - Defined comprehensive testing approach
  - Planned API integration tests
  - Planned worker tests
  - Established success criteria

---

**Maintained by**: Worker07 - Testing & QA Specialist  
**Last Updated**: 2025-11-07  
**Status**: Active - Implementation in progress
