/**
 * Debounce utility for performance optimization
 * Delays function execution until after a wait period of inactivity
 */

/**
 * Debounce a function call
 * @param fn Function to debounce
 * @param delay Delay in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null

  return function (this: any, ...args: Parameters<T>) {
    if (timeoutId !== null) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      fn.apply(this, args)
      timeoutId = null
    }, delay)
  }
}

/**
 * Throttle a function call
 * Ensures function is called at most once per specified time period
 * @param fn Function to throttle
 * @param limit Time limit in milliseconds
 * @returns Throttled function
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false

  return function (this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      fn.apply(this, args)
      inThrottle = true
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}

/**
 * Request idle callback wrapper with fallback
 * @param callback Function to call during idle time
 * @param options Options for idle callback
 */
export function requestIdleCallback(
  callback: IdleRequestCallback,
  options?: IdleRequestOptions
): number {
  if ('requestIdleCallback' in window) {
    return window.requestIdleCallback(callback, options)
  } else {
    // Fallback for browsers that don't support requestIdleCallback
    return setTimeout(() => {
      const start = Date.now()
      callback({
        didTimeout: false,
        timeRemaining: () => Math.max(0, 50 - (Date.now() - start))
      })
    }, 1) as unknown as number
  }
}

/**
 * Cancel idle callback with fallback
 * @param id Idle callback ID
 */
export function cancelIdleCallback(id: number): void {
  if ('cancelIdleCallback' in window) {
    window.cancelIdleCallback(id)
  } else {
    clearTimeout(id)
  }
}
