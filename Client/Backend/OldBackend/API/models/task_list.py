"""TaskList models for API endpoints.

TaskList represents the current tasks in the system - the actual instances
of tasks that need to be or are being executed.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskListBase(BaseModel):
    """Base model for TaskList with common fields."""
    
    task_type_id: int = Field(..., description="Reference to the TaskType")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for this task instance"
    )
    priority: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Task priority (lower = higher priority)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata for this task"
    )


class TaskListCreate(TaskListBase):
    """Model for creating a new Task."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_type_id": 1,
                "parameters": {
                    "format": "mp4",
                    "resolution": "1080p",
                    "input_file": "video.raw"
                },
                "priority": 50,
                "metadata": {
                    "user_id": "user123",
                    "request_id": "req-456"
                }
            }
        }
    )


class TaskListUpdate(BaseModel):
    """Model for updating an existing Task."""
    
    status: Optional[TaskStatus] = Field(None, description="Updated task status")
    priority: Optional[int] = Field(None, ge=1, le=1000, description="Updated priority")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Updated parameters")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "completed",
                "result": {
                    "output_file": "video_processed.mp4",
                    "duration": "5m 23s"
                }
            }
        }
    )


class TaskListResponse(TaskListBase):
    """Model for Task response."""
    
    id: int = Field(..., description="Unique identifier")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="When the task was created")
    updated_at: Optional[datetime] = Field(None, description="When the task was last updated")
    started_at: Optional[datetime] = Field(None, description="When the task started execution")
    completed_at: Optional[datetime] = Field(None, description="When the task completed")
    
    model_config = ConfigDict(from_attributes=True)
