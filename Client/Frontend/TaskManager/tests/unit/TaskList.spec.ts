import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TaskList from '../../src/views/TaskList.vue'
import { useTaskStore } from '../../src/stores/tasks'
import type { Task } from '../../src/types'

// Mock the composables
vi.mock('../../src/composables/useTaskPolling', () => ({
  useTaskPolling: vi.fn()
}))

// Mock router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  RouterLink: {
    template: '<a><slot /></a>'
  }
}))

describe('TaskList.vue', () => {
  let wrapper: any
  let taskStore: any

  const createMockTask = (overrides: Partial<Task> = {}): Task => ({
    id: 1,
    type: 'test-task',
    status: 'pending',
    priority: 'medium',
    attempts: 0,
    max_attempts: 3,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    payload: {},
    progress: 0,
    worker_id: null,
    claimed_at: null,
    completed_at: null,
    failed_at: null,
    error_message: null,
    ...overrides
  })

  beforeEach(() => {
    setActivePinia(createPinia())
    taskStore = useTaskStore()
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('component rendering', () => {
    it('should render the component', () => {
      wrapper = mount(TaskList)
      expect(wrapper.exists()).toBe(true)
    })

    it('should display header with title', () => {
      wrapper = mount(TaskList)
      expect(wrapper.find('header h1').text()).toBe('TaskManager')
    })

    it('should render loading state', async () => {
      taskStore.loading = true
      wrapper = mount(TaskList)
      
      expect(wrapper.find('p').text()).toContain('Loading tasks')
    })

    it('should render error state', async () => {
      taskStore.error = 'Failed to load tasks'
      taskStore.loading = false
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toContain('Failed to load tasks')
    })

    it('should display bottom navigation', () => {
      wrapper = mount(TaskList)
      const nav = wrapper.find('nav[aria-label="Main navigation"]')
      expect(nav.exists()).toBe(true)
      expect(nav.text()).toContain('Tasks')
      expect(nav.text()).toContain('Workers')
      expect(nav.text()).toContain('Settings')
    })
  })

  describe('task filtering', () => {
    beforeEach(() => {
      taskStore.tasks = [
        createMockTask({ id: 1, status: 'pending' }),
        createMockTask({ id: 2, status: 'claimed' }),
        createMockTask({ id: 3, status: 'completed' }),
        createMockTask({ id: 4, status: 'failed' }),
        createMockTask({ id: 5, status: 'pending' })
      ]
    })

    it('should show all tasks by default', () => {
      wrapper = mount(TaskList)
      const tasks = wrapper.findAll('.card')
      expect(tasks).toHaveLength(5)
    })

    it('should filter by pending status', async () => {
      wrapper = mount(TaskList)
      const filterButtons = wrapper.findAll('button')
      
      // Click pending filter
      await filterButtons[1].trigger('click')
      await wrapper.vm.$nextTick()
      
      const tasks = wrapper.findAll('.card')
      expect(tasks).toHaveLength(2)
    })

    it('should filter by claimed status', async () => {
      wrapper = mount(TaskList)
      const filterButtons = wrapper.findAll('button')
      
      await filterButtons[2].trigger('click')
      await wrapper.vm.$nextTick()
      
      const tasks = wrapper.findAll('.card')
      expect(tasks).toHaveLength(1)
    })

    it('should filter by completed status', async () => {
      wrapper = mount(TaskList)
      const filterButtons = wrapper.findAll('button')
      
      await filterButtons[3].trigger('click')
      await wrapper.vm.$nextTick()
      
      const tasks = wrapper.findAll('.card')
      expect(tasks).toHaveLength(1)
    })

    it('should filter by failed status', async () => {
      wrapper = mount(TaskList)
      const filterButtons = wrapper.findAll('button')
      
      await filterButtons[4].trigger('click')
      await wrapper.vm.$nextTick()
      
      const tasks = wrapper.findAll('.card')
      expect(tasks).toHaveLength(1)
    })

    it('should show correct task counts in filter buttons', () => {
      wrapper = mount(TaskList)
      const text = wrapper.text()
      
      expect(text).toContain('(5)')
      expect(text).toContain('(2)')
      expect(text).toContain('(1)')
    })

    it('should show empty state when no tasks match filter', async () => {
      taskStore.tasks = [createMockTask({ status: 'pending' })]
      wrapper = mount(TaskList)
      
      const filterButtons = wrapper.findAll('button')
      await filterButtons[3].trigger('click') // Click completed
      
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('No completed tasks')
    })
  })

  describe('task display', () => {
    it('should display task type', () => {
      taskStore.tasks = [createMockTask({ type: 'email-sender' })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toContain('email-sender')
    })

    it('should display task ID', () => {
      taskStore.tasks = [createMockTask({ id: 123 })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toContain('ID: 123')
    })

    it('should display task priority', () => {
      taskStore.tasks = [createMockTask({ priority: 'high' })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toContain('Priority: high')
    })

    it('should display attempt count', () => {
      taskStore.tasks = [createMockTask({ attempts: 2, max_attempts: 3 })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toContain('Attempts: 2/3')
    })

    it('should show progress bar for claimed tasks with progress', () => {
      taskStore.tasks = [createMockTask({ status: 'claimed', progress: 50 })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toContain('50% complete')
    })

    it('should not show progress bar for tasks without progress', () => {
      taskStore.tasks = [createMockTask({ status: 'claimed', progress: 0 })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).not.toContain('% complete')
    })

    it('should not show progress bar for non-claimed tasks', () => {
      taskStore.tasks = [createMockTask({ status: 'pending', progress: 50 })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).not.toContain('% complete')
    })
  })

  describe('task navigation', () => {
    it('should navigate to task detail on click', async () => {
      taskStore.tasks = [createMockTask({ id: 123 })]
      wrapper = mount(TaskList)
      
      const taskCard = wrapper.find('.card')
      await taskCard.trigger('click')
      
      expect(mockPush).toHaveBeenCalledWith('/tasks/123')
    })

    it('should navigate to correct task when multiple tasks exist', async () => {
      taskStore.tasks = [
        createMockTask({ id: 1 }),
        createMockTask({ id: 2 }),
        createMockTask({ id: 3 })
      ]
      wrapper = mount(TaskList)
      
      const taskCards = wrapper.findAll('.card')
      await taskCards[1].trigger('click')
      
      expect(mockPush).toHaveBeenCalledWith('/tasks/2')
    })
  })

  describe('date formatting', () => {
    it('should show "Just now" for recent tasks', () => {
      const now = new Date()
      taskStore.tasks = [createMockTask({ created_at: now.toISOString() })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toContain('Just now')
    })

    it('should show minutes ago for tasks created within an hour', () => {
      const thirtyMinutesAgo = new Date(Date.now() - 30 * 60 * 1000)
      taskStore.tasks = [createMockTask({ created_at: thirtyMinutesAgo.toISOString() })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toMatch(/\d+m ago/)
    })

    it('should show hours ago for tasks created within a day', () => {
      const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000)
      taskStore.tasks = [createMockTask({ created_at: twoHoursAgo.toISOString() })]
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toMatch(/\d+h ago/)
    })

    it('should show date for tasks created more than a day ago', () => {
      const twoDaysAgo = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
      taskStore.tasks = [createMockTask({ created_at: twoDaysAgo.toISOString() })]
      wrapper = mount(TaskList)
      
      const text = wrapper.text()
      expect(text).not.toContain('Just now')
      expect(text).not.toMatch(/\d+m ago/)
    })
  })

  describe('status indicators', () => {
    it('should show yellow indicator for pending tasks', () => {
      taskStore.tasks = [createMockTask({ status: 'pending' })]
      wrapper = mount(TaskList)
      
      expect(wrapper.find('.bg-yellow-400').exists()).toBe(true)
    })

    it('should show blue indicator for claimed tasks', () => {
      taskStore.tasks = [createMockTask({ status: 'claimed' })]
      wrapper = mount(TaskList)
      
      expect(wrapper.find('.bg-blue-400').exists()).toBe(true)
    })

    it('should show green indicator for completed tasks', () => {
      taskStore.tasks = [createMockTask({ status: 'completed' })]
      wrapper = mount(TaskList)
      
      expect(wrapper.find('.bg-green-400').exists()).toBe(true)
    })

    it('should show red indicator for failed tasks', () => {
      taskStore.tasks = [createMockTask({ status: 'failed' })]
      wrapper = mount(TaskList)
      
      expect(wrapper.find('.bg-red-400').exists()).toBe(true)
    })
  })

  describe('empty states', () => {
    it('should show empty state when no tasks exist', () => {
      taskStore.tasks = []
      wrapper = mount(TaskList)
      
      expect(wrapper.text()).toContain('No all tasks')
    })

    it('should show appropriate message for each filter', async () => {
      taskStore.tasks = []
      wrapper = mount(TaskList)
      
      const filterButtons = wrapper.findAll('button')
      
      await filterButtons[1].trigger('click') // Pending
      expect(wrapper.text()).toContain('No pending tasks')
      
      await filterButtons[2].trigger('click') // Claimed
      expect(wrapper.text()).toContain('No claimed tasks')
    })
  })

  describe('error handling', () => {
    it('should show retry button on error', () => {
      taskStore.error = 'Network error'
      taskStore.loading = false
      wrapper = mount(TaskList)
      
      const retryButton = wrapper.find('button')
      expect(retryButton.text()).toBe('Retry')
    })

    it('should clear error on retry button click', async () => {
      taskStore.error = 'Network error'
      taskStore.loading = false
      taskStore.clearError = vi.fn()
      wrapper = mount(TaskList)
      
      const retryButton = wrapper.find('button')
      await retryButton.trigger('click')
      
      expect(taskStore.clearError).toHaveBeenCalled()
    })
  })

  describe('responsive behavior', () => {
    it('should render filter tabs with overflow scroll', () => {
      wrapper = mount(TaskList)
      
      const filterContainer = wrapper.find('.overflow-x-auto')
      expect(filterContainer.exists()).toBe(true)
    })

    it('should maintain active filter state across renders', async () => {
      taskStore.tasks = [
        createMockTask({ status: 'pending' }),
        createMockTask({ status: 'completed' })
      ]
      wrapper = mount(TaskList)
      
      const filterButtons = wrapper.findAll('button')
      await filterButtons[3].trigger('click') // Completed
      
      expect(wrapper.vm.currentFilter).toBe('completed')
    })
  })
})
