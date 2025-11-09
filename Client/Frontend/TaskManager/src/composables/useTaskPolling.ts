import { ref, onMounted, onUnmounted } from 'vue'
import { useTaskStore } from '../stores/tasks'

/**
 * Composable for polling task updates
 * @param intervalMs - Polling interval in milliseconds (default: 5000)
 * @param autoStart - Whether to start polling automatically on mount (default: true)
 */
export function useTaskPolling(intervalMs = 5000, autoStart = true) {
  const taskStore = useTaskStore()
  const isPolling = ref(false)
  let intervalId: number | null = null
  
  function startPolling() {
    if (isPolling.value) return
    
    isPolling.value = true
    intervalId = window.setInterval(() => {
      taskStore.fetchTasks()
    }, intervalMs)
    
    // Fetch immediately on start
    taskStore.fetchTasks()
  }
  
  function stopPolling() {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
    isPolling.value = false
  }
  
  if (autoStart) {
    onMounted(() => {
      startPolling()
    })
  }
  
  onUnmounted(() => {
    stopPolling()
  })
  
  return {
    isPolling,
    startPolling,
    stopPolling
  }
}
