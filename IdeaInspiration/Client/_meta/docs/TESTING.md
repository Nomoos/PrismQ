# PrismQ Web Client - Test Documentation

This document describes the comprehensive test coverage for both the Backend and Frontend components of the PrismQ Web Client.

## Test Overview

### Backend Tests (FastAPI + pytest)
- **Location**: `Backend/tests/`
- **Framework**: pytest + pytest-asyncio
- **Tests**: 5 passing tests
- **Coverage**: API endpoints, health checks, error handling

### Frontend Tests (Vue 3 + Vitest)
- **Location**: `Frontend/tests/unit/`
- **Framework**: Vitest + Vue Test Utils
- **Tests**: 18 passing tests
- **Coverage**: Types, services, components

## Backend Test Suite

### Location
```
Client/_meta/tests/
├── Backend/
│   ├── __init__.py
│   └── test_api.py          # API endpoint tests (5 tests)
└── Frontend/unit/
    ├── types.spec.ts         # Type validation tests (6 tests)
    ├── services.spec.ts      # API service tests (4 tests)
    └── ModuleCard.spec.ts    # Component tests (8 tests)
```

### Running Backend Tests

```bash
cd Client/Backend
pytest ../_meta/tests/Backend/ -v
```

### Test Coverage

#### 1. Health Check Tests
- ✅ Health endpoint returns 200 OK
- ✅ Health response includes service status and version

#### 2. Root Endpoint Tests
- ✅ Root endpoint returns API information
- ✅ Response includes docs and health URLs

#### 3. Module API Tests
- ✅ List all modules successfully
- ✅ Get specific module by ID
- ✅ Handle module not found (404 error)

#### 4. Error Handling Tests
- ✅ Proper error responses for invalid requests
- ✅ 404 errors for nonexistent resources

### Backend Test Results
```
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_root_endpoint PASSED
tests/test_api.py::test_list_modules PASSED
tests/test_api.py::test_get_module PASSED
tests/test_api.py::test_get_nonexistent_module PASSED

5 passed
```

## Frontend Test Suite

### Location
```
Frontend/tests/unit/
├── types.spec.ts         # Type validation tests (6 tests)
├── services.spec.ts      # API service tests (4 tests)
└── ModuleCard.spec.ts    # Component tests (8 tests)
```

### Running Frontend Tests

```bash
cd Frontend
npm test                  # Run all tests
npm test -- --watch       # Watch mode
npm run test:ui           # Interactive UI
npm run coverage          # Generate coverage report
```

### Test Coverage

#### 1. Type Tests (`types.spec.ts` - 6 tests)

**Module Types:**
- ✅ Create valid Module object
- ✅ Create valid ModuleParameter object
- ✅ Handle optional ModuleParameter options

**Run Types:**
- ✅ Create valid Run object
- ✅ Handle all RunStatus values (queued, running, completed, failed, cancelled)
- ✅ Handle optional Run fields (end_time, exit_code, error_message)

#### 2. Service Tests (`services.spec.ts` - 4 tests)

**Module Service:**
- ✅ List modules successfully
- ✅ Get specific module by ID
- ✅ Handle API errors when listing modules
- ✅ Handle API errors when getting a module

**Features Tested:**
- Axios integration
- API endpoint calls
- Error handling and propagation
- Response data transformation

#### 3. Component Tests (`ModuleCard.spec.ts` - 8 tests)

**Rendering:**
- ✅ Render module information (name, description, category)
- ✅ Display parameter count
- ✅ Show "Launch Module" button when enabled
- ✅ Show "Disabled" button when module is disabled

**Interaction:**
- ✅ Emit launch event with correct parameters
- ✅ Apply hover styles correctly

**Edge Cases:**
- ✅ Handle modules with no parameters
- ✅ Handle modules with multiple parameters

### Frontend Test Results
```
✓ tests/unit/types.spec.ts (6 tests)
✓ tests/unit/services.spec.ts (4 tests)
✓ tests/unit/ModuleCard.spec.ts (8 tests)

Test Files  3 passed (3)
Tests  18 passed (18)
```

## Combined Test Results

### Summary
- **Total Tests**: 23 (5 Backend + 18 Frontend)
- **Passing**: 23/23 (100%)
- **Failing**: 0
- **Test Frameworks**: pytest, Vitest, Vue Test Utils

### Coverage Breakdown

#### Backend Coverage
```
✅ Health & Info Endpoints    (2/2 tests)
✅ Module Discovery API        (2/2 tests)
✅ Error Handling              (1/1 tests)
```

#### Frontend Coverage
```
✅ TypeScript Types            (6/6 tests)
✅ API Service Layer           (4/4 tests)
✅ Vue Components              (8/8 tests)
```

## Test Commands

### Backend
```bash
# Run all Backend tests
cd Client/Backend
pytest ../_meta/tests/Backend/ -v

# Run with coverage
pytest ../_meta/tests/Backend/ -v --cov=src --cov-report=html

# Run specific test file
pytest ../_meta/tests/Backend/test_api.py -v
```

### Frontend
```bash
# Run all Frontend tests
cd Client/Frontend
npm test

# Run in watch mode (development)
npm test -- --watch

# Run with UI
npm run test:ui

# Generate coverage report
npm run coverage

# Run specific test file
npm test ../_meta/tests/Frontend/unit/types.spec.ts
```

## Continuous Integration

Both test suites are designed to run in CI/CD pipelines:

### Backend CI
```yaml
- name: Test Backend
  run: |
    cd Client/Backend
    pip install -r requirements.txt
    pytest ../_meta/tests/Backend/ -v
```

### Frontend CI
```yaml
- name: Test Frontend
  run: |
    cd Client/Frontend
    npm install
    npm test -- --run
```

## Test Quality Metrics

### Backend
- **Test Coverage**: Core API endpoints
- **Async Testing**: Full async/await support
- **HTTP Testing**: Uses httpx AsyncClient
- **Assertions**: FastAPI status codes and JSON responses

### Frontend
- **Component Testing**: Vue Test Utils mounting
- **Type Safety**: Full TypeScript coverage
- **Mocking**: Proper axios mocking for services
- **User Interaction**: Event emission and click handlers

## Adding New Tests

### Backend Test Template
```python
@pytest.mark.asyncio
async def test_new_endpoint():
    """Test description."""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        response = await client.get("/new-endpoint")
    
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

### Frontend Test Template
```typescript
import { describe, it, expect } from 'vitest'

describe('New Feature', () => {
  it('should do something', () => {
    // Test implementation
    expect(true).toBe(true)
  })
})
```

## Test Maintenance

- Keep tests focused and isolated
- Mock external dependencies (APIs, databases)
- Use descriptive test names
- Test both success and error cases
- Maintain test coverage above 80%
- Run tests before committing

## Troubleshooting

### Backend Tests Fail
1. Ensure all dependencies installed: `pip install -r requirements.txt`
2. Check Python version (3.10+)
3. Verify FastAPI app imports correctly

### Frontend Tests Fail
1. Ensure all dependencies installed: `npm install`
2. Check Node.js version (18+)
3. Clear node_modules and reinstall if needed
4. Verify Vitest configuration

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
