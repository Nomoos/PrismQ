# Issue #109: Error Handling and User Notifications

**Type**: Feature  
**Priority**: High  
**Status**: WIP  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1 week  
**Dependencies**: All core features (#103-#108)  
**Can be parallelized with**: #111 (Testing)

---

## Description

Implement comprehensive error handling across the entire application (backend and frontend) with clear user notifications. Handle edge cases, validate inputs, and provide helpful error messages.

## Backend Error Handling

### 1. Custom Exceptions

```python
# src/core/exceptions.py

class WebClientException(Exception):
    """Base exception for web client errors."""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ModuleNotFoundException(WebClientException):
    """Module not found in registry."""
    pass

class ModuleExecutionException(WebClientException):
    """Error executing module."""
    pass

class ResourceLimitException(WebClientException):
    """System resource limit exceeded."""
    pass

class ValidationException(WebClientException):
    """Parameter validation failed."""
    pass

class RunNotFoundException(WebClientException):
    """Run not found in registry."""
    pass
```

### 2. Global Exception Handler

```python
# src/main.py

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from .core.exceptions import WebClientException
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

@app.exception_handler(WebClientException)
async def web_client_exception_handler(request: Request, exc: WebClientException):
    logger.error(f"WebClient error: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### 3. Input Validation

```python
# Enhanced parameter validation
from pydantic import BaseModel, validator, Field

class RunCreate(BaseModel):
    parameters: dict
    save_config: bool = True
    
    @validator('parameters')
    def validate_parameters(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Parameters must be a dictionary")
        if len(v) > 100:
            raise ValueError("Too many parameters (max 100)")
        return v

class ConfigUpdate(BaseModel):
    parameters: dict = Field(..., max_length=100)
    
    @validator('parameters')
    def validate_no_sensitive_keys(cls, v):
        # Prevent overwriting sensitive config
        forbidden = ['__internal__', '__system__']
        for key in v.keys():
            if key in forbidden:
                raise ValueError(f"Cannot set forbidden parameter: {key}")
        return v
```

### 4. Module Execution Error Handling

```python
# src/core/module_runner.py

async def _execute_async(self, run: Run, script_path: Path, parameters: Dict):
    try:
        # Validate script exists
        if not script_path.exists():
            raise ModuleExecutionException(
                f"Module script not found: {script_path}",
                error_code="SCRIPT_NOT_FOUND"
            )
        
        # ... execution code ...
        
    except FileNotFoundError as e:
        run.status = RunStatus.FAILED
        run.error_message = f"File not found: {e.filename}"
        logger.error(f"File not found in run {run.run_id}: {e}")
        
    except PermissionError as e:
        run.status = RunStatus.FAILED
        run.error_message = "Permission denied executing module"
        logger.error(f"Permission error in run {run.run_id}: {e}")
        
    except asyncio.TimeoutError:
        run.status = RunStatus.FAILED
        run.error_message = "Module execution timed out"
        logger.error(f"Timeout in run {run.run_id}")
        
    except Exception as e:
        run.status = RunStatus.FAILED
        run.error_message = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error in run {run.run_id}", exc_info=True)
        
    finally:
        self.registry.update_run(run)
```

## Frontend Error Handling

### 1. API Error Interceptor

```typescript
// src/services/api.ts

import axios, { AxiosError } from 'axios'
import { useNotificationStore } from '@/stores/notifications'

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  (error: AxiosError) => {
    const notifications = useNotificationStore()
    
    if (error.response) {
      // Server responded with error
      const data = error.response.data as any
      const message = data.detail || 'An error occurred'
      
      notifications.error({
        title: `Error ${error.response.status}`,
        message,
        errorCode: data.error_code
      })
    } else if (error.request) {
      // Request made but no response
      notifications.error({
        title: 'Connection Error',
        message: 'Cannot connect to server. Is it running?'
      })
    } else {
      // Something else happened
      notifications.error({
        title: 'Error',
        message: error.message
      })
    }
    
    return Promise.reject(error)
  }
)

export default api
```

### 2. Notification Store (Pinia)

```typescript
// src/stores/notifications.ts

import { defineStore } from 'pinia'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  errorCode?: string
  duration?: number
}

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [] as Notification[]
  }),
  
  actions: {
    add(notification: Omit<Notification, 'id'>) {
      const id = Date.now().toString()
      const duration = notification.duration || 5000
      
      this.notifications.push({ ...notification, id })
      
      // Auto-remove after duration
      if (duration > 0) {
        setTimeout(() => this.remove(id), duration)
      }
    },
    
    success(options: Omit<Notification, 'id' | 'type'>) {
      this.add({ ...options, type: 'success' })
    },
    
    error(options: Omit<Notification, 'id' | 'type'>) {
      this.add({ ...options, type: 'error', duration: 10000 })
    },
    
    warning(options: Omit<Notification, 'id' | 'type'>) {
      this.add({ ...options, type: 'warning' })
    },
    
    info(options: Omit<Notification, 'id' | 'type'>) {
      this.add({ ...options, type: 'info' })
    },
    
    remove(id: string) {
      const index = this.notifications.findIndex(n => n.id === id)
      if (index !== -1) {
        this.notifications.splice(index, 1)
      }
    }
  }
})
```

### 3. Notification Component

```vue
<!-- src/components/NotificationToast.vue -->

