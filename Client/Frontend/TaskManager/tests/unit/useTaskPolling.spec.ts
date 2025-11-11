import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useTaskPolling } from '@/composables/useTaskPolling'
import { setActivePinia, createPinia } from 'pinia'
import { useTaskStore } from '@/stores/tasks'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'

// Mock task service
vi.mock('@/services/taskService', () => ({
  taskService: {
    getTasks: vi.fn().mockResolvedValue({
      success: true,
      data: [],
      pagination: { total: 0, page: 1, per_page: 10, total_pages: 0 }
    })
  }
}))

describe('useTaskPolling Composable', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllTimers()
    vi.restoreAllMocks()
  })

  describe('initialization', () => {
    it('should start polling automatically when autoStart is true', async () => {
      const TestComponent = defineComponent({
        setup() {
          const polling = useTaskPolling(1000, true)
          return () => h('div', polling.isPolling.value ? 'polling' : 'not polling')
        }
      })

      const wrapper = mount(TestComponent)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toBe('polling')
    })

    it('should not start polling automatically when autoStart is false', async () => {
      const TestComponent = defineComponent({
        setup() {
          const polling = useTaskPolling(1000, false)
          return () => h('div', polling.isPolling.value ? 'polling' : 'not polling')
        }
      })

      const wrapper = mount(TestComponent)
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toBe('not polling')
    })

    it('should use default interval of 5000ms when not specified', async () => {
      const taskStore = useTaskStore()
      vi.clearAllMocks()
      const fetchTasksSpy = vi.spyOn(taskStore, 'fetchTasks')

      const TestComponent = defineComponent({
        setup() {
          useTaskPolling(undefined, true)
          return () => h('div')
        }
      })

      mount(TestComponent)
      await vi.runOnlyPendingTimersAsync()

      // Verify polling was started
      expect(fetchTasksSpy).toHaveBeenCalled()
    })
  })

  describe('startPolling', () => {
    it('should fetch tasks immediately when starting', async () => {
      const taskStore = useTaskStore()
      vi.clearAllMocks()
      const fetchTasksSpy = vi.spyOn(taskStore, 'fetchTasks')

      const TestComponent = defineComponent({
        setup() {
          const polling = useTaskPolling(1000, false)
          polling.startPolling()
          return () => h('div')
        }
      })

      mount(TestComponent)
      await vi.runOnlyPendingTimersAsync()

      // Should be called at least once (immediately on start)
      expect(fetchTasksSpy).toHaveBeenCalled()
    })

    it('should fetch tasks at regular intervals', async () => {
      const taskStore = useTaskStore()
      vi.clearAllMocks()
      const fetchTasksSpy = vi.spyOn(taskStore, 'fetchTasks')

      const TestComponent = defineComponent({
        setup() {
          const polling = useTaskPolling(1000, false)
          polling.startPolling()
          return () => h('div')
        }
      })

      mount(TestComponent)
      await vi.runOnlyPendingTimersAsync()

      expect(fetchTasksSpy).toHaveBeenCalled()
      const initialCalls = fetchTasksSpy.mock.calls.length

      vi.advanceTimersByTime(1000)
      await vi.runOnlyPendingTimersAsync()
      expect(fetchTasksSpy.mock.calls.length).toBeGreaterThan(initialCalls)
    })

    it('should set isPolling to true', async () => {
      const TestComponent = defineComponent({
        setup() {
          const polling = useTaskPolling(1000, false)
          return { polling }
        },
        template: '<div></div>'
      })

      const wrapper = mount(TestComponent)
      
      expect(wrapper.vm.polling.isPolling.value).toBe(false)
      
      wrapper.vm.polling.startPolling()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.polling.isPolling.value).toBe(true)
    })

    it('should not start polling if already polling', async () => {
      const taskStore = useTaskStore()
      vi.clearAllMocks()
      const fetchTasksSpy = vi.spyOn(taskStore, 'fetchTasks')

      const TestComponent = defineComponent({
        setup() {
          const polling = useTaskPolling(1000, false)
          return { polling }
        },
        template: '<div></div>'
      })

      const wrapper = mount(TestComponent)
      
      wrapper.vm.polling.startPolling()
      await vi.runOnlyPendingTimersAsync()
      
      const callCount = fetchTasksSpy.mock.calls.length
      
      // Try to start again
      wrapper.vm.polling.startPolling()
      await vi.runOnlyPendingTimersAsync()
      
      // Should not increase call count significantly (at most one more from interval)
      expect(fetchTasksSpy.mock.calls.length).toBeLessThanOrEqual(callCount + 1)
    })
  })

  describe('stopPolling', () => {
    it('should stop fetching tasks', async () => {
      const taskStore = useTaskStore()
      vi.clearAllMocks()
      const fetchTasksSpy = vi.spyOn(taskStore, 'fetchTasks')

      const TestComponent = defineComponent({
        setup() {
          const polling = useTaskPolling(1000, false)
          return { polling }
        },
        template: '<div></div>'
      })

      const wrapper = mount(TestComponent)
      
      wrapper.vm.polling.startPolling()
      await vi.runOnlyPendingTimersAsync()
      
      const callCount = fetchTasksSpy.mock.calls.length
      
      wrapper.vm.polling.stopPolling()
      
      vi.advanceTimersByTime(5000)
      await vi.runOnlyPendingTimersAsync()
      
      // Should not have made any more calls
      expect(fetchTasksSpy.mock.calls.length).toBe(callCount)
    })

    it('should set isPolling to false', async () => {
      const TestComponent = defineComponent({
        setup() {
          const polling = useTaskPolling(1000, false)
          return { polling }
        },
        template: '<div></div>'
      })

      const wrapper = mount(TestComponent)
      
      wrapper.vm.polling.startPolling()
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.polling.isPolling.value).toBe(true)
      
      wrapper.vm.polling.stopPolling()
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.polling.isPolling.value).toBe(false)
    })

    it('should handle stopping when not polling gracefully', () => {
      const TestComponent = defineComponent({
        setup() {
          const polling = useTaskPolling(1000, false)
          return { polling }
        },
        template: '<div></div>'
      })

      const wrapper = mount(TestComponent)
      
      expect(() => wrapper.vm.polling.stopPolling()).not.toThrow()
    })
  })

  describe('cleanup on unmount', () => {
    it('should stop polling when component is unmounted', async () => {
      const taskStore = useTaskStore()
      vi.clearAllMocks()
      const fetchTasksSpy = vi.spyOn(taskStore, 'fetchTasks')

      const TestComponent = defineComponent({
        setup() {
          useTaskPolling(1000, true)
          return () => h('div')
        }
      })

      const wrapper = mount(TestComponent)
      await vi.runOnlyPendingTimersAsync()
      
      const callCount = fetchTasksSpy.mock.calls.length
      
      wrapper.unmount()
      
      vi.advanceTimersByTime(5000)
      await vi.runOnlyPendingTimersAsync()
      
      // Should not have made any more calls after unmount
      expect(fetchTasksSpy.mock.calls.length).toBe(callCount)
    })
  })
})
