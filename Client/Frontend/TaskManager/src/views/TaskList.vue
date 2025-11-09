<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <h1 class="text-2xl font-bold text-gray-900">TaskManager</h1>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-6">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <LoadingSpinner size="lg" />
        <p class="mt-2 text-gray-600">Loading tasks...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-red-800">{{ error }}</p>
        <button @click="taskStore.clearError" class="btn-primary mt-2">
          Retry
        </button>
      </div>

      <!-- Task List -->
      <div v-else>
        <!-- Filter Tabs -->
        <div class="flex gap-2 mb-4 overflow-x-auto pb-2">
          <button
            v-for="status in ['all', 'pending', 'claimed', 'completed', 'failed']"
            :key="status"
            @click="currentFilter = status"
            :class="[
              'px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors',
              currentFilter === status
                ? 'bg-primary-500 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100'
            ]"
          >
            {{ status.charAt(0).toUpperCase() + status.slice(1) }}
            <span class="ml-2 text-sm opacity-75">
              ({{ getTaskCount(status) }})
            </span>
          </button>
        </div>

        <!-- Tasks -->
        <EmptyState
          v-if="filteredTasks.length === 0"
          icon="📋"
          :title="`No ${currentFilter} tasks`"
          message="There are no tasks matching this filter"
        />

        <div v-else class="space-y-3">
          <div
            v-for="task in filteredTasks"
            :key="task.id"
            @click="goToTask(task.id)"
            class="card cursor-pointer hover:shadow-md transition-shadow"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'inline-block w-3 h-3 rounded-full',
                      getStatusColor(task.status)
                    ]"
                  ></span>
                  <h3 class="font-semibold text-gray-900 truncate">
                    {{ task.type }}
                  </h3>
                </div>
                <p class="text-sm text-gray-500 mt-1">ID: {{ task.id }}</p>
                <p class="text-sm text-gray-600 mt-1">
                  Priority: {{ task.priority }} | Attempts: {{ task.attempts }}/{{ task.max_attempts }}
                </p>
                
                <!-- Progress Bar -->
                <div v-if="task.status === 'claimed' && task.progress > 0" class="mt-2">
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-primary-500 h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${task.progress}%` }"
                    ></div>
                  </div>
                  <p class="text-xs text-gray-500 mt-1">{{ task.progress }}% complete</p>
                </div>
              </div>
              
              <div class="ml-4 text-right flex-shrink-0">
                <StatusBadge :status="task.status" />
                <p class="text-xs text-gray-500 mt-2">
                  {{ formatDate(task.created_at) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Bottom Navigation -->
    <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-inset-bottom">
      <div class="flex justify-around">
        <RouterLink
          to="/"
          class="flex-1 flex flex-col items-center py-3 text-primary-600"
        >
          <span class="text-xs font-medium">Tasks</span>
        </RouterLink>
        <RouterLink
          to="/workers"
          class="flex-1 flex flex-col items-center py-3 text-gray-600 hover:text-primary-600"
        >
          <span class="text-xs font-medium">Workers</span>
        </RouterLink>
        <RouterLink
          to="/settings"
          class="flex-1 flex flex-col items-center py-3 text-gray-600 hover:text-primary-600"
        >
          <span class="text-xs font-medium">Settings</span>
        </RouterLink>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskStore } from '../stores/tasks'
import { useTaskPolling } from '../composables/useTaskPolling'
import LoadingSpinner from '../components/base/LoadingSpinner.vue'
import EmptyState from '../components/base/EmptyState.vue'
import StatusBadge from '../components/base/StatusBadge.vue'

const router = useRouter()
const taskStore = useTaskStore()

// Enable real-time polling (fetches tasks every 5 seconds)
useTaskPolling(5000, true)

const currentFilter = ref('all')
const loading = computed(() => taskStore.loading)
const error = computed(() => taskStore.error)

const filteredTasks = computed(() => {
  if (currentFilter.value === 'all') {
    return taskStore.tasks
  }
  return taskStore.tasks.filter(t => t.status === currentFilter.value)
})

function getTaskCount(status: string): number {
  if (status === 'all') return taskStore.tasks.length
  return taskStore.tasks.filter(t => t.status === status).length
}

function getStatusColor(status: string): string {
  const colors = {
    pending: 'bg-yellow-400',
    claimed: 'bg-blue-400',
    completed: 'bg-green-400',
    failed: 'bg-red-400'
  }
  return colors[status as keyof typeof colors] || 'bg-gray-400'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / 60000)
  
  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
  return date.toLocaleDateString()
}

function goToTask(id: number) {
  router.push(`/tasks/${id}`)
}
</script>
