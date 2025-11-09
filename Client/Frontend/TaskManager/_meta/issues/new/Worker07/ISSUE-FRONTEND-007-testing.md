# ISSUE-FRONTEND-007: Testing & QA

## Status
🔴 NOT STARTED

## Component
Frontend (Testing / Quality Assurance)

## Type
Testing / QA

## Priority
High

## Assigned To
Worker07 - Testing & QA Specialist

## Description
Implement comprehensive testing suite for Frontend/TaskManager including unit tests, component tests, integration tests, and end-to-end tests with focus on mobile viewports and accessibility.

## Problem Statement
The Frontend needs:
- Unit tests for utilities and composables
- Component tests for all Vue components
- Integration tests for API services
- End-to-end tests for critical user flows
- Mobile viewport testing
- Accessibility testing
- > 80% test coverage

## Solution
Create complete testing infrastructure including:
1. Vitest setup for unit/component tests
2. Playwright setup for E2E tests
3. Test utilities and helpers
4. Mock data and fixtures
5. CI/CD integration
6. Coverage reporting

## Deliverables

### Testing Infrastructure
- [ ] Vitest configuration
- [ ] Playwright configuration
- [ ] Test utilities and helpers
- [ ] Mock API server
- [ ] Fixture data
- [ ] Coverage reporting setup
- [ ] CI/CD integration

### Unit Tests
- [ ] Utility function tests
- [ ] Composable tests
- [ ] Store tests (Pinia)
- [ ] Service tests (API client)
- [ ] Type validation tests

### Component Tests
- [ ] Base component tests
- [ ] Task component tests
- [ ] Worker component tests
- [ ] View tests
- [ ] Accessibility tests

### Integration Tests
- [ ] API integration tests
- [ ] Router integration tests
- [ ] Store + API integration
- [ ] Component composition tests

### E2E Tests
- [ ] Task claiming flow
- [ ] Task completion flow
- [ ] Task creation flow
- [ ] Navigation tests
- [ ] Mobile viewport tests
- [ ] Error handling tests

### Documentation
- [ ] Testing guide
- [ ] Writing tests guide
- [ ] Running tests guide
- [ ] CI/CD documentation
- [ ] Coverage reports

## Acceptance Criteria
- [ ] > 80% code coverage (all types)
- [ ] All critical flows tested
- [ ] All components have tests
- [ ] Mobile viewport tests passing
- [ ] Accessibility tests passing
- [ ] CI/CD pipeline integrated
- [ ] All tests passing
- [ ] Documentation complete

## Dependencies
- ISSUE-FRONTEND-001 (Project Setup) - provides structure
- ISSUE-FRONTEND-003 (API Integration) - for integration tests
- ISSUE-FRONTEND-004 (Core Components) - for component tests

## Testing Stack

### Unit & Component Testing
- **Framework**: Vitest
- **Component Testing**: @vue/test-utils
- **Assertions**: expect (Vitest)
- **Mocking**: vi (Vitest)
- **Coverage**: c8

### E2E Testing
- **Framework**: Playwright
- **Browsers**: Chromium, WebKit (mobile)
- **Viewports**: Mobile (375px), Tablet (768px), Desktop (1280px)

### Accessibility Testing
- **Tools**: axe-core, @axe-core/playwright
- **Standards**: WCAG 2.1 AA

## Test Configuration

### Vitest Config
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      provider: 'c8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.spec.ts',
        '**/*.test.ts'
      ],
      statements: 80,
      branches: 80,
      functions: 80,
      lines: 80
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
```

### Playwright Config
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
  },
  projects: [
    // Mobile (Redmi 24115RA8EG)
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        viewport: { width: 360, height: 800 }
      },
    },
    // Tablet
    {
      name: 'Tablet',
      use: { 
        ...devices['iPad Pro'],
      },
    },
    // Desktop
    {
      name: 'Desktop Chrome',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

## Unit Test Examples

### Composable Test
```typescript
// tests/unit/composables/useTask.spec.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useTask } from '@/composables/useTask'
import { useTaskStore } from '@/stores/tasks'
import { createPinia, setActivePinia } from 'pinia'

