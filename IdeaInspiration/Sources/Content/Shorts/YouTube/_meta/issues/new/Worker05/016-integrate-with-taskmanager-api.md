# Issue #016: Integrate with TaskManager API

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 05 - DevOps/Infrastructure  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: High  
**Duration**: 2-3 days  
**Dependencies**: #002 (Worker Base), #004 (Database Schema)

---

## Objective

Integrate the YouTube worker system with the PrismQ.Client TaskManager API to enable centralized task management, monitoring, and control across the entire PrismQ ecosystem.

---

## Problem Statement

The worker system needs to integrate with TaskManager API (from PrismQ.Client) to:
1. Report task status updates to central system
2. Receive task assignments from central queue
3. Report worker health and metrics
4. Enable cross-module task coordination
5. Support unified monitoring dashboard

---

## Proposed Solution

### TaskManager Client

**File**: `Sources/Content/Shorts/YouTube/src/integration/taskmanager_client.py` (NEW)

```python
"""TaskManager API client for worker integration."""

import requests
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class TaskManagerConfig:
    """TaskManager API configuration."""
    api_url: str
    api_key: Optional[str] = None
    timeout: int = 30


class TaskManagerClient:
    """Client for TaskManager API.
    
    Handles communication with PrismQ.Client TaskManager API.
    """
    
    def __init__(self, config: TaskManagerConfig):
        """Initialize client.
        
        Args:
            config: TaskManager configuration
        """
        self.config = config
        self.session = requests.Session()
        
        if config.api_key:
            self.session.headers['Authorization'] = f'Bearer {config.api_key}'
    
    def report_task_status(
        self,
        task_id: int,
        status: str,
        progress: Optional[float] = None,
        result_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """Report task status to TaskManager.
        
        Args:
            task_id: Local task ID
            status: Task status
            progress: Progress percentage (0-100)
            result_data: Result data
            error: Error message if failed
            
        Returns:
            True if successful
        """
        try:
            response = self.session.post(
                f"{self.config.api_url}/tasks/{task_id}/status",
                json={
                    'status': status,
                    'progress': progress,
                    'result_data': result_data,
                    'error': error
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to report task status: {e}")
            return False
    
    def report_worker_heartbeat(
        self,
        worker_id: str,
        status: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """Report worker heartbeat to TaskManager.
        
        Args:
            worker_id: Worker identifier
            status: Worker status
            metrics: Worker metrics
            
        Returns:
            True if successful
        """
        try:
            response = self.session.post(
                f"{self.config.api_url}/workers/{worker_id}/heartbeat",
                json={
                    'status': status,
                    'metrics': metrics
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to report heartbeat: {e}")
            return False
    
    def fetch_assigned_tasks(self, worker_id: str) -> list:
        """Fetch tasks assigned to worker.
        
        Args:
            worker_id: Worker identifier
            
        Returns:
            List of assigned tasks
        """
        try:
            response = self.session.get(
                f"{self.config.api_url}/workers/{worker_id}/tasks",
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json().get('tasks', [])
        except Exception as e:
            logger.error(f"Failed to fetch assigned tasks: {e}")
            return []
```

### Integration with BaseWorker

Update BaseWorker to use TaskManager client:

```python
# In base_worker.py

def _update_task_manager(self, task: Task, result: TaskResult) -> None:
    """Update TaskManager API."""
    if not self.taskmanager_client:
        return
    
    status = 'completed' if result.success else 'failed'
    
    self.taskmanager_client.report_task_status(
        task_id=task.id,
        status=status,
        result_data=result.data,
        error=result.error
    )
```

---

## Acceptance Criteria

- [ ] TaskManager client implemented
- [ ] Task status updates sent to TaskManager
- [ ] Worker heartbeats sent to TaskManager
- [ ] Error handling for API failures
- [ ] Retry logic for failed API calls
- [ ] Configuration via config file
- [ ] Integration tests passing
- [ ] Documentation complete

---

## Files to Create

1. `Sources/Content/Shorts/YouTube/src/integration/__init__.py` - NEW
2. `Sources/Content/Shorts/YouTube/src/integration/taskmanager_client.py` - NEW
3. `Sources/Content/Shorts/YouTube/_meta/tests/test_taskmanager_client.py` - NEW

---

**Status**: ✅ Ready for Implementation  
**Assignee**: Worker05 - DevOps/Infrastructure  
**Timeline**: Week 3, Days 1-3
