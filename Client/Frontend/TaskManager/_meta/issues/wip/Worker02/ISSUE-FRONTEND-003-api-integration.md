# ISSUE-FRONTEND-003: TaskManager Integration

## Status
🔴 NOT STARTED

## Component
Frontend (API Integration)

## Type
API Integration / State Management

## Priority
High

## Assigned To
Worker02 - API Integration Expert

## Description
Create comprehensive integration layer between Frontend and Backend/TaskManager, including API client, TypeScript types, state management, and real-time updates.

## Problem Statement
The Frontend needs to:
- Communicate with Backend/TaskManager REST API
- Manage task and worker state
- Handle real-time task updates
- Provide robust error handling
- Type-safe API interactions

## Solution
Implement complete API integration including:
1. API client library (Axios or Fetch)
2. TypeScript interfaces from OpenAPI spec
3. Pinia stores for state management
4. Real-time update mechanism
5. Error handling and retry logic
6. Request/response interceptors

## Deliverables

### API Client
- [ ] Base API client configuration
- [ ] Authentication (API key)
- [ ] Request interceptors
- [ ] Response interceptors
- [ ] Error handling
- [ ] Retry logic

### TypeScript Types
- [ ] Task types (from OpenAPI)
- [ ] Worker types
- [ ] API request types
- [ ] API response types
- [ ] Error types
- [ ] Validation types

### Pinia Stores
- [ ] Task store (list, get, create, update)
- [ ] Worker store (registration, status)
- [ ] Auth store (API key management)
- [ ] Global state (loading, errors)

### Services
- [ ] Task service (CRUD operations)
- [ ] Worker service
- [ ] Health check service
- [ ] Real-time update service

### Real-time Updates
- [ ] Polling implementation (primary)
- [ ] Server-Sent Events (if supported)
- [ ] WebSocket (future enhancement)

### Documentation
- [ ] API integration guide
- [ ] Type definitions documentation
- [ ] State management guide
- [ ] Error handling patterns

## Acceptance Criteria
- [ ] API client configured and working
- [ ] All TypeScript types defined from OpenAPI
- [ ] Pinia stores implemented
- [ ] All CRUD operations working
- [ ] Real-time updates functional
- [ ] Error handling comprehensive
- [ ] Integration tests passing
- [ ] Documentation complete

## Dependencies
- Backend/TaskManager API (already complete)
- Backend OpenAPI specification

## Related Issues
- ISSUE-FRONTEND-004 (Core Components) - will use this integration
- ISSUE-FRONTEND-007 (Testing) - will test integration

## Backend/TaskManager API

### Endpoints Used

#### Task Management
```
GET    /tasks              # List all tasks
GET    /tasks/:id          # Get task details
POST   /tasks              # Create new task
POST   /tasks/:id/claim    # Claim task
POST   /tasks/:id/progress # Update progress
POST   /tasks/:id/complete # Complete task
POST   /tasks/:id/fail     # Fail task
```

#### Worker Management (if available)
```
GET    /workers            # List workers
POST   /workers/register   # Register worker
```

#### Health
```
GET    /health             # API health check
```

## TypeScript Types

### Task Type
```typescript
interface Task {
  id: number;
  task_type: string;
  status: 'pending' | 'claimed' | 'completed' | 'failed';
  priority: number;
  progress: number;
  params: Record<string, any>;
  result: Record<string, any> | null;
  claimed_by: string | null;
  created_at: string;
  updated_at: string;
  claimed_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  attempts: number;
}

interface CreateTaskRequest {
  task_type: string;
  params: Record<string, any>;
  priority?: number;
}

interface ClaimTaskRequest {
  worker_id: string;
}

interface UpdateProgressRequest {
  worker_id: string;
  progress: number;
  message?: string;
}

interface CompleteTaskRequest {
  worker_id: string;
  result: Record<string, any>;
}
```

## API Client Implementation

### Base Configuration
```typescript
// services/api.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': import.meta.env.VITE_API_KEY
  }
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add timestamp, logging, etc.
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // Handle errors globally
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Task Service
```typescript
// services/tasks.ts
import apiClient from './api';
import type { Task, CreateTaskRequest } from '@/types';

