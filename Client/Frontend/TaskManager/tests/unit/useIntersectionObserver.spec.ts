import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { useIntersectionObserver, useLazyLoad } from '../../src/composables/useIntersectionObserver'

// Mock IntersectionObserver
class MockIntersectionObserver {
  callback: IntersectionObserverCallback
  options: IntersectionObserverInit
  elements: Set<Element>

  constructor(callback: IntersectionObserverCallback, options: IntersectionObserverInit = {}) {
    this.callback = callback
    this.options = options
    this.elements = new Set()
  }

  observe(element: Element) {
    this.elements.add(element)
  }

  unobserve(element: Element) {
    this.elements.delete(element)
  }

  disconnect() {
    this.elements.clear()
  }

  // Helper to trigger intersection
  triggerIntersection(isIntersecting: boolean) {
    const entries = Array.from(this.elements).map(element => ({
      target: element,
      isIntersecting,
      intersectionRatio: isIntersecting ? 1 : 0,
      boundingClientRect: {} as DOMRectReadOnly,
      intersectionRect: {} as DOMRectReadOnly,
      rootBounds: null,
      time: Date.now()
    }))
    this.callback(entries as IntersectionObserverEntry[], this as any)
  }
}

describe('useIntersectionObserver', () => {
  let mockObserver: MockIntersectionObserver
  let originalIntersectionObserver: any

  beforeEach(() => {
    // Save original and mock IntersectionObserver
    originalIntersectionObserver = global.IntersectionObserver
    mockObserver = new MockIntersectionObserver(() => {})
    
    global.IntersectionObserver = vi.fn((callback, options) => {
      mockObserver = new MockIntersectionObserver(callback, options)
      return mockObserver as any
    }) as any
  })

  afterEach(() => {
    global.IntersectionObserver = originalIntersectionObserver
  })

  describe('basic functionality', () => {
    it('should initialize with correct default values', () => {
      const { isIntersecting, hasIntersected, elementRef } = useIntersectionObserver()
      
      expect(isIntersecting.value).toBe(false)
      expect(hasIntersected.value).toBe(false)
      expect(elementRef.value).toBe(null)
    })

    it('should expose elementRef, isIntersecting, and hasIntersected', () => {
      const result = useIntersectionObserver()
      
      expect(result).toHaveProperty('elementRef')
      expect(result).toHaveProperty('isIntersecting')
      expect(result).toHaveProperty('hasIntersected')
    })

    it('should accept custom options', () => {
      const customOptions = {
        rootMargin: '50px',
        threshold: 0.5
      }
      
      const result = useIntersectionObserver(customOptions)
      
      // Should not throw and return expected interface
      expect(result.elementRef).toBeDefined()
      expect(result.isIntersecting).toBeDefined()
      expect(result.hasIntersected).toBeDefined()
    })
  })

  describe('with component integration', () => {
    it('should work when used in a component', async () => {
      let composableResult: any

      const TestComponent = defineComponent({
        setup() {
          composableResult = useIntersectionObserver()
          return () => h('div', { ref: composableResult.elementRef }, 'Test')
        }
      })

      const wrapper = mount(TestComponent)
      
      expect(composableResult.isIntersecting.value).toBe(false)
      expect(composableResult.hasIntersected.value).toBe(false)
      
      wrapper.unmount()
    })

    it('should create observer when element is mounted', async () => {
      const TestComponent = defineComponent({
        setup() {
          const result = useIntersectionObserver()
          return () => h('div', { ref: result.elementRef }, 'Test')
        }
      })

      const wrapper = mount(TestComponent)
      await wrapper.vm.$nextTick()
      
      // Observer should be created
      expect(global.IntersectionObserver).toHaveBeenCalled()
      
      wrapper.unmount()
    })
  })

  describe('fallback behavior', () => {
    it('should fallback when IntersectionObserver is not supported', () => {
      // Remove IntersectionObserver from window
      const temp = global.IntersectionObserver
      delete (global as any).IntersectionObserver
      
      const TestComponent = defineComponent({
        setup() {
          const result = useIntersectionObserver()
          return () => h('div', { ref: result.elementRef }, 'Test')
        }
      })

      expect(() => mount(TestComponent)).not.toThrow()
      
      // Restore
      global.IntersectionObserver = temp
    })
  })

  describe('custom options', () => {
    it('should accept rootMargin option', () => {
      const options = { rootMargin: '100px' }
      const result = useIntersectionObserver(options)
      
      expect(result.elementRef).toBeDefined()
    })

    it('should accept threshold option', () => {
      const options = { threshold: 0.75 }
      const result = useIntersectionObserver(options)
      
      expect(result.elementRef).toBeDefined()
    })

    it('should accept array of thresholds', () => {
      const options = { threshold: [0, 0.25, 0.5, 0.75, 1] }
      const result = useIntersectionObserver(options)
      
      expect(result.elementRef).toBeDefined()
    })

    it('should accept root element option', () => {
      const root = document.createElement('div')
      const options = { root }
      const result = useIntersectionObserver(options)
      
      expect(result.elementRef).toBeDefined()
    })
  })
})

describe('useLazyLoad', () => {
  let originalIntersectionObserver: any

  beforeEach(() => {
    originalIntersectionObserver = global.IntersectionObserver
    
    global.IntersectionObserver = vi.fn((callback, options) => {
      return new MockIntersectionObserver(callback, options) as any
    }) as any
  })

  afterEach(() => {
    global.IntersectionObserver = originalIntersectionObserver
  })

  describe('basic functionality', () => {
    it('should initialize with shouldLoad as false', () => {
      const { shouldLoad, elementRef } = useLazyLoad()
      
      expect(shouldLoad.value).toBe(false)
      expect(elementRef.value).toBe(null)
    })

    it('should expose elementRef and shouldLoad', () => {
      const result = useLazyLoad()
      
      expect(result).toHaveProperty('elementRef')
      expect(result).toHaveProperty('shouldLoad')
    })

    it('should accept custom options', () => {
      const customOptions = {
        rootMargin: '200px',
        threshold: 0.1
      }
      
      const result = useLazyLoad(customOptions)
      
      expect(result.elementRef).toBeDefined()
      expect(result.shouldLoad).toBeDefined()
    })
  })

  describe('with component integration', () => {
    it('should work when used in a component', () => {
      let composableResult: any

      const TestComponent = defineComponent({
        setup() {
          composableResult = useLazyLoad()
          return () => h('div', { ref: composableResult.elementRef }, 'Test')
        }
      })

      const wrapper = mount(TestComponent)
      
      expect(composableResult.shouldLoad.value).toBe(false)
      
      wrapper.unmount()
    })
  })

  describe('fallback behavior', () => {
    it('should not throw when IntersectionObserver is not supported', () => {
      const temp = global.IntersectionObserver
      delete (global as any).IntersectionObserver
      
      const TestComponent = defineComponent({
        setup() {
          const result = useLazyLoad()
          return () => h('div', { ref: result.elementRef }, 'Test')
        }
      })

      expect(() => mount(TestComponent)).not.toThrow()
      
      global.IntersectionObserver = temp
    })
  })
})

