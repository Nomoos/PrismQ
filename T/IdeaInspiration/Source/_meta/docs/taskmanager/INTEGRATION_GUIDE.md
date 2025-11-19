# TaskManager API - Worker Integration Guide

**Version**: 1.0  
**Status**: Planning  
**Created**: 2025-11-12  
**Last Updated**: 2025-11-12

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Integration Patterns](#integration-patterns)
- [Step-by-Step Integration](#step-by-step-integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide explains how to integrate PrismQ.IdeaInspiration workers with the external TaskManager API to enable centralized task coordination, monitoring, and distributed work management.

### What is TaskManager API?

**TaskManager API** is an external RESTful service that provides:
- Centralized task queue management
- Task type registration with JSON Schema validation
- Task deduplication (prevents duplicate work)
- Worker coordination and load balancing
- Task claiming and completion tracking
- Audit logging and monitoring

**External API Details:**
- **API Root**: https://api.prismq.nomoos.cz/api/
- **Swagger UI**: https://api.prismq.nomoos.cz/public/swagger-ui
- **OpenAPI Spec**: https://api.prismq.nomoos.cz/api/openapi.json

### Why Integrate?

**Benefits of Integration:**
1. ✅ **Centralized coordination** - All workers share same task queue
2. ✅ **Deduplication** - Prevents multiple workers from processing same content
3. ✅ **Load balancing** - Tasks distributed across available workers
4. ✅ **Monitoring** - Unified dashboard for all worker activity
5. ✅ **Priority management** - High-priority tasks processed first
6. ✅ **Retry logic** - Failed tasks automatically retried
7. ✅ **Cross-module tasks** - YouTube worker can create tasks for Reddit worker

**Without Integration:**
- ❌ Each worker operates independently
- ❌ No coordination between workers
- ❌ Duplicate work possible
- ❌ No unified monitoring
- ❌ Manual prioritization required

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                PrismQ.IdeaInspiration Workers                    │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   YouTube    │  │   Reddit     │  │    Other     │          │
│  │   Workers    │  │   Workers    │  │   Workers    │          │
│  │              │  │              │  │              │          │
│  │ - Channel    │  │ - Posts      │  │ - TikTok     │          │
│  │ - Video      │  │ - Comments   │  │ - Trends     │          │
│  │ - Search     │  │              │  │ - ...        │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
│                            │                                     │
│                            ▼                                     │
│                 ┌────────────────────────┐                       │
│                 │  TaskManager Client    │  ← Python Library    │
│                 │     (Python 3.10+)     │                       │
│                 │                        │                       │
│                 │ - register_task_type() │                       │
│                 │ - create_task()        │                       │
│                 │ - claim_task()         │                       │
│                 │ - complete_task()      │                       │
│                 └────────┬───────────────┘                       │
└──────────────────────────┼────────────────────────────────────────┘
                           │ HTTPS/REST
                           ▼
              ┌────────────────────────────┐
              │  External TaskManager API  │  ← Existing Service
              │  (https://api.prismq.      │
              │   nomoos.cz/api/)          │
              │                            │
              │ - Task Types Registry      │
              │ - Task Queue               │
              │ - Deduplication Logic      │
              │ - Worker Tracking          │
              │ - Audit Logs               │
              └────────────────────────────┘
```

### Data Flow

```
1. Worker Initialization
   Worker → TaskManagerClient.register_task_type()
   → External API: POST /api/task-types
   → Returns: task_type_id

2. Task Creation (Discovery Phase)
   Worker discovers content (YouTube video, Reddit post, etc.)
   → TaskManagerClient.create_task(params)
   → External API: POST /api/tasks
   → Deduplication check (dedupe_key)
   → Returns: task_id (or existing_task_id if duplicate)

3. Task Claiming (Processing Phase)
   Worker → TaskManagerClient.claim_task()
   → External API: POST /api/tasks/claim
   → Returns: task with status="claimed"
   
4. Task Processing
   Worker processes claimed task
   → Scrapes content, runs classification, etc.
   → Saves results to Model/IdeaInspiration database
   
5. Task Completion
   Worker → TaskManagerClient.complete_task(result)
   → External API: POST /api/tasks/{id}/complete
   → Task marked as "completed"
```

---

## Integration Patterns

### Pattern 1: Direct Integration (Recommended)

**Best for**: New workers, simple workflows

See full code example in issue document #008.

### Pattern 2: Hybrid Integration (Local + Remote)

**Best for**: Existing workers with local SQLite queues

Workers can maintain local queues for reliability while syncing with TaskManager.

### Pattern 3: Discovery-Only Integration

**Best for**: Workers that discover content but don't process immediately

Workers find content and create tasks for other workers to process.

---

## Step-by-Step Integration

### Step 1: Install TaskManager Client

```bash
# Install from Source/TaskManager directory
pip install -e ./Source/TaskManager
```

### Step 2: Configure Authentication

```python
# Get API key from environment
import os

TASKMANAGER_API_KEY = os.getenv("TASKMANAGER_API_KEY")
```

### Step 3: Register Task Type

```python
from taskmanager import TaskManagerClient, TaskManagerConfig

config = TaskManagerConfig(
    api_url="https://api.prismq.nomoos.cz/api",
    api_key=TASKMANAGER_API_KEY
)
client = TaskManagerClient(config)

# Register once
client.register_task_type(
    name="youtube_video_scrape",
    version="1.0",
    param_schema={
        "type": "object",
        "properties": {
            "video_url": {"type": "string"}
        },
        "required": ["video_url"]
    }
)
```

### Step 4: Integrate Into Worker

```python
# Main worker loop
while True:
    task = client.claim_task(task_type="youtube_video_scrape")
    if task:
        result = process_task(task['params'])
        client.complete_task(task['id'], result)
```

---

## Best Practices

1. **Error Handling**: Always wrap API calls in try/except
2. **Retry Logic**: Use exponential backoff for network errors
3. **Graceful Shutdown**: Release claimed tasks on shutdown
4. **Logging**: Log all task operations for debugging
5. **Monitoring**: Track metrics (tasks claimed, completed, failed)

---

## Troubleshooting

### Common Issues

**Authentication Failed**: Verify API key is correct  
**Task Type Not Found**: Register task type first  
**No Tasks Available**: Create tasks or adjust filters  
**Network Timeouts**: Increase timeout, check connectivity

---

## Additional Resources

- **Full Documentation**: `Source/_meta/issues/new/Developer06/008-taskmanager-api-client-integration.md`
- **API Swagger**: https://api.prismq.nomoos.cz/public/swagger-ui
- **OpenAPI Spec**: https://api.prismq.nomoos.cz/api/openapi.json
- **Example Code**: Coming in Source/TaskManager/_meta/examples/

---

**Last Updated**: 2025-11-12  
**Version**: 1.0  
**Maintainer**: Developer06
