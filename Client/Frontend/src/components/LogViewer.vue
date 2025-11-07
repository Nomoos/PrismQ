<template>
  <div class="log-viewer">
    <div class="log-controls">
      <button @click="toggleAutoScroll" class="btn-small">
        {{ autoScrollEnabled ? '📌 Auto-scroll ON' : '📌 Auto-scroll OFF' }}
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
      
      <span v-if="connectionStatus" class="connection-status" :class="connectionStatus">
        {{ connectionStatus === 'connected' ? '🟢 Connected' : connectionStatus === 'connecting' ? '🟡 Connecting...' : '🔴 Disconnected' }}
      </span>
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
import type { LogEntry, LogLevel } from '@/types/run'

const props = defineProps<{
  runId: string
  autoScroll?: boolean
}>()

// Log level hierarchy for filtering
const LOG_LEVEL_FILTERS: Record<LogLevel, LogLevel[]> = {
  'ERROR': ['ERROR'],
  'WARNING': ['ERROR', 'WARNING'],
  'INFO': ['ERROR', 'WARNING', 'INFO'],
  'DEBUG': ['ERROR', 'WARNING', 'INFO', 'DEBUG']
}

const logs = ref<LogEntry[]>([])
const logLevel = ref<'all' | LogLevel>('all')
const autoScrollEnabled = ref(props.autoScroll ?? true)
const isLoading = ref(true)
const logContainer = ref<HTMLElement>()
const eventSource = ref<EventSource>()
const connectionStatus = ref<'connecting' | 'connected' | 'disconnected'>('connecting')

const filteredLogs = computed(() => {
  if (logLevel.value === 'all') return logs.value
  
  return logs.value.filter(log => 
    LOG_LEVEL_FILTERS[logLevel.value as LogLevel]?.includes(log.level)
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
  connectionStatus.value = 'connecting'
  
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const url = `${baseURL}/api/runs/${props.runId}/logs/stream`
  
  try {
    eventSource.value = new EventSource(url)
    
    eventSource.value.onopen = () => {
      connectionStatus.value = 'connected'
      isLoading.value = false
    }
    
    eventSource.value.onmessage = (event) => {
      try {
        const log = JSON.parse(event.data) as LogEntry
        logs.value.push(log)
        isLoading.value = false
        
        if (autoScrollEnabled.value) {
          nextTick(() => scrollToBottom())
        }
      } catch (err) {
        console.error('Failed to parse log entry:', err)
      }
    }
    
    eventSource.value.onerror = (error) => {
      console.error('SSE error:', error)
      connectionStatus.value = 'disconnected'
      isLoading.value = false
      
      // Auto-reconnect after 5 seconds
      setTimeout(() => {
        if (eventSource.value?.readyState === EventSource.CLOSED) {
          connectSSE()
        }
      }, 5000)
    }
  } catch (err) {
    console.error('Failed to create EventSource:', err)
    connectionStatus.value = 'disconnected'
    isLoading.value = false
  }
}

function disconnectSSE() {
  if (eventSource.value) {
    eventSource.value.close()
    eventSource.value = undefined
  }
  connectionStatus.value = 'disconnected'
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
    if (!isAtBottom && autoScrollEnabled.value) {
      autoScrollEnabled.value = false
    }
  }
}

function clearLogs() {
  if (confirm('Clear all logs from this view? (This does not affect server logs)')) {
    logs.value = []
  }
}

function downloadLogs() {
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
  try {
    return new Date(timestamp).toLocaleTimeString()
  } catch {
    return timestamp
  }
}
</script>

<style scoped>
.log-viewer {
  @apply bg-white rounded-lg border border-gray-200 overflow-hidden;
}

.log-controls {
  @apply flex items-center gap-2 p-3 bg-gray-50 border-b border-gray-200;
}

.btn-small {
  @apply px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-100 transition-colors;
}

.level-filter {
  @apply px-3 py-1 text-sm border border-gray-300 rounded bg-white;
}

.connection-status {
  @apply ml-auto text-sm font-medium;
}

.connection-status.connected {
  @apply text-green-600;
}

.connection-status.connecting {
  @apply text-yellow-600;
}

.connection-status.disconnected {
  @apply text-red-600;
}

.log-container {
  @apply h-[600px] overflow-y-auto bg-gray-900 text-gray-100 font-mono text-sm p-4;
}

.log-entry {
  @apply grid gap-4 py-1 border-b border-gray-800;
  grid-template-columns: 100px 80px 1fr;
}

.log-entry.level-error {
  @apply text-red-400 bg-red-900 bg-opacity-20;
}

.log-entry.level-warning {
  @apply text-yellow-300;
}

.log-entry.level-info {
  @apply text-gray-100;
}

.log-entry.level-debug {
  @apply text-gray-400;
}

.log-timestamp {
  @apply text-gray-500;
}

.log-level {
  @apply font-semibold;
}

.log-message {
  @apply whitespace-pre-wrap break-words;
}

.log-loading,
.log-empty {
  @apply text-center py-8 text-gray-500;
}
</style>
