# Issue #107: Display Execution Status and Live Logs in UI

**Type**: Feature  
**Priority**: High  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 2 weeks  
**Dependencies**: #104 (Log Streaming), #105 (Frontend UI)  
**Can be parallelized with**: #106 (Parameter Persistence)

---

## Description

Create Vue components to display real-time execution status and stream live logs from running modules. This provides immediate feedback to users and enables monitoring of module progress, similar to Script-Server's real-time output feature.

## Components

### 1. RunDetails View (`src/views/RunDetails.vue`)

Main view for monitoring a specific run.

```vue
<template>
  <div class="run-details">
    <header class="run-header">
      <div class="run-info">
        <h1>{{ run?.module_name }}</h1>
        <span class="run-id">{{ run?.run_id }}</span>
      </div>
      
      <StatusBadge :status="run?.status" />
      
      <button 
        v-if="canCancel"
        @click="cancelRun"
        class="btn-danger"
      >
        Cancel Run
      </button>
    </header>
    
    <div class="run-stats">
      <StatCard label="Status" :value="run?.status" />
      <StatCard label="Duration" :value="formatDuration(run?.duration_seconds)" />
      <StatCard label="Progress" :value="`${run?.progress_percent || 0}%`" />
      <StatCard label="Items" :value="`${run?.items_processed || 0} / ${run?.items_total || '?'}`" />
    </div>
    
    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'logs' }"
        @click="activeTab = 'logs'"
      >
        Logs
      </button>
      <button 
        :class="{ active: activeTab === 'parameters' }"
        @click="activeTab = 'parameters'"
      >
        Parameters
      </button>
      <button 
        v-if="run?.status === 'completed'"
        :class="{ active: activeTab === 'results' }"
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
        :parameters="run?.parameters"
      />
      
      <ResultsView 
        v-else-if="activeTab === 'results'"
        :run-id="runId"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { runService } from '@/services/runs'
import LogViewer from '@/components/LogViewer.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const runId = route.params.id as string

const run = ref(null)
const activeTab = ref('logs')
const pollInterval = ref(null)

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
  run.value = await runService.getRun(runId)
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
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
  }
}

async function cancelRun() {
  if (confirm('Are you sure you want to cancel this run?')) {
    await runService.cancelRun(runId)
    await loadRun()
  }
}

function formatDuration(seconds: number | undefined): string {
  if (!seconds) return '--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}m ${secs}s`
}
</script>
```

### 2. LogViewer Component (`src/components/LogViewer.vue`)

Real-time log streaming with SSE.

```vue
<template>
  <div class="log-viewer">
    <div class="log-controls">
      <button @click="toggleAutoScroll" class="btn-small">
        {{ autoScroll ? '📌 Auto-scroll ON' : '📌 Auto-scroll OFF' }}
      </button>
      
      <select v-model="logLevel" class="level-filter">
        <option value="all">All Levels</option>
        <option value="ERROR">Errors Only</option>
        <option value="WARNING">Warnings+</option>
        <option value="INFO">Info+</option>
      </select>
      
      <button @click="downloadLogs" class="btn-small">
        ⬇️ Download
      </button>
      
      <button @click="clearLogs" class="btn-small">
        🗑️ Clear
      </button>
    </div>
    
    <div 
      ref="logContainer"
      class="log-container"
      @scroll="handleScroll"
    >
      <div 
        v-for="(log, index) in filteredLogs"
        :key="index"
        :class="['log-entry', `level-${log.level.toLowerCase()}`]"
      >
        <span class="log-timestamp">{{ formatTime(log.timestamp) }}</span>
        <span class="log-level">{{ log.level }}</span>
        <span class="log-message">{{ log.message }}</span>
      </div>
      
      <div v-if="isLoading" class="log-loading">
        Loading logs...
      </div>
      
      <div v-if="logs.length === 0 && !isLoading" class="log-empty">
        No logs yet. Waiting for output...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { runService } from '@/services/runs'
import type { LogEntry } from '@/types/run'

const props = defineProps<{
  runId: string
  autoScroll?: boolean
}>()

const logs = ref<LogEntry[]>([])
const logLevel = ref('all')
const autoScrollEnabled = ref(props.autoScroll ?? true)
const isLoading = ref(true)
const logContainer = ref<HTMLElement>()
const eventSource = ref<EventSource>()

const filteredLogs = computed(() => {
  if (logLevel.value === 'all') return logs.value
  
  const levels = {
    'ERROR': ['ERROR'],
    'WARNING': ['ERROR', 'WARNING'],
    'INFO': ['ERROR', 'WARNING', 'INFO']
  }
  
  return logs.value.filter(log => 
    levels[logLevel.value]?.includes(log.level)
  )
})

onMounted(() => {
  connectSSE()
})

onUnmounted(() => {
  disconnectSSE()
})

watch(() => props.runId, () => {
  logs.value = []
  disconnectSSE()
  connectSSE()
})

function connectSSE() {
  isLoading.value = true
  
  const url = `http://localhost:8000/api/runs/${props.runId}/logs/stream`
  eventSource.value = new EventSource(url)
  
  eventSource.value.onmessage = (event) => {
    const log = JSON.parse(event.data)
    logs.value.push(log)
    isLoading.value = false
    
    if (autoScrollEnabled.value) {
      nextTick(() => scrollToBottom())
    }
  }
  
  eventSource.value.onerror = (error) => {
    console.error('SSE error:', error)
    isLoading.value = false
    // Auto-reconnect after 5 seconds
    setTimeout(() => {
      if (eventSource.value?.readyState === EventSource.CLOSED) {
        connectSSE()
      }
    }, 5000)
  }
}

