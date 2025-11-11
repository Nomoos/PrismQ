/**
 * Composable for managing task actions (claim, complete, fail)
 * 
 * Extracts task action logic from TaskDetail.vue
 */
import { ref, type Ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskStore } from '../stores/tasks'
import { useWorkerStore } from '../stores/worker'
import { useToast } from './useToast'
import type { Task } from '../types'

export function useTaskActions(task: Ref<Task | null>) {
  const router = useRouter()
  const taskStore = useTaskStore()
  const workerStore = useWorkerStore()
  const toast = useToast()
  
  const actionLoading = ref(false)
  const completingSuccess = ref(false)
  
  async function claim() {
    if (!task.value || !workerStore.workerId) return
    
    actionLoading.value = true
    try {
      const claimedTask = await taskStore.claimTask(workerStore.workerId, task.value.type_id)
      if (claimedTask) {
        task.value = claimedTask
        toast.success('Task claimed successfully!')
      }
    } catch (e) {
      console.error('Failed to claim task:', e)
      toast.error('Failed to claim task. Please try again.')
    } finally {
      actionLoading.value = false
    }
  }
  
  async function complete(success: boolean, result?: any, errorMessage?: string) {
    if (!task.value || !workerStore.workerId) return
    
    actionLoading.value = true
    completingSuccess.value = success
    
    try {
      const completedTask = await taskStore.completeTask(
        task.value.id,
        workerStore.workerId,
        success,
        result,
        errorMessage
      )
      
      if (completedTask) {
        task.value = completedTask
        toast.success(success ? 'Task completed successfully!' : 'Task marked as failed')
        // Navigate back to task list after a short delay
        setTimeout(() => {
          router.push('/')
        }, 1500)
      }
    } catch (e) {
      console.error('Failed to complete task:', e)
      toast.error('Failed to complete task. Please try again.')
    } finally {
      actionLoading.value = false
    }
  }
  
  async function completeSuccess() {
    const result = { completed: true, timestamp: new Date().toISOString() }
    await complete(true, result)
  }
  
  async function completeFailed(errorMessage: string = 'Task marked as failed by user') {
    await complete(false, undefined, errorMessage)
  }
  
  return {
    actionLoading,
    completingSuccess,
    claim,
    complete,
    completeSuccess,
    completeFailed
  }
}