<template>
  <teleport to="body">
    <div class="notification-container">
      <transition-group name="slide-fade">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="['notification', `notification-${notification.type}`]"
        >
          <div class="notification-icon">
            {{ getIcon(notification.type) }}
          </div>
          
          <div class="notification-content">
            <h4>{{ notification.title }}</h4>
            <p>{{ notification.message }}</p>
            <small v-if="notification.errorCode">
              Code: {{ notification.errorCode }}
            </small>
          </div>
          
          <button 
            @click="store.remove(notification.id)"
            class="notification-close"
          >
            ×
          </button>
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useNotificationStore } from '@/stores/notifications'

const store = useNotificationStore()
const { notifications } = storeToRefs(store)

function getIcon(type: string): string {
  const icons = {
    success: '✓',
    error: '✗',
    warning: '⚠',
    info: 'ℹ'
  }
  return icons[type] || '•'
}
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 400px;
}

.notification {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background: white;
}

.notification-success {
  border-left: 4px solid #10b981;
}

.notification-error {
  border-left: 4px solid #ef4444;
}

.notification-warning {
  border-left: 4px solid #f59e0b;
}

.notification-info {
  border-left: 4px solid #3b82f6;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
```

### 4. Form Validation

```vue
<!-- In ModuleLaunchModal.vue -->

<script setup lang="ts">
const errors = ref<Record<string, string>>({})

function validateForm(): boolean {
  errors.value = {}
  
  for (const param of props.module.parameters) {
    const value = formData.value[param.name]
    
    // Required check
    if (param.required && (value === undefined || value === '')) {
      errors.value[param.name] = `${param.name} is required`
    }
    
    // Type checks
    if (param.type === 'number' && value !== undefined) {
      const num = Number(value)
      if (isNaN(num)) {
        errors.value[param.name] = 'Must be a number'
      } else if (param.min !== undefined && num < param.min) {
        errors.value[param.name] = `Must be >= ${param.min}`
      } else if (param.max !== undefined && num > param.max) {
        errors.value[param.name] = `Must be <= ${param.max}`
      }
    }
  }
  
  return Object.keys(errors.value).length === 0
}

async function handleSubmit() {
  if (!validateForm()) {
    return
  }
  
  // ... submit logic ...
}
</script>

<template>
  <div v-if="errors[param.name]" class="error-message">
    {{ errors[param.name] }}
  </div>
</template>
```

---

## Error Scenarios to Handle

### Backend
- [x] Module not found
- [x] Invalid parameters
- [x] Resource limits exceeded
- [x] Script execution failure
- [x] File permission errors
- [x] Process timeout
- [x] Disk space full
- [x] Configuration file corruption
- [x] Port already in use

### Frontend
- [x] API connection failure
- [x] Network timeout
- [x] Invalid form input
- [x] SSE connection lost
- [x] Module launch failure
- [x] Run not found
- [x] Unauthorized access (future)

---

## Tasks

### Backend
- [x] Create custom exception classes
- [x] Implement global exception handler
- [x] Add validation to all endpoints
- [x] Enhance error logging
- [x] Add error recovery mechanisms

### Frontend
- [x] Create notification store
- [x] Implement NotificationToast component
- [x] Add API error interceptor
- [x] Implement form validation
- [ ] Add error boundaries (Vue error handlers - future enhancement)
- [ ] Handle SSE disconnections gracefully (future enhancement)

### Testing
- [x] Test all error scenarios
- [x] Validate error messages
- [x] Test error recovery
- [x] Test user notifications

---

## Acceptance Criteria

- [x] All backend errors handled gracefully
- [x] User-friendly error messages displayed
- [x] Validation prevents invalid inputs
- [x] Notifications auto-dismiss after timeout
- [x] Critical errors logged for debugging
- [x] No unhandled promise rejections
- [x] Error codes help identify issues
- [x] UI remains responsive during errors

## Related Issues

- **Depends on**: All core features
- **Parallel**: #111 (Testing)

## References

- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Pinia Stores](https://pinia.vuejs.org/)