describe('useTask', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should claim task successfully', async () => {
    const { claimTask } = useTask()
    const taskStore = useTaskStore()
    
    vi.spyOn(taskStore, 'claimTask').mockResolvedValue({
      id: 1,
      status: 'claimed'
    })

    await claimTask(1, 'worker-1')
    
    expect(taskStore.claimTask).toHaveBeenCalledWith(1, 'worker-1')
  })

  it('should handle claim error', async () => {
    const { claimTask } = useTask()
    const taskStore = useTaskStore()
    
    vi.spyOn(taskStore, 'claimTask').mockRejectedValue(
      new Error('Failed to claim')
    )

    await expect(claimTask(1, 'worker-1')).rejects.toThrow()
  })
})
```

### Store Test
```typescript
// tests/unit/stores/tasks.spec.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTaskStore } from '@/stores/tasks'
import { taskService } from '@/services/tasks'

vi.mock('@/services/tasks')

describe('Task Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should fetch tasks', async () => {
    const store = useTaskStore()
    const mockTasks = [
      { id: 1, status: 'pending' },
      { id: 2, status: 'claimed' }
    ]
    
    vi.mocked(taskService.list).mockResolvedValue(mockTasks)

    await store.fetchTasks()
    
    expect(store.tasks).toEqual(mockTasks)
    expect(store.loading).toBe(false)
  })

  it('should handle fetch error', async () => {
    const store = useTaskStore()
    
    vi.mocked(taskService.list).mockRejectedValue(
      new Error('API Error')
    )

    await expect(store.fetchTasks()).rejects.toThrow()
    expect(store.error).toBeTruthy()
  })

  it('should filter pending tasks', () => {
    const store = useTaskStore()
    store.tasks = [
      { id: 1, status: 'pending' },
      { id: 2, status: 'claimed' },
      { id: 3, status: 'pending' }
    ]

    expect(store.pendingTasks).toHaveLength(2)
  })
})
```

## Component Test Examples

### Button Component Test
```typescript
// tests/unit/components/Button.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/base/Button.vue'

describe('Button', () => {
  it('renders slot content', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Click Me'
      }
    })
    expect(wrapper.text()).toContain('Click Me')
  })

  it('emits click event', async () => {
    const wrapper = mount(Button)
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('shows loading spinner when loading', () => {
    const wrapper = mount(Button, {
      props: { loading: true }
    })
    expect(wrapper.find('.spinner').exists()).toBe(true)
  })

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(Button, {
      props: { disabled: true }
    })
    expect(wrapper.element.disabled).toBe(true)
  })

  it('applies correct variant class', () => {
    const wrapper = mount(Button, {
      props: { variant: 'primary' }
    })
    expect(wrapper.classes()).toContain('btn-primary')
  })
})
```

### TaskCard Component Test
```typescript
// tests/unit/components/TaskCard.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TaskCard from '@/components/tasks/TaskCard.vue'

