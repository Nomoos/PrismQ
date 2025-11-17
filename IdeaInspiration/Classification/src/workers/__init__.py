"""Worker module for classification task processing.

This module provides worker functionality for processing classification tasks
from the TaskManager API queue.
"""

from typing import Protocol, Dict, Any
from dataclasses import dataclass
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    CLAIMED = "claimed"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Task representation."""
    id: int
    task_type: str
    params: Dict[str, Any]
    status: TaskStatus
    priority: int = 0
    attempts: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task from dictionary."""
        return cls(
            id=data['id'],
            task_type=data['task_type'],
            params=data.get('params', {}),
            status=TaskStatus(data.get('status', 'pending')),
            priority=data.get('priority', 0),
            attempts=data.get('attempts', 0)
        )


@dataclass
class TaskResult:
    """Task processing result."""
    success: bool
    data: Dict[str, Any]
    error: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'success': self.success,
            'data': self.data
        }
        if self.error:
            result['error'] = self.error
        return result


class WorkerProtocol(Protocol):
    """Protocol defining worker interface."""
    
    def process_task(self, task: Task) -> TaskResult:
        """Process a task and return result."""
        ...
    
    def run(self, poll_interval: int = 5, max_iterations: int = 0) -> None:
        """Run worker loop."""
        ...


__all__ = [
    'Task',
    'TaskResult',
    'TaskStatus',
    'WorkerProtocol'
]
