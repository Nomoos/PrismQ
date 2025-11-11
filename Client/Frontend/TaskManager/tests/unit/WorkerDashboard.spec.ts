import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import WorkerDashboard from '../../src/views/WorkerDashboard.vue'
import { useTaskStore } from '../../src/stores/tasks'
import { useWorkerStore } from '../../src/stores/worker'
import type { Task } from '../../src/types'

// Mock router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
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

describe('WorkerDashboard.vue', () => {
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
    workerStore = useWorkerStore()
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('component rendering', () => {
    it('should render the component', () => {
      wrapper = mount(WorkerDashboard)
      expect(wrapper.exists()).toBe(true)
    })

    it('should display header with title', () => {
      wrapper = mount(WorkerDashboard)
      const header = wrapper.find('header')
      expect(header.exists()).toBe(true)
      expect(header.text()).toContain('Worker Dashboard')
    })

    it('should render worker information card', () => {
      wrapper = mount(WorkerDashboard)
      expect(wrapper.text()).toContain('Worker Information')
    })

    it('should render task statistics card', () => {
      wrapper = mount(WorkerDashboard)
      expect(wrapper.text()).toContain('Task Statistics')
    })

    it('should render task actions card', () => {
      wrapper = mount(WorkerDashboard)
      expect(wrapper.text()).toContain('Task Actions')
    })
  })

  describe('worker information', () => {
    it('should display worker ID when initialized', () => {
      workerStore.workerId = 'worker-123'
      workerStore.isInitialized = true
      
      wrapper = mount(WorkerDashboard)
      expect(wrapper.text()).toContain('worker-123')
    })

    it('should show "Not initialized" when worker is not initialized', () => {
      workerStore.workerId = null
      workerStore.isInitialized = false
      
      wrapper = mount(WorkerDashboard)
      expect(wrapper.text()).toContain('Not initialized')
    })

    it('should display worker status', () => {
      workerStore.status = 'active'
      
      wrapper = mount(WorkerDashboard)
      const statusBadge = wrapper.findComponent({ name: 'StatusBadge' })
      expect(statusBadge.exists()).toBe(true)
      expect(statusBadge.props('status')).toBe('active')
    })

    it('should show initialize button when worker is not initialized', () => {
      workerStore.isInitialized = false
      
      wrapper = mount(WorkerDashboard)
      const initButton = wrapper.find('button')
      expect(initButton.text()).toContain('Initialize Worker')
    })

    it('should show status buttons when worker is initialized', () => {
      workerStore.isInitialized = true
      
      wrapper = mount(WorkerDashboard)
      expect(wrapper.text()).toContain('Set Active')
      expect(wrapper.text()).toContain('Set Idle')
    })

    it('should call initializeWorker when init button is clicked', async () => {
      workerStore.isInitialized = false
      workerStore.initializeWorker = vi.fn()
      
      wrapper = mount(WorkerDashboard)
      await wrapper.vm.initWorker()
      
      expect(workerStore.initializeWorker).toHaveBeenCalled()
    })

    it('should disable Set Active button when worker is already active', () => {
      workerStore.isInitialized = true
      workerStore.status = 'active'
      
      wrapper = mount(WorkerDashboard)
      const buttons = wrapper.findAll('button')
      const activeButton = buttons.find((b: any) => b.text().includes('Set Active'))
      
      expect(activeButton?.attributes('disabled')).toBeDefined()
    })

    it('should disable Set Idle button when worker is already idle', () => {
      workerStore.isInitialized = true
      workerStore.status = 'idle'
      
      wrapper = mount(WorkerDashboard)
      const buttons = wrapper.findAll('button')
      const idleButton = buttons.find((b: any) => b.text().includes('Set Idle'))
      
      expect(idleButton?.attributes('disabled')).toBeDefined()
    })
  })

  describe('task statistics', () => {
    beforeEach(() => {
      // Setup mock tasks
      taskStore.tasks = [
        createMockTask({ id: 1, status: 'pending' }),
        createMockTask({ id: 2, status: 'pending' }),
        createMockTask({ id: 3, status: 'claimed' }),
        createMockTask({ id: 4, status: 'completed' }),
        createMockTask({ id: 5, status: 'completed' }),
        createMockTask({ id: 6, status: 'completed' }),
        createMockTask({ id: 7, status: 'failed' })
      ]
    })

    it('should display correct pending task count', () => {
      wrapper = mount(WorkerDashboard)
      
      const stats = wrapper.text()
      expect(stats).toContain('2') // 2 pending tasks
      expect(stats).toContain('Pending')
    })

    it('should display correct claimed task count', () => {
      wrapper = mount(WorkerDashboard)
      
      const stats = wrapper.text()
      expect(stats).toContain('1') // 1 claimed task
      expect(stats).toContain('Claimed')
    })

    it('should display correct completed task count', () => {
      wrapper = mount(WorkerDashboard)
      
      const stats = wrapper.text()
      expect(stats).toContain('3') // 3 completed tasks
      expect(stats).toContain('Completed')
    })

    it('should display correct failed task count', () => {
      wrapper = mount(WorkerDashboard)
      
      const stats = wrapper.text()
      expect(stats).toContain('1') // 1 failed task
      expect(stats).toContain('Failed')
    })

    it('should show zero counts when no tasks exist', () => {
      taskStore.tasks = []
      
      wrapper = mount(WorkerDashboard)
      
      // All counts should be 0
      const stats = wrapper.findAll('.text-2xl')
      stats.forEach((stat: any) => {
        expect(stat.text()).toBe('0')
      })
    })
  })

  describe('claim next task', () => {
    it('should show claim next task button', () => {
      workerStore.isInitialized = true
      
      wrapper = mount(WorkerDashboard)
      expect(wrapper.text()).toContain('Claim Next Task')
    })

    it('should disable claim button when worker is not initialized', () => {
      workerStore.isInitialized = false
      
      wrapper = mount(WorkerDashboard)
      const claimButton = wrapper.find('button')
      expect(claimButton.classes()).toContain('opacity-50')
      expect(claimButton.classes()).toContain('cursor-not-allowed')
    })

    it('should disable claim button when no tasks are available', () => {
      workerStore.isInitialized = true
      wrapper = mount(WorkerDashboard)
      
      // Set no available task types
      wrapper.vm.availableTaskTypes = []
      await wrapper.vm.$nextTick()
      
      const buttons = wrapper.findAll('button')
      const claimButton = buttons.find((b: any) => b.text().includes('Claim Next Task'))
      
      expect(claimButton?.attributes('disabled')).toBeDefined()
    })

    it('should show "Claiming..." when claim is in progress', async () => {
      workerStore.isInitialized = true
      
      wrapper = mount(WorkerDashboard)
      wrapper.vm.claimingTask = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('Claiming...')
    })

    it('should show error message when claim fails', async () => {
      workerStore.isInitialized = true
      
      wrapper = mount(WorkerDashboard)
      wrapper.vm.claimError = 'Failed to claim task'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toContain('Failed to claim task')
    })

    it('should call claimTask when claim button is clicked', async () => {
      workerStore.isInitialized = true
      workerStore.workerId = 'test-worker'
      taskStore.claimTask = vi.fn().mockResolvedValue(createMockTask())
      
      wrapper = mount(WorkerDashboard)
      wrapper.vm.availableTaskTypes = ['test-type']
      await wrapper.vm.$nextTick()
      
      await wrapper.vm.claimNextTask()
      
      expect(taskStore.claimTask).toHaveBeenCalledWith('test-worker', expect.any(String))
    })

    it('should show success toast when task is claimed successfully', async () => {
      workerStore.isInitialized = true
      workerStore.workerId = 'test-worker'
      const mockTask = createMockTask({ id: 123 })
      taskStore.claimTask = vi.fn().mockResolvedValue(mockTask)
      
      wrapper = mount(WorkerDashboard)
      wrapper.vm.availableTaskTypes = ['test-type']
      await wrapper.vm.$nextTick()
      
      await wrapper.vm.claimNextTask()
      await wrapper.vm.$nextTick()
      
      expect(mockToastSuccess).toHaveBeenCalled()
    })

    it('should show error when claim fails', async () => {
      workerStore.isInitialized = true
      workerStore.workerId = 'test-worker'
      taskStore.claimTask = vi.fn().mockRejectedValue(new Error('Claim failed'))
      
      wrapper = mount(WorkerDashboard)
      wrapper.vm.availableTaskTypes = ['test-type']
      await wrapper.vm.$nextTick()
      
      await wrapper.vm.claimNextTask()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.claimError).toBeTruthy()
    })
  })

  describe('worker status changes', () => {
    it('should call setStatus when Set Active is clicked', async () => {
      workerStore.isInitialized = true
      workerStore.status = 'idle'
      workerStore.setStatus = vi.fn()
      
      wrapper = mount(WorkerDashboard)
      await wrapper.vm.setActive()
      
      expect(workerStore.setStatus).toHaveBeenCalledWith('active')
    })

    it('should call setStatus when Set Idle is clicked', async () => {
      workerStore.isInitialized = true
      workerStore.status = 'active'
      workerStore.setStatus = vi.fn()
      
      wrapper = mount(WorkerDashboard)
      await wrapper.vm.setIdle()
      
      expect(workerStore.setStatus).toHaveBeenCalledWith('idle')
    })

    it('should show success toast when status changes to active', async () => {
      workerStore.isInitialized = true
      workerStore.status = 'idle'
      workerStore.setStatus = vi.fn().mockResolvedValue(undefined)
      
      wrapper = mount(WorkerDashboard)
      await wrapper.vm.setActive()
      await wrapper.vm.$nextTick()
      
      expect(mockToastSuccess).toHaveBeenCalledWith('Worker status set to active')
    })

    it('should show success toast when status changes to idle', async () => {
      workerStore.isInitialized = true
      workerStore.status = 'active'
      workerStore.setStatus = vi.fn().mockResolvedValue(undefined)
      
      wrapper = mount(WorkerDashboard)
      await wrapper.vm.setIdle()
      await wrapper.vm.$nextTick()
      
      expect(mockToastSuccess).toHaveBeenCalledWith('Worker status set to idle')
    })
  })

  describe('color coding', () => {
    it('should use yellow color for pending tasks', () => {
      wrapper = mount(WorkerDashboard)
      const pendingCard = wrapper.find('.bg-yellow-50')
      expect(pendingCard.exists()).toBe(true)
    })

    it('should use blue color for claimed tasks', () => {
      wrapper = mount(WorkerDashboard)
      const claimedCard = wrapper.find('.bg-blue-50')
      expect(claimedCard.exists()).toBe(true)
    })

    it('should use green color for completed tasks', () => {
      wrapper = mount(WorkerDashboard)
      const completedCard = wrapper.find('.bg-green-50')
      expect(completedCard.exists()).toBe(true)
    })

    it('should use red color for failed tasks', () => {
      wrapper = mount(WorkerDashboard)
      const failedCard = wrapper.find('.bg-red-50')
      expect(failedCard.exists()).toBe(true)
    })
  })

  describe('responsive layout', () => {
    it('should use grid layout for statistics', () => {
      wrapper = mount(WorkerDashboard)
      const grid = wrapper.find('.grid.grid-cols-2')
      expect(grid.exists()).toBe(true)
    })

    it('should have proper spacing classes', () => {
      wrapper = mount(WorkerDashboard)
      const main = wrapper.find('main')
      expect(main.classes()).toContain('space-y-4')
    })

    it('should have proper padding on mobile', () => {
      wrapper = mount(WorkerDashboard)
      const main = wrapper.find('main')
      expect(main.classes()).toContain('px-4')
      expect(main.classes()).toContain('py-6')
    })
  })

  describe('accessibility', () => {
    it('should have proper heading hierarchy', () => {
      wrapper = mount(WorkerDashboard)
      const h1 = wrapper.find('h1')
      expect(h1.text()).toBe('Worker Dashboard')
      
      const h2s = wrapper.findAll('h2')
      expect(h2s.length).toBeGreaterThan(0)
    })

    it('should have proper button labels', () => {
      workerStore.isInitialized = true
      
      wrapper = mount(WorkerDashboard)
      const buttons = wrapper.findAll('button')
      
      buttons.forEach((button: any) => {
        expect(button.text().length).toBeGreaterThan(0)
      })
    })

    it('should use semantic HTML structure', () => {
      wrapper = mount(WorkerDashboard)
      
      expect(wrapper.find('header').exists()).toBe(true)
      expect(wrapper.find('main').exists()).toBe(true)
    })
  })
})
