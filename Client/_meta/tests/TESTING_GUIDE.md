# Testing Guide - PrismQ Client

This guide explains how to run and maintain tests for the PrismQ Client application.

## Test Structure

```
Client/
├── _meta/tests/
│   ├── Backend/
│   │   ├── test_*.py           # Unit tests
│   │   └── integration/
│   │       └── test_api_workflows.py  # API integration tests
│   └── Frontend/
│       ├── unit/
│       │   └── *.spec.ts       # Component & service unit tests
│       └── e2e/
│           └── *.spec.ts       # End-to-end tests
├── Backend/
│   ├── pyproject.toml          # Python project configuration
│   └── requirements.txt        # Python dependencies
└── Frontend/
    ├── package.json            # Node.js project configuration
    ├── vitest.config.ts        # Vitest configuration
    └── playwright.config.ts    # Playwright configuration (in Client/)
```

## Backend Tests

### Running Tests

```bash
cd Client/Backend

# Run all backend tests
python -m pytest ../_meta/tests/Backend/ -v

# Run only unit tests
python -m pytest ../_meta/tests/Backend/ -v --ignore=../_meta/tests/Backend/integration/

# Run only integration tests
python -m pytest ../_meta/tests/Backend/integration/ -v

# Run with coverage
python -m pytest ../_meta/tests/Backend/ --cov=src --cov-report=html

# Run specific test file
python -m pytest ../_meta/tests/Backend/test_api.py -v

# Run specific test
python -m pytest ../_meta/tests/Backend/test_api.py::test_health_check -v
```

### Test Coverage

Current coverage: **150 unit tests + 6 integration tests = 156 tests total**

Test categories:
- API endpoint tests
- Module runner tests
- Run registry tests
- Process manager tests
- Output capture tests
- Configuration storage tests
- Edge case tests
- Integration workflow tests

### Writing New Backend Tests

1. Create test file following naming convention: `test_*.py`
2. Import required modules:
   ```python
   import pytest
   from httpx import AsyncClient, ASGITransport
   from src.main import app
   ```
3. Use `@pytest.mark.asyncio` for async tests
4. Follow existing patterns for consistency

## Frontend Tests

### Running Tests

```bash
cd Client/Frontend

# Run all unit tests
npm test

# Run tests in UI mode
npm run test:ui

# Run tests with coverage
npm run coverage

# Run E2E tests (requires backend and frontend running)
npm run test:e2e

# Run E2E tests in UI mode
npm run test:e2e:ui

# View E2E test report
npm run test:e2e:report
```

### Test Coverage

Current coverage: **74 component and service tests**

Test categories:
- Component tests (ModuleCard, LogViewer, etc.)
- Service tests (API client, modules, runs)
- Type validation tests
- E2E workflow tests

### Writing New Frontend Tests

#### Unit Tests (Vitest)

1. Create test file: `*.spec.ts` in `_meta/tests/Frontend/unit/`
2. Import testing utilities:
   ```typescript
   import { describe, it, expect } from 'vitest'
   import { mount } from '@vue/test-utils'
   ```
3. Write tests:
   ```typescript
   describe('MyComponent', () => {
     it('should render correctly', () => {
       const wrapper = mount(MyComponent, {
         props: { /* props */ }
       })
       expect(wrapper.text()).toContain('expected text')
     })
   })
   ```

#### E2E Tests (Playwright)

1. Create test file in `_meta/tests/Frontend/e2e/`
2. Import Playwright:
   ```typescript
   import { test, expect } from '@playwright/test'
   ```
3. Write tests:
   ```typescript
   test('should complete workflow', async ({ page }) => {
     await page.goto('/')
     await page.click('button')
     await expect(page.locator('.result')).toBeVisible()
   })
   ```

## Integration Tests

Integration tests verify complete API workflows from start to finish.

### Test Scenarios

