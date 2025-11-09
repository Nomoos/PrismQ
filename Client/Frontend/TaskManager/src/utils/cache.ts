/**
 * Request caching utilities for network optimization
 * Implements in-memory cache with TTL and stale-while-revalidate pattern
 */

interface CacheEntry<T> {
  data: T
  timestamp: number
  ttl: number
}

interface CacheOptions {
  ttl?: number // Time to live in milliseconds (default: 5 minutes)
  staleWhileRevalidate?: boolean // Return stale data while fetching fresh (default: true)
}

class RequestCache {
  private cache = new Map<string, CacheEntry<any>>()
  private pendingRequests = new Map<string, Promise<any>>()

  /**
   * Get cached data if valid, or execute fetch function
   * @param key Cache key
   * @param fetchFn Function to fetch fresh data
   * @param options Cache options
   */
  async get<T>(
    key: string,
    fetchFn: () => Promise<T>,
    options: CacheOptions = {}
  ): Promise<T> {
    const { ttl = 5 * 60 * 1000, staleWhileRevalidate = true } = options

    // Check if there's a pending request for this key
    const pending = this.pendingRequests.get(key)
    if (pending) {
      return pending
    }

    // Check cache
    const cached = this.cache.get(key)
    const now = Date.now()

    if (cached) {
      const age = now - cached.timestamp
      
      // Fresh data - return immediately
      if (age < cached.ttl) {
        return cached.data
      }

      // Stale data - return stale while revalidating in background
      if (staleWhileRevalidate) {
        // Return stale data immediately
        this.revalidate(key, fetchFn, ttl)
        return cached.data
      }
    }

    // No cache or cache expired without stale-while-revalidate
    return this.fetch(key, fetchFn, ttl)
  }

  /**
   * Fetch fresh data and update cache
   */
  private async fetch<T>(key: string, fetchFn: () => Promise<T>, ttl: number): Promise<T> {
    const promise = fetchFn()
    this.pendingRequests.set(key, promise)

    try {
      const data = await promise
      this.set(key, data, ttl)
      return data
    } finally {
      this.pendingRequests.delete(key)
    }
  }

  /**
   * Revalidate in background
   */
  private revalidate<T>(key: string, fetchFn: () => Promise<T>, ttl: number): void {
    // Don't revalidate if already pending
    if (this.pendingRequests.has(key)) {
      return
    }

    // Fetch in background
    this.fetch(key, fetchFn, ttl).catch(err => {
      console.warn(`Background revalidation failed for ${key}:`, err)
    })
  }

  /**
   * Set cache entry
   */
  set<T>(key: string, data: T, ttl: number = 5 * 60 * 1000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    })
  }

  /**
   * Invalidate cache entry
   */
  invalidate(key: string): void {
    this.cache.delete(key)
    this.pendingRequests.delete(key)
  }

  /**
   * Invalidate all cache entries matching a pattern
   */
  invalidatePattern(pattern: RegExp): void {
    for (const key of this.cache.keys()) {
      if (pattern.test(key)) {
        this.invalidate(key)
      }
    }
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear()
    this.pendingRequests.clear()
  }

  /**
   * Clean expired entries
   */
  cleanup(): void {
    const now = Date.now()
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key)
      }
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      pending: this.pendingRequests.size,
      keys: Array.from(this.cache.keys())
    }
  }
}

// Export singleton instance
export const requestCache = new RequestCache()

// Run cleanup every 5 minutes
if (typeof window !== 'undefined') {
  setInterval(() => {
    requestCache.cleanup()
  }, 5 * 60 * 1000)
}

export default requestCache
