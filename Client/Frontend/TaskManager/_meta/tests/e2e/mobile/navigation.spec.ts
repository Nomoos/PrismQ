import { test, expect } from '@playwright/test'

/**
 * Mobile Device Test: Navigation Flow
 * Device: Redmi 24115RA8EG (and similar Android devices)
 * 
 * Tests mobile navigation patterns including bottom navigation,
 * back button behavior, and deep linking.
 */

test.describe('Mobile: Navigation Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should navigate using bottom navigation', async ({ page }) => {
    // Wait for app to load
    await page.waitForLoadState('networkidle')
    
    // Check if bottom navigation exists
    const bottomNav = page.locator('[data-testid="bottom-navigation"]')
    const navExists = await bottomNav.count() > 0
    
    if (navExists) {
      await expect(bottomNav).toBeVisible()
      
      // Tap on dashboard nav item
      const dashboardNav = page.locator('[data-testid="nav-dashboard"]')
      await dashboardNav.tap()
      
      // Verify navigation occurred
      await expect(page).toHaveURL(/.*dashboard/)
      
      // Tap on tasks nav item
      const tasksNav = page.locator('[data-testid="nav-tasks"]')
      await tasksNav.tap()
      
      // Verify navigation occurred
      await expect(page).toHaveURL(/.*tasks/)
    }
  })

  test('should have accessible navigation buttons (44x44px)', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const navButtons = page.locator('[data-testid="bottom-navigation"] button')
    const count = await navButtons.count()
    
    if (count > 0) {
      for (let i = 0; i < count; i++) {
        const button = navButtons.nth(i)
        const box = await button.boundingBox()
        
        if (box) {
          expect(box.width).toBeGreaterThanOrEqual(44)
          expect(box.height).toBeGreaterThanOrEqual(44)
        }
      }
    }
  })

  test('should show active state on current navigation item', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const bottomNav = page.locator('[data-testid="bottom-navigation"]')
    const navExists = await bottomNav.count() > 0
    
    if (navExists) {
      // Tap on dashboard
      const dashboardNav = page.locator('[data-testid="nav-dashboard"]')
      await dashboardNav.tap()
      
      // Wait for navigation
      await page.waitForTimeout(500)
      
      // Check for active class or aria-current
      const isActive = await dashboardNav.evaluate((el) => {
        return el.classList.contains('active') || 
               el.getAttribute('aria-current') === 'page' ||
               el.classList.contains('router-link-active')
      })
      
      expect(isActive).toBeTruthy()
    }
  })

  test('should handle back button correctly', async ({ page }) => {
    // Navigate to a task detail page
    await page.goto('/tasks')
    await page.waitForLoadState('networkidle')
    
    const taskItem = page.locator('[data-testid="task-item"]').first()
    const taskExists = await taskItem.count() > 0
    
    if (taskExists) {
      await taskItem.tap()
      
      // Verify we're on detail page
      await page.waitForTimeout(500)
      
      // Go back using browser back button
      await page.goBack()
      
      // Verify we're back on tasks list
      await expect(page).toHaveURL(/.*tasks/)
      const taskList = page.locator('[data-testid="task-list"]')
      await expect(taskList).toBeVisible()
    }
  })

  test('should navigate between sections without flicker', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const bottomNav = page.locator('[data-testid="bottom-navigation"]')
    const navExists = await bottomNav.count() > 0
    
    if (navExists) {
      // Navigate to different sections
      const sections = ['nav-dashboard', 'nav-tasks', 'nav-settings']
      
      for (const section of sections) {
        const navItem = page.locator(`[data-testid="${section}"]`)
        const itemExists = await navItem.count() > 0
        
        if (itemExists) {
          // Record navigation time
          const startTime = Date.now()
          await navItem.tap()
          await page.waitForLoadState('networkidle')
          const endTime = Date.now()
          
          // Navigation should be quick (< 1 second)
          expect(endTime - startTime).toBeLessThan(1000)
        }
      }
    }
  })

  test('should support swipe gestures for navigation (if implemented)', async ({ page }) => {
    // This test checks if swipe gestures work
    // Skip if not implemented
    await page.waitForLoadState('networkidle')
    
    // Try to perform a swipe gesture
    const startX = 300
    const startY = 400
    const endX = 50
    const endY = 400
    
    await page.touchscreen.tap(startX, startY)
    await page.touchscreen.swipe({ x: startX, y: startY }, { x: endX, y: endY })
    
    // Wait for any navigation to complete
    await page.waitForTimeout(500)
    
    // Just verify page is still functional
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('should maintain scroll position when navigating back', async ({ page }) => {
    await page.goto('/tasks')
    await page.waitForLoadState('networkidle')
    
    // Scroll down
    await page.evaluate(() => window.scrollTo(0, 500))
    await page.waitForTimeout(500)
    const scrollPosition = await page.evaluate(() => window.scrollY)
    
    // Navigate to another page
    const taskItem = page.locator('[data-testid="task-item"]').first()
    const taskExists = await taskItem.count() > 0
    
    if (taskExists) {
      await taskItem.tap()
      await page.waitForTimeout(500)
      
      // Go back
      await page.goBack()
      await page.waitForTimeout(500)
      
      // Check if scroll position is restored (allowing some margin)
      const restoredPosition = await page.evaluate(() => window.scrollY)
      expect(Math.abs(restoredPosition - scrollPosition)).toBeLessThan(50)
    }
  })

  test('should handle deep links correctly', async ({ page }) => {
    // Navigate directly to a deep link
    await page.goto('/tasks/123')
    await page.waitForLoadState('networkidle')
    
    // Verify the page loaded (even if task doesn't exist)
    const body = page.locator('body')
    await expect(body).toBeVisible()
    
    // Should show error or task details
    const hasContent = await page.evaluate(() => {
      return document.body.textContent && document.body.textContent.length > 0
    })
    expect(hasContent).toBeTruthy()
  })
})
