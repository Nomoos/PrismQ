# Worker07 Testing Infrastructure

This directory contains comprehensive testing for the TaskManager application.

## Test Structure

```
tests/
├── unit/           # Unit tests for stores, services, and utilities
│   ├── tasks.spec.ts
│   └── taskService.spec.ts
└── e2e/            # End-to-end tests
    └── task-list.spec.ts
```

## Running Tests

### Unit Tests

Unit tests are written with Vitest and @vue/test-utils.

```bash
# Run all unit tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm run test:coverage

# Run a specific test file
npm test tests/unit/tasks.spec.ts
```

### E2E Tests

E2E tests are written with Playwright.

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode (interactive)
npm run test:e2e:ui

# Run E2E tests in headed mode (see browser)
npm run test:e2e -- --headed

# Run E2E tests for specific project
npm run test:e2e -- --project="Mobile Chrome"
```

## Test Coverage

Current test coverage:

- **Task Store**: 19 tests
  - State initialization
  - Getters (filtering)
  - Actions (fetchTasks, createTask, updateProgress)
  - Error handling

- **Task Service**: 14 tests
  - API method calls
  - Request parameter handling
  - Response handling

- **E2E Tests**: 5 test scenarios
  - Task list display
  - Navigation
  - Mobile viewport
  - Responsive design

## Writing Tests

### Unit Test Example

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTaskStore } from '@/stores/tasks'

describe('My Feature', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should do something', () => {
    const store = useTaskStore()
    expect(store.tasks).toEqual([])
  })
})
```

### E2E Test Example

```typescript
import { test, expect } from '@playwright/test'

test('should display page', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toBeVisible()
})
```

## Test Configuration

### Vitest (Unit Tests)

Configuration in `vitest.config.ts`:
- Environment: jsdom
- Coverage provider: v8
- Coverage threshold: 80%

### Playwright (E2E Tests)

Configuration in `playwright.config.ts`:
- Test directory: `./tests/e2e`
- Base URL: http://localhost:5173
- Projects: Desktop Chrome, Mobile Chrome
- Automatic dev server startup

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run unit tests
  run: npm test -- --run

- name: Run E2E tests
  run: |
    npx playwright install --with-deps
    npm run test:e2e
```

## Troubleshooting

### Unit Tests

**Issue**: Module not found errors
- **Solution**: Ensure path aliases are configured in `vitest.config.ts`

**Issue**: Pinia errors
- **Solution**: Always call `setActivePinia(createPinia())` in `beforeEach`

### E2E Tests

**Issue**: Browsers not installed
- **Solution**: Run `npx playwright install`

**Issue**: Port already in use
- **Solution**: Stop other dev servers or change port in `playwright.config.ts`

**Issue**: Tests timeout
- **Solution**: Increase timeout in `playwright.config.ts` or use `test.setTimeout()`

## Test Data

Mock data and fixtures should be placed in:
- `tests/fixtures/` - Shared test data
- `tests/mocks/` - Mock services and utilities

## Next Steps

1. Add component tests for Vue components
2. Add integration tests for API + Store
3. Increase E2E test coverage for all user flows
4. Add accessibility tests with @axe-core/playwright
5. Set up test coverage reporting in CI/CD

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Playwright Documentation](https://playwright.dev/)
