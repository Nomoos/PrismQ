<template>
  <article
    role="listitem"
    tabindex="0"
    @click="$emit('click', task.id)"
    @keydown.enter="$emit('click', task.id)"
    @keydown.space.prevent="$emit('click', task.id)"
    :aria-label="`Task ${task.type}, ID ${task.id}, status ${task.status}, priority ${task.priority}`"
    class="card cursor-pointer hover:shadow-md dark:hover:border-dark-border-strong transition-shadow"
  >
    <div class="flex items-start justify-between">
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <span
            :class="[
              'inline-block w-3 h-3 rounded-full',
              getStatusColor(task.status)
            ]"
            :aria-label="`Status: ${task.status}`"
            role="img"
          ></span>
          <h2 class="font-semibold text-gray-900 dark:text-dark-text-primary truncate">
            {{ task.type }}
          </h2>
        </div>
        <p class="text-sm text-gray-500 dark:text-dark-text-secondary mt-1">
          ID: {{ task.id }}
        </p>
        <p class="text-sm text-gray-600 dark:text-dark-text-secondary mt-1">
          Priority: {{ task.priority }} | Attempts: {{ task.attempts }}/{{ task.max_attempts }}
        </p>
        
        <!-- Progress Bar -->
        <div v-if="showProgress && task.status === 'claimed' && task.progress > 0" class="mt-2">
          <div 
            class="w-full bg-gray-200 dark:bg-dark-neutral-bg rounded-full h-2"
            role="progressbar"
            :aria-valuenow="task.progress"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-label="`Task progress: ${task.progress}%`"
          >
            <div
              class="bg-primary-500 dark:bg-dark-primary-bg h-2 rounded-full transition-all duration-300"
              :style="{ width: `${task.progress}%` }"
            ></div>
          </div>
          <p class="text-xs text-gray-500 dark:text-dark-text-tertiary mt-1">
            {{ task.progress }}% complete
          </p>
        </div>
      </div>
      
      <div class="ml-4 text-right flex-shrink-0">
        <StatusBadge :status="task.status" />
        <p v-if="showDate" class="text-xs text-gray-500 dark:text-dark-text-tertiary mt-2">
          {{ formatRelativeTime(task.created_at) }}
        </p>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import StatusBadge from './base/StatusBadge.vue'
import { getStatusColor } from '../utils/statusHelpers'
import { formatRelativeTime } from '../utils/dateFormatting'
import type { Task } from '../types'

withDefaults(defineProps<{
  task: Task
  showProgress?: boolean
  showDate?: boolean
}>(), {
  showProgress: true,
  showDate: true
})

defineEmits<{
  click: [id: number]
}>()
</script>
