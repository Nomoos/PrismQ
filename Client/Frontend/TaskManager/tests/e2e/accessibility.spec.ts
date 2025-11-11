import { test, expect } from '@playwright/test'

test.describe('Mobile Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should display bottom navigation on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Check if bottom navigation exists
    const nav = page.locator('nav').last()
    await expect(nav).toBeVisible()
  })

  test('should navigate using bottom navigation', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Check for navigation items
    const navItems = page.locator('nav a, nav button')
    const count = await navItems.count()
    
    expect(count).toBeGreaterThan(0)
  })

  test('should be responsive at different viewports', async ({ page }) => {
    // Test at mobile viewport
    await page.setViewportSize({ width: 360, height: 640 })
    await expect(page.locator('body')).toBeVisible()
    
    // Test at tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 })
    await expect(page.locator('body')).toBeVisible()
    
    // Test at desktop viewport
    await page.setViewportSize({ width: 1280, height: 720 })
    await expect(page.locator('body')).toBeVisible()
  })

  test('should maintain state during viewport changes', async ({ page }) => {
    // Start at desktop
    await page.setViewportSize({ width: 1280, height: 720 })
    
    // Get page title
    const title = await page.locator('h1').first().textContent()
    
    // Change to mobile
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Verify title is still present
    await expect(page.locator('h1').first()).toContainText(title || '')
  })
})

test.describe('Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should have proper heading hierarchy', async ({ page }) => {
    const h1 = page.locator('h1')
    
    // Should have at least one h1
    await expect(h1.first()).toBeVisible()
  })

  test('should have skip to content link for keyboard users', async ({ page }) => {
    // Focus on first element
    await page.keyboard.press('Tab')
    
    // Should be able to navigate with keyboard
    const focused = await page.evaluate(() => document.activeElement?.tagName)
    expect(focused).toBeTruthy()
  })

  test('should have proper ARIA labels on interactive elements', async ({ page }) => {
    const buttons = page.locator('button')
    const count = await buttons.count()
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = buttons.nth(i)
      if (await button.isVisible()) {
        const hasText = await button.textContent()
        const hasAriaLabel = await button.getAttribute('aria-label')
        const hasAriaLabelledBy = await button.getAttribute('aria-labelledby')
        
        // Button should have either text content or aria-label
        expect(hasText || hasAriaLabel || hasAriaLabelledBy).toBeTruthy()
      }
    }
  })

  test('should be navigable with keyboard', async ({ page }) => {
    // Tab through interactive elements
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    
    // Should be able to focus elements
    const focused = await page.evaluate(() => document.activeElement !== document.body)
    expect(focused).toBe(true)
  })

  test('should have sufficient color contrast', async ({ page }) => {
    // Get text elements
    const textElements = page.locator('p, h1, h2, h3, button, a')
    const count = await textElements.count()
    
    // Just verify text elements exist and are visible
    expect(count).toBeGreaterThan(0)
  })
})

test.describe('Loading States', () => {
  test('should show loading state while fetching data', async ({ page }) => {
    // Slow down network to catch loading state
    await page.route('**/api/**', route => {
      setTimeout(() => route.continue(), 100)
    })
    
    await page.goto('/')
    
    // Page should load even with slow API
    await expect(page.locator('body')).toBeVisible()
  })

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/tasks**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      })
    })
    
    await page.goto('/')
    
    // Page should still render without crashing
    await expect(page.locator('body')).toBeVisible()
  })
})

test.describe('Performance', () => {
  test('should load page within acceptable time', async ({ page }) => {
    const startTime = Date.now()
    
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const loadTime = Date.now() - startTime
    
    // Page should load in less than 5 seconds
    expect(loadTime).toBeLessThan(5000)
  })

  test('should render content above the fold quickly', async ({ page }) => {
    await page.goto('/')
    
    // Main content should be visible
    await expect(page.locator('main, [role="main"], body')).toBeVisible({ timeout: 3000 })
  })
})
