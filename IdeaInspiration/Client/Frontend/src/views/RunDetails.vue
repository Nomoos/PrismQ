<template>
  <div class="run-details">
    <div v-if="loading" class="loading-container">
      <div class="loading-card">
        <div class="loading-header">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <h3 class="loading-title">Loading Run Details</h3>
        </div>
        <div class="action-log">
          <div class="action-log-header">Action Log:</div>
          <div class="action-log-entries">
            <div v-for="(entry, index) in actionLog" :key="index" class="log-entry">
              {{ entry }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-card">
        <div class="error-icon">⚠️</div>
        <div class="error-content">
          <h3 class="error-title">Failed to Load Run Details</h3>
          <p class="error-message">{{ error }}</p>
          <div class="error-actions">
            <button @click="loadRun" class="btn-retry">
              🔄 Retry
            </button>
            <button @click="$router.push('/runs')" class="btn-back">
              ← Back to History
            </button>
          </div>
        </div>
      </div>
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
const actionLog = ref<string[]>([])

function addLogEntry(message: string) {
  const timestamp = new Date().toLocaleTimeString()
  actionLog.value.push(`[${timestamp}] ${message}`)
}

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
    actionLog.value = [] // Clear previous logs
    
    addLogEntry(`Starting to load run: ${runId}`)
    addLogEntry('Sending API request to backend...')
    
    const startTime = Date.now()
    run.value = await runService.getRun(runId)
    const duration = Date.now() - startTime
    
    addLogEntry(`✓ Received run data in ${duration}ms`)
    addLogEntry(`Run status: ${run.value.status}`)
    
    // Calculate duration if not provided
    if (run.value && !run.value.duration_seconds && run.value.start_time) {
      addLogEntry('Calculating run duration...')
      const start = new Date(run.value.start_time).getTime()
      const end = run.value.end_time ? new Date(run.value.end_time).getTime() : Date.now()
      run.value.duration_seconds = Math.floor((end - start) / 1000)
      addLogEntry(`✓ Duration calculated: ${run.value.duration_seconds}s`)
    }
    
    addLogEntry('✓ Run details loaded successfully')
  } catch (err: any) {
    addLogEntry('✗ Error occurred while loading run')
    
    // Provide more descriptive error messages
    if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
      addLogEntry('✗ Request timeout (30 seconds)')
      addLogEntry('Backend may be slow or unresponsive')
      error.value = 'Request timed out after 30 seconds. The backend may be slow or unresponsive.'
    } else if (err.response) {
      // Server responded with error
      const status = err.response.status
      addLogEntry(`Server responded with status: ${status}`)
      
      if (status === 404) {
        error.value = `Run "${runId}" not found. It may have been deleted or never existed.`
        addLogEntry('Error: Run not found (404)')
      } else if (status === 500) {
        error.value = 'Server error occurred while loading run details. Please try again later.'
        addLogEntry('Error: Server error (500)')
      } else {
        error.value = err.response.data?.detail || err.message || 'Failed to load run details'
        addLogEntry(`Error: ${error.value}`)
      }
    } else if (err.request) {
      // Request made but no response
      addLogEntry('✗ No response from backend server')
      addLogEntry('Backend may not be running or network issue')
      error.value = 'Cannot connect to backend server. Please ensure it is running at the configured URL.'
    } else {
      // Something else happened
      addLogEntry(`✗ Unexpected error: ${err.message}`)
      error.value = err.message || 'An unexpected error occurred while loading run details'
    }
    console.error('Error loading run:', err)
  } finally {
    loading.value = false
    if (loading.value === false && actionLog.value.length > 0) {
      addLogEntry('Loading process completed')
    }
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

.loading-container {
  @apply flex justify-center py-8;
}

.loading-card {
  @apply bg-white border-2 border-blue-300 rounded-lg p-6 max-w-2xl w-full shadow-lg;
}

.loading-header {
  @apply flex items-center gap-4 mb-4 pb-4 border-b border-gray-200;
}

.loading-title {
  @apply text-xl font-semibold text-gray-900;
}

.action-log {
  @apply mt-4;
}

.action-log-header {
  @apply text-sm font-semibold text-gray-700 mb-2;
}

.action-log-entries {
  @apply bg-gray-50 border border-gray-200 rounded p-4 max-h-64 overflow-y-auto font-mono text-xs;
}

.log-entry {
  @apply text-gray-700 py-1;
}

.log-entry:last-child {
  @apply font-semibold;
}

.error-container {
  @apply flex justify-center py-8;
}

.error-card {
  @apply bg-red-50 border-2 border-red-300 rounded-lg p-6 max-w-md shadow-lg flex gap-4;
}

.error-icon {
  @apply text-4xl flex-shrink-0;
}

.error-content {
  @apply flex-1;
}

.error-title {
  @apply text-lg font-bold text-red-900 mb-2;
}

.error-message {
  @apply text-sm text-red-700 mb-4;
}

.error-actions {
  @apply flex gap-2;
}

.btn-retry {
  @apply px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm font-medium;
}

.btn-back {
  @apply px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors text-sm font-medium;
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
