# Testing Guide

## Overview

This guide covers testing practices for the TaskManager frontend application. We use Vitest for unit and component tests, and Playwright for end-to-end tests.

## Test Structure

```
tests/
├── unit/              # Unit and component tests
│   ├── *.spec.ts      # Test files
│   └── ...
└── e2e/               # End-to-end tests
    ├── *.spec.ts      # E2E test files
    └── ...
```

## Running Tests

### Unit Tests

```bash
# Run all unit tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- path/to/test.spec.ts

# Run tests with coverage
npm run test:coverage
```

### E2E Tests

```bash
# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode
npm run test:e2e:ui

# Run E2E tests for specific browser
npm run test:e2e -- --project="Mobile Chrome"
```

## Writing Tests

### Unit Tests

Unit tests should focus on testing individual functions, composables, and stores.

**Example: Testing a composable**

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { useToast } from '@/composables/useToast'

describe('useToast', () => {
  beforeEach(() => {
    const { clear } = useToast()
    clear()
  })

  it('should show toast message', () => {
    const { showToast, toasts } = useToast()
    
    showToast('Test message', 'success')
    
    expect(toasts.value).toHaveLength(1)
    expect(toasts.value[0].message).toBe('Test message')
  })
})
```

### Component Tests

Component tests verify Vue components render correctly and respond to user interactions.

**Example: Testing a component**

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '@/components/base/StatusBadge.vue'

describe('StatusBadge', () => {
  it('should render status text', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'pending' }
    })
    
    expect(wrapper.text()).toBe('PENDING')
  })

  it('should apply correct styling', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'completed' }
    })
    
    expect(wrapper.classes()).toContain('bg-green-100')
  })
})
```

### Store Tests

Store tests verify Pinia stores manage state correctly.

**Example: Testing a store**

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTaskStore } from '@/stores/tasks'

describe('Task Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should fetch tasks', async () => {
    const store = useTaskStore()
    
    await store.fetchTasks()
    
    expect(store.loading).toBe(false)
    expect(store.error).toBeNull()
  })
})
```

### E2E Tests

E2E tests verify complete user workflows in a real browser.

**Example: Testing navigation**

```typescript
import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('should navigate to settings', async ({ page }) => {
    await page.goto('/')
    
    await page.click('[data-test="settings-link"]')
    
    await expect(page).toHaveURL(/\/settings/)
  })
})
```

## Best Practices

### General

1. **Test behavior, not implementation**
   - Focus on what the code does, not how it does it
   - Avoid testing internal implementation details

2. **Use descriptive test names**
   ```typescript
   // Good
   it('should display error message when login fails')
   
   // Bad
   it('test login')
   ```

3. **Follow the AAA pattern**
   - **Arrange**: Set up test data and conditions
   - **Act**: Execute the code being tested
   - **Assert**: Verify the results

4. **Keep tests independent**
   - Each test should be able to run independently
   - Use `beforeEach` to reset state

5. **Don't test third-party libraries**
   - Trust that libraries like Vue, Pinia work correctly
   - Test your code that uses them

### Component Testing

1. **Test user-visible behavior**
   ```typescript
   // Good
   expect(wrapper.text()).toContain('Welcome')
   
   // Avoid
   expect(wrapper.vm.internalState).toBe(true)
   ```

2. **Use data-test attributes for stable selectors**
   ```vue
   <button data-test="submit-btn">Submit</button>
   ```
   
   ```typescript
   wrapper.find('[data-test="submit-btn"]')
   ```

3. **Test accessibility**
   - Verify ARIA attributes
   - Check keyboard navigation
   - Ensure proper semantic HTML

### E2E Testing

1. **Test critical user flows**
   - Focus on the most important user journeys
   - Don't test every edge case in E2E tests

2. **Use page object pattern for complex pages**
   ```typescript
   class TaskListPage {
     constructor(public page: Page) {}
     
     async goto() {
       await this.page.goto('/tasks')
     }
     
     async claimTask(taskId: number) {
       await this.page.click(`[data-task-id="${taskId}"] [data-test="claim-btn"]`)
     }
   }
   ```

3. **Handle async operations properly**
   ```typescript
   // Wait for network requests
   await page.waitForLoadState('networkidle')
   
   // Wait for specific elements
   await page.waitForSelector('[data-test="task-list"]')
   ```

4. **Test on mobile viewports**
   ```typescript
   test.use({ ...devices['Pixel 5'] })
   
   test('should work on mobile', async ({ page }) => {
     // Test will run with mobile viewport
   })
   ```

## Mocking

### Mocking Modules

```typescript
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))
```

### Mocking Functions

```typescript
const mockFn = vi.fn()
mockFn.mockReturnValue('mocked value')
mockFn.mockResolvedValue({ data: [] })
```

### Mocking Timers

```typescript
beforeEach(() => {
  vi.useFakeTimers()
})

afterEach(() => {
  vi.restoreAllMocks()
})

test('debounce function', () => {
  const fn = vi.fn()
  const debounced = debounce(fn, 100)
  
  debounced()
  vi.advanceTimersByTime(100)
  
  expect(fn).toHaveBeenCalled()
})
```

## Coverage

### Coverage Goals

- **Overall**: > 80%
- **Composables**: > 90%
- **Stores**: > 85%
- **Services**: > 85%
- **Components**: > 70%

### Viewing Coverage

```bash
# Generate coverage report
npm run test:coverage

# Open HTML coverage report
open coverage/index.html
```

### Excluded from Coverage

- Test files (*.spec.ts, *.test.ts)
- Configuration files
- Type definitions
- Generated files

## Continuous Integration

Tests run automatically on:
- Push to any branch
- Pull request creation/update

### CI Configuration

See `.github/workflows/test.yml` for CI configuration.

## Debugging Tests

### Vitest

```bash
# Run tests in debug mode
node --inspect-brk ./node_modules/vitest/vitest.mjs run

# Use console.log (visible in test output)
console.log('Debug:', variable)
```

### Playwright

```bash
# Run in headed mode
npm run test:e2e -- --headed

# Run in debug mode
npm run test:e2e -- --debug

# Take screenshots on failure (automatic)
# Screenshots saved to test-results/
```

## Common Issues

### Issue: Tests timing out

**Solution**: Increase timeout
```typescript
test('slow test', async ({ page }) => {
  // Custom timeout for this test
}, { timeout: 60000 })
```

### Issue: Flaky tests

**Solution**: 
- Add proper waits
- Mock time-dependent code
- Use stable selectors

### Issue: Component not rendering

**Solution**: Check if you need to provide dependencies
```typescript
mount(Component, {
  global: {
    plugins: [router, pinia],
    stubs: {
      'external-component': true
    }
  }
})
```

## Resources

- [Vitest Documentation](https://vitest.dev)
- [Vue Test Utils](https://test-utils.vuejs.org)
- [Playwright Documentation](https://playwright.dev)
- [Testing Library Best Practices](https://testing-library.com/docs/guiding-principles)

## Getting Help

- Check existing tests for examples
- Review this guide
- Ask the team in #testing channel
- File an issue if you find bugs in the test infrastructure
