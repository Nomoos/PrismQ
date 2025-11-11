import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useToast } from '@/composables/useToast'

describe('useToast Composable', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // Clear toasts between tests by calling clear
    const { clear } = useToast()
    clear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('showToast', () => {
    it('should add a toast to the list', () => {
      const { showToast, toasts } = useToast()

      const id = showToast('Test message', 'info')

      expect(toasts.value).toHaveLength(1)
      expect(toasts.value[0]).toEqual({
        id,
        message: 'Test message',
        type: 'info',
        duration: 3000
      })
    })

    it('should return a unique id for each toast', () => {
      const { showToast } = useToast()

      const id1 = showToast('Message 1')
      const id2 = showToast('Message 2')

      expect(id1).not.toBe(id2)
    })

    it('should auto-remove toast after duration', () => {
      const { showToast, toasts } = useToast()

      showToast('Test message', 'info', 1000)
      expect(toasts.value).toHaveLength(1)

      vi.advanceTimersByTime(999)
      expect(toasts.value).toHaveLength(1)

      vi.advanceTimersByTime(1)
      expect(toasts.value).toHaveLength(0)
    })

    it('should not auto-remove toast when duration is 0', () => {
      const { showToast, toasts } = useToast()

      showToast('Persistent message', 'info', 0)
      expect(toasts.value).toHaveLength(1)

      vi.advanceTimersByTime(10000)
      expect(toasts.value).toHaveLength(1)
    })

    it('should use default duration of 3000ms when not specified', () => {
      const { showToast, toasts } = useToast()

      showToast('Test message', 'info')
      expect(toasts.value[0].duration).toBe(3000)
    })

    it('should use default type of info when not specified', () => {
      const { showToast, toasts } = useToast()

      showToast('Test message')
      expect(toasts.value[0].type).toBe('info')
    })
  })

  describe('removeToast', () => {
    it('should remove toast by id', () => {
      const { showToast, removeToast, toasts } = useToast()

      const id1 = showToast('Message 1', 'info', 0)
      const id2 = showToast('Message 2', 'info', 0)
      const id3 = showToast('Message 3', 'info', 0)

      expect(toasts.value).toHaveLength(3)

      removeToast(id2)

      expect(toasts.value).toHaveLength(2)
      expect(toasts.value.find(t => t.id === id2)).toBeUndefined()
      expect(toasts.value.find(t => t.id === id1)).toBeDefined()
      expect(toasts.value.find(t => t.id === id3)).toBeDefined()
    })

    it('should handle removing non-existent toast gracefully', () => {
      const { removeToast, toasts } = useToast()

      expect(() => removeToast(999)).not.toThrow()
      expect(toasts.value).toHaveLength(0)
    })
  })

  describe('success', () => {
    it('should create a success toast', () => {
      const { success, toasts } = useToast()

      success('Success message')

      expect(toasts.value[0].type).toBe('success')
      expect(toasts.value[0].message).toBe('Success message')
    })

    it('should use default duration of 3000ms', () => {
      const { success, toasts } = useToast()

      success('Success message')

      expect(toasts.value[0].duration).toBe(3000)
    })

    it('should accept custom duration', () => {
      const { success, toasts } = useToast()

      success('Success message', 5000)

      expect(toasts.value[0].duration).toBe(5000)
    })
  })

  describe('error', () => {
    it('should create an error toast', () => {
      const { error, toasts } = useToast()

      error('Error message')

      expect(toasts.value[0].type).toBe('error')
      expect(toasts.value[0].message).toBe('Error message')
    })

    it('should use default duration of 4000ms', () => {
      const { error, toasts } = useToast()

      error('Error message')

      expect(toasts.value[0].duration).toBe(4000)
    })

    it('should accept custom duration', () => {
      const { error, toasts } = useToast()

      error('Error message', 6000)

      expect(toasts.value[0].duration).toBe(6000)
    })
  })

  describe('warning', () => {
    it('should create a warning toast', () => {
      const { warning, toasts } = useToast()

      warning('Warning message')

      expect(toasts.value[0].type).toBe('warning')
      expect(toasts.value[0].message).toBe('Warning message')
    })

    it('should use default duration of 3500ms', () => {
      const { warning, toasts } = useToast()

      warning('Warning message')

      expect(toasts.value[0].duration).toBe(3500)
    })

    it('should accept custom duration', () => {
      const { warning, toasts } = useToast()

      warning('Warning message', 5000)

      expect(toasts.value[0].duration).toBe(5000)
    })
  })

  describe('info', () => {
    it('should create an info toast', () => {
      const { info, toasts } = useToast()

      info('Info message')

      expect(toasts.value[0].type).toBe('info')
      expect(toasts.value[0].message).toBe('Info message')
    })

    it('should use default duration of 3000ms', () => {
      const { info, toasts } = useToast()

      info('Info message')

      expect(toasts.value[0].duration).toBe(3000)
    })

    it('should accept custom duration', () => {
      const { info, toasts } = useToast()

      info('Info message', 2000)

      expect(toasts.value[0].duration).toBe(2000)
    })
  })

  describe('clear', () => {
    it('should remove all toasts', () => {
      const { success, error, warning, clear, toasts } = useToast()

      success('Success', 0)
      error('Error', 0)
      warning('Warning', 0)

      expect(toasts.value).toHaveLength(3)

      clear()

      expect(toasts.value).toHaveLength(0)
    })

    it('should work when no toasts exist', () => {
      const { clear, toasts } = useToast()

      expect(() => clear()).not.toThrow()
      expect(toasts.value).toHaveLength(0)
    })
  })

  describe('multiple toasts', () => {
    it('should handle multiple toasts with different durations', () => {
      const { showToast, toasts } = useToast()

      showToast('Toast 1', 'info', 1000)
      showToast('Toast 2', 'info', 2000)
      showToast('Toast 3', 'info', 3000)

      expect(toasts.value).toHaveLength(3)

      vi.advanceTimersByTime(1000)
      expect(toasts.value).toHaveLength(2)

      vi.advanceTimersByTime(1000)
      expect(toasts.value).toHaveLength(1)

      vi.advanceTimersByTime(1000)
      expect(toasts.value).toHaveLength(0)
    })
  })
})
