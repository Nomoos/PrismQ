<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center">
        <button @click="$router.back()" class="mr-4 text-gray-600 hover:text-gray-900">
          ← Back
        </button>
        <h1 class="text-xl font-bold text-gray-900">Task Detail</h1>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-6 space-y-4">
      <!-- Loading State -->
      <div v-if="loading" class="card text-center py-8">
        <LoadingSpinner size="lg" />
        <p class="mt-2 text-gray-600">Loading task...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-red-800">{{ error }}</p>
        <button @click="loadTask" class="btn-primary mt-2">
          Retry
        </button>
      </div>

      <!-- Task Details -->
      <div v-else-if="task" class="space-y-4">
        <!-- Status Card -->
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-2xl font-bold text-gray-900">{{ task.type }}</h2>
            <StatusBadge :status="task.status" />
          </div>
          
          <!-- Progress Bar for claimed tasks -->
          <div v-if="task.status === 'claimed' && task.progress > 0" class="mb-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-700">Progress</span>
              <span class="text-sm font-medium text-gray-900">{{ task.progress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
              <div
                class="bg-primary-500 h-3 rounded-full transition-all duration-300"
                :style="{ width: `${task.progress}%` }"
              ></div>
            </div>
          </div>

          <!-- Key Information -->
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-500">Task ID:</span>
              <p class="font-medium text-gray-900">#{{ task.id }}</p>
            </div>
            <div>
              <span class="text-gray-500">Priority:</span>
              <p class="font-medium text-gray-900">{{ task.priority }}</p>
            </div>
            <div>
              <span class="text-gray-500">Attempts:</span>
              <p class="font-medium text-gray-900">{{ task.attempts }}/{{ task.max_attempts }}</p>
            </div>
            <div>
              <span class="text-gray-500">Created:</span>
              <p class="font-medium text-gray-900">{{ formatDate(task.created_at) }}</p>
            </div>
          </div>
        </div>

        <!-- Worker Information -->
        <div v-if="task.claimed_by" class="card">
          <h3 class="text-lg font-semibold text-gray-900 mb-3">Worker Information</h3>
          <div class="space-y-2 text-sm">
            <div>
              <span class="text-gray-500">Claimed by:</span>
              <p class="font-medium text-gray-900">{{ task.claimed_by }}</p>
            </div>
            <div v-if="task.claimed_at">
              <span class="text-gray-500">Claimed at:</span>
              <p class="font-medium text-gray-900">{{ formatDate(task.claimed_at) }}</p>
            </div>
            <div v-if="task.completed_at">
              <span class="text-gray-500">Completed at:</span>
              <p class="font-medium text-gray-900">{{ formatDate(task.completed_at) }}</p>
            </div>
          </div>
        </div>

        <!-- Parameters -->
        <div class="card">
          <h3 class="text-lg font-semibold text-gray-900 mb-3">Parameters</h3>
          <pre class="bg-gray-100 rounded p-3 text-xs overflow-x-auto">{{ JSON.stringify(task.params, null, 2) }}</pre>
        </div>

        <!-- Result (if completed) -->
        <div v-if="task.result" class="card">
          <h3 class="text-lg font-semibold text-gray-900 mb-3">Result</h3>
          <pre class="bg-gray-100 rounded p-3 text-xs overflow-x-auto">{{ JSON.stringify(task.result, null, 2) }}</pre>
        </div>

        <!-- Error Message (if failed) -->
        <div v-if="task.error_message" class="card bg-red-50 border border-red-200">
          <h3 class="text-lg font-semibold text-red-900 mb-3">Error Message</h3>
          <p class="text-red-800 text-sm">{{ task.error_message }}</p>
        </div>

        <!-- Action Buttons -->
        <div class="card">
          <div class="space-y-3">
            <!-- Claim Button (for pending tasks) -->
            <button
              v-if="task.status === 'pending'"
              @click="handleClaim"
              :disabled="actionLoading"
              class="w-full btn-primary flex items-center justify-center min-h-[44px]"
            >
              <LoadingSpinner v-if="actionLoading" size="sm" color="white" class="mr-2" />
              {{ actionLoading ? 'Claiming...' : 'Claim Task' }}
            </button>

            <!-- Complete Button (for claimed tasks) -->
            <div v-if="task.status === 'claimed' && task.claimed_by === workerStore.workerId" class="space-y-2">
              <button
                @click="handleComplete(true)"
                :disabled="actionLoading"
                class="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-300 flex items-center justify-center min-h-[44px]"
              >
                <LoadingSpinner v-if="actionLoading && completingSuccess" size="sm" color="white" class="mr-2" />
                {{ actionLoading && completingSuccess ? 'Completing...' : 'Mark as Complete' }}
              </button>
              
              <button
                @click="showFailConfirmation = true"
                :disabled="actionLoading"
                class="w-full bg-red-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-red-700 disabled:bg-gray-300 flex items-center justify-center min-h-[44px]"
              >
                Mark as Failed
              </button>
            </div>

            <!-- Info message for claimed tasks by other workers -->
            <div v-if="task.status === 'claimed' && task.claimed_by !== workerStore.workerId" class="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p class="text-blue-800 text-sm">This task is claimed by another worker: {{ task.claimed_by }}</p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Confirmation Dialog -->
    <ConfirmDialog
      v-model="showFailConfirmation"
      title="Mark Task as Failed"
      message="Are you sure you want to mark this task as failed? This action cannot be undone."
      confirm-text="Mark as Failed"
      cancel-text="Cancel"
      danger-mode
      @confirm="handleComplete(false)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore } from '../stores/tasks'
import { useWorkerStore } from '../stores/worker'
import { useToast } from '../composables/useToast'
import ConfirmDialog from '../components/base/ConfirmDialog.vue'
import LoadingSpinner from '../components/base/LoadingSpinner.vue'
import StatusBadge from '../components/base/StatusBadge.vue'
import type { Task } from '../types'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const workerStore = useWorkerStore()
const toast = useToast()

const task = ref<Task | null>(null)
const actionLoading = ref(false)
const completingSuccess = ref(false)
const showFailConfirmation = ref(false)

// Initialize worker if not already initialized
if (!workerStore.isInitialized) {
  workerStore.initializeWorker()
}

const loading = computed(() => taskStore.loading)
const error = computed(() => taskStore.error)

async function loadTask() {
  const taskId = Number(route.params.id)
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

async function handleClaim() {
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

async function handleComplete(success: boolean) {
  if (!task.value || !workerStore.workerId) return
  
  actionLoading.value = true
  completingSuccess.value = success
  
  try {
    const result = success ? { completed: true, timestamp: new Date().toISOString() } : undefined
    const errorMessage = success ? undefined : 'Task marked as failed by user'
    
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

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / 60000)
  
  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
  
  // Format as full date for older items
  return date.toLocaleString()
}

onMounted(() => {
  loadTask()
})
</script>
