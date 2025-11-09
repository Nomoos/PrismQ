<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <h1 class="text-xl font-bold text-gray-900">Worker Dashboard</h1>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-6 space-y-4">
      <!-- Worker Info Card -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Worker Information</h2>
        <div class="space-y-2">
          <div class="flex justify-between">
            <span class="text-gray-600">Worker ID:</span>
            <span class="font-mono text-sm">{{ workerStore.workerId || 'Not initialized' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Status:</span>
            <StatusBadge :status="workerStore.status" :uppercase="false" />
          </div>
        </div>
        
        <div class="mt-4 pt-4 border-t">
          <button 
            v-if="!workerStore.isInitialized"
            @click="initWorker"
            class="btn-primary w-full"
          >
            Initialize Worker
          </button>
          <div v-else class="flex gap-2">
            <button 
              @click="setActive"
              :disabled="workerStore.status === 'active'"
              class="btn-primary flex-1"
              :class="{ 'opacity-50 cursor-not-allowed': workerStore.status === 'active' }"
            >
              Set Active
            </button>
            <button 
              @click="setIdle"
              :disabled="workerStore.status === 'idle'"
              class="btn-secondary flex-1"
              :class="{ 'opacity-50 cursor-not-allowed': workerStore.status === 'idle' }"
            >
              Set Idle
            </button>
          </div>
        </div>
      </div>

      <!-- Task Statistics Card -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Task Statistics</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-yellow-50 rounded-lg p-4 text-center">
            <p class="text-2xl font-bold text-yellow-800">{{ taskStore.pendingTasks.length }}</p>
            <p class="text-xs text-yellow-600 mt-1">Pending</p>
          </div>
          <div class="bg-blue-50 rounded-lg p-4 text-center">
            <p class="text-2xl font-bold text-blue-800">{{ taskStore.claimedTasks.length }}</p>
            <p class="text-xs text-blue-600 mt-1">Claimed</p>
          </div>
          <div class="bg-green-50 rounded-lg p-4 text-center">
            <p class="text-2xl font-bold text-green-800">{{ taskStore.completedTasks.length }}</p>
            <p class="text-xs text-green-600 mt-1">Completed</p>
          </div>
          <div class="bg-red-50 rounded-lg p-4 text-center">
            <p class="text-2xl font-bold text-red-800">{{ taskStore.failedTasks.length }}</p>
            <p class="text-xs text-red-600 mt-1">Failed</p>
          </div>
        </div>
      </div>

      <!-- Task Actions Card -->
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Task Actions</h2>
        <p class="text-gray-600 text-sm mb-4">
          Claim and process the next available task from the queue
        </p>
        <div class="space-y-3">
          <button 
            @click="claimNextTask"
            :disabled="!workerStore.isInitialized || claimingTask || availableTaskTypes.length === 0"
            class="btn-primary w-full"
            :class="{ 'opacity-50 cursor-not-allowed': !workerStore.isInitialized || claimingTask || availableTaskTypes.length === 0 }"
          >
            <span v-if="claimingTask">Claiming...</span>
            <span v-else>Claim Next Task</span>
          </button>
          
          <!-- Error message -->
          <div v-if="claimError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
            {{ claimError }}
          </div>
          
          <!-- Info -->
          <div class="text-xs text-gray-500 space-y-1">
            <p v-if="availableTaskTypes.length > 0">
              {{ availableTaskTypes.length }} task type(s) available
            </p>
            <p v-else class="text-yellow-600">
              No task types registered yet
            </p>
          </div>
        </div>
      </div>

      <!-- My Tasks Card -->
      <div class="card" v-if="myClaimedTasks.length > 0">
        <h2 class="text-lg font-semibold mb-4">My Tasks</h2>
        <div class="space-y-2">
          <div
            v-for="task in myClaimedTasks"
            :key="task.id"
            @click="goToTask(task.id)"
            class="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="font-medium text-gray-900 truncate">{{ task.type }}</p>
                <p class="text-xs text-gray-500 mt-1">ID: {{ task.id }}</p>
              </div>
              <div class="ml-4">
                <StatusBadge :status="task.status" />
              </div>
            </div>
            <!-- Progress bar -->
            <div v-if="task.progress > 0" class="mt-2">
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-primary-500 h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${task.progress}%` }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ task.progress }}% complete</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Integration Guide -->
      <div class="card bg-blue-50 border-blue-200">
        <h3 class="text-sm font-semibold text-blue-900 mb-2">Integration Example</h3>
        <pre class="text-xs text-blue-800 overflow-x-auto"><code>// Use worker store in components
import { useWorkerStore } from '@/stores/worker'
import { useTaskStore } from '@/stores/tasks'
import { taskService } from '@/services/taskService'

const workerStore = useWorkerStore()
const taskStore = useTaskStore()

// Initialize worker
workerStore.initializeWorker()

// Load available task types
const taskTypes = await taskService.getTaskTypes()

// Claim next available task
const task = await taskStore.claimTask(
  workerStore.workerId!, 
  taskTypes.data[0].id
)</code></pre>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useWorkerStore } from '../stores/worker'
import { useTaskStore } from '../stores/tasks'
import { taskService } from '../services/taskService'
import StatusBadge from '../components/base/StatusBadge.vue'
import type { TaskType } from '../types'

const router = useRouter()
const workerStore = useWorkerStore()
const taskStore = useTaskStore()

const availableTaskTypes = ref<TaskType[]>([])
const claimingTask = ref(false)
const claimError = ref<string | null>(null)

// Computed property for tasks claimed by this worker
const myClaimedTasks = computed(() => {
  if (!workerStore.workerId) return []
  return taskStore.tasks.filter(t => 
    t.status === 'claimed' && t.claimed_by === workerStore.workerId
  )
})

function goToTask(id: number) {
  router.push(`/tasks/${id}`)
}

function initWorker() {
  workerStore.initializeWorker()
}

function setActive() {
  workerStore.setStatus('active')
}

function setIdle() {
  workerStore.setStatus('idle')
}

async function loadTaskTypes() {
  try {
    const response = await taskService.getTaskTypes(true)
    if (response.success && response.data) {
      availableTaskTypes.value = response.data
    }
  } catch (error) {
    console.error('Failed to load task types:', error)
  }
}

async function claimNextTask() {
  if (!workerStore.workerId) {
    alert('Please initialize worker first')
    return
  }
  
  if (availableTaskTypes.value.length === 0) {
    alert('No task types available. Please register a task type first.')
    return
  }
  
  claimingTask.value = true
  claimError.value = null
  
  try {
    // Try to claim a task from the first available task type
    const taskType = availableTaskTypes.value[0]
    const task = await taskStore.claimTask(workerStore.workerId, taskType.id)
    
    if (task) {
      // Successfully claimed a task - navigate to task detail
      await router.push(`/tasks/${task.id}`)
    } else {
      // No tasks available for this type
      claimError.value = 'No pending tasks available at the moment'
    }
  } catch (error) {
    console.error('Failed to claim task:', error)
    claimError.value = error instanceof Error ? error.message : 'Failed to claim task'
  } finally {
    claimingTask.value = false
  }
}

onMounted(async () => {
  // Auto-initialize worker on mount
  if (!workerStore.isInitialized) {
    workerStore.initializeWorker()
  }
  
  // Load available task types
  await loadTaskTypes()
  
  // Load tasks to populate statistics
  await taskStore.fetchTasks()
})
</script>
