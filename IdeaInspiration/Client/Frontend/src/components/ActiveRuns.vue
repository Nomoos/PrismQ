<template>
  <div class="active-runs">
    <div class="header">
      <h2 class="title">Active Runs ({{ activeRuns.length }})</h2>
      <button 
        v-if="activeRuns.length > 0" 
        @click="refreshRuns" 
        class="btn-refresh"
        :disabled="loading"
      >
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>
    
    <div v-if="activeRuns.length === 0" class="empty-state">
      <p class="text-gray-500">No active runs</p>
    </div>
    
    <div v-else class="runs-list">
      <div 
        v-for="run in activeRuns"
        :key="run.run_id || run.id"
        class="run-card"
        @click="viewRun(run)"
      >
        <div class="run-header">
          <h3 class="run-name">{{ run.module_name }}</h3>
          <StatusBadge :status="run.status" />
        </div>
        
        <div class="run-details">
          <div class="detail-item">
            <span class="label">Run ID:</span>
            <span class="value">{{ run.run_id || run.id }}</span>
          </div>
          
          <div class="detail-item" v-if="run.started_at || run.start_time">
            <span class="label">Started:</span>
            <span class="value">{{ formatTime(run.started_at || run.start_time || '') }}</span>
          </div>
          
          <div class="detail-item" v-if="run.duration_seconds">
            <span class="label">Duration:</span>
            <span class="value">{{ formatDuration(run.duration_seconds) }}</span>
          </div>
          
          <div class="detail-item" v-if="run.progress_percent !== undefined">
            <span class="label">Progress:</span>
            <span class="value">{{ run.progress_percent }}%</span>
          </div>
        </div>
        
        <div class="run-actions">
          <button @click.stop="viewRunDetails(run)" class="btn-view">
            View Details
          </button>
          <button 
            v-if="run.status === 'running' || run.status === 'queued'"
            @click.stop="cancelRun(run)" 
            class="btn-cancel"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { runService } from '@/services/runs'
import StatusBadge from './StatusBadge.vue'
import type { Run } from '@/types/run'

const emit = defineEmits<{
  (e: 'runs-updated', count: number): void
}>()

const router = useRouter()
const activeRuns = ref<Run[]>([])
const pollInterval = ref<ReturnType<typeof setInterval> | null>(null)
const loading = ref(false)

// Watch activeRuns and emit count changes
watch(() => activeRuns.value.length, (count) => {
  emit('runs-updated', count)
}, { immediate: true })

onMounted(() => {
  loadActiveRuns()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

async function loadActiveRuns() {
  try {
    loading.value = true
    // Filter for queued and running runs
    const runs = await runService.listRuns({ 
      status: 'running',
      limit: 50 
    })
    const queuedRuns = await runService.listRuns({ 
      status: 'queued',
      limit: 50 
    })
    activeRuns.value = [...runs, ...queuedRuns].sort((a, b) => {
      const timeA = new Date(a.started_at || a.start_time || a.created_at || 0).getTime()
      const timeB = new Date(b.started_at || b.start_time || b.created_at || 0).getTime()
      return timeB - timeA
    })
  } catch (err: any) {
    console.error('Error loading active runs:', err)
  } finally {
    loading.value = false
  }
}

async function refreshRuns() {
  await loadActiveRuns()
}

function startPolling() {
  // Poll every 5 seconds to reduce server load
  pollInterval.value = setInterval(loadActiveRuns, 5000)
}

function stopPolling() {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

function viewRun(run: Run) {
  viewRunDetails(run)
}

function viewRunDetails(run: Run) {
  router.push(`/runs/${run.run_id || run.id}`)
}

async function cancelRun(run: Run) {
  const runId = run.run_id || run.id
  if (!runId) {
    console.error('No run ID found')
    return
  }
  if (confirm(`Are you sure you want to cancel "${run.module_name}"?`)) {
    try {
      await runService.cancelRun(runId)
      await loadActiveRuns()
    } catch (err: any) {
      alert(`Failed to cancel run: ${err.message}`)
      console.error('Error canceling run:', err)
    }
  }
}

function formatTime(timestamp: string | undefined): string {
  if (!timestamp) return '--'
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}m ${secs}s`
}
</script>

<style scoped>
.active-runs {
  @apply bg-white rounded-lg shadow p-6;
}

.header {
  @apply flex justify-between items-center mb-4;
}

.title {
  @apply text-xl font-semibold text-gray-900;
}

.btn-refresh {
  @apply px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:bg-gray-400;
}

.empty-state {
  @apply text-center py-8;
}

.runs-list {
  @apply space-y-3;
}

.run-card {
  @apply border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer;
}

.run-header {
  @apply flex justify-between items-start mb-3;
}

.run-name {
  @apply text-lg font-medium text-gray-900;
}

.run-details {
  @apply grid grid-cols-2 gap-2 mb-3 text-sm;
}

.detail-item {
  @apply flex gap-2;
}

.label {
  @apply text-gray-500 font-medium;
}

.value {
  @apply text-gray-900;
}

.run-actions {
  @apply flex gap-2 pt-2 border-t border-gray-100;
}

.btn-view {
  @apply px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors;
}

.btn-cancel {
  @apply px-3 py-1 text-sm bg-red-50 hover:bg-red-100 text-red-600 rounded transition-colors;
}
</style>
