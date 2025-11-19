# Issue #008: TaskManager API Client Integration

**Priority**: ⭐⭐⭐ CRITICAL  
**Assigned**: Developer06 (Implementation)  
**Estimated Effort**: 2-3 days  
**Dependencies**: None (External API already exists)  
**Phase**: 1 - Foundation

---

## Overview

Create a Python client library to integrate PrismQ.IdeaInspiration workers with the existing external TaskManager API at https://api.prismq.nomoos.cz/api/. This client will enable centralized task coordination, monitoring, and distributed work management across all Source modules.

---

## Problem Statement

**Current Situation:**
- Each worker module has its own local task queue (SQLite-based)
- No centralized coordination between workers
- No unified monitoring or task distribution
- Duplicate work possible across workers
- No cross-module task prioritization

**External TaskManager API Exists:**
- Hosted at: https://api.prismq.nomoos.cz/api/
- Swagger UI: https://api.prismq.nomoos.cz/public/swagger-ui
- OpenAPI Spec: https://api.prismq.nomoos.cz/api/openapi.json
- Provides: Task type registration, task creation, claiming, completion, deduplication

**What We Need:**
A Python client library that allows PrismQ.IdeaInspiration workers to:
1. Register task types with the external API
2. Create tasks that need to be processed
3. Claim tasks for processing
4. Report task completion with results
5. Handle authentication and error handling

---

## Why Python Client (Not PHP Implementation)

### Incorrect Interpretation
The original issue #008 was titled "Database Schema Design" and described implementing database tables, indexes, and migrations. This was incorrectly interpreted as **building the API backend** (PHP + database).

### Correct Requirement
The actual requirement is to **consume an existing external API** by creating a Python client library that integrates with:
- **External API**: https://api.prismq.nomoos.cz/api/ (already deployed and operational)
- **Existing workers**: Python 3.10+ based workers in Source modules
- **Existing patterns**: Similar to worker integrations in `Source/Video/YouTube/_meta/issues/new/Worker05/016-integrate-with-taskmanager-api.md`

### Architecture Clarification

```
┌─────────────────────────────────────────────────────────────┐
│ PrismQ.IdeaInspiration Workers (Python)                     │
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  YouTube   │  │  Reddit    │  │   Other    │            │
│  │  Worker    │  │  Worker    │  │  Workers   │            │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │
│        │                │                │                    │
│        └────────────────┴────────────────┘                   │
│                         │                                     │
│                         ▼                                     │
│              ┌──────────────────────┐                        │
│              │ TaskManager Client   │  ← NEW: Python Client │
│              │    (Python)          │                        │
│              └──────────┬───────────┘                        │
└─────────────────────────┼─────────────────────────────────────┘
                          │ HTTP/REST
                          ▼
              ┌───────────────────────┐
              │  External TaskManager │  ← EXISTING: External API
              │  API (PHP Backend)    │     (https://api.prismq.nomoos.cz)
              │  - Task Types         │
              │  - Tasks Queue        │
              │  - Deduplication      │
              │  - Authentication     │
              └───────────────────────┘
```

### Why Not Duplicate the Backend?

**Reasons NOT to implement PHP backend locally:**
1. ❌ **External API already exists** - Fully functional at https://api.prismq.nomoos.cz/api/
2. ❌ **Duplication** - Would duplicate existing Model/IdeaInspiration database and worker queues
3. ❌ **Language mismatch** - Workers are Python 3.10+, not PHP
4. ❌ **Deployment complexity** - Would require PHP hosting, when workers just need to call REST API
5. ❌ **Maintenance overhead** - Two systems to maintain instead of one

**Reasons TO create Python client:**
1. ✅ **Integration** - Enables workers to use external TaskManager
2. ✅ **Language compatibility** - Python client for Python workers
3. ✅ **Simple deployment** - Just pip install the client library
4. ✅ **Centralized coordination** - All workers use same external task queue
5. ✅ **Easy testing** - Can mock HTTP requests for unit tests

---

## Technical Requirements

### 1. Python Client Library Structure

```
Source/TaskManager/
├── __init__.py
├── client.py                    # Main TaskManagerClient class
├── models.py                    # Data models (TaskType, Task, etc.)
├── exceptions.py                # Custom exceptions
├── config.py                    # Configuration management
├── README.md                    # Usage documentation
├── _meta/
│   ├── docs/
│   │   └── INTEGRATION_GUIDE.md  # How to integrate with workers
│   ├── examples/
│   │   ├── register_task_type.py
│   │   ├── create_task.py
│   │   ├── claim_task.py
│   │   └── complete_task.py
│   └── tests/
│       ├── test_client.py
│       ├── test_models.py
│       └── test_integration.py
└── pyproject.toml               # Package configuration
```

### 2. TaskManagerClient Class

