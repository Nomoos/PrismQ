# ISSUE-FRONTEND-007: Testing & QA

## Status
🔴 NOT STARTED

## Component
Frontend (Testing)

## Type
Testing / Quality Assurance

## Priority
High

## Assigned To
Worker07 - Testing & QA Specialist

## Description
Implement comprehensive testing suite for the Frontend application, including unit tests, component tests, E2E tests, and mobile-specific tests. Ensure >80% code coverage and test all critical user flows.

## Problem Statement
The Frontend needs:
- Unit tests for all components and composables
- Component tests with Vue Test Utils
- E2E tests for critical user flows
- Mobile viewport testing
- Test coverage >80%
- CI/CD integration for automated testing
- Visual regression testing (optional)
- Performance testing

## Solution
Build comprehensive testing infrastructure:
1. Unit testing with Vitest
2. Component testing with Vue Test Utils
3. E2E testing with Playwright (mobile viewports)
4. Coverage reporting and enforcement
5. CI/CD integration
6. Mobile-specific test scenarios
7. Accessibility testing
8. Performance testing

## Deliverables

### Test Infrastructure
- [ ] Vitest configuration
- [ ] Vue Test Utils setup
- [ ] Playwright configuration (mobile viewports)
- [ ] Coverage reporting (Istanbul/c8)
- [ ] CI/CD test integration
- [ ] Test utilities and helpers

### Unit Tests
- [ ] All composables tested (useTask, useWorker, useMobile, etc.)
- [ ] Utility functions tested
- [ ] Store actions and getters tested
- [ ] Router guards tested
- [ ] API client tested (mocked)

### Component Tests
- [ ] All base components tested
- [ ] Task components tested
- [ ] Worker components tested
- [ ] Mobile components tested
- [ ] View components tested

### E2E Tests
- [ ] Task list flow
- [ ] Task claim flow
- [ ] Task complete flow
- [ ] Task create flow
- [ ] Worker dashboard flow
- [ ] Mobile navigation flow
- [ ] Error handling flows

### Mobile Testing
- [ ] Touch interactions
- [ ] Swipe gestures
- [ ] Viewport responsiveness
- [ ] Mobile keyboard
- [ ] Orientation changes
- [ ] Touch target sizes

### Accessibility Testing
- [ ] WCAG 2.1 AA compliance
- [ ] Screen reader compatibility
- [ ] Keyboard navigation
- [ ] Focus management
- [ ] Color contrast
- [ ] ARIA labels

### Performance Testing
- [ ] Load time tests
- [ ] Bundle size tests
- [ ] Lighthouse CI integration
- [ ] Memory leak detection
- [ ] Performance budgets

## Acceptance Criteria
- [ ] Unit test coverage >80%
- [ ] All components have tests
- [ ] All composables have tests
- [ ] E2E tests for critical flows
- [ ] Mobile viewport tests passing
- [ ] Accessibility tests passing
- [ ] Performance tests passing
- [ ] CI/CD runs all tests
- [ ] Coverage reports generated
- [ ] Test documentation complete

## Dependencies
- **Depends On**: ISSUE-FRONTEND-004 (Core Components) - needs components to test
- **Parallel**: Can plan and setup infrastructure early

## Enables
- ISSUE-FRONTEND-010 (Senior Review) - quality validation
- Production deployment confidence

## Technical Details

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'c8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.spec.ts',
        '**/*.test.ts',
        '**/dist/**'
      ],
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

### Test Setup

```typescript
// tests/setup.ts
import { config } from '@vue/test-utils'
import { vi } from 'vitest'

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
})

// Global test configuration
config.global.mocks = {
  $route: {
    params: {},
    query: {}
  },
  $router: {
    push: vi.fn(),
    replace: vi.fn()
  }
}
```

### Unit Test Examples