function disconnectSSE() {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = undefined
  }
}

function toggleAutoScroll() {
  autoScrollEnabled.value = !autoScrollEnabled.value
  if (autoScrollEnabled.value) {
    scrollToBottom()
  }
}

function scrollToBottom() {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

function handleScroll() {
  // Disable auto-scroll if user scrolls up
  if (logContainer.value) {
    const { scrollTop, scrollHeight, clientHeight } = logContainer.value
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 10
    if (!isAtBottom) {
      autoScrollEnabled.value = false
    }
  }
}

function clearLogs() {
  if (confirm('Clear all logs?')) {
    logs.value = []
  }
}

async function downloadLogs() {
  const blob = new Blob(
    [logs.value.map(l => `[${l.timestamp}] [${l.level}] ${l.message}`).join('\n')],
    { type: 'text/plain' }
  )
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.runId}.log`
  a.click()
  URL.revokeObjectURL(url)
}

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString()
}
</script>

<style scoped>
.log-container {
  height: 600px;
  overflow-y: auto;
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  padding: 1rem;
}

.log-entry {
  display: grid;
  grid-template-columns: 100px 80px 1fr;
  gap: 1rem;
  padding: 0.25rem 0;
  border-bottom: 1px solid #333;
}

.log-entry.level-error {
  color: #f48771;
  background: rgba(244, 135, 113, 0.1);
}

.log-entry.level-warning {
  color: #dcdcaa;
}

.log-entry.level-info {
  color: #d4d4d4;
}

.log-timestamp {
  color: #858585;
}

.log-level {
  font-weight: bold;
}

.log-message {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
```

### 3. StatusBadge Component

```vue
<template>
  <span :class="['status-badge', `status-${status}`]">
    {{ statusText }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
}>()

const statusText = computed(() => {
  const texts = {
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
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
}

.status-queued {
  background: #e0e7ff;
  color: #4338ca;
}

.status-running {
  background: #dbeafe;
  color: #1e40af;
  animation: pulse 2s infinite;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-failed {
  background: #fee2e2;
  color: #991b1b;
}

.status-cancelled {
  background: #f3f4f6;
  color: #4b5563;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
```

### 4. API Service Updates

```typescript
// src/services/runs.ts

import axios from 'axios'
import type { Run, LogEntry } from '@/types/run'

const API_BASE = 'http://localhost:8000/api'

class RunService {
  async getRun(runId: string): Promise<Run> {
    const response = await axios.get(`${API_BASE}/runs/${runId}`)
    return response.data
  }
  
  async getRuns(filters?: {
    module_id?: string
    status?: string
    limit?: number
    offset?: number
  }): Promise<{ runs: Run[], total: number }> {
    const response = await axios.get(`${API_BASE}/runs`, { params: filters })
    return response.data
  }
  
  async cancelRun(runId: string): Promise<void> {
    await axios.delete(`${API_BASE}/runs/${runId}`)
  }
  
  async getLogs(runId: string, tail?: number): Promise<LogEntry[]> {
    const response = await axios.get(`${API_BASE}/runs/${runId}/logs`, {
      params: { tail }
    })
    return response.data.logs
  }
  
  // SSE connection is handled directly in component via EventSource API
}

export const runService = new RunService()
```

---

## Tasks

### Components
- [ ] Create RunDetails view
- [ ] Implement LogViewer with SSE support
- [ ] Create StatusBadge component
- [ ] Create StatCard component
- [ ] Implement ParametersView component
- [ ] Implement ResultsView component

### Real-time Features
- [ ] Implement SSE connection in LogViewer
- [ ] Add auto-scroll functionality
- [ ] Add manual scroll detection
- [ ] Implement log level filtering
- [ ] Add log search functionality
- [ ] Handle SSE reconnection

### State Management
- [ ] Create run service API layer
- [ ] Implement status polling
- [ ] Add loading states
- [ ] Handle errors gracefully

### UX Enhancements
- [ ] Add download logs feature
- [ ] Add clear logs feature
- [ ] Show connection status indicator
- [ ] Add log highlighting for errors
- [ ] Implement log timestamps formatting

### Testing
- [ ] Component unit tests
- [ ] Test SSE connection handling
- [ ] Test auto-scroll behavior
- [ ] Test log filtering
- [ ] E2E tests for monitoring flow

---

## Acceptance Criteria

- [x] RunDetails view displays current run status
- [x] LogViewer streams logs in real-time via SSE
- [x] Auto-scroll works and can be toggled
- [x] Log levels are color-coded
- [x] Log filtering by level works
- [x] Download logs feature works
- [x] SSE reconnects automatically on disconnect
- [x] Status updates in real-time (polling)
- [x] Cancel button works for running modules
- [x] UI remains responsive with large log volumes

## Performance Targets

- SSE latency: <100ms
- Log rendering: >1000 lines without lag
- Memory usage: Reasonable with 10,000+ log lines
- Smooth auto-scroll with high log throughput

## Related Issues

- **Depends on**: #104 (Log Streaming), #105 (Frontend UI)
- **Parallel**: #106 (Parameter Persistence)
- **Related**: #108 (Multiple Concurrent Runs)

## References

- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [Vue Virtual Scroller](https://github.com/Akryum/vue-virtual-scroller) (for large logs)