1. **Complete Module Launch Workflow**
   - Health check
   - List modules
   - Get/save configuration
   - Launch module
   - Get run details
   - Get run logs

2. **Run Listing and Filtering**
   - Pagination
   - Status filtering
   - Module filtering

3. **Error Handling**
   - Non-existent resources
   - Invalid parameters

4. **Concurrent Operations**
   - Multiple simultaneous requests
   - Data consistency

5. **Module Statistics**
   - Run tracking
   - Stats updates

6. **API Response Consistency**
   - Response format validation
   - Required fields presence

## CI/CD Integration

### GitHub Actions (Future)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd Client/Backend
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          cd Client/Backend
          pytest ../_meta/tests/Backend/ -v --cov=src

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd Client/Frontend
          npm install
      - name: Run tests
        run: |
          cd Client/Frontend
          npm test
          npm run coverage
```

## Performance Testing

### Backend Performance

```bash
cd Client/Backend

# Profile a specific test
python -m cProfile -o profile.stats -m pytest ../_meta/tests/Backend/test_api.py

# Analyze profile
python -m pstats profile.stats
```

### Load Testing (Locust)

Create `locustfile.py`:
```python
from locust import HttpUser, task, between

class WebClientUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_modules(self):
        self.client.get("/api/modules")
    
    @task(1)
    def launch_module(self):
        self.client.post("/api/modules/test-module/run", 
                        json={"parameters": {}})
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## Test Best Practices

### General
1. Write descriptive test names
2. Test one thing per test
3. Use fixtures for shared setup
4. Clean up resources in teardown
5. Mock external dependencies
6. Test edge cases and error conditions

### Backend
1. Use `AsyncClient` for API tests
2. Test both success and error paths
3. Validate response status codes and structure
4. Use parametrized tests for multiple scenarios
5. Test concurrent operations

### Frontend
1. Test component behavior, not implementation
2. Use `mount()` for full rendering
3. Test user interactions (clicks, inputs)
4. Mock API calls
5. Test accessibility (ARIA labels)

### E2E
1. Test critical user workflows
2. Use page objects for reusable elements
3. Wait for elements to be ready
4. Take screenshots on failure
5. Keep tests independent

## Troubleshooting

### Common Issues

**Backend tests fail with import errors:**
```bash
cd Client/Backend
pip install -e ".[dev]"
```

**Frontend tests can't resolve @vue/test-utils:**
- Check `vitest.config.ts` has the correct alias
- Reinstall dependencies: `npm install`

**E2E tests timeout:**
- Ensure backend is running on http://localhost:8000
- Ensure frontend is running on http://localhost:5173
- Increase timeout in `playwright.config.ts`

**Tests pass locally but fail in CI:**
- Check environment variables
- Verify dependencies are installed
- Check for timing issues (add waits)

## Test Maintenance

### Adding New Tests
1. Identify what to test (new feature, bug fix)
2. Choose appropriate test type (unit/integration/e2e)
3. Write test following existing patterns
4. Verify test passes
5. Update this documentation if needed

### Updating Existing Tests
1. Tests should be updated when:
   - API contracts change
   - Component behavior changes
   - New edge cases discovered
   - Bugs are fixed (add regression test)

### Test Metrics
Track these metrics:
- Total test count
- Test coverage percentage
- Test execution time
- Flaky test rate
- Bug detection rate

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Quick Reference

```bash
# Backend
cd Client/Backend
python -m pytest ../_meta/tests/Backend/ -v                    # All tests
python -m pytest ../_meta/tests/Backend/ --cov=src            # With coverage
python -m pytest ../_meta/tests/Backend/integration/ -v        # Integration only

# Frontend
cd Client/Frontend
npm test                           # Unit tests
npm run coverage                   # With coverage
npm run test:e2e                   # E2E tests
npm run test:e2e:ui                # E2E tests in UI mode

# Both
./scripts/run_all_tests.sh         # Run all tests (if script exists)
```