describe('TaskCard', () => {
  const mockTask = {
    id: 1,
    task_type: 'test',
    status: 'pending',
    progress: 0,
    created_at: '2025-11-09T12:00:00Z'
  }

  it('displays task information', () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask }
    })
    expect(wrapper.text()).toContain('test')
  })

  it('shows claim button for pending tasks', () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask }
    })
    expect(wrapper.find('[data-test="claim-btn"]').exists()).toBe(true)
  })

  it('emits claim event when claim button clicked', async () => {
    const wrapper = mount(TaskCard, {
      props: { task: mockTask }
    })
    await wrapper.find('[data-test="claim-btn"]').trigger('click')
    expect(wrapper.emitted('claim')).toBeTruthy()
    expect(wrapper.emitted('claim')[0]).toEqual([mockTask])
  })

  it('shows complete button for claimed tasks', () => {
    const claimedTask = { ...mockTask, status: 'claimed' }
    const wrapper = mount(TaskCard, {
      props: { task: claimedTask }
    })
    expect(wrapper.find('[data-test="complete-btn"]').exists()).toBe(true)
  })
})
```

## E2E Test Examples

### Task Claiming Flow
```typescript
// tests/e2e/task-claiming.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Task Claiming Flow', () => {
  test('should claim a task successfully', async ({ page }) => {
    await page.goto('/')
    
    // Wait for tasks to load
    await page.waitForSelector('[data-test="task-card"]')
    
    // Get first pending task
    const firstTask = page.locator('[data-test="task-card"]').first()
    
    // Click claim button
    await firstTask.locator('[data-test="claim-btn"]').click()
    
    // Verify success toast
    await expect(page.locator('[data-test="toast"]')).toContainText('Task claimed')
    
    // Verify task moved to claimed section
    await page.click('[data-test="claimed-tab"]')
    await expect(firstTask).toBeVisible()
  })

  test('should handle claim error gracefully', async ({ page }) => {
    // Mock API to return error
    await page.route('**/tasks/*/claim', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Server error' })
      })
    })

    await page.goto('/')
    await page.waitForSelector('[data-test="task-card"]')
    
    await page.locator('[data-test="claim-btn"]').first().click()
    
    // Verify error toast
    await expect(page.locator('[data-test="toast"]')).toContainText('Failed')
  })
})
```

### Mobile Viewport Test
```typescript
// tests/e2e/mobile-navigation.spec.ts
import { test, expect, devices } from '@playwright/test'

test.use({ ...devices['Pixel 5'] })

test.describe('Mobile Navigation', () => {
  test('should navigate using bottom tab bar', async ({ page }) => {
    await page.goto('/')
    
    // Verify bottom navigation visible
    const bottomNav = page.locator('[data-test="bottom-nav"]')
    await expect(bottomNav).toBeVisible()
    
    // Click worker dashboard tab
    await bottomNav.locator('[data-test="workers-tab"]').click()
    
    // Verify navigation
    await expect(page).toHaveURL(/\/workers/)
    await expect(page.locator('h1')).toContainText('Workers')
  })

  test('should have touch-friendly targets', async ({ page }) => {
    await page.goto('/')
    
    // Check button size
    const button = page.locator('[data-test="claim-btn"]').first()
    const box = await button.boundingBox()
    
    expect(box.height).toBeGreaterThanOrEqual(44)
    expect(box.width).toBeGreaterThanOrEqual(44)
  })
})
```

### Accessibility Test
```typescript
// tests/e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility', () => {
  test('should not have accessibility violations', async ({ page }) => {
    await page.goto('/')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/')
    
    // Tab through interactive elements
    await page.keyboard.press('Tab')
    await expect(page.locator(':focus')).toBeVisible()
    
    // Press Enter on focused button
    await page.keyboard.press('Enter')
    // Verify action
  })
})
```

## Coverage Requirements

### Overall Coverage
- **Statements**: > 80%
- **Branches**: > 80%
- **Functions**: > 80%
- **Lines**: > 80%

### Critical Paths
- Task operations: > 90%
- API services: > 85%
- Stores: > 85%
- Composables: > 80%

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run test:unit -- --coverage
      - run: npm run test:e2e
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

## Timeline
- **Start**: After ISSUE-FRONTEND-004 (Core Components) ready
- **Duration**: Throughout development + 3-4 days final
- **Target**: Week 3
- **Parallel with**: Worker04 (Performance), Worker06 (Documentation)

## Success Criteria
- ✅ > 80% test coverage
- ✅ All critical flows tested
- ✅ Mobile viewport tests passing
- ✅ Accessibility tests passing
- ✅ CI/CD integrated
- ✅ All tests passing
- ✅ Documentation complete

## Notes
- Write tests as features are developed
- Test on real mobile devices when possible
- Include accessibility from the start
- Monitor test performance (< 5min total)
- Keep tests maintainable and readable

---

**Created By**: Worker01 (Project Manager)  
**Date**: 2025-11-09  
**Assigned To**: Worker07 (Testing & QA Specialist)  
**Status**: 🔴 NOT STARTED  
**Priority**: High (quality gate)
