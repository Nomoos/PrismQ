/**
 * Sentry Error Tracking Configuration
 * 
 * Configures Sentry SDK for production error monitoring.
 * Only active in production/staging environments.
 * 
 * @see https://docs.sentry.io/platforms/javascript/guides/vue/
 */

import * as Sentry from '@sentry/vue'
import type { App } from 'vue'
import type { Router } from 'vue-router'

/**
 * Sentry configuration options
 */
export interface SentryConfig {
  dsn: string
  environment: string
  release?: string
  enabled?: boolean
  sampleRate?: number
  tracesSampleRate?: number
}

/**
 * Initialize Sentry for error tracking and performance monitoring
 * 
 * @param app - Vue app instance
 * @param router - Vue Router instance
 * @param config - Sentry configuration
 */
export function initSentry(app: App, router: Router, config: SentryConfig): void {
  const {
    dsn,
    environment,
    release,
    enabled = true,
    sampleRate = 1.0,
    tracesSampleRate = 0.1
  } = config

  // Only initialize if DSN is provided and Sentry is enabled
  if (!dsn || !enabled) {
    if (import.meta.env.DEV) {
      console.log('[Sentry] Disabled - no DSN or explicitly disabled')
    }
    return
  }

  // Don't initialize in development unless explicitly requested
  if (import.meta.env.DEV && environment !== 'development') {
    console.log('[Sentry] Skipping initialization in development mode')
    return
  }

  try {
    Sentry.init({
      app,
      dsn,
      environment,
      release,

      // Integration configuration
      integrations: [
        // Track Vue component performance
        Sentry.browserTracingIntegration({ router }),
        
        // Capture unhandled promise rejections
        Sentry.captureConsoleIntegration({
          levels: ['error']
        }),
        
        // Session replay (disabled by default for privacy)
        // Uncomment to enable session replay
        // Sentry.replayIntegration({
        //   maskAllText: true,
        //   blockAllMedia: true,
        // }),
      ],

      // Performance monitoring
      tracesSampleRate, // 10% of transactions for performance monitoring
      
      // Error sampling
      sampleRate, // 100% of errors by default

      // Privacy settings
      beforeSend(event, hint) {
        // Filter out sensitive data
        if (event.request?.headers) {
          // Remove authorization headers
          delete event.request.headers['Authorization']
          delete event.request.headers['X-API-Key']
        }

        // Scrub PII from breadcrumbs
        if (event.breadcrumbs) {
          event.breadcrumbs = event.breadcrumbs.map(breadcrumb => {
            if (breadcrumb.data) {
              // Remove potential PII from data
              const { password, token, apiKey, ...safeData } = breadcrumb.data
              return { ...breadcrumb, data: safeData }
            }
            return breadcrumb
          })
        }

        // In development, log errors to console instead of sending
        if (import.meta.env.DEV) {
          console.error('[Sentry]', event, hint)
          return null // Don't send to Sentry
        }

        return event
      },

      // Ignore certain errors
      ignoreErrors: [
        // Browser extensions
        'top.GLOBALS',
        'chrome-extension://',
        'moz-extension://',
        
        // Network errors that are expected
        'NetworkError',
        'Failed to fetch',
        'Load failed',
        
        // Cancelled requests (expected behavior)
        'Request aborted',
        'Duplicate request cancelled',
        
        // Non-error console output
        'ResizeObserver loop limit exceeded',
      ],

      // Only track errors from our domain
      allowUrls: [
        /https?:\/\/(.*\.)?prismq\.nomoos\.cz/,
        /https?:\/\/(.*\.)?your-domain\.com/, // Update with your production domain
      ],

      // Track releases for better error debugging
      beforeBreadcrumb(breadcrumb) {
        // Don't track console logs in breadcrumbs
        if (breadcrumb.category === 'console') {
          return null
        }
        return breadcrumb
      },
    })

    // Set default tags
    Sentry.setTag('app.component', 'frontend-taskmanager')
    Sentry.setTag('app.platform', 'web')

    if (import.meta.env.DEV) {
      console.log('[Sentry] Initialized successfully', {
        environment,
        release,
        sampleRate,
        tracesSampleRate
      })
    }
  } catch (error) {
    console.error('[Sentry] Failed to initialize:', error)
  }
}

/**
 * Set user context for Sentry
 * 
 * @param workerId - Worker ID
 */
export function setSentryUser(workerId: string | null): void {
  if (workerId) {
    Sentry.setUser({ id: workerId })
    Sentry.setTag('worker.id', workerId)
  } else {
    Sentry.setUser(null)
  }
}

/**
 * Capture a custom error message
 * 
 * @param message - Error message
 * @param level - Severity level
 * @param context - Additional context
 */
export function captureSentryMessage(
  message: string,
  level: 'info' | 'warning' | 'error' = 'error',
  context?: Record<string, any>
): void {
  Sentry.captureMessage(message, {
    level,
    extra: context
  })
}

/**
 * Capture an exception
 * 
 * @param error - Error object
 * @param context - Additional context
 */
export function captureSentryException(
  error: Error,
  context?: Record<string, any>
): void {
  Sentry.captureException(error, {
    extra: context
  })
}

/**
 * Add breadcrumb for debugging
 * 
 * @param message - Breadcrumb message
 * @param data - Additional data
 */
export function addSentryBreadcrumb(
  message: string,
  data?: Record<string, any>
): void {
  Sentry.addBreadcrumb({
    message,
    data,
    level: 'info'
  })
}

/**
 * Get Sentry configuration from environment variables
 * 
 * @returns Sentry configuration
 */
export function getSentryConfig(): SentryConfig {
  return {
    dsn: import.meta.env.VITE_SENTRY_DSN || '',
    environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || import.meta.env.VITE_APP_ENV || 'production',
    release: import.meta.env.VITE_SENTRY_RELEASE || undefined,
    enabled: import.meta.env.VITE_SENTRY_ENABLED !== 'false',
    sampleRate: parseFloat(import.meta.env.VITE_SENTRY_SAMPLE_RATE || '1.0'),
    tracesSampleRate: parseFloat(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || '0.1')
  }
}
