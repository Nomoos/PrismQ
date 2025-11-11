# Testing Guide - Frontend/TaskManager

## Overview

This document provides comprehensive guidance on testing the Frontend/TaskManager application. The test suite includes unit tests, component tests, and end-to-end (E2E) tests to ensure code quality and reliability.

## Test Coverage

**Current Status** (as of 2025-11-10):
- **Total Tests**: 581 (561 passing, 17 failing, 3 skipped)
- **Pass Rate**: 96.6%
- **Net Addition**: +120 new tests from baseline

**Coverage by Category**:
- **Components**: 98.27% (base components) ✅
- **Composables**: 95.28% ✅
- **Stores**: 87.33% ✅
- **Services**: 64.47% (needs improvement)
- **Views**: Significantly improved with new comprehensive tests

**Target**: >80% overall coverage (in progress)

## Test Framework

- **Unit/Component Tests**: Vitest + Vue Test Utils
- **E2E Tests**: Playwright
- **Coverage**: V8 provider

## Running Tests

### Run All Unit Tests
```bash
npm test
```

### Run Tests with Coverage
```bash
npm run test:coverage
```

### Run E2E Tests
```bash
npm run test:e2e
```

### Run Specific Test File
```bash
npm test -- worker.spec.ts
```

### Watch Mode
```bash
npm test -- --watch
```

## Test Structure

### Unit Tests Location
```
tests/unit/
├── components/
│   ├── ConfirmDialog.spec.ts         ✅ 9 tests
│   ├── EmptyState.spec.ts            ✅ 18 tests
│   ├── LoadingSkeleton.spec.ts       ✅ 21 tests
│   ├── LoadingSpinner.spec.ts        ✅ 14 tests
│   ├── StatusBadge.spec.ts           ✅ 15 tests
│   ├── Toast.spec.ts                 ✅ 27 tests
│   └── ToastContainer.spec.ts        ✅ 15 tests
├── composables/
│   ├── useAccessibility.spec.ts      ⚠️  36 tests (2 failing)
│   ├── useFormValidation.spec.ts     ✅ 63 tests
│   ├── useIntersectionObserver.spec.ts ✅ 18 tests
│   ├── useTaskPolling.spec.ts        ✅ 11 tests
│   └── useToast.spec.ts              ✅ 23 tests
├── stores/
│   ├── tasks.spec.ts                 ✅ 19 tests
│   └── worker.spec.ts                ✅ 19 tests
├── services/
│   ├── api.spec.ts                   ✅ 2 tests
│   ├── healthService.spec.ts         ✅ 13 tests
│   └── taskService.spec.ts           ✅ 14 tests
├── views/
│   ├── TaskList.spec.ts              ✅ 35 tests
│   ├── TaskDetail.spec.ts            ⚠️  85 tests (9 failing)
│   ├── WorkerDashboard.spec.ts       ✅ 96 tests
│   └── Settings.spec.ts              ⚠️  78 tests (6 failing, 3 skipped)
└── utils/
    ├── debounce.spec.ts              ✅ 15 tests
    ├── optimisticUpdates.spec.ts     ✅ 13 tests
    ├── performance.spec.ts           ✅ 16 tests
    ├── resourceHints.spec.ts         ✅ 10 tests
    ├── sanitize.spec.ts              ✅ 40 tests
    └── lazyLoading.spec.ts           ✅ 7 tests
```

### E2E Tests Location
```
tests/e2e/
├── accessibility.spec.ts
├── task-list.spec.ts
└── workflows.spec.ts
```

## Recent Additions (Worker07)

The following comprehensive test files were added to achieve >80% coverage:

1. **TaskDetail.spec.ts** (85 tests)
   - Component rendering and navigation
   - Task details display and formatting
   - Progress bar visualization
   - Task actions (claim, complete, fail)
   - Worker information display
   - Payload display and JSON formatting
   - Error handling
   - Accessibility compliance

2. **WorkerDashboard.spec.ts** (96 tests)
   - Worker information and status
   - Task statistics and counts
   - Task claiming functionality
   - Color coding and visual indicators
   - Responsive layout
   - Dark mode support
   - Accessibility features

3. **Settings.spec.ts** (78 tests, 3 skipped)
   - Worker configuration
   - API settings display
   - Form validation
   - User feedback messages
   - Responsive design
   - Dark mode support
   - Accessibility compliance

4. **useAccessibility.spec.ts** (36 tests)
   - Screen reader announcements
   - Focus management
   - Focus trapping
   - Focusable elements detection
   - Skip links creation

5. **useIntersectionObserver.spec.ts** (18 tests)
   - Basic intersection observation
   - Lazy loading functionality
   - Fallback behavior
   - Custom options support

## Writing Tests

### Unit Test Example

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(MyComponent, {
      props: {
        title: 'Test'
      }
    })
  })

  it('should render title', () => {
    expect(wrapper.text()).toContain('Test')
  })

  it('should emit event on click', async () => {
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted().click).toBeTruthy()
  })
})
```

### Store Test Example

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useWorkerStore } from '@/stores/worker'

describe('Worker Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should initialize worker', () => {
    const store = useWorkerStore()
    store.initializeWorker()
    
    expect(store.workerId).toBeTruthy()
    expect(store.status).toBe('idle')
  })
})
```

