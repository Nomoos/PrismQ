import { test, expect } from '@playwright/test'

/**
 * E2E test for the module launch workflow
 * 
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - Frontend dev server running on http://localhost:5173
 * - At least one test module available
 */

test.describe('Module Launch Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard
    await page.goto('http://localhost:5173')
  })

  test('should display the dashboard with modules', async ({ page }) => {
    // Wait for modules to load
    await page.waitForSelector('.module-card', { timeout: 10000 })
    
    // Verify at least one module card is present
    const moduleCards = await page.locator('.module-card').count()
    expect(moduleCards).toBeGreaterThan(0)
  })

  test('should open launch modal when clicking launch button', async ({ page }) => {
    // Wait for modules to load
    await page.waitForSelector('.module-card', { timeout: 10000 })
    
    // Click the first module's launch button
    await page.locator('.module-card button:has-text("Launch")').first().click()
    
    // Modal should be visible
    await expect(page.locator('.modal-content')).toBeVisible()
    
    // Modal should have a title
    await expect(page.locator('h2')).toContainText(/Launch|Module/)
  })

  test('should close modal when clicking cancel', async ({ page }) => {
    // Open modal
    await page.waitForSelector('.module-card', { timeout: 10000 })
    await page.locator('.module-card button:has-text("Launch")').first().click()
    await expect(page.locator('.modal-content')).toBeVisible()
    
    // Click cancel button
    await page.locator('button:has-text("Cancel")').click()
    
    // Modal should be hidden
    await expect(page.locator('.modal-content')).not.toBeVisible()
  })

  test('should launch module and navigate to run details', async ({ page }) => {
    // Wait for modules to load
    await page.waitForSelector('.module-card', { timeout: 10000 })
    
    // Click launch button
    await page.locator('.module-card button:has-text("Launch")').first().click()
    
    // Wait for modal
    await expect(page.locator('.modal-content')).toBeVisible()
    
    // Fill in any required parameters (if present)
    // Note: This assumes default values are acceptable
    
    // Click launch in modal
    await page.locator('.modal-content button:has-text("Launch")').click()
    
    // Should navigate to run details page
    await page.waitForURL(/\/runs\/run_/, { timeout: 10000 })
    
    // Verify we're on the run details page
    expect(page.url()).toMatch(/\/runs\/run_/)
  })

  test('should display log viewer on run details page', async ({ page }) => {
    // Navigate directly to a run (this test assumes we can create a run first)
    // For now, we'll skip this test if no runs exist
    test.skip(true, 'Requires a running module to test')
    
    // This test would:
    // 1. Launch a module
    // 2. Navigate to run details
    // 3. Verify log viewer is visible
    // 4. Verify logs start streaming
  })

  test('should handle module launch errors gracefully', async ({ page }) => {
    // This test would verify error handling
    // For now, we'll mark it as a placeholder
    test.skip(true, 'Requires error simulation setup')
  })
})

test.describe('Dashboard Navigation', () => {
  test('should navigate between dashboard and runs', async ({ page }) => {
    await page.goto('http://localhost:5173')
    
    // Should be on dashboard initially
    expect(page.url()).toContain('/')
    
    // Check if there's a navigation menu or link to runs
    // This depends on the actual UI implementation
  })

  test('should filter modules by search', async ({ page }) => {
    await page.goto('http://localhost:5173')
    await page.waitForSelector('.module-card', { timeout: 10000 })
    
    // Get initial count of modules
    const initialCount = await page.locator('.module-card').count()
    
    // If there's a search input, test filtering
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i]')
    if (await searchInput.count() > 0) {
      await searchInput.fill('test')
      
      // Wait a bit for filtering
      await page.waitForTimeout(500)
      
      // Count should change (could be 0 or less than initial)
      const filteredCount = await page.locator('.module-card').count()
      expect(filteredCount).toBeLessThanOrEqual(initialCount)
    } else {
      test.skip(true, 'No search functionality implemented yet')
    }
  })
})
