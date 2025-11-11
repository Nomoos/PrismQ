<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-canvas-default">
    <!-- Header -->
    <header 
      role="banner"
      class="bg-white dark:bg-dark-surface-default shadow-sm sticky top-0 z-10 dark:border-b dark:border-dark-border-default"
    >
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-dark-text-primary">TaskManager</h1>
        <RouterLink
          to="/tasks/new"
          class="btn-primary px-4 py-2 text-sm"
          aria-label="Create new task"
        >
          + New Task
        </RouterLink>
      </div>
    </header>

    <!-- Navigation Breadcrumb -->
    <NavigationBreadcrumb />

    <!-- Main Content -->
    <main 
      id="main-content"
      role="main"
      aria-label="Task list"
      class="max-w-7xl mx-auto px-4 py-6"
      tabindex="-1"
    >
      <!-- Loading State -->
      <LoadingState v-if="loading" message="Loading tasks..." />

      <!-- Error State -->
      <ErrorDisplay 
        v-else-if="error" 
        :message="error"
        @retry="taskStore.clearError"
      />

      <!-- Task List -->
      <div v-else>
        <!-- Filter Tabs -->
        <nav 
          aria-label="Task filter tabs"
          class="flex gap-2 mb-4 overflow-x-auto pb-2"
          role="tablist"
        >
          <button
            v-for="status in ['all', 'pending', 'claimed', 'completed', 'failed']"
            :key="status"
            @click="currentFilter = status"
            role="tab"
            :aria-selected="currentFilter === status"
            :aria-label="`Filter by ${status} tasks, ${getTaskCount(status)} tasks`"
            :tabindex="currentFilter === status ? 0 : -1"
            @keydown.left="navigateFilter(-1, status)"
            @keydown.right="navigateFilter(1, status)"
            @keydown.home="navigateToFirstFilter"
            @keydown.end="navigateToLastFilter"
            :class="[
              'px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors',
              currentFilter === status
                ? 'bg-primary-500 text-white dark:bg-dark-primary-bg dark:text-white'
                : 'bg-white text-gray-700 hover:bg-gray-100 dark:bg-dark-surface-default dark:text-dark-text-primary dark:hover:bg-dark-surface-overlay dark:border dark:border-dark-border-default'
            ]"
          >
            {{ status.charAt(0).toUpperCase() + status.slice(1) }}
            <span class="ml-2 text-sm opacity-75" aria-hidden="true">
              ({{ getTaskCount(status) }})
            </span>
          </button>
        </nav>

        <!-- Tasks -->
        <EmptyState
          v-if="filteredTasks.length === 0"
          icon="📋"
          :title="`No ${currentFilter} tasks`"
          message="There are no tasks matching this filter"
        />

        <div 
          v-else 
          class="space-y-3"
          role="list"
          aria-label="Tasks"
        >
          <TaskCard
            v-for="task in filteredTasks"
            :key="task.id"
            :task="task"
            @click="goToTask"
          />
        </div>
      </div>
    </main>

    <!-- Bottom Navigation -->
    <nav 
      role="navigation"
      aria-label="Main navigation"
      class="fixed bottom-0 left-0 right-0 bg-white dark:bg-dark-surface-default border-t border-gray-200 dark:border-dark-border-default safe-area-inset-bottom"
    >
      <div class="flex justify-around">
        <RouterLink
          to="/"
          aria-label="Tasks"
          aria-current="page"
          class="flex-1 flex flex-col items-center py-3 text-primary-600 dark:text-dark-primary-text"
        >
          <span class="text-xs font-medium">Tasks</span>
        </RouterLink>
        <RouterLink
          to="/workers"
          aria-label="Workers"
          class="flex-1 flex flex-col items-center py-3 text-gray-600 dark:text-dark-text-secondary hover:text-primary-600 dark:hover:text-dark-primary-text"
        >
          <span class="text-xs font-medium">Workers</span>
        </RouterLink>
        <RouterLink
          to="/settings"
          aria-label="Settings"
          class="flex-1 flex flex-col items-center py-3 text-gray-600 dark:text-dark-text-secondary hover:text-primary-600 dark:hover:text-dark-primary-text"
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
import LoadingState from '../components/base/LoadingState.vue'
import ErrorDisplay from '../components/base/ErrorDisplay.vue'
import EmptyState from '../components/base/EmptyState.vue'
import TaskCard from '../components/TaskCard.vue'
import NavigationBreadcrumb from '../components/NavigationBreadcrumb.vue'

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

const filterStatuses = ['all', 'pending', 'claimed', 'completed', 'failed']

function getTaskCount(status: string): number {
  if (status === 'all') return taskStore.tasks.length
  return taskStore.tasks.filter(t => t.status === status).length
}

function goToTask(id: number) {
  router.push(`/tasks/${id}`)
}

// Keyboard navigation for filter tabs
function navigateFilter(direction: number, currentStatus: string) {
  const currentIndex = filterStatuses.indexOf(currentStatus)
  const newIndex = currentIndex + direction
  
  if (newIndex >= 0 && newIndex < filterStatuses.length) {
    currentFilter.value = filterStatuses[newIndex]
    // Focus the new tab
    setTimeout(() => {
      const buttons = document.querySelectorAll('[role="tab"]')
      const button = buttons[newIndex] as HTMLElement
      button?.focus()
    }, 0)
  }
}

function navigateToFirstFilter() {
  currentFilter.value = filterStatuses[0]
  setTimeout(() => {
    const buttons = document.querySelectorAll('[role="tab"]')
    const button = buttons[0] as HTMLElement
    button?.focus()
  }, 0)
}

function navigateToLastFilter() {
  currentFilter.value = filterStatuses[filterStatuses.length - 1]
  setTimeout(() => {
    const buttons = document.querySelectorAll('[role="tab"]')
    const button = buttons[buttons.length - 1] as HTMLElement
    button?.focus()
  }, 0)
}
</script>
