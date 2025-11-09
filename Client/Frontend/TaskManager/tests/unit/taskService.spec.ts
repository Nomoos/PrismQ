import { describe, it, expect, vi, beforeEach } from 'vitest'
import { taskService } from '@/services/taskService'
import api from '@/services/api'

// Mock the api module
vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

describe('Task Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getTasks', () => {
    it('should fetch tasks with no parameters', async () => {
      const mockResponse = {
        success: true,
        data: [{ id: 1 }],
        pagination: { total: 1, page: 1, per_page: 10, total_pages: 1 }
      }
      
      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await taskService.getTasks()
      
      expect(api.get).toHaveBeenCalledWith('/tasks', undefined)
      expect(result).toEqual(mockResponse)
    })

    it('should fetch tasks with filters', async () => {
      const params = { status: 'pending', type: 'test' }
      
      vi.mocked(api.get).mockResolvedValue({
        success: true,
        data: [],
        pagination: { total: 0, page: 1, per_page: 10, total_pages: 0 }
      })

      await taskService.getTasks(params)
      
      expect(api.get).toHaveBeenCalledWith('/tasks', params)
    })
  })

  describe('getTask', () => {
    it('should fetch single task by id', async () => {
      const mockTask = { id: 1, status: 'pending' }
      
      vi.mocked(api.get).mockResolvedValue({
        success: true,
        data: mockTask
      })

      const result = await taskService.getTask(1)
      
      expect(api.get).toHaveBeenCalledWith('/tasks/1')
      expect(result.data).toEqual(mockTask)
    })
  })

  describe('createTask', () => {
    it('should create task with required fields', async () => {
      const taskData = {
        type: 'test.task',
        params: { key: 'value' }
      }
      
      vi.mocked(api.post).mockResolvedValue({
        success: true,
        data: { id: 1, ...taskData }
      })

      const result = await taskService.createTask(taskData)
      
      expect(api.post).toHaveBeenCalledWith('/tasks', taskData)
      expect(result.success).toBe(true)
    })

    it('should create task with priority', async () => {
      const taskData = {
        type: 'test.task',
        params: {},
        priority: 5
      }
      
      vi.mocked(api.post).mockResolvedValue({
        success: true,
        data: { id: 1 }
      })

      await taskService.createTask(taskData)
      
      expect(api.post).toHaveBeenCalledWith('/tasks', taskData)
    })
  })

  describe('claimTask', () => {
    it('should claim task with worker id and task type', async () => {
      vi.mocked(api.post).mockResolvedValue({
        success: true,
        data: { id: 1, status: 'claimed' }
      })

      const claimData = {
        worker_id: 'worker-1',
        task_type_id: 123
      }

      await taskService.claimTask(claimData)
      
      expect(api.post).toHaveBeenCalledWith('/tasks/claim', claimData)
    })
  })

  describe('completeTask', () => {
    it('should complete task successfully', async () => {
      vi.mocked(api.post).mockResolvedValue({
        success: true,
        data: { id: 1, status: 'completed' }
      })

      const completeData = {
        worker_id: 'worker-1',
        success: true,
        result: { output: 'data' }
      }

      await taskService.completeTask(1, completeData)
      
      expect(api.post).toHaveBeenCalledWith('/tasks/1/complete', completeData)
    })

    it('should complete task with error', async () => {
      vi.mocked(api.post).mockResolvedValue({
        success: true,
        data: { id: 1, status: 'failed' }
      })

      const completeData = {
        worker_id: 'worker-1',
        success: false,
        error: 'Error occurred'
      }

      await taskService.completeTask(1, completeData)
      
      expect(api.post).toHaveBeenCalledWith('/tasks/1/complete', completeData)
    })
  })

  describe('updateProgress', () => {
    it('should update progress without message', async () => {
      vi.mocked(api.post).mockResolvedValue({
        success: true
      })

      const progressData = {
        worker_id: 'worker-1',
        progress: 50
      }

      await taskService.updateProgress(1, progressData)
      
      expect(api.post).toHaveBeenCalledWith('/tasks/1/progress', progressData)
    })

    it('should update progress with message', async () => {
      vi.mocked(api.post).mockResolvedValue({
        success: true
      })

      const progressData = {
        worker_id: 'worker-1',
        progress: 75,
        message: 'Processing items...'
      }

      await taskService.updateProgress(1, progressData)
      
      expect(api.post).toHaveBeenCalledWith('/tasks/1/progress', progressData)
    })
  })

  describe('getTaskTypes', () => {
    it('should fetch active task types by default', async () => {
      vi.mocked(api.get).mockResolvedValue({
        success: true,
        data: [],
        pagination: { total: 0, page: 1, per_page: 10, total_pages: 0 }
      })

      await taskService.getTaskTypes()
      
      expect(api.get).toHaveBeenCalledWith('/task-types', { active_only: true })
    })

    it('should fetch all task types when specified', async () => {
      vi.mocked(api.get).mockResolvedValue({
        success: true,
        data: [],
        pagination: { total: 0, page: 1, per_page: 10, total_pages: 0 }
      })

      await taskService.getTaskTypes(false)
      
      expect(api.get).toHaveBeenCalledWith('/task-types', { active_only: false })
    })
  })

  describe('getTaskType', () => {
    it('should fetch task type by name', async () => {
      vi.mocked(api.get).mockResolvedValue({
        success: true,
        data: { name: 'test.task', version: '1.0' }
      })

      await taskService.getTaskType('test.task')
      
      expect(api.get).toHaveBeenCalledWith('/task-types/test.task')
    })
  })

  describe('registerTaskType', () => {
    it('should register new task type', async () => {
      const taskTypeData = {
        name: 'test.task',
        version: '1.0',
        param_schema: { type: 'object' }
      }
      
      vi.mocked(api.post).mockResolvedValue({
        success: true,
        data: { id: 1, ...taskTypeData }
      })

      await taskService.registerTaskType(taskTypeData)
      
      expect(api.post).toHaveBeenCalledWith('/task-types/register', taskTypeData)
    })
  })
})
