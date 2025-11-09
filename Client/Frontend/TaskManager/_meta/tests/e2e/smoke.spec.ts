import { test, expect } from '@playwright/test'

/**
 * Smoke Test - Basic Mobile Functionality
 * 
 * This test verifies basic app loading and navigation on mobile devices.
 * These tests use generic selectors since test-specific data attributes
 * may not be implemented yet.
 */

test.describe('Smoke Test: Basic Mobile Functionality', () => {
  test('should load the application on mobile device', async ({ page }) => {
    await page.goto('/')
    
    // Wait for page to load
    await page.waitForLoadState('networkidle')
    
    // Verify page loaded
    const body = page.locator('body')
    await expect(body).toBeVisible()
    
    // Check if app has rendered content
    const hasContent = await page.evaluate(() => {
      return document.body.textContent && document.body.textContent.length > 0
    })
    
    expect(hasContent).toBeTruthy()
  })

  test('should have viewport meta tag for mobile', async ({ page }) => {
    await page.goto('/')
    
    const viewportMeta = await page.evaluate(() => {
      const meta = document.querySelector('meta[name="viewport"]')
      return meta ? meta.getAttribute('content') : null
    })
    
    // Should have viewport meta tag
    expect(viewportMeta).toBeTruthy()
    
    // Should contain width=device-width
    if (viewportMeta) {
      expect(viewportMeta).toContain('width=device-width')
    }
  })

  test('should be responsive (no horizontal scroll)', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth
    })
    
    expect(hasHorizontalScroll).toBe(false)
  })

  test('should have a title', async ({ page }) => {
    await page.goto('/')
    
    const title = await page.title()
    
    expect(title).toBeTruthy()
    expect(title.length).toBeGreaterThan(0)
  })

  test('should load in under 5 seconds', async ({ page }) => {
    const startTime = Date.now()
    
    await page.goto('/', { waitUntil: 'load' })
    
    const loadTime = Date.now() - startTime
    
    // Should load in under 5 seconds (generous for initial setup)
    expect(loadTime).toBeLessThan(5000)
  })

  test('should have clickable elements with adequate size', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Find all buttons
    const buttons = await page.locator('button').all()
    
    if (buttons.length > 0) {
      for (const button of buttons.slice(0, 5)) {
        const box = await button.boundingBox()
        
        if (box) {
          // Buttons should be at least 40x40px (close to 44x44px target)
          expect(box.width).toBeGreaterThanOrEqual(40)
          expect(box.height).toBeGreaterThanOrEqual(40)
        }
      }
    }
  })

  test('should navigate between pages', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Try to find navigation links
    const links = await page.locator('a[href]').all()
    
    if (links.length > 0) {
      // Click first navigation link
      const firstLink = links[0]
      await firstLink.click()
      
      // Wait for navigation
      await page.waitForLoadState('networkidle')
      
      // Verify we're still on the site
      const body = page.locator('body')
      await expect(body).toBeVisible()
    }
  })
})

/**
 * NOTE: To run the full test suite, the following data-testid attributes
 * should be added to the components:
 * 
 * TaskList.vue:
 * - data-testid="task-list" on the task container
 * - data-testid="task-item" on each task card
 * 
 * TaskDetail.vue:
 * - data-testid="task-details" on the detail container
 * - data-testid="claim-button" on the claim button
 * 
 * Common:
 * - data-testid="bottom-navigation" on the navigation container
 * - data-testid="nav-dashboard", "nav-tasks", "nav-settings" on nav items
 * - data-testid="success-message" on success notifications
 * - data-testid="my-tasks-nav" on the my tasks navigation
 * - data-testid="claimed-task" on claimed task items
 * 
 * See the comprehensive test files in:
 * - mobile/task-claiming.spec.ts
 * - mobile/navigation.spec.ts
 * - mobile/touch-interactions.spec.ts
 */
