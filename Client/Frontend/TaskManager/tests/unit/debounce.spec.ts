import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { debounce, throttle, requestIdleCallback, cancelIdleCallback } from '@/utils/debounce'

describe('Debounce Utility', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('debounce', () => {
    it('should delay function execution', () => {
      const fn = vi.fn()
      const debouncedFn = debounce(fn, 100)

      debouncedFn()
      expect(fn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(50)
      expect(fn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(50)
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should cancel previous calls when called multiple times', () => {
      const fn = vi.fn()
      const debouncedFn = debounce(fn, 100)

      debouncedFn()
      vi.advanceTimersByTime(50)
      debouncedFn()
      vi.advanceTimersByTime(50)
      debouncedFn()
      
      expect(fn).not.toHaveBeenCalled()
      
      vi.advanceTimersByTime(100)
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should pass arguments correctly', () => {
      const fn = vi.fn()
      const debouncedFn = debounce(fn, 100)

      debouncedFn('arg1', 'arg2')
      vi.advanceTimersByTime(100)

      expect(fn).toHaveBeenCalledWith('arg1', 'arg2')
    })

    it('should preserve this context', () => {
      const obj = {
        value: 42,
        method: vi.fn(function(this: any) {
          return this.value
        })
      }
      
      const debouncedMethod = debounce(obj.method, 100)
      debouncedMethod.call(obj)
      
      vi.advanceTimersByTime(100)
      expect(obj.method).toHaveBeenCalled()
    })

    it('should work with different delay values', () => {
      const fn = vi.fn()
      const debouncedFn = debounce(fn, 500)

      debouncedFn()
      vi.advanceTimersByTime(499)
      expect(fn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(1)
      expect(fn).toHaveBeenCalledTimes(1)
    })
  })

  describe('throttle', () => {
    it('should execute function immediately on first call', () => {
      const fn = vi.fn()
      const throttledFn = throttle(fn, 100)

      throttledFn()
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should ignore calls within throttle period', () => {
      const fn = vi.fn()
      const throttledFn = throttle(fn, 100)

      throttledFn()
      throttledFn()
      throttledFn()

      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should allow execution after throttle period expires', () => {
      const fn = vi.fn()
      const throttledFn = throttle(fn, 100)

      throttledFn()
      expect(fn).toHaveBeenCalledTimes(1)

      vi.advanceTimersByTime(50)
      throttledFn()
      expect(fn).toHaveBeenCalledTimes(1)

      vi.advanceTimersByTime(50)
      throttledFn()
      expect(fn).toHaveBeenCalledTimes(2)
    })

    it('should pass arguments correctly', () => {
      const fn = vi.fn()
      const throttledFn = throttle(fn, 100)

      throttledFn('test', 123)
      expect(fn).toHaveBeenCalledWith('test', 123)
    })

    it('should preserve this context', () => {
      const obj = {
        value: 42,
        method: vi.fn(function(this: any) {
          return this.value
        })
      }
      
      const throttledMethod = throttle(obj.method, 100)
      throttledMethod.call(obj)
      
      expect(obj.method).toHaveBeenCalled()
    })
  })

  describe('requestIdleCallback', () => {
    it('should use native requestIdleCallback when available', () => {
      const callback = vi.fn()
      const mockRequestIdleCallback = vi.fn().mockReturnValue(123)
      
      // @ts-ignore - mock window.requestIdleCallback
      window.requestIdleCallback = mockRequestIdleCallback

      const id = requestIdleCallback(callback)

      expect(mockRequestIdleCallback).toHaveBeenCalledWith(callback, undefined)
      expect(id).toBe(123)

      // @ts-ignore - cleanup
      delete window.requestIdleCallback
    })

    it('should fall back to setTimeout when requestIdleCallback is not available', () => {
      const callback = vi.fn()
      
      // Ensure requestIdleCallback is not available
      // @ts-ignore
      delete window.requestIdleCallback

      const id = requestIdleCallback(callback)

      // In Node/jsdom environment, setTimeout returns a Timeout object, not a number
      expect(id).toBeDefined()
      expect(callback).not.toHaveBeenCalled()

      vi.advanceTimersByTime(1)
      expect(callback).toHaveBeenCalled()

      // Verify the callback receives the expected interface
      const callbackArg = callback.mock.calls[0][0]
      expect(callbackArg).toHaveProperty('didTimeout', false)
      expect(callbackArg).toHaveProperty('timeRemaining')
      expect(typeof callbackArg.timeRemaining).toBe('function')
    })

    it('should pass options to native requestIdleCallback', () => {
      const callback = vi.fn()
      const options = { timeout: 1000 }
      const mockRequestIdleCallback = vi.fn().mockReturnValue(123)
      
      // @ts-ignore
      window.requestIdleCallback = mockRequestIdleCallback

      requestIdleCallback(callback, options)

      expect(mockRequestIdleCallback).toHaveBeenCalledWith(callback, options)

      // @ts-ignore - cleanup
      delete window.requestIdleCallback
    })
  })

  describe('cancelIdleCallback', () => {
    it('should use native cancelIdleCallback when available', () => {
      const mockCancelIdleCallback = vi.fn()
      
      // @ts-ignore
      window.cancelIdleCallback = mockCancelIdleCallback

      cancelIdleCallback(123)

      expect(mockCancelIdleCallback).toHaveBeenCalledWith(123)

      // @ts-ignore - cleanup
      delete window.cancelIdleCallback
    })

    it('should fall back to clearTimeout when cancelIdleCallback is not available', () => {
      // @ts-ignore
      delete window.cancelIdleCallback
      
      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')

      cancelIdleCallback(123)

      expect(clearTimeoutSpy).toHaveBeenCalledWith(123)
    })
  })
})
