import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTaskStore } from '@/stores/tasks'
import { taskService } from '@/services/taskService'

// Mock the task service
vi.mock('@/services/taskService', () => ({
  taskService: {
    getTasks: vi.fn(),
    createTask: vi.fn(),
    updateProgress: vi.fn()
  }
}))

describe('Task Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('state initialization', () => {
    it('should initialize with empty tasks array', () => {
      const store = useTaskStore()
      expect(store.tasks).toEqual([])
    })

    it('should initialize with loading false', () => {
      const store = useTaskStore()
      expect(store.loading).toBe(false)
    })

    it('should initialize with null error', () => {
      const store = useTaskStore()
      expect(store.error).toBe(null)
    })
  })

  describe('getters', () => {
    it('should filter pending tasks', () => {
      const store = useTaskStore()
      store.tasks = [
        { id: 1, status: 'pending' } as any,
        { id: 2, status: 'claimed' } as any,
        { id: 3, status: 'pending' } as any,
        { id: 4, status: 'completed' } as any
      ]

      expect(store.pendingTasks).toHaveLength(2)
      expect(store.pendingTasks[0].id).toBe(1)
      expect(store.pendingTasks[1].id).toBe(3)
    })

    it('should filter claimed tasks', () => {
      const store = useTaskStore()
      store.tasks = [
        { id: 1, status: 'pending' } as any,
        { id: 2, status: 'claimed' } as any,
        { id: 3, status: 'claimed' } as any
      ]

      expect(store.claimedTasks).toHaveLength(2)
      expect(store.claimedTasks[0].id).toBe(2)
    })

    it('should filter completed tasks', () => {
      const store = useTaskStore()
      store.tasks = [
        { id: 1, status: 'completed' } as any,
        { id: 2, status: 'pending' } as any
      ]

      expect(store.completedTasks).toHaveLength(1)
      expect(store.completedTasks[0].id).toBe(1)
    })

    it('should filter failed tasks', () => {
      const store = useTaskStore()
      store.tasks = [
        { id: 1, status: 'failed' } as any,
        { id: 2, status: 'pending' } as any,
        { id: 3, status: 'failed' } as any
      ]

      expect(store.failedTasks).toHaveLength(2)
    })
  })

  describe('fetchTasks action', () => {
    it('should fetch tasks successfully', async () => {
      const store = useTaskStore()
      const mockTasks = [
        { id: 1, status: 'pending' },
        { id: 2, status: 'claimed' }
      ]
      
      vi.mocked(taskService.getTasks).mockResolvedValue({
        success: true,
        data: mockTasks,
        pagination: {
          total: 2,
          page: 1,
          per_page: 10,
          total_pages: 1
        }
      })

      await store.fetchTasks()
      
      expect(store.tasks).toEqual(mockTasks)
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
    })

    it('should set loading to true while fetching', async () => {
      const store = useTaskStore()
      
      vi.mocked(taskService.getTasks).mockImplementation(() => 
        new Promise(resolve => {
          expect(store.loading).toBe(true)
          resolve({
            success: true,
            data: [],
            pagination: { total: 0, page: 1, per_page: 10, total_pages: 0 }
          })
        })
      )

      await store.fetchTasks()
    })

    it('should handle fetch error', async () => {
      const store = useTaskStore()
      const errorMessage = 'Network error'
      
      vi.mocked(taskService.getTasks).mockRejectedValue(new Error(errorMessage))

      await store.fetchTasks()
      
      expect(store.error).toBe(errorMessage)
      expect(store.loading).toBe(false)
    })

    it('should pass parameters to service', async () => {
      const store = useTaskStore()
      const params = { status: 'pending', type: 'test' }
      
      vi.mocked(taskService.getTasks).mockResolvedValue({
        success: true,
        data: [],
        pagination: { total: 0, page: 1, per_page: 10, total_pages: 0 }
      })

      await store.fetchTasks(params)
      
      expect(taskService.getTasks).toHaveBeenCalledWith(params)
    })
  })

  describe('createTask action', () => {
    it('should create task successfully', async () => {
      const store = useTaskStore()
      const newTask = { id: 1, type: 'test', status: 'pending' }
      
      vi.mocked(taskService.createTask).mockResolvedValue({
        success: true,
        data: newTask as any
      })

      const taskData = { type: 'test', params: { key: 'value' } }
      const result = await store.createTask(taskData)
      
      expect(result.success).toBe(true)
      expect(store.tasks[0]).toEqual(newTask)
    })

    it('should add new task to beginning of list', async () => {
      const store = useTaskStore()
      store.tasks = [{ id: 1, status: 'pending' } as any]
      
      const newTask = { id: 2, type: 'test', status: 'pending' }
      vi.mocked(taskService.createTask).mockResolvedValue({
        success: true,
        data: newTask as any
      })

      const taskData = { type: 'test', params: {} }
      await store.createTask(taskData)
      
      expect(store.tasks[0].id).toBe(2)
      expect(store.tasks).toHaveLength(2)
    })

    it('should handle create error', async () => {
      const store = useTaskStore()
      const errorMessage = 'Failed to create task'
      
      vi.mocked(taskService.createTask).mockRejectedValue(new Error(errorMessage))

      const taskData = { type: 'test', params: {} }
      await expect(store.createTask(taskData)).rejects.toThrow()
      expect(store.error).toBe(errorMessage)
    })

    it('should pass priority parameter', async () => {
      const store = useTaskStore()
      
      vi.mocked(taskService.createTask).mockResolvedValue({
        success: true,
        data: { id: 1 } as any
      })

      const taskData = { type: 'test', params: { key: 'value' }, priority: 5 }
      await store.createTask(taskData)
      
      expect(taskService.createTask).toHaveBeenCalledWith(taskData)
    })
  })

  describe('updateProgress action', () => {
    it('should update task progress', async () => {
      const store = useTaskStore()
      store.tasks = [
        { id: 1, progress: 0, status: 'claimed' } as any
      ]
      
      vi.mocked(taskService.updateProgress).mockResolvedValue({
        success: true
      })

      await store.updateProgress(1, 'worker-1', 50)
      
      expect(store.tasks[0].progress).toBe(50)
      expect(taskService.updateProgress).toHaveBeenCalledWith(1, {
        worker_id: 'worker-1',
        progress: 50,
        message: undefined
      })
    })

    it('should pass optional message', async () => {
      const store = useTaskStore()
      store.tasks = [{ id: 1, progress: 0 } as any]
      
      vi.mocked(taskService.updateProgress).mockResolvedValue({
        success: true
      })

      await store.updateProgress(1, 'worker-1', 75, 'Processing...')
      
      expect(taskService.updateProgress).toHaveBeenCalledWith(1, {
        worker_id: 'worker-1',
        progress: 75,
        message: 'Processing...'
      })
    })

    it('should handle update error', async () => {
      const store = useTaskStore()
      store.tasks = [{ id: 1, progress: 0 } as any]
      
      vi.mocked(taskService.updateProgress).mockRejectedValue(new Error('Update failed'))

      await expect(store.updateProgress(1, 'worker-1', 50)).rejects.toThrow()
    })
  })

  describe('clearError action', () => {
    it('should clear error', () => {
      const store = useTaskStore()
      store.error = 'Some error'
      
      store.clearError()
      
      expect(store.error).toBe(null)
    })
  })
})
