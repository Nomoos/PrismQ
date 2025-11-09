import { test, expect } from '@playwright/test'

/**
 * Performance Tests for Mobile Devices
 * 
 * Tests load times, interaction responsiveness, and performance
 * metrics on mobile networks (3G, 4G, WiFi).
 */

test.describe('Performance: Load Time Testing', () => {
  test('should load in under 3 seconds on 3G network', async ({ page, browserName }) => {
    // Only run on 3G network simulation
    test.skip(browserName !== 'redmi-3g')
    
    const startTime = Date.now()
    
    await page.goto('/', { waitUntil: 'load' })
    
    const loadTime = Date.now() - startTime
    
    // Target: < 3s on 3G
    expect(loadTime).toBeLessThan(3000)
  })

  test('should load in under 1.5 seconds on 4G network', async ({ page }) => {
    const startTime = Date.now()
    
    await page.goto('/', { waitUntil: 'load' })
    
    const loadTime = Date.now() - startTime
    
    // Target: < 1.5s on 4G
    expect(loadTime).toBeLessThan(1500)
  })

  test('should have First Contentful Paint under 2 seconds', async ({ page }) => {
    await page.goto('/')
    
    const fcp = await page.evaluate(() => {
      const perfEntries = performance.getEntriesByType('paint')
      const fcpEntry = perfEntries.find(entry => entry.name === 'first-contentful-paint')
      return fcpEntry ? fcpEntry.startTime : 0
    })
    
    // FCP should be under 2 seconds
    expect(fcp).toBeLessThan(2000)
  })

  test('should measure Core Web Vitals', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const metrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries()
          const vitals: any = {}
          
          entries.forEach((entry: any) => {
            if (entry.name === 'first-contentful-paint') {
              vitals.fcp = entry.startTime
            }
            if (entry.entryType === 'largest-contentful-paint') {
              vitals.lcp = entry.startTime
            }
          })
          
          // Get CLS
          const cls = entries
            .filter((entry: any) => entry.entryType === 'layout-shift' && !entry.hadRecentInput)
            .reduce((sum: number, entry: any) => sum + entry.value, 0)
          
          vitals.cls = cls
          
          resolve(vitals)
        })
        
        observer.observe({ entryTypes: ['paint', 'largest-contentful-paint', 'layout-shift'] })
        
        // Timeout after 5 seconds
        setTimeout(() => {
          observer.disconnect()
          resolve({})
        }, 5000)
      })
    })
    
    // Check metrics if they exist
    if ((metrics as any).lcp) {
      // LCP should be under 2.5s
      expect((metrics as any).lcp).toBeLessThan(2500)
    }
    
    if ((metrics as any).cls !== undefined) {
      // CLS should be under 0.1
      expect((metrics as any).cls).toBeLessThan(0.1)
    }
  })

  test('should have minimal Cumulative Layout Shift', async ({ page }) => {
    await page.goto('/')
    
    // Wait for page to stabilize
    await page.waitForTimeout(2000)
    
    const cls = await page.evaluate(() => {
      return new Promise((resolve) => {
        let clsValue = 0
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            const layoutShift = entry as any
            if (!layoutShift.hadRecentInput) {
              clsValue += layoutShift.value
            }
          }
        })
        
        observer.observe({ entryTypes: ['layout-shift'] })
        
        setTimeout(() => {
          observer.disconnect()
          resolve(clsValue)
        }, 3000)
      })
    })
    
    // CLS should be minimal (< 0.1)
    expect(cls).toBeLessThan(0.1)
  })

  test('should load critical resources quickly', async ({ page }) => {
    const startTime = Date.now()
    
    await page.goto('/')
    
    // Wait for critical resources
    await page.waitForSelector('body', { timeout: 5000 })
    
    const timeToInteractive = Date.now() - startTime
    
    // Should be interactive quickly
    expect(timeToInteractive).toBeLessThan(5000)
  })
})

