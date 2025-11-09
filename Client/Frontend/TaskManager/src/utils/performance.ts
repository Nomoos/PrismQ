/**
 * Performance monitoring utilities
 * Tracks Core Web Vitals and custom performance metrics
 */

import { onCLS, onINP, onLCP, onFCP, onTTFB, type Metric } from 'web-vitals'

interface PerformanceReport {
  metric: string
  value: number
  rating: 'good' | 'needs-improvement' | 'poor'
  delta: number
}

/**
 * Send performance metrics to analytics
 * @param metric The performance metric to report
 */
function sendToAnalytics(metric: Metric) {
  const { name, value, rating, delta } = metric
  
  // Log to console in development
  if (import.meta.env.DEV) {
    console.log(`[Performance] ${name}:`, {
      value: Math.round(value),
      rating,
      delta: Math.round(delta)
    })
  }
  
  // In production, send to analytics service
  // Example: send to Google Analytics, Sentry, or custom endpoint
  if (import.meta.env.PROD) {
    // TODO: Implement analytics reporting
    // Example: gtag('event', name, { value, rating })
  }
}

/**
 * Initialize Core Web Vitals tracking
 * Should be called once when the app starts
 */
export function initPerformanceMonitoring() {
  // Track Cumulative Layout Shift (CLS)
  // Target: < 0.1 (good), < 0.25 (needs improvement), >= 0.25 (poor)
  onCLS(sendToAnalytics)
  
  // Track Interaction to Next Paint (INP) - replaces FID
  // Target: < 200ms (good), < 500ms (needs improvement), >= 500ms (poor)
  onINP(sendToAnalytics)
  
  // Track Largest Contentful Paint (LCP)
  // Target: < 2.5s (good), < 4s (needs improvement), >= 4s (poor)
  onLCP(sendToAnalytics)
  
  // Track First Contentful Paint (FCP)
  // Target: < 1.8s (good), < 3s (needs improvement), >= 3s (poor)
  onFCP(sendToAnalytics)
  
  // Track Time to First Byte (TTFB)
  // Target: < 0.8s (good), < 1.8s (needs improvement), >= 1.8s (poor)
  onTTFB(sendToAnalytics)
}

/**
 * Mark a custom performance measurement
 * @param name The name of the measurement
 */
export function markPerformance(name: string) {
  if (performance && performance.mark) {
    performance.mark(name)
  }
}

/**
 * Measure time between two performance marks
 * @param name The name of the measurement
 * @param startMark The starting mark name
 * @param endMark The ending mark name (optional, defaults to now)
 */
export function measurePerformance(name: string, startMark: string, endMark?: string) {
  if (performance && performance.measure) {
    try {
      performance.measure(name, startMark, endMark)
      const measure = performance.getEntriesByName(name)[0]
      
      if (import.meta.env.DEV) {
        console.log(`[Performance] ${name}:`, Math.round(measure.duration), 'ms')
      }
      
      return measure.duration
    } catch (e) {
      console.warn(`Failed to measure performance: ${name}`, e)
    }
  }
  return 0
}

/**
 * Get current performance metrics
 */
export function getPerformanceMetrics(): PerformanceReport[] {
  const reports: PerformanceReport[] = []
  
  if (performance && performance.getEntriesByType) {
    const navigationTiming = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    
    if (navigationTiming) {
      // DOM Content Loaded
      reports.push({
        metric: 'DOM Content Loaded',
        value: navigationTiming.domContentLoadedEventEnd - navigationTiming.domContentLoadedEventStart,
        rating: 'good',
        delta: 0
      })
      
      // DOM Interactive
      reports.push({
        metric: 'DOM Interactive',
        value: navigationTiming.domInteractive - navigationTiming.fetchStart,
        rating: 'good',
        delta: 0
      })
      
      // Load Complete
      reports.push({
        metric: 'Load Complete',
        value: navigationTiming.loadEventEnd - navigationTiming.fetchStart,
        rating: 'good',
        delta: 0
      })
    }
  }
  
  return reports
}

/**
 * Log all performance metrics (for debugging)
 */
export function logPerformanceMetrics() {
  if (import.meta.env.DEV) {
    const metrics = getPerformanceMetrics()
    console.group('[Performance Metrics]')
    metrics.forEach(m => {
      console.log(`${m.metric}:`, Math.round(m.value), 'ms', `(${m.rating})`)
    })
    console.groupEnd()
  }
}
