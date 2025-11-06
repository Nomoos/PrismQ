"""Pydantic models for queue API endpoints."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
import json


class EnqueueTaskRequest(BaseModel):
    """Request model for enqueuing a new task."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "video_processing",
                "priority": 50,
                "payload": {"format": "mp4", "resolution": "1080p"},
                "compatibility": {"region": "us-west"},
                "max_attempts": 3,
                "idempotency_key": "video-123-process",
            }
        }
    )

    type: str = Field(..., description="Task type identifier", min_length=1)
    priority: int = Field(
        default=100,
        description="Task priority (lower = higher priority)",
        ge=1,
        le=1000,
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict, description="Task payload data"
    )
    compatibility: Dict[str, Any] = Field(
        default_factory=dict, description="Worker compatibility requirements"
    )
    max_attempts: int = Field(
        default=5, description="Maximum retry attempts", ge=1, le=10
    )
    run_after_utc: Optional[datetime] = Field(
        default=None, description="Schedule task to run after this time"
    )
    idempotency_key: Optional[str] = Field(
        default=None, description="Unique key to prevent duplicate task creation"
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate task type is not empty."""
        if not v or not v.strip():
            raise ValueError("Task type cannot be empty")
        return v.strip()


class EnqueueTaskResponse(BaseModel):
    """Response model for enqueued task."""

    task_id: int = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status")
    created_at_utc: datetime = Field(..., description="Task creation timestamp")
    message: str = Field(default="Task enqueued successfully")


class TaskStatusResponse(BaseModel):
    """Response model for task status."""

    task_id: int = Field(..., description="Unique task identifier")
    type: str = Field(..., description="Task type")
    status: str = Field(..., description="Current task status")
    priority: int = Field(..., description="Task priority")
    attempts: int = Field(..., description="Number of execution attempts")
    max_attempts: int = Field(..., description="Maximum retry attempts")
    payload: Dict[str, Any] = Field(..., description="Task payload")
    compatibility: Dict[str, Any] = Field(..., description="Compatibility requirements")
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )
    created_at_utc: Optional[datetime] = Field(
        default=None, description="Task creation timestamp"
    )
    processing_started_utc: Optional[datetime] = Field(
        default=None, description="Processing start timestamp"
    )
    finished_at_utc: Optional[datetime] = Field(
        default=None, description="Task completion timestamp"
    )
    locked_by: Optional[str] = Field(default=None, description="Worker ID if claimed")

    @classmethod
    def from_task(cls, task) -> "TaskStatusResponse":
        """Create response from Task model."""
        return cls(
            task_id=task.id,
            type=task.type,
            status=task.status,
            priority=task.priority,
            attempts=task.attempts,
            max_attempts=task.max_attempts,
            payload=task.get_payload_dict(),
            compatibility=task.get_compatibility_dict(),
            error_message=task.error_message,
            created_at_utc=task.created_at_utc,
            processing_started_utc=task.processing_started_utc,
            finished_at_utc=task.finished_at_utc,
            locked_by=task.locked_by,
        )


class CancelTaskResponse(BaseModel):
    """Response model for task cancellation."""

    task_id: int = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status")
    message: str = Field(..., description="Cancellation result message")


class QueueStatsResponse(BaseModel):
    """Response model for queue statistics."""

    total_tasks: int = Field(..., description="Total tasks in queue")
    queued_tasks: int = Field(..., description="Number of queued tasks")
    processing_tasks: int = Field(..., description="Number of processing tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    failed_tasks: int = Field(..., description="Number of failed tasks")
    oldest_queued_age_seconds: Optional[float] = Field(
        default=None, description="Age of oldest queued task in seconds"
    )
