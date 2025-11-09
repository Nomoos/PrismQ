import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E Test Configuration for TaskManager
 * 
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests/e2e',
  
  // Maximum time one test can run for
  timeout: 30 * 1000,
  
  // Test execution settings
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: './playwright-report' }],
    ['list']
  ],
  
  // Shared settings for all tests
  use: {
    // Base URL for tests
    baseURL: 'http://localhost:5173',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure
    video: 'retain-on-failure',
  },

  // Configure projects for different browsers and viewports
  projects: [
    {
      name: 'Desktop Chrome',
      use: { ...devices['Desktop Chrome'] },
    },
    
    // Mobile viewport (primary target)
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'],
        viewport: { width: 360, height: 800 }
      },
    },

    // Uncomment for more browser testing
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],

  // Run local dev server before starting the tests
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
})
