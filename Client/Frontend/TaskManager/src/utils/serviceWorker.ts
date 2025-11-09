/**
 * Service Worker registration and management utilities
 */

interface ServiceWorkerConfig {
  onSuccess?: (registration: ServiceWorkerRegistration) => void
  onUpdate?: (registration: ServiceWorkerRegistration) => void
  onOfflineReady?: () => void
}

/**
 * Register the service worker
 * @param config Configuration callbacks for service worker events
 * @returns Service worker registration or undefined
 */
export async function registerServiceWorker(config: ServiceWorkerConfig = {}): Promise<ServiceWorkerRegistration | undefined> {
  // Only register in production
  if (import.meta.env.DEV) {
    console.log('[SW] Service worker disabled in development mode')
    return undefined
  }
  
  // Check if service workers are supported
  if (!('serviceWorker' in navigator)) {
    console.log('[SW] Service workers not supported')
    return undefined
  }
  
  try {
    // Wait for page to load
    if (document.readyState === 'loading') {
      await new Promise((resolve) => {
        window.addEventListener('load', resolve)
      })
    }
    
    console.log('[SW] Registering service worker...')
    
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/'
    })
    
    console.log('[SW] Service worker registered:', registration.scope)
    
    // Handle updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing
      if (!newWorker) return
      
      console.log('[SW] New service worker found')
      
      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed') {
          if (navigator.serviceWorker.controller) {
            // New service worker available
            console.log('[SW] New content available, please refresh')
            config.onUpdate?.(registration)
          } else {
            // Content cached for offline use
            console.log('[SW] Content cached for offline use')
            config.onOfflineReady?.()
          }
        }
        
        if (newWorker.state === 'activated') {
          console.log('[SW] Service worker activated')
          config.onSuccess?.(registration)
        }
      })
    })
    
    // Check for updates periodically (every hour)
    setInterval(() => {
      registration.update()
    }, 1000 * 60 * 60)
    
    return registration
  } catch (error) {
    console.error('[SW] Service worker registration failed:', error)
    return undefined
  }
}

/**
 * Unregister all service workers
 * Useful for development or debugging
 */
export async function unregisterServiceWorker() {
  if (!('serviceWorker' in navigator)) {
    return false
  }
  
  try {
    const registrations = await navigator.serviceWorker.getRegistrations()
    
    for (const registration of registrations) {
      await registration.unregister()
      console.log('[SW] Service worker unregistered')
    }
    
    return true
  } catch (error) {
    console.error('[SW] Failed to unregister service worker:', error)
    return false
  }
}

/**
 * Check if a service worker is registered and active
 */
export function isServiceWorkerActive(): boolean {
  return !!(navigator.serviceWorker && navigator.serviceWorker.controller)
}

/**
 * Send a message to the active service worker
 * @param message Message to send
 */
export async function sendMessageToServiceWorker(message: any) {
  if (!navigator.serviceWorker.controller) {
    console.warn('[SW] No active service worker to send message to')
    return
  }
  
  navigator.serviceWorker.controller.postMessage(message)
}

/**
 * Trigger service worker to skip waiting and activate immediately
 */
export async function skipWaitingServiceWorker() {
  const registration = await navigator.serviceWorker.getRegistration()
  
  if (registration?.waiting) {
    await sendMessageToServiceWorker({ type: 'SKIP_WAITING' })
    
    // Reload the page after activation
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      window.location.reload()
    })
  }
}

/**
 * Manually cache specific URLs
 * @param urls Array of URLs to cache
 */
export async function cacheUrls(urls: string[]) {
  await sendMessageToServiceWorker({
    type: 'CACHE_URLS',
    urls
  })
}
