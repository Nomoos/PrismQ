import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTaskStore } from '@/stores/tasks'
import { taskService } from '@/services/taskService'

// Mock the task service
vi.mock('@/services/taskService', () => ({
  taskService: {
    getTasks: vi.fn(),
    getTask: vi.fn(),
    createTask: vi.fn(),
    claimTask: vi.fn(),
    completeTask: vi.fn(),
    updateProgress: vi.fn()
  }
}))

describe('Task Store - Optimistic Updates', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('completeTask with optimistic update', () => {
    it('should optimistically update task status to completed', async () => {
      const store = useTaskStore()
      const mockTask = { 
        id: 1, 
        status: 'claimed', 
        result: null,
        error_message: null 
      } as any
      
      store.tasks = [mockTask]
      
      // Mock successful completion
      vi.mocked(taskService.completeTask).mockResolvedValue({
        success: true
      })
      
      vi.mocked(taskService.getTask).mockResolvedValue({
        success: true,
        data: { ...mockTask, status: 'completed', result: { output: 'done' } }
      })

      // Start completion (should optimistically update)
      const promise = store.completeTask(1, 'worker-1', true, { output: 'done' })
      
      // Task should be immediately marked as completed (optimistic)
      expect(store.tasks[0].status).toBe('completed')
      
      // Wait for actual API call
      await promise
      
      // Verify API was called
      expect(taskService.completeTask).toHaveBeenCalledWith(1, {
        worker_id: 'worker-1',
        success: true,
        result: { output: 'done' },
        error: undefined
      })
    })

    it('should rollback optimistic update on failure', async () => {
      const store = useTaskStore()
      const mockTask = { 
        id: 1, 
        status: 'claimed',
        result: null,
        error_message: null
      } as any
      
      store.tasks = [mockTask]
      
      // Mock API failure
      vi.mocked(taskService.completeTask).mockRejectedValue(new Error('API Error'))

      // Attempt completion
      try {
        await store.completeTask(1, 'worker-1', true, { output: 'done' })
      } catch (e) {
        // Expected to throw
      }
      
      // Task should be rolled back to original status
      expect(store.tasks[0].status).toBe('claimed')
      expect(store.tasks[0].result).toBeNull()
    })

    it('should optimistically update task to failed status', async () => {
      const store = useTaskStore()
      const mockTask = { 
        id: 1, 
        status: 'claimed',
        result: null,
        error_message: null
      } as any
      
      store.tasks = [mockTask]
      
      vi.mocked(taskService.completeTask).mockResolvedValue({
        success: true
      })
      
      vi.mocked(taskService.getTask).mockResolvedValue({
        success: true,
        data: { ...mockTask, status: 'failed', error_message: 'Task failed' }
      })

      // Complete with failure
      const promise = store.completeTask(1, 'worker-1', false, undefined, 'Task failed')
      
      // Should be optimistically marked as failed
      expect(store.tasks[0].status).toBe('failed')
      expect(store.tasks[0].error_message).toBe('Task failed')
      
      await promise
    })
  })

  describe('failTask with optimistic update', () => {
    it('should optimistically update task to failed', async () => {
      const store = useTaskStore()
      const mockTask = { 
        id: 1, 
        status: 'claimed',
        error_message: null
      } as any
      
      store.tasks = [mockTask]
      
      vi.mocked(taskService.completeTask).mockResolvedValue({
        success: true
      })

      // Start failure (should optimistically update)
      const promise = store.failTask(1, 'worker-1', 'Processing error')
      
      // Should be immediately marked as failed
      expect(store.tasks[0].status).toBe('failed')
      expect(store.tasks[0].error_message).toBe('Processing error')
      
      await promise
    })

    it('should rollback on API failure', async () => {
      const store = useTaskStore()
      const mockTask = { 
        id: 1, 
        status: 'claimed',
        error_message: null
      } as any
      
      store.tasks = [mockTask]
      
      vi.mocked(taskService.completeTask).mockRejectedValue(new Error('API Error'))

      try {
        await store.failTask(1, 'worker-1', 'Processing error')
      } catch (e) {
        // Expected to throw
      }
      
      // Should be rolled back
      expect(store.tasks[0].status).toBe('claimed')
      expect(store.tasks[0].error_message).toBeNull()
    })

    it('should handle task not found', async () => {
      const store = useTaskStore()
      store.tasks = []

      await expect(store.failTask(999, 'worker-1', 'Error')).rejects.toThrow('Task not found')
    })
  })

  describe('updateProgress with optimistic update', () => {
    it('should optimistically update progress', async () => {
      const store = useTaskStore()
      const mockTask = { 
        id: 1, 
        status: 'claimed',
        progress: 0
      } as any
      
      store.tasks = [mockTask]
      
      vi.mocked(taskService.updateProgress).mockResolvedValue({
        success: true
      })

      // Start progress update
      const promise = store.updateProgress(1, 'worker-1', 50)
      
      // Should be immediately updated
      expect(store.tasks[0].progress).toBe(50)
      
      await promise
    })

    it('should rollback progress on API failure', async () => {
      const store = useTaskStore()
      const mockTask = { 
        id: 1, 
        status: 'claimed',
        progress: 25
      } as any
      
      store.tasks = [mockTask]
      
      vi.mocked(taskService.updateProgress).mockRejectedValue(new Error('API Error'))

      try {
        await store.updateProgress(1, 'worker-1', 75)
      } catch (e) {
        // Expected to throw
      }
      
      // Should be rolled back to original progress
      expect(store.tasks[0].progress).toBe(25)
    })

    it('should handle task not found', async () => {
      const store = useTaskStore()
      store.tasks = []

      await expect(store.updateProgress(999, 'worker-1', 50)).rejects.toThrow('Task not found')
    })

    it('should update progress with message', async () => {
      const store = useTaskStore()
      const mockTask = { 
        id: 1, 
        progress: 0
      } as any
      
      store.tasks = [mockTask]
      
      vi.mocked(taskService.updateProgress).mockResolvedValue({
        success: true
      })

      await store.updateProgress(1, 'worker-1', 50, 'Processing items...')
      
      expect(taskService.updateProgress).toHaveBeenCalledWith(1, {
        worker_id: 'worker-1',
        progress: 50,
        message: 'Processing items...'
      })
    })
  })

  describe('error messages', () => {
    it('should set user-friendly error message on claim failure', async () => {
      const store = useTaskStore()
      
      vi.mocked(taskService.claimTask).mockRejectedValue(new Error('Network error'))

      try {
        await store.claimTask('worker-1', 1)
      } catch (e) {
        // Expected
      }
      
      // The store preserves the actual error message from the error object
      expect(store.error).toBe('Network error')
    })

    it('should set user-friendly error message on fetch failure', async () => {
      const store = useTaskStore()
      
      vi.mocked(taskService.getTasks).mockRejectedValue(new Error('Network error'))

      await store.fetchTasks()
      
      // The store preserves the actual error message from the error object
      expect(store.error).toBe('Network error')
    })

    it('should use fallback message when error is not an Error instance', async () => {
      const store = useTaskStore()
      
      vi.mocked(taskService.getTasks).mockRejectedValue('String error')

      await store.fetchTasks()
      
      expect(store.error).toContain('Failed to fetch tasks')
    })
  })
})
