import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { setSentryUser } from '../utils/sentry'

export const useWorkerStore = defineStore('worker', () => {
  // State
  const workerId = ref<string | null>(null)
  const status = ref<'active' | 'idle' | 'offline'>('offline')
  
  // Initialize worker ID from localStorage or generate new one
  function initializeWorker() {
    const stored = localStorage.getItem('worker_id')
    if (stored) {
      workerId.value = stored
    } else {
      // Generate a unique worker ID
      const id = `worker-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
      workerId.value = id
      localStorage.setItem('worker_id', id)
    }
    status.value = 'idle'
    
    // Set Sentry user context
    setSentryUser(workerId.value)
  }
  
  // Update worker ID
  function setWorkerId(id: string) {
    workerId.value = id
    localStorage.setItem('worker_id', id)
    
    // Update Sentry user context
    setSentryUser(id)
  }
  
  // Update worker status
  function setStatus(newStatus: 'active' | 'idle' | 'offline') {
    status.value = newStatus
  }
  
  // Check if worker is initialized
  const isInitialized = computed(() => workerId.value !== null)
  
  return {
    workerId,
    status,
    isInitialized,
    initializeWorker,
    setWorkerId,
    setStatus
  }
})