```python
"""TaskManager API Client for PrismQ.IdeaInspiration workers."""

import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TaskManagerConfig:
    """Configuration for TaskManager API client."""
    api_url: str = "https://api.prismq.nomoos.cz/api"
    api_key: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3


class TaskManagerClient:
    """Client for TaskManager API.
    
    Provides methods to interact with external TaskManager API:
    - Register task types
    - Create tasks with deduplication
    - Claim tasks for processing
    - Report task completion
    
    Example:
        >>> client = TaskManagerClient(config)
        >>> client.register_task_type("youtube_scrape", schema)
        >>> task_id = client.create_task("youtube_scrape", params)
        >>> task = client.claim_task("youtube_scrape")
        >>> client.complete_task(task_id, result_data)
    """
    
    def __init__(self, config: TaskManagerConfig):
        """Initialize client with configuration."""
        self.config = config
        self.session = requests.Session()
        
        if config.api_key:
            self.session.headers['X-API-Key'] = config.api_key
    
    def register_task_type(
        self,
        name: str,
        version: str,
        param_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register a new task type with the API.
        
        Args:
            name: Task type name (e.g., "youtube_scrape")
            version: Task type version (e.g., "1.0")
            param_schema: JSON Schema for task parameters
            
        Returns:
            Task type registration response
            
        Raises:
            TaskManagerAPIError: If registration fails
        """
        # Implementation
        pass
    
    def create_task(
        self,
        task_type: str,
        params: Dict[str, Any],
        priority: int = 5
    ) -> int:
        """Create a new task.
        
        Args:
            task_type: Name of registered task type
            params: Task parameters (validated against schema)
            priority: Task priority (1-10, default 5)
            
        Returns:
            Task ID
            
        Raises:
            TaskManagerAPIError: If creation fails
        """
        # Implementation with deduplication
        pass
    
    def claim_task(
        self,
        task_type: Optional[str] = None,
        worker_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Claim next available task.
        
        Args:
            task_type: Optional task type filter
            worker_id: Worker identifier
            
        Returns:
            Task data or None if no tasks available
            
        Raises:
            TaskManagerAPIError: If claim fails
        """
        # Implementation
        pass
    
    def complete_task(
        self,
        task_id: int,
        result: Dict[str, Any],
        status: str = "completed"
    ) -> Dict[str, Any]:
        """Mark task as completed.
        
        Args:
            task_id: Task ID to complete
            result: Task result data
            status: "completed" or "failed"
            
        Returns:
            Completion response
            
        Raises:
            TaskManagerAPIError: If completion fails
        """
        # Implementation
        pass
    
    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """Get task status and details."""
        # Implementation
        pass
    
    def health_check(self) -> bool:
        """Check if API is healthy."""
        # Implementation
        pass
```

### 3. Data Models

```python
"""Data models for TaskManager API."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class TaskType:
    """Task type definition."""
    id: int
    name: str
    version: str
    param_schema: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Task:
    """Task instance."""
    id: int
    task_type_id: int
    status: str  # pending, claimed, completed, failed
    params: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    priority: int
    attempts: int
    max_attempts: int
    worker_id: Optional[str]
    claimed_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
```

### 4. Exception Handling

```python
"""Custom exceptions for TaskManager client."""


class TaskManagerError(Exception):
    """Base exception for TaskManager client."""
    pass


class TaskManagerAPIError(TaskManagerError):
    """API request failed."""
    
    def __init__(self, status_code: int, message: str, response_data: dict = None):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data
        super().__init__(f"API Error {status_code}: {message}")


class TaskManagerAuthError(TaskManagerError):
    """Authentication failed."""
    pass


class TaskManagerValidationError(TaskManagerError):
    """Task parameters validation failed."""
    pass


class TaskManagerNotFoundError(TaskManagerError):
    """Task or task type not found."""
    pass
```

---

## Integration with Existing Workers

### Pattern 1: Direct Integration (Simple)

```python
"""Example: YouTube worker with TaskManager integration."""

from taskmanager import TaskManagerClient, TaskManagerConfig
from idea_inspiration_db import IdeaInspirationDatabase

# Setup
config = TaskManagerConfig(api_key="your-api-key")
tm_client = TaskManagerClient(config)
db = IdeaInspirationDatabase("db.s3db")

# Register task type (one-time setup)
tm_client.register_task_type(
    name="youtube_channel_scrape",
    version="1.0",
    param_schema={
        "type": "object",
        "properties": {
            "channel_url": {"type": "string"},
            "top_n": {"type": "integer"}
        },
        "required": ["channel_url"]
    }
)

# Worker loop
while True:
    # Claim task from external API
    task = tm_client.claim_task(
        task_type="youtube_channel_scrape",
        worker_id="youtube-worker-001"
    )
    
    if task:
        try:
            # Process task
            results = scrape_youtube_channel(task['params'])
            
            # Save to IdeaInspiration database (local storage)
            for idea in results:
                db.insert(idea)
            
            # Report completion to external API
            tm_client.complete_task(
                task_id=task['id'],
                result={"ideas_found": len(results)},
                status="completed"
            )
        except Exception as e:
            # Report failure
            tm_client.complete_task(
                task_id=task['id'],
                result={"error": str(e)},
                status="failed"
            )
```

