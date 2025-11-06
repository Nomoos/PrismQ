<template>
  <div class="multi-run-monitor">
    <div v-if="monitoredRuns.length === 0" class="empty-state">
      <p class="text-gray-500">No runs being monitored</p>
      <p class="text-sm text-gray-400 mt-2">Start a module or view active runs to begin monitoring</p>
    </div>
    
    <div v-else>
      <div class="tabs">
        <div
          v-for="run in monitoredRuns"
          :key="run.run_id"
          :class="['tab', { active: activeRunId === run.run_id }]"
          @click="switchToRun(run.run_id)"
        >
          <span class="tab-name">{{ run.module_name }}</span>
          <span :class="['status-indicator', getStatusClass(run.status)]" :title="run.status"></span>
          <span 
            @click.stop="closeTab(run.run_id)" 
            class="close-btn"
            :title="`Close ${run.module_name}`"
            role="button"
            tabindex="0"
            @keydown.enter="closeTab(run.run_id)"
            @keydown.space.prevent="closeTab(run.run_id)"
          >
            ×
          </span>
        </div>
      </div>
      
      <div class="tab-content">
        <LogViewer 
          v-if="activeRunId"
          :run-id="activeRunId"
          :key="activeRunId"
          :auto-scroll="true"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import LogViewer from './LogViewer.vue'
import { runService } from '@/services/runs'
import type { Run } from '@/types/run'

/**
 * MultiRunMonitor component
 * 
 * Provides a tabbed interface for monitoring multiple concurrent runs.
 * Users can switch between different run logs and close tabs.
 * 
 * Features:
 * - Tabbed interface for multiple runs
 * - Status indicator for each run
 * - Close individual tabs
 * - Live log streaming for active run
 */

const monitoredRuns = ref<Run[]>([])
const activeRunId = ref<string | null>(null)
const pollInterval = ref<ReturnType<typeof setInterval> | null>(null)

defineExpose({
  addRun,
  removeRun,
  clearAll
})

onMounted(() => {
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

/**
 * Add a run to the monitoring tabs
 */
function addRun(run: Run) {
  // Check if already being monitored
  const exists = monitoredRuns.value.find(r => r.run_id === run.run_id)
  if (exists) {
    // Just switch to it
    switchToRun(run.run_id)
    return
  }
  
  // Add to monitored runs
  monitoredRuns.value.push(run)
  
  // Switch to the new run
  switchToRun(run.run_id)
}

/**
 * Remove a run from monitoring
 */
function removeRun(runId: string) {
  closeTab(runId)
}

/**
 * Clear all monitored runs
 */
function clearAll() {
  monitoredRuns.value = []
  activeRunId.value = null
}

/**
 * Switch to a different run tab
 */
function switchToRun(runId: string) {
  activeRunId.value = runId
}

/**
 * Close a run tab
 */
function closeTab(runId: string) {
  const index = monitoredRuns.value.findIndex(r => r.run_id === runId)
  if (index === -1) return
  
  monitoredRuns.value.splice(index, 1)
  
  // Switch to another tab if closing active
  if (activeRunId.value === runId) {
    if (monitoredRuns.value.length > 0) {
      // Switch to the previous tab or first tab
      const newIndex = Math.max(0, index - 1)
      const newRun = monitoredRuns.value[newIndex]
      activeRunId.value = newRun.run_id
    } else {
      activeRunId.value = null
    }
  }
}

/**
 * Poll for run status updates
 * Only polls for active runs (running/queued) to reduce API calls
 */
function startPolling() {
  pollInterval.value = setInterval(async () => {
    // Only update runs that are still active (running or queued)
    const activeRuns = monitoredRuns.value.filter(
      run => run.status === 'running' || run.status === 'queued'
    )
    
    // If no active runs, no need to poll
    if (activeRuns.length === 0) return
    
    // Update status for active monitored runs
    for (const run of activeRuns) {
      try {
        const updated = await runService.getRun(run.run_id)
        // Update the run in place
        Object.assign(run, updated)
      } catch (err) {
        console.error(`Error updating run ${run.run_id}:`, err)
      }
    }
  }, 5000) // Poll every 5 seconds
}

/**
 * Stop polling
 */
function stopPolling() {
  if (pollInterval.value !== null) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

/**
 * Get CSS class for status indicator
 */
function getStatusClass(status: string): string {
  const colors: Record<string, string> = {
    queued: 'bg-yellow-400',
    running: 'bg-blue-500 animate-pulse',
    completed: 'bg-green-500',
    failed: 'bg-red-500',
    cancelled: 'bg-gray-400'
  }
  
  return colors[status] || 'bg-gray-300'
}
</script>

<style scoped>
.multi-run-monitor {
  @apply bg-white rounded-lg shadow;
}

.empty-state {
  @apply text-center py-12 px-4;
}

.tabs {
  @apply flex gap-1 bg-gray-50 p-2 rounded-t-lg overflow-x-auto;
}

.tab {
  @apply flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-t hover:bg-gray-50 transition-colors relative whitespace-nowrap cursor-pointer;
}

.tab.active {
  @apply bg-white border-b-white -mb-px z-10 shadow-sm;
}

.tab-name {
  @apply text-sm font-medium text-gray-700;
}

.tab.active .tab-name {
  @apply text-blue-600;
}

.status-indicator {
  @apply w-2 h-2 rounded-full inline-block;
}

.close-btn {
  @apply ml-2 text-gray-400 hover:text-gray-600 font-bold text-lg leading-none transition-colors;
}

.close-btn:hover {
  @apply text-red-500;
}

.tab-content {
  @apply p-4 bg-white rounded-b-lg border border-t-0 border-gray-200 min-h-96;
}
</style>
