import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { 
  initPerformanceMonitoring,
  markPerformance,
  measurePerformance,
  getPerformanceMetrics,
  logPerformanceMetrics
} from '@/utils/performance'

// Mock web-vitals
vi.mock('web-vitals', () => ({
  onCLS: vi.fn(),
  onINP: vi.fn(),
  onLCP: vi.fn(),
  onFCP: vi.fn(),
  onTTFB: vi.fn()
}))

describe('Performance Utilities', () => {
  let consoleLogSpy: any
  let consoleWarnSpy: any
  let consoleGroupSpy: any
  let consoleGroupEndSpy: any

  beforeEach(() => {
    consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    consoleGroupSpy = vi.spyOn(console, 'group').mockImplementation(() => {})
    consoleGroupEndSpy = vi.spyOn(console, 'groupEnd').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('initPerformanceMonitoring', () => {
    it('should initialize all Core Web Vitals tracking', async () => {
      const { onCLS, onINP, onLCP, onFCP, onTTFB } = await import('web-vitals')

      initPerformanceMonitoring()

      expect(onCLS).toHaveBeenCalled()
      expect(onINP).toHaveBeenCalled()
      expect(onLCP).toHaveBeenCalled()
      expect(onFCP).toHaveBeenCalled()
      expect(onTTFB).toHaveBeenCalled()
    })

    it('should pass callback function to each web vital', async () => {
      const { onCLS, onINP, onLCP, onFCP, onTTFB } = await import('web-vitals')

      initPerformanceMonitoring()

      expect(vi.mocked(onCLS).mock.calls[0][0]).toBeTypeOf('function')
      expect(vi.mocked(onINP).mock.calls[0][0]).toBeTypeOf('function')
      expect(vi.mocked(onLCP).mock.calls[0][0]).toBeTypeOf('function')
      expect(vi.mocked(onFCP).mock.calls[0][0]).toBeTypeOf('function')
      expect(vi.mocked(onTTFB).mock.calls[0][0]).toBeTypeOf('function')
    })
  })

  describe('markPerformance', () => {
    it('should create a performance mark when performance API is available', () => {
      const mockMark = vi.fn()
      global.performance = {
        mark: mockMark
      } as any

      markPerformance('test-mark')

      expect(mockMark).toHaveBeenCalledWith('test-mark')
    })

    it('should handle missing performance API gracefully', () => {
      // @ts-ignore
      global.performance = undefined

      expect(() => markPerformance('test-mark')).not.toThrow()
    })

    it('should handle missing mark method gracefully', () => {
      global.performance = {} as any

      expect(() => markPerformance('test-mark')).not.toThrow()
    })
  })

  describe('measurePerformance', () => {
    it('should measure performance between two marks', () => {
      const mockMeasure = vi.fn()
      const mockGetEntriesByName = vi.fn().mockReturnValue([
        { duration: 150.5 }
      ])

      global.performance = {
        measure: mockMeasure,
        getEntriesByName: mockGetEntriesByName
      } as any

      const duration = measurePerformance('test-measure', 'start-mark', 'end-mark')

      expect(mockMeasure).toHaveBeenCalledWith('test-measure', 'start-mark', 'end-mark')
      expect(mockGetEntriesByName).toHaveBeenCalledWith('test-measure')
      expect(duration).toBe(150.5)
    })

    it('should measure from mark to now when endMark is not provided', () => {
      const mockMeasure = vi.fn()
      const mockGetEntriesByName = vi.fn().mockReturnValue([
        { duration: 100 }
      ])

      global.performance = {
        measure: mockMeasure,
        getEntriesByName: mockGetEntriesByName
      } as any

      const duration = measurePerformance('test-measure', 'start-mark')

      expect(mockMeasure).toHaveBeenCalledWith('test-measure', 'start-mark', undefined)
      expect(duration).toBe(100)
    })

    it('should return 0 when performance API is not available', () => {
      // @ts-ignore
      global.performance = undefined

      const duration = measurePerformance('test-measure', 'start-mark')

      expect(duration).toBe(0)
    })

    it('should handle measure errors gracefully', () => {
      const mockMeasure = vi.fn().mockImplementation(() => {
        throw new Error('Mark not found')
      })

      global.performance = {
        measure: mockMeasure
      } as any

      const duration = measurePerformance('test-measure', 'invalid-mark')

      expect(duration).toBe(0)
      expect(consoleWarnSpy).toHaveBeenCalled()
    })

    it('should return 0 when measure method is not available', () => {
      global.performance = {} as any

      const duration = measurePerformance('test-measure', 'start-mark')

      expect(duration).toBe(0)
    })
  })

  describe('getPerformanceMetrics', () => {
    it('should return performance metrics when navigation timing is available', () => {
      const mockNavigationTiming = {
        domContentLoadedEventEnd: 2000,
        domContentLoadedEventStart: 1900,
        domInteractive: 1500,
        fetchStart: 100,
        loadEventEnd: 3000
      }

      global.performance = {
        getEntriesByType: vi.fn().mockReturnValue([mockNavigationTiming])
      } as any

      const metrics = getPerformanceMetrics()

      expect(metrics).toHaveLength(3)
      expect(metrics[0]).toEqual({
        metric: 'DOM Content Loaded',
        value: 100,
        rating: 'good',
        delta: 0
      })
      expect(metrics[1]).toEqual({
        metric: 'DOM Interactive',
        value: 1400,
        rating: 'good',
        delta: 0
      })
      expect(metrics[2]).toEqual({
        metric: 'Load Complete',
        value: 2900,
        rating: 'good',
        delta: 0
      })
    })

    it('should return empty array when performance API is not available', () => {
      // @ts-ignore
      global.performance = undefined

      const metrics = getPerformanceMetrics()

      expect(metrics).toEqual([])
    })

    it('should return empty array when getEntriesByType is not available', () => {
      global.performance = {} as any

      const metrics = getPerformanceMetrics()

      expect(metrics).toEqual([])
    })

    it('should return empty array when navigation timing is not available', () => {
      global.performance = {
        getEntriesByType: vi.fn().mockReturnValue([])
      } as any

      const metrics = getPerformanceMetrics()

      expect(metrics).toEqual([])
    })
  })

  describe('logPerformanceMetrics', () => {
    it('should log metrics in development mode', () => {
      const mockNavigationTiming = {
        domContentLoadedEventEnd: 2000,
        domContentLoadedEventStart: 1900,
        domInteractive: 1500,
        fetchStart: 100,
        loadEventEnd: 3000
      }

      global.performance = {
        getEntriesByType: vi.fn().mockReturnValue([mockNavigationTiming])
      } as any

      // Mock DEV environment
      vi.stubGlobal('import', {
        meta: {
          env: {
            DEV: true
          }
        }
      })

      logPerformanceMetrics()

      expect(consoleGroupSpy).toHaveBeenCalledWith('[Performance Metrics]')
      expect(consoleLogSpy).toHaveBeenCalled()
      expect(consoleGroupEndSpy).toHaveBeenCalled()
    })

    it('should handle missing performance API gracefully', () => {
      // @ts-ignore
      global.performance = undefined

      expect(() => logPerformanceMetrics()).not.toThrow()
    })
  })
})
