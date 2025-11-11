# API Integration Guide

Complete guide for integrating with the Frontend/TaskManager API layer.

## Overview

The Frontend/TaskManager uses a service-based architecture to communicate with the Backend/TaskManager API. All API communication goes through typed service layers with built-in error handling, retry logic, and caching.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Vue Components                      │
│              (TaskList, TaskDetail, etc.)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   Pinia Stores                          │
│              (useTaskStore, useWorkerStore)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                          │
│         (taskService, healthService, etc.)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  API Client (Axios)                     │
│        (api.ts - with retry & error handling)           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
          Backend/TaskManager REST API
```

## Core Components

### 1. API Client (`src/services/api.ts`)

The base API client handles all HTTP communication.

**Features:**
- Automatic retry on network errors (3 attempts)
- Request/response logging in development
- Error transformation
- Configurable timeout (30s default)
- API key authentication

**Configuration:**
```typescript
// Environment variables (.env)
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_KEY=your-api-key-here
```

**Usage:**
```typescript
import api from '@/services/api'

// GET request
const data = await api.get<ResponseType>('/endpoint', { param: 'value' })

// POST request
const result = await api.post<ResponseType>('/endpoint', { key: 'value' })

// PUT request
const updated = await api.put<ResponseType>('/endpoint', { key: 'value' })

// DELETE request
const deleted = await api.delete<ResponseType>('/endpoint')
```

### 2. Task Service (`src/services/taskService.ts`)

Handles all task-related API operations.

**Available Methods:**

#### Get Tasks
```typescript
import { taskService } from '@/services/taskService'

// Get all tasks with optional filters
const response = await taskService.getTasks({
  status: 'pending',  // optional: pending, claimed, completed, failed
  type: 'task-type',  // optional: filter by task type
  limit: 20,          // optional: pagination limit
  offset: 0           // optional: pagination offset
})

// Response type: PaginatedResponse<Task>
console.log(response.data)    // Task[]
console.log(response.total)   // number
console.log(response.success) // boolean
```

#### Get Single Task
```typescript
// Get task by ID (cached for 30 seconds)
const response = await taskService.getTask(taskId)

if (response.success) {
  const task = response.data
  console.log(task.status)
  console.log(task.params)
  console.log(task.result)
}
```

#### Create Task
```typescript
const response = await taskService.createTask({
  type: 'PrismQ.YouTube.ScrapeShorts',
  params: {
    search_query: 'inspiration',
    max_results: 10
  },
  priority: 5
})

if (response.success) {
  const newTask = response.data
  console.log('Created task:', newTask.id)
}
```

#### Claim Task
```typescript
const response = await taskService.claimTask({
  worker_id: 'worker-123',
  task_type_id: 1
})

if (response.success && response.data) {
  const claimedTask = response.data
  console.log('Processing:', claimedTask.id)
}
```

#### Complete Task
```typescript
// Success
await taskService.completeTask(taskId, {
  worker_id: 'worker-123',
  success: true,
  result: {
    videos_found: 42,
    data: [/* ... */]
  }
})

// Failure
await taskService.completeTask(taskId, {
  worker_id: 'worker-123',
  success: false,
  error: 'API rate limit exceeded'
})
```

#### Update Progress
```typescript
await taskService.updateProgress(taskId, {
  worker_id: 'worker-123',
  progress: 65,  // percentage
  message: 'Processing video 13/20'
})
```

#### Task Types
```typescript
// Get all active task types (cached for 5 minutes)
const response = await taskService.getTaskTypes(true)
const taskTypes = response.data

// Get specific task type
const typeResponse = await taskService.getTaskType('PrismQ.YouTube.ScrapeShorts')

// Register new task type
await taskService.registerTaskType({
  name: 'PrismQ.Custom.NewTask',
  version: '1.0.0',
  param_schema: {
    param1: { type: 'string', required: true },
    param2: { type: 'number', default: 10 }
  }
})
```

### 3. Health Service (`src/services/healthService.ts`)

Check API health status.

```typescript
import { healthService } from '@/services/healthService'

const response = await healthService.check()
if (response.status === 'healthy') {
  console.log('API is operational')
}
```

## Using Stores (Recommended)

For Vue components, use Pinia stores instead of calling services directly.

### Task Store (`src/stores/tasks.ts`)

```typescript
import { useTaskStore } from '@/stores/tasks'