#### Composable Test
```typescript
// tests/unit/composables/useTask.spec.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useTask } from '@/composables/useTask'
import { setActivePinia, createPinia } from 'pinia'

describe('useTask', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with loading false', () => {
    const { loading } = useTask()
    expect(loading.value).toBe(false)
  })

  it('claims task successfully', async () => {
    const { claimTask, loading } = useTask()
    const promise = claimTask('task-1')
    expect(loading.value).toBe(true)
    await promise
    expect(loading.value).toBe(false)
  })

  it('handles claim error', async () => {
    const { claimTask, error } = useTask()
    // Mock API to throw error
    await claimTask('invalid-task')
    expect(error.value).toBeTruthy()
  })
})
```

#### Store Test
```typescript
// tests/unit/stores/tasks.spec.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTaskStore } from '@/stores/tasks'

describe('Task Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with empty tasks', () => {
    const store = useTaskStore()
    expect(store.tasks).toEqual([])
  })

  it('adds task to store', () => {
    const store = useTaskStore()
    const task = { id: '1', title: 'Test', status: 'pending' }
    store.addTask(task)
    expect(store.tasks).toHaveLength(1)
    expect(store.tasks[0]).toEqual(task)
  })

  it('filters tasks by status', () => {
    const store = useTaskStore()
    store.tasks = [
      { id: '1', status: 'pending' },
      { id: '2', status: 'claimed' },
      { id: '3', status: 'pending' }
    ]
    expect(store.pendingTasks).toHaveLength(2)
  })
})
```

### Component Test Examples

#### Base Component Test
```typescript
// tests/component/BaseButton.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '@/components/common/BaseButton.vue'

describe('BaseButton', () => {
  it('renders with text', () => {
    const wrapper = mount(BaseButton, {
      slots: {
        default: 'Click me'
      }
    })
    expect(wrapper.text()).toBe('Click me')
  })

  it('emits click event', async () => {
    const wrapper = mount(BaseButton)
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(BaseButton, {
      props: { disabled: true }
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('has correct touch target size (44px)', () => {
    const wrapper = mount(BaseButton)
    const button = wrapper.find('button')
    const styles = window.getComputedStyle(button.element)
    expect(parseInt(styles.minHeight)).toBeGreaterThanOrEqual(44)
  })
})
```

#### Complex Component Test
```typescript
// tests/component/TaskCard.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TaskCard from '@/components/tasks/TaskCard.vue'

describe('TaskCard', () => {
  const mockTask = {
    id: '1',
    title: 'Test Task',
    status: 'pending',
    priority: 'high',
    created_at: '2025-11-09T10:00:00Z'
  }

  it('renders task information', () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask }
    })
    expect(wrapper.text()).toContain('Test Task')
    expect(wrapper.text()).toContain('high')
  })

  it('emits claim event when claim button clicked', async () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask }
    })
    await wrapper.find('[data-test="claim-btn"]').trigger('click')
    expect(wrapper.emitted('claim')).toBeTruthy()
    expect(wrapper.emitted('claim')[0]).toEqual(['1'])
  })

  it('shows correct status badge', () => {
    const wrapper = mount(TaskCard, {
      props: { task: { ...mockTask, status: 'completed' } }
    })
    expect(wrapper.find('[data-test="status-badge"]').classes())
      .toContain('status-completed')
  })

  it('handles swipe gesture', async () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask }
    })
    await wrapper.trigger('touchstart', { touches: [{ clientX: 0 }] })
    await wrapper.trigger('touchmove', { touches: [{ clientX: 100 }] })
    await wrapper.trigger('touchend')
    expect(wrapper.emitted('swipe')).toBeTruthy()
  })
})
```

