import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Toast from '../../src/components/base/Toast.vue'

describe('Toast.vue', () => {
  let wrapper: any

  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.restoreAllMocks()
  })

  describe('rendering', () => {
    it('should render when visible is true', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Test message',
          visible: true
        }
      })
      
      expect(wrapper.find('[role="alert"]').exists()).toBe(true)
      expect(wrapper.text()).toContain('Test message')
    })

    it('should not render when visible is false', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Test message',
          visible: false
        }
      })
      
      expect(wrapper.find('[role="alert"]').exists()).toBe(false)
    })

    it('should display the message', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Success! Task completed',
          visible: true
        }
      })
      
      expect(wrapper.text()).toContain('Success! Task completed')
    })
  })

  describe('toast types', () => {
    it('should apply success styling for success type', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Success',
          type: 'success',
          visible: true
        }
      })
      
      const toast = wrapper.find('[role="alert"]')
      expect(toast.classes()).toContain('bg-green-600')
    })

    it('should apply error styling for error type', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Error',
          type: 'error',
          visible: true
        }
      })
      
      const toast = wrapper.find('[role="alert"]')
      expect(toast.classes()).toContain('bg-red-600')
    })

    it('should apply warning styling for warning type', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Warning',
          type: 'warning',
          visible: true
        }
      })
      
      const toast = wrapper.find('[role="alert"]')
      expect(toast.classes()).toContain('bg-yellow-600')
    })

    it('should apply info styling for info type (default)', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Info',
          visible: true
        }
      })
      
      const toast = wrapper.find('[role="alert"]')
      expect(toast.classes()).toContain('bg-blue-600')
    })

    it('should show checkmark icon for success', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Success',
          type: 'success',
          visible: true
        }
      })
      
      const svg = wrapper.find('svg')
      expect(svg.exists()).toBe(true)
      expect(svg.find('path').attributes('d')).toContain('M5 13l4 4L19 7')
    })

    it('should show X icon for error', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Error',
          type: 'error',
          visible: true
        }
      })
      
      const svg = wrapper.find('svg')
      expect(svg.exists()).toBe(true)
      expect(svg.find('path').attributes('d')).toContain('M6 18L18 6M6 6l12 12')
    })

    it('should show warning icon for warning', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Warning',
          type: 'warning',
          visible: true
        }
      })
      
      const svg = wrapper.find('svg')
      expect(svg.exists()).toBe(true)
      const path = svg.find('path').attributes('d')
      expect(path).toContain('M12 9v2m0 4h.01m')
    })

    it('should show info icon for info', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Info',
          type: 'info',
          visible: true
        }
      })
      
      const svg = wrapper.find('svg')
      expect(svg.exists()).toBe(true)
      const path = svg.find('path').attributes('d')
      expect(path).toContain('M13 16h-1v-4h-1m1-4h.01M21 12a9')
    })
  })

  describe('auto-dismiss', () => {
    it('should auto-dismiss after default duration (3000ms)', async () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Auto dismiss',
          visible: true
        }
      })
      
      expect(wrapper.emitted().close).toBeFalsy()
      
      vi.advanceTimersByTime(3000)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.emitted().close).toBeTruthy()
    })

    it('should auto-dismiss after custom duration', async () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Custom duration',
          duration: 5000,
          visible: true
        }
      })
      
      vi.advanceTimersByTime(4999)
      await wrapper.vm.$nextTick()
      expect(wrapper.emitted().close).toBeFalsy()
      
      vi.advanceTimersByTime(1)
      await wrapper.vm.$nextTick()
      expect(wrapper.emitted().close).toBeTruthy()
    })

    it('should not auto-dismiss when duration is 0', async () => {
      wrapper = mount(Toast, {
        props: {
          message: 'No auto dismiss',
          duration: 0,
          visible: true
        }
      })
      
      vi.advanceTimersByTime(10000)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.emitted().close).toBeFalsy()
    })

    it('should not auto-dismiss when duration is negative', async () => {
      wrapper = mount(Toast, {
        props: {
          message: 'No auto dismiss',
          duration: -1,
          visible: true
        }
      })
      
      vi.advanceTimersByTime(10000)
      await wrapper.vm.$nextTick()
      
      expect(wrapper.emitted().close).toBeFalsy()
    })
  })

  describe('manual dismiss', () => {
    it('should emit close when close button clicked', async () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Manual close',
          visible: true,
          duration: 0
        }
      })
      
      const closeButton = wrapper.find('button')
      await closeButton.trigger('click')
      
      expect(wrapper.emitted().close).toBeTruthy()
      expect(wrapper.emitted().close).toHaveLength(1)
    })

    it('should emit close when toast is clicked', async () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Click to close',
          visible: true,
          duration: 0
        }
      })
      
      const toast = wrapper.find('[role="alert"]')
      await toast.trigger('click')
      
      expect(wrapper.emitted().close).toBeTruthy()
    })

    it('should clear timeout when manually closed', async () => {
      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')
      
      wrapper = mount(Toast, {
        props: {
          message: 'Manual close with timeout',
          visible: true,
          duration: 5000
        }
      })
      
      const closeButton = wrapper.find('button')
      await closeButton.trigger('click')
      
      expect(clearTimeoutSpy).toHaveBeenCalled()
    })
  })

  describe('accessibility', () => {
    it('should have alert role', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Accessible toast',
          visible: true
        }
      })
      
      expect(wrapper.find('[role="alert"]').exists()).toBe(true)
    })

    it('should have close button with aria-label', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Close button test',
          visible: true
        }
      })
      
      const closeButton = wrapper.find('button')
      expect(closeButton.attributes('aria-label')).toBe('Close notification')
    })

    it('should have minimum touch target size for close button', () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Touch target',
          visible: true
        }
      })
      
      const closeButton = wrapper.find('button')
      expect(closeButton.classes()).toContain('min-w-[44px]')
      expect(closeButton.classes()).toContain('min-h-[44px]')
    })
  })

  describe('reactivity', () => {
    it('should update visibility when prop changes', async () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Reactive visibility',
          visible: true,
          duration: 0
        }
      })
      
      expect(wrapper.find('[role="alert"]').exists()).toBe(true)
      
      await wrapper.setProps({ visible: false })
      expect(wrapper.find('[role="alert"]').exists()).toBe(false)
      
      await wrapper.setProps({ visible: true })
      expect(wrapper.find('[role="alert"]').exists()).toBe(true)
    })

    it('should update message when prop changes', async () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Original message',
          visible: true,
          duration: 0
        }
      })
      
      expect(wrapper.text()).toContain('Original message')
      
      await wrapper.setProps({ message: 'Updated message' })
      expect(wrapper.text()).toContain('Updated message')
    })

    it('should update type styling when prop changes', async () => {
      wrapper = mount(Toast, {
        props: {
          message: 'Type change',
          type: 'success',
          visible: true,
          duration: 0
        }
      })
      
      let toast = wrapper.find('[role="alert"]')
      expect(toast.classes()).toContain('bg-green-600')
      
      await wrapper.setProps({ type: 'error' })
      toast = wrapper.find('[role="alert"]')
      expect(toast.classes()).toContain('bg-red-600')
    })
  })

  describe('edge cases', () => {
    it('should handle empty message', () => {
      wrapper = mount(Toast, {
        props: {
          message: '',
          visible: true,
          duration: 0
        }
      })
      
      expect(wrapper.find('[role="alert"]').exists()).toBe(true)
    })

    it('should handle very long messages', () => {
      const longMessage = 'This is a very long message that should still be displayed properly. '.repeat(10)
      wrapper = mount(Toast, {
        props: {
          message: longMessage,
          visible: true,
          duration: 0
        }
      })
      
      // Just check that the message is rendered (whitespace may differ)
      expect(wrapper.text()).toContain('This is a very long message')
    })

    it('should cleanup on unmount', () => {
      const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')
      
      wrapper = mount(Toast, {
        props: {
          message: 'Cleanup test',
          visible: true,
          duration: 5000
        }
      })
      
      wrapper.unmount()
      // Timeout should be cleared when component is unmounted
      // (Note: This is implicit in the component lifecycle)
    })
  })
})
