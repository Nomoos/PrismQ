/**
 * Composable for managing task detail view logic
 * 
 * Extracts task fetching and state management from TaskDetail.vue
 */
import { ref, computed } from 'vue'
import { useTaskStore } from '../stores/tasks'
import type { Task } from '../types'

export function useTaskDetail(taskId: number) {
  const taskStore = useTaskStore()
  const task = ref<Task | null>(null)
  
  const loading = computed(() => taskStore.loading)
  const error = computed(() => taskStore.error)
  
  async function loadTask() {
    if (isNaN(taskId)) {
      taskStore.error = 'Invalid task ID'
      return
    }

    try {
      const fetchedTask = await taskStore.fetchTask(taskId)
      if (fetchedTask) {
        task.value = fetchedTask
      }
    } catch (e) {
      console.error('Failed to load task:', e)
    }
  }
  
  function refreshTask() {
    return loadTask()
  }
  
  return {
    task,
    loading,
    error,
    loadTask,
    refreshTask
  }
}
