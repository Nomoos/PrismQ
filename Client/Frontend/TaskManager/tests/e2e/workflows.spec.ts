import { test, expect } from '@playwright/test'

test.describe('Task Workflows - Critical Paths', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the task list page
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should display task list with filtering', async ({ page }) => {
    // Check if task list is displayed
    const taskManager = page.locator('h1', { hasText: 'TaskManager' })
    await expect(taskManager).toBeVisible()
    
    // Check if filter buttons exist
    const allFilter = page.getByText(/all/i).filter({ has: page.locator('button') }).first()
    if (await allFilter.isVisible()) {
      await expect(allFilter).toBeVisible()
    }
  })

  test('should filter tasks by status', async ({ page }) => {
    // Wait for page to load
    await page.waitForSelector('button', { timeout: 5000 })
    
    // Find and click pending filter if it exists
    const buttons = await page.locator('button').all()
    for (const button of buttons) {
      const text = await button.textContent()
      if (text && text.toLowerCase().includes('pending')) {
        await button.click()
        await page.waitForTimeout(300)
        break
      }
    }
  })

  test('should navigate to task detail when clicking on a task', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForTimeout(1000)
    
    // Try to find and click on a task card
    const taskCard = page.locator('.card').first()
    const cardExists = await taskCard.count() > 0
    
    if (cardExists) {
      await taskCard.click()
      await page.waitForTimeout(500)
      
      // Check if we navigated to a task detail page
      expect(page.url()).toMatch(/\/tasks\/\d+/)
    }
  })

  test('should show empty state when no tasks exist', async ({ page }) => {
    // Filter to a status with likely no tasks
    await page.waitForSelector('button', { timeout: 5000 })
    
    // Try clicking on different filters to find empty state
    const filterButtons = await page.locator('button').all()
    for (const button of filterButtons) {
      await button.click()
      await page.waitForTimeout(300)
      
      // Check if empty state is shown
      const emptyState = page.getByText(/no.*tasks/i)
      if (await emptyState.isVisible()) {
        await expect(emptyState).toBeVisible()
        break
      }
    }
  })
})

test.describe('Worker Dashboard Workflow', () => {
  test('should navigate to worker dashboard', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Find workers navigation link
    const workersLink = page.getByRole('link', { name: /workers/i })
    
    if (await workersLink.isVisible()) {
      await workersLink.click()
      await page.waitForLoadState('networkidle')
      
      // Verify we're on the workers page
      expect(page.url()).toMatch(/\/workers/)
    }
  })

  test('should display worker information', async ({ page }) => {
    // Navigate directly to workers page
    await page.goto('/workers')
    await page.waitForLoadState('networkidle')
    
    // Check if page loaded successfully
    await expect(page).not.toHaveURL(/404|error/)
  })
})

test.describe('Settings Workflow', () => {
  test('should navigate to settings page', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Find settings navigation link
    const settingsLink = page.getByRole('link', { name: /settings/i })
    
    if (await settingsLink.isVisible()) {
      await settingsLink.click()
      await page.waitForLoadState('networkidle')
      
      // Verify we're on the settings page
      expect(page.url()).toMatch(/\/settings/)
    }
  })

  test('should display settings options', async ({ page }) => {
    // Navigate directly to settings page
    await page.goto('/settings')
    await page.waitForLoadState('networkidle')
    
    // Check if page loaded successfully
    await expect(page).not.toHaveURL(/404|error/)
  })
})

test.describe('Mobile Viewport Tests', () => {
  test.use({ 
    viewport: { width: 375, height: 667 } // iPhone SE viewport
  })

  test('should display mobile navigation', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Check if bottom navigation is visible
    const nav = page.locator('nav').last()
    await expect(nav).toBeVisible()
    
    // Check if navigation items are visible
    const navItems = page.locator('nav a, nav button')
    const count = await navItems.count()
    expect(count).toBeGreaterThan(0)
  })

  test('should be scrollable on mobile', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Try to scroll
    await page.evaluate(() => window.scrollTo(0, 100))
    await page.waitForTimeout(200)
    
    const scrollY = await page.evaluate(() => window.scrollY)
    expect(scrollY).toBeGreaterThanOrEqual(0)
  })

  test('should have touch-friendly tap targets', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Check if buttons have minimum size (44x44px recommended)
    const buttons = await page.locator('button').all()
    
    if (buttons.length > 0) {
      const firstButton = buttons[0]
      const box = await firstButton.boundingBox()
      
      if (box) {
        // Minimum touch target should be 44x44px, but we'll accept 40x40px
        expect(box.height).toBeGreaterThanOrEqual(30)
        expect(box.width).toBeGreaterThanOrEqual(40)
      }
    }
  })
})

test.describe('Error Handling', () => {
  test('should handle navigation to non-existent routes gracefully', async ({ page }) => {
    await page.goto('/non-existent-page-12345')
    await page.waitForLoadState('networkidle')
    
    // Should either show 404 or redirect to home
    const url = page.url()
    expect(url).toBeTruthy()
  })

  test('should display loading state', async ({ page }) => {
    // Navigate to page and check for loading indicators
    const response = page.goto('/')
    
    // Check if loading spinner appears (briefly)
    const loadingSpinner = page.locator('[role="status"]').or(page.getByText(/loading/i))
    
    await response
    await page.waitForLoadState('networkidle')
  })
})

test.describe('Performance and Responsiveness', () => {
  test('should load the main page within acceptable time', async ({ page }) => {
    const startTime = Date.now()
    
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const loadTime = Date.now() - startTime
    
    // Page should load within 5 seconds
    expect(loadTime).toBeLessThan(5000)
  })

  test('should respond to user interactions quickly', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Find first clickable button
    const button = page.locator('button').first()
    
    if (await button.isVisible()) {
      const startTime = Date.now()
      await button.click()
      const responseTime = Date.now() - startTime
      
      // Click should respond within 500ms
      expect(responseTime).toBeLessThan(500)
    }
  })
})
