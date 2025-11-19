"""Worker implementation for PrismQ.IdeaInspiration.Scoring.

This module implements the Worker pattern for scoring tasks, integrating with
TaskManager API for distributed task processing.

Architecture follows SOLID principles:
- Single Responsibility: Each worker type handles specific scoring tasks
- Open/Closed: Extensible through subclassing without modifying base
- Liskov Substitution: Workers are interchangeable through common protocol
- Interface Segregation: Minimal, focused worker protocol
- Dependency Inversion: Depends on abstractions (protocols), not concrete implementations
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Protocol
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    QUEUED = "queued"
    CLAIMED = "claimed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Task representation for worker processing.
    
    Attributes:
        id: Unique task identifier
        task_type: Type of scoring task (e.g., 'text_scoring', 'engagement_scoring')
        parameters: Task-specific parameters
        priority: Task priority (higher = more important)
        status: Current task status
        retry_count: Number of times task has been retried
        max_retries: Maximum number of retry attempts
        created_at: Task creation timestamp
        claimed_at: Task claim timestamp
    """
    id: int
    task_type: str
    parameters: Dict[str, Any]
    priority: int = 0
    status: TaskStatus = TaskStatus.QUEUED
    retry_count: int = 0
    max_retries: int = 3
    created_at: Optional[str] = None
    claimed_at: Optional[str] = None


@dataclass
class TaskResult:
    """Result of task processing.
    
    Attributes:
        success: Whether task completed successfully
        data: Result data (score breakdown, metrics, etc.)
        error: Error message if failed
        items_processed: Number of items processed
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    items_processed: int = 0


class WorkerProtocol(Protocol):
    """Protocol defining worker interface (Interface Segregation Principle).
    
    Workers must implement:
    - claim_task(): Claim a task from the queue
    - process_task(): Process a claimed task
    - report_result(): Report task completion
    """
    
    def claim_task(self) -> Optional[Task]:
        """Claim a task from the queue.
        
        Returns:
            Task if available, None otherwise
        """
        ...
    
    def process_task(self, task: Task) -> TaskResult:
        """Process a claimed task.
        
        Args:
            task: Task to process
            
        Returns:
            TaskResult with processing outcome
        """
        ...
    
    def report_result(self, task: Task, result: TaskResult) -> None:
        """Report task completion.
        
        Args:
            task: Completed task
            result: Processing result
        """
        ...


__all__ = [
    "Task",
    "TaskResult", 
    "TaskStatus",
    "WorkerProtocol",
]
