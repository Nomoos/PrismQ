import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E Test Configuration
 * 
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './Frontend/TaskManager/_meta/tests/e2e',
  
  // Maximum time one test can run for
  timeout: 30 * 1000,
  
  // Test execution settings
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: './Frontend/TaskManager/_meta/tests/e2e-results' }],
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

  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // Mobile Device Testing - Redmi 24115RA8EG (Primary Target)
    {
      name: 'redmi-chrome',
      use: {
        ...devices['Pixel 5'], // Similar screen size and resolution
        viewport: { width: 393, height: 851 }, // Redmi-like viewport
        userAgent: 'Mozilla/5.0 (Linux; Android 14; 24115RA8EG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        deviceScaleFactor: 2.75,
        isMobile: true,
        hasTouch: true,
      },
    },

    // Mobile Device Testing - Android Firefox
    {
      name: 'redmi-firefox',
      use: {
        ...devices['Pixel 5'],
        viewport: { width: 393, height: 851 },
        userAgent: 'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0',
        deviceScaleFactor: 2.75,
        isMobile: true,
        hasTouch: true,
      },
    },

    // Network Throttling Tests - 3G
    {
      name: 'redmi-3g',
      use: {
        ...devices['Pixel 5'],
        viewport: { width: 393, height: 851 },
        deviceScaleFactor: 2.75,
        isMobile: true,
        hasTouch: true,
        // Simulate Slow 3G: 400kbps download, 400kbps upload
        launchOptions: {
          args: ['--simulate-outdated-no-au=Tue, 31 Dec 2099 23:59:59 GMT'],
        },
      },
    },

    // iOS Testing
    {
      name: 'iphone',
      use: { ...devices['iPhone 14'] },
    },

    // Tablet Testing
    {
      name: 'ipad',
      use: { ...devices['iPad Pro'] },
    },

    // Desktop browsers for responsive testing
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  // Run local dev server before starting the tests
  webServer: [
    {
      command: 'cd Frontend && npm run dev',
      url: 'http://localhost:5173',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
    {
      command: process.env.CI 
        ? 'cd Backend && uvicorn src.main:app' 
        : 'cd Backend && uvicorn src.main:app --reload',
      url: 'http://localhost:8000/api/health',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
    },
  ],
})
