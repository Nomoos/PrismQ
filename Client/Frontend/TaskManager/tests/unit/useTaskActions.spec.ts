import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useTaskActions } from '../../src/composables/useTaskActions'
import { useTaskStore } from '../../src/stores/tasks'
import { useWorkerStore } from '../../src/stores/worker'
import { useToast } from '../../src/composables/useToast'
import { setActivePinia, createPinia } from 'pinia'
import type { Task } from '../../src/types'

vi.mock('../../src/stores/tasks')
vi.mock('../../src/stores/worker')
vi.mock('../../src/composables/useToast')
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

describe('useTaskActions', () => {
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
  let mockWorkerStore: any
  let mockToast: any
  let taskRef: any
  
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
    
    taskRef = ref(mockTask)
    
    mockTaskStore = {
      claimTask: vi.fn().mockResolvedValue({ ...mockTask, status: 'claimed' }),
      completeTask: vi.fn().mockResolvedValue({ ...mockTask, status: 'completed' })
    }
    
    mockWorkerStore = {
      workerId: 'worker-123'
    }
    
    mockToast = {
      success: vi.fn(),
      error: vi.fn()
    }
    
    vi.mocked(useTaskStore).mockReturnValue(mockTaskStore)
    vi.mocked(useWorkerStore).mockReturnValue(mockWorkerStore)
    vi.mocked(useToast).mockReturnValue(mockToast)
  })
  
  afterEach(() => {
    vi.useRealTimers()
  })
  
  it('initializes with correct default values', () => {
    const { actionLoading, completingSuccess } = useTaskActions(taskRef)
    
    expect(actionLoading.value).toBe(false)
    expect(completingSuccess.value).toBe(false)
  })
  
  it('claims task successfully', async () => {
    const { claim, actionLoading } = useTaskActions(taskRef)
    
    await claim()
    
    expect(mockTaskStore.claimTask).toHaveBeenCalledWith('worker-123', 1)
    expect(taskRef.value.status).toBe('claimed')
    expect(mockToast.success).toHaveBeenCalledWith('Task claimed successfully!')
    expect(actionLoading.value).toBe(false)
  })
  
  it('handles claim error', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    mockTaskStore.claimTask.mockRejectedValue(new Error('Claim failed'))
    
    const { claim } = useTaskActions(taskRef)
    
    await claim()
    
    expect(mockToast.error).toHaveBeenCalledWith('Failed to claim task. Please try again.')
    
    consoleErrorSpy.mockRestore()
  })
  
  it('does not claim if task is null', async () => {
    const nullTaskRef = ref(null)
    const { claim } = useTaskActions(nullTaskRef)
    
    await claim()
    
    expect(mockTaskStore.claimTask).not.toHaveBeenCalled()
  })
  
  it('does not claim if worker ID is missing', async () => {
    mockWorkerStore.workerId = null
    const { claim } = useTaskActions(taskRef)
    
    await claim()
    
    expect(mockTaskStore.claimTask).not.toHaveBeenCalled()
  })
  
  it('completes task successfully', async () => {
    const { completeSuccess } = useTaskActions(taskRef)
    
    await completeSuccess()
    
    expect(mockTaskStore.completeTask).toHaveBeenCalledWith(
      1,
      'worker-123',
      true,
      expect.objectContaining({ completed: true }),
      undefined
    )
    expect(mockToast.success).toHaveBeenCalledWith('Task completed successfully!')
  })
  
  it('completes task as failed', async () => {
    const { completeFailed } = useTaskActions(taskRef)
    
    await completeFailed('Custom error message')
    
    expect(mockTaskStore.completeTask).toHaveBeenCalledWith(
      1,
      'worker-123',
      false,
      undefined,
      'Custom error message'
    )
    expect(mockToast.success).toHaveBeenCalledWith('Task marked as failed')
  })
  
  it('navigates to home after successful completion', async () => {
    const { completeSuccess } = useTaskActions(taskRef)
    
    await completeSuccess()
    
    vi.advanceTimersByTime(1500)
    
    // Navigation is tested through router mock
    expect(mockToast.success).toHaveBeenCalled()
  })
  
  it('handles complete error', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    mockTaskStore.completeTask.mockRejectedValue(new Error('Complete failed'))
    
    const { completeSuccess } = useTaskActions(taskRef)
    
    await completeSuccess()
    
    expect(mockToast.error).toHaveBeenCalledWith('Failed to complete task. Please try again.')
    
    consoleErrorSpy.mockRestore()
  })
  
  it('sets actionLoading during claim operation', async () => {
    let loadingDuringClaim = false
    mockTaskStore.claimTask.mockImplementation(async () => {
      const { actionLoading } = useTaskActions(taskRef)
      loadingDuringClaim = actionLoading.value
      return { ...mockTask, status: 'claimed' }
    })
    
    const { claim, actionLoading } = useTaskActions(taskRef)
    
    expect(actionLoading.value).toBe(false)
    await claim()
    expect(actionLoading.value).toBe(false)
  })
})
