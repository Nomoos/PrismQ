# PrismQ Client - On-Demand Architecture

## Overview

The PrismQ Client follows an **on-demand architecture** where all background operations are initiated by explicit requests from the UI to the API. This design ensures clear separation of concerns and predictable behavior.

## Architecture Principle

**Core Principle**: All communication is managed on request made by UI → API (on demand)

### What This Means

1. **No Autonomous Background Tasks**: The backend does not run periodic tasks automatically
2. **UI-Driven Operations**: All operations are triggered by user actions in the frontend
3. **Clear Request-Response Flow**: Every background operation has a clear initiator (the UI)

## Communication Flow

```
┌─────────────┐
│     UI      │  User initiates action
│  (Frontend) │  (button click, page load, etc.)
└──────┬──────┘
       │
       ▼ HTTP Request
┌─────────────┐
│     API     │  Processes request
│  (Backend)  │  Performs operation
└──────┬──────┘
       │
       ▼ Response
┌─────────────┐
│     UI      │  Displays result
│  (Frontend) │
└─────────────┘
```

## Components

### 1. UI Layer (Frontend)
- **Responsibility**: User interface and interaction
- **Role**: Initiates all operations via API calls
- **Technology**: Vue 3, TypeScript, Vite

### 2. API Layer (Backend)
- **Responsibility**: Request handling and business logic
- **Role**: Receives requests, executes operations, returns responses
- **Technology**: FastAPI, Python

### 3. Background Communications
- **Responsibility**: Execute operations requested via API
- **Role**: Module execution, maintenance operations
- **Trigger**: Only when explicitly requested through API endpoints

## Changes from Previous Architecture

### Before (Autonomous Background Tasks)
```
Backend Server ──[Automatic]──> Periodic Tasks
                                (cleanup every 1 hour)
                                (health check every 5 min)
                                (statistics every 15 min)
```

**Issue**: Tasks run independently without user interaction, violating the on-demand principle.

### After (On-Demand Operations)
```
UI ──[User Action]──> API Endpoint ──> Background Operation
```

**Benefit**: All operations are traceable to user actions, providing clear control and accountability.

## On-Demand Maintenance Endpoints

The following maintenance operations are now available as API endpoints:

### 1. Cleanup Old Runs
**Endpoint**: `POST /api/system/maintenance/cleanup-runs`

**Purpose**: Remove old completed/failed runs to prevent registry from growing indefinitely

**Parameters**:
- `max_age_hours` (default: 24) - Maximum age of runs to keep

**Example Usage**:
```typescript
// Frontend code
const response = await axios.post('/api/system/maintenance/cleanup-runs', {
  max_age_hours: 24
});
```

### 2. System Health Check
**Endpoint**: `POST /api/system/maintenance/health-check`

**Purpose**: Perform comprehensive system health check

**Returns**: 
- Memory usage
- CPU usage
- Disk usage
- Active task count
- Overall health status

**Example Usage**:
```typescript
// Frontend code
const response = await axios.post('/api/system/maintenance/health-check');
const health = response.data;
```

### 3. Cleanup Temporary Files
**Endpoint**: `POST /api/system/maintenance/cleanup-temp-files`

**Purpose**: Remove old temporary files

**Parameters**:
- `max_age_hours` (default: 24) - Maximum age of files to keep

**Example Usage**:
```typescript
// Frontend code
const response = await axios.post('/api/system/maintenance/cleanup-temp-files', {
  max_age_hours: 24
});
```

### 4. Log Statistics
**Endpoint**: `POST /api/system/maintenance/log-statistics`

**Purpose**: Collect and log system statistics for monitoring

**Returns**:
- Asyncio task statistics
- System resource statistics

**Example Usage**:
```typescript
// Frontend code
const response = await axios.post('/api/system/maintenance/log-statistics');
const stats = response.data;
```

## Module Execution Flow

Module execution follows the same on-demand pattern:

```
1. User clicks "Run Module" in UI
   ↓
2. UI sends POST request to /api/modules/{id}/run
   ↓
3. Backend creates run and starts module execution
   ↓
4. Backend returns run details immediately
   ↓
5. UI polls for updates or subscribes to SSE for logs
```

## Benefits of On-Demand Architecture

### 1. **Predictability**
- Users know exactly when operations are performed
- No surprise resource usage from background tasks

### 2. **Control**
- Users decide when maintenance operations should run
- Maintenance can be scheduled during low-activity periods

### 3. **Debugging**
- Clear audit trail of who triggered what operation
- Easier to diagnose issues with specific requests

### 4. **Resource Efficiency**
- Resources are used only when needed
- No wasted cycles on unnecessary periodic checks

### 5. **Separation of Concerns**
- UI manages user interaction
- API manages request processing
- Background communications only occur on request

## Implementation Details

### Disabled Components

The following components are **disabled** in the on-demand architecture:

1. **PeriodicTaskManager**: No longer instantiated or used
2. **Automatic Task Registration**: Maintenance tasks are not registered at startup
3. **Automatic Task Execution**: Tasks only run when explicitly called via API

### Modified Components

1. **main.py**: Removed periodic task initialization
2. **system.py**: Added on-demand maintenance endpoints

### Preserved Components

All core functionality remains intact:
- Module discovery and listing
- Module execution
- Run tracking and monitoring
- Configuration management
- Log streaming (SSE)

## Migration Guide

### For Frontend Developers

**Add Maintenance Buttons** (Optional):
If you want to provide UI controls for maintenance operations:

```vue
<template>
  <button @click="cleanupOldRuns">Clean Old Runs</button>
  <button @click="checkSystemHealth">Check Health</button>
</template>

<script setup lang="ts">
import axios from 'axios';

const cleanupOldRuns = async () => {
  const response = await axios.post('/api/system/maintenance/cleanup-runs');
  console.log('Cleaned up:', response.data.runs_cleaned);
};

const checkSystemHealth = async () => {
  const response = await axios.post('/api/system/maintenance/health-check');
  console.log('Health status:', response.data.status);
};
</script>
```

### For Backend Developers

**No Changes Required**: The maintenance functions are still available, just not called automatically.

If you need to add new maintenance operations:

1. Add the function to `core/maintenance.py`
2. Add an endpoint to `api/system.py`
3. Document the endpoint in this file

## Testing

The on-demand architecture is tested through:

1. **Integration Tests**: Verify API endpoints work correctly
2. **Unit Tests**: Verify maintenance functions work independently
3. **Manual Testing**: UI interactions trigger expected operations

## Future Enhancements

Potential future enhancements while maintaining on-demand architecture:

1. **Scheduled Maintenance**: UI allows users to schedule maintenance operations
2. **Maintenance Dashboard**: UI panel showing last maintenance execution times
3. **Auto-Trigger on Conditions**: UI can configure conditions that trigger maintenance (e.g., "cleanup when runs > 1000")

All enhancements should maintain the principle that operations are ultimately triggered by user configuration/action.

## Summary

The PrismQ Client now strictly follows an on-demand architecture where:

- ✅ UI initiates all operations
- ✅ API processes requests and executes operations
- ✅ Background communications only occur when requested
- ✅ No autonomous periodic tasks
- ✅ Clear separation of concerns
- ✅ Predictable and controllable behavior

This architecture ensures the Client project manages exactly what it should: **UI, API, and background communications triggered on demand**.

---

**Last Updated**: 2025-11-06
**Version**: 1.0.0