export const taskService = {
  list: async (): Promise<Task[]> => {
    return apiClient.get('/tasks');
  },
  
  get: async (id: number): Promise<Task> => {
    return apiClient.get(`/tasks/${id}`);
  },
  
  create: async (data: CreateTaskRequest): Promise<Task> => {
    return apiClient.post('/tasks', data);
  },
  
  claim: async (id: number, workerId: string): Promise<Task> => {
    return apiClient.post(`/tasks/${id}/claim`, { worker_id: workerId });
  },
  
  updateProgress: async (id: number, progress: number, workerId: string): Promise<Task> => {
    return apiClient.post(`/tasks/${id}/progress`, { 
      worker_id: workerId,
      progress 
    });
  },
  
  complete: async (id: number, result: any, workerId: string): Promise<Task> => {
    return apiClient.post(`/tasks/${id}/complete`, {
      worker_id: workerId,
      result
    });
  },
  
  fail: async (id: number, error: string, workerId: string): Promise<Task> => {
    return apiClient.post(`/tasks/${id}/fail`, {
      worker_id: workerId,
      error_message: error
    });
  }
};
```

## Pinia Store Implementation

### Task Store
```typescript
// stores/tasks.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { taskService } from '@/services/tasks';
import type { Task } from '@/types';

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  const pendingTasks = computed(() => 
    tasks.value.filter(t => t.status === 'pending')
  );
  
  const claimedTasks = computed(() => 
    tasks.value.filter(t => t.status === 'claimed')
  );
  
  async function fetchTasks() {
    loading.value = true;
    error.value = null;
    try {
      tasks.value = await taskService.list();
    } catch (e) {
      error.value = 'Failed to fetch tasks';
      throw e;
    } finally {
      loading.value = false;
    }
  }
  
  async function createTask(data: CreateTaskRequest) {
    const task = await taskService.create(data);
    tasks.value.push(task);
    return task;
  }
  
  async function claimTask(id: number, workerId: string) {
    const task = await taskService.claim(id, workerId);
    updateTask(task);
    return task;
  }
  
  function updateTask(updatedTask: Task) {
    const index = tasks.value.findIndex(t => t.id === updatedTask.id);
    if (index !== -1) {
      tasks.value[index] = updatedTask;
    }
  }
  
  return {
    tasks,
    loading,
    error,
    pendingTasks,
    claimedTasks,
    fetchTasks,
    createTask,
    claimTask,
    updateTask
  };
});
```

## Real-time Updates

### Polling Strategy
```typescript
// composables/usePolling.ts
import { ref, onMounted, onUnmounted } from 'vue';
import { useTaskStore } from '@/stores/tasks';

export function useTaskPolling(intervalMs = 5000) {
  const taskStore = useTaskStore();
  let intervalId: number | null = null;
  
  function startPolling() {
    intervalId = setInterval(() => {
      taskStore.fetchTasks();
    }, intervalMs);
  }
  
  function stopPolling() {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
  }
  
  onMounted(() => {
    startPolling();
  });
  
  onUnmounted(() => {
    stopPolling();
  });
  
  return {
    startPolling,
    stopPolling
  };
}
```

## Error Handling

### Error Types
```typescript
// types/errors.ts
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}
```

### Error Interceptor
```typescript
// Handle errors in response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      // Server responded with error
      throw new APIError(
        error.response.data.message || 'API Error',
        error.response.status,
        error.response.data
      );
    } else if (error.request) {
      // Network error
      throw new NetworkError('Network error - please check your connection');
    } else {
      throw new Error(error.message);
    }
  }
);
```

## Testing

### Integration Tests
```typescript
// tests/integration/api.spec.ts
import { describe, it, expect, beforeAll } from 'vitest';
import { taskService } from '@/services/tasks';

describe('Task API Integration', () => {
  it('should list tasks', async () => {
    const tasks = await taskService.list();
    expect(Array.isArray(tasks)).toBe(true);
  });
  
  it('should create task', async () => {
    const task = await taskService.create({
      task_type: 'test',
      params: { test: true }
    });
    expect(task.id).toBeDefined();
    expect(task.status).toBe('pending');
  });
  
  // More tests...
});
```

## Timeline
- **Start**: After ISSUE-FRONTEND-001 (can work in parallel with Worker11)
- **Duration**: 1 week
- **Target**: Week 2

## Success Criteria
- ✅ API client configured and tested
- ✅ All TypeScript types from OpenAPI
- ✅ Pinia stores implemented
- ✅ All CRUD operations working
- ✅ Real-time updates functional
- ✅ Error handling comprehensive
- ✅ Integration tests > 80% coverage
- ✅ Documentation complete

---

**Created By**: Worker01 (Project Manager)  
**Date**: 2025-11-09  
**Assigned To**: Worker02 (API Integration Expert)  
**Status**: 🔴 NOT STARTED  
**Priority**: High (can run parallel to UX design)
