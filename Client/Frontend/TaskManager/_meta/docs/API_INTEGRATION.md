# Frontend/TaskManager - API Integration Guide

**Version**: 1.0  
**Last Updated**: 2025-11-09  
**Audience**: Developers

---

## Table of Contents

1. [Overview](#overview)
2. [API Client Setup](#api-client-setup)
3. [Endpoint Reference](#endpoint-reference)
4. [Request/Response Examples](#requestresponse-examples)
5. [Error Handling](#error-handling)
6. [Authentication](#authentication)
7. [TypeScript Types](#typescript-types)
8. [Best Practices](#best-practices)

---

## Overview

Frontend/TaskManager integrates with the Backend/TaskManager REST API to manage tasks, task types, and workers. All communication uses JSON over HTTPS.

### Base Configuration

```typescript
// Environment variables (.env)
VITE_API_BASE_URL=https://api.prismq.nomoos.cz/api
VITE_API_KEY=your-api-key-here
```

### API Client

The application uses Axios for HTTP requests with interceptors for authentication and error handling.

---

## API Client Setup

### Core Configuration

```typescript
// src/services/api.ts
import axios, { AxiosInstance } from 'axios'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000 // 10 seconds
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add API key if available
    const apiKey = import.meta.env.VITE_API_KEY
    if (apiKey) {
      config.headers.Authorization = `Bearer ${apiKey}`
    }
    
    // Log request in debug mode
    if (import.meta.env.VITE_DEBUG_MODE === 'true') {
      console.log('[API Request]', config.method?.toUpperCase(), config.url)
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Log response in debug mode
    if (import.meta.env.VITE_DEBUG_MODE === 'true') {
      console.log('[API Response]', response.status, response.config.url)
    }
    return response
  },
  (error) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with error status
      console.error('[API Error]', error.response.status, error.response.data)
    } else if (error.request) {
      // Request made but no response received
      console.error('[Network Error]', 'No response received')
    } else {
      // Error in request setup
      console.error('[Request Error]', error.message)
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

---

## Endpoint Reference

### Health Check

#### GET /health

Check API health and availability.

**Request**: None

**Response**:
```json
{
  "status": "ok",
  "timestamp": "2025-11-09T12:00:00Z"
}
```

**Usage**:
```typescript
const response = await apiClient.get('/health')
console.log(response.data.status) // "ok"
```

---

### Task Types

#### POST /task-types/register

Register a new task type with parameter schema.

**Request**:
```json
{
  "name": "PrismQ.IdeaInspiration.Generate",
  "version": "1.0.0",
  "param_schema": {
    "type": "object",
    "properties": {
      "topic": { "type": "string" },
      "count": { "type": "integer", "minimum": 1, "maximum": 10 }
    },
    "required": ["topic"]
  }
}
```

**Response**:
```json
{
  "task_type": {
    "id": 1,
    "name": "PrismQ.IdeaInspiration.Generate",
    "version": "1.0.0",
    "param_schema": { ... },
    "is_active": true,
    "created_at": "2025-11-09T12:00:00Z"
  }
}
```

#### GET /task-types/{name}

Get a specific task type by name.

**Request**: None

**Response**:
```json
{
  "task_type": {
    "id": 1,
    "name": "PrismQ.IdeaInspiration.Generate",
    "version": "1.0.0",
    "param_schema": { ... },
    "is_active": true
  }
}
```

#### GET /task-types

List all task types.

**Request**: None

**Response**:
```json
{
  "task_types": [
    {
      "id": 1,
      "name": "PrismQ.IdeaInspiration.Generate",
      "version": "1.0.0",
      "is_active": true
    },
    ...
  ]
}
```

---

### Tasks

#### POST /tasks

Create a new task.

**Request**:
```json
{
  "task_type_id": 1,
  "params": {
    "topic": "AI and creativity",
    "count": 5
  },
  "priority": 5
}
```

**Response**:
```json
{
  "task": {
    "id": 42,
    "task_type_id": 1,
    "task_type": "PrismQ.IdeaInspiration.Generate",
    "status": "pending",
    "params": { ... },
    "priority": 5,
    "attempts": 0,
    "created_at": "2025-11-09T12:00:00Z"
  }
}
```

#### GET /tasks

List all tasks with optional filtering.

**Query Parameters**:
- `status` (optional): Filter by status (pending, claimed, completed, failed)
- `task_type_id` (optional): Filter by task type ID
- `limit` (optional): Maximum number of tasks to return
- `offset` (optional): Offset for pagination

**Request**:
```
GET /tasks?status=pending&limit=10
```

**Response**:
```json
{
  "tasks": [
    {
      "id": 42,
      "task_type": "PrismQ.IdeaInspiration.Generate",
      "status": "pending",
      "priority": 5,
      "attempts": 0,
      "progress": 0,
      "created_at": "2025-11-09T12:00:00Z"
    },
    ...
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

#### GET /tasks/{id}

Get a specific task by ID.

**Request**: None

**Response**:
```json
{
  "task": {
    "id": 42,
    "task_type_id": 1,
    "task_type": "PrismQ.IdeaInspiration.Generate",
    "status": "pending",
    "params": {
      "topic": "AI and creativity",
      "count": 5
    },
    "result": null,
    "error_message": null,
    "priority": 5,
    "attempts": 0,
    "progress": 0,
    "claimed_by": null,
    "claimed_at": null,
    "completed_at": null,
    "created_at": "2025-11-09T12:00:00Z",
    "updated_at": "2025-11-09T12:00:00Z"
  }
}
```

#### POST /tasks/claim

Claim a task for processing.

**Request**:
```json
{
  "task_type_id": 1,
  "worker_id": "worker-123-abc"
}
```

**Response**:
```json
{
  "task": {
    "id": 42,
    "status": "claimed",
    "claimed_by": "worker-123-abc",
    "claimed_at": "2025-11-09T12:05:00Z",
    ...
  }
}
```

**Error Response** (no tasks available):
```json
{
  "error": "No pending tasks available for this type"
}
```

#### POST /tasks/{id}/complete

Complete a task with result or error.

**Request** (Success):
```json
{
  "status": "completed",
  "result": {
    "ideas": [
      "Idea 1",
      "Idea 2",
      "Idea 3"
    ],
    "count": 3
  }
}
```

**Request** (Failed):
```json
{
  "status": "failed",
  "error_message": "API rate limit exceeded"
}
```

**Response**:
```json
{
  "task": {
    "id": 42,
    "status": "completed",
    "result": { ... },
    "completed_at": "2025-11-09T12:10:00Z",
    ...
  }
}
```

#### POST /tasks/{id}/progress

Update task progress (0-100).

**Request**:
```json
{
  "progress": 50
}
```

**Response**:
```json
{
  "task": {
    "id": 42,
    "progress": 50,
    "updated_at": "2025-11-09T12:07:00Z",
    ...
  }
}
```

---

## Request/Response Examples

### Complete Task Flow Example

```typescript
// src/services/taskService.ts
import apiClient from './api'
import type { Task, CreateTaskRequest } from '@/types/task'

export const taskService = {
  // 1. Create a task
  async create(data: CreateTaskRequest) {
    return apiClient.post<{ task: Task }>('/tasks', data)
  },
  
  // 2. Claim the task
  async claim(taskTypeId: number, workerId: string) {
    return apiClient.post<{ task: Task }>('/tasks/claim', {
      task_type_id: taskTypeId,
      worker_id: workerId
    })
  },
  
  // 3. Update progress
  async updateProgress(taskId: number, progress: number) {
    return apiClient.post<{ task: Task }>(`/tasks/${taskId}/progress`, {
      progress
    })
  },
  
  // 4. Complete the task
  async complete(taskId: number, result: object) {
    return apiClient.post<{ task: Task }>(`/tasks/${taskId}/complete`, {
      status: 'completed',
      result
    })
  },
  
  // 5. Or mark as failed
  async fail(taskId: number, errorMessage: string) {
    return apiClient.post<{ task: Task }>(`/tasks/${taskId}/complete`, {
      status: 'failed',
      error_message: errorMessage
    })
  }
}
```

### Using in Component

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { taskService } from '@/services/taskService'

const workerId = 'worker-123-abc'
const processing = ref(false)

async function processTask() {
  processing.value = true
  
  try {
    // 1. Claim task
    const claimResponse = await taskService.claim(1, workerId)
    const task = claimResponse.data.task
    console.log('Claimed task:', task.id)
    
    // 2. Simulate processing with progress updates
    for (let i = 0; i <= 100; i += 20) {
      await taskService.updateProgress(task.id, i)
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    
    // 3. Complete task
    const result = {
      status: 'success',
      output: 'Task completed successfully'
    }
    await taskService.complete(task.id, result)
    console.log('Task completed')
    
  } catch (error) {
    console.error('Error processing task:', error)
    // Optionally mark as failed
    // await taskService.fail(taskId, error.message)
  } finally {
    processing.value = false
  }
}
</script>
```

---

## Error Handling

### Error Types

1. **Network Errors**: No response from server
2. **Server Errors**: 5xx status codes
3. **Client Errors**: 4xx status codes
4. **Validation Errors**: Invalid request data

### Error Response Format

```json
{
  "error": "Error message",
  "details": {
    "field": "validation error details"
  },
  "code": "ERROR_CODE"
}
```

### Handling Errors

```typescript
import axios from 'axios'

try {
  const response = await taskService.claim(1, workerId)
} catch (error) {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const message = error.response.data.error || 'Unknown error'
      
      switch (status) {
        case 400:
          console.error('Bad Request:', message)
          break
        case 401:
          console.error('Unauthorized:', message)
          // Redirect to login or refresh token
          break
        case 404:
          console.error('Not Found:', message)
          break
        case 409:
          console.error('Conflict:', message)
          // Task already claimed
          break
        case 500:
          console.error('Server Error:', message)
          break
        default:
          console.error('Error:', status, message)
      }
    } else if (error.request) {
      // Request made but no response
      console.error('Network error: No response from server')
      // Show offline message to user
    } else {
      // Error in request setup
      console.error('Request error:', error.message)
    }
  } else {
    // Non-Axios error
    console.error('Unexpected error:', error)
  }
}
```

### Global Error Handler

```typescript
// In Pinia store
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useErrorStore = defineStore('errors', () => {
  const lastError = ref<string | null>(null)
  
  function handleError(error: unknown) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.error || error.message
      lastError.value = message
      
      // Show toast notification
      showToast(message, 'error')
    }
  }
  
  return { lastError, handleError }
})
```

---

## Authentication

### API Key Authentication

The API uses Bearer token authentication:

```typescript
// Automatically added by request interceptor
headers: {
  'Authorization': `Bearer ${apiKey}`
}
```

### Configuration

Set API key in environment:

```env
VITE_API_KEY=your-api-key-here
```

Or use runtime configuration:

```typescript
// src/services/api.ts
function getApiKey(): string | null {
  // Try runtime config first
  if (window.APP_CONFIG?.API_KEY) {
    return window.APP_CONFIG.API_KEY
  }
  // Fall back to environment variable
  return import.meta.env.VITE_API_KEY || null
}
```

### Refreshing Tokens (if applicable)

```typescript
apiClient.interceptors.response.use(
  response => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired - refresh it
      try {
        const newToken = await refreshToken()
        // Retry original request with new token
        error.config.headers.Authorization = `Bearer ${newToken}`
        return apiClient.request(error.config)
      } catch (refreshError) {
        // Redirect to login
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)
```

---

## TypeScript Types

### Task Types

```typescript
// src/types/task.ts

export interface Task {
  id: number
  task_type_id: number
  task_type: string
  status: TaskStatus
  params: Record<string, any>
  result: Record<string, any> | null
  error_message: string | null
  priority: number
  attempts: number
  progress: number
  claimed_by: string | null
  claimed_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export type TaskStatus = 'pending' | 'claimed' | 'completed' | 'failed'

export interface CreateTaskRequest {
  task_type_id: number
  params: Record<string, any>
  priority?: number
}

export interface ClaimTaskRequest {
  task_type_id: number
  worker_id: string
}

export interface CompleteTaskRequest {
  status: 'completed' | 'failed'
  result?: Record<string, any>
  error_message?: string
}

export interface UpdateProgressRequest {
  progress: number
}
```

### API Response Types

```typescript
// src/types/api.ts

export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface ApiError {
  error: string
  details?: Record<string, string>
  code?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  limit: number
  offset: number
}
```

---

## Best Practices

### 1. Use TypeScript Types

Always type your API responses:

```typescript
const response = await apiClient.get<{ tasks: Task[] }>('/tasks')
const tasks: Task[] = response.data.tasks
```

### 2. Handle Errors Properly

Don't swallow errors:

```typescript
// ❌ Bad
async function fetchTasks() {
  try {
    const response = await taskService.list()
    return response.data.tasks
  } catch (error) {
    // Silent failure
  }
}

// ✅ Good
async function fetchTasks() {
  try {
    const response = await taskService.list()
    return response.data.tasks
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
    throw error // Re-throw for caller to handle
  }
}
```

### 3. Use Loading States

Show loading indicators:

```typescript
const loading = ref(false)

async function loadTasks() {
  loading.value = true
  try {
    const response = await taskService.list()
    tasks.value = response.data.tasks
  } finally {
    loading.value = false
  }
}
```

### 4. Cache Responses

Avoid unnecessary API calls:

```typescript
const cache = new Map<string, { data: any, timestamp: number }>()
const CACHE_TTL = 60000 // 1 minute

async function getCached<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const cached = cache.get(key)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data as T
  }
  
  const data = await fetcher()
  cache.set(key, { data, timestamp: Date.now() })
  return data
}
```

### 5. Use Optimistic Updates

Update UI immediately, rollback on error:

```typescript
async function completeTask(taskId: number, result: object) {
  // Optimistic update
  const task = tasks.value.find(t => t.id === taskId)
  if (task) {
    const originalStatus = task.status
    task.status = 'completed'
    
    try {
      await taskService.complete(taskId, result)
    } catch (error) {
      // Rollback on error
      task.status = originalStatus
      throw error
    }
  }
}
```

### 6. Debounce Requests

For search or frequent updates:

```typescript
import { debounce } from 'lodash-es'

const searchTasks = debounce(async (query: string) => {
  const response = await taskService.search(query)
  searchResults.value = response.data.tasks
}, 300)
```

### 7. Cancel Requests

Cancel pending requests when component unmounts:

```typescript
import { onUnmounted } from 'vue'

const abortController = new AbortController()

async function fetchTasks() {
  const response = await apiClient.get('/tasks', {
    signal: abortController.signal
  })
  return response.data.tasks
}

onUnmounted(() => {
  abortController.abort()
})
```

---

**Document Owner**: Worker06 (Documentation Specialist)  
**Last Updated**: 2025-11-09  
**Version**: 1.0  
**Status**: ✅ Complete
