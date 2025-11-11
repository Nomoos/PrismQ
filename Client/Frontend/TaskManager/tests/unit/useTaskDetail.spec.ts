import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useTaskDetail } from '../../src/composables/useTaskDetail'
import { useTaskStore } from '../../src/stores/tasks'
import { setActivePinia, createPinia } from 'pinia'
import type { Task } from '../../src/types'

vi.mock('../../src/stores/tasks', () => ({
  useTaskStore: vi.fn()
}))

describe('useTaskDetail', () => {
  const mockTask: Task = {
    id: 1,
    type: 'test-task',
    type_id: 1,
    status: 'pending',
    priority: 1,
    attempts: 0,
    max_attempts: 3,
    progress: 0,
    created_at: '2025-11-10T12:00:00Z',
    updated_at: '2025-11-10T12:00:00Z',
    claimed_at: null,
    completed_at: null,
    worker_id: null,
    params: {},
    result: null,
    error: null
  }
  
  let mockTaskStore: any
  
  beforeEach(() => {
    setActivePinia(createPinia())
    
    mockTaskStore = {
      loading: false,
      error: null,
      fetchTask: vi.fn().mockResolvedValue(mockTask)
    }
    
    vi.mocked(useTaskStore).mockReturnValue(mockTaskStore)
  })
  
  it('initializes with correct default values', () => {
    const { task, loading, error } = useTaskDetail(1)
    
    expect(task.value).toBeNull()
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })
  
  it('loads task successfully', async () => {
    const { task, loadTask } = useTaskDetail(1)
    
    await loadTask()
    
    expect(mockTaskStore.fetchTask).toHaveBeenCalledWith(1)
    expect(task.value).toEqual(mockTask)
  })
  
  it('handles invalid task ID', async () => {
    const { loadTask } = useTaskDetail(NaN)
    
    await loadTask()
    
    expect(mockTaskStore.error).toBe('Invalid task ID')
    expect(mockTaskStore.fetchTask).not.toHaveBeenCalled()
  })
  
  it('handles fetch error', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    mockTaskStore.fetchTask.mockRejectedValue(new Error('Network error'))
    
    const { task, loadTask } = useTaskDetail(1)
    
    await loadTask()
    
    expect(task.value).toBeNull()
    expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to load task:', expect.any(Error))
    
    consoleErrorSpy.mockRestore()
  })
  
  it('refreshTask calls loadTask', async () => {
    const { refreshTask, task } = useTaskDetail(1)
    
    await refreshTask()
    
    expect(mockTaskStore.fetchTask).toHaveBeenCalledWith(1)
    expect(task.value).toEqual(mockTask)
  })
  
  it('exposes loading state from store', () => {
    mockTaskStore.loading = true
    
    const { loading } = useTaskDetail(1)
    
    expect(loading.value).toBe(true)
  })
  
  it('exposes error state from store', () => {
    mockTaskStore.error = 'Test error'
    
    const { error } = useTaskDetail(1)
    
    expect(error.value).toBe('Test error')
  })
})
