import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Task, CreateTaskRequest } from '../types'
import { taskService } from '../services/taskService'

export const useTaskStore = defineStore('tasks', () => {
  // State
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const pendingTasks = computed(() => 
    tasks.value.filter(t => t.status === 'pending')
  )
  
  const claimedTasks = computed(() => 
    tasks.value.filter(t => t.status === 'claimed')
  )
  
  const completedTasks = computed(() => 
    tasks.value.filter(t => t.status === 'completed')
  )
  
  const failedTasks = computed(() => 
    tasks.value.filter(t => t.status === 'failed')
  )
  
  // Actions
  async function fetchTasks(params?: { status?: string; type?: string }) {
    loading.value = true
    error.value = null
    try {
      const response = await taskService.getTasks(params)
      if (response.success) {
        tasks.value = response.data
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch tasks. Please check your connection and try again.'
    } finally {
      loading.value = false
    }
  }
  
  async function createTask(data: CreateTaskRequest) {
    loading.value = true
    error.value = null
    try {
      const response = await taskService.createTask(data)
      if (response.success && response.data) {
        tasks.value.unshift(response.data)
      }
      return response
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to create task. Please verify your input and try again.'
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function fetchTask(id: number): Promise<Task | undefined> {
    loading.value = true
    error.value = null
    try {
      const response = await taskService.getTask(id)
      if (response.success && response.data) {
        // Update or add task to local state
        const index = tasks.value.findIndex(t => t.id === id)
        if (index !== -1) {
          tasks.value[index] = response.data
        } else {
          tasks.value.push(response.data)
        }
        return response.data
      }
      return undefined
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch task details. Please try again.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function claimTask(workerId: string, taskTypeId: number): Promise<Task | undefined> {
    loading.value = true
    error.value = null
    try {
      const response = await taskService.claimTask({
        worker_id: workerId,
        task_type_id: taskTypeId
      })
      if (response.success && response.data) {
        // Update task in local state
        updateTask(response.data)
        return response.data
      }
      return undefined
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to claim task. Please try again.'
      throw e
    } finally {
      loading.value = false
    }
  }
  
  async function completeTask(
    id: number, 
    workerId: string, 
    success: boolean, 
    result?: Record<string, any>, 
    errorMessage?: string
  ): Promise<Task | undefined> {
    // Find the task for optimistic update
    const task = tasks.value.find(t => t.id === id)
    if (!task) {
      error.value = 'Task not found in local state'
      throw new Error('Task not found')
    }

    // Store original state for rollback
    const originalStatus = task.status
    const originalResult = task.result
    const originalError = task.error_message
    
    // Optimistic update - immediately update UI
    task.status = success ? 'completed' : 'failed'
    if (success && result) {
      task.result = result
    }
    if (!success && errorMessage) {
      task.error_message = errorMessage
    }
    
    loading.value = true
    error.value = null
    try {
      const response = await taskService.completeTask(id, {
        worker_id: workerId,
        success,
        result,
        error: errorMessage
      })
      if (response.success) {
        // Refresh the specific task to get updated state from server
        const taskResponse = await taskService.getTask(id)
        if (taskResponse.success && taskResponse.data) {
          const index = tasks.value.findIndex(t => t.id === id)
          if (index !== -1) {
            tasks.value[index] = taskResponse.data
          }
          return taskResponse.data
        }
      }
      return task
    } catch (e) {
      // Rollback optimistic update on error
      task.status = originalStatus
      task.result = originalResult
      task.error_message = originalError
      error.value = e instanceof Error ? e.message : 'Failed to complete task. Changes have been reverted.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function failTask(taskId: number, workerId: string, errorMessage: string) {
    // Find task for optimistic update
    const task = tasks.value.find(t => t.id === taskId)
    if (!task) {
      error.value = 'Task not found in local state'
      throw new Error('Task not found')
    }

    // Store original state for rollback
    const originalStatus = task.status
    const originalError = task.error_message

    // Optimistic update
    task.status = 'failed'
    task.error_message = errorMessage
    
    loading.value = true
    error.value = null
    try {
      await taskService.completeTask(taskId, {
        worker_id: workerId,
        success: false,
        error: errorMessage
      })
      // Success - optimistic update is already applied
    } catch (e) {
      // Rollback optimistic update on error
      task.status = originalStatus
      task.error_message = originalError
      error.value = e instanceof Error ? e.message : 'Failed to mark task as failed. Changes have been reverted.'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateProgress(taskId: number, workerId: string, progress: number, message?: string) {
    // Find task for optimistic update
    const task = tasks.value.find(t => t.id === taskId)
    if (!task) {
      error.value = 'Task not found in local state'
      throw new Error('Task not found')
    }

    // Store original progress for rollback
    const originalProgress = task.progress

    // Optimistic update - immediately show progress
    task.progress = progress
    
    loading.value = true
    error.value = null
    try {
      await taskService.updateProgress(taskId, {
        worker_id: workerId,
        progress,
        message
      })
      // Success - optimistic update is already applied
    } catch (e) {
      // Rollback optimistic update on error
      task.progress = originalProgress
      error.value = e instanceof Error ? e.message : 'Failed to update progress. Progress has been reverted.'
      throw e
    } finally {
      loading.value = false
    }
  }

  function updateTask(updatedTask: Task) {
    const index = tasks.value.findIndex(t => t.id === updatedTask.id)
    if (index !== -1) {
      tasks.value[index] = updatedTask
    } else {
      // Task not in list, add it
      tasks.value.push(updatedTask)
    }
  }
  
  function clearError() {
    error.value = null
  }
  
  return {
    tasks,
    loading,
    error,
    pendingTasks,
    claimedTasks,
    completedTasks,
    failedTasks,
    fetchTasks,
    fetchTask,
    createTask,
    claimTask,
    completeTask,
    failTask,
    updateProgress,
    updateTask,
    clearError
  }
})
