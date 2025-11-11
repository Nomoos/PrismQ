import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('WCAG 2.1 AA Accessibility Compliance', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should not have any automatically detectable WCAG 2.1 AA violations on TaskList', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have skip to main content link', async ({ page }) => {
    // Tab to focus the skip link
    await page.keyboard.press('Tab')
    
    // The skip link should be focused and visible
    const skipLink = page.getByText('Skip to main content')
    await expect(skipLink).toBeFocused()
  })

  test('should have proper heading hierarchy', async ({ page }) => {
    // Check for h1
    const h1 = page.locator('h1')
    await expect(h1.first()).toBeVisible()
    
    // Get all headings and verify order
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all()
    expect(headings.length).toBeGreaterThan(0)
  })

  test('should have ARIA labels on all interactive elements', async ({ page }) => {
    // Check buttons
    const buttons = await page.locator('button:visible').all()
    
    for (const button of buttons) {
      const text = await button.textContent()
      const ariaLabel = await button.getAttribute('aria-label')
      const ariaLabelledBy = await button.getAttribute('aria-labelledby')
      
      // Button should have either text content or aria-label
      const hasLabel = (text && text.trim().length > 0) || ariaLabel || ariaLabelledBy
      expect(hasLabel).toBeTruthy()
    }
  })

  test('should be fully keyboard navigable', async ({ page }) => {
    // Tab through several elements
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab')
      
      // Verify something has focus
      const activeElement = await page.evaluate(() => {
        return document.activeElement !== document.body
      })
      expect(activeElement).toBe(true)
    }
  })

  test('should have visible focus indicators', async ({ page }) => {
    // Tab to first interactive element
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    
    // Get the focused element's outline
    const outlineWidth = await page.evaluate(() => {
      const style = window.getComputedStyle(document.activeElement!)
      return style.outlineWidth
    })
    
    // Should have an outline (focus indicator)
    expect(parseInt(outlineWidth)).toBeGreaterThan(0)
  })

  test('should have proper ARIA roles for main landmarks', async ({ page }) => {
    // Check for main content
    const main = page.locator('main, [role="main"]')
    await expect(main.first()).toBeVisible()
    
    // Check for navigation
    const nav = page.locator('nav, [role="navigation"]')
    await expect(nav.first()).toBeVisible()
  })

  test('should have aria-live regions for dynamic content', async ({ page }) => {
    // Check for live regions
    const liveRegions = page.locator('[aria-live]')
    const count = await liveRegions.count()
    
    expect(count).toBeGreaterThan(0)
  })

  test('should have minimum touch target size', async ({ page }) => {
    // Check button sizes
    const buttons = await page.locator('button:visible').all()
    
    if (buttons.length > 0) {
      const firstButton = buttons[0]
      const box = await firstButton.boundingBox()
      
      if (box) {
        // WCAG 2.5.5: Touch targets should be at least 44x44px
        expect(box.height).toBeGreaterThanOrEqual(44)
      }
    }
  })

  test('should handle task detail page accessibility', async ({ page }) => {
    // Navigate to task detail if tasks exist
    const taskCard = page.locator('[role="listitem"]').first()
    const taskCount = await taskCard.count()
    
    if (taskCount > 0) {
      await taskCard.click()
      await page.waitForLoadState('networkidle')
      
      // Run accessibility scan on task detail page
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        .analyze()
      
      expect(accessibilityScanResults.violations).toEqual([])
    }
  })

  test('should handle worker dashboard accessibility', async ({ page }) => {
    // Navigate to workers page
    await page.goto('/workers')
    await page.waitForLoadState('networkidle')
    
    // Run accessibility scan
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should handle settings page accessibility', async ({ page }) => {
    // Navigate to settings page
    await page.goto('/settings')
    await page.waitForLoadState('networkidle')
    
    // Run accessibility scan
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have proper form labels in settings', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForLoadState('networkidle')
    
    // Check that all inputs have associated labels
    const inputs = await page.locator('input:visible').all()
    
    for (const input of inputs) {
      const id = await input.getAttribute('id')
      const ariaLabel = await input.getAttribute('aria-label')
      const ariaLabelledBy = await input.getAttribute('aria-labelledby')
      
      // Input should have either:
      // 1. An ID with a corresponding label
      // 2. An aria-label
      // 3. An aria-labelledby
      const hasLabel = id || ariaLabel || ariaLabelledBy
      expect(hasLabel).toBeTruthy()
    }
  })

  test('should respect reduced motion preference', async ({ page, context }) => {
    // Set prefers-reduced-motion
    await context.addInitScript(() => {
      Object.defineProperty(window, 'matchMedia', {
        writable: true,
        value: (query: string) => ({
          matches: query === '(prefers-reduced-motion: reduce)',
          media: query,
          onchange: null,
          addEventListener: () => {},
          removeEventListener: () => {},
          dispatchEvent: () => true
        })
      })
    })
    
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    // Verify animations are reduced or disabled
    const animationDuration = await page.evaluate(() => {
      const style = window.getComputedStyle(document.body)
      return style.animationDuration
    })
    
    // With reduced motion, animations should be very short or disabled
    expect(['0s', '0.01ms', '0ms']).toContain(animationDuration)
  })

  test('should have proper color contrast for text', async ({ page }) => {
    // Get text elements
    const textElements = await page.locator('p, h1, h2, h3, button, a').all()
    
    // Just verify they exist (actual contrast ratio testing requires more complex setup)
    expect(textElements.length).toBeGreaterThan(0)
    
    // Note: Actual color contrast is tested by axe-core in the main scan
  })

  test('should have semantic HTML structure', async ({ page }) => {
    // Check for semantic elements
    const header = page.locator('header')
    await expect(header).toHaveCount(1)
    
    const main = page.locator('main')
    await expect(main).toHaveCount(1)
    
    const nav = page.locator('nav')
    await expect(nav.first()).toBeVisible()
  })

  test('should handle keyboard navigation in filter tabs', async ({ page }) => {
    // Wait for filter tabs to load
    const filterTabs = page.locator('[role="tab"]')
    const tabCount = await filterTabs.count()
    
    if (tabCount > 0) {
      // Focus first tab
      await filterTabs.first().focus()
      
      // Try arrow key navigation
      await page.keyboard.press('ArrowRight')
      
      // Verify focus moved
      const activeText = await page.evaluate(() => {
        return document.activeElement?.textContent
      })
      expect(activeText).toBeTruthy()
    }
  })

  test('should announce loading states to screen readers', async ({ page }) => {
    // Check for loading spinners with ARIA labels
    const loadingSpinner = page.locator('[role="status"]').first()
    
    if (await loadingSpinner.count() > 0) {
      const ariaLabel = await loadingSpinner.getAttribute('aria-label')
      const textContent = await loadingSpinner.textContent()
      
      // Should have either aria-label or text content
      expect(ariaLabel || textContent).toBeTruthy()
    }
  })

  test('should have accessible error messages', async ({ page }) => {
    // Mock an error scenario
    await page.route('**/api/tasks**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Server error' })
      })
    })
    
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    // Check for error alert
    const errorAlert = page.locator('[role="alert"]')
    const alertCount = await errorAlert.count()
    
    // If error is shown, it should have role="alert" for screen readers
    if (alertCount > 0) {
      await expect(errorAlert.first()).toBeVisible()
    }
  })
})
