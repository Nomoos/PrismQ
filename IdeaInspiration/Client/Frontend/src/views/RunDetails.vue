<template>
  <div class="run-details">
    <div v-if="loading" class="loading-container">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p class="mt-4 text-gray-600">Loading run details...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        <p class="font-bold">Error loading run</p>
        <p class="text-sm">{{ error }}</p>
      </div>
      <button @click="$router.push('/')" class="mt-4 btn-primary">
        Back to Dashboard
      </button>
    </div>
    
    <div v-else-if="run">
      <header class="run-header">
        <div class="run-info">
          <h1 class="text-3xl font-semibold text-gray-900">{{ run.module_name }}</h1>
          <span class="text-gray-600 text-sm">{{ run.run_id || run.id }}</span>
        </div>
        
        <div class="header-actions">
          <StatusBadge :status="run.status" />
          
          <button 
            v-if="canCancel"
            @click="cancelRun"
            class="btn-danger"
          >
            Cancel Run
          </button>
        </div>
      </header>
      
      <div class="run-stats">
        <StatCard label="Status" :value="run.status" />
        <StatCard label="Duration" :value="formatDuration(run.duration_seconds)" />
        <StatCard label="Progress" :value="`${run.progress_percent || 0}%`" />
        <StatCard label="Items" :value="`${run.items_processed || 0} / ${run.items_total || '?'}`" />
      </div>
      
      <div class="tabs">
        <button 
          :class="['tab-button', { active: activeTab === 'logs' }]"
          @click="activeTab = 'logs'"
        >
          Logs
        </button>
        <button 
          :class="['tab-button', { active: activeTab === 'parameters' }]"
          @click="activeTab = 'parameters'"
        >
          Parameters
        </button>
        <button 
          v-if="run.status === 'completed'"
          :class="['tab-button', { active: activeTab === 'results' }]"
          @click="activeTab = 'results'"
        >
          Results
        </button>
      </div>
      
      <div class="tab-content">
        <LogViewer 
          v-if="activeTab === 'logs'"
          :run-id="runId"
          :auto-scroll="true"
        />
        
        <ParametersView 
          v-else-if="activeTab === 'parameters'"
          :parameters="run.parameters"
        />
        
        <ResultsView 
          v-else-if="activeTab === 'results'"
          :run-id="runId"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { runService } from '@/services/runs'
import LogViewer from '@/components/LogViewer.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import StatCard from '@/components/StatCard.vue'
import ParametersView from '@/components/ParametersView.vue'
import ResultsView from '@/components/ResultsView.vue'
import type { Run } from '@/types/run'

const route = useRoute()
const runId = route.params.id as string

const run = ref<Run | null>(null)
const activeTab = ref<'logs' | 'parameters' | 'results'>('logs')
const pollInterval = ref<ReturnType<typeof setInterval> | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const canCancel = computed(() => 
  run.value?.status === 'queued' || run.value?.status === 'running'
)

onMounted(async () => {
  await loadRun()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

async function loadRun() {
  try {
    loading.value = true
    error.value = null
    run.value = await runService.getRun(runId)
    
    // Calculate duration if not provided
    if (run.value && !run.value.duration_seconds && run.value.start_time) {
      const start = new Date(run.value.start_time).getTime()
      const end = run.value.end_time ? new Date(run.value.end_time).getTime() : Date.now()
      run.value.duration_seconds = Math.floor((end - start) / 1000)
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load run details'
    console.error('Error loading run:', err)
  } finally {
    loading.value = false
  }
}

function startPolling() {
  pollInterval.value = setInterval(async () => {
    if (run.value?.status === 'running' || run.value?.status === 'queued') {
      await loadRun()
    } else {
      stopPolling()
    }
  }, 2000) // Poll every 2 seconds
}

function stopPolling() {
  if (pollInterval.value !== null) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

async function cancelRun() {
  if (!run.value) return
  
  if (confirm(`Are you sure you want to cancel the run "${run.value.module_name}"?`)) {
    try {
      await runService.cancelRun(runId)
      await loadRun()
    } catch (err: any) {
      alert(`Failed to cancel run: ${err.message}`)
      console.error('Error canceling run:', err)
    }
  }
}

function formatDuration(seconds: number | undefined): string {
  if (seconds === undefined || seconds === null) return '--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}m ${secs}s`
}
</script>

<style scoped>
.run-details {
  @apply max-w-7xl mx-auto px-4 py-6;
}

.loading-container,
.error-container {
  @apply text-center py-12;
}

.run-header {
  @apply flex justify-between items-start mb-6 pb-4 border-b border-gray-200;
}

.run-info h1 {
  @apply mb-1;
}

.header-actions {
  @apply flex items-center gap-3;
}

.btn-danger {
  @apply px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded transition-colors;
}

.btn-primary {
  @apply px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition-colors;
}

.run-stats {
  @apply grid grid-cols-1 md:grid-cols-4 gap-4 mb-6;
}

.tabs {
  @apply flex gap-2 mb-4 border-b border-gray-200;
}

.tab-button {
  @apply px-4 py-2 font-medium text-gray-600 hover:text-gray-900 border-b-2 border-transparent transition-colors;
}

.tab-button.active {
  @apply text-blue-600 border-blue-600;
}

.tab-content {
  @apply mt-4;
}
</style>
