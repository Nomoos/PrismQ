module.exports = {
  ci: {
    collect: {
      // Number of runs per URL
      numberOfRuns: 3,
      
      // URLs to test
      url: [
        'http://localhost:4173/', // Vite preview server
        'http://localhost:4173/workers',
        'http://localhost:4173/settings'
      ],
      
      // Lighthouse settings
      settings: {
        // Emulate mobile device (Redmi 24115RA8EG specs)
        formFactor: 'mobile',
        throttling: {
          rttMs: 150,
          throughputKbps: 1.6 * 1024, // 3G network
          requestLatencyMs: 150,
          downloadThroughputKbps: 1.6 * 1024,
          uploadThroughputKbps: 750,
          cpuSlowdownMultiplier: 4
        },
        screenEmulation: {
          mobile: true,
          width: 412,
          height: 915,
          deviceScaleFactor: 2.625,
          disabled: false
        }
      }
    },
    
    assert: {
      // Performance budgets
      assertions: {
        // Performance metrics
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['warn', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
        
        // Core Web Vitals
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['warn', { maxNumericValue: 300 }],
        
        // Other important metrics
        'interactive': ['error', { maxNumericValue: 5000 }],
        'speed-index': ['warn', { maxNumericValue: 4000 }],
        
        // Resource hints
        'uses-rel-preconnect': 'off',
        'uses-rel-preload': 'off'
      }
    },
    
    upload: {
      // Store reports locally
      target: 'temporary-public-storage'
    }
  }
}