test.describe('Performance: Interaction Responsiveness', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should respond to button clicks in under 100ms', async ({ page }) => {
    await page.waitForSelector('button', { timeout: 5000 })
    
    const button = page.locator('button').first()
    const buttonExists = await button.count() > 0
    
    if (buttonExists) {
      const startTime = Date.now()
      await button.click()
      const responseTime = Date.now() - startTime
      
      // Target: < 100ms First Input Delay
      expect(responseTime).toBeLessThan(100)
    }
  })

  test('should scroll smoothly at 60fps', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Measure scroll performance
    const scrollPerformance = await page.evaluate(() => {
      return new Promise((resolve) => {
        let frameCount = 0
        let totalFrameTime = 0
        let lastTimestamp = performance.now()
        
        const measureFrames = (timestamp: number) => {
          const frameTime = timestamp - lastTimestamp
          totalFrameTime += frameTime
          frameCount++
          lastTimestamp = timestamp
          
          if (frameCount < 60) {
            requestAnimationFrame(measureFrames)
          } else {
            const avgFrameTime = totalFrameTime / frameCount
            const fps = 1000 / avgFrameTime
            resolve({ fps, avgFrameTime })
          }
        }
        
        // Trigger scroll
        window.scrollBy(0, 500)
        requestAnimationFrame(measureFrames)
      })
    })
    
    // Average FPS should be close to 60
    expect((scrollPerformance as any).fps).toBeGreaterThan(50)
  })

  test('should handle rapid interactions without lag', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    const button = page.locator('button').first()
    const buttonExists = await button.count() > 0
    
    if (buttonExists) {
      const startTime = Date.now()
      
      // Perform 10 rapid clicks
      for (let i = 0; i < 10; i++) {
        await button.click({ timeout: 500 }).catch(() => {})
        await page.waitForTimeout(50)
      }
      
      const totalTime = Date.now() - startTime
      
      // Should complete all interactions quickly
      expect(totalTime).toBeLessThan(2000)
    }
  })

  test('should update UI without blocking', async ({ page }) => {
    await page.waitForLoadState('networkidle')
    
    // Measure if page remains responsive during updates
    const isResponsive = await page.evaluate(() => {
      return new Promise((resolve) => {
        let blocked = false
        
        // Start a timer to check responsiveness
        const checkInterval = setInterval(() => {
          const start = Date.now()
          // This should execute immediately if page is responsive
          setTimeout(() => {
            const delay = Date.now() - start
            if (delay > 100) {
              blocked = true
            }
          }, 0)
        }, 100)
        
        // Trigger some UI updates
        document.body.style.backgroundColor = '#f0f0f0'
        
        // Check for 1 second
        setTimeout(() => {
          clearInterval(checkInterval)
          resolve(!blocked)
        }, 1000)
      })
    })
    
    expect(isResponsive).toBeTruthy()
  })
})

test.describe('Performance: Resource Loading', () => {
  test('should have optimized bundle size', async ({ page }) => {
    const resources = await page.evaluate(() => {
      const entries = performance.getEntriesByType('resource')
      let totalSize = 0
      
      entries.forEach((entry: any) => {
        totalSize += entry.transferSize || 0
      })
      
      return {
        totalSize,
        resourceCount: entries.length
      }
    })
    
    // Total transfer size should be reasonable for initial load
    // Target: < 2MB for initial load
    expect(resources.totalSize).toBeLessThan(2 * 1024 * 1024)
  })

  test('should cache resources effectively', async ({ page }) => {
    // First visit
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const firstLoadResources = await page.evaluate(() => {
      return performance.getEntriesByType('resource').length
    })
    
    // Second visit (should use cache)
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const secondLoadResources = await page.evaluate(() => {
      const entries = performance.getEntriesByType('resource') as any[]
      const cachedCount = entries.filter(entry => 
        entry.transferSize === 0 || entry.transferSize < entry.encodedBodySize
      ).length
      
      return {
        total: entries.length,
        cached: cachedCount
      }
    })
    
    // At least some resources should be cached
    expect(secondLoadResources.cached).toBeGreaterThan(0)
  })

  test('should lazy load images', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const images = await page.evaluate(() => {
      const imgs = Array.from(document.querySelectorAll('img'))
      return imgs.map(img => ({
        loading: img.loading,
        src: img.src
      }))
    })
    
    if (images.length > 0) {
      // Images below the fold should have loading="lazy"
      const hasLazyLoading = images.some(img => img.loading === 'lazy')
      
      // Either lazy loading is implemented or there are few images
      expect(hasLazyLoading || images.length < 5).toBeTruthy()
    }
  })
})

test.describe('Performance: Memory Usage', () => {
  test('should not leak memory on navigation', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Get initial memory (if available)
    const initialMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0
    })
    
    // Navigate around the app
    for (let i = 0; i < 5; i++) {
      await page.goto('/')
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(500)
    }
    
    // Get final memory
    const finalMemory = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0
    })
    
    if (initialMemory > 0 && finalMemory > 0) {
      // Memory shouldn't grow excessively (allow 50% growth)
      const memoryGrowth = (finalMemory - initialMemory) / initialMemory
      expect(memoryGrowth).toBeLessThan(0.5)
    }
  })
})
