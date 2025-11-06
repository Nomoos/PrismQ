/**
 * Automated Screenshot Capture Script for PrismQ Web Client
 * 
 * This script uses Playwright to capture screenshots of the web interface.
 * 
 * Prerequisites:
 * 1. Backend server running on http://localhost:8000
 * 2. Frontend server running on http://localhost:5173
 * 3. Playwright installed: npm install --save-dev playwright
 * 
 * Usage:
 *   node scripts/capture-screenshots.js
 * 
 * Output:
 *   Screenshots saved to docs/screenshots/
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const FRONTEND_URL = 'http://localhost:5173';
const BACKEND_URL = 'http://localhost:8000';
const SCREENSHOT_DIR = path.join(__dirname, '..', 'docs', 'screenshots');

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function captureScreenshots() {
  console.log('🚀 Starting screenshot capture...\n');
  
  const browser = await chromium.launch({
    headless: true,
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });
  
  const page = await context.newPage();
  
  try {
    // Check if backend is running
    console.log('✓ Checking backend health...');
    const healthResponse = await page.goto(`${BACKEND_URL}/health`);
    if (!healthResponse.ok()) {
      throw new Error('Backend not running. Please start the backend server.');
    }
    console.log('✓ Backend is healthy\n');
    
    // 1. Dashboard View
    console.log('📸 Capturing dashboard...');
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'dashboard.png'),
      fullPage: false,
    });
    console.log('✓ Saved: dashboard.png\n');
    
    // 2. Module Card Detail
    console.log('📸 Capturing module card...');
    const moduleCard = await page.locator('.module-card, [data-testid="module-card"]').first();
    if (await moduleCard.count() > 0) {
      await moduleCard.screenshot({
        path: path.join(SCREENSHOT_DIR, 'module-card.png'),
      });
      console.log('✓ Saved: module-card.png\n');
    } else {
      console.log('⚠ Module card not found, skipping...\n');
    }
    
    // 3. Launch Modal
    console.log('📸 Capturing launch modal...');
    const launchButton = await page.locator('button:has-text("Launch")').first();
    if (await launchButton.count() > 0) {
      await launchButton.click();
      await page.waitForTimeout(1000);
      const modal = await page.locator('.modal, [role="dialog"]').first();
      if (await modal.count() > 0) {
        await modal.screenshot({
          path: path.join(SCREENSHOT_DIR, 'launch-modal.png'),
        });
        console.log('✓ Saved: launch-modal.png\n');
        
        const closeButton = await page.locator('button:has-text("Cancel"), button:has-text("Close")').first();
        if (await closeButton.count() > 0) {
          await closeButton.click();
        } else {
          await page.keyboard.press('Escape');
        }
        await page.waitForTimeout(500);
      }
    } else {
      console.log('⚠ Launch button not found, skipping modal...\n');
    }
    
    // 7. API Documentation
    console.log('📸 Capturing API docs...');
    await page.goto(`${BACKEND_URL}/docs`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    const firstEndpoint = await page.locator('.opblock').first();
    if (await firstEndpoint.count() > 0) {
      await firstEndpoint.click();
      await page.waitForTimeout(500);
    }
    
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, 'api-docs.png'),
      fullPage: false,
    });
    console.log('✓ Saved: api-docs.png\n');
    
    console.log('✅ All screenshots captured successfully!\n');
    console.log(`Screenshots saved to: ${SCREENSHOT_DIR}\n`);
    
  } catch (error) {
    console.error('❌ Error capturing screenshots:', error.message);
    console.error('\nPlease ensure:');
    console.error('1. Backend is running on http://localhost:8000');
    console.error('2. Frontend is running on http://localhost:5173');
    console.error('3. Application has loaded properly\n');
    process.exit(1);
  } finally {
    await browser.close();
  }
}

captureScreenshots().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
