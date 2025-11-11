<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-canvas-default pb-20">
    <header 
      role="banner"
      class="bg-white dark:bg-dark-surface-default shadow-sm sticky top-0 z-10 dark:border-b dark:border-dark-border-default"
    >
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center">
        <button 
          @click="$router.back()" 
          class="mr-4 text-gray-600 dark:text-dark-text-secondary hover:text-gray-900 dark:hover:text-dark-text-primary"
          aria-label="Go back to task list"
        >
          ← Back
        </button>
        <h1 class="text-xl font-bold text-gray-900 dark:text-dark-text-primary">Task Detail</h1>
      </div>
    </header>

    <main 
      id="main-content"
      role="main"
      aria-label="Task details"
      class="max-w-7xl mx-auto px-4 py-6 space-y-4"
      tabindex="-1"
    >
      <!-- Loading State -->
      <div v-if="loading" class="card">
        <LoadingState message="Loading task..." />
      </div>

      <!-- Error State -->
      <ErrorDisplay 
        v-else-if="error" 
        :message="error"
        @retry="loadTask"
      />

      <!-- Task Details -->
      <div v-else-if="task" class="space-y-4">
        <!-- Status Card -->
        <section class="card" aria-labelledby="task-status-heading">
          <div class="flex items-center justify-between mb-4">
            <h2 id="task-status-heading" class="text-2xl font-bold text-gray-900 dark:text-dark-text-primary">{{ task.type }}</h2>
            <StatusBadge :status="task.status" />
          </div>
          
          <!-- Progress Bar for claimed tasks -->
          <div v-if="task.status === 'claimed' && task.progress > 0" class="mb-4">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-dark-text-secondary">Progress</span>
              <span class="text-sm font-medium text-gray-900 dark:text-dark-text-primary">{{ task.progress }}%</span>
            </div>
            <div 
              class="w-full bg-gray-200 dark:bg-dark-neutral-bg rounded-full h-3"
              role="progressbar"
              :aria-valuenow="task.progress"
              aria-valuemin="0"
              aria-valuemax="100"
              :aria-label="`Task progress: ${task.progress}%`"
            >
              <div
                class="bg-primary-500 dark:bg-dark-primary-bg h-3 rounded-full transition-all duration-300"
                :style="{ width: `${task.progress}%` }"
              ></div>
            </div>
          </div>

          <!-- Key Information -->
          <div class="grid grid-cols-2 gap-4 text-sm" role="list" aria-label="Task information">
            <div role="listitem">
              <span class="text-gray-500 dark:text-dark-text-secondary">Task ID:</span>
              <p class="font-medium text-gray-900 dark:text-dark-text-primary">#{{ task.id }}</p>
            </div>
            <div role="listitem">
              <span class="text-gray-500 dark:text-dark-text-secondary">Priority:</span>
              <p class="font-medium text-gray-900 dark:text-dark-text-primary">{{ task.priority }}</p>
            </div>
            <div role="listitem">
              <span class="text-gray-500 dark:text-dark-text-secondary">Attempts:</span>
              <p class="font-medium text-gray-900 dark:text-dark-text-primary">{{ task.attempts }}/{{ task.max_attempts }}</p>
            </div>
            <div role="listitem">
              <span class="text-gray-500 dark:text-dark-text-secondary">Created:</span>
              <p class="font-medium text-gray-900 dark:text-dark-text-primary">{{ formatDate(task.created_at) }}</p>
            </div>
          </div>
        </section>

        <!-- Worker Information -->
        <section v-if="task.claimed_by" class="card" aria-labelledby="worker-info-heading">
          <h3 id="worker-info-heading" class="text-lg font-semibold text-gray-900 dark:text-dark-text-primary mb-3">Worker Information</h3>
          <div class="space-y-2 text-sm" role="list" aria-label="Worker details">
            <div role="listitem">
              <span class="text-gray-500 dark:text-dark-text-secondary">Claimed by:</span>
              <p class="font-medium text-gray-900 dark:text-dark-text-primary">{{ task.claimed_by }}</p>
            </div>
            <div v-if="task.claimed_at" role="listitem">
              <span class="text-gray-500 dark:text-dark-text-secondary">Claimed at:</span>
              <p class="font-medium text-gray-900 dark:text-dark-text-primary">{{ formatDate(task.claimed_at) }}</p>
            </div>
            <div v-if="task.completed_at" role="listitem">
              <span class="text-gray-500 dark:text-dark-text-secondary">Completed at:</span>
              <p class="font-medium text-gray-900 dark:text-dark-text-primary">{{ formatDate(task.completed_at) }}</p>
            </div>
          </div>
        </section>

        <!-- Parameters -->
        <section class="card" aria-labelledby="parameters-heading">
          <h3 id="parameters-heading" class="text-lg font-semibold text-gray-900 dark:text-dark-text-primary mb-3">Parameters</h3>
          <pre 
            class="bg-gray-100 dark:bg-dark-canvas-inset rounded p-3 text-xs overflow-x-auto text-gray-900 dark:text-dark-text-primary"
            role="region"
            aria-label="Task parameters"
            tabindex="0"
          >{{ JSON.stringify(task.params, null, 2) }}</pre>
        </section>

        <!-- Result (if completed) -->
        <section v-if="task.result" class="card" aria-labelledby="result-heading">
          <h3 id="result-heading" class="text-lg font-semibold text-gray-900 dark:text-dark-text-primary mb-3">Result</h3>
          <pre 
            class="bg-gray-100 dark:bg-dark-canvas-inset rounded p-3 text-xs overflow-x-auto text-gray-900 dark:text-dark-text-primary"
            role="region"
            aria-label="Task result"
            tabindex="0"
          >{{ JSON.stringify(task.result, null, 2) }}</pre>
        </section>

        <!-- Error Message (if failed) -->
        <section 
          v-if="task.error_message" 
          class="card bg-red-50 dark:bg-dark-error-subtle border border-red-200 dark:border-dark-error-border"
          aria-labelledby="error-heading"
          role="alert"
        >
          <h3 id="error-heading" class="text-lg font-semibold text-red-900 dark:text-dark-error-text mb-3">Error Message</h3>
          <p class="text-red-800 dark:text-dark-error-text text-sm">{{ task.error_message }}</p>
        </section>

        <!-- Action Buttons -->
        <section class="card" aria-labelledby="actions-heading">
          <h3 id="actions-heading" class="sr-only">Task Actions</h3>
          <div class="space-y-3">
            <!-- Claim Button (for pending tasks) -->
            <button
              v-if="task.status === 'pending'"
              @click="handleClaim"
              :disabled="actionLoading"
              :aria-busy="actionLoading"
              aria-label="Claim this task"
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
                :aria-busy="actionLoading && completingSuccess"
                aria-label="Mark task as complete"
                class="w-full bg-green-600 dark:bg-dark-success-bg text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 dark:hover:bg-dark-success-muted disabled:bg-gray-300 dark:disabled:bg-dark-neutral-bg flex items-center justify-center min-h-[44px]"
              >
                <LoadingSpinner v-if="actionLoading && completingSuccess" size="sm" color="white" class="mr-2" />
                {{ actionLoading && completingSuccess ? 'Completing...' : 'Mark as Complete' }}
              </button>
              
              <button
                @click="showFailConfirmation = true"
                :disabled="actionLoading"
                aria-label="Mark task as failed"
                class="w-full bg-red-600 dark:bg-dark-error-bg text-white py-3 px-4 rounded-lg font-medium hover:bg-red-700 dark:hover:bg-dark-error-muted disabled:bg-gray-300 dark:disabled:bg-dark-neutral-bg flex items-center justify-center min-h-[44px]"
              >
                Mark as Failed
              </button>
            </div>

            <!-- Info message for claimed tasks by other workers -->
            <div 
              v-if="task.status === 'claimed' && task.claimed_by !== workerStore.workerId" 
              class="bg-blue-50 dark:bg-dark-info-subtle border border-blue-200 dark:border-dark-info-border rounded-lg p-3"
              role="status"
              aria-live="polite"
            >
              <p class="text-blue-800 dark:text-dark-info-text text-sm">This task is claimed by another worker: {{ task.claimed_by }}</p>
            </div>
          </div>
        </section>
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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useWorkerStore } from '../stores/worker'
import { useTaskDetail } from '../composables/useTaskDetail'
import { useTaskActions } from '../composables/useTaskActions'
import ConfirmDialog from '../components/base/ConfirmDialog.vue'
import LoadingState from '../components/base/LoadingState.vue'
import ErrorDisplay from '../components/base/ErrorDisplay.vue'
import StatusBadge from '../components/base/StatusBadge.vue'
import { formatDate as formatDateUtil } from '../utils/dateFormatting'

const route = useRoute()
const workerStore = useWorkerStore()

const showFailConfirmation = ref(false)

// Initialize worker if not already initialized
if (!workerStore.isInitialized) {
  workerStore.initializeWorker()
}

// Use composables for task detail and actions
const taskId = Number(route.params.id)
const { task, loading, error, loadTask } = useTaskDetail(taskId)
const { actionLoading, completingSuccess, claim, completeSuccess, completeFailed } = useTaskActions(task)

async function handleClaim() {
  await claim()
}

async function handleComplete(success: boolean) {
  if (success) {
    await completeSuccess()
  } else {
    await completeFailed()
  }
}

function formatDate(dateString: string): string {
  return formatDateUtil(dateString)
}

onMounted(() => {
  loadTask()
})
</script>
