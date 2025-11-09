import { test, expect } from '@playwright/test'

/**
 * Mobile Device Test: Task Claiming Flow
 * Device: Redmi 24115RA8EG (and similar Android devices)
 * 
 * Tests the complete task claiming flow on mobile devices,
 * ensuring proper touch interactions, responsive layout,
 * and mobile-friendly UX.
 */

test.describe('Mobile: Task Claiming Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should load and display task list on mobile device', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForSelector('[data-testid="task-list"]', { timeout: 5000 })
    
    // Verify task list is visible
    const taskList = page.locator('[data-testid="task-list"]')
    await expect(taskList).toBeVisible()
    
    // Verify at least one task is displayed
    const tasks = page.locator('[data-testid="task-item"]')
    await expect(tasks.first()).toBeVisible()
  })

  test('should have adequate touch targets (44x44px minimum)', async ({ page }) => {
    await page.waitForSelector('[data-testid="task-item"]', { timeout: 5000 })
    
    // Get the first task item
    const taskItem = page.locator('[data-testid="task-item"]').first()
    const boundingBox = await taskItem.boundingBox()
    
    // Verify minimum touch target size (44x44 CSS pixels)
    expect(boundingBox).not.toBeNull()
    if (boundingBox) {
      expect(boundingBox.height).toBeGreaterThanOrEqual(44)
      // Width should be at least 44px for tappable elements
      const tappableElements = await taskItem.locator('button, a').all()
      for (const element of tappableElements) {
        const box = await element.boundingBox()
        if (box) {
          expect(box.width).toBeGreaterThanOrEqual(44)
          expect(box.height).toBeGreaterThanOrEqual(44)
        }
      }
    }
  })

  test('should claim a task with touch interaction', async ({ page }) => {
    await page.waitForSelector('[data-testid="task-item"]', { timeout: 5000 })
    
    // Tap on first available task
    const taskItem = page.locator('[data-testid="task-item"]').first()
    await taskItem.tap()
    
    // Wait for task details to appear
    await page.waitForSelector('[data-testid="task-details"]', { timeout: 3000 })
    
    // Tap the claim button
    const claimButton = page.locator('[data-testid="claim-button"]')
    await expect(claimButton).toBeVisible()
    await claimButton.tap()
    
    // Verify success feedback
    const successMessage = page.locator('[data-testid="success-message"]')
    await expect(successMessage).toBeVisible({ timeout: 3000 })
    
    // Verify task moved to "My Tasks"
    await page.locator('[data-testid="my-tasks-nav"]').tap()
    await expect(page.locator('[data-testid="claimed-task"]').first()).toBeVisible()
  })

  test('should handle scrolling smoothly on mobile', async ({ page }) => {
    await page.waitForSelector('[data-testid="task-list"]', { timeout: 5000 })
    
    // Get initial scroll position
    const initialScroll = await page.evaluate(() => window.scrollY)
    
    // Perform scroll gesture
    await page.mouse.wheel(0, 500)
    await page.waitForTimeout(500) // Wait for scroll to complete
    
    // Verify scroll happened
    const finalScroll = await page.evaluate(() => window.scrollY)
    expect(finalScroll).toBeGreaterThan(initialScroll)
  })

  test('should provide clear visual feedback on tap', async ({ page }) => {
    await page.waitForSelector('[data-testid="task-item"]', { timeout: 5000 })
    
    const taskItem = page.locator('[data-testid="task-item"]').first()
    
    // Check for hover/active states (CSS)
    await taskItem.tap()
    
    // Take screenshot to verify visual feedback
    await page.screenshot({ 
      path: 'Frontend/TaskManager/_meta/tests/e2e-results/mobile-tap-feedback.png' 
    })
  })

  test('should work in portrait orientation', async ({ page }) => {
    // Already in portrait by default for mobile devices
    await page.waitForSelector('[data-testid="task-list"]', { timeout: 5000 })
    
    // Verify layout is appropriate for portrait
    const viewport = page.viewportSize()
    expect(viewport).not.toBeNull()
    if (viewport) {
      expect(viewport.height).toBeGreaterThan(viewport.width)
    }
    
    const taskList = page.locator('[data-testid="task-list"]')
    await expect(taskList).toBeVisible()
  })

  test('should work in landscape orientation', async ({ page, browserName }) => {
    // Skip for desktop browsers
    test.skip(browserName === 'chromium' && !page.context().browser()?.version().includes('Mobile'))
    
    // Rotate to landscape
    await page.setViewportSize({ width: 851, height: 393 })
    
    await page.goto('/')
    await page.waitForSelector('[data-testid="task-list"]', { timeout: 5000 })
    
    // Verify layout adapts to landscape
    const taskList = page.locator('[data-testid="task-list"]')
    await expect(taskList).toBeVisible()
  })

  test('should not have horizontal scroll', async ({ page }) => {
    await page.waitForSelector('[data-testid="task-list"]', { timeout: 5000 })
    
    // Check for horizontal overflow
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth
    })
    
    expect(hasHorizontalScroll).toBe(false)
  })

  test('should display content without being cut off', async ({ page }) => {
    await page.waitForSelector('[data-testid="task-item"]', { timeout: 5000 })
    
    // Verify all task items fit within viewport width
    const taskItems = await page.locator('[data-testid="task-item"]').all()
    const viewportWidth = page.viewportSize()?.width || 0
    
    for (const item of taskItems.slice(0, 3)) { // Check first 3 items
      const box = await item.boundingBox()
      if (box) {
        expect(box.x + box.width).toBeLessThanOrEqual(viewportWidth)
      }
    }
  })
})
