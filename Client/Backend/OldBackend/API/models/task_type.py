"""TaskType models for API endpoints.

TaskType represents a registration of task types that microservices can perform.
It's not tied to workers or specific implementations - just a registry of what
task types exist in the system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class TaskTypeBase(BaseModel):
    """Base model for TaskType with common fields."""
    
    name: str = Field(..., description="Unique name of the task type", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Description of what this task type does")
    parameters_schema: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="JSON schema defining the parameters this task type accepts"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata about the task type"
    )


class TaskTypeCreate(TaskTypeBase):
    """Model for creating a new TaskType."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "video_processing",
                "description": "Process video files with different parameters",
                "parameters_schema": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string", "enum": ["mp4", "webm"]},
                        "resolution": {"type": "string", "enum": ["720p", "1080p", "4k"]}
                    },
                    "required": ["format"]
                },
                "metadata": {
                    "category": "media",
                    "estimated_duration": "5m"
                }
            }
        }
    )


class TaskTypeUpdate(BaseModel):
    """Model for updating an existing TaskType."""
    
    description: Optional[str] = Field(None, description="Updated description")
    parameters_schema: Optional[Dict[str, Any]] = Field(None, description="Updated parameters schema")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    is_active: Optional[bool] = Field(None, description="Whether this task type is active")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Updated description",
                "is_active": True
            }
        }
    )


class TaskTypeResponse(TaskTypeBase):
    """Model for TaskType response."""
    
    id: int = Field(..., description="Unique identifier")
    is_active: bool = Field(default=True, description="Whether this task type is active")
    created_at: datetime = Field(..., description="When the task type was created")
    updated_at: Optional[datetime] = Field(None, description="When the task type was last updated")
    
    model_config = ConfigDict(from_attributes=True)
