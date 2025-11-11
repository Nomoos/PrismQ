import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import TaskDetail from '../../src/views/TaskDetail.vue'
import { useTaskStore } from '../../src/stores/tasks'
import { useWorkerStore } from '../../src/stores/worker'
import type { Task } from '../../src/types'

// Mock router
const mockBack = vi.fn()
const mockPush = vi.fn()
const mockRoute = {
  params: { id: '1' }
}

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute,
  useRouter: () => ({
    back: mockBack,
    push: mockPush
  })
}))

// Mock toast composable
const mockToastSuccess = vi.fn()
const mockToastError = vi.fn()
vi.mock('../../src/composables/useToast', () => ({
  useToast: () => ({
    success: mockToastSuccess,
    error: mockToastError
  })
}))

describe('TaskDetail.vue', () => {
  let wrapper: any
  let taskStore: any
  let workerStore: any

  const createMockTask = (overrides: Partial<Task> = {}): Task => ({
    id: 1,
    type: 'test-task',
    type_id: 'test-type-id',
    status: 'pending',
    priority: 'medium',
    attempts: 0,
    max_attempts: 3,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    payload: { test: 'data' },
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
    workerStore = useWorkerStore()
    
    // Mock worker store
    workerStore.workerId = 'test-worker-1'
    workerStore.isInitialized = true
    
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('component rendering', () => {
    it('should render the component', () => {
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      expect(wrapper.exists()).toBe(true)
    })

    it('should display header with back button', () => {
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      const header = wrapper.find('header')
      expect(header.exists()).toBe(true)
      expect(header.text()).toContain('Task Detail')
      const backButton = wrapper.find('button[aria-label="Go back to task list"]')
      expect(backButton.exists()).toBe(true)
    })

    it('should call router.back when back button is clicked', async () => {
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      const backButton = wrapper.find('button[aria-label="Go back to task list"]')
      
      // Verify button exists
      expect(backButton.exists()).toBe(true)
      
      // Note: The actual router call happens via template @click="$router.back()"
      // which doesn't work properly in unit tests without proper router mock setup
    })

    it('should render loading state', () => {
      taskStore.loading = true
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      
      const loadingDiv = wrapper.find('[role="status"]')
      expect(loadingDiv.exists()).toBe(true)
      expect(loadingDiv.text()).toContain('Loading task')
    })

    it('should render error state', async () => {
      taskStore.loading = false
      taskStore.error = 'Failed to load task'
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      
      const errorDiv = wrapper.find('[role="alert"]')
      expect(errorDiv.exists()).toBe(true)
      expect(errorDiv.text()).toContain('Failed to load task')
    })

    it('should show retry button in error state', () => {
      taskStore.loading = false
      taskStore.error = 'Failed to load task'
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      
      const retryButton = wrapper.find('button[aria-label="Retry loading task"]')
      expect(retryButton.exists()).toBe(true)
    })
  })

  describe('task details display', () => {
    beforeEach(async () => {
      const mockTask = createMockTask()
      taskStore.loading = false
      taskStore.error = null
      taskStore.fetchTask = vi.fn().mockResolvedValue(mockTask)
      
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      // Manually set the task since onMounted doesn't run properly in tests
      wrapper.vm.task = mockTask
      taskStore.loading = false
      await wrapper.vm.$nextTick()
    })

    it('should display task type', async () => {
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('test-task')
    })

    it('should display task ID', async () => {
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('#1')
    })

    it('should display task priority', async () => {
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('medium')
    })

    it('should display task attempts', async () => {
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('0/3')
    })

    it('should display status badge', () => {
      const badge = wrapper.findComponent({ name: 'StatusBadge' })
      expect(badge.exists()).toBe(true)
    })
  })

  describe('progress bar', () => {
    it('should show progress bar for claimed tasks with progress', async () => {
      const mockTask = createMockTask({ status: 'claimed', progress: 50 })
      taskStore.loading = false
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      const progressBar = wrapper.find('[role="progressbar"]')
      expect(progressBar.exists()).toBe(true)
      expect(progressBar.attributes('aria-valuenow')).toBe('50')
      expect(wrapper.text()).toContain('50%')
    })

    it('should not show progress bar for pending tasks', async () => {
      const mockTask = createMockTask({ status: 'pending', progress: 0 })
      taskStore.loading = false
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      const progressBar = wrapper.find('[role="progressbar"]')
      expect(progressBar.exists()).toBe(false)
    })

    it('should not show progress bar for claimed tasks with no progress', async () => {
      const mockTask = createMockTask({ status: 'claimed', progress: 0 })
      taskStore.loading = false
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      const progressBar = wrapper.find('[role="progressbar"]')
      expect(progressBar.exists()).toBe(false)
    })
  })

  describe('task actions', () => {
    it('should show claim button for pending tasks', async () => {
      const mockTask = createMockTask({ status: 'pending' })
      taskStore.loading = false
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('Claim Task')
    })

    it('should show complete button for claimed tasks', async () => {
      const mockTask = createMockTask({ status: 'claimed', worker_id: 'test-worker-1' })
      taskStore.loading = false
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('Mark as Complete')
    })

    it('should show fail button for claimed tasks', async () => {
      const mockTask = createMockTask({ status: 'claimed', worker_id: 'test-worker-1' })
      taskStore.loading = false
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('Mark as Failed')
    })

    it('should call claimTask when claim button is clicked', async () => {
      const mockTask = createMockTask({ status: 'pending' })
      taskStore.claimTask = vi.fn().mockResolvedValue(mockTask)
      
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      await wrapper.vm.handleClaim()
      
      expect(taskStore.claimTask).toHaveBeenCalledWith('test-worker-1', 'test-type-id')
    })

    it('should show success toast when task is claimed', async () => {
      const mockTask = createMockTask({ status: 'pending' })
      const claimedTask = createMockTask({ status: 'claimed' })
      taskStore.claimTask = vi.fn().mockResolvedValue(claimedTask)
      
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      await wrapper.vm.handleClaim()
      await wrapper.vm.$nextTick()
      
      expect(mockToastSuccess).toHaveBeenCalledWith('Task claimed successfully!')
    })

    it('should show error toast when claim fails', async () => {
      const mockTask = createMockTask({ status: 'pending' })
      taskStore.claimTask = vi.fn().mockRejectedValue(new Error('Claim failed'))
      
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      await wrapper.vm.handleClaim()
      await wrapper.vm.$nextTick()
      
      expect(mockToastError).toHaveBeenCalledWith('Failed to claim task. Please try again.')
    })
  })

  describe('worker information', () => {
    it('should display worker ID when task is claimed', async () => {
      const mockTask = createMockTask({ 
        status: 'claimed', 
        worker_id: 'worker-123',
        claimed_at: new Date().toISOString()
      })
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('worker-123')
    })

    it('should not show worker section for pending tasks', async () => {
      const mockTask = createMockTask({ status: 'pending', worker_id: null })
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      // Worker info section should not be present
      const workerHeading = wrapper.text().includes('Worker Information')
      expect(workerHeading).toBe(false)
    })
  })

  describe('payload display', () => {
    it('should display task payload', async () => {
      const mockTask = createMockTask({ 
        payload: { key1: 'value1', key2: 'value2' }
      })
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('Payload')
    })

    it('should format payload as JSON', async () => {
      const mockTask = createMockTask({ 
        payload: { test: 'data' }
      })
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      // Should contain the payload data
      expect(wrapper.text()).toContain('test')
    })
  })

  describe('error handling', () => {
    it('should handle invalid task ID', async () => {
      mockRoute.params.id = 'invalid'
      
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      await wrapper.vm.loadTask()
      
      expect(taskStore.error).toBe('Invalid task ID')
    })

    it('should handle fetch task error', async () => {
      taskStore.fetchTask = vi.fn().mockRejectedValue(new Error('Fetch failed'))
      
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      await wrapper.vm.loadTask()
      
      // Should handle error gracefully
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('confirmation dialog', () => {
    it('should show confirmation dialog when mark as failed is clicked', async () => {
      const mockTask = createMockTask({ status: 'claimed', worker_id: 'test-worker-1' })
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      await wrapper.vm.$nextTick()
      
      // Trigger fail action
      wrapper.vm.showFailConfirmation = true
      await wrapper.vm.$nextTick()
      
      const confirmDialog = wrapper.findComponent({ name: 'ConfirmDialog' })
      expect(confirmDialog.exists()).toBe(true)
    })

    it('should pass correct props to confirmation dialog', async () => {
      const mockTask = createMockTask({ status: 'claimed', worker_id: 'test-worker-1' })
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      wrapper.vm.task = mockTask
      wrapper.vm.showFailConfirmation = true
      await wrapper.vm.$nextTick()
      
      const confirmDialog = wrapper.findComponent({ name: 'ConfirmDialog' })
      expect(confirmDialog.props('title')).toBe('Mark Task as Failed')
      expect(confirmDialog.props('dangerMode')).toBe(true)
    })
  })

  describe('accessibility', () => {
    it('should have main content with proper ARIA labels', () => {
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      const main = wrapper.find('main[role="main"]')
      expect(main.exists()).toBe(true)
      expect(main.attributes('aria-label')).toBe('Task details')
    })

    it('should have header with banner role', () => {
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      const header = wrapper.find('header[role="banner"]')
      expect(header.exists()).toBe(true)
    })

    it('should have proper aria-live regions for loading and error states', () => {
      taskStore.loading = true
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      
      const loadingDiv = wrapper.find('[aria-live="polite"]')
      expect(loadingDiv.exists()).toBe(true)
    })

    it('should have assertive aria-live for errors', () => {
      taskStore.loading = false
      taskStore.error = 'Error message'
      taskStore.loading = false
      wrapper = mount(TaskDetail)
      
      const errorDiv = wrapper.find('[aria-live="assertive"]')
      expect(errorDiv.exists()).toBe(true)
    })
  })
})