export default {
  setup() {
    const taskStore = useTaskStore()
    
    // Fetch tasks
    await taskStore.fetchTasks({ status: 'pending' })
    
    // Access state
    console.log(taskStore.tasks)
    console.log(taskStore.pendingTasks)
    console.log(taskStore.loading)
    console.log(taskStore.error)
    
    // Create task
    const response = await taskStore.createTask({
      type: 'task-type',
      params: {}
    })
    
    // Claim task
    const task = await taskStore.claimTask('worker-id', taskTypeId)
    
    // Complete task
    await taskStore.completeTask(
      taskId,
      'worker-id',
      true,
      { result: 'data' }
    )
    
    // Update progress
    await taskStore.updateProgress(
      taskId,
      'worker-id',
      50,
      'Halfway done'
    )
    
    return { taskStore }
  }
}
```

### Worker Store (`src/stores/worker.ts`)

```typescript
import { useWorkerStore } from '@/stores/worker'

export default {
  setup() {
    const workerStore = useWorkerStore()
    
    // Initialize worker (generates ID if needed)
    workerStore.initializeWorker()
    
    // Access worker info
    console.log(workerStore.workerId)
    console.log(workerStore.status)
    console.log(workerStore.isInitialized)
    
    // Update status
    workerStore.setStatus('active')
    
    return { workerStore }
  }
}
```

## Error Handling

### Error Types

The API client throws specific error types:

```typescript
import { APIError, NetworkError } from '@/types'

try {
  await taskService.getTasks()
} catch (error) {
  if (error instanceof APIError) {
    // Server error with status code
    console.error('API Error:', error.message)
    console.error('Status:', error.status)
    console.error('Data:', error.data)
  } else if (error instanceof NetworkError) {
    // Network connectivity issue
    console.error('Network Error:', error.message)
  } else {
    // Other error
    console.error('Error:', error)
  }
}
```

### Automatic Retry

Network errors are automatically retried up to 3 times with exponential backoff:
- Attempt 1: immediate
- Attempt 2: 1 second delay
- Attempt 3: 2 second delay
- Attempt 4: 3 second delay

### Cache Invalidation

Some methods automatically invalidate caches:
```typescript
// Invalidates task:{id} cache
await taskService.completeTask(id, data)
await taskService.updateProgress(id, data)
```

## Request Caching

The service layer uses intelligent caching via `src/utils/cache.ts`:

```typescript
import { requestCache } from '@/utils/cache'

// Cached request (default TTL: 60s)
const data = await requestCache.get(
  'cache-key',
  async () => {
    return await fetchDataFromAPI()
  }
)

// Custom TTL
const data = await requestCache.get(
  'cache-key',
  async () => fetchDataFromAPI(),
  { ttl: 300000 } // 5 minutes
)

// Manual invalidation
requestCache.invalidate('cache-key')

// Clear all cache
requestCache.clear()

// Check cache stats
console.log(requestCache.stats())
```

## Real-time Updates

Use the polling composable for real-time task updates:

```typescript
import { useTaskPolling } from '@/composables/useTaskPolling'

export default {
  setup() {
    const { isPolling, startPolling, stopPolling } = useTaskPolling({
      interval: 5000  // 5 seconds
    })
    
    // Start polling
    startPolling()
    
    // Stop polling
    onUnmounted(() => {
      stopPolling()
    })
    
    return { isPolling }
  }
}
```

## Type Definitions

All API types are defined in `src/types/index.ts`:

```typescript
// Core types
interface Task {
  id: number
  type: string
  status: 'pending' | 'claimed' | 'completed' | 'failed'
  params: Record<string, any>
  result?: Record<string, any>
  error_message?: string
  priority: number
  progress: number
  created_at: string
  claimed_at?: string
  completed_at?: string
  worker_id?: string
}

interface TaskType {
  id: number
  name: string
  version: string
  param_schema: Record<string, any>
  active: boolean
}

// Request types
interface CreateTaskRequest {
  type: string
  params: Record<string, any>
  priority?: number
}

interface ClaimTaskRequest {
  worker_id: string
  task_type_id: number
}

interface CompleteTaskRequest {
  worker_id: string
  success: boolean
  result?: Record<string, any>
  error?: string
}

// Response types
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

