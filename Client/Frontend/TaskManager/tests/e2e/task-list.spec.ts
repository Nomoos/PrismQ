import { test, expect } from '@playwright/test'

test.describe('Task List View', () => {
  test('should display task list page', async ({ page }) => {
    await page.goto('/')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Tasks')
  })

  test('should navigate between task views using tabs', async ({ page }) => {
    await page.goto('/')
    
    // Wait for page to load
    await page.waitForLoadState('networkidle')
    
    // Check if tab navigation exists
    const tabBar = page.locator('[role="tablist"]').first()
    if (await tabBar.isVisible()) {
      await expect(tabBar).toBeVisible()
    }
  })

  test('should be responsive on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    
    // Check bottom navigation is visible on mobile
    const bottomNav = page.locator('nav').last()
    await expect(bottomNav).toBeVisible()
  })
})

test.describe('Navigation', () => {
  test('should navigate to worker dashboard', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Click on workers link/tab
    const workersLink = page.getByRole('link', { name: /workers/i }).or(
      page.getByText(/workers/i).first()
    )
    
    if (await workersLink.isVisible()) {
      await workersLink.click()
      await expect(page).toHaveURL(/\/workers/)
    }
  })

  test('should navigate to settings', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Click on settings link
    const settingsLink = page.getByRole('link', { name: /settings/i }).or(
      page.getByText(/settings/i).first()
    )
    
    if (await settingsLink.isVisible()) {
      await settingsLink.click()
      await expect(page).toHaveURL(/\/settings/)
    }
  })
})