### Pattern 2: Hybrid Integration (Keep Local Queue)

```python
"""Keep local SQLite queue for reliability, sync with TaskManager."""

from taskmanager import TaskManagerClient
from workers.queue_database import QueueDatabase

local_queue = QueueDatabase("local_queue.db")
tm_client = TaskManagerClient(config)

# Sync: Pull tasks from TaskManager to local queue
def sync_tasks_from_remote():
    task = tm_client.claim_task(task_type="youtube_scrape")
    if task:
        # Add to local queue for processing
        local_queue.enqueue(
            task_type=task['type'],
            payload=task['params'],
            priority=task['priority'],
            metadata={"tm_task_id": task['id']}
        )

# Worker processes from local queue
def process_local_queue():
    local_task = local_queue.dequeue()
    if local_task:
        result = process_task(local_task)
        
        # Report back to TaskManager if it came from there
        if "tm_task_id" in local_task.metadata:
            tm_client.complete_task(
                task_id=local_task.metadata["tm_task_id"],
                result=result
            )
```

---

## Acceptance Criteria

### Functional Requirements
- [ ] TaskManagerClient class implemented with all methods
- [ ] Data models defined (TaskType, Task)
- [ ] Custom exceptions for error handling
- [ ] Configuration management
- [ ] HTTP request retry logic
- [ ] Authentication with API keys
- [ ] Request/response logging

### Integration Requirements
- [ ] Works with existing Python 3.10+ workers
- [ ] Compatible with Model/IdeaInspiration database
- [ ] Can integrate with existing worker queue patterns
- [ ] Example scripts provided for each operation
- [ ] Integration guide documentation

### Testing Requirements
- [ ] Unit tests for client methods (with mocked HTTP)
- [ ] Integration tests with actual API (optional, depends on API access)
- [ ] Error handling tests
- [ ] Retry logic tests
- [ ] Authentication tests

### Documentation Requirements
- [ ] README with quick start guide
- [ ] API reference documentation
- [ ] Integration guide for workers
- [ ] Example scripts
- [ ] Troubleshooting guide

---

## Implementation Steps

### Day 1: Core Client Implementation
1. Create project structure
2. Implement TaskManagerClient class
3. Implement data models
4. Implement exception classes
5. Add configuration management
6. Write unit tests

### Day 2: Integration & Examples
1. Create example scripts
2. Write integration guide
3. Test with existing worker patterns
4. Add retry and error handling
5. Write integration tests

### Day 3: Documentation & Polish
1. Complete README
2. API reference documentation
3. Troubleshooting guide
4. Code review and refactoring
5. Performance testing

---

## Testing Strategy

```python
# tests/test_client.py
import pytest
from unittest.mock import Mock, patch
from taskmanager import TaskManagerClient, TaskManagerConfig

def test_register_task_type():
    """Test task type registration."""
    config = TaskManagerConfig(api_key="test-key")
    client = TaskManagerClient(config)
    
    with patch('requests.Session.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": 1}
        
        result = client.register_task_type(
            name="test_task",
            version="1.0",
            param_schema={"type": "object"}
        )
        
        assert result["id"] == 1
        mock_post.assert_called_once()

def test_create_task():
    """Test task creation."""
    # Test implementation
    pass

def test_claim_task():
    """Test task claiming."""
    # Test implementation
    pass

def test_complete_task():
    """Test task completion."""
    # Test implementation
    pass
```

---

## Security Considerations

- ✅ API key stored in environment variables, not in code
- ✅ HTTPS for all API communications
- ✅ Request timeout to prevent hanging
- ✅ Retry logic with exponential backoff
- ✅ Input validation before sending to API
- ✅ Sensitive data (results) handled securely

---

## Performance Targets

- API call latency: <500ms (p95)
- Task claiming: <1s (p95)
- Retry backoff: 1s, 2s, 4s
- Connection pooling for multiple requests
- Async support (optional, for high-volume workers)

---

## Dependencies

### Required
- `requests>=2.28.0` - HTTP client
- `python>=3.10,<3.11` - Python version

### Optional
- `aiohttp>=3.8.0` - Async HTTP (for high-performance workers)
- `tenacity>=8.0.0` - Retry logic library
- `pydantic>=2.0.0` - Data validation (alternative to dataclasses)

---

## Related Issues

- Issue #016 in YouTube workers: Integration pattern reference
- Model/IdeaInspiration database: Result storage
- Worker queue patterns: Local queue integration

---

## Definition of Done

- [x] Python client library implemented
- [x] All methods tested and working
- [x] Integration examples provided
- [x] Documentation complete
- [x] Works with existing workers
- [x] Code reviewed by Developer10
- [x] Security reviewed by Developer07

---

**Status**: Ready for Implementation  
**Estimated Timeline**: 2-3 days  
**Assignee**: Developer06  
**Reviewer**: Developer10  
**Critical Success Factor**: Seamless integration with existing Python workers