### Playwright E2E Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        viewport: { width: 393, height: 851 }
      }
    },
    {
      name: 'Redmi Simulation',
      use: {
        ...devices['Pixel 5'],
        viewport: { width: 412, height: 915 }, // Approximate Redmi viewport
        deviceScaleFactor: 2.625
      }
    },
    {
      name: 'Desktop Chrome',
      use: { ...devices['Desktop Chrome'] }
    }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI
  }
})
```

### E2E Test Examples

```typescript
// tests/e2e/task-claiming.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Task Claiming Flow', () => {
  test('user can claim a pending task', async ({ page }) => {
    await page.goto('/')
    
    // Wait for task list to load
    await expect(page.locator('[data-test="task-list"]')).toBeVisible()
    
    // Click on a pending task
    await page.locator('[data-test="task-card"]').first().click()
    
    // Click claim button
    await page.locator('[data-test="claim-btn"]').click()
    
    // Verify success toast
    await expect(page.locator('[data-test="toast"]'))
      .toContainText('Task claimed successfully')
    
    // Verify task appears in "My Tasks"
    await page.locator('[data-test="my-tasks-tab"]').click()
    await expect(page.locator('[data-test="task-card"]').first())
      .toBeVisible()
  })

  test('swipe to claim on mobile', async ({ page }) => {
    await page.goto('/')
    await page.setViewportSize({ width: 375, height: 667 })
    
    const taskCard = page.locator('[data-test="task-card"]').first()
    const box = await taskCard.boundingBox()
    
    if (box) {
      // Swipe right
      await page.touchscreen.tap(box.x + 10, box.y + box.height / 2)
      await page.touchscreen.tap(box.x + 200, box.y + box.height / 2)
    }
    
    // Verify claim action triggered
    await expect(page.locator('[data-test="toast"]'))
      .toContainText('Task claimed')
  })
})
```

### Accessibility Testing

```typescript
// tests/e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test'
import { injectAxe, checkA11y } from 'axe-playwright'

test.describe('Accessibility', () => {
  test('homepage is accessible', async ({ page }) => {
    await page.goto('/')
    await injectAxe(page)
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: {
        html: true
      }
    })
  })

  test('task detail page is accessible', async ({ page }) => {
    await page.goto('/tasks/1')
    await injectAxe(page)
    await checkA11y(page)
  })

  test('keyboard navigation works', async ({ page }) => {
    await page.goto('/')
    
    // Tab through interactive elements
    await page.keyboard.press('Tab')
    await expect(page.locator(':focus')).toBeVisible()
    
    // Enter to activate
    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/.*tasks.*/)
  })
})
```

## Test Coverage Goals

### Overall Coverage >80%
- [ ] Statements: >80%
- [ ] Branches: >80%
- [ ] Functions: >80%
- [ ] Lines: >80%

### By Area
- [ ] Components: >90%
- [ ] Composables: >90%
- [ ] Stores: >90%
- [ ] Utils: >95%
- [ ] API Client: >85%
- [ ] Router: >80%

## Timeline
- **Planning**: Week 2 (parallel with development)
- **Implementation**: Week 3
- **Duration**: 1 week
- **Target**: Week 3 completion

## Progress Tracking
- [ ] Test infrastructure setup
- [ ] Unit tests for composables
- [ ] Unit tests for stores
- [ ] Unit tests for utils
- [ ] Component tests (base components)
- [ ] Component tests (task components)
- [ ] Component tests (worker components)
- [ ] E2E tests (critical flows)
- [ ] Mobile viewport tests
- [ ] Accessibility tests
- [ ] Performance tests
- [ ] CI/CD integration
- [ ] Coverage reporting
- [ ] Documentation

## Success Criteria
- ✅ Test coverage >80%
- ✅ All critical flows tested (E2E)
- ✅ Mobile viewport tests passing
- ✅ Accessibility tests passing
- ✅ CI/CD runs tests automatically
- ✅ Coverage reports generated
- ✅ All tests documented
- ✅ Test failures investigated and fixed
- ✅ Approved by Worker10

## Notes
- Plan test structure early (Week 2)
- Write tests alongside development when possible
- Focus on critical user flows for E2E
- Test mobile-specific features thoroughly
- Don't aim for 100% coverage, focus on critical paths
- Mock external dependencies (API calls)
- Use factories/fixtures for test data
- Keep tests fast and reliable

---

**Created By**: Worker01 (Project Manager)  
**Date**: 2025-11-09  
**Assigned To**: Worker07 (Testing & QA Specialist)  
**Status**: 🔴 NOT STARTED  
**Priority**: High (start planning Week 2, implement Week 3)
