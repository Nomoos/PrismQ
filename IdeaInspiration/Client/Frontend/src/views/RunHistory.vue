<template>
  <div class="run-history">
    <header class="header">
      <h1 class="title">Run History</h1>
      
      <div class="filters">
        <select v-model="statusFilter" class="filter-select">
          <option value="">All Status</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="cancelled">Cancelled</option>
          <option value="running">Running</option>
          <option value="queued">Queued</option>
        </select>
        
        <select v-model="moduleFilter" class="filter-select">
          <option value="">All Modules</option>
          <option v-for="module in availableModules" :key="module" :value="module">
            {{ module }}
          </option>
        </select>
        
        <button @click="loadRuns" class="btn-refresh">
          Refresh
        </button>
      </div>
    </header>
    
    <div v-if="loading" class="loading-container">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p class="mt-4 text-gray-600">Loading runs...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        <p class="font-bold">Error loading runs</p>
        <p class="text-sm">{{ error }}</p>
      </div>
    </div>
    
    <div v-else>
      <div v-if="runs.length === 0" class="empty-state">
        <p class="text-gray-600">
          {{ statusFilter || moduleFilter ? 'No runs match your filters' : 'No runs found' }}
        </p>
      </div>
      
      <div v-else class="table-container">
        <table class="runs-table">
          <thead>
            <tr>
              <th>Module</th>
              <th>Status</th>
              <th>Started</th>
              <th>Duration</th>
              <th>Progress</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="run in paginatedRuns" 
              :key="run.run_id || run.id"
              @click="viewRun(run)"
              class="table-row"
            >
              <td class="module-cell">
                <div class="module-name">{{ run.module_name }}</div>
                <div class="run-id">{{ run.run_id || run.id }}</div>
              </td>
              <td>
                <StatusBadge :status="run.status" />
              </td>
              <td>{{ formatDate(run.started_at || run.start_time || run.created_at || '') }}</td>
              <td>{{ formatDuration(run.duration_seconds) }}</td>
              <td>
                <div v-if="run.items_processed && run.items_total" class="progress-info">
                  {{ run.items_processed }} / {{ run.items_total }}
                  <span v-if="run.progress_percent" class="progress-percent">
                    ({{ run.progress_percent }}%)
                  </span>
                </div>
                <div v-else-if="run.progress_percent">
                  {{ run.progress_percent }}%
                </div>
                <span v-else class="text-gray-400">--</span>
              </td>
              <td>
                <div class="action-buttons">
                  <button @click.stop="viewRun(run)" class="btn-view">
                    View
                  </button>
                  <button 
                    v-if="run.status === 'running' || run.status === 'queued'"
                    @click.stop="cancelRun(run)" 
                    class="btn-cancel"
                  >
                    Cancel
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="totalPages > 1" class="pagination">
        <button 
          :disabled="currentPage === 1"
          @click="previousPage"
          class="btn-page"
        >
          Previous
        </button>
        <span class="page-info">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <button 
          :disabled="currentPage >= totalPages"
          @click="nextPage"
          class="btn-page"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { runService } from '@/services/runs'
import StatusBadge from '@/components/StatusBadge.vue'
import type { Run } from '@/types/run'

const router = useRouter()

const runs = ref<Run[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const statusFilter = ref('')
const moduleFilter = ref('')
const currentPage = ref(1)
const pageSize = 20

// Computed properties
const availableModules = computed(() => {
  const modules = new Set(runs.value.map(r => r.module_name))
  return Array.from(modules).sort()
})

const filteredRuns = computed(() => {
  let filtered = runs.value
  
  if (statusFilter.value) {
    filtered = filtered.filter(r => r.status === statusFilter.value)
  }
  
  if (moduleFilter.value) {
    filtered = filtered.filter(r => r.module_name === moduleFilter.value)
  }
  
  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredRuns.value.length / pageSize)
})

const paginatedRuns = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredRuns.value.slice(start, end)
})

// Watch filters and reset to page 1
watch([statusFilter, moduleFilter], () => {
  currentPage.value = 1
})

onMounted(() => {
  loadRuns()
})

async function loadRuns() {
  try {
    loading.value = true
    error.value = null
    // Load reasonable number of recent runs - user can paginate through more
    runs.value = await runService.listRuns({ limit: 100 })
  } catch (err: any) {
    error.value = err.message || 'Failed to load runs'
    console.error('Error loading runs:', err)
  } finally {
    loading.value = false
  }
}

function viewRun(run: Run) {
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
      await loadRuns()
    } catch (err: any) {
      alert(`Failed to cancel run: ${err.message}`)
      console.error('Error canceling run:', err)
    }
  }
}

function previousPage() {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

function formatDate(timestamp: string | undefined): string {
  if (!timestamp) return '--'
  const date = new Date(timestamp)
  return date.toLocaleString()
}

function formatDuration(seconds: number | undefined): string {
  if (seconds === undefined || seconds === null) return '--'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}m ${secs}s`
}
</script>

<style scoped>
.run-history {
  @apply max-w-7xl mx-auto px-4 py-6;
}

.header {
  @apply mb-6;
}

.title {
  @apply text-3xl font-semibold text-gray-900 mb-4;
}

.filters {
  @apply flex gap-4;
}

.filter-select {
  @apply px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white;
}

.btn-refresh {
  @apply px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors;
}

.loading-container,
.error-container,
.empty-state {
  @apply text-center py-12;
}

.table-container {
  @apply overflow-x-auto bg-white rounded-lg shadow;
}

.runs-table {
  @apply min-w-full divide-y divide-gray-200;
}

.runs-table thead {
  @apply bg-gray-50;
}

.runs-table th {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider;
}

.runs-table tbody {
  @apply bg-white divide-y divide-gray-200;
}

.table-row {
  @apply hover:bg-gray-50 cursor-pointer transition-colors;
}

.runs-table td {
  @apply px-6 py-4 whitespace-nowrap text-sm;
}

.module-cell {
  @apply space-y-1;
}

.module-name {
  @apply font-medium text-gray-900;
}

.run-id {
  @apply text-xs text-gray-500;
}

.progress-info {
  @apply text-gray-900;
}

.progress-percent {
  @apply text-gray-500;
}

.action-buttons {
  @apply flex gap-2;
}

.btn-view {
  @apply px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded transition-colors;
}

.btn-cancel {
  @apply px-3 py-1 bg-red-50 hover:bg-red-100 text-red-600 rounded transition-colors;
}

.pagination {
  @apply flex justify-center items-center gap-4 mt-6;
}

.btn-page {
  @apply px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors;
}

.page-info {
  @apply text-sm text-gray-700;
}
</style>
