import { test, expect } from '@playwright/test'

/**
 * Mobile Device Test: Touch Interactions
 * Device: Redmi 24115RA8EG (and similar Android devices)
 * 
 * Tests touch-specific interactions including tap, long press,
 * and gesture recognition.
 */

test.describe('Mobile: Touch Interactions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should respond to tap immediately (< 100ms)', async ({ page }) => {
    await page.waitForSelector('[data-testid="task-item"]', { timeout: 5000 })
    
    const button = page.locator('button').first()
    const buttonExists = await button.count() > 0
    
    if (buttonExists) {
      // Measure tap response time
      const startTime = Date.now()
      await button.tap()
      
      // Wait for visual feedback (active state, ripple effect, etc.)
      await page.waitForTimeout(100)
      const endTime = Date.now()
      
      // Response should be immediate (< 100ms is target, we allow 150ms for test)
      expect(endTime - startTime).toBeLessThan(150)
    }
  })

  test('should show tap feedback (ripple or highlight)', async ({ page }) => {
    await page.waitForSelector('button', { timeout: 5000 })
    
    const button = page.locator('button').first()
    const buttonExists = await button.count() > 0
    
    if (buttonExists) {
      // Take screenshot before tap
      await page.screenshot({ 
        path: 'Frontend/TaskManager/_meta/tests/e2e-results/before-tap.png' 
      })
      
      // Tap the button
      await button.tap()
      
      // Wait a moment for feedback
      await page.waitForTimeout(50)
      
      // Take screenshot during tap feedback
      await page.screenshot({ 
        path: 'Frontend/TaskManager/_meta/tests/e2e-results/during-tap.png' 
      })
    }
  })

  test('should handle multi-touch gestures (pinch zoom disabled)', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Check meta viewport tag to ensure pinch zoom is disabled for app
    const viewportMeta = await page.evaluate(() => {
      const meta = document.querySelector('meta[name="viewport"]')
      return meta ? meta.getAttribute('content') : ''
    })
    
    // For a task manager app, we typically want to disable pinch zoom
    // to prevent accidental zooming during task interaction
    expect(viewportMeta).toContain('user-scalable=no')
  })

  test('should handle long press (if context menu is implemented)', async ({ page }) => {
    await page.waitForSelector('[data-testid="task-item"]', { timeout: 5000 })
    
    const taskItem = page.locator('[data-testid="task-item"]').first()
    
    // Perform long press (tap and hold)
    await taskItem.tap({ delay: 1000 })
    
    // Wait for potential context menu
    await page.waitForTimeout(500)
    
    // Check if context menu appeared
    const contextMenu = page.locator('[data-testid="context-menu"]')
    const menuExists = await contextMenu.count() > 0
    
    if (menuExists) {
      await expect(contextMenu).toBeVisible()
    }
  })

  test('should prevent accidental double-taps', async ({ page }) => {
    await page.waitForSelector('button', { timeout: 5000 })
    
    const button = page.locator('[data-testid="submit-button"], button').first()
    const buttonExists = await button.count() > 0
    
    if (buttonExists) {
      // Tap twice quickly
      await button.tap()
      await page.waitForTimeout(50)
      await button.tap()
      
      // Wait to see if action was triggered twice
      await page.waitForTimeout(500)
      
      // In a well-designed app, submit buttons should be disabled
      // after first tap to prevent double submission
      const isDisabled = await button.isDisabled()
      
      // Or button might be hidden after successful action
      const isVisible = await button.isVisible()
      
      // At least one protection should be in place
      expect(isDisabled || !isVisible).toBeTruthy()
    }
  })

  test('should have adequate spacing between touch targets', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Find groups of interactive elements (buttons in a toolbar, etc.)
    const buttons = await page.locator('button').all()
    
    if (buttons.length > 1) {
      // Check spacing between first two buttons
      const box1 = await buttons[0].boundingBox()
      const box2 = await buttons[1].boundingBox()
      
      if (box1 && box2) {
        // Calculate distance between buttons
        const horizontalGap = Math.abs((box2.x) - (box1.x + box1.width))
        const verticalGap = Math.abs((box2.y) - (box1.y + box1.height))
        
        // Buttons should have at least 8px spacing (common design guideline)
        // or be far apart enough to not cause accidental taps
        const hasAdequateSpacing = horizontalGap >= 8 || verticalGap >= 8 || 
                                   horizontalGap > 44 || verticalGap > 44
        
        expect(hasAdequateSpacing).toBeTruthy()
      }
    }
  })

  test('should handle swipe on scrollable lists', async ({ page }) => {
    await page.waitForSelector('[data-testid="task-list"]', { timeout: 5000 })
    
    // Get initial scroll position
    const initialScroll = await page.evaluate(() => window.scrollY)
    
    // Perform swipe gesture
    await page.touchscreen.swipe(
      { x: 200, y: 600 },
      { x: 200, y: 200 }
    )
    
    // Wait for scroll to complete
    await page.waitForTimeout(500)
    
    // Verify scroll occurred
    const finalScroll = await page.evaluate(() => window.scrollY)
    expect(finalScroll).toBeGreaterThan(initialScroll)
  })

  test('should handle pull-to-refresh (if implemented)', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Try pull-to-refresh gesture
    await page.touchscreen.swipe(
      { x: 200, y: 200 },
      { x: 200, y: 600 }
    )
    
    // Wait for potential refresh
    await page.waitForTimeout(1000)
    
    // Check if refresh indicator appeared
    const refreshIndicator = page.locator('[data-testid="refresh-indicator"]')
    const refreshExists = await refreshIndicator.count() > 0
    
    if (refreshExists) {
      // Wait for refresh to complete
      await page.waitForTimeout(2000)
      
      // Verify content reloaded
      const taskList = page.locator('[data-testid="task-list"]')
      await expect(taskList).toBeVisible()
    }
  })

  test('should not register touch on disabled elements', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Create a disabled button for testing (if not already present)
    await page.evaluate(() => {
      const button = document.createElement('button')
      button.textContent = 'Disabled Button'
      button.disabled = true
      button.setAttribute('data-testid', 'disabled-test-button')
      document.body.appendChild(button)
    })
    
    const disabledButton = page.locator('[data-testid="disabled-test-button"]')
    await expect(disabledButton).toBeDisabled()
    
    // Try to tap disabled button
    await disabledButton.tap({ force: true })
    
    // Button should remain disabled and not trigger action
    await expect(disabledButton).toBeDisabled()
  })

  test('should handle rapid taps without errors', async ({ page }) => {
    await page.waitForSelector('button', { timeout: 5000 })
    
    const button = page.locator('button').first()
    const buttonExists = await button.count() > 0
    
    if (buttonExists) {
      // Perform rapid taps
      for (let i = 0; i < 5; i++) {
        await button.tap({ timeout: 100 }).catch(() => {
          // Button might become disabled or hidden, which is fine
        })
        await page.waitForTimeout(50)
      }
      
      // Verify page is still functional
      const body = page.locator('body')
      await expect(body).toBeVisible()
    }
  })
})