### E2E Test Example

```typescript
import { test, expect } from '@playwright/test'

test('should navigate to task detail', async ({ page }) => {
  await page.goto('/')
  await page.waitForLoadState('networkidle')
  
  const taskCard = page.locator('.card').first()
  await taskCard.click()
  
  expect(page.url()).toMatch(/\/tasks\/\d+/)
})
```

## Test Categories

### 1. Component Tests
Test Vue components in isolation:
- Props validation
- Event emissions
- Computed properties
- Template rendering
- User interactions

**Example Components Tested**:
- ConfirmDialog (93.65% coverage)
- Toast (100% coverage)
- LoadingSkeleton (100% coverage)
- TaskList (100% coverage)

### 2. Store Tests
Test Pinia stores:
- State initialization
- Getters
- Actions
- State mutations
- Error handling

**Example Stores Tested**:
- Worker Store (100% coverage)
- Task Store (85.55% coverage)

### 3. Service Tests
Test API and business logic services:
- API calls
- Error handling
- Data transformation
- Retry logic

**Example Services Tested**:
- Health Service (100% coverage)
- Task Service (100% coverage)
- API Client (38.66% coverage)

### 4. Composable Tests
Test Vue composables:
- State management
- Side effects
- Reactivity
- Cleanup

**Example Composables Tested**:
- useToast (100% coverage)
- useFormValidation (100% coverage)
- useTaskPolling (100% coverage)

### 5. E2E Tests
Test complete user workflows:
- Task viewing and filtering
- Navigation between pages
- Mobile viewport interactions
- Error handling
- Performance

## Coverage Configuration

Coverage is configured in `vitest.config.ts`:

```typescript
coverage: {
  provider: 'v8',
  reporter: ['text', 'json', 'html'],
  exclude: [
    'node_modules/',
    'tests/',
    '**/*.spec.ts',
    '**/*.test.ts'
  ],
  include: ['src/**/*.{ts,vue}'],
  statements: 80,
  branches: 80,
  functions: 80,
  lines: 80
}
```

## Best Practices

### 1. Test Organization
- One test file per source file
- Group related tests with `describe`
- Use descriptive test names with `it('should...')`
- Clean up after each test

### 2. Test Isolation
- Use `beforeEach` to reset state
- Don't depend on test execution order
- Mock external dependencies
- Use fake timers for time-dependent code

### 3. Component Testing
- Test user behavior, not implementation
- Use data-testid attributes for reliable selectors
- Test accessibility (ARIA roles, labels)
- Verify responsive behavior

### 4. Assertions
- Be specific with expectations
- Test both success and error cases
- Verify side effects
- Check edge cases

### 5. Mocking
```typescript
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn()
  }
}))
```

### 6. Async Testing
```typescript
it('should fetch data', async () => {
  await wrapper.vm.fetchData()
  expect(wrapper.vm.data).toBeDefined()
})
```

## Mobile Testing

### Viewport Configuration
```typescript
test.use({
  viewport: { width: 375, height: 667 } // iPhone SE
})
```

### Touch Target Testing
Ensure minimum 44x44px touch targets:
```typescript
const button = await page.locator('button').first()
const box = await button.boundingBox()
expect(box.height).toBeGreaterThanOrEqual(44)
expect(box.width).toBeGreaterThanOrEqual(44)
```

## Accessibility Testing

Test components for accessibility:
- ARIA roles and labels
- Keyboard navigation
- Screen reader compatibility
- Color contrast

Example:
```typescript
it('should have proper ARIA attributes', () => {
  const dialog = wrapper.find('[role="dialog"]')
  expect(dialog.attributes('aria-modal')).toBe('true')
  expect(dialog.attributes('aria-labelledby')).toBeTruthy()
})
```

## Continuous Integration

Tests run automatically on:
- Pull request creation
- Push to main branches
- Pre-deployment checks

## Troubleshooting

### Common Issues

**1. Teleport Components**
Components using `<Teleport>` (e.g., modals) need special handling:
```typescript
wrapper = mount(Component, {
  attachTo: document.body
})
```

**2. Router Components**
Mock Vue Router for components using `<RouterLink>`:
```typescript
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  }),
  RouterLink: {
    template: '<a><slot /></a>'
  }
}))
```

**3. Async State Updates**
Wait for Vue to update the DOM:
```typescript
await wrapper.vm.$nextTick()
await flushPromises()
```

## Test Coverage Goals

| Category | Current | Target | Priority |
|----------|---------|--------|----------|
| Overall | 62.5% | >80% | High |
| Components (base) | 98.27% | >95% | ✅ Met |
| Composables | 95.28% | >90% | ✅ Met |
| Stores | 87.33% | >85% | ✅ Met |
| Services | 64.47% | >80% | Medium |
| Views | 21.18% | >70% | High |
| Router | 0% | >80% | Medium |

## Next Steps

1. Add tests for remaining views (TaskDetail, WorkerDashboard, Settings)
2. Improve API client test coverage
3. Add router integration tests
4. Expand E2E test coverage
5. Document mobile-specific test scenarios

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

## Contact

For questions or issues with tests, contact the QA team or create an issue in the repository.

---

**Last Updated**: 2025-11-10
**Test Suite Version**: 1.0.0
**Total Tests**: 410 passing
**Coverage**: 62.5%
