"""Worker task queue system for HackerNews scraping.

This package provides the worker infrastructure for processing HackerNews scraping tasks.
It follows SOLID principles with clear separation of concerns.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Protocol


class TaskStatus(Enum):
    """Task execution status."""

    QUEUED = "queued"
    CLAIMED = "claimed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a task from the queue.

    Following Single Responsibility Principle - only represents task data.

    NOTE: This is NOT a database schema. Tasks are managed externally via
    TaskManager REST API. This class is just for holding task data during
    worker processing.
    """

    id: int
    task_type: str  # 'story_fetch', 'frontpage_fetch', etc.
    parameters: Dict[str, Any]
    priority: int
    status: TaskStatus
    retry_count: int
    max_retries: int
    created_at: str
    claimed_at: Optional[str] = None


@dataclass
class TaskResult:
    """Result of task processing.

    Following Single Responsibility Principle - only represents result data.

    NOTE: This is NOT a database schema. Results are stored in IdeaInspiration
    table and connected to tasks by ID when calling complete_task endpoint.
    """

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    items_processed: int = 0
    metrics: Optional[Dict[str, Any]] = None


class WorkerProtocol(Protocol):
    """Protocol (interface) that all workers must implement.

    Following Interface Segregation Principle (ISP) - minimal interface.
    Only essential methods, no unnecessary dependencies.
    """

    def claim_task(self) -> Optional[Task]:
        """Claim a task from the queue using configured strategy.

        Returns:
            Task if available, None otherwise
        """
        ...

    def process_task(self, task: Task) -> TaskResult:
        """Process a claimed task.

        Args:
            task: The task to process

        Returns:
            TaskResult with success status and data
        """
        ...

    def report_result(self, task: Task, result: TaskResult) -> None:
        """Report task result back to queue.

        Args:
            task: The completed task
            result: The task execution result
        """
        ...


__all__ = [
    "TaskStatus",
    "Task",
    "TaskResult",
    "WorkerProtocol",
]
