/**
 * Service Worker for PrismQ TaskManager
 * Implements caching strategies for offline support and performance
 */

const CACHE_VERSION = 'v1.0.0'
const CACHE_NAME = `prismq-taskmanager-${CACHE_VERSION}`
const API_CACHE_NAME = `prismq-api-${CACHE_VERSION}`

// Static assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html'
  // Note: Vite generates hashed asset names, so we'll cache them dynamically
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...')
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets')
        return cache.addAll(STATIC_ASSETS)
      })
      .then(() => {
        // Force activation of new service worker
        return self.skipWaiting()
      })
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...')
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              // Delete caches that don't match current version
              return cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME
            })
            .map((cacheName) => {
              console.log('[Service Worker] Deleting old cache:', cacheName)
              return caches.delete(cacheName)
            })
        )
      })
      .then(() => {
        // Take control of all clients immediately
        return self.clients.claim()
      })
  )
})

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Handle API requests with network-first strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request, API_CACHE_NAME))
    return
  }
  
  // Handle static assets with cache-first strategy
  if (
    request.destination === 'script' ||
    request.destination === 'style' ||
    request.destination === 'font' ||
    request.destination === 'image'
  ) {
    event.respondWith(cacheFirstStrategy(request, CACHE_NAME))
    return
  }
  
  // Handle navigation requests with network-first (for index.html)
  if (request.mode === 'navigate') {
    event.respondWith(networkFirstStrategy(request, CACHE_NAME))
    return
  }
  
  // Default: network-first for everything else
  event.respondWith(networkFirstStrategy(request, CACHE_NAME))
})

/**
 * Cache-first strategy
 * Try cache first, fall back to network if not cached
 * Best for static assets that don't change
 */
async function cacheFirstStrategy(request, cacheName) {
  try {
    // Try to get from cache first
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Not in cache, fetch from network
    const networkResponse = await fetch(request)
    
    // Cache the response for future use
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.error('[Service Worker] Cache-first strategy failed:', error)
    
    // Try to return from cache as last resort
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline page or error response
    return new Response('Offline', {
      status: 503,
      statusText: 'Service Unavailable'
    })
  }
}

/**
 * Network-first strategy
 * Try network first, fall back to cache if offline
 * Best for API calls and dynamic content
 */
async function networkFirstStrategy(request, cacheName) {
  try {
    // Try network first
    const networkResponse = await fetch(request)
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.log('[Service Worker] Network failed, trying cache:', error.message)
    
    // Network failed, try cache
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Both network and cache failed
    return new Response('Offline', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'text/plain' }
    })
  }
}

// Handle messages from clients
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    const urls = event.data.urls || []
    event.waitUntil(
      caches.open(CACHE_NAME)
        .then((cache) => cache.addAll(urls))
    )
  }
})
