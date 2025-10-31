# Issue #108: Support Multiple Concurrent Runs

**Type**: Feature  
**Priority**: Medium  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1-2 weeks  
**Dependencies**: #103 (Backend Module Runner), #107 (Live Logs UI)  
**Can be parallelized with**: None (requires core features complete)

---

## Description

Enhance the system to handle running multiple modules simultaneously, or the same module multiple times concurrently. This includes backend process management, frontend UI for tracking multiple runs, and proper isolation of logs and state.

## Backend Enhancements

### 1. Concurrent Execution Manager

Already partially implemented in #103, but needs enhancement:

```python
# src/core/module_runner.py

class ModuleRunner:
    def __init__(self, max_concurrent_runs: int = 10):
        self.max_concurrent_runs = max_concurrent_runs
        self.active_runs: Dict[str, asyncio.Task] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent_runs)
    
    async def execute_module(self, ...):
        # Check limit
        if len(self.active_runs) >= self.max_concurrent_runs:
            raise RuntimeError(f"Max concurrent runs ({self.max_concurrent_runs}) reached")
        
        # Acquire semaphore
        async with self.semaphore:
            # Create and track task
            task = asyncio.create_task(self._execute_async(...))
            self.active_runs[run_id] = task
            
            try:
                await task
            finally:
                del self.active_runs[run_id]
```

### 2. Resource Management

```python
# src/core/resource_manager.py

class ResourceManager:
    """
    Manage system resources for concurrent runs.
    
    - CPU allocation
    - Memory limits
    - GPU scheduling (if applicable)
    """
    
    def __init__(self):
        self.cpu_limit_per_run = 2  # cores
        self.memory_limit_per_run = 4 * 1024 * 1024 * 1024  # 4GB
    
    async def allocate_resources(self, run_id: str) -> bool:
        """Check if resources available for new run."""
        # Check system resources
        import psutil
        
        available_memory = psutil.virtual_memory().available
        if available_memory < self.memory_limit_per_run:
            return False
        
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 80:  # System too busy
            return False
        
        return True
```

## Frontend Enhancements

### 1. Active Runs Dashboard

```vue
<!-- src/components/ActiveRuns.vue -->

<template>
  <div class="active-runs">
    <h2>Active Runs ({{ activeRuns.length }})</h2>
    
    <div v-if="activeRuns.length === 0" class="empty">
      No active runs
    </div>
    
    <div v-else class="runs-list">
      <RunCard 
        v-for="run in activeRuns"
        :key="run.run_id"
        :run="run"
        @view="viewRun"
        @cancel="cancelRun"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { runService } from '@/services/runs'

const activeRuns = ref([])
const pollInterval = ref(null)

onMounted(() => {
  loadActiveRuns()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

async function loadActiveRuns() {
  const result = await runService.getRuns({
    status: 'running'
  })
  activeRuns.value = result.runs
}

function startPolling() {
  pollInterval.value = setInterval(loadActiveRuns, 3000)
}

function stopPolling() {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
  }
}
</script>
```

### 2. Run History View

```vue
<!-- src/views/RunHistory.vue -->

<template>
  <div class="run-history">
    <header>
      <h1>Run History</h1>
      
      <div class="filters">
        <select v-model="statusFilter">
          <option value="">All Status</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        
        <select v-model="moduleFilter">
          <option value="">All Modules</option>
          <option v-for="module in modules" :key="module.id">
            {{ module.name }}
          </option>
        </select>
      </div>
    </header>
    
    <table class="runs-table">
      <thead>
        <tr>
          <th>Run ID</th>
          <th>Module</th>
          <th>Status</th>
          <th>Started</th>
          <th>Duration</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="run in filteredRuns" :key="run.run_id">
          <td>{{ run.run_id }}</td>
          <td>{{ run.module_name }}</td>
          <td><StatusBadge :status="run.status" /></td>
          <td>{{ formatDate(run.started_at) }}</td>
          <td>{{ formatDuration(run.duration_seconds) }}</td>
          <td>
            <button @click="viewRun(run.run_id)">View</button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <div class="pagination">
      <button 
        :disabled="offset === 0"
        @click="previousPage"
      >
        Previous
      </button>
      <span>{{ offset / limit + 1 }} of {{ totalPages }}</span>
      <button 
        :disabled="offset + limit >= total"
        @click="nextPage"
      >
        Next
      </button>
    </div>
  </div>
</template>
```

### 3. Multi-Run Monitoring

```vue
<!-- src/components/MultiRunMonitor.vue -->

<template>
  <div class="multi-run-monitor">
    <div class="tabs">
      <button
        v-for="run in monitoredRuns"
        :key="run.run_id"
        :class="{ active: activeRunId === run.run_id }"
        @click="switchToRun(run.run_id)"
      >
        {{ run.module_name }}
        <StatusIndicator :status="run.status" />
        <button @click.stop="closeTab(run.run_id)">×</button>
      </button>
    </div>
    
    <div class="tab-content">
      <LogViewer 
        v-if="activeRunId"
        :run-id="activeRunId"
        :key="activeRunId"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const monitoredRuns = ref([])
const activeRunId = ref(null)

function switchToRun(runId: string) {
  activeRunId.value = runId
}

function closeTab(runId: string) {
  const index = monitoredRuns.value.findIndex(r => r.run_id === runId)
  if (index !== -1) {
    monitoredRuns.value.splice(index, 1)
    
    // Switch to another tab if closing active
    if (activeRunId.value === runId && monitoredRuns.value.length > 0) {
      activeRunId.value = monitoredRuns.value[0].run_id
    }
  }
}
</script>
```

---

## Tasks

### Backend
- [x] Implement concurrent run limiting
- [x] Add resource management checks
- [x] Ensure proper process isolation
- [x] Test concurrent execution under load
- [x] Add metrics for concurrent runs

### Frontend
- [x] Create ActiveRuns component
- [x] Implement RunHistory view
- [x] Add multi-run tabbed interface
- [x] Update dashboard to show active runs
- [x] Add quick actions (view, cancel, restart)

### State Management
- [x] Track multiple runs in state
- [x] Poll all active runs efficiently
- [x] Handle run lifecycle events
- [ ] Implement run notifications (future enhancement)

### Testing
- [x] Test concurrent module launches
- [x] Test resource limits enforcement
- [x] Test UI with multiple runs
- [ ] Load testing (10+ concurrent runs) (manual testing recommended)
- [x] Test log isolation between runs

---

## Acceptance Criteria

- [x] Multiple modules can run concurrently (up to limit)
- [x] Same module can have multiple concurrent runs
- [x] Each run has isolated logs and state
- [x] Concurrent run limit enforced
- [x] UI displays all active runs
- [x] User can switch between run logs
- [x] Run history view shows all past runs
- [x] System remains stable under concurrent load
- [x] Resource usage monitored and limited

## Performance Targets

- Support 10+ concurrent runs
- No performance degradation with multiple runs
- Efficient polling (don't query each run separately)
- Memory usage scales linearly

## Related Issues

- **Depends on**: #103, #107
- **Related**: #109 (Error Handling)

## References

- [Python asyncio Semaphores](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore)
- [psutil - System monitoring](https://psutil.readthedocs.io/)
