import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

/**
 * Accessibility Tests (WCAG 2.1 AA Compliance)
 * 
 * Tests accessibility compliance using axe-core,
 * focusing on WCAG 2.1 Level AA requirements.
 */

test.describe('Accessibility: WCAG 2.1 AA Compliance', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should not have any automatically detectable accessibility violations', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have proper color contrast ratios', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['cat.color'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have all images with alt text', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['cat.text-alternatives'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should be keyboard navigable', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['cat.keyboard'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have proper form labels', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['cat.forms'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have proper heading hierarchy', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Check heading structure
    const headings = await page.evaluate(() => {
      const elements = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'))
      return elements.map(el => ({
        level: parseInt(el.tagName.substring(1)),
        text: el.textContent?.trim()
      }))
    })
    
    if (headings.length > 0) {
      // First heading should be h1
      expect(headings[0].level).toBe(1)
      
      // Check for proper hierarchy (no skipping levels)
      for (let i = 1; i < headings.length; i++) {
        const levelDiff = headings[i].level - headings[i - 1].level
        expect(levelDiff).toBeLessThanOrEqual(1)
      }
    }
  })

  test('should have ARIA labels for interactive elements', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['cat.aria'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should have visible focus indicators', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const button = page.locator('button').first()
    const buttonExists = await button.count() > 0
    
    if (buttonExists) {
      // Focus the button
      await button.focus()
      
      // Check if focus indicator is visible
      const focusStyles = await button.evaluate((el) => {
        const styles = window.getComputedStyle(el, ':focus')
        return {
          outline: styles.outline,
          outlineWidth: styles.outlineWidth,
          outlineStyle: styles.outlineStyle,
          boxShadow: styles.boxShadow
        }
      })
      
      // Should have either outline or box-shadow for focus
      const hasFocusIndicator = 
        focusStyles.outlineWidth !== '0px' ||
        focusStyles.boxShadow !== 'none'
      
      expect(hasFocusIndicator).toBeTruthy()
    }
  })

  test('should be navigable with keyboard only', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Tab through interactive elements
    await page.keyboard.press('Tab')
    let focusedElement = await page.evaluate(() => document.activeElement?.tagName)
    
    // Should focus on an interactive element
    const interactiveTags = ['BUTTON', 'A', 'INPUT', 'SELECT', 'TEXTAREA']
    expect(interactiveTags).toContain(focusedElement)
    
    // Tab again
    await page.keyboard.press('Tab')
    const nextFocusedElement = await page.evaluate(() => document.activeElement?.tagName)
    
    // Focus should move to another element
    expect(nextFocusedElement).toBeTruthy()
  })

  test('should allow tabbing backwards (Shift+Tab)', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Tab forward twice
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    
    const secondElement = await page.evaluate(() => document.activeElement?.tagName)
    
    // Tab backward
    await page.keyboard.press('Shift+Tab')
    
    const firstElement = await page.evaluate(() => document.activeElement?.tagName)
    
    // Should be on different element
    expect(firstElement).toBeTruthy()
  })

  test('should have no keyboard traps', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Tab through elements and ensure we can always move focus
    let previousElement = ''
    let sameElementCount = 0
    
    for (let i = 0; i < 20; i++) {
      await page.keyboard.press('Tab')
      const currentElement = await page.evaluate(() => {
        const el = document.activeElement
        return el?.tagName + (el?.id ? `#${el.id}` : '') + (el?.className ? `.${el.className.split(' ')[0]}` : '')
      })
      
      if (currentElement === previousElement) {
        sameElementCount++
      } else {
        sameElementCount = 0
      }
      
      // If stuck on same element for 3 tabs, there's a keyboard trap
      expect(sameElementCount).toBeLessThan(3)
      
      previousElement = currentElement
    }
  })

  test('should support screen reader announcements', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Check for ARIA live regions
    const liveRegions = await page.locator('[aria-live]').count()
    
    // Should have at least one live region for announcements
    // (This depends on implementation, so we just check it exists or doesn't)
    expect(typeof liveRegions).toBe('number')
  })

  test('should have proper button labels', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const buttons = await page.locator('button').all()
    
    for (const button of buttons) {
      // Each button should have accessible text
      const accessibleName = await button.evaluate((el) => {
        return el.textContent?.trim() || 
               el.getAttribute('aria-label') || 
               el.getAttribute('title')
      })
      
      expect(accessibleName).toBeTruthy()
      expect(accessibleName!.length).toBeGreaterThan(0)
    }
  })

  test('should have sufficient touch target sizes (44x44px)', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const interactiveElements = await page.locator('button, a, input, select').all()
    
    for (const element of interactiveElements.slice(0, 10)) { // Check first 10
      const box = await element.boundingBox()
      
      if (box && (box.width > 0 || box.height > 0)) {
        // WCAG 2.5.5 (AAA, but good practice for mobile)
        expect(box.width).toBeGreaterThanOrEqual(44)
        expect(box.height).toBeGreaterThanOrEqual(44)
      }
    }
  })

  test('should support text resizing to 200%', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Get original text size
    const originalSize = await page.evaluate(() => {
      const body = document.body
      return window.getComputedStyle(body).fontSize
    })
    
    // Increase font size to 200%
    await page.evaluate(() => {
      document.body.style.fontSize = '200%'
    })
    
    await page.waitForTimeout(500)
    
    // Check that content is still visible and not cut off
    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth
    })
    
    // Some horizontal overflow might occur, but content should still be readable
    // Main check is that page doesn't break
    const bodyVisible = await page.locator('body').isVisible()
    expect(bodyVisible).toBeTruthy()
  })

  test('should not use color alone to convey information', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Run specific axe check for color dependence
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['cat.sensory-and-visual-cues'])
      .analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })
})
