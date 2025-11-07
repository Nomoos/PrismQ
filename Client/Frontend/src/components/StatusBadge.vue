<template>
  <span :class="['status-badge', `status-${status}`]">
    {{ statusText }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RunStatus } from '@/types/run'

const props = defineProps<{
  status: RunStatus
}>()

const statusText = computed(() => {
  const texts: Record<RunStatus, string> = {
    queued: 'Queued',
    running: 'Running...',
    completed: 'Completed ✓',
    failed: 'Failed ✗',
    cancelled: 'Cancelled'
  }
  return texts[props.status] || props.status
})
</script>

<style scoped>
.status-badge {
  @apply px-4 py-2 rounded-full font-semibold text-sm;
}

.status-queued {
  @apply bg-indigo-100 text-indigo-800;
}

.status-running {
  @apply bg-blue-100 text-blue-800;
  animation: pulse 2s infinite;
}

.status-completed {
  @apply bg-green-100 text-green-800;
}

.status-failed {
  @apply bg-red-100 text-red-800;
}

.status-cancelled {
  @apply bg-gray-100 text-gray-600;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