interface PaginatedResponse<T> extends ApiResponse<T[]> {
  total: number
  limit: number
  offset: number
}
```

## Best Practices

### 1. Use Stores in Components
✅ **Good:**
```typescript
const taskStore = useTaskStore()
await taskStore.fetchTasks()
```

❌ **Avoid:**
```typescript
import { taskService } from '@/services/taskService'
await taskService.getTasks()
```

### 2. Handle Loading States
```typescript
const taskStore = useTaskStore()

watchEffect(() => {
  if (taskStore.loading) {
    // Show spinner
  }
})

await taskStore.fetchTasks()
```

### 3. Handle Errors Gracefully
```typescript
try {
  await taskStore.createTask(data)
  // Show success toast
} catch (error) {
  // Show error toast
  console.error(error)
}
```

### 4. Clean Up Polling
```typescript
onUnmounted(() => {
  stopPolling()
})
```

### 5. Use TypeScript Types
```typescript
import type { Task, TaskType } from '@/types'

const task: Task = await taskStore.fetchTask(id)
```

## Examples

### Complete Task Workflow

```typescript
import { useTaskStore } from '@/stores/tasks'
import { useWorkerStore } from '@/stores/worker'
import { useToast } from '@/composables/useToast'

export default {
  setup() {
    const taskStore = useTaskStore()
    const workerStore = useWorkerStore()
    const { showSuccess, showError } = useToast()
    
    // Initialize worker
    workerStore.initializeWorker()
    
    async function processTask() {
      try {
        // Claim a task
        const task = await taskStore.claimTask(
          workerStore.workerId!,
          1 // task type id
        )
        
        if (!task) {
          showError('No tasks available')
          return
        }
        
        showSuccess('Task claimed')
        
        // Simulate processing with progress updates
        for (let i = 0; i <= 100; i += 20) {
          await taskStore.updateProgress(
            task.id,
            workerStore.workerId!,
            i,
            `Processing: ${i}%`
          )
          await sleep(1000)
        }
        
        // Complete task
        await taskStore.completeTask(
          task.id,
          workerStore.workerId!,
          true,
          { processed: true }
        )
        
        showSuccess('Task completed')
        
      } catch (error) {
        showError('Task processing failed')
        console.error(error)
      }
    }
    
    return { processTask }
  }
}
```

### Task List with Polling

```typescript
import { useTaskStore } from '@/stores/tasks'
import { useTaskPolling } from '@/composables/useTaskPolling'

export default {
  setup() {
    const taskStore = useTaskStore()
    
    // Initial load
    onMounted(async () => {
      await taskStore.fetchTasks({ status: 'pending' })
    })
    
    // Auto-refresh every 5 seconds
    const { startPolling, stopPolling } = useTaskPolling({
      interval: 5000
    })
    
    startPolling()
    
    onUnmounted(() => {
      stopPolling()
    })
    
    return {
      tasks: computed(() => taskStore.pendingTasks),
      loading: computed(() => taskStore.loading)
    }
  }
}
```

## Troubleshooting

### CORS Errors
Ensure Backend/TaskManager has CORS configured:
```python
# Backend config
CORS_ORIGINS = ["http://localhost:5173", "https://your-domain.com"]
```

### Authentication Errors
Set the API key in `.env`:
```bash
VITE_API_KEY=your-api-key
```

### Network Timeouts
Increase timeout in `api.ts`:
```typescript
timeout: 60000  // 60 seconds
```

### Cache Issues
Clear cache manually:
```typescript
import { requestCache } from '@/utils/cache'
requestCache.clear()
```

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List tasks |
| GET | `/api/tasks/:id` | Get task details |
| POST | `/api/tasks` | Create task |
| POST | `/api/tasks/claim` | Claim pending task |
| POST | `/api/tasks/:id/complete` | Complete task |
| POST | `/api/tasks/:id/progress` | Update progress |
| GET | `/api/task-types` | List task types |
| GET | `/api/task-types/:name` | Get task type |
| POST | `/api/task-types/register` | Register task type |
| GET | `/api/health` | Health check |

## Support

- **Documentation**: `/Frontend/TaskManager/README.md`
- **Issues**: GitHub Issues
- **Examples**: `/Frontend/TaskManager/src/views/`

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-09  
**Maintained by**: Worker06 (API Integration Documentation)
