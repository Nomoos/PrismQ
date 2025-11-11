import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright UX Testing Configuration for Worker12
 * Mobile Device Testing - Redmi 24115RA8EG Focus
 * 
 * This configuration is specifically for comprehensive UX testing including:
 * - Mobile device testing (Redmi 24115RA8EG simulation)
 * - Accessibility testing (WCAG 2.1 AA)
 * - Performance testing (3G/4G/WiFi networks)
 * - Cross-browser compatibility
 */
export default defineConfig({
  testDir: './_meta/tests/e2e',
  
  // Maximum time one test can run for
  timeout: 60 * 1000,
  
  // Test execution settings
  fullyParallel: false, // Run serially for UX testing to avoid resource conflicts
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: 1, // Single worker for consistent results
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: './_meta/tests/e2e-results' }],
    ['json', { outputFile: './_meta/tests/e2e-results/results.json' }],
    ['list']
  ],
  
  // Shared settings for all tests
  use: {
    // Base URL for tests
    baseURL: 'http://localhost:5173',
    
    // Collect trace for analysis
    trace: 'on',
    
    // Screenshot settings
    screenshot: 'on',
    
    // Video for all tests
    video: 'on',
    
    // Action timeout
    actionTimeout: 10 * 1000,
  },

  // Configure projects for comprehensive UX testing
  projects: [
    // === PRIMARY TARGET DEVICE ===
    {
      name: 'redmi-chrome',
      use: { 
        ...devices['Pixel 5'],
        viewport: { 
          width: 360,  // Redmi 24115RA8EG scaled viewport
          height: 800 
        },
        userAgent: 'Mozilla/5.0 (Linux; Android 14; Redmi Note 13 Pro+) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        isMobile: true,
        hasTouch: true,
        deviceScaleFactor: 2,
      },
    },

    // === NETWORK PERFORMANCE TESTING ===
    {
      name: 'redmi-3g',
      use: { 
        ...devices['Pixel 5'],
        viewport: { width: 360, height: 800 },
        userAgent: 'Mozilla/5.0 (Linux; Android 14; Redmi) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        isMobile: true,
        hasTouch: true,
        // Simulate 3G Slow network
        launchOptions: {
          slowMo: 100,
        },
        // This will be set via page.route() in tests for network throttling
      },
    },

    {
      name: 'redmi-4g',
      use: { 
        ...devices['Pixel 5'],
        viewport: { width: 360, height: 800 },
        userAgent: 'Mozilla/5.0 (Linux; Android 14; Redmi) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        isMobile: true,
        hasTouch: true,
        // Simulate 4G network (faster)
      },
    },

    // === MOBILE BROWSERS ===
    {
      name: 'redmi-firefox',
      use: {
        ...devices['Pixel 5'],
        viewport: { width: 360, height: 800 },
        userAgent: 'Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0',
        isMobile: true,
        hasTouch: true,
      },
    },

    // === iOS TESTING ===
    {
      name: 'iphone',
      use: { 
        ...devices['iPhone 14'],
        viewport: { width: 390, height: 844 },
      },
    },

    {
      name: 'ipad',
      use: { 
        ...devices['iPad Pro'],
        viewport: { width: 1024, height: 1366 },
      },
    },

    // === DESKTOP BROWSERS (Responsive) ===
    {
      name: 'desktop-chrome',
      use: { 
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
    },

    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        viewport: { width: 1280, height: 720 },
      },
    },

    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        viewport: { width: 1280, height: 720 },
      },
    },

    // === ACCESSIBILITY TESTING (Desktop for better DevTools) ===
    {
      name: 'accessibility',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
        // Additional accessibility settings
      },
      testMatch: /accessibility\/.*\.spec\.ts/,
    },
  ],

  // Run local dev server before starting the tests
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
})
